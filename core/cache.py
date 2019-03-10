from core.url import URL
import urllib, pathlib, mimetypes, json, time, lxml.html, requests
from datetime import datetime

class WebFile:
    def __init__(self):
        self.accessed = -1
        self.url = ""
        self.path = ""
        self.file = ""
        self.type = ""
        self.encoding = "utf-8"
        self.content = None
        self.status_code = -1

    def from_cache(url):
        wf = WebFile()
        wf.url = URL.from_url(url)

        cache_path = pathlib.Path(wf.url.resolve_to_path())
        response_path = cache_path / "response.json"
        if not response_path.exists():
            return None

        response = json.load(open(response_path, "r"))
        wf.accessed = response["accessed"]
        wf.file = response["file"]
        wf.path = cache_path / wf.file
        wf.type = response["type"]
        wf.encoding = response["encoding"]
        wf.status_code = response["statusCode"]

        with open(wf.path, "rb") as f:
            wf.content = f.read()

        return wf

    def from_web(url):
        wf = WebFile()
        wf.url = URL.from_url(url)
        wf.accessed = time.time()

        # Requesting file from web server:
        response = requests.get(wf.url.resolve())
        wf.encoding = response.apparent_encoding # response.encoding
        wf.content = response.content
        wf.type = response.headers.get('content-type')
        # "text/html; charset=utf-8"
        if ';' in wf.type:
            wf.type = wf.type[:wf.type.find(';')]
        wf.status_code = response.status_code

        #stream = urllib.request.urlopen(wf.url.resolve())
        #wf.encoding = stream.headers.get_content_charset()
        #if not wf.encoding:
        #    wf.encoding = "utf-8"
        #wf.content = stream.read()
        #wf.type = stream.info().get_content_type()
        #stream.close()
        
        # Determine file name:
        extension = _determine_extention(wf.url.get_filename(), wf.type)
        wf.file = "saved" + extension

        wf.path = pathlib.Path(wf.url.resolve_to_path()) / wf.file

        return wf

    def get_decoded_content(self):
        return self.content.decode(self.encoding, errors="ignore")

    def set_decoded_content(self, content):
        self.content = content.encode(self.encoding)

    def save(self):
        # Create folders:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Cache for later use:
        with open(self.path, "wb") as f:
            f.write(self.content)

        # Write to logfile:
        with open("cache/logfile.txt", "a") as f:
            f.write("%s\n -- Accessed %s; \"%s\"; %.2f KiB\n" %
            (self.url, datetime.fromtimestamp(self.accessed), self.type, len(self.content) / 1024))

        # Save response meta-data:
        with open(self.path.parent / "response.json", "w") as f:
            f.write(json.dumps({
                "accessed": self.accessed,
                "url": str(self.url),
                "file": self.file,
                "type": self.type,
                "encoding": self.encoding,
                "statusCode": self.status_code
            }, indent=4))


class WebCacher:
    def get(url):
        wf = None
        if WebCacher.is_cached(url):
            wf = WebFile.from_cache(url)
        else:
            wf = WebFile.from_web(url)
            wf.save()
        return wf

    def download(url):
        wf = WebFile.from_web(url)
        wf.save()
        return wf

    def is_cached(url):
        path = pathlib.Path(URL.from_url(url).resolve_to_path()) / "response.json"
        return path.exists()


class WebCrawler:
    _crawled = []

    def crawl_url(url, times=1):
        if url in WebCrawler._crawled:
            return
        else:
            WebCrawler._crawled.append(url)
        print("Caching:  %s" % (url))
        try:
            wf = WebCacher.get(url)
            WebCrawler.crawl_file(wf, times=times)
        except:
            print("Fetching failed: %s" % (url))

    def crawl_file(wf, times=1):
        if times <= 0:
            return
        if wf.type != "text/html":
            return
        print("Crawling: %s" % (wf.url))
        for url in _get_urls(wf):
            WebCrawler.crawl_url(url, times=(times-1))

def _get_urls(wf):
    result = []
    try:
        content = wf.get_decoded_content()
        tree = lxml.html.fromstring(content) # Parse whole html tree

        for el in [["a", "href"], ["link", "href"], ["script", "src"], ["img", "src"]]: # Crawl elements with URL
            for link_element in tree.xpath('//' + el[0]):
                url = link_element.get(el[1])
                result.append(wf.url / url)
    except:
        pass
    return result

def _determine_extention(filename, mimetype):
    extension = ".html"
    i = filename.rfind(".")
    if i >= 0:
        extension = filename[i:]
    else:
        extension = mimetypes.guess_extension(mimetype)
        if not extension:
            extension = ".html"
    return extension