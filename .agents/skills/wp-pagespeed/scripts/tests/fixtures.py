# Dữ liệu giả cho test offline của wp-pagespeed. Không gọi mạng ngoài 127.0.0.1.
import base64
import io
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(script, *argv, env=None, input_=None, timeout=120, cwd=None):
    """Chạy script trong scripts/. .py chạy bằng python3 -I như SKILL.md, .mjs chạy bằng node."""
    # Chốt an toàn: psi_run.py thật sự đo phải trỏ vào server giả. Không bao giờ để test gọi API Google với key của workspace.
    if script == 'psi_run.py' and not ({'--api-base', '--dry-run', '--help'} & set(argv)):
        raise AssertionError('test psi_run.py phải có --api-base trỏ server giả')
    exe = ['python3', '-I'] if script.endswith('.py') else ['node']
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(exe + [os.path.join(SCRIPTS, script)] + list(argv), capture_output=True, text=True, env=e, timeout=timeout, input=input_, cwd=cwd)


def tiny_jpeg_data_uri():
    try:
        from PIL import Image
    except ImportError:
        return 'data:image/jpeg;base64,' + base64.b64encode(b'\xff\xd8\xff\xd9').decode()
    b = io.BytesIO()
    Image.new('RGB', (8, 6), (200, 30, 30)).save(b, 'JPEG')
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def psi_json(score=90, lcp=1500, cls=0.0, bench=1000.0, tbt=50, dev='mobile', shifts=None, pad=True, fcp=900):
    au = {
        'metrics': {'numericValue': 0, 'details': {'type': 'debugdata', 'items': [{'totalBlockingTime': tbt, 'largestContentfulPaint': lcp,
                                                                                    'observedFirstContentfulPaint': fcp, 'observedTraceEnd': 3000, 'observedLoad': 600}]}},
        'largest-contentful-paint': {'numericValue': lcp},
        'first-contentful-paint': {'numericValue': fcp},
        'total-blocking-time': {'numericValue': tbt},
        'cumulative-layout-shift': {'numericValue': cls},
        'layout-shifts': {'details': {'items': shifts or []}},
        'final-screenshot': {'details': {'data': tiny_jpeg_data_uri(), 'timing': 3000}},
        'screenshot-thumbnails': {'details': {'type': 'filmstrip', 'items': [{'data': tiny_jpeg_data_uri(), 'timing': 300 * i} for i in range(1, 4)]}},
    }
    j = {'lighthouseResult': {'lighthouseVersion': '12.6.1', 'finalDisplayedUrl': 'https://site-a.example/trang/', 'environment': {'benchmarkIndex': bench},
                              'configSettings': {'formFactor': dev}, 'audits': au, 'categories': {'performance': {'score': score / 100.0}}},
         'loadingExperience': {'metrics': {'CUMULATIVE_LAYOUT_SHIFT_SCORE': {'percentile': 12, 'category': 'FAST'}}}}
    if pad:
        j['pad'] = 'x' * 11000  # psi_run coi file dưới 10 KB là chưa đo
    return j


def write_psi(d, name, **kw):
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with open(p, 'w') as f:
        json.dump(psi_json(**kw), f)
    return p


class PsiStub:
    """Server PSI giả trên 127.0.0.1. mode 'ok' trả JSON, 'fail' trả 500. Ghi lại thứ tự gọi và số request đồng thời lớn nhất.
    cache_hits=N: sau lượt đầu của mỗi cặp URL + thiết bị, N lượt kế tiếp trả lại đúng fetchTime cũ (PSI trả kết quả đã lưu)."""

    def __init__(self, mode='ok', delay=0.0, cache_hits=0):
        self.mode, self.delay, self.calls, self.inflight, self.max_inflight = mode, delay, [], 0, 0
        self.cache_hits, self.n, self.ft = cache_hits, {}, {}
        self.lock = threading.Lock()
        stub = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                q = parse_qs(urlsplit(self.path).query)
                if not self.path.startswith('/runPagespeed'):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'<html></html>')
                    return
                with stub.lock:
                    stub.inflight += 1
                    stub.max_inflight = max(stub.max_inflight, stub.inflight)
                    stub.calls.append((q.get('url', [''])[0], q.get('strategy', [''])[0], q.get('key', [''])[0]))
                try:
                    import time
                    time.sleep(stub.delay)
                    if stub.mode == 'fail':
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b'loi')
                        return
                    k = (q.get('url', [''])[0], q.get('strategy', [''])[0])
                    with stub.lock:
                        i = stub.n[k] = stub.n.get(k, 0) + 1
                        if i == 1 or i > 1 + stub.cache_hits:
                            stub.ft[k] = '2026-10-27T00:00:%02d.%03dZ' % (len(stub.calls) % 60, i)
                    j = psi_json(dev=q.get('strategy', ['mobile'])[0])
                    j['lighthouseResult']['fetchTime'] = stub.ft[k]
                    body = json.dumps(j).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(body)
                finally:
                    with stub.lock:
                        stub.inflight -= 1

        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.port = self.srv.server_address[1]
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()

    @property
    def api(self):
        return 'http://127.0.0.1:%d/runPagespeed' % self.port


class SiteStub:
    """Server trang giả: / và /ok trả 200 với title, /404 trả 404. fixed: nếu cho thì mọi đường dẫn trả mã đó."""

    def __init__(self, status_map=None, title='Trang thử WPS'):
        self.status_map, self.title = status_map or {}, title
        stub = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                code = stub.status_map.get(self.path.split('?')[0], 200)
                self.send_response(code)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(('<!doctype html><html><head><meta charset=utf-8><title>%s</title></head><body><h1>Xin chào</h1></body></html>' % (stub.title if code < 400 else 'Không tìm thấy')).encode())

        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
        self.port = self.srv.server_address[1]
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.srv.shutdown()
        self.srv.server_close()

    def url(self, path='/ok'):
        return 'http://127.0.0.1:%d%s' % (self.port, path)
