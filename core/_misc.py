"""
!!! This file contains old, unused code that I've put here in case I need it later. !!!
"""

import lxml.html, urllib, pathlib, sys, traceback, json, time, mimetypes
from core.url import *

def to_cache_url(origin, link):
    try:
        return "http://localhost:8080/cache?url=" + urllib.parse.quote((URL.from_url(origin) / link).resolve())
    except ValueError as e:
        print("[WARN] Concatening of \"%s\" failed: %s" % (link, e))
        return link

def manipulate_urls(origin, content, callback):
    tree = lxml.html.fromstring(content) # Parse whole html tree

    for el in [["a", "href"], ["link", "href"], ["script", "src"], ["img", "src"]]: # Crawl elements with URL
        for link_element in tree.xpath('//' + el[0]):
            url = link_element.get(el[1]) # Get original URL
            if url:
                url = callback(origin, url) # Call callback
                link_element.set(el[1], url) # Override old URL

    return lxml.html.tostring(tree, encoding="unicode") # Return modified content

def get_traceback_as_html():
    return "<b>ERROR: {}</b><br>{}<br><br><b>Traceback:</b><br>{}".format(
        sys.exc_info()[0].__name__, # Class name of exception
        str(sys.exc_info()[1]), # Description of exception
        "<br>".join(traceback.format_tb(sys.exc_info()[2])) # Traceback of exception
    )

def is_html(content):
    content = content.lower()
    for el in ["html", "head", "body"]:
        if not el in content:
            return False
    return True
    
def save_file(url):
    # Get information about URL:
    url = URL.from_url(url)
    cache_path = pathlib.Path(url.resolve_to_path())
    response_path = cache_path / "response.json"
    file_name = url.get_filename()

    response = {
        "accessed": time.time(),
        "url": url.resolve()
    }

    # If cached and static, skip download:
    if response_path.exists():
        response = json.load(open(response_path, "r"))
        print("[INFO] Already cached: \"%s\"" % response["url"])
        return cache_path / response["file"]
    else:
        print("[INFO] Downloading and caching under \"%s\"" % cache_path)

    # Download:
    stream = urllib.request.urlopen(url.resolve())
    encoding = stream.headers.get_content_charset()
    if not encoding:
        encoding = "utf-8"
    content = stream.read()
    mimetype = stream.info().get_content_type()
    stream.close()

    if file_name.rfind(".") < 0:
        file_name += mimetypes.guess_extension(mimetype)

    response["type"] = mimetype
    response["file"] = file_name

    file_path = cache_path / file_name

    # Manipulate, if possible:
    try:
        if mimetype.strip().lower() == "text/html":
            content = manipulate_urls(url.resolve(), content.decode(encoding), to_cache_url).encode(encoding)
    except:
        print ("[WARN] Couldn't manipulate URLs. Page \"%s\" may be broken." % (url))

    # Create folders:
    cache_path.mkdir(parents=True, exist_ok=True)

    # Cache for later use:
    with open(file_path, "wb") as f:
        f.write(content)

    # Save response meta-data:
    with open(response_path, "w") as f:
        f.write(json.dumps(response, indent=4))

    # Return path:
    return file_path