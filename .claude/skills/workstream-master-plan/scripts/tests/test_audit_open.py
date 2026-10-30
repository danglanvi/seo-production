import json
import unittest

from _common import Base, FIXED_NOW, P, make_plan
import audit_open as A


def user(text, ts="2026-10-25T01:00:00.000Z", **kw):
    o = {"type": "user", "message": {"role": "user", "content": text}, "timestamp": ts,
         "origin": {"kind": "human"}, "turnOrigin": "human"}
    o.update(kw)
    return o


class AuditTest(Base):
    def plan_with_asks(self, *asks):
        def m(p):
            p["requests"] = [{"date": "25/10/2026 09:00", "ask": a, "items": "M1"} for a in asks]
        return self.write_plan(m)

    def transcript(self, rows, name="s.jsonl"):
        f = self.dir / name
        f.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        return f

    def audit(self, *argv):
        return self.run_main(A.main, list(argv))

    # --- ca hỏng thật: 10 việc bị sót (19/10 16:55). 4 tin, 1 vào sổ, 3 phải bị liệt kê.
    def test_liet_ke_tin_chua_vao_so(self):
        plan = self.plan_with_asks("Thêm trang EN cho dịch vụ")
        t = self.transcript([
            user("Thêm trang EN cho dịch vụ SEO nhé"),
            user("Đổi nút Blueprint trùng thành Xem dịch vụ tư vấn"),
            user("Tiêu đề trang tự đếm số thẻ đã duyệt"),
            user("Quarantine giữ tới 18/11 và chặn URL đêm nay"),
        ])
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t))
        self.assertEqual(code, 1)
        self.assertIn("đã vào sổ 1", out)
        self.assertIn("chưa vào sổ 3", out)
        self.assertIn("Blueprint", out)
        self.assertIn("Quarantine", out)
        self.assertNotIn("Thêm trang EN", out.split("Tin xét")[1].split("\n", 1)[1])

    def test_het_viec_mo_thi_ma_thoat_0(self):
        plan = self.plan_with_asks("Đổi nút Blueprint trùng thành Xem dịch vụ tư vấn")
        t = self.transcript([user("Đổi nút Blueprint trùng thành Xem dịch vụ tư vấn")])
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t))
        self.assertEqual(code, 0)
        self.assertIn("chưa vào sổ 0", out)

    def test_ask_cat_bang_dau_ba_cham_van_khop(self):
        plan = self.plan_with_asks("Quarantine giữ tới 18/11 … chặn URL đêm 23:37, không 301 logo")
        t = self.transcript([user("Ok. Quarantine giữ tới 18/11, ẩn khỏi Media, chặn URL đêm 23:37, không 301 logo nhé. Thêm ý khác dài dài.")])
        code, _, _ = self.audit("--plan", str(plan), "--source", str(t))
        self.assertEqual(code, 0)

    # --- ca hỏng thật 27/10/2026 22:25: tin 284 ký tự, ask dán gần cả tin bị từ chối (210 > 200).
    # Cách đúng: nối các đoạn nguyên văn bằng '…', ask <= ASK_MAX và tin vẫn tính là đã vào sổ.
    def test_tin_dai_noi_doan_nguyen_van_van_khop(self):
        import plan as PLAN
        msg = ("1. hai trang dịch vụ mà còn dưới 97, không sao. Để đó cũng dc. \n2. slide case study check và review lại rồi chỉnh nhé. \n"
               "3. Nâng cấp skills speed và các skills liên quan giúp tôi khi có trải nghiệm và chạy thực tế rồi nhé. \n"
               "4. còn lại bạn tự chay nha, các phần cần tôi thì để sau cũng dc.")
        ask = ("hai trang dịch vụ mà còn dưới 97, không sao … slide case study check và review lại rồi chỉnh "
               "… Nâng cấp skills speed … khi có trải nghiệm và chạy thực tế rồi nhé … còn lại bạn tự chay nha")
        self.assertGreater(len(" ".join(msg.split())), PLAN.ASK_MAX)
        self.assertLessEqual(len(ask), PLAN.ASK_MAX)
        plan = self.plan_with_asks(ask)
        t = self.transcript([user(msg)])
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t))
        self.assertEqual(code, 0, out)

    # --- lọc nguồn transcript
    def test_loai_tin_he_thong_giu_tin_gui_giua_luot_va_peer(self):
        plan = self.plan_with_asks("không liên quan gì hết")
        rows = [
            user("Tin gõ tay thật của Lead về footer"),
            user("<task-notification><task-id>x</task-id></task-notification>", origin={"kind": "task-notification"}),
            user("Tin do lịch tự kiểm sinh ra", turnOrigin="scheduled"),
            user("Tin meta của harness dài dài dài", isMeta=True),
            {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "kết quả tool dài dài"}]},
             "timestamp": "2026-10-25T01:00:00Z"},
            {"type": "attachment", "timestamp": "2026-10-25T01:02:00Z",
             "attachment": {"type": "queued_command", "commandMode": "prompt", "prompt": "Tin gửi giữa lượt về menu"}},
            {"type": "attachment", "timestamp": "2026-10-25T01:03:00Z",
             "attachment": {"type": "queued_command", "commandMode": "prompt", "prompt": "<task-notification>bỏ</task-notification>"}},
            user("Another Claude session nhắn: Lead bảo đổi cỡ chữ hero"),
            user("This session is being continued from a previous conversation that ran out"),
            {"type": "assistant", "message": {"role": "assistant", "content": "trả lời của agent"}},
        ]
        t = self.transcript(rows)
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t), "--json")
        data = json.loads(out)
        kinds = sorted(m["kind"] for m in data["open_messages"])
        self.assertEqual(kinds, ["peer", "queued", "typed"])
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t), "--json", "--no-peer")
        self.assertEqual(len(json.loads(out)["open_messages"]), 2)

    def test_bo_qua_tin_ngan_va_dong_anh(self):
        plan = self.plan_with_asks("không liên quan")
        t = self.transcript([user("ok"), user("duyệt hết"), user("[Image: source: /tmp/a.png]"),
                             user("Sửa lại phần header cho gọn\n[Image: source: /tmp/b.png]")])
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t), "--json")
        d = json.loads(out)
        self.assertEqual(len(d["open_messages"]), 1)
        self.assertNotIn("[Image", d["open_messages"][0]["text"])
        self.assertEqual(d["stats"]["short"], 2)

    # --- runtime khác: file text
    def test_file_text_tach_theo_gach_va_loc_since(self):
        plan = self.plan_with_asks("không liên quan")
        f = self.dir / "tin.txt"
        f.write_text("[24/10/2026 08:00] Tin cũ về logo footer\n---\n[25/10/2026 08:00] Tin mới về menu mobile\n---\nTin không giờ về schema\n",
                     encoding="utf-8")
        code, out, _ = self.audit("--plan", str(plan), "--source", str(f), "--since", "25/10/2026 00:00", "--json")
        texts = [m["text"] for m in json.loads(out)["open_messages"]]
        self.assertEqual(texts, ["Tin mới về menu mobile", "Tin không giờ về schema"])

    def test_file_text_khong_co_gach_tach_theo_dong_trong(self):
        plan = self.plan_with_asks("không liên quan")
        f = self.dir / "tin.md"
        f.write_text("Tin một về header\nvẫn tin một\n\nTin hai về footer\n", encoding="utf-8")
        _, out, _ = self.audit("--plan", str(plan), "--source", str(f), "--json")
        self.assertEqual(len(json.loads(out)["open_messages"]), 2)

    # --- thẻ approved/edited chưa applied
    def test_the_da_duyet_chua_ap(self):
        plan = self.plan_with_asks("x y z w")
        cards = self.dir / "cards.json"
        cards.write_text(json.dumps({"c1": {"status": "approved"}, "c2": {"status": "edited"},
                                     "c3": {"status": "approved", "applied": True},
                                     "c4": {"status": "pending"}, "c5": {"status": "approved", "applied_at": "x"},
                                     "c6": {"status": "approved"}}), encoding="utf-8")
        applied = self.dir / "mark_applied.json"
        applied.write_text(json.dumps(["c6"]), encoding="utf-8")
        code, out, _ = self.audit("--plan", str(plan), "--cards", str(cards), "--applied", str(applied), "--json")
        self.assertEqual(code, 1)
        self.assertEqual(sorted(c["id"] for c in json.loads(out)["pending_cards"]), ["c1", "c2"])
        applied.write_text(json.dumps([{"id": "c1"}, {"id": "c2"}, {"id": "c6"}]), encoding="utf-8")
        code, _, _ = self.audit("--plan", str(plan), "--cards", str(cards), "--applied", str(applied))
        self.assertEqual(code, 0)

    # --- an toàn
    def test_che_token_trong_dau_ra_va_khong_ghi_file(self):
        plan = self.plan_with_asks("không liên quan")
        t = self.transcript([user("Dùng khoá sk-abcdefghijklmnopqrstuvwx và password: hunter22 để vào")])
        before = sorted(p.name for p in self.dir.iterdir())
        code, out, _ = self.audit("--plan", str(plan), "--source", str(t))
        self.assertNotIn("sk-abcdefgh", out)
        self.assertNotIn("hunter22", out)
        self.assertIn("[đã che]", out)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), before)

    # --- ca hỏng thật: chạy thử transcript site-mau 25/10, 3 tin lộ khoá ?sk= của link artifact
    def test_che_khoa_chia_se_trong_link(self):
        plan = self.plan_with_asks("không liên quan")
        t = self.transcript([user("https://claude.ai/artifact/AbCd1234?sk=lDx5WFqN1c1lyHQuyBo3VQ - ok cập nhật trạng thái")])
        _, out, _ = self.audit("--plan", str(plan), "--source", str(t))
        self.assertNotIn("lDx5WFqN1c1lyHQuyBo3VQ", out)
        self.assertIn("?sk=[đã che]", out)

    # --- ca hỏng thật: chạy thử transcript site-mau 25/10, 4 tin chỉ là khối <ide_opened_file>, <ide_selection>
    def test_bo_khoi_ide_giu_chu_cua_lead(self):
        plan = self.plan_with_asks("không liên quan")
        t = self.transcript([
            user("<ide_opened_file>The user opened the file /a/b.md in the IDE.</ide_opened_file>"),
            user([{"type": "text", "text": "<ide_selection>The user selected lines 1 to 9\nnội dung</ide_selection>"},
                  {"type": "text", "text": "Sửa đoạn này cho gọn hơn"}]),
        ])
        _, out, _ = self.audit("--plan", str(plan), "--source", str(t), "--json")
        texts = [m["text"] for m in json.loads(out)["open_messages"]]
        self.assertEqual(texts, ["Sửa đoạn này cho gọn hơn"])

    # --- runtime khác: .jsonl không phải định dạng Claude Code thì dừng, không báo "0 việc mở"
    def test_jsonl_khong_phai_claude_code_ma_thoat_2(self):
        plan = self.plan_with_asks("không liên quan")
        t = self.transcript([{"timestamp": "2026-10-25T01:00:00Z", "type": "response_item",
                              "payload": {"role": "user", "content": "Sửa footer"}}], name="codex.jsonl")
        code, _, err = self.audit("--plan", str(plan), "--source", str(t))
        self.assertEqual(code, 2)
        self.assertIn("không phải transcript Claude Code", err)

    def test_dau_vao_sai_ma_thoat_2(self):
        plan = self.plan_with_asks("x y z w")
        self.assertEqual(self.audit("--plan", str(plan))[0], 2)
        self.assertEqual(self.audit("--plan", str(plan), "--source", str(self.dir / "khong-co.jsonl"))[0], 2)
        self.assertEqual(self.audit("--plan", str(self.dir / "khong-co.json"), "--source", "x.txt")[0], 2)
        self.assertEqual(self.audit("--plan", str(plan), "--source", "x.txt", "--since", "hôm qua")[0], 2)

    def test_help(self):
        code, out, _ = self.audit("--help")
        self.assertEqual(code, 0)
        self.assertIn("--source", out)


if __name__ == "__main__":
    unittest.main()
