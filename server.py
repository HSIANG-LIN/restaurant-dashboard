#!/usr/bin/env python3
"""美食地圖 Dashboard Server"""
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser

PORT = 8788
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        # CORS headers so the HTML can fetch restaurants.json freely
        if self.path == '/restaurants.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            with open(os.path.join(DIR, 'restaurants.json'), 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
            return
        return super().do_GET()

if __name__ == '__main__':
    print(f'\n  🍽️  美食地圖已啟動！')
    print(f'  📍 http://localhost:{PORT}/dashboard.html')
    print(f'  ⏎ 按 Ctrl+C 停止\n')
    webbrowser.open(f'http://localhost:{PORT}/dashboard.html')
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
