#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 بوابة API آمنة لـ XMRig — تحقق من التوكن + CORS + توجيه للمنجم المحلي
التشغيل: python3 serve.py
ثم: cloudflared tunnel --url http://localhost:8080
"""
import hmac
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen

XMRIG_API = "http://127.0.0.1:10000"   # منفذ XMRig API المحلي
API_TOKEN = "Rbpt_I3VmYHjZ-Csu-rUAedbuqX0XvMl"                  # 🔑 التوكن السري — انسخه للوحة التحكم

class Handler(SimpleHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            # التحقق من التوكن
            auth = self.headers.get("Authorization", "")
            if not hmac.compare_digest(auth, f"Bearer {API_TOKEN}"):
                self.send_response(401); self._cors(); self.end_headers()
                self.wfile.write(b'{"error":"unauthorized"}')
                return
            try:
                with urlopen(XMRIG_API + self.path[4:]) as r:
                    data = r.read()
                self.send_response(200); self._cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(502); self._cors(); self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    print("🔐 البوابة تعمل: http://127.0.0.1:8080")
    print("🔑 التوكن الخاص بك:", API_TOKEN)
    HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
