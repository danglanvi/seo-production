import datetime as dt
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/server-bin/health.sh'


class Health(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.access = self.root / 'access with spaces.log'
        self.error = self.root / 'error.log'
        self.day = dt.datetime.now().strftime('%d/%b/%Y')
        self.iso = dt.date.today().isoformat()
        self.zone = dt.datetime.now().astimezone().strftime('%z')
        self.access.write_text(self.request('09:30:00', 200))
        self.error.write_text('')

    def request(self, when, status):
        return f'127.0.0.1 - - [{self.day}:{when} {self.zone}] "GET / HTTP/1.1" {status} 10\n'

    def run_health(self):
        env = dict(os.environ, ACCESS_LOG=str(self.access), ERROR_LOG=str(self.error), SITE_DOMAIN='example.test')
        return subprocess.run(['bash', str(SCRIPT), '09:00', '10:00'], env=env, capture_output=True, text=True)

    def test_counts_only_site_and_window(self):
        self.access.write_text(self.request('08:30:00', 500) + self.request('09:30:00', 503))
        self.error.write_text(f'{self.iso} 09:20:00 [x#other.test] PHP Fatal error\n'
                              f'{self.iso} 09:21:00 [x#example.test.evil] PHP Fatal error\n'
                              f'{self.iso} 09:22:00 [x#example.test:443] PHP Fatal error\n'
                              f'{self.iso} 08:22:00 [x#example.test] PHP Fatal error\n')
        r = self.run_health()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn('5xx_tu_09:00=1', r.stdout)
        self.assertIn('php_fatal_example.test_tu_09:00=1', r.stdout)
        self.assertIn('access_requests=1', r.stdout)

    def test_other_vhost_fatal_is_not_site_failure(self):
        self.error.write_text(f'{self.iso} 09:20:00 [x#other.test] PHP Fatal error\n')
        self.assertEqual(self.run_health().returncode, 0)

    def test_missing_log_is_incomplete(self):
        self.error.unlink()
        self.assertEqual(self.run_health().returncode, 2)

    def test_malformed_access_is_incomplete(self):
        self.access.write_text('not an access log\n')
        self.assertEqual(self.run_health().returncode, 2)

    def test_unattributed_fatal_is_incomplete(self):
        self.error.write_text(f'{self.iso} 09:20:00 PHP Fatal error without vhost\n')
        r = self.run_health()
        self.assertEqual(r.returncode, 2)
        self.assertIn('fatal_unattributed=1', r.stdout)

    def test_empty_window_is_incomplete(self):
        self.access.write_text(self.request('08:30:00', 200))
        self.assertEqual(self.run_health().returncode, 2)


if __name__ == '__main__':
    unittest.main()
