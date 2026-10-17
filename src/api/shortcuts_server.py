"""
Flow Studio — Apple Shortcuts & Remote Webhook API Server
Runs a lightweight HTTP server on port 8503 to allow iPhone Shortcuts
and Siri to trigger autonomous video generation remotely.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

API_PORT = 8503
_server_instance = None
_server_thread = None


class ShortcutsHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, status_code: int, data: dict):
        response = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/health", "/api/health"):
            self._send_json(200, {
                "status": "online",
                "app": "Flow Studio",
                "version": "2.5.0",
                "device": "Mac",
                "dashboard_url": "http://Efe-Dizustu-Bilgisayar.local:8502"
            })
            return

        if path == "/api/status":
            from config.settings import CANDIDATES_DIR
            num_candidates = len(list(Path(CANDIDATES_DIR).glob("short_*"))) if Path(CANDIDATES_DIR).exists() else 0
            self._send_json(200, {
                "status": "online",
                "ready_candidates": num_candidates,
                "message": f"Flow Studio aktif. {num_candidates} adet hazır aday video var."
            })
            return

        if path == "/api/generate":
            self._trigger_generation(parsed)
            return

        self._send_json(404, {"error": "Not Found", "available_endpoints": ["/health", "/api/status", "/api/generate"]})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/generate":
            self._trigger_generation(parsed)
        else:
            self._send_json(404, {"error": "Not Found"})

    def _trigger_generation(self, parsed):
        params = parse_qs(parsed.query)
        topic = params.get("topic", [None])[0]

        def _worker():
            try:
                from src.automation.flow_cdp_bot import FlowCDPBot
                bot = FlowCDPBot()
                bot.generate_flow_video_full_auto(topic=topic)
            except Exception as e:
                print(f"[ShortcutsAPI] Remote generation error: {e}")

        worker_thread = threading.Thread(target=_worker, daemon=True)
        worker_thread.start()

        self._send_json(200, {
            "status": "started",
            "message": "🎬 Flow Studio: 3D Video üretimi Mac'inizde başlatıldı!",
            "topic": topic or "Rastgele En Viral Trend"
        })


def start_shortcuts_api():
    """Starts the lightweight Shortcuts API server in a background daemon thread."""
    global _server_instance, _server_thread

    if _server_instance is not None:
        return

    try:
        server = HTTPServer(("0.0.0.0", API_PORT), ShortcutsHandler)
        _server_instance = server

        def serve():
            print(f"[ShortcutsAPI] iPhone Shortcuts API dinleniyor: http://0.0.0.0:{API_PORT}")
            server.serve_forever()

        t = threading.Thread(target=serve, daemon=True)
        t.start()
        _server_thread = t
    except Exception as e:
        print(f"[ShortcutsAPI] Sunucu başlatılamadı: {e}")


if __name__ == "__main__":
    start_shortcuts_api()
    import time
    while True:
        time.sleep(1)
