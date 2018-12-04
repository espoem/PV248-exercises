import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse, request
import json
import re

http_re = re.compile(r"^https?://")

def get_handler(url):
    class ServerHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = parse.urlparse(self.path).query
            target_url = url
            match = http_re.match(target_url)
            if not match:
                target_url = "http://" + target_url
            if params:
                target_url = "{}?{}".format(target_url, params)

            headers = dict(self.headers)
            if "Host" in headers:
                del headers["Host"]

            new_request = request.Request(url=target_url, data=None, headers=headers, method="GET")
            try:
                with request.urlopen(new_request, timeout=1) as response:
                    content = response.read().decode("UTF-8")
                    prepared_data = self._output_dict(response.getcode(), response.getheaders(), content)
                    self.respond(200, prepared_data)
            except:
                prepared_data = self._output_dict("timeout")
                self.respond(200, prepared_data)

        def respond(self, status_code, content_dict):
            prepared_data = json.dumps(content_dict, indent=2)
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=UTF-8")
            self.send_header("Content-Length", str(len(prepared_data)))
            self.wfile.write(bytes(prepared_data, "UTF-8"))

        @staticmethod
        def _output_dict(status_code, headers=None, content=None):
            output = {"code": status_code}
            if headers:
                if isinstance(headers, dict):
                    output["headers"] = dict(headers)
                else:
                    output["headers"] = {}
                    for header, value in headers:
                        output["headers"][header] = value
            if content:
                try:
                    output["json"] = json.loads(content)
                except ValueError:
                    output["content"] = content

            return output

        @staticmethod
        def _output_json(self, status_code, headers=None, content=None):
            output = self._output_dict(status_code, headers, content)
            return json.dumps(output, indent=2)

        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            content = self.rfile.read(content_length)

            try:
                content_dict = json.loads(content)
            except ValueError:
                prepared_data = self._output_dict("invalid json")
                self.respond(200, prepared_data)
                return

            method = "GET"
            if "type" in content_dict:
                method = content_dict["type"].upper()

            if "url" not in content_dict or (method == "POST" and "content" not in content_dict):
                prepared_data = self._output_dict("invalid json")
                self.respond(200, prepared_data)
                return

            target_url = content_dict["url"]
            match = http_re.match(target_url)
            if not match:
                target_url = "http://" + target_url
            headers = content_dict.get("headers", {})
            timeout = content_dict.get("timeout", 1)

            has_content_type = False
            for k in headers.keys():
                if k.lower() == 'content-type':
                    has_content_type = True
                    break
            if not has_content_type:
                headers["Content-Type"] = "text/plain"

            data = None
            if method == "POST":
                data = bytes(content_dict.get("content", ""), "UTF-8")

            new_request = request.Request(url=target_url, data=data, headers=headers, method=method)
            try:
                with request.urlopen(new_request, timeout=timeout) as response:
                    res_content = response.read().decode("UTF-8")
                    prepared_data = self._output_dict(response.getcode(), headers=response.getheaders(), content=res_content)
                    self.respond(200, prepared_data)
            except:
                prepared_data = self._output_dict('timeout')
                self.respond(200, prepared_data)

    return ServerHandler


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, port=8000):
    server_address = ('', port)
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
        print("Target URL not specified")
        exit(1)
    url = args[2]

    httpd = None
    try:
        httpd = run(HTTPServer, get_handler(url), port)
    except KeyboardInterrupt:
        print("Server closed")
    finally:
        if httpd:
            httpd.server_close()
