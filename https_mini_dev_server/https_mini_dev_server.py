#!/usr/bin/env python3

import http.server, ssl, os, sys

serverdir = os.path.dirname(os.path.abspath(__file__))
pem = serverdir + '/server.pem'
os.chdir(os.path.join(serverdir, os.pardir))
port = int(sys.argv[1]) if len(sys.argv) == 2 else 4343
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        http.server.SimpleHTTPRequestHandler.end_headers(self)
httpd = http.server.HTTPServer(('0.0.0.0', port), RequestHandler)
if not os.path.isfile(pem):
    os.system(f'openssl req -new -x509 -keyout {pem} -out {pem} -days 3650 -nodes -subj /C=US')
httpd.socket = ssl.wrap_socket(httpd.socket, certfile=pem, server_side=True)
print(f'https://localhost:{port}/')
httpd.serve_forever()
