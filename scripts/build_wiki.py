"""生成 wiki 知识页。

这些页面是本项目的自然流量入口：纯静态 HTML，爬虫不执行 JS 也能读全文。
内容为原创，参考行业公开信息整理，不复制竞品文案。
"""

import html
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wiki_content import FB_BODY, FB_FAQ, BM_BODY, BM_FAQ, TIKTOK_BODY, TIKTOK_FAQ  # noqa: E402
from wiki_articles2 import SHOPIFY_BODY, SHOPIFY_FAQ, REJECT_BODY, REJECT_FAQ  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wiki"
SITE = "https://xuanlanch.dpdns.org"
YE = "玄澜跨境"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass

FONT_STACK = (
    "'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', "
    "'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans SC', 'Segoe UI', sans-serif"
)

CSS = f"""
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: #000; color: #f5f5f7; font-family: {FONT_STACK};
      line-height: 1.85; -webkit-font-smoothing: antialiased;
    }}
    a {{ color: #2997ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 760px; margin: 0 auto; padding: 0 24px; }}
    nav {{ position: sticky; top: 0; z-index: 20; background: rgba(0,0,0,.82);
      backdrop-filter: blur(18px); border-bottom: 1px solid rgba(255,255,255,.1); }}
    nav .inner {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; height: 56px;
      display: flex; align-items: center; gap: 24px; }}
    nav .brand {{ font-weight: 600; font-size: 17px; color: #f5f5f7; }}
    nav .links {{ display: flex; gap: 20px; margin-left: auto; font-size: 13px; }}
    nav .links a {{ color: #a1a1a6; }}
    nav .links a:hover {{ color: #fff; text-decoration: none; }}
    nav .cta {{ background: #2997ff; color: #fff; padding: 7px 16px; border-radius: 980px; }}
    nav .cta:hover {{ background: #0071e3; color: #fff; text-decoration: none; }}
    @media (max-width: 720px) {{ nav .links {{ display: none; }} }}
    .crumbs {{ font-size: 12px; color: #6e6e73; padding: 24px 0 0; }}
    .crumbs a {{ color: #86868b; }}
    article {{ padding: 12px 0 40px; }}
    .eyebrow {{ color: #2997ff; font-size: 12px; font-weight: 600; letter-spacing: .09em;
      text-transform: uppercase; margin: 22px 0 12px; }}
    h1 {{ font-size: clamp(28px, 4.4vw, 40px); line-height: 1.25; letter-spacing: -.02em;
      font-weight: 600; margin: 0 0 16px; }}
    .lede {{ font-size: 17px; color: #a1a1a6; margin: 0 0 10px; }}
    .meta {{ font-size: 12px; color: #6e6e73; margin-bottom: 34px; }}
    h2 {{ font-size: 22px; margin: 46px 0 14px; font-weight: 600; letter-spacing: -.01em; }}
    h3 {{ font-size: 16px; margin: 26px 0 8px; font-weight: 600; color: #f5f5f7; }}
    p {{ color: #a1a1a6; font-size: 15.5px; margin: 0 0 14px; }}
    ul, ol {{ padding-left: 22px; margin: 0 0 16px; }}
    li {{ color: #a1a1a6; font-size: 15.5px; margin-bottom: 9px; }}
    strong {{ color: #f5f5f7; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin: 18px 0 22px; }}
    th, td {{ text-align: left; padding: 11px 12px; border-bottom: 1px solid #2a2a2c; vertical-align: top; }}
    th {{ color: #86868b; font-weight: 500; font-size: 13px; background: #141415; }}
    td {{ color: #d2d2d7; }}
    .callout {{ background: #141415; border-left: 2px solid #2997ff; padding: 16px 18px;
      margin: 22px 0; border-radius: 0 10px 10px 0; }}
    .callout p {{ margin: 0; font-size: 14.5px; }}
    .cta-box {{ background: #1d1d1f; border: 1px solid #2a2a2c; border-radius: 18px;
      padding: 24px; margin: 40px 0 0; }}
    .cta-box h2 {{ margin: 0 0 8px; font-size: 18px; }}
    .cta-box p {{ margin: 0 0 16px; font-size: 14px; }}
    .btn {{ display: inline-flex; align-items: center; gap: 6px; background: #2997ff;
      color: #fff; padding: 10px 20px; border-radius: 980px; font-size: 14px; font-weight: 500; }}
    .btn:hover {{ background: #0071e3; color: #fff; text-decoration: none; }}
    .btn.ghost {{ background: transparent; border: 1px solid #2997ff; color: #2997ff; margin-left: 10px; }}
    .btn.ghost:hover {{ background: #2997ff; color: #fff; }}
    .toc {{ background: #141415; border-radius: 14px; padding: 18px 22px; margin: 26px 0 8px; }}
    .toc .t {{ font-size: 12px; color: #86868b; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 10px; }}
    .toc ol {{ margin: 0; }}
    .toc li {{ font-size: 14px; margin-bottom: 6px; }}
    figure.fig {{ margin: 28px 0 30px; }}
    figure.fig img {{
      width: 100%; height: auto; display: block;
      border-radius: 14px; border: 1px solid #2a2a2c; background: #0a0a0b;
    }}
    figure.fig figcaption {{
      font-size: 13px; color: #6e6e73; margin-top: 10px; line-height: 1.6;
    }}
    footer {{ border-top: 1px solid #1d1d1f; padding: 32px 0; font-size: 12px; color: #6e6e73; margin-top: 40px; }}
    footer .inner {{ display: flex; flex-wrap: wrap; gap: 12px; justify-content: space-between; }}
"""


