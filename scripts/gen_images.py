"""Generate the social share covers locally.

The live site pointed og:image at an Unsplash photo that now 404s, so every
Telegram / WeChat / Facebook share rendered without a card image. These assets
are generated from the brand palette so they can never rot.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"

FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_REG = "C:/Windows/Fonts/msyh.ttc"

BLACK = (0, 0, 0)
WHITE = (245, 245, 247)
GRAY = (134, 134, 139)
BLUE = (41, 151, 255)


def glow(size, center, radius, color, strength):
    w, h = size
    ys, xs = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xs - center[0]) ** 2 + (ys - center[1]) ** 2)
    alpha = np.clip(1 - dist / radius, 0, 1) ** 2 * strength
    layer = np.zeros((h, w, 4), dtype=np.uint8)
    layer[..., 0], layer[..., 1], layer[..., 2] = color
    layer[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(layer, "RGBA")


def dotted_grid(size, step=40, color=(255, 255, 255), alpha=26):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for x in range(0, size[0], step):
        for y in range(0, size[1], step):
            draw.ellipse((x, y, x + 2, y + 2), fill=(*color, alpha))
    return layer


def tracked_text(draw, xy, text, font, fill, tracking=0):
    """PIL has no letter-spacing; draw glyph by glyph."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def build_og():
    size = (1200, 630)
    canvas = Image.new("RGB", size, BLACK)
    canvas = Image.alpha_composite(
        canvas.convert("RGBA"), glow(size, (600, -80), 780, BLUE, 0.38)
    )
    canvas = Image.alpha_composite(canvas, dotted_grid(size))

    draw = ImageDraw.Draw(canvas)
    title = ImageFont.truetype(FONT_BOLD, 104)
    sub = ImageFont.truetype(FONT_REG, 33)
    tag = ImageFont.truetype(FONT_REG, 30)
    domain = ImageFont.truetype(FONT_REG, 24)

    tracked_text(draw, (96, 190), "玄澜跨境", title, WHITE, tracking=8)

    draw.rectangle((100, 340, 232, 346), fill=BLUE)

    draw.text(
        (96, 380),
        "Google · Meta · TikTok · Shopify",
        font=sub,
        fill=GRAY,
    )
    draw.text((96, 428), "一站式跨境出海解决方案", font=tag, fill=WHITE)

    draw.text((96, 540), "出海，由此开始。", font=tag, fill=(120, 170, 235))
    w = draw.textlength("xuanlanch.dpdns.org", font=domain)
    draw.text((1104 - w, 546), "xuanlanch.dpdns.org", font=domain, fill=(90, 90, 95))

    path = OUT / "og-cover.png"
    canvas.convert("RGB").save(path, "PNG", optimize=True)
    return path


def build_wechat():
    size = (400, 400)
    canvas = Image.new("RGB", size, BLACK)
    canvas = Image.alpha_composite(
        canvas.convert("RGBA"), glow(size, (200, 120), 320, BLUE, 0.42)
    )
    draw = ImageDraw.Draw(canvas)

    big = ImageFont.truetype(FONT_BOLD, 96)
    small = ImageFont.truetype(FONT_REG, 22)

    a = draw.textlength("玄澜", font=big)
    draw.text(((400 - a) / 2, 120), "玄澜", font=big, fill=WHITE)

    draw.rectangle((178, 246, 222, 250), fill=BLUE)

    b = draw.textlength("跨境出海解决方案", font=small)
    draw.text(((400 - b) / 2, 278), "跨境出海解决方案", font=small, fill=GRAY)

    path = OUT / "wechat-cover.png"
    canvas.convert("RGB").save(path, "PNG", optimize=True)
    return path


def build_article(name, category, title_lines, accent, tint):
    size = (800, 450)
    canvas = Image.new("RGB", size, BLACK)
    canvas = Image.alpha_composite(
        canvas.convert("RGBA"), glow(size, (0, 0), 620, tint, 0.55)
    )
    draw = ImageDraw.Draw(canvas)

    cat = ImageFont.truetype(FONT_BOLD, 17)
    title = ImageFont.truetype(FONT_BOLD, 58)

    tracked_text(draw, (52, 46), category, cat, accent, tracking=3.5)
    y = 200
    for line in title_lines:
        draw.text((52, y), line, font=title, fill=WHITE)
        y += 76

    draw.rectangle((52, y + 26, 132, y + 31), fill=accent)

    path = OUT / name
    canvas.convert("RGB").save(path, "JPEG", quality=88, optimize=True, progressive=True)
    return path


def build_article_covers():
    return [
        build_article(
            "cover-tiktok-shop.jpg",
            "TRENDS",
            ["TikTok Shop", "美国区入驻政策"],
            (254, 44, 85),
            (254, 44, 85),
        ),
        build_article(
            "cover-pmax.jpg",
            "STRATEGY",
            ["PMax", "效果最大化投放"],
            (41, 151, 255),
            (41, 151, 255),
        ),
    ]


if __name__ == "__main__":
    outputs = [build_og(), build_wechat(), *build_article_covers()]
    for p in outputs:
        print(f"{p.name}: {p.stat().st_size / 1024:.1f} KB")
