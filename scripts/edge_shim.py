#!/usr/bin/env python3
import os, re, json, tarfile, urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.environ.get("EDGE_REPO_ROOT", "/srv/edge-repo")  # base dir for artifacts

def chart_info_from_tgz(path):
    """Read Chart.yaml inside a .tgz and return (name, version)."""
    try:
        with tarfile.open(path, "r:gz") as tf:
            member = next((m for m in tf.getmembers()
                           if m.name.endswith("Chart.yaml") or m.name.endswith("Chart.yml")), None)
            if not member:
                return (None, None)
            data = tf.extractfile(member).read().decode("utf-8", errors="ignore")
            name = re.search(r'^\s*name:\s*([A-Za-z0-9._-]+)\s*$', data, re.M)
            ver  = re.search(r'^\s*version:\s*([A-Za-z0-9._+-]+)\s*$', data, re.M)
            return (name.group(1) if name else None, ver.group(1) if ver else None)
    except Exception:
        return (None, None)

def list_charts(repo="edge-helm-platinum", subpath="api/charts", filter_name=None):
    """Return AQL-like items for .tgz charts under repo/subpath."""
    charts_dir = os.path.join(ROOT, repo, *subpath.split("/"))
    results = []
    if not os.path.isdir(charts_dir):
        return results
    for fname in sorted(os.listdir(charts_dir)):
        if not fname.endswith(".tgz"):
            continue
        fpath = os.path.join(charts_dir, fname)
        name, version = chart_info_from_tgz(fpath)
        if not name or not version:
            m = re.match(r"(.+)-([0-9].+)\.tgz$", fname)
            if m:
                name, version = m.group(1), m.group(2)
        if filter_name and name != filter_name:
            continue
        results.append({
            "repo": repo,
            "path": subpath,
            "name": fname,
            # add both a properties list and a convenience field
            "@chart.version": version if version else "",
            "properties": [
                {"key": "chart.name", "value": name if name else ""},
                {"key": "chart.version", "value": version if version else ""}
            ]
        })
    return results

def wanted_chart_from_aql_body(body_bytes):
    """Detect the chart name filter in the AQL body."""
    b = body_bytes.decode("utf-8", errors="ignore")
    if '"@chart.name":"edge-cd"' in b:
        return "edge-cd"
    if '"@chart.name":"collibra-edge"' in b:
        return "collibra-edge"
    return None  # no filter

class Handler(SimpleHTTPRequestHandler):
    # Map /artifactory/* onto ROOT/*, and rewrite flat installer path to nested
    def translate_path(self, path):
        if not path.startswith("/artifactory/"):
            return super().translate_path(path)

        # flat form: /artifactory/edge-generic-prod/installer-<ver>.tgz
        if re.match(r"^/artifactory/edge-generic-prod/installer-[^/]+\.tgz$", path):
            ver = re.search(r"installer-([^/]+)\.tgz$", path).group(1)
            path = f"/artifactory/edge-generic-prod/installer/{ver}/installer-{ver}.tgz"

        rel = urllib.parse.unquote(path[len("/artifactory/"):])
        return os.path.join(ROOT, rel)

    def do_POST(self):
        if self.path == "/artifactory/api/search/aql":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length > 0 else b""
            chart_filter = wanted_chart_from_aql_body(body)
            items = list_charts(filter_name=chart_filter)

            payload = {
                "results": items,
                "range": {"start_pos": 0, "end_pos": len(items), "total": len(items)}
            }
            data = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_POST()

    def do_GET(self):
        # optional properties endpoint for debugging
        if self.path.startswith("/artifactory/api/storage/") and self.path.endswith("?properties"):
            rel = urllib.parse.unquote(self.path[len("/artifactory/api/storage/"):-len("?properties")])
            fs_path = os.path.join(ROOT, rel)
            props = {}
            if os.path.exists(fs_path) and fs_path.endswith(".tgz"):
                n, v = chart_info_from_tgz(fs_path)
                if n and v:
                    props = {"chart.name": [n], "chart.version": [v]}
            resp = {
                "repo": rel.split("/", 1)[0] if "/" in rel else rel,
                "path": "/" + rel.split("/", 1)[1] if "/" in rel else "/",
                "size": str(os.path.getsize(fs_path)) if os.path.exists(fs_path) else "0",
                "properties": props
            }
            data = json.dumps(resp).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--bind", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--root", default=ROOT)
    args = p.parse_args()
    ROOT = args.root
    httpd = HTTPServer((args.bind, args.port), Handler)
    print(f"edge-shim serving {ROOT} on {args.bind}:{args.port}")
    httpd.serve_forever()
