import sys, traceback, socket, re, urllib

def get_traceback_as_html():
    return "<b>ERROR: {}</b><br>{}<br><br><b>Traceback:</b><br>{}".format(
        sys.exc_info()[0].__name__, # Class name of exception
        str(sys.exc_info()[1]), # Description of exception
        "<br>".join(traceback.format_tb(sys.exc_info()[2])) # Traceback of exception
    )

def get_file(path):
    result = ""
    with open(path, "r") as f:
        result = f.read()
    return result

def check_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    # As suggested by https://stackoverflow.com/a/33117579
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:
        return False

def remove_unsafe_characters(path):
    result = []
    for chunk in path.split("/"):
        result.append(
            re.sub(r'[^a-zA-Z0-9_\-\.]', "_", chunk)
        )
    return "/".join(result)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP