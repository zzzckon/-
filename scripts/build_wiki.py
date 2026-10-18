"""生成 wiki 知识页。

这些页面是本项目的自然流量入口：纯静态 HTML，爬虫不执行 JS 也能读全文。
内容为原创，参考行业公开信息整理，不复制竞品文案。
"""

import html
import json
import sys
from datetime import date
from pathlib import Path

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


# ---------------------------------------------------------------- 文章 1

FB_TYPES_BODY = """
        <div class="toc">
          <div class="t">本文目录</div>
          <ol>
            <li><a href="#why">为什么账号分这么多类型</a></li>
            <li><a href="#types">11 种常见分类是什么</a></li>
            <li><a href="#warmup">养号到底在养什么</a></li>
            <li><a href="#ads">想直接投广告该买哪种</a></li>
            <li><a href="#scam">哪些说法是坑</a></li>
          </ol>
        </div>

        <h2 id="why">为什么账号分这么多类型</h2>
        <p>Facebook 的风控不是一道闸门，而是一串连续的状态判断：这个账号像不像真人、有没有真实社交关系、能不能承担广告消费、历史上有没有违规记录。</p>
        <p>账号交易市场里的各种叫法，本质上是<strong>把这条连续光谱切成几段</strong>，方便报价。所以你会看到「白号」「三解号」「大小黑」「不充电」这类词——它们描述的都是同一个东西的不同切面：<strong>这个号现在处在什么状态，能干什么，干过什么</strong>。</p>
        <div class="callout">
          <p>买号之前先问自己一个问题：我要它登录发内容，还是要它挂广告？这两个需求对应的账号类型完全不同，买错了号 90% 会浪费。</p>
        </div>

        <h2 id="types">11 种常见分类是什么</h2>
        <table>
          <thead><tr><th>类型</th><th>含义</th><th>适合场景</th></tr></thead>
          <tbody>
            <tr><td>白号</td><td>刚注册、无广告行为、无违规记录的干净账号</td><td>需要自己养、自己绑定资产</td></tr>
            <tr><td>新号 / 老号</td><td>按注册时长区分，老号社交历史更完整</td><td>老号更耐受风控</td></tr>
            <tr><td>耐用号</td><td>经过一定养护、登录环境稳定的账号</td><td>长期运营账号</td></tr>
            <tr><td>专页号</td><td>已绑定或可绑定公共主页的账号</td><td>品牌页运营</td></tr>
            <tr><td>有绿标号</td><td>带认证或信任标记的账号</td><td>需要更高信任度</td></tr>
            <tr><td>大小号</td><td>主账号与辅助账号的搭配组合</td><td>矩阵运营、分散风险</td></tr>
            <tr><td>三解号 / 二解号</td><td>被限制后通过申诉解除某种限制的账号（三解=解除三类限制）</td><td>需要较高投放容忍度</td></tr>
            <tr><td>小黑 / 大白号</td><td>行业黑话，指历史状态与当前可用性的不同组合</td><td>价格低，风险也高</td></tr>
            <tr><td>不充电号</td><td>没有历史广告消费记录的账号</td><td>需要自己起量</td></tr>
            <tr><td>Meta 认证账号</td><td>完成 Meta 官方身份验证</td><td>长期品牌投放</td></tr>
            <tr><td>已登录状态号</td><td>带有效登录态，可直接使用</td><td>快速上手</td></tr>
          </tbody>
        </table>
        <p>注意：<strong>这些术语没有官方定义</strong>，不同卖家的叫法可能不一致。看到「三解」这种词，一定要问清具体解除了哪三类限制、有没有截图证据。</p>

        <h2 id="warmup">养号到底在养什么</h2>
        <p>养号不是玄学，是在人为补足这几项信号：</p>
        <ul>
          <li><strong>设备与 IP 的一致性</strong>：长期在同一个设备、同一地区 IP 登录</li>
          <li><strong>社交关系</strong>：加好友、互动、加群，让它不像个空壳</li>
          <li><strong>行为轨迹</strong>：浏览、点赞、停留时长</li>
          <li><strong>时间</strong>：注册时间越久、记录越平滑，越不容易被判定为批量注册</li>
        </ul>
        <p>养号周期通常要 <strong>7 到 30 天</strong>，视账号用途而定。想马上投广告的，养号这条路基本走不通——那是企业广告账户要解决的问题。</p>

        <h2 id="ads">想直接投广告该买哪种</h2>
        <p>这是最多人踩坑的地方。个人号 + 自己开的广告账户，限额低、审核慢、封了很难申诉。真正用来跑量的通常是<strong>企业广告账户（代理开户）</strong>，特征是：</p>
        <ul>
          <li>绑定在 BM（商务管理平台）下，不是挂在个人身上</li>
          <li>日消耗限额按账户等级发放，可以用得更高</li>
          <li>账户被限制时，可以联系代理经理协助申诉</li>
          <li>支持绑定公共主页、像素、域名</li>
        </ul>
        <p>所以正确的路径一般是：<strong>先有 BM 或企业广告账户，再配套个人号做操作者</strong>，而不是反过来。</p>

        <h2 id="scam">哪些说法是坑</h2>
        <ul>
          <li><strong>「永不被封」</strong>——没有这种账号。只能说稳定性有差异。</li>
          <li><strong>「0 粉直接挂车，完全没风险」</strong>——平台规则在变，挂车本身有门槛和审核。</li>
          <li><strong>「账号带原始邮箱，绝对安全」</strong>——要看邮箱是不是真的原始、有没有二次验证绑定。</li>
          <li><strong>价格低得不合理</strong>——通常意味着来源不明或已被标记。</li>
        </ul>
        <p>判断一个卖家靠不靠谱，比价格更有效的指标是：<strong>能不能说清账号来源、能不能给登录截图、出问题多久内补发</strong>。</p>
"""

