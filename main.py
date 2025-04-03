import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class JSONRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(post_data)
            if 'message' in payload:
                message_json_str = payload['message']
                message_json = json.loads(message_json_str)
                print("Custom content from 'message' field:", json.dumps(message_json, indent=2))
                # TODO start screenshotting process here...
            else:
                print("No 'message' field found in the payload.")

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': 'Invalid JSON'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=JSONRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
