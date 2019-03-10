import socket, urllib, lxml.html
from core.url import URL
from core.locals import *

def manipulate_urls(wf):
    try:
        content = wf.get_decoded_content()
        tree = lxml.html.fromstring(content) # Parse whole html tree

        for el in [["a", "href"], ["link", "href"], ["script", "src"], ["img", "src"]]: # Crawl elements with URL
            for link_element in tree.xpath('//' + el[0]):
                url = link_element.get(el[1]) # Get original URL
                if url:
                    url = _to_cache_url(wf.url.resolve(), url) # Call callback
                    link_element.set(el[1], url) # Override old URL

        wf.content = lxml.html.tostring(tree, encoding=wf.encoding)
    except:
        raise
        print("[WARN] Couldn't manipulate URLs. Page \"%s\" may be broken." % (url))
    return wf

def _to_cache_url(origin, link):
    try:
        #return "http://%s:8080/cache?url=%s" % (_local_ip_address, urllib.parse.quote((URL.from_url(origin) / link).resolve()))
        url = URL.from_url(origin) / link
        url.scheme = None # Scheme ("https://") will not be in string
        return "http://%s:8080/cache/%s" % (_local_ip_address, url.resolve())
    except ValueError as e:
        print("[WARN] Concatening of \"%s\" failed: %s" % (link, e))
        return link
    
_local_ip_address = get_ip()