FB_TYPES_FAQ = [
    (
        "买 FB 账号能直接投广告吗？",
        "个人号通常需要先绑定 BM 并开通广告账户，且初始限额较低。要直接投放，一般购买企业广告账户（含 BM 授权）更合适。",
    ),
    (
        "三解号、二解号是什么意思？",
        "指账号曾被平台限制，之后通过申诉解除了若干类限制。具体解除哪几类没有统一标准，购买前务必让卖家说明并提供证据。",
    ),
    (
        "新号和老号差在哪？",
        "主要是注册时长带来的社交记录与行为轨迹差异。老号通常更耐受风控，但也更贵；新号便宜但需要自己养。",
    ),
    (
        "养号要多久？",
        "常见周期是 7 到 30 天，取决于用途。如果目的是尽快投广告，应该直接走企业广告账户，而不是养个人号。",
    ),
]


# ---------------------------------------------------------------- 文章 2

BM_BODY = """
        <div class="toc">
          <div class="t">本文目录</div>
          <ol>
            <li><a href="#what">BM 到底是什么</a></li>
            <li><a href="#diff">个人户 / 企业户 / 二不限的区别</a></li>
            <li><a href="#when">什么阶段该换企业户</a></li>
            <li><a href="#limit">限额和稳定性怎么看</a></li>
            <li><a href="#checklist">开户前准备清单</a></li>
          </ol>
        </div>

        <h2 id="what">BM 到底是什么</h2>
        <p>BM 是 Meta 商务管理平台（Business Manager）的简称。它可以理解成一个<strong>资产容器</strong>：把广告账户、公共主页、像素、商品目录、支付方式都装进一个组织下面，然后给不同的人分配不同权限。</p>
        <p>没有 BM 的时候，广告账户挂在个人账号上——个人号一封，账户和素材全没。有了 BM，资产挂在组织下，个人号只是「操作者」，换人、加人都不影响资产本身。</p>
        <table>
          <thead><tr><th>资产</th><th>挂个人号下</th><th>挂 BM 下</th></tr></thead>
          <tbody>
            <tr><td>广告账户</td><td>随个人号封禁一起失效</td><td>可在组织内转移、更换操作者</td></tr>
            <tr><td>公共主页</td><td>迁移麻烦</td><td>可授权给多人管理</td></tr>
            <tr><td>像素 / 数据</td><td>重建即丢失历史数据</td><td>组织内共享</td></tr>
            <tr><td>团队协作</td><td>只能共享账号密码</td><td>分级权限</td></tr>
          </tbody>
        </table>

        <h2 id="diff">个人户 / 企业户 / 二不限的区别</h2>
        <h3>个人广告账户</h3>
        <p>用个人号自助开通，门槛低、开得快，但限额小、申诉通道弱，适合验证产品和少量测试。</p>
        <h3>企业广告账户（代理开户）</h3>
        <p>通过代理走企业资质开通，绑定在 BM 下。优势是限额等级更高、有代理经理可协助申诉、支持更多资产类型。行业里常说的「电商户」「游戏户」就是按用途和资质分的不同开通通道。</p>
        <h3>二不限 / 三不限</h3>
        <p>指投放限制较少的账户类型（例如不限制某些品类或投放范围）。这类账户通常价格更高，适合已经跑通模式、需要放量的团队。<strong>注意</strong>：不同代理对「二不限」的具体含义说法不完全一致，签约前要问清到底不限哪两项。</p>

        <h2 id="when">什么阶段该换企业户</h2>
        <ul>
          <li><strong>日消耗稳定超过个人户限额</strong>：说明模型跑通了，卡在额度上</li>
          <li><strong>需要多人协作</strong>：投手、素材、财务要分权限</li>
          <li><strong>需要稳定长期投放</strong>：个人号封一次就断流，成本远高于账户差价</li>
          <li><strong>需要绑定多个主页或站点</strong>：BM 内管理更清晰</li>
        </ul>
        <div class="callout">
          <p>判断标准其实很简单：<strong>如果你开始因为「账户被封导致投放中断」而焦虑，就该上企业户了。</strong></p>
        </div>

        <h2 id="limit">限额和稳定性怎么看</h2>
        <p>广告账户的日消耗限额不是固定的，平台会根据账户历史表现动态调整。影响它的因素包括：</p>
        <ul>
          <li>账户的注册时间与历史消费</li>
          <li>支付方式是否稳定（是否频繁拒付）</li>
          <li>广告内容与落地页的合规记录</li>
          <li>拒登率、投诉率</li>
        </ul>
        <p>所以「买一个高限额账户」不是终点——<strong>账户买来后如果违规操作，限额照样会掉</strong>。这也是为什么素材合规和落地页质量比账户等级更值得投入。</p>

        <h2 id="checklist">开户前准备清单</h2>
        <ol>
          <li>营业执照或主体资质（代理开户通常需要）</li>
          <li>可用的公共主页（建议提前建好，名称与业务一致）</li>
          <li>落地页与隐私政策页（审核会看）</li>
          <li>支付方式：信用卡 / PayPal / 对公</li>
          <li>像素或转化 API 的接入方案</li>
          <li>明确的目标市场与品类（影响开通通道选择）</li>
        </ol>
        <p>准备齐再开户，比反复提交被拒要快得多。</p>
"""

