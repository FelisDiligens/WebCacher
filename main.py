from flask import Flask, redirect, send_from_directory, send_file, request
app = Flask(__name__)

from core.locals import *
from core.url import URL
from core.cache import WebFile, WebCacher, WebCrawler
from core.postprocess import *

import io, pathlib

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from requests.exceptions import ConnectionError


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
    return redirect("http://" + get_ip() + "/cache/" + url.resolve(), code=302)


@app.route("/cache/<path:url>")
def cache_url(url):
    # /cache/de.wikipedia.org/wiki/Hauptseite
    # => https://de.wikipedia.org/wiki/Hauptseite
    try:
        query = request.query_string.decode("UTF-8")
        if query:
            query = "?" + query
        url = "https://" + url + query
        print("Accessing: \"%s\"" % (url))
        wf = WebCacher.get(url)
        if wf.type == "text/html":
            manipulate_urls(wf)
        return wf.send_file()
    except ConnectionError:
        if check_connection():
            return send_file("www/error/unavailable.html")
        else:
            return send_file("www/error/offline.html")
    except:
        print("[FAIL] Couldn't load \"%s\"" % url)
        return get_file("www/error/guru.html").replace("%%TRACEBACK%%", get_traceback_as_html())
        #return get_traceback_as_html()

@app.errorhandler(404)
def error404(e):
    return send_file("www/error/404.html")

"""
@app.route("/crawl")
def crawl():
    return "Caution: EXPERIMENTAL FEATURE!"

    url = request.values.get('url')
    times = request.values.get('times')
    if times:
        times = int(times)
    else:
        times = 2
    print("\n[DEBUG] Begin crawling...\n      * URL = %s\n      * TIMES = %s\n" % (url, times))
    WebCrawler.crawl_url(url, times=times)
    return "Well... look into the console window."
"""

app.run(host='0.0.0.0', port=8000)