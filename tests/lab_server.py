"""Local dev server for portfolio.

Run: python tests/lab_server.py
Opens at http://127.0.0.1:8765

Safe to use as a verification target (no external dependencies,
no DB, no auth — pure static).
"""
import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 9292


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        # Disable caching during local dev
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[portfolio] " + fmt % args + "\n")


if __name__ == "__main__":
    print(f"Serving portfolio at http://127.0.0.1:{PORT}/")
    print("Press Ctrl+C to stop.")
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[portfolio] stopped.")