BM_FAQ = [
    (
        "BM 被封了怎么办？",
        "先确认是 BM 本身被限制还是下属资产被限制。BM 被限制通常可以通过申诉或由代理协助处理，但周期不确定，所以建议保留备用 BM。",
    ),
    (
        "个人户能转成企业户吗？",
        "不能直接转换。企业广告账户需要按对应通道重新开通，历史数据需要通过像素和主页延续，而不是账户本身。",
    ),
    (
        "二不限比普通企业户贵在哪？",
        "主要是投放限制更少、适用品类更广，因此供应更少、价格更高。购买前要确认具体不限的项目。",
    ),
]


# ---------------------------------------------------------------- 文章 3

TIKTOK_BODY = """
        <div class="toc">
          <div class="t">本文目录</div>
          <ol>
            <li><a href="#what">橱窗号是什么</a></li>
            <li><a href="#gate">各国开通门槛</a></li>
            <li><a href="#zero">「0 粉挂车」的真实情况</a></li>
            <li><a href="#why">为什么自己开的号经常掉</a></li>
            <li><a href="#how">从 0 到能带货的完整路径</a></li>
          </ol>
        </div>

        <h2 id="what">橱窗号是什么</h2>
        <p>TikTok 的电商功能（TikTok Shop）允许创作者在视频和直播里挂商品链接，观众点进去就能下单。开通这个能力的账号，行业里俗称「橱窗号」或「带货号」。</p>
        <p>对卖家来说，它解决的是一个很实际的问题：<strong>有了橱窗，内容就能直接变成成交</strong>，不用把用户导到站外。</p>

        <h2 id="gate">各国开通门槛</h2>
        <p>不同站点的要求差异很大，而且<strong>平台规则一直在变</strong>。以下是常见维度的对比，具体数值请以平台当期规则为准：</p>
        <table>
          <thead><tr><th>维度</th><th>通常要求</th><th>说明</th></tr></thead>
          <tbody>
            <tr><td>粉丝数</td><td>部分站点有门槛，部分放宽</td><td>放宽不等于没有审核</td></tr>
            <tr><td>年龄</td><td>通常 18 岁以上</td><td>需要实名信息</td></tr>
            <tr><td>账号地区</td><td>需与目标站点一致</td><td>地区与手机号、注册环境相关</td></tr>
            <tr><td>身份/资质</td><td>部分站点需本地身份或企业资质</td><td>东南亚各站差异大</td></tr>
            <tr><td>账号状态</td><td>无严重违规记录</td><td>有过限制的号难过审</td></tr>
          </tbody>
        </table>
        <p>常见站点包括新加坡、马来西亚、印尼、泰国、菲律宾、越南。<strong>印尼市场对本地资质的要求历来最严</strong>，这是新手最容易低估的地方。</p>

        <h2 id="zero">「0 粉挂车」的真实情况</h2>
        <p>市场上普遍宣传「0 粉即可挂车」。这句话要分两层看：</p>
        <ul>
          <li><strong>技术上</strong>：确实存在不需要粉丝数的开通路径</li>
          <li><strong>实际上</strong>：<strong>挂得上车 ≠ 卖得动货</strong>。没有粉丝就没有流量，商品挂在一个没人看的视频下，等于没挂</li>
        </ul>
        <div class="callout">
          <p>橱窗解决的是「成交环节」，不是「流量环节」。开完号之后真正的难题是内容，这个号本身不提供。</p>
        </div>

        <h2 id="why">为什么自己开的号经常掉</h2>
        <p>自己注册的账号容易在几周内失效，通常和这几件事有关：</p>
        <ul>
          <li><strong>注册环境不稳定</strong>：IP 频繁变动、设备指纹异常</li>
          <li><strong>资料不完整</strong>：头像、简介、发布记录都是空的，像机器号</li>
          <li><strong>地区与内容不匹配</strong>：用 A 国环境发 B 国内容，容易被判异常</li>
          <li><strong>短期内操作过猛</strong>：新号立刻大量关注、发布、改资料</li>
          <li><strong>多账号同环境</strong>：一台设备登录多个新号，关联封禁</li>
        </ul>
        <p>这些不是「运气不好」，而是可解释的风控结果。<strong>稳定环境 + 渐进行为 + 真实内容</strong>，才是能活下来的组合。</p>

        <h2 id="how">从 0 到能带货的完整路径</h2>
        <ol>
          <li><strong>确定目标站点</strong>：先想清楚卖给谁，再决定开哪个地区的号</li>
          <li><strong>准备环境</strong>：稳定 IP、独立设备或指纹环境，一个号一套</li>
          <li><strong>拿到可用账号</strong>：自己注册或购买已养护的账号</li>
          <li><strong>补齐资料</strong>：头像、简介、几条正常内容，让它像个真人</li>
          <li><strong>开通橱窗</strong>：按站点要求提交，处理审核</li>
          <li><strong>持续做内容</strong>：这一步没有捷径，也是决定成败的一步</li>
        </ol>
        <p>第 3 步和第 6 步是我们能帮上忙的地方：<strong>前者省时间，后者决定天花板</strong>。</p>
"""

