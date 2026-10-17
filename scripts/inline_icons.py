"""Inline the 19 lucide icons used by the page as SVG, dropping the 454KB
lucide UMD runtime (and therefore the unpkg CDN dependency).

`lucide@1.58.0` no longer ships brand icons, so `facebook` is not available from
lucide-static; it is replaced with a filled circle-f mark.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "assets" / "icons"
HTML = ROOT / "index.html"

STROKE_ATTRS = (
    'fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"'
)

# lucide removed brand icons in 1.0; reproduce the circle-f mark locally.
FACEBOOK = (
    '<svg class="{cls}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 '
    '3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 '
    '2.89h-2.34v6.99A10 10 0 0 0 22 12z"/></svg>'
)


def icon_body(name: str) -> str:
    svg = (ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
    # The license comment contains a '>', so strip comments before locating the root tag.
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    root = svg[svg.index("<svg") : svg.rindex("</svg>")]
    inner = root[root.index(">") + 1 :]
    return inner.strip()


def main() -> int:
    html = HTML.read_text(encoding="utf-8")

    # <i id="x" data-lucide="name" class="..."></i>  ->  <svg class="..." ...>paths</svg>
    pattern = re.compile(
        r'<i\b([^>]*?)data-lucide="([a-z0-9-]+)"([^>]*?)></i>', re.S
    )

    def repl(match: re.Match) -> str:
        before, name, after = match.group(1), match.group(2), match.group(3)
        attrs = f"{before} {after}"
        attrs = re.sub(r"\s+", " ", attrs).strip()
        cls = ""
        cls_match = re.search(r'class="([^"]*)"', attrs)
        if cls_match:
            cls = cls_match.group(1)
            attrs = attrs.replace(cls_match.group(0), "").strip()
        attrs = re.sub(r"\s+", " ", attrs).strip()
        tail = f" {attrs}" if attrs else ""

        if name == "facebook":
            return FACEBOOK.format(cls=cls) if cls else FACEBOOK.format(cls="")
        if not (ICON_DIR / f"{name}.svg").exists():
            raise SystemExit(f"missing icon asset: {name}")
        return (
            f'<svg{tail} class="{cls}" viewBox="0 0 24 24" {STROKE_ATTRS} '
            f'aria-hidden="true">{icon_body(name)}</svg>'
        )

    html, count = pattern.subn(repl, html)

    # Drop the lucide runtime entirely.
    html = html.replace(
        '    <!-- Lucide Icons -->\n    <script src="https://unpkg.com/lucide@latest"></script>\n',
        "",
    )
    html = html.replace("        lucide.createIcons();\n\n", "")

    HTML.write_text(html, encoding="utf-8")

    leftovers = re.findall(r"<i\b[^>]*>", html)
    print(f"inlined: {count}")
    print(f"leftover <i> tags: {len(leftovers)} {leftovers[:5]}")
    print(f"lucide refs left: {html.count('lucide')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
