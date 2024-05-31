#!/usr/bin/env python3

import http.server
import os
import re
import socket
import socketserver
import ssl
import sys


def ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))  # doesn't even have to be reachable
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


serverdir = os.path.dirname(os.path.abspath(__file__))
httpdir = serverdir + '/..'
pem = serverdir + '/server.pem'
port = int(sys.argv[1]) if len(sys.argv) == 2 else 4343
if not os.path.isfile(pem):
    os.system(f'openssl req -new -x509 -keyout {pem} -out {pem} -days 3650 -nodes -subj /C=US')

_route_get = []
_route_post = []


def route_GET(pattern, fct):
    _route_get.append((re.compile(pattern), fct))


def route_POST(pattern, fct):
    _route_post.append((re.compile(pattern), fct))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=httpdir, **kwargs)

    def _redirect301(self, url):
        self.send_response(301)
        self.send_header("Location", url)
        self.end_headers()

    def _send_html(self, html):
        self._send_text(html, "text/html")

    def _send_text(self, text, ctype = "text/plain"):
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def do_GET(self):
        for p, f in _route_get:
            m = p.match(self.path)
            if m:
                g = m.groups() or []
                f(self, *g)
                break
        else:
            super().do_GET()

    def do_POST(self):
        for p, f in _route_post:
            m = p.match(self.path)
            if m:
                g = m.groups() or []
                f(self, *g)
                break
        else:
            super().do_POST()


route_GET(r"^/index.htm$", lambda s: s._redirect301('/'))

with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f'https://{ip()}:{port}/')
    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslctx.load_cert_chain(pem)
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    httpd.socket = sslctx.wrap_socket(httpd.socket)
    httpd.serve_forever()
