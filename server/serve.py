"""Serve Ancient Works from this Mac: the page and its data from web/, a small JSON document store, and live
LiDAR relief tiles.

usage: .venv/bin/python server/serve.py [--lan] [--port 8642] [--allow 10.0.0.0/16 ...]
   (the normal run is /Users/ethan/code/projects/ancient-works/.venv/bin/python server/serve.py --lan)

  default   listens on 127.0.0.1 only
  --lan     listens on every interface so a phone on the home Wi-Fi can open it; requests from addresses
            outside --allow (default: loopback + 10.0.0.0/16, the home VLANs) are refused outright, so the
            site stays closed on other networks the Mac joins

Document store (replaces the claude.ai artifact database the page used before):
  GET    /api/db/<collection>          -> {"docs": [{"id": ..., "data": {...}}, ...]}
  GET    /api/db/<collection>/<doc>    -> the document, or 404
  PUT    /api/db/<collection>/<doc>    -> replace the document (JSON object body)
  DELETE /api/db/<collection>/<doc>
Documents live in data/db/<collection>/<doc>.json.

Relief tiles (server/relief_tiles.py; needs numpy/scipy/PIL, i.e. the venv python):
  GET    /tiles/relief/<z>/<x>/<y>.png -> z 12-17; transparent outside LiDAR coverage; 503 while a DEM
                                          service is failing. DEMs and PNGs are cached in data/tilecache/.
The rest is stdlib only, so the system python3 still runs the site; tiles then answer 404.
"""
import argparse
import ipaddress
import json
import os
import re
import select
import socket
import sys
import tempfile
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DB = os.path.join(ROOT, "data", "db")
SEG = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]{0,199}$")
TILE = re.compile(r"^/tiles/relief/(\d{1,2})/(\d{1,6})/(\d{1,6})\.png$")
RELIEF = None  # the relief_tiles module, when numpy & co. are importable (see main)
MAX_BODY = 1 << 20


class Handler(SimpleHTTPRequestHandler):
    allow = []

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEB, **kw)

    # ---- access ----
    def allowed(self):
        ip = ipaddress.ip_address(self.client_address[0])
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        return any(ip in net for net in self.allow)

    def refuse(self):
        self.send_error(HTTPStatus.FORBIDDEN, "not on the home network")

    # ---- static ----
    def end_headers(self):
        path = self.path.split("?")[0]
        # the page and the site index change on every build; images under data/sites/ are rebuilt rarely
        if path in ("/", "/index.html") or path.endswith(".json"):
            self.send_header("Cache-Control", "no-cache")
        elif path.startswith(("/data/", "/vendor/")):
            self.send_header("Cache-Control", "max-age=3600")
        super().end_headers()

    def do_GET(self):
        if not self.allowed():
            return self.refuse()
        if self.path.startswith("/api/"):
            return self.api("GET")
        if self.path.startswith("/tiles/"):
            return self.tile()
        super().do_GET()

    def do_HEAD(self):
        if not self.allowed():
            return self.refuse()
        super().do_HEAD()

    def do_PUT(self):
        if not self.allowed():
            return self.refuse()
        self.api("PUT")

    def do_DELETE(self):
        if not self.allowed():
            return self.refuse()
        self.api("DELETE")

    # ---- relief tiles ----
    def tile(self):
        m = TILE.match(self.path.split("?")[0])
        if not m or RELIEF is None:
            return self.send_error(HTTPStatus.NOT_FOUND)
        try:
            body = RELIEF.tile(*map(int, m.groups()), alive=self.client_waiting)
        except ValueError:
            return self.send_error(HTTPStatus.NOT_FOUND)
        except RELIEF.Cancelled:
            self.close_connection = True
            return
        except RELIEF.Unavailable:
            self.send_response(HTTPStatus.SERVICE_UNAVAILABLE)
            self.send_header("Retry-After", str(RELIEF.RETRY_AFTER_S))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            super().end_headers()
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=86400")
        super().end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):  # the map dropped a tile it no longer shows
            pass

    def client_waiting(self):
        """False once the browser has closed this connection (MapLibre aborts tiles that left the view)."""
        try:
            ready, _, _ = select.select([self.connection], [], [], 0)
            return not ready or self.connection.recv(1, socket.MSG_PEEK) != b""
        except OSError:
            return False

    # ---- api ----
    def reply(self, code, obj=None):
        body = json.dumps(obj if obj is not None else {}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
        self.wfile.write(body)

    def api(self, method):
        parts = self.path.split("?")[0].strip("/").split("/")
        if len(parts) not in (3, 4) or parts[:2] != ["api", "db"] or not all(SEG.match(p) for p in parts[2:]):
            return self.reply(404, {"error": "unknown path"})
        coll = os.path.join(DB, parts[2])
        if len(parts) == 3:
            if method != "GET":
                return self.reply(405, {"error": "collections are read-only"})
            docs = []
            if os.path.isdir(coll):
                for f in sorted(os.listdir(coll)):
                    if f.endswith(".json"):
                        try:
                            docs.append({"id": f[:-5], "data": json.load(open(os.path.join(coll, f)))})
                        except (OSError, ValueError):
                            pass
            return self.reply(200, {"docs": docs})
        path = os.path.join(coll, parts[3] + ".json")
        if method == "GET":
            if not os.path.exists(path):
                return self.reply(404, {"error": "no such document"})
            return self.reply(200, json.load(open(path)))
        if method == "DELETE":
            if os.path.exists(path):
                os.remove(path)
            return self.reply(200, {"ok": True})
        n = int(self.headers.get("Content-Length") or 0)
        if not 0 < n <= MAX_BODY:
            return self.reply(413, {"error": "body missing or over 1 MB"})
        try:
            data = json.loads(self.rfile.read(n))
        except ValueError:
            return self.reply(400, {"error": "body is not JSON"})
        if not isinstance(data, dict):
            return self.reply(400, {"error": "a document is a JSON object"})
        os.makedirs(coll, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=coll, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, path)
        return self.reply(200, {"ok": True})

    def log_message(self, fmt, *args):
        if self.path.startswith("/api/") or (args and str(args[1]) not in ("200", "304")):
            sys.stderr.write("%s %s\n" % (self.client_address[0], fmt % args))


def lan_address():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.0.10.1", 53))  # no packet is sent; this only picks the outgoing interface
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lan", action="store_true", help="listen on the home network, not just this Mac")
    ap.add_argument("--port", type=int, default=8642)
    ap.add_argument("--allow", action="append", default=None, help="client network allowed with --lan")
    a = ap.parse_args()
    nets = ["127.0.0.0/8", "::1/128"] + ((a.allow or ["10.0.0.0/16"]) if a.lan else [])
    Handler.allow = [ipaddress.ip_network(n) for n in nets]
    host = "0.0.0.0" if a.lan else "127.0.0.1"
    global RELIEF
    try:
        import relief_tiles
        RELIEF = relief_tiles
    except ImportError as e:
        print(f"relief tiles off ({e.name or e} not importable); run with .venv/bin/python for the LiDAR relief layer",
              flush=True)
    srv = ThreadingHTTPServer((host, a.port), Handler)
    print(f"Ancient Works on http://127.0.0.1:{a.port}/", flush=True)
    if a.lan:
        ip = lan_address()
        print(f"  home network: http://{ip}:{a.port}/  (allowed clients: {', '.join(nets[2:])})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
