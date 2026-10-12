# Local dev server for the rules page. Same as `python3 -m http.server 3000`,
# but tells the browser not to cache, so CSS and HTML edits show on reload.
import http.server


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    serverPort = 3000
    server = http.server.ThreadingHTTPServer(("", serverPort), NoCacheHandler)
    print(f"Serving on http://localhost:{serverPort}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
