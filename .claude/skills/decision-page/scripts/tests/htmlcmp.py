"""Công cụ test: rút nội dung có nghĩa từ trang chờ quyết để so hai trang với nhau."""
from __future__ import annotations

from html.parser import HTMLParser


def ws(s):
    return " ".join(s.split())


class Ext(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.cards = []
        self.cur = None
        self.top = {"h1": "", "lede": "", "eyebrow": "", "key": ""}
        self.report = []
        self.in_key_done = False

    def _in(self, tag, cls=None):
        return any(t == tag and (cls is None or cls in c) for t, c in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        self.stack.append((tag, cls))
        if tag == "section" and "card" in cls:
            self.cur = {"id": a.get("id"), "label": "", "h2": "", "li": [], "opts": [], "cells": [], "stats": [], "ph": None, "q": []}
            self.cards.append(self.cur)
        elif self.cur is not None:
            if tag == "li" and self._in("ul", "ctx"):
                self.cur["li"].append("")
            elif tag == "label":
                self.cur["opts"].append({"rec": "rec" in cls, "value": None, "text": ""})
            elif tag == "input" and self.cur["opts"]:
                self.cur["opts"][-1]["value"] = a.get("value")
            elif tag == "textarea":
                self.cur["ph"] = a.get("placeholder")
            elif tag in ("td", "th"):
                self.cur["cells"].append("")
            elif tag == "div" and "stat" in cls:
                self.cur["stats"].append("")
            elif tag == "div" and "q" in cls:
                self.cur["q"].append({"short": a.get("data-q"), "text": ""})

    def handle_endtag(self, tag):
        while self.stack:
            t, c = self.stack.pop()
            if t == tag:
                break
        if tag == "section":
            self.cur = None

    def handle_data(self, d):
        if self._in("article", "report"):
            self.report.append(d)
            return
        if self._in("em", "chip") or self._in("small", "cons"):
            return
        if self.cur is None:
            if self._in("h1"):
                self.top["h1"] += d
            elif self._in("p", "lede"):
                self.top["lede"] += d
            elif self._in("div", "eyebrow"):
                self.top["eyebrow"] += d
            elif self._in("div", "note") and self._in("div", "key") and not self.in_key_done:
                self.top["key"] += d
            return
        c = self.cur
        if self._in("h2"):
            if self._in("span", "id"):
                c["label"] += d
            else:
                c["h2"] += d
        elif self._in("label") and c["opts"]:
            c["opts"][-1]["text"] += d
        elif self._in("ul", "ctx") and c["li"] and self._in("li"):
            c["li"][-1] += d
        elif (self._in("td") or self._in("th")) and c["cells"]:
            c["cells"][-1] += d
        elif self._in("div", "stat") and c["stats"]:
            c["stats"][-1] += d
        elif self._in("div", "q") and self._in("b") and c["q"] and not self._in("label"):
            c["q"][-1]["text"] += d


def extract(html_text):
    p = Ext()
    p.feed(html_text)
    out = {"top": {k: ws(v) for k, v in p.top.items()}, "report": ws("".join(p.report)), "cards": []}
    for c in p.cards:
        out["cards"].append({
            "id": c["id"], "label": ws(c["label"]), "h2": ws(c["h2"]),
            "li": [ws(x) for x in c["li"]],
            "opts": [(o["value"], o["rec"], ws(o["text"])) for o in c["opts"]],
            "cells": [ws(x) for x in c["cells"]],
            "stats": [ws(x) for x in c["stats"]],
            "ph": c["ph"], "q": [(q["short"], ws(q["text"])) for q in c["q"]],
        })
    return out


def diff(a, b):
    """So hai kết quả extract. Trả danh sách khác biệt."""
    d = []
    for k in a["top"]:
        if a["top"][k] != b["top"][k]:
            d.append("top.%s: %r != %r" % (k, a["top"][k], b["top"][k]))
    if a["report"] != b["report"]:
        d.append("tab báo cáo khác (%d và %d ký tự)" % (len(a["report"]), len(b["report"])))
    if [c["id"] for c in a["cards"]] != [c["id"] for c in b["cards"]]:
        d.append("danh sách id thẻ khác")
        return d
    for x, y in zip(a["cards"], b["cards"]):
        for k in x:
            if x[k] != y[k]:
                d.append("thẻ %s, trường %s: %r != %r" % (x["id"], k, str(x[k])[:120], str(y[k])[:120]))
    return d
