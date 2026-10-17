"""Static acceptance checks for the rebuilt site.

Run after any edit:  python scripts/verify.py
Exits non-zero (and lists findings) when something is broken.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "privacy.html", "terms.html"]

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

ALLOWED_EXTERNAL = {"t.me", "mp.weixin.qq.com", "www.w3.org", "schema.org"}


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = []
        self.anchors = []
        self.assets = []
        self.externals = set()
        self.jsonld = []
        self._in_script_type = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.anchors.append(a["href"])
        for key in ("src", "href"):
            val = a.get(key, "")
            if not val or val.startswith("data:"):
                continue
            if val.startswith("#"):
                continue
            host = urlparse(val).netloc
            if host:
                self.externals.add(host)
            elif val.startswith("/") or not val.startswith(("http", "mailto:", "tel:")):
                self.assets.append(val)
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_script_type = "jsonld"
            self._buf = []
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script_type == "jsonld":
            self.jsonld.append("".join(self._buf))
            self._in_script_type = None
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}>")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"expected </{self.stack[-1]}> got </{tag}>")
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
            return
        self.stack.pop()

    def handle_data(self, data):
        if self._in_script_type == "jsonld":
            self._buf.append(data)


def main() -> int:
    problems = []
    for name in PAGES:
        path = ROOT / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue

        raw = path.read_text(encoding="utf-8")
        doc = Doc()
        doc.feed(raw)
        doc.close()

        for err in doc.errors:
            problems.append(f"{name}: {err}")
        for tag in doc.stack:
            problems.append(f"{name}: unclosed <{tag}>")

        dupes = {i for i in doc.ids if doc.ids.count(i) > 1}
        for d in dupes:
            problems.append(f"{name}: duplicate id #{d}")

        for a in doc.anchors:
            if a == "#":
                problems.append(f"{name}: dead anchor href=\"#\"")
            elif a.startswith("#") and a[1:] and a[1:] not in doc.ids:
                problems.append(f"{name}: anchor {a} has no matching id")

        for asset in doc.assets:
            clean = asset.split("?")[0].split("#")[0]
            if not (ROOT / clean.lstrip("/")).exists():
                problems.append(f"{name}: missing local asset {clean}")

        for host in sorted(doc.externals):
            if host not in ALLOWED_EXTERNAL and not host.endswith("xuanlanch.dpdns.org"):
                problems.append(f"{name}: unexpected external host {host}")

        for blob in doc.jsonld:
            try:
                json.loads(blob)
            except json.JSONDecodeError as exc:
                problems.append(f"{name}: invalid JSON-LD ({exc})")

        for bad in ("data-lucide=", "cdn.tailwindcss.com", "unpkg.com", "fonts.googleapis.com", "api.qrserver.com"):
            if bad in raw:
                problems.append(f"{name}: still references {bad}")

        if re.search(r"<i\b", raw):
            problems.append(f"{name}: leftover <i> icon placeholder")

        # 内联 SVG 必须显式指定尺寸，否则浏览器给默认 300x150 或 0，图标会消失。
        for i, tag in enumerate(re.findall(r"<svg\b[^>]*>", raw), 1):
            if tag.startswith('<svg xmlns=%22'):
                continue  # favicon data URI，不是真实元素
            cls = re.search(r'class="([^"]*)"', tag)
            cls = cls.group(1) if cls else ""
            sized = bool(re.search(r"\bw-\d|\bw-\[", cls)) and bool(
                re.search(r"\bh-\d|\bh-\[", cls)
            )
            has_attrs = bool(re.search(r'\swidth="\d', tag)) and bool(
                re.search(r'\sheight="\d', tag)
            )
            if not (sized or has_attrs):
                problems.append(f"{name}: svg #{i} has no explicit size -> {tag[:70]}")

        print(f"{name}: {len(raw):>7,} bytes, {len(doc.assets)} local refs, "
              f"{len(doc.externals)} external hosts, {len(doc.jsonld)} JSON-LD blocks")

    print()
    if problems:
        print(f"FAILED ({len(problems)})")
        for p in problems:
            print("  -", p)
        return 1
    print("PASSED: no structural, asset, anchor or SEO-schema problems found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
