import socket, urllib, lxml.html
from core.url import URL
from core.locals import *

"""
I borrowed this code piece (proxifyCSS) of joshdick's miniProxy.php
Link: https://github.com/joshdick/miniProxy
Thank you.
"""
# Proxify contents of url() references in blocks of CSS text.
def proxify_css(wf):
    # Add a "url()" wrapper to any CSS @import rules that only specify a URL without the wrapper,
    # so that they're proxified when searching for "url()" wrappers below.
    content = wf.get_decoded_content()

    source_lines = content.split("\n")
    normalized_lines = []
    for line in source_lines:
        if re.match(r"@import\s+url", line):
            normalized_lines.append(line)
        else:
            def repl(m):
                return m.group(1) + "url(" + m.group(2) + ")" + m.group(3)

            normalized_lines.append(re.sub(r"(@import\s+)([^;\s]+)([\s;])", repl, line))

    normalized_css = "\n".join(normalized_lines)
    wf_url = wf.url.resolve()
    def repl2(m):
        url = m.group(1)
        # Remove any surrounding single or double quotes from the URL so it can be passed to rel2abs - the quotes are optional in CSS
        # Assume that if there is a leading quote then there should be a trailing quote, so just use trim() to remove them
        if url.find("'") == 0:
            url = url.strip("'")
        if url.find("\"") == 0:
            url = url.strip("\"")

        if url.find("data:") == 0:
            return "url(" + url + ")" # The URL isn't an HTTP URL but is actual binary data. Don't proxify it.
        return "url(" + _to_cache_url(wf_url, url) + ")"

    wf.set_decoded_content(re.sub(r"url\((.*?)\)", repl2, normalized_css))
    return wf


def proxify_html(wf):
    try:
        content = wf.get_decoded_content()
        tree = lxml.html.fromstring(content) # Parse whole html tree

        for el in [["a", "href"], ["link", "href"], ["script", "src"], ["img", "src"], ["form", "action"], ["iframe", "src"]]: # Crawl elements with URL
            # meta[@http-equiv]
            for link_element in tree.xpath('//' + el[0]):
                url = link_element.get(el[1]) # Get original URL
                if url:
                    url = _to_cache_url(wf.url.resolve(), url) # Call callback
                    link_element.set(el[1], url) # Override old URL

                # Remove integrity and crossorigin="anonymous" from <link>
                if el[0] == "link":
                    if "integrity" in link_element.attrib:
                        del link_element.attrib["integrity"]
                    if "crossorigin" in link_element.attrib:
                        del link_element.attrib["crossorigin"]

        wf.content = lxml.html.tostring(tree, encoding=wf.encoding)
    except:
        #raise
        print("[WARN] Couldn't proxify URLs. Page \"%s\" may be broken." % (wf.url))
    return wf

def proxify(wf):
    if wf.type == "text/html":
        proxify_html(wf)
    elif wf.type == "text/css":
        proxify_css(wf)
    return wf

def _to_cache_url(origin, link):
    try:
        #return "http://%s:8080/cache?url=%s" % (_local_ip_address, urllib.parse.quote((URL.from_url(origin) / link).resolve()))
        url = URL.from_url(origin) / link
        url.scheme = None # Scheme ("https://") will not be in string
        return "http://%s:8080/cache/%s" % (_local_ip_address, url.resolve())
    except ValueError as e:
        #print("[WARN] Concatening of \"%s\" failed: %s" % (link, e))
        return link
    
_local_ip_address = get_ip()