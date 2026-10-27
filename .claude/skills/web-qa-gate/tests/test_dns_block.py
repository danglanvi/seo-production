#!/usr/bin/env python3
"""test_dns_block.py: dnsRules() của _cdp.mjs chặn host tracking ở tầng DNS, Chrome headless thật không gửi được request nào tới host đó.

Ca thật 26/10/2026: Chrome headless chạy QA trên production lọt khoảng 12 page_view và 15 sự kiện thử vào GA4; chặn bằng
Network.setBlockedURLs không bắt được beacon gửi lúc đóng tab. Test dùng host "localhost" làm host tracking giả: trang ở 127.0.0.1
tải ảnh từ localhost; có luật DNS thì server không nhận lượt nào, không có luật thì nhận 1 lượt (đối chứng).
"""
import http.server
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
NODE = shutil.which("node")


def chrome_bin():
    p = subprocess.run([NODE, "-e", "import('" + (SCRIPTS / "_cdp.mjs").as_uri() + "').then(m=>console.log(m.chromeBin()))"],
                       capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def rules(block, resolve=None):
    arg = "undefined" if resolve is None else repr(resolve)
    p = subprocess.run([NODE, "-e", "import('" + (SCRIPTS / "_cdp.mjs").as_uri() + "').then(m=>console.log(m.dnsRules("
                        + repr(block).replace("'", '"') + ", " + arg + ") || ''))"], capture_output=True, text=True)
    return p.stdout.strip()


class T(unittest.TestCase):
    @unittest.skipUnless(NODE, "không có node")
    def test_rules_text(self):
        r = rules(["*googletagmanager.com*", "*facebook.com/tr*", "*clarity.ms*"], "example.test=127.0.0.1")
        self.assertTrue(r.startswith("--host-resolver-rules=MAP example.test 127.0.0.1, "))
        self.assertIn("MAP googletagmanager.com ~NOTFOUND, MAP *.googletagmanager.com ~NOTFOUND", r)
        self.assertNotIn("facebook.com", r)  # mẫu có path chỉ chặn bằng URL
        self.assertEqual(rules([]), "")

    @unittest.skipUnless(NODE, "không có node")
    def test_chrome_khong_goi_host_bi_chan(self):
        chrome = chrome_bin()
        if not chrome:
            self.skipTest("không có Chrome")
        hits = []

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.path.startswith("/hit"):
                    hits.append(self.headers.get("Host"))
                    body, ct = b"GIF89a", "image/gif"
                else:
                    body, ct = f'<html><body><img src="http://localhost:{port}/hit.gif">x</body></html>'.encode(), "text/html"
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.end_headers()
                self.wfile.write(body)

        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            def run(extra):
                prof = tempfile.mkdtemp()
                subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={prof}", *extra,
                                "--dump-dom", f"http://127.0.0.1:{port}/p"], capture_output=True, timeout=60)
                shutil.rmtree(prof, ignore_errors=True)
            run([])
            self.assertEqual(len(hits), 1, "đối chứng: không có luật DNS thì phải tới server")
            run([rules(["*localhost*"])])
            self.assertEqual(len(hits), 1, "có luật DNS thì không request nào tới host bị chặn")
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