def esc(t):
    return html.escape(str(t), quote=True)


def page(slug, title, desc, h1, eyebrow, lede, body, faq=None, related=None):
    faq_ld = ""
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": desc,
        "datePublished": "2026-10-18",
        "dateModified": date.today().isoformat(),
        "author": {"@type": "Organization", "name": YE},
        "publisher": {"@type": "Organization", "name": YE},
        "mainEntityOfPage": f"{SITE}/wiki/{slug}/",
    }
    graph = [ld]
    if faq:
        graph.append(
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in faq
                ],
            }
        )
    graph.append(
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "出海知识库", "item": SITE + "/wiki/"},
                {"@type": "ListItem", "position": 3, "name": h1, "item": f"{SITE}/wiki/{slug}/"},
            ],
        }
    )
    faq_html = ""
    if faq:
        items = "".join(
            f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq
        )
        faq_html = f'<h2>常见问题</h2>{items}'

    rel_html = ""
    if related:
        links = "".join(
            f'<li><a href="/wiki/{s}/">{esc(t)}</a></li>' for s, t in related
        )
        rel_html = f'<h2>相关内容</h2><ul>{links}</ul>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta name="theme-color" content="#000000">
    <link rel="canonical" href="{SITE}/wiki/{slug}/">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{YE}">
    <meta property="og:locale" content="zh_CN">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:url" content="{SITE}/wiki/{slug}/">
    <meta property="og:image" content="{SITE}/assets/img/og-cover.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>">
    <style>{CSS}</style>
    <script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)}
    </script>
