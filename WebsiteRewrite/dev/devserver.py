# Local preview with fake sensor data. Not part of the website: do not upload.
# Usage (from D:/PortfolioProjects): python -I WebsiteRewrite/dev/devserver.py WebsiteRewrite  ->  http://127.0.0.1:8123/
import http.server, json, math, time, functools, sys
ROOT = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/sensor.php"):
            now = int(time.time()); ts = [now - i*600 for i in range(1008)][::-1]
            t = [21 + 1.5*math.sin(i/72*math.pi) for i in range(len(ts))]
            p = [1013 + 4*math.sin(i/300) for i in range(len(ts))]
            h = [0.0]*len(ts)
            body = {"ok": True, "count": len(ts), "latest": {"recorded_at": ts[-1], "temperature": t[-1], "humidity": 0.0, "pressure": p[-1]},
                    "series": {"timestamps": ts, "temperatures": t, "humidities": h, "pressures": p}}
            return self.send_json(body)
        if self.path.startswith("/PHP/sendMail.php?csrf=1"):
            return self.send_json({"token": "dev"})
        return super().do_GET()
    def do_POST(self):
        return self.send_json({"success": False, "error": "Dev server does not send mail."}, 400)
    def send_json(self, body, status=200):
        data = json.dumps(body).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", 8123), functools.partial(H, directory=ROOT)).serve_forever()
