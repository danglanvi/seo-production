#!/usr/bin/env python3
"""che_secret.py: che mật khẩu, key, token trong output của lệnh đọc cấu hình server hoặc API nhà cung cấp, trước khi output vào transcript.

Hai cách dùng:
  che_secret.py [--ip] -- ssh <alias> 'grep -n maxmemory /etc/redis/redis.conf'    chạy lệnh, che stdout và stderr, giữ mã thoát
  <lệnh> | che_secret.py [--ip]                                                       lọc stdin

Che: requirepass, masterauth; define('DB_PASSWORD' | *_KEY | *_SALT, '...') của wp-config; dòng hoặc trường JSON tên password, pass, pwd,
secret, token, key, apikey, accesskey, deploymentkey; "redis-cli -a <mật khẩu>"; "Bearer ..."; chuỗi AIza...; mọi giá trị dài từ 8 ký tự
của file secret dùng chung (.agent-secrets/.env, tìm ngược lên từ thư mục hiện tại và thư mục script). --ip che thêm địa chỉ IPv4.
Script không in giá trị đã che. Dòng cuối stderr ghi số chỗ đã che.

Ca thật: đêm 26–27/10/2026 một lane in mật khẩu Redis vào transcript 2 lần khi đọc file cấu hình và chạy redis-cli -a.
Cách không lộ ngay từ đầu: đặt mật khẩu Redis qua biến REDISCLI_AUTH đọc trên server, không truyền -a.
Mã thoát: của lệnh con; 2 khi lỗi dùng.
"""
import os
import re
import subprocess
import sys

NAME = r"(?:pass(?:word)?|pwd|secret|token|api[_-]?key|access[_-]?key|deployment[_-]?key|private[_-]?key|auth[_-]?key)"
RULES = [
    re.compile(r"(?im)^(\s*(?:requirepass|masterauth)\s+)(\S+)"),
    re.compile(r"(?i)(define\(\s*['\"](?:DB_PASSWORD|\w*_(?:KEY|SALT))['\"]\s*,\s*['\"])([^'\"]*)"),
    re.compile(r"(?i)(\bredis-cli\b[^\n|;]*?\s-a\s+)(\S+)"),
    re.compile(r'(?i)("[^"\n]*' + NAME + r'[^"\n]*"\s*:\s*")((?:[^"\\\n]|\\.)+)'),
    re.compile(r"(?i)(\b\w*" + NAME + r"\w*\b\s*[:=]\s*['\"]?)([^\s'\",;|\\]{4,})"),
    re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._~+/=-]{12,})"),
    re.compile(r"()(AIza[0-9A-Za-z_-]{20,})"),
]
IPV4 = re.compile(r"\b(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b")


def env_values():
    seen, vals = set(), set()
    for start in (os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
        d = start
        while True:
            f = os.path.join(d, ".agent-secrets", ".env")
            if os.path.isfile(f) and f not in seen:
                seen.add(f)
                for line in open(f, encoding="utf-8", errors="replace"):
                    m = re.match(r"\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*(.*)", line)
                    if m:
                        v = m.group(1).strip().strip("'\"")
                        if len(v) >= 8:
                            vals.add(v)
            up = os.path.dirname(d)
            if up == d:
                break
            d = up
    return sorted(vals, key=len, reverse=True)


def mask(text, known=(), ip=False):
    n = 0
    for v in known:
        if v in text:
            n += text.count(v)
            text = text.replace(v, "***")
    for rx in RULES:
        text, k = rx.subn(lambda m: m.group(1) + "***", text)
        n += k
    if ip:
        text, k = IPV4.subn("<ip>", text)
        n += k
    return text, n


def main(argv):
    ip = "--ip" in argv
    argv = [a for a in argv if a != "--ip"]
    known = env_values()
    if argv[:1] == ["--"]:
        if len(argv) < 2:
            print("dùng: che_secret.py [--ip] -- <lệnh> ...", file=sys.stderr)
            return 2
        p = subprocess.run(argv[1:], capture_output=True, text=True, errors="replace")
        out, a = mask(p.stdout, known, ip)
        err, b = mask(p.stderr, known, ip)
        sys.stdout.write(out)
        sys.stderr.write(err)
        print(f"che_secret: đã che {a + b} chỗ", file=sys.stderr)
        return p.returncode
    if argv:
        print("dùng: <lệnh> | che_secret.py [--ip]", file=sys.stderr)
        return 2
    out, n = mask(sys.stdin.read(), known, ip)
    sys.stdout.write(out)
    print(f"che_secret: đã che {n} chỗ", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
