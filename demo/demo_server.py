# -*- coding: utf-8 -*-
"""VPN.lat demo server — :8908
Reconstructed hetecn API proxy + local cache. Research use only.
Endpoints:
  /api/servers          — country list (upstream /server)
  /api/cities/<id>      — city list
  /api/ovpn/<id>        — OpenVPN config fetch
  /api/wire/<id>        — WireGuard config fetch
  /api/status           — local health
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from vpnlat_client import get
from http.server import BaseHTTPRequestHandler, HTTPServer

PROXY = os.environ.get("VPNLAT_PROXY")  # optional http proxy in supported country

CACHE = {}

def cached(path):
    if path in CACHE: return CACHE[path]
    try:
        data = get(path, proxy=PROXY)
        CACHE[path] = (200, data)
    except urllib.error.HTTPError as e:
        CACHE[path] = (e.code, {"error": f"upstream {e.code}"})
    except Exception as e:
        CACHE[path] = (502, {"error": str(e)[:120]})
    return CACHE[path]

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        p = self.path
        if p == "/api/status":
            return self._send(200, {"ok": True, "cache": list(CACHE), "proxy": PROXY})
        try:
            if p == "/api/servers": return self._send(*cached("/server"))
            if p.startswith("/api/cities/"): return self._send(*cached(f"/country/{p.split('/')[-1]}/server"))
            if p.startswith("/api/ovpn/"): return self._send(*cached(f"/opvn/server/{p.split('/')[-1]}?cx=2"))
            if p.startswith("/api/wire/"): return self._send(*cached(f"/wire/server/{p.split('/')[-1]}?cx=2"))
            self._send(404, {"error": "not found"})
        except Exception as e:
            self._send(500, {"error": str(e)[:200]})
    def log_message(self, *a): pass

if __name__ == "__main__":
    port = int(os.environ.get("VPNLAT_PORT", "8908"))
    print(f"VPN.lat demo on :{port} proxy={PROXY}")
    HTTPServer(("127.0.0.1", port), H).serve_forever()
