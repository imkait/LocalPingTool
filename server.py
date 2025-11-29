import http.server
import socketserver
import subprocess
import platform
import urllib.parse
import json
import os
import sys
import csv

PORT = 8000

# 判斷是否在 PyInstaller 打包環境中執行
if getattr(sys, 'frozen', False):
    DIRECTORY = sys._MEIPASS
    # 執行檔模式下，CSV 應該存在執行檔同級目錄，而不是暫存目錄
    # sys.executable 是執行檔的路徑
    DATA_DIR = os.path.dirname(sys.executable)
else:
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = DIRECTORY

CSV_FILE = os.path.join(DATA_DIR, 'ips.csv')

class PingRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/ping':
            self.handle_ping(parsed_path.query)
        elif parsed_path.path == '/api/ips':
            self.handle_get_ips()
        else:
            super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/ips':
            self.handle_save_ips()
        else:
            self.send_error(404, "Not Found")

    def handle_get_ips(self):
        ips = []
        if os.path.exists(CSV_FILE):
            try:
                with open(CSV_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2:
                            # 支援舊格式 (name, ip) 與新格式 (name, ip, type)
                            item = {'name': row[0], 'ip': row[1]}
                            if len(row) >= 3:
                                item['type'] = row[2]
                            else:
                                item['type'] = 'server' # 預設值
                            ips.append(item)
            except Exception as e:
                print(f"Error reading CSV: {e}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(ips).encode())

    def handle_save_ips(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            # data 預期為 [{'name': '...', 'ip': '...', 'type': '...'}, ...]
            
            with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for item in data:
                    writer.writerow([
                        item.get('name', ''), 
                        item.get('ip', ''),
                        item.get('type', 'server')
                    ])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except Exception as e:
            self.send_error(500, str(e))

    def handle_ping(self, query_string):
        query_params = urllib.parse.parse_qs(query_string)
        ip = query_params.get('ip', [None])[0]

        if not ip:
            self.send_error(400, "Missing IP parameter")
            return

        # 簡單的安全檢查
        allowed_chars = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:")
        if not set(ip).issubset(allowed_chars):
             self.send_response(400)
             self.send_header('Content-type', 'application/json')
             self.end_headers()
             self.wfile.write(json.dumps({"status": "invalid_ip"}).encode())
             return

        # 判斷作業系統以決定 ping 指令參數
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        command = ['ping', param, '1']
        
        if platform.system().lower() == 'darwin': # macOS
             command.extend(['-W', '1000', ip])
        elif platform.system().lower() == 'windows':
             command.extend(['-w', '1000', ip])
        else: # Linux
             command.extend(['-W', '1', ip])

        try:
            # Capture stdout to parse latency
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            is_alive = (result.returncode == 0)
            latency = None
            
            if is_alive:
                # Parse latency using regex
                # Windows: time=10ms
                # Unix/macOS: time=10.5 ms or time=10 ms
                import re
                output = result.stdout
                match = re.search(r'time=([\d.]+)\s*ms', output, re.IGNORECASE)
                if match:
                    try:
                        latency = float(match.group(1))
                    except ValueError:
                        pass

            response_data = {
                "status": "ok" if is_alive else "unreachable", 
                "ip": ip,
                "latency": latency
            }

        except Exception as e:
            response_data = {"status": "error", "message": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

import webbrowser

if __name__ == "__main__":
    # 確保在正確的目錄執行
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), PingRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Serving at {url}")
        print(f"Press Ctrl+C to stop.")
        
        # 自動開啟瀏覽器
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
