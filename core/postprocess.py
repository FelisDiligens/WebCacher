import socket, urllib
from core.url import URL, is_valid_url, is_relative_url
from core.locals import *
from io import StringIO
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style

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
        return "url(" + to_cache_url(wf_url, url) + ")"

    wf.set_decoded_content(re.sub(r"url\((.*?)\)", repl2, normalized_css))
    return wf

def proxify_html(wf):
    """Make modifications to the cached HTML page, such as proxifing the URLs or removing crossorigin bullshit."""
    try:
        content = wf.get_decoded_content()
        soup = BeautifulSoup(content, 'html5lib') # html5lib is apparently "Extremely lenient". That's suits us well!

        # Replace all URLs with proxified ones:
        for keywords in [["a", "href"], ["link", "href"], ["script", "src"], ["img", "src"], ["form", "action"], ["iframe", "src"]]:
            tag_name = keywords[0]
            attr_name = keywords[1]
            for tag in soup.find_all(tag_name):
                if tag.get(attr_name) != None:
                    tag[attr_name] = to_cache_url(wf.url.resolve(), tag[attr_name])

                # Remove integrity and crossorigin="anonymous" from <link>
                if tag_name == "link":
                    if tag.get("integrity") != None:
                        del tag["integrity"]
                    if tag.get("crossorigin") != None:
                        del tag["crossorigin"]

        # Search for URLs in "data-" attributes and proxify any url
        # This might cause or solve problems depending on the webpage
        for tag_name in ["div"]:
            for tag in soup.find_all(tag_name):
                for attr in tag.attrs.keys():
                    if attr.startswith("data-") and (is_relative_url(tag[attr]) or is_valid_url(tag[attr])):
                        tag[attr] = to_cache_url(wf.url.resolve(), tag[attr])


        #wf.content = soup.prettify(wf.encoding, formatter=None) # return binary string
        wf.content = str(soup).encode(wf.encoding, errors="ignore")
    except:
        #raise # TODO: Comment this for productive use
        print(Fore.YELLOW + ("[WARN] Couldn't proxify URLs. Page \"%s\" may be broken." % (wf.url)) + Style.RESET_ALL)
    return wf

def get_html_title(wf):
    try:
        content = wf.get_decoded_content()
        soup = BeautifulSoup(content, 'html5lib')
        title = soup.find('title')
        return title.string
    except:
        print(Fore.YELLOW + ("[WARN] Couldn't proxify URLs. Page \"%s\" may be broken." % (wf.url)) + Style.RESET_ALL)
    return wf.url.resolve()

def proxify(wf):
    if wf.type == "text/html":
        proxify_html(wf)
    elif wf.type == "text/css":
        proxify_css(wf)
    return wf

def to_cache_url(origin, link):
    # ERROR: ValueError // The given url "javascript:void(0)" is invalid.
    if link.startswith('data:image') or link.startswith('javascript:') or link.startswith('about:blank'):
        return link
    try:
        url = URL.from_url(origin) / link
        url.scheme = None # Scheme ("https://") will not be in string
        #return "http://%s:8080/cache?url=%s" % (_local_ip_address, urllib.parse.quote((URL.from_url(origin) / link).resolve()))
        return "http://%s:8080/cache/%s" % (_local_ip_address, url.resolve())
    except ValueError: # The given url "javascript:void(0)" is invalid.
        return "http://%s:8080/cache/%s" % (_local_ip_address, link)
    
_local_ip_address = get_ip()