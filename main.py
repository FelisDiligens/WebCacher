from flask import Flask, redirect, send_from_directory, send_file, request
from flask_cors import CORS
from datetime import datetime
app = Flask(__name__)
CORS(app)

from core.locals import *
from core.url import URL
from core.cache import WebFile, WebCacher
from core.postprocess import *
import core.database as database

import io, pathlib

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from requests.exceptions import ConnectionError

from colorama import init, Fore, Back, Style
init()


@app.route("/")
@app.route("/index.html")
def index():
    return send_file("www/index.html")

@app.route("/www/<path:file>")
def www(file):
    return send_file("www/" + file)
    

@app.route("/cache")
def cache():
    url = URL.from_url(request.values.get('url'))
    url.scheme = None
    return redirect("http://" + get_ip() + ":8080/cache/" + url.resolve(), code=302)


@app.route("/cache/<path:url>")
def cache_url(url):
    # /cache/de.wikipedia.org/wiki/Hauptseite
    # => https://de.wikipedia.org/wiki/Hauptseite
    try:
        query = request.query_string.decode("UTF-8")
        if query:
            query = "?" + query
        url = "https://" + url + query
        urlObj = URL.from_url(url)

        headers = {}
        for header in get_config()["forwardHeaders"]:
            if request.headers[header]:
                headers[header] = request.headers[header]

        if get_config()["verbose"]:
            print("[Web] Accessing: \"%s\"" % (url))
        wf = WebCacher.get(url, headers)
        proxify(wf)
        return wf.send_file()
    except ConnectionError:
        if check_connection():
            return send_file("www/error/unavailable.html")
        else:
            return send_file("www/error/offline.html")
    except:
        print(Fore.RED + ("[FAIL] Couldn't load \"%s\"" % url) + Style.RESET_ALL)
        return get_file("www/error/guru.html").replace("%%TRACEBACK%%", get_traceback_as_html())
    

@app.route("/history")
def cache_history():
    history = []
    rows = database.get_history()
    for row in rows:
        wf = WebFile.from_cache(row[1])
        url = wf.url.copy()
        url.scheme = None # Scheme ("https://") will not be in string
        cache_url = "http://%s:8080/cache/%s" % (get_ip(), url.resolve())
        history.append(f"<li><a href=\"{cache_url}\" title=\"{url.resolve()}\">{get_html_title(wf)}</a> (first accessed {datetime.utcfromtimestamp(wf.accessed).strftime('%Y-%m-%d %H:%M:%S')})</li>")
    return get_file("www/history.html").replace("%%HISTORY%%", "<ul>\n" + "\n".join(history) + "\n</ul>")



@app.errorhandler(404)
def error404(e):
    return send_file("www/error/404.html")



host = get_config()["server"]["host"]
port = get_config()["server"]["port"]

print("""
               |             /   /
,---.,---.,---.|---.,---.o  /   / 
|    ,---||    |   ||---'  /   /  
`---'`---^`---'`   '`---'o/   /   

Running caching server at %s:%s
Open http://%s:%s/ in your browser.
""" % (host, port, get_ip(), port))

app.run(host=host, port=port)