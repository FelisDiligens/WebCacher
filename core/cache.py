from core.url import URL
from core.locals import *
import core.database as database
import urllib, pathlib, mimetypes, json, time, requests, os, io
from flask import send_file
from datetime import datetime
import uuid

class WebFile:
    def __init__(self):
        self.uuid = ""
        self.accessed = -1
        self.url = ""
        self.path = ""
        self.type = ""
        self.encoding = "utf-8"
        self.content = None
        self.status_code = -1
        self.size = 0

    def from_cache(url):
        wf = WebFile()
        wf.url = URL.from_url(url)

        row = database.get(wf.url)
        if not row:
            return None

        wf.uuid = row[0]
        wf.type = row[2]
        wf.size = row[3]
        wf.accessed = row[4]
        wf.encoding = row[5]
        wf.status_code = row[6]

        wf.path = pathlib.Path(".\\cache") / wf.uuid

        with open(wf.path, "rb") as f:
            wf.content = f.read()

        return wf

    def from_web(url, headers=None):
        wf = WebFile()
        wf.url = URL.from_url(url)
        wf.accessed = time.time()

        # Requesting file from web server:
        response = requests.get(wf.url.resolve(), timeout=60, headers=headers)

        # Extract info:
        wf.encoding = response.apparent_encoding
        if wf.encoding is None:
            wf.encoding = response.encoding
        wf.content = response.content
        wf.type = response.headers.get('content-type')
        # "text/html; charset=utf-8"
        if ';' in wf.type:
            wf.type = wf.type[:wf.type.find(';')]
        wf.status_code = response.status_code

        # filename_extension = _determine_extention(wf.url.get_filename(), wf.type)

        wf.uuid = str(uuid.uuid4())

        #wf.path = pathlib.Path(wf.url.resolve_to_path()) / wf.file
        wf.path = pathlib.Path(".\\cache") / wf.uuid

        wf.size = len(wf.content)

        return wf

    def get_decoded_content(self):
        return self.content.decode(self.encoding, errors="ignore")

    def set_decoded_content(self, content):
        self.content = content.encode(self.encoding)

    def send_file(self):
        return send_file(
            io.BytesIO(self.content),
            mimetype=self.type)

    def save(self):
        # Create folders:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Cache for later use:
        with open(self.path, "wb") as f:
            f.write(self.content)

        # Save response meta-data:
        database.insert(self)

class WebCacher:
    def get(url, headers=None):
        wf = WebFile.from_cache(url)
        if not wf:
            if get_config()["verbose"]:
                print("[Web] Loading: " + url)
            wf = WebFile.from_web(url, headers)
            wf.save()
        else:
            if get_config()["verbose"]:
                print("[Web] Cached: " + url)
        return wf

    def download(url):
        wf = WebFile.from_web(url)
        wf.save()
        return wf

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