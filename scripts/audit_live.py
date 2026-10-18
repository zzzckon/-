"""线上体检：对 https://xuanlanch.dpdns.org 做一次可复核的健康检查。

用法：python scripts/audit_live.py
退出码 0 = 全部通过；1 = 有项目失败（会明确列出）。
纯标准库，不需要安装依赖，也不依赖这台机器上的浏览器。
"""

import gzip
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

# Vercel 会压缩 HTML、去掉属性引号，所以解析一律用「引号可选」的正则。
ATTR = r'''["']?([^\s"'>]+)["']?'''

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass

BASE = "https://xuanlanch.dpdns.org"
TIMEOUT = 20
UA = "xuanlanch-audit/1.0 (+maintenance check)"
ALLOWED_LINK_HOSTS = {
    "t.me",
    "mp.weixin.qq.com",
    "www.w3.org",
    "schema.org",
    "xuanlanch.dpdns.org",
}

results = []


def record(ok, name, detail=""):
    results.append((ok, name, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def fetch(url, want_body=True, accept_encoding=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if accept_encoding:
        req.add_header("Accept-Encoding", "gzip")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
        raw = resp.read() if want_body else b""
        headers = dict(resp.headers)
        return resp.status, headers, raw


def decode(raw, headers):
    if headers.get("Content-Encoding") == "gzip":
        try:
            return gzip.decompress(raw)
        except OSError:
            return raw
    return raw


def main() -> int:
    print(f"检查目标: {BASE}\n")

    # 1. 首页
    print("首页")
    status, headers, raw = fetch(BASE + "/")
    record(status == 200, "首页返回 200", f"HTTP {status}")
    html = decode(raw, headers).decode("utf-8", "replace")
    record(len(html) > 20000, "页面内容完整", f"{len(html):,} 字符")

    # 2. 关键头部标签
    print("\nSEO 与分享")
    record('property="og:image"' in html, "存在 og:image")
    record('rel="canonical"' in html, "存在 canonical")
    record(
        'application/ld+json' in html,
        "存在 JSON-LD 结构化数据",
    )
    og = re.search(r'property="og:image"\s+content="([^"]+)"', html)
    if og:
        og_url = og.group(1)
        record(og_url.startswith("https://"), "og:image 是绝对地址", og_url)
        try:
            st, hd, ograw = fetch(og_url)
            ok_img = st == 200 and hd.get("Content-Type", "").startswith("image/")
            record(ok_img, "og:image 可访问且是图片", f"HTTP {st}, {len(ograw) // 1024}KB")
            if ok_img and len(ograw) < 300_000:
                record(True, "og:image 体积合理", f"{len(ograw) // 1024}KB")
        except urllib.error.URLError as exc:
            record(False, "og:image 可访问", str(exc))
    else:
        record(False, "能解析出 og:image")

    # 3. robots / sitemap
    print("\n抓取入口")
    try:
        st, _, rraw = fetch(BASE + "/robots.txt")
        robots = rraw.decode("utf-8", "replace")
        record(st == 200 and "Sitemap:" in robots, "robots.txt 正常且声明 sitemap")
    except urllib.error.URLError as exc:
        record(False, "robots.txt 可访问", str(exc))

    try:
        st, shdrs, sraw = fetch(BASE + "/sitemap.xml")
        sitemap = decode(sraw, shdrs).decode("utf-8", "replace")
        locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
        record(st == 200 and bool(locs), "sitemap.xml 正常", f"{len(locs)} 个 URL")
        for loc in locs:
            try:
                st2, _, _ = fetch(loc, want_body=False)
                record(st2 == 200, f"  sitemap 内地址可访问", loc)
            except urllib.error.URLError as exc:
                record(False, "  sitemap 内地址可访问", f"{loc} ({exc})")
    except urllib.error.URLError as exc:
        record(False, "sitemap.xml 可访问", str(exc))

    # 4. 站内资源
    print("\n资源完整性")
    refs = set()
    for m in re.finditer(r'(?:src|href)=\s*["\']?(/[^\s"\'>]+)', html):
        path = m.group(1).split("?")[0].split("#")[0]
        if not path.startswith("/assets/"):
            continue
        refs.add(path)
    bad = []
    for path in sorted(refs):
        try:
            st, hd, _ = fetch(BASE + path, want_body=False)
            if st != 200:
                bad.append(f"{path} -> {st}")
        except urllib.error.URLError as exc:
            bad.append(f"{path} -> {exc}")
    record(not bad, f"站内资源全部可访问（{len(refs)} 个）", "; ".join(bad))

    # 5. 外部依赖残留
    print("\n第三方依赖")
    hosts = {urlparse(m.group(1)).netloc for m in re.finditer(r'(?:src|href)=\s*["\']?(https?://[^\s"\'>]+)', html)}
    unknown = sorted(h for h in hosts if h and h not in ALLOWED_LINK_HOSTS)
    record(not unknown, "没有意料之外的第三方域名", ", ".join(unknown) if unknown else "仅聚合站内资源")

    # 6. 传输体积
    print("\n性能")
    gz = len(construct_gzip(html))
    record(gz < 20_000, "首页 HTML（gzip）小于 20KB", f"{gz / 1024:.1f}KB")
    css = re.search(r'href=\s*["\']?(/assets/css/[^\s"\'>]+)', html)
    if css:
        try:
            stc, hc, craw = fetch(BASE + css.group(1))
            gzc = len(construct_gzip(decode(craw, hc).decode("utf-8", "replace")))
            record(gzc < 15_000, "CSS（gzip）小于 15KB", f"{gzc / 1024:.1f}KB")
            record(
                "max-age=86400" in hc.get("Cache-Control", ""),
                "静态资源有长缓存",
                hc.get("Cache-Control", ""),
            )
        except urllib.error.URLError as exc:
            record(False, "CSS 可访问", str(exc))

    # 7. 商品目录（静态化可抓取检查）
    print("\n商品目录")
    try:
        stp, chdrs, praw = fetch(BASE + "/products/")
        prod_html = decode(praw, chdrs).decode("utf-8", "replace")
        cards = len(re.findall(r'class=\"?card\"?', prod_html))
        record(stp == 200 and cards > 0, "商品目录可访问", f"{cards} 个商品卡片")
    except urllib.error.URLError as exc:
        record(False, "商品目录可访问", str(exc))
    try:
        stpr, phdrs, prraw = fetch(BASE + "/product/fb-enterprise-eco-1p1/")
        pr = decode(prraw, phdrs).decode("utf-8", "replace")
        body = re.sub(r"<script.*?</script>", "", pr, flags=re.S)
        body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
        body = re.sub(r"<[^>]+>", " ", body)
        body = re.sub(r"\s+", " ", body).strip()
        record(
            stpr == 200 and len(body) > 300,
            "商品详情页无 JS 可见正文 > 300 字符",
            f"{len(body)} 字符",
        )
        record(re.search(r'"@type"\s*:\s*"Product"', pr) is not None,
               "商品页含 Product 结构化数据")
    except urllib.error.URLError as exc:
        record(False, "商品详情页可访问", str(exc))

    # 8. 转化入口提示（t.me 在大陆通常不可达，只报告不判失败）
    print("\n转化入口")
    has_qq = "956878659" in html
    record(has_qq, "页面上有可复制的 QQ 号")
    record("copyText(" in html, "实现了复制交互")

    failed = [r for r in results if not r[0]]
    print("\n" + "=" * 52)
    if failed:
        print(f"体检结果：{len(failed)} 项异常 / 共 {len(results)} 项")
        for _, name, detail in failed:
            print(f"  - {name} {detail}")
        return 1
    print(f"体检结果：全部通过（{len(results)} 项）")
    return 0


def construct_gzip(text: str) -> bytes:
    return gzip.compress(text.encode("utf-8"), 9)


if __name__ == "__main__":
    sys.exit(main())
