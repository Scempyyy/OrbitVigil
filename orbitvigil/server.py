"""OrbitVigil Web Dashboard HTTP Server."""

import http.server
import json
import os
import socketserver
import urllib.parse
from orbitvigil.checker import check_site_health, find_broken_links


WEB_DIR = os.path.join(os.path.dirname(__file__), "web")


class OrbitVigilHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"service": "OrbitVigil", "status": "online"}).encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if parsed.path == "/api/check":
            url = payload.get("url", "https://google.com")
            crawl_links = payload.get("crawl_links", False)

            health = check_site_health(url)

            broken_links = []
            if crawl_links and health.get("body_preview"):
                broken_links = find_broken_links(url, health["body_preview"])

            # Remove body preview before returning JSON
            health.pop("body_preview", None)
            health["links"] = broken_links

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(health).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def start_monitor_server(host: str = "127.0.0.1", port: int = 8950):
    class ReuseAddressServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReuseAddressServer((host, port), OrbitVigilHTTPHandler) as httpd:
        print(f"\n🛰️  OrbitVigil Website Health Monitor live at http://{host}:{port}")
        print("Press Ctrl+C to terminate.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nMonitor terminated cleanly.")
