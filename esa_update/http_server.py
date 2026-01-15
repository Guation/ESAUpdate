#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"

import json, threading, time
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from .esa_api import update_ip, update_port
from logging import debug, info, warning, error

class JSONRequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        self._set_headers(200)
        self.wfile.write("https://github.com/Guation/ESAUpdate".encode('utf-8'))
    
    def do_POST(self):
        # parsed_path = urlparse(self.path)
        content_type = self.headers.get('Content-Type', '')
        if content_type != 'application/json':
            self._set_headers(400)
            response = {
                "error": "无效的内容类型，请使用application/json",
                "status": "error"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            debug(json_data)
            if json_data["type"] == "A":
                update_ip(json_data["data"])
            elif json_data["type"] == "SRV":
                update_port(json_data["port"])
            response = {
                "error": "",
                "status": "success"
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except json.JSONDecodeError:
            self._set_headers(400)
            response = {
                "error": "无效的JSON数据",
                "status": "error"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(ip: str, port: int):
    with socketserver.TCPServer((ip, port), JSONRequestHandler) as httpd:
        info(f"服务器运行在 http://{ip}:{port}")
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            info("服务器已停止")