</head>
<body>
    <nav>
      <div class="inner">
        <a class="brand" href="/">🌐 {YE}</a>
        <div class="links">
          <a href="/products/">商品价格</a>
          <a href="/wiki/">知识库</a>
          <a href="/category/facebook/">Facebook</a>
          <a href="/category/tiktok/">TikTok</a>
          <a class="cta" href="/#contact">立即咨询</a>
        </div>
      </div>
    </nav>

    <main class="wrap">
      <div class="crumbs"><a href="/">首页</a> / <a href="/wiki/">出海知识库</a> / {esc(h1)}</div>
      <article>
        <div class="eyebrow">{esc(eyebrow)}</div>
        <h1>{esc(h1)}</h1>
        <p class="lede">{esc(lede)}</p>
        <div class="meta">更新于 {date.today().isoformat()} · 阅读约 6 分钟</div>
{body}
        <div class="cta-box">
          <h2>需要直接拿到可用的账号？</h2>
          <p>我们提供已交付的 Facebook 企业广告账户、养号与 TikTok 资产，现货可查，30 分钟内交付。</p>
          <a class="btn" href="/products/">查看价格与库存</a>
          <a class="btn ghost" href="/#contact">直接咨询</a>
        </div>
        {faq_html}
        {rel_html}
      </article>
    </main>

    <footer>
      <div class="wrap inner">
        <span>© <span id="year">{date.today().year}</span> Xuanlan Global</span>
        <span><a href="/">首页</a> · <a href="/products/">商品目录</a> · <a href="/wiki/">知识库</a> · <a href="/privacy.html">隐私政策</a></span>
      </div>
    </footer>
    <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def build_wiki_index(articles):
    cards = "".join(
        f"""<a class="item" href="/wiki/{s}/">
          <div class="cat">{esc(cat)}</div>
          <h2>{esc(t)}</h2>
          <p>{esc(d)}</p>
        </a>"""
        for s, t, d, cat in articles
    )
    body = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>出海知识库 | {YE}</title>
    <meta name="description" content="Facebook 账号类型、BM 开户、TikTok 橱窗号开通的实操指南。写给正在出海的中小卖家。">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{SITE}/wiki/">
    <meta property="og:title" content="出海知识库 | {YE}">
    <meta property="og:description" content="Facebook 账号类型、BM 开户、TikTok 橱窗号开通的实操指南。">
    <meta property="og:image" content="{SITE}/assets/img/og-cover.png">
    <meta property="og:url" content="{SITE}/wiki/">
    <meta property="og:locale" content="zh_CN">
    <meta name="twitter:card" content="summary_large_image">
    <style>{CSS}
      .list {{ display: grid; gap: 14px; padding: 24px 0 60px; }}
      .item {{ display: block; background: #141415; border: 1px solid #2a2a2c;
        border-radius: 16px; padding: 22px; transition: border-color .2s ease; }}
      .item:hover {{ border-color: #3a3a3c; text-decoration: none; }}
      .item .cat {{ font-size: 11px; color: #2997ff; letter-spacing: .08em;
        text-transform: uppercase; font-weight: 600; margin-bottom: 8px; }}
      .item h2 {{ font-size: 18px; margin: 0 0 8px; color: #f5f5f7; }}
      .item p {{ font-size: 14px; color: #86868b; margin: 0; }}
      .item:hover h2 {{ color: #2997ff; }}
    </style>
</head>
<body>
    <nav>
      <div class="inner">
        <a class="brand" href="/">🌐 {YE}</a>
        <div class="links">
          <a href="/products/">商品价格</a>
          <a href="/wiki/">知识库</a>
          <a class="cta" href="/#contact">立即咨询</a>
        </div>
      </div>
    </nav>
    <main class="wrap">
      <div class="crumbs"><a href="/">首页</a> / 出海知识库</div>
      <article>
        <div class="eyebrow">出海知识库</div>
        <h1>把账号和投放的事讲清楚</h1>
        <p class="lede">不卖关子的实操笔记：账号类型、开户门槛、避坑清单。看不明白的，直接来问。</p>
      </article>
      <div class="list">{cards}</div>
    </main>
    <footer>
      <div class="wrap inner">
        <span>© <span id="year">{date.today().year}</span> Xuanlan Global</span>
        <span><a href="/">首页</a> · <a href="/products/">商品目录</a></span>
      </div>
    </footer>
    <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""
    p = OUT / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def write(slug, *args, **kwargs):
    html_text = page(slug, *args, **kwargs)
    p = OUT / slug / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html_text, encoding="utf-8")
    return p


def main():
    write(
        "fb-account-types",
        "FB 账号类型完全指南：白号、三解号、大小黑都是什么 | " + YE,
        "Facebook 账号的 11 种常见分类、养号原理、想投广告该买哪种、哪些说法是坑。写给正在出海的中小卖家。",
        "FB 账号类型完全指南：白号、三解号、大小黑都是什么",
        "Facebook",
        "买号前先搞清楚这些词到底指什么。选错类型，90% 的预算会浪费在不能用的账号上。",
        FB_BODY,
        faq=FB_FAQ,
        related=[
            ("bm-guide", "BM 开户与广告账户类型：个人户、企业户、二不限怎么选"),
            ("tiktok-shop-guide", "TikTok 橱窗号怎么开：各国门槛与常见坑"),
            ("shopify-dropshipping", "独立站选品与建站：从 0 到能投放"),
        ],
    )

    write(
        "bm-guide",
        "BM 开户与广告账户类型：个人户、企业户、二不限怎么选 | " + YE,
        "BM 是什么、个人户与企业户的差异、二不限的含义、什么阶段该换企业户、开户前的准备清单。",
        "BM 开户与广告账户类型：个人户、企业户、二不限怎么选",
        "Meta",
        "账户类型选错，是投放跑不起来最常见的原因。这篇讲清楚三者到底差在哪。",
        BM_BODY,
        faq=BM_FAQ,
        related=[
            ("fb-account-types", "FB 账号类型完全指南"),
            ("tiktok-shop-guide", "TikTok 橱窗号怎么开"),
            ("ad-rejection-guide", "广告被拒登怎么办"),
        ],
    )

    write(
        "tiktok-shop-guide",
        "TikTok 橱窗号怎么开：各国门槛、所需资料与常见坑 | " + YE,
        "TikTok 橱窗号是什么、东南亚各国开通门槛、「0 粉挂车」的真实限制、自己开的号为什么会掉，以及完整落地路径。",
        "TikTok 橱窗号怎么开：各国门槛、所需资料与常见坑",
        "TikTok",
        "开通只要一两天，养出一个能卖货的号要几个月。先把规则搞明白，少走弯路。",
        TIKTOK_BODY,
        faq=TIKTOK_FAQ,
        related=[
            ("fb-account-types", "FB 账号类型完全指南"),
            ("bm-guide", "BM 开户与广告账户类型"),
            ("shopify-dropshipping", "独立站选品与建站"),
        ],
    )

    write(
        "shopify-dropshipping",
        "独立站选品与建站：从 0 到能投放的完整流程 | " + YE,
        "独立站与平台店的本质区别、选品排除法、用最小成本验证产品、详情页必备的 6 个模块，以及新手的 4 个常见错误。",
        "独立站选品与建站：从 0 到能投放的完整流程",
        "独立站",
        "独立站不是「更高级的店铺」，是一台需要燃料的机器。先想清楚燃料从哪来。",
        SHOPIFY_BODY,
        faq=SHOPIFY_FAQ,
        related=[
            ("bm-guide", "BM 开户与广告账户类型"),
            ("ad-rejection-guide", "广告被拒登怎么办"),
            ("fb-account-types", "FB 账号类型完全指南"),
        ],
    )

    write(
        "ad-rejection-guide",
        "广告被拒登怎么办：8 种高频原因与申诉写法 | " + YE,
        "拒登与封号的本质区别、三步定位问题层级、8 种最常见拒登原因对照表、有效申诉应包含的内容，以及预防清单。",
        "广告被拒登怎么办：8 种高频原因与申诉写法",
        "投放",
        "拒登不等于封号。先花十分钟判断问题在哪一层，比盲目改素材省事得多。",
        REJECT_BODY,
        faq=REJECT_FAQ,
        related=[
            ("bm-guide", "BM 开户与广告账户类型"),
            ("shopify-dropshipping", "独立站选品与建站"),
            ("fb-account-types", "FB 账号类型完全指南"),
        ],
    )

    build_wiki_index(
        [
            (
                "fb-account-types",
                "FB 账号类型完全指南：白号、三解号、大小黑都是什么",
                "11 种账号分类、养号周期、哪些能直接投广告、哪些一登就死。",
                "Facebook",
            ),
            (
                "bm-guide",
                "BM 开户与广告账户类型：个人户、企业户、二不限怎么选",
                "BM 是什么、三种账户的限额与稳定性差异、什么阶段该换企业户。",
                "Meta",
            ),
            (
                "tiktok-shop-guide",
                "TikTok 橱窗号怎么开：各国门槛、所需资料与常见坑",
                "东南亚六国的开通条件、0 粉挂车的真实限制、为什么自己开的号经常掉。",
                "TikTok",
            ),
            (
                "shopify-dropshipping",
                "独立站选品与建站：从 0 到能投放的完整流程",
                "选品排除法、最小成本验证、详情页 6 个必备模块、新手的 4 个错误。",
                "独立站",
            ),
            (
                "ad-rejection-guide",
                "广告被拒登怎么办：8 种高频原因与申诉写法",
                "拒登与封号的区别、三步定位问题、8 种原因对照表、预防清单。",
                "投放",
            ),
        ]
    )

    print("wiki 页面生成完成：5 篇文章 + 1 个索引页")
    return 0


if __name__ == "__main__":
    sys.exit(main())
