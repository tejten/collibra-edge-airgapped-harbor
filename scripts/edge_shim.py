#!/usr/bin/env python3
"""
Minimal AQL-like shim for serving Helm charts from a flat file system.

This is a simplified placeholder. In production, replace with your vetted shim.
It exposes:
  - GET  /healthz               -> "ok"
  - GET  /artifactory/<path>    -> static file serving under --root
  - POST /artifactory/api/search/aql -> returns a toy JSON for demo

Usage:
  python3 edge_shim.py --root /srv/edge-repo --port 8080
"""
import argparse, http.server, socketserver, os, json

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type","text/plain")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return
        if self.path.startswith("/artifactory/"):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        return super().do_GET()

    def do_POST(self):
        if self.path == "/artifactory/api/search/aql":
            body = {
                "results": [
                    {"repo":"edge-helm-platinum","path":"api/charts","name":"collibra-edge","@chart.version":"2025.6.77-3"}
                ],
                "range": {"start_pos": 0, "end_pos": 1, "total": 1}
            }
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_POST()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Root directory that contains edge-helm-platinum, etc.")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()

    os.chdir(args.root)
    with socketserver.TCPServer(("", args.port), Handler) as httpd:
        print(f"Shim serving from {args.root} on :{args.port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
