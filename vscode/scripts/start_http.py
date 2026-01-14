# 使用以下代码启动服务器
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys, os

import argparse, os, glob, logging, json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s %(funcName)s:%(lineno)d]: %(message)s")

filepath = str(Path(__file__).resolve().parent)
logging.debug(f"filepath: {filepath}")


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        return super().end_headers()


if __name__ == "__main__":
    os.chdir(filepath + "/../assets")
    server_address = ("localhost", 8001)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    httpd.serve_forever()
