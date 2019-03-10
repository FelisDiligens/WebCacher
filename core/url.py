import re
import urllib.parse
from core.locals import *

"""
    TODO:
    * Documentation
    * Adding comments
    * Write own concatenation method, instead of relying on urllib
"""

class URL:
    """Holds the parts of an parsed URL for analyzing, manipulating and resolving."""

    def __init__(self):
        # scheme:[//authority]path[?query][#fragment]
        # authority = [userinfo@]host[:port]
        self.original_url = ""
        self.scheme = ""
        #self.userinfo = ""
        self.host = ""
        self.port = ""
        self.path = []
        self.query = {}
        self.fragment = ""
        self.endswith_separator = False

    def from_url(u):
        """
        Class-level function. Returns an URL object.
        
        Will raise an ValueError, if URL is invalid.
        """
        return _parse_url(URL(), u)

    def parse(self, u):
        """
        Object-level method. Changes will be applied directly.
        
        Will raise an ValueError, if URL is invalid.
        """
        _parse_url(self, u)

    def __str__(self):
        return self.resolve()

    def resolve(self):
        return _resolve_to_url(self)

    def resolve_to_path(self):
        """
        Resolves the url to an path for caching.

        For instance
        "http://www.example.com/search?q=foo+bar"
        will be resolved to
        "./cache/com/example/www/search/query171143778"
        """
        return _resolve_to_path(self)

    def _concat(self, s):
        """In development..."""
        # If the url is absolute...
        if _is_valid_url(s):
            return URL.from_url(s) # parse it instead.

        # /starts/with/slash
        if s.lstrip().startswith("/"):
            pass

    def concat(self, s):
        """
        Concatenate an path to the url.
        
        The URL object itself will be changed.
        If you want to create a new object instead, then use the '+'-operator.
        """

        # If the url is absolute...
        if _is_valid_url(s):
            return self.parse(s) # parse it instead.
        else:
            self.parse(urllib.parse.urljoin(self.resolve(), s))
        return self

    def __add__(self, other):
        return URL.from_url(urllib.parse.urljoin(self.resolve(), other))

    __truediv__ = __add__

    def __eq__(self, other):
        return str(self) == str(other)

    def get_parent(self):
        """
        Get the parent of the url.

        e.g. URL.from_str("http://www.example.com/sub/page.php").get_parent().resolve() # => "http://www.example.com/sub/"
        """
        if len(self.path) == 0:
            return self.copy()
        u = self.copy()
        u.path.pop()
        u.endswith_separator = True
        return u

    def get_root(self):
        """
        Get the root of the url.

        e.g. URL.from_str("http://www.example.com/sub/page.php").get_root().resolve() # => "http://www.example.com"
        """
        if len(self.path) == 0:
            return self.copy()
        u = self.copy()
        u.path = []
        u.endswith_separator = False
        return u

    def get_filename(self):
        if len(self.path) == 0:
            return "index.html"
        return self.path[-1]

    def copy(self):
        u = URL()
        u.original_url = self.original_url
        u.scheme = self.scheme
        u.userinfo = self.userinfo
        u.host = self.host
        u.port = self.port
        u.path = self.path.copy()
        u.query = self.query.copy()
        u.fragment = self.fragment
        u.endswith_separator = self.endswith_separator
        return u



    
# https://mathiasbynens.be/demo/url-regex
#URL_REGEX = re.compile(r"^(https?|ftp)://(-\.)?([^\s/?\.#-]+\.?)+(/[^\s]*)?$")
URL_REGEX = re.compile(r"(^|[\s.:;?\-\]<\(])(https?://[-\w;/?:@&=+$\|\_.!~*\|'()\[\]%#,☺]+[\w/#](\(\))?)(?=$|[\s',\|\(\).:;?\-\[\]>\)])")

def _is_valid_url(s):
    return bool(URL_REGEX.match(str(s)))

def _parse_url_query(s):
    args = {}
    for arg in s.strip().lstrip("?").split("&"):
        key, value = arg.split("=")
        args[key] = urllib.parse.unquote_plus(value)
    return args

def _parse_url(url, s):
    # Don't parse invalid URLs:
    if not _is_valid_url(s):
        raise ValueError("The given url \"%s\" is invalid." % (s))

    url.original_url = str(s)
    temp = str(s)

    # Get the scheme (e.g. "http")
    i = temp.find("://")
    if i >= 0:
        url.scheme = temp[:i]
        temp = temp[i+3:]

    # Get the query (e.g. "?q=foo+bar")
    i = temp.find("?")
    if i >= 0:
        url.query = _parse_url_query(temp[i+1:])
        temp = temp[:i]

    # Get the fragment (e.g. "#anRandomFragment")
    i = temp.find("#")
    if i >= 0:
        url.fragment = temp[i+1:]
        temp = temp[:i]

    # Get the host (e.g. "www.example.com")
    url.endswith_separator = temp.rstrip().endswith("/")
    i = temp.find("/")
    if i < 0:
        url.host = temp
        url.path = []
    else:
        url.host = temp[:i]
        temp = temp[i+1:]

        # Get the path (e.g. "/subpage/index.html")
        url.path = temp.strip("/ ").split("/")

    # Get the port (e.g. ":8080")
    i = url.host.find(":")
    if i >= 0:
        url.port = url.host[i+1:]
        url.host = url.host[:i]

    url.resolved_url = _resolve_to_url(url)
    return url

def _resolve_to_url(url):
    resolved_url = ""

    # Add scheme, if available (e.g. "http://")
    if url.scheme:
        resolved_url += url.scheme + "://"

    # Add host (e.g. "www.example.com")
    resolved_url += url.host

    # Add port (e.g. ":8080")
    if url.port:
        resolved_url += ":" + url.port

    # Add path, if available (e.g. "/subpage/index.html")
    if len(url.path) > 0:
        resolved_url += "/" + "/".join(url.path)

    # Ends with an separator?
    if url.endswith_separator:
        resolved_url += "/"

    # Add fragment, if available (e.g. "#anRandomFragment")
    if url.fragment:
        resolved_url += "#" + url.fragment

    # Add query, if available (e.g. "?q=foo+bar")
    if url.query:
        resolved_url += "?" + urllib.parse.urlencode(url.query)

    return resolved_url

def _resolve_to_path(url):
    """
    Resolves the url to an path for caching.

    For instance
    "http://www.example.com/search?q=foo+bar"
    will be resolved to
    "./cache/com/example/www/search/query171143778"
    """

    # TODO: ADD PORT AND THE OTHER STUFF!!
    result = remove_unsafe_characters("./cache/" + "/".join(reversed(url.host.split("."))) + "/" + "/".join(url.path))

    # Has query? Then calculate and append an hash to path.
    if url.query:
        query_hash = _java_string_hashcode(urllib.parse.urlencode(url.query))
        result += "/query%.0f" % (query_hash)

    return result

# https://gist.github.com/hanleybrand/5224673
def _java_string_hashcode(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000