from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

import apprise

from screenshot import screenshot_element

server = "http://127.0.0.1:4444"

# Notification URL List: post://xxx.xxx.xxx.xxx:xxxx

# Notification Body:
# {
#   "url": "{{watch_url}}",
#   "cssQueriesToDelete": [
#     "[role=\"navigation\"]",
#     "#onetrust-banner-sdk",
#     ".PatchNotesTop"
#   ],
#   "xPathToCapture": "//div[contains(@class, 'PatchNotes-patch') and contains(@class, 'PatchNotes-live')][1]",
#   "appriseURL": "discord://xxxxxxxxxxxxxxxxxxx/xx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/"
#   "appriseTitle": "Title"
#   "appriseBody": "A body"
# }

# Move Apprise to separate file
# Cleanup logs
# Refactor try / catches
# Configure Selenium driver and HTTP server setting through environment variables

class JSONRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(post_data)
            
            print("Incoming request")
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            print(" ↳ Starting screenshot flow...")
            screenshot_element(
                server=server,
                url=payload['url'],
                xpath=payload['xPathToCapture'],
                elements_to_remove=payload['cssQueriesToDelete'],
            )

            print(" ↳ Sending notification to Apprise...")
            try:
                apobj = apprise.Apprise()
                apobj.add(payload['appriseURL'])

                image_path = os.path.abspath("./image.png")
                if not os.path.exists(image_path):
                    print(f"Warning: Image file not found at {image_path}")

                attachment = apprise.AppriseAttachment()
                attachment_result = attachment.add(image_path)
                print(f"Attachment add result: {attachment_result}")

                apobj.notify(
                    title=payload['appriseTitle'],
                    body=payload['appriseBody'],
                    attach=attachment,
                )
            except Exception as e:
                print(f"Error sending notification: {e}")

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': 'Invalid JSON'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        print("Request processed")

def run(server_class=HTTPServer, handler_class=JSONRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
