"""Test offline: luật check của media_match.py và vị trí logo của watermark.py. Chạy: python3 -B tests/test_media.py"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import media_match  # noqa: E402
import watermark  # noqa: E402
from PIL import Image  # noqa: E402


def test_check_rules():
    slots = [
        {"slot_id": "a", "page": "/1/", "decision": "youtube_video", "media": {"video_id": "V1"}, "alt": "x", "caption": "y"},
        {"slot_id": "b", "page": "/2/", "decision": "youtube_video", "media": {"video_id": "V1"}, "alt": "x", "caption": "y"},
        {"slot_id": "c", "page": "/3/", "decision": "youtube_video", "media": {"video_id": "V1"}, "alt": "x", "caption": ""},
        {"slot_id": "d", "page": "/4/", "decision": "ai_image", "gap_media_type": "real_photo", "media": {}, "alt": "x", "caption": "y"},
        {"slot_id": "e", "page": "/5/", "decision": "real_photo", "status": "needs_source", "media": {}, "alt": "", "caption": ""},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "plan.json")
        p.write_text(json.dumps({"slots": slots}), encoding="utf-8")
        nn = Path(d, "nn.jsonl")
        nn.write_text("\n".join(json.dumps({"id": s, "top": [{"id": "V2"}, {"id": "V1"}]}) for s in "abc"), encoding="utf-8")
        out = []
        media_match.print = lambda s: out.append(s)
        rc = media_match.main(["check", "--plan", str(p), "--nn", str(nn)])
        r = json.loads(out[0])
        assert rc == 1 and r["video_rank"] == {"top3": 3}
        e = " ".join(r["errors"])
        assert "c: thiếu caption" in e and "video V1 ở 3 trang" in e and "d: ảnh AI thay ảnh thật" in e and "e:" not in e


def test_check_testimonial_and_reuse():
    # Ca thật site gtvseo 19/10: video lời chứng thực trên trang chủ brand A, transcript cho thấy người nói là học viên của brand B.
    # Ca thật 17/10: trang mới dùng lại 11 ảnh của trang chủ, sau đó phải thay 8/9 ô.
    slots = [
        {"slot_id": "t1", "page": "/", "decision": "self_hosted_video", "purpose": "testimonial", "media": {"src": "/v/hv1.mp4"},
         "alt": "x", "caption": "y", "speaker_entity": "Brand B", "speaker_evidence": "00:12 'em học khoá của Brand B'"},
        {"slot_id": "t2", "page": "/", "decision": "youtube_video", "purpose": "testimonial", "media": {"video_id": "V9"}, "alt": "x", "caption": "y"},
        {"slot_id": "t3", "page": "/gioi-thieu/", "decision": "youtube_video", "purpose": "testimonial", "media": {"video_id": "V8"},
         "alt": "x", "caption": "y", "speaker_entity": "brand a", "speaker_evidence": "01:05 giám đốc khách hàng của Brand A"},
        {"slot_id": "t4", "page": "/x/", "decision": "youtube_video", "purpose": "testimonial", "status": "needs_source", "media": {}, "alt": "", "caption": ""},
        {"slot_id": "r1", "page": "https://site.vn/landing/", "decision": "real_photo", "alt": "x", "caption": "y",
         "media": {"src": "https://cdn.example/wp-content/uploads/2026/10/hoi-thao-1024x683.jpg?v=2"}},
        {"slot_id": "r2", "page": "/landing/", "decision": "real_photo", "alt": "x", "caption": "y", "media": {"src": "/wp-content/uploads/2026/10/doi-ngu.jpg"}},
        {"slot_id": "r3", "page": "/landing/", "decision": "real_photo", "alt": "x", "caption": "y", "allow_reuse": True,
         "media": {"src": "/wp-content/uploads/2026/10/tac-gia.jpg"}},
        {"slot_id": "r4", "page": "/a/", "decision": "screenshot", "alt": "x", "caption": "y", "media": {"src": "/u/gsc.png"}},
        {"slot_id": "r5", "page": "/b/", "decision": "screenshot", "alt": "x", "caption": "y", "media": {"src": "/u/gsc.png"}},
    ]
    used = [{"page": "https://site.vn/", "src": "https://site.vn/wp-content/uploads/2026/10/hoi-thao.jpg"},
            {"page": "https://site.vn/landing/", "src": "https://site.vn/wp-content/uploads/2026/10/doi-ngu.jpg"},
            {"page": "https://site.vn/", "src": "https://site.vn/wp-content/uploads/2026/10/tac-gia.jpg"}]
    with tempfile.TemporaryDirectory() as d:
        p, u, t = Path(d, "plan.json"), Path(d, "images.jsonl"), Path(d, "used.txt")
        p.write_text(json.dumps({"site_entity": "Brand A", "slots": slots}), encoding="utf-8")
        u.write_text("\n".join(json.dumps(x) for x in used), encoding="utf-8")
        t.write_text("# ảnh trang chủ\n/u/gsc-300x200.png\n", encoding="utf-8")
        out = []
        media_match.print = lambda s: out.append(s)
        assert media_match.main(["check", "--plan", str(p), "--used", str(u)]) == 1
        e = json.loads(out[-1])["errors"]
        j = " | ".join(e)
        assert "t1: người nói thuộc Brand B, trang thuộc Brand A" in j
        assert "t2: lời chứng thực chưa kiểm entity người nói" in j
        assert "t3:" not in j and "t4:" not in j  # cùng entity (không phân biệt hoa thường); slot chờ nguồn bỏ qua
        assert "r1: ảnh" in j and "['/']" in j  # cùng ảnh dù khác host, query và hậu tố -1024x683
        assert "r2:" not in j and "r3:" not in j  # ảnh của chính trang đó; allow_reuse
        assert any("ảnh /u/gsc.png lặp ở 2 trang của plan" in x for x in e)
        media_match.main(["check", "--plan", str(p), "--used", str(t)])
        j = " | ".join(json.loads(out[-1])["errors"])
        assert "r4: ảnh /u/gsc.png đã dùng ở trang khác: theo --used" in j and "r1:" not in j
        p.write_text(json.dumps({"slots": slots[2:3]}), encoding="utf-8")  # plan thiếu site_entity
        assert media_match.main(["check", "--plan", str(p)]) == 1
        assert "cần page_entity hoặc site_entity" in json.loads(out[-1])["errors"][0]


def test_watermark_corner():
    im = Image.new("RGB", (1000, 500), "white")
    logo = Image.new("RGBA", (100, 50), (0, 0, 0, 255))
    out = watermark.stamp(im, logo)
    assert out.getpixel((1000 - 25 - 45, 500 - 25 - 20)) != (255, 255, 255)  # trong vùng logo 90x45
    assert out.getpixel((10, 10)) == (255, 255, 255)


if __name__ == "__main__":
    test_check_rules()
    test_check_testimonial_and_reuse()
    test_watermark_corner()
    print("OK 3 test")
