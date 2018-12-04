import os
import socketserver
import sys
import urllib.parse
from http.server import HTTPServer, CGIHTTPRequestHandler, SimpleHTTPRequestHandler


def get_handler():
    class ServerHandler(CGIHTTPRequestHandler):
        def do_HEAD(self):
            self._process_request(method="HEAD")

        def do_GET(self):
            self._process_request(method="GET")

        def do_POST(self):
            self._process_request(method="POST")

        def _process_request(self, method):
            # Check that the directory a file is in is in cgi_directories
            # so run_cgi can be called
            directory = os.path.dirname(self.path)
            if directory not in self.cgi_directories:
                self.cgi_directories.append(directory)
            # Check that the file is a .cgi file
            filepath = urllib.parse.urlparse(self.path).path
            if filepath.endswith(".cgi") and self.is_cgi():
                # self.send_head()
                self.run_cgi()  # handles GET and POST methods
            else:
                # self.send_head()
                file = SimpleHTTPRequestHandler.send_head(self)
                if file:
                    if method.upper() != "HEAD":
                        # while True:
                        #     chunk = file.read(8*1024)
                        #     if not chunk:
                        #         break
                        #     self.wfile.write(chunk)
                        self.copyfile(file, self.wfile)
                    file.close()

    return ServerHandler


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    return httpd


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Port is missing")
        exit(1)
    port = int(args[1])
    if len(args) < 3:
        print("Directory not specified")
        exit(1)
    dirname = args[2]

    # change directory to run the server from
    os.chdir(os.path.abspath(dirname))

    httpd = None
    try:
        httpd = run(ThreadedHTTPServer, get_handler(), port)
    except KeyboardInterrupt:
        print("Server closed")
    finally:
        if httpd:
            httpd.server_close()