TIKTOK_FAQ = [
    (
        "TikTok 橱窗号需要多少粉丝？",
        "各站点要求不同，部分站点已放宽或取消粉丝数门槛，但仍需满足年龄、地区与账号状态等条件。具体以当期平台规则为准。",
    ),
    (
        "0 粉挂车能卖出去货吗？",
        "可以挂上，但没有粉丝就没有内容曝光，成交要靠后续做内容和投流。橱窗解决成交环节，不解决流量。",
    ),
    (
        "自己注册的账号为什么容易被封？",
        "常见原因是注册环境不稳定、资料不完整、地区与内容不匹配、新号操作过猛、多账号共用同一环境。",
    ),
    (
        "买现成的橱窗号值得吗？",
        "适合想跳过养号和审核等待的人，但需要确认账号的交付状态与售后补发政策。买号不解决内容问题。",
    ),
]


def main():
    write(
        "fb-account-types",
        "FB 账号类型完全指南：白号、三解号、大小黑都是什么 | " + YE,
        "Facebook 账号的 11 种常见分类、养号原理、想投广告该买哪种、哪些说法是坑。写给正在出海的中小卖家。",
        "FB 账号类型完全指南：白号、三解号、大小黑都是什么",
        "Facebook",
        "买号前先搞清楚这些词到底指什么。选错类型，90% 的预算会浪费在不能用的账号上。",
        FB_TYPES_BODY,
        faq=FB_TYPES_FAQ,
        related=[
            ("bm-guide", "BM 开户与广告账户类型：个人户、企业户、二不限怎么选"),
            ("tiktok-shop-guide", "TikTok 橱窗号怎么开：各国门槛与常见坑"),
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
        ]
    )

    print("wiki 页面生成完成：3 篇文章 + 1 个索引页")
    return 0


if __name__ == "__main__":
    sys.exit(main())
