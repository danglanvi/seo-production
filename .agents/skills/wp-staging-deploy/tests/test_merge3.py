"""Test merge3.py trên cây thư mục giả. Chạy: python3 -B tests/test_merge3.py"""
import os
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import merge3  # noqa: E402

T = "themes/t"


def tree(root, files):
    for k, v in files.items():
        p = Path(root, k)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(v, encoding="utf-8")


def fixture(d):
    base = {f"{T}/a.php": "1\n2\n3\n", f"{T}/b.php": "x\n", f"{T}/c.php": "1\n2\n3\n4\n5\n", f"{T}/d.php": "k\n",
            f"{T}/e.php": "q\n", "mu-plugins/m.php": "m\n"}
    stg = dict(base, **{f"{T}/a.php": "1\nS\n3\n", f"{T}/c.php": "S\n2\n3\n4\n5\n", f"{T}/new.php": "n\n",
                        f"{T}/e.php": "s\n", "mu-plugins/zz-staging-only.php": "stg\n"})
    prod = dict(base, **{f"{T}/b.php": "P\n", f"{T}/c.php": "1\n2\n3\n4\nP\n", f"{T}/e.php": "p\n"})
    del stg[f"{T}/d.php"]
    for name, files in (("base", base), ("stg", stg), ("prod", prod)):
        tree(Path(d, name), files)
    return [str(Path(d, x)) for x in ("base", "stg", "prod")]


def test_plan_cases():
    with tempfile.TemporaryDirectory() as d:
        b, s, p = fixture(d)
        items, errs = merge3.plan(b, s, p, [T, "mu-plugins"], ["mu-plugins/zz-staging-only.php"])
        got = {k: kind for kind, k, _ in items}
        assert got == {f"{T}/a.php": "stg", f"{T}/c.php": "merged", f"{T}/new.php": "stg"}, got
        assert f"staging thiếu {T}/d.php (production có)" in errs
        assert f"xung đột chưa giải: {T}/e.php" in errs
        merged = next(m for kind, k, m in items if kind == "merged")
        assert merged.decode() == "S\n2\n3\n4\nP\n"


def test_apply_backup_and_rollback_list():
    with tempfile.TemporaryDirectory() as d:
        b, s, p = fixture(d)
        os.remove(Path(s, T, "e.php")); Path(s, T, "e.php").write_text("p\n")  # bỏ xung đột
        Path(s, T, "d.php").write_text("k\n")
        bk = str(Path(d, "bk"))
        assert merge3.main(["--base", b, "--stg", s, "--prod", p, "--roots", f"{T},mu-plugins",
                            "--skip", "mu-plugins/zz-staging-only.php", "--apply", "--backup-dir", bk, "--owner", ""]) == 0
        assert Path(p, T, "a.php").read_text() == "1\nS\n3\n"
        assert Path(p, T, "c.php").read_text() == "S\n2\n3\n4\nP\n"
        assert not Path(p, "mu-plugins/zz-staging-only.php").exists()
        tgz = next(Path(bk).glob("prod-before-*.tgz"))
        with tarfile.open(tgz) as t:
            names = set(t.getnames())
        assert {f"{T}/a.php", f"{T}/c.php"} <= names
        assert next(Path(bk).glob("prod-new-files-*.txt")).read_text().split() == [f"{T}/new.php"]


def test_apply_needs_backup_dir():
    with tempfile.TemporaryDirectory() as d:
        b, s, p = fixture(d)
        Path(s, T, "e.php").write_text("p\n"); Path(s, T, "d.php").write_text("k\n")
        assert merge3.main(["--base", b, "--stg", s, "--prod", p, "--roots", T, "--apply"]) == 2


if __name__ == "__main__":
    for f in (test_plan_cases, test_apply_backup_and_rollback_list, test_apply_needs_backup_dir):
        f()
    print("OK 3 test")
