"""从 data/products.json 生成全站静态页面。

设计目标（对标 RunAdStore 的结构性弱点）：
* 每个商品一个独立 URL，纯静态 HTML，爬虫不执行 JS 也能读全
* 每页自带 Product / Offer / BreadcrumbList 结构化数据
* sitemap.xml 与 robots.txt 由数据自动生成，不会漏
* 商品清单改一份 JSON，全站重建

用法：
    python scripts/build_pages.py
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "products.json"
OUT = ROOT
SITE = "https://xuanlanch.dpdns.org"
YE = "玄澜跨境"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass


def esc(text):
    return html.escape(str(text), quote=True)


def money(value):
    """0.08 -> 0.08 ；420 -> 420"""
    if isinstance(value, float) and value != int(value):
        return f"{value:g}"
    return f"{int(value)}" if float(value).is_integer() else f"{value:g}"


FONT_STACK = (
    "'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', "
    "'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans SC', 'Segoe UI', sans-serif"
)

BASE_CSS = f"""
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: #000; color: #f5f5f7;
      font-family: {FONT_STACK};
      line-height: 1.7; -webkit-font-smoothing: antialiased;
    }}
    a {{ color: #2997ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}
    nav {{
      position: sticky; top: 0; z-index: 20;
      background: rgba(0,0,0,.82); backdrop-filter: blur(18px);
      border-bottom: 1px solid rgba(255,255,255,.1);
    }}
    nav .inner {{
      max-width: 1080px; margin: 0 auto; padding: 0 24px; height: 56px;
      display: flex; align-items: center; gap: 28px;
    }}
    nav .brand {{ font-weight: 600; font-size: 17px; color: #f5f5f7; display: flex; align-items: center; gap: 8px; }}
    nav .links {{ display: flex; gap: 22px; margin-left: auto; font-size: 13px; }}
    nav .links a {{ color: #a1a1a6; }}
    nav .links a:hover {{ color: #fff; text-decoration: none; }}
    nav .cta {{
      background: #2997ff; color: #fff; padding: 7px 16px; border-radius: 980px;
      font-weight: 500;
    }}
    nav .cta:hover {{ background: #0071e3; color: #fff; text-decoration: none; }}
    header.hero {{ padding: 72px 0 40px; }}
    h1 {{ font-size: clamp(30px, 5vw, 46px); line-height: 1.18; margin: 0 0 16px; letter-spacing: -.02em; font-weight: 600; }}
    .lede {{ font-size: 17px; color: #a1a1a6; max-width: 660px; margin: 0 0 8px; }}
    .eyebrow {{ color: #2997ff; font-size: 13px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; padding: 24px 0 64px; }}
    .card {{
      background: #1d1d1f; border: 1px solid #2a2a2c; border-radius: 18px;
      padding: 20px; display: flex; flex-direction: column; gap: 12px;
      transition: transform .2s ease, border-color .2s ease;
    }}
    .card:hover {{ transform: translateY(-2px); border-color: #3a3a3c; }}
    .card .name {{ font-size: 16px; font-weight: 600; line-height: 1.45; margin: 0; }}
    .card .summary {{ font-size: 13px; color: #86868b; margin: 0; flex: 1; }}
    .card .bottom {{ display: flex; align-items: baseline; justify-content: space-between; gap: 10px; }}
    .price {{ font-size: 22px; font-weight: 600; color: #f5f5f7; }}
    .price .cur {{ font-size: 13px; color: #86868b; font-weight: 400; margin-right: 2px; }}
    .was {{ color: #6e6e73; font-size: 13px; text-decoration: line-through; margin-left: 6px; }}
    .stock {{ font-size: 12px; color: #86868b; white-space: nowrap; }}
    .stock.low {{ color: #ff9f0a; }}
    .badges {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .badge {{
      font-size: 11px; padding: 2px 9px; border-radius: 980px;
      border: 1px solid #3a3a3c; color: #a1a1a6;
    }}
    .badge.hot {{ border-color: #2997ff; color: #2997ff; }}
    .buy {{
      display: inline-flex; align-items: center; justify-content: center;
      background: #2997ff; color: #fff; border: 0; cursor: pointer;
      padding: 10px 18px; border-radius: 980px; font-size: 14px; font-weight: 500;
      font-family: inherit; width: 100%;
    }}
    .buy:hover {{ background: #0071e3; text-decoration: none; }}
    .buy.ghost {{ background: transparent; border: 1px solid #2997ff; color: #2997ff; }}
    .buy.ghost:hover {{ background: #2997ff; color: #fff; }}
    table.specs {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    table.specs th, table.specs td {{ text-align: left; padding: 11px 0; border-bottom: 1px solid #2a2a2c; }}
    table.specs th {{ color: #86868b; font-weight: 400; width: 38%; }}
    table.specs td {{ color: #f5f5f7; }}
    ul.plain {{ padding-left: 18px; margin: 0; }}
    ul.plain li {{ color: #a1a1a6; font-size: 14px; margin-bottom: 8px; }}
    .detail {{ display: grid; grid-template-columns: 1.15fr .85fr; gap: 40px; padding: 40px 0 72px; align-items: start; }}
    @media (max-width: 860px) {{
      .detail {{ grid-template-columns: 1fr; gap: 28px; }}
      nav .links {{ display: none; }}
    }}
    .panel {{ background: #1d1d1f; border: 1px solid #2a2a2c; border-radius: 20px; padding: 24px; }}
    .panel h2 {{ font-size: 15px; margin: 0 0 14px; font-weight: 600; }}
    .crumbs {{ font-size: 12px; color: #6e6e73; padding: 20px 0 0; }}
    .crumbs a {{ color: #86868b; }}
    footer {{ border-top: 1px solid #1d1d1f; padding: 36px 0; font-size: 12px; color: #6e6e73; }}
    footer .inner {{ display: flex; flex-wrap: wrap; gap: 12px; justify-content: space-between; }}
    .note {{ font-size: 13px; color: #86868b; border-left: 2px solid #2997ff; padding-left: 12px; margin: 20px 0; }}
    .cat-head {{ padding: 56px 0 8px; }}
    h2.sec {{ font-size: 24px; margin: 0 0 8px; font-weight: 600; }}
    .muted {{ color: #86868b; font-size: 15px; }}
    .grad {{ background: linear-gradient(135deg,#2997ff,#7cc7ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .trust {{ display: flex; flex-wrap: wrap; gap: 18px; margin: 22px 0 26px; font-size: 13px; color: #a1a1a6; }}
    .catnav {{ display: flex; flex-wrap: wrap; gap: 10px; padding-bottom: 8px; }}
    .pill {{ display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 980px;
             border: 1px solid #3a3a3c; color: #f5f5f7; font-size: 14px; }}
    .pill:hover {{ border-color: #2997ff; color: #2997ff; text-decoration: none; }}
    .pill .n {{ font-size: 11px; color: #86868b; background: #2a2a2c; padding: 1px 7px; border-radius: 980px; }}
"""


def shell(title, desc, canonical, body, jsonld=None, og_image="/assets/img/og-cover.png"):
    ld = ""
    if jsonld:
        ld = (
            '\n    <script type="application/ld+json">\n'
            + json.dumps(jsonld, ensure_ascii=False, indent=2)
            + "\n    </script>"
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta name="theme-color" content="#000000">
    <link rel="canonical" href="{esc(canonical)}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{YE}">
    <meta property="og:locale" content="zh_CN">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:image" content="{SITE}{og_image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>">
    <style>{BASE_CSS}</style>{ld}
</head>
<body>
    <nav>
      <div class="inner">
        <a class="brand" href="/">🌐 玄澜跨境</a>
        <div class="links">
          <a href="/products/">全部商品</a>
          <a href="/category/facebook/">Facebook</a>
          <a href="/category/tiktok/">TikTok</a>
          <a href="/category/email/">邮箱资源</a>
          <a href="/category/service/">建站代运营</a>
          <a class="cta" href="/#contact">立即咨询</a>
        </div>
      </div>
    </nav>
{body}
    <footer>
      <div class="wrap inner">
        <span>© <span id="year">{date.today().year}</span> Xuanlan Global · 社交媒体广告资产解决方案</span>
        <span><a href="/privacy.html">隐私政策</a> · <a href="/terms.html">服务条款</a> · <a href="/products/">商品目录</a></span>
      </div>
    </footer>
    <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def stock_label(stock):
    if stock is None:
        return "现货可询", "stock"
    if stock <= 0:
        return "缺货", "stock"
    if stock <= 5:
        return f"仅剩 {stock} 件", "stock low"
    return f"库存 {stock}", "stock"


def badge_html(tags):
    out = []
    for t in tags or []:
        cls = "badge hot" if t in ("热销", "推荐") else "badge"
        out.append(f'<span class="{cls}">{esc(t)}</span>')
    return f'<div class="badges">{"".join(out)}</div>' if out else ""


def card_html(item, cat):
    label, cls = stock_label(item.get("stock"))
    was = f'<span class="was">${money(item["was"])}</span>' if item.get("was") else ""
    if item.get("price") == 0 and item.get("priceNote"):
        price = f'<span class="price" style="font-size:15px">{esc(item["priceNote"])}</span>'
    else:
        price = f'<span class="price"><span class="cur">$</span>{money(item["price"])}{was}</span>'
    return f"""      <a class="card" href="/product/{esc(item['id'])}/">
        {badge_html(item.get('tags'))}
        <h3 class="name">{esc(item['name'])}</h3>
        <p class="summary">{esc(item['summary'])}</p>
        <div class="bottom">
          {price}
          <span class="{cls}">{esc(label)}</span>
        </div>
        <span class="buy">查看详情</span>
      </a>"""


def build_products_index(data):
    cards = []
    for cat in data["categories"]:
        for item in cat["items"]:
            cards.append(card_html(item, cat))
    catnav = "".join(
        f'<a class="pill" href="/category/{c["slug"]}/">{esc(c["name"])} <span class="n">{len(c["items"])}</span></a>'
        for c in data["categories"]
    )
    body = f"""    <main class="wrap">
      <header class="hero">
        <div class="eyebrow">全球广告资产商城</div>
        <h1>社交媒体广告资产<br><span class="grad">一站式采购</span></h1>
        <p class="lede">Facebook 企业广告账户、养号、TikTok 资产、邮箱资源与建站代运营。
        下单前可先咨询，交付全程可追踪，支持支付宝 / 微信 / USDT。</p>
        <div class="trust">
          <span>✔ 现货 {sum(len(c["items"]) for c in data["categories"])} 款</span>
          <span>✔ 30 分钟交付</span>
          <span>✔ 7 天售后</span>
          <span>✔ 支持开票</span>
        </div>
        <div class="catnav">{catnav}</div>
      </header>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </main>"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{YE}｜全部商品",
        "url": f"{SITE}/products/",
        "isPartOf": {"@type": "WebSite", "name": YE, "url": SITE + "/"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(cards),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{SITE}/product/{item['id']}/",
                    "name": item["name"],
                }
                for i, item in enumerate(
                    [i for c in data["categories"] for i in c["items"]]
                )
            ],
        },
    }
    path = OUT / "products" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        shell(
            f"社交媒体广告资产与出海资源 | {YE}",
            f"{YE}商品目录：Facebook 企业广告账户、养号、TikTok 橱窗号、邮箱资源与建站代运营，价格库存实时更新。",
            f"{SITE}/products/",
            body,
            jsonld,
        ),
        encoding="utf-8",
    )
    return len(cards)


def build_category(cat):
    cards = [card_html(i, cat) for i in cat["items"]]
    body = f"""    <main class="wrap">
      <div class="crumbs"><a href="/">首页</a> / <a href="/products/">全部商品</a> / {esc(cat['name'])}</div>
      <header class="cat-head">
        <div class="eyebrow">分类</div>
        <h1>{esc(cat['name'])}</h1>
        <p class="lede">{esc(cat['desc'])}</p>
      </header>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </main>"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{cat['name']}｜{YE}",
        "url": f"{SITE}/category/{cat['slug']}/",
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{SITE}/product/{it['id']}/",
                    "name": it["name"],
                }
                for i, it in enumerate(cat["items"])
            ],
        },
    }
    path = OUT / "category" / cat["slug"] / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        shell(
            f"{cat['name']} 价格与库存 | {YE}",
            f"{cat['desc']} 共 {len(cat['items'])} 款，价格与库存实时更新。",
            f"{SITE}/category/{cat['slug']}/",
            body,
            jsonld,
        ),
        encoding="utf-8",
    )
    return len(cards)


def build_product(item, cat):
    label, cls = stock_label(item.get("stock"))
    specs = "\n".join(
        f'        <tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>'
        for k, v in item.get("specs", {}).items()
    )
    highlights = "\n".join(
        f"        <li>{esc(h)}</li>" for h in item.get("highlights", [])
    )
    if item.get("price") == 0 and item.get("priceNote"):
        price_block = f'<div class="price" style="font-size:18px">{esc(item["priceNote"])}</div>'
        offer_price = None
    else:
        was = f'<span class="was">${money(item["was"])}</span>' if item.get("was") else ""
        price_block = f'<div class="price"><span class="cur">$</span>{money(item["price"])}{was}</div>'
        offer_price = f'{item["price"]:g}'

    body = f"""    <main class="wrap">
      <div class="crumbs"><a href="/">首页</a> / <a href="/products/">全部商品</a> / <a href="/category/{esc(cat['slug'])}/">{esc(cat['name'])}</a> / {esc(item['name'])}</div>
      <div class="detail">
        <div>
          <div class="eyebrow">{esc(cat['name'])}</div>
          <h1>{esc(item['name'])}</h1>
          <p class="lede">{esc(item['summary'])}</p>
          {badge_html(item.get('tags'))}
          <h2 class="sec" style="margin-top:34px">这个账号包含什么</h2>
          <ul class="plain" style="margin-top:12px">
{highlights}
          </ul>
          <h2 class="sec" style="margin-top:34px">规格明细</h2>
          <table class="specs" style="margin-top:8px">
{specs}
          </table>
          <p class="note">下单前请确认账号类型与投放用途。账号类资产一经交付不支持退换；
          交付后 7 天内因我方原因导致无法使用的，免费补发。</p>
        </div>
        <aside class="panel">
          <h2>价格</h2>
          {price_block}
          <div class="{cls}" style="margin:6px 0 18px">{esc(label)}</div>
          <a class="buy" href="/#contact">立即咨询购买</a>
          <a class="buy ghost" href="/category/{esc(cat['slug'])}/" style="margin-top:10px">看同类商品</a>
          <h2 style="margin-top:26px">付款方式</h2>
          <ul class="plain">
            <li>支付宝 / 微信</li>
            <li>USDT（Arbitrum One）</li>
            <li>对公转账（可开票）</li>
          </ul>
        </aside>
      </div>
    </main>"""

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": item["name"],
        "description": item["summary"],
        "sku": item["id"],
        "brand": {"@type": "Brand", "name": YE},
        "url": f"{SITE}/product/{item['id']}/",
        "category": cat["name"],
    }
    if offer_price is not None:
        avail = (
            "https://schema.org/InStock"
            if item.get("stock", 1) > 0
            else "https://schema.org/OutOfStock"
        )
        jsonld["offers"] = {
            "@type": "Offer",
            "price": offer_price,
            "priceCurrency": "USD",
            "availability": avail,
            "url": f"{SITE}/product/{item['id']}/",
            "seller": {"@type": "Organization", "name": YE},
        }
    jsonld["@graph"] = [
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "全部商品", "item": SITE + "/products/"},
                {"@type": "ListItem", "position": 3, "name": cat["name"], "item": f"{SITE}/category/{cat['slug']}/"},
                {"@type": "ListItem", "position": 4, "name": item["name"], "item": f"{SITE}/product/{item['id']}/"},
            ],
        }
    ]

    path = OUT / "product" / item["id"] / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        shell(
            f"{item['name']} 价格 | {YE}",
            f"{item['summary']} 现价 ${money(item['price'])}。",
            f"{SITE}/product/{item['id']}/",
            body,
            jsonld,
        ),
        encoding="utf-8",
    )


def build_sitemap(data):
    urls = [
        ("/", "1.0", "weekly"),
        ("/products/", "0.9", "daily"),
    ]
    for cat in data["categories"]:
        urls.append((f"/category/{cat['slug']}/", "0.8", "daily"))
        for item in cat["items"]:
            urls.append((f"/product/{item['id']}/", "0.7", "daily"))
    urls.append(("/wiki/", "0.8", "weekly"))
    for slug in ("fb-account-types", "bm-guide", "tiktok-shop-guide", "shopify-dropshipping", "ad-rejection-guide"):
        urls.append((f"/wiki/{slug}/", "0.7", "monthly"))
    urls += [
        ("/privacy.html", "0.2", "yearly"),
        ("/terms.html", "0.2", "yearly"),
    ]
    today = data.get("updated") or date.today().isoformat()
    entries = "\n".join(
        f"""    <url>
        <loc>{SITE}{path}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>{freq}</changefreq>
        <priority>{prio}</priority>
    </url>"""
        for path, prio, freq in urls
    )
    (OUT / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
""",
        encoding="utf-8",
    )
    return len(urls)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    n_all = build_products_index(data)
    n_cat = 0
    n_item = 0
    for cat in data["categories"]:
        n_cat += build_category(cat)
        for item in cat["items"]:
            build_product(item, cat)
            n_item += 1
    n_url = build_sitemap(data)
    print(f"商品总数      : {n_item}")
    print(f"商品卡片      : {n_all}")
    print(f"分类页        : {len(data['categories'])}")
    print(f"商品详情页    : {n_item}")
    print(f"sitemap URL 数: {n_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
