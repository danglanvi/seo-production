# Mẫu luật chữ cho test (không phải số đã duyệt của site nào)

Khối dưới đây mô phỏng cách `ui-rules.md` của một site khai số riêng cho `type_check.py`.

```json
{
  "type_rules": {
    "small_pct_max": 6,
    "components": [
      {"name": "nhãn chỉ số case", "sel_regex": "case-metric", "min_px": {"desktop": 14, "mobile": 13}},
      {"name": "chú thích ảnh AI", "sel_regex": "ai-caption", "min_px": {"desktop": 15, "mobile": 15}},
      {"name": "chức danh người nói", "sel_regex": "speaker-title", "min_px": {"desktop": 15, "mobile": 13}}
    ],
    "h_scale": {"h2": {"desktop": [32], "mobile": [26]}}
  }
}
```
