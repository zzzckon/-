"""生成知识页配图。

全部用代码画，不依赖外部图库，避免版权问题和外链失效。
每张图按 1200x630 或 1200x720 输出，适配正文宽度与分享。
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "wiki"
OUT.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_REG = "C:/Windows/Fonts/msyh.ttc"

BLACK = (0, 0, 0)
CARD = (29, 29, 31)
WHITE = (245, 245, 247)
GRAY = (161, 161, 166)
DIM = (110, 110, 115)
BLUE = (41, 151, 255)
PINK = (254, 44, 85)
PURPLE = (175, 82, 222)
GREEN = (48, 209, 88)
ORANGE = (255, 159, 10)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass


def glow(size, center, radius, color, strength):
    w, h = size
    ys, xs = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xs - center[0]) ** 2 + (ys - center[1]) ** 2)
    alpha = np.clip(1 - dist / radius, 0, 1) ** 2 * strength
    layer = np.zeros((h, w, 4), dtype=np.uint8)
    layer[..., 0], layer[..., 1], layer[..., 2] = color
    layer[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(layer, "RGBA")


def canvas_with_glow(w, h, center, color, strength=0.30):
    img = Image.new("RGB", (w, h), BLACK)
    img = Image.alpha_composite(img.convert("RGBA"), glow((w, h), center, 900, color, strength))
    return img


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw, xy, txt, font, fill):
    w = draw.textlength(txt, font=font)
    draw.text((xy[0] - w / 2, xy[1]), txt, font=font, fill=fill)


# ------------------------------------------------------------------ 图1 账号谱系

def fig_account_spectrum():
    w, h = 1200, 700
    img = canvas_with_glow(w, h, (300, 0), BLUE, 0.22)
    d = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD, 38)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_step = ImageFont.truetype(FONT_BOLD, 20)
    f_body = ImageFont.truetype(FONT_REG, 17)

    d.text((60, 46), "Facebook 账号的可用性光谱", font=f_title, fill=WHITE)
    d.text((60, 100), "从左到右：越往右越能承担投放，价格越高，也越依赖环境", font=f_sub, fill=GRAY)

    stages = [
        ("白号", "刚注册\n无历史", DIM),
        ("养护号", "有社交记录\n环境稳定", (90, 120, 160)),
        ("有广告功能", "已开广告\n可绑 BM", BLUE),
        ("企业广告户", "绑 BM\n限额更高", (60, 180, 255)),
        ("二不限", "限制最少\n大预算放量", GREEN),
    ]

    y = 210
    bw, gap = 196, 26
    for i, (name, desc, col) in enumerate(stages):
        x = 60 + i * (bw + gap)
        rounded(d, (x, y, x + bw, y + 150), 16, fill=CARD, outline=(60, 60, 64))
        rounded(d, (x, y, x + bw, y + 6), 3, fill=col)
        text_center(d, (x + bw / 2, y + 34), name, f_step, col)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, (x + bw / 2, y + 76 + j * 26), line, f_body, GRAY)
        if i < len(stages) - 1:
            ax = x + bw + 6
            d.line((ax, y + 75, ax + gap - 12, y + 75), fill=(70, 70, 74), width=2)
            d.polygon(
                [(ax + gap - 12, y + 70), (ax + gap - 4, y + 75), (ax + gap - 12, y + 80)],
                fill=(70, 70, 74),
            )

    d.text((60, 410), "买之前先确定用途", font=ImageFont.truetype(FONT_BOLD, 24), fill=WHITE)

    boxes = [
        ("要登录发内容", "白号 / 养护号即可\n便宜，但要自己养", DIM),
        ("要直接投广告", "企业广告账户\n含 BM，限额更高", BLUE),
        ("要跑量放大", "游戏户 · 二不限\n限制最少", GREEN),
    ]
    y2 = 470
    for i, (need, ans, col) in enumerate(boxes):
        x = 60 + i * 366
        rounded(d, (x, y2, x + 336, y2 + 150), 16, fill=CARD, outline=(60, 60, 64))
        d.text((x + 24, y2 + 22), need, font=ImageFont.truetype(FONT_BOLD, 21), fill=WHITE)
        for j, line in enumerate(ans.split("\n")):
            d.text((x + 24, y2 + 62 + j * 28), line, font=f_body, fill=col if j == 0 else GRAY)

    p = OUT / "fb-account-spectrum.png"
    img.convert("RGB").save(p, "PNG", optimize=True)
    return p


# ------------------------------------------------------------------ 图2 BM 结构

def fig_bm_structure():
    w, h = 1200, 720
    img = canvas_with_glow(w, h, (600, 0), PURPLE, 0.22)
    d = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD, 38)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_node = ImageFont.truetype(FONT_BOLD, 22)
    f_small = ImageFont.truetype(FONT_REG, 16)

    d.text((60, 46), "BM 是资产的容器，不是账号本身", font=f_title, fill=WHITE)
    d.text((60, 100), "资产挂在组织下，个人号只是操作者；换人不断资产", font=f_sub, fill=GRAY)

    # BM 容器
    rounded(d, (60, 180, 1140, 560), 22, fill=(22, 20, 28), outline=(120, 70, 150), width=2)
    d.text((88, 202), "BM 商务管理平台", font=ImageFont.truetype(FONT_BOLD, 24), fill=(200, 140, 230))

    cells = [
        ("广告账户", "可转移\n不随人走", BLUE),
        ("公共主页", "可授权\n多人管理", GREEN),
        ("像素 / 数据", "组织内共享\n不丢历史", ORANGE),
        ("支付方式", "绑在组织\n换卡不重建", PURPLE),
    ]
    for i, (name, desc, col) in enumerate(cells):
        x = 96 + i * 254
        rounded(d, (x, 272, x + 226, 470), 16, fill=CARD, outline=(60, 60, 64))
        rounded(d, (x, 272, x + 226, 278), 3, fill=col)
        text_center(d, (x + 113, 306), name, f_node, col)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, (x + 113, 360 + j * 26), line, f_small, GRAY)

    d.text((88, 500), "操作者（个人号）", font=ImageFont.truetype(FONT_BOLD, 18), fill=GRAY)
    d.text((88, 526), "只负责登录与操作，被封不影响上方资产", font=f_small, fill=DIM)

    # 对比
    d.text((60, 600), "挂个人号 vs 挂 BM", font=ImageFont.truetype(FONT_BOLD, 22), fill=WHITE)
    pairs = [("个人号挂了", "账户、素材、主页一起没", ORANGE), ("BM 挂了", "可申诉，资产可转移重建", GREEN)]
    for i, (k, v, col) in enumerate(pairs):
        x = 60 + i * 560
        d.text((x, 644), k, font=ImageFont.truetype(FONT_BOLD, 19), fill=col)
        d.text((x + 130, 646), v, font=f_small, fill=GRAY)

    p = OUT / "bm-structure.png"
    img.convert("RGB").save(p, "PNG", optimize=True)
    return p


# ------------------------------------------------------------------ 图3 橱窗流程

def fig_tiktok_flow():
    w, h = 1200, 760
    img = canvas_with_glow(w, h, (900, 0), PINK, 0.22)
    d = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD, 38)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_step = ImageFont.truetype(FONT_BOLD, 19)
    f_body = ImageFont.truetype(FONT_REG, 16)
    f_num = ImageFont.truetype(FONT_BOLD, 22)

    d.text((60, 46), "从 0 到能带货：6 步", font=f_title, fill=WHITE)
    d.text((60, 100), "第 3 步决定能不能开出来，第 6 步决定能卖多少", font=f_sub, fill=GRAY)

    steps = [
        ("定站点", "卖给谁\n就开哪国号"),
        ("备环境", "独立 IP\n一号一环境"),
        ("拿账号", "自注册\n或直接买"),
        ("补资料", "头像简介\n几条内容"),
        ("开橱窗", "按站点要求\n提交审核"),
        ("做内容", "持续产出\n决定天花板"),
    ]

    y = 190
    bw, gap = 168, 22
    for i, (name, desc) in enumerate(steps):
        x = 60 + i * (bw + gap)
        col = PINK if i < 5 else GREEN
        if i in (2, 5):
            rounded(d, (x, y, x + bw, y + 186), 16, fill=(30, 22, 28), outline=col, width=2)
        else:
            rounded(d, (x, y, x + bw, y + 186), 16, fill=CARD, outline=(60, 60, 64))
        d.ellipse((x + bw / 2 - 20, y + 18, x + bw / 2 + 20, y + 58), fill=col)
        text_center(d, (x + bw / 2, y + 28), str(i + 1), f_num, BLACK)
        text_center(d, (x + bw / 2, y + 76), name, f_step, WHITE)
        for j, line in enumerate(desc.split("\n")):
            text_center(d, (x + bw / 2, y + 118 + j * 24), line, f_body, GRAY)

    d.text((60, 410), "两种常见失败方式", font=ImageFont.truetype(FONT_BOLD, 24), fill=WHITE)

    fails = [
        ("挂上车但没流量", "0 粉能挂，但没人看的视频挂什么都卖不动。\n橱窗解决成交环节，不解决流量环节。", ORANGE),
        ("开出来两周就掉", "IP 频繁变、资料空白、新号操作过猛。\n平台判定为批量注册号。", (255, 90, 90)),
    ]
    y2 = 462
    for i, (title, body, col) in enumerate(fails):
        x = 60 + i * 552
        rounded(d, (x, y2, x + 528, y2 + 168), 16, fill=CARD, outline=(60, 60, 64))
        d.text((x + 24, y2 + 22), "× " + title, font=ImageFont.truetype(FONT_BOLD, 20), fill=col)
        for j, line in enumerate(body.split("\n")):
            d.text((x + 24, y2 + 66 + j * 28), line, font=f_body, fill=GRAY)

    d.text((60, 672), "能做的：稳定环境 + 渐进行为 + 真实内容", font=ImageFont.truetype(FONT_BOLD, 21), fill=BLUE)

    p = OUT / "tiktok-shop-flow.png"
    img.convert("RGB").save(p, "PNG", optimize=True)
    return p


# ------------------------------------------------------------------ 图4 价格对照

def fig_price_anchor():
    w, h = 1200, 620
    img = canvas_with_glow(w, h, (600, 620), BLUE, 0.20)
    d = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD, 38)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_row = ImageFont.truetype(FONT_REG, 19)
    f_price = ImageFont.truetype(FONT_BOLD, 24)

    d.text((60, 46), "为什么个人户便宜、企业户贵", font=f_title, fill=WHITE)
    d.text((60, 100), "差价买的不是账号本身，是「被封之后还能不能救」", font=f_sub, fill=GRAY)

    rows = [
        ("个人广告账户", "限额低 · 申诉弱 · 封了难救", "$0", DIM),
        ("企业广告账户", "限额更高 · 代理可协助申诉", "$22 起", BLUE),
        ("游戏户 · 二不限", "限制最少 · 可大预算放量", "$33 起", GREEN),
    ]

    y = 200
    for name, desc, price, col in rows:
        rounded(d, (60, y, 1140, y + 104), 14, fill=CARD, outline=(58, 58, 62))
        d.text((88, y + 24), name, font=ImageFont.truetype(FONT_BOLD, 22), fill=WHITE)
        d.text((88, y + 62), desc, font=f_row, fill=GRAY)
        pw = d.textlength(price, font=f_price)
        d.text((1112 - pw, y + 38), price, font=f_price, fill=col)
        y += 122

    d.text(
        (60, 566),
        "注：价格为本站标价，仅供参考；账户限额由平台按账户历史动态发放。",
        font=ImageFont.truetype(FONT_REG, 17),
        fill=DIM,
    )

    p = OUT / "price-anchor.png"
    img.convert("RGB").save(p, "PNG", optimize=True)
    return p


if __name__ == "__main__":
    for fn in (fig_account_spectrum, fig_bm_structure, fig_tiktok_flow, fig_price_anchor):
        p = fn()
        print(f"{p.name}: {p.stat().st_size / 1024:.1f} KB")
