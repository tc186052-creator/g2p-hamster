"""HTTP API cho g2p-hamster — thuần stdlib, không thêm dependency.

Chạy:   python3 -m g2p_hamster.serve --port 8080
Dùng:   curl -s localhost:8080/g2p -d '{"text":"HLV của HAGL họp HĐQT tại TP.HCM."}'

Endpoint:
  GET  /health  → {"ok": true, "version": …}
  POST /g2p     → body {"text": "…"} hoặc {"texts": ["…", …]}
                → JSON kết quả như cli.py (một object hoặc mảng),
                  kèm "errors" cho câu nào xử lý hỏng.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .g2p_v2 import text_to_profile_v2_full


def _run(texts):
    results, errors = [], {}
    for i, s in enumerate(texts):
        try:
            r = text_to_profile_v2_full(s)
            r["text"] = s
            results.append(r)
        except Exception as e:
            results.append({"text": s, "state": "error"})
            errors[str(i)] = f"{type(e).__name__}: {e}"
    return results, errors


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            from . import __version__
            self._send(200, {"ok": True, "version": __version__})
        else:
            self._send(404, {"error": "chỉ có /health và POST /g2p"})

    def do_POST(self):
        if self.path != "/g2p":
            self._send(404, {"error": "chỉ có /health và POST /g2p"})
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            self._send(400, {"error": f"body không phải JSON: {e}"})
            return
        texts = payload.get("texts") or ([payload["text"]]
                                         if payload.get("text") else None)
        if not texts or not all(isinstance(t, str) for t in texts):
            self._send(400, {"error": 'cần {"text": "…"} hoặc {"texts": […]}'})
            return
        results, errors = _run(texts)
        out = {"results": results}
        if len(results) == 1 and not errors:
            self._send(200, results[0])
        else:
            out["errors"] = errors
            self._send(200, out)

    def log_message(self, *a):   # im log mặc định ra stderr mỗi request
        pass


def main():
    ap = argparse.ArgumentParser(description="g2p-hamster HTTP API")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="0.0.0.0")
    a = ap.parse_args()
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
