"""把首页的「价目表卡片区」替换成「内容矩阵区」。

锚点用注释定位，避免依赖行号；重复执行是幂等的（已替换过就跳过）。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

START = "    <!-- Services Section -->"
END = "    <!-- Insights Section -->"

NEW_SECTION = '''    <!-- 内容矩阵：首页不摆价目表，价格统一在 /products/ -->
    <section id="services" class="py-32 px-6 max-w-[1400px] mx-auto">
        <div class="mb-16 reveal">
            <h2 class="text-4xl md:text-6xl font-semibold tracking-tight mb-4">我们做什么。</h2>
            <p class="text-xl text-gray-400 max-w-2xl">三条业务线：广告资产交付、独立站搭建、广告代投。
            具体型号与价格在商品页，先看下面的知识库了解怎么选。</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
            <a href="/category/facebook/" class="bento-card p-8 md:p-10 reveal group block">
                <svg class="w-11 h-11 text-blue-600 mb-6" viewBox="0 0 24 24" fill="currentColor" width="24" height="24" aria-hidden="true"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12z"/></svg>
                <h3 class="text-2xl font-semibold text-white mb-3 group-hover:text-blue-400 transition">广告资产交付</h3>
                <p class="text-gray-400 text-base leading-relaxed mb-6">Facebook 个人号、企业广告账户、公共主页与 BM 授权，覆盖冷启动到规模化投放。</p>
                <span class="text-blue-400 text-sm font-medium inline-flex items-center gap-1">看商品与价格 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></span>
            </a>

            <a href="/category/service/" class="bento-card p-8 md:p-10 reveal group block">
                <svg class="w-11 h-11 text-green-500 mb-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="24" height="24" aria-hidden="true"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
                <h3 class="text-2xl font-semibold text-white mb-3 group-hover:text-blue-400 transition">独立站搭建</h3>
                <p class="text-gray-400 text-base leading-relaxed mb-6">Shopify 主题定制、支付对接、GA4 埋点与基础 SEO，按可被搜索收录的标准交付。</p>
                <span class="text-blue-400 text-sm font-medium inline-flex items-center gap-1">看交付范围 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></span>
            </a>

            <a href="/category/tiktok/" class="bento-card p-8 md:p-10 reveal group block">
                <svg class="w-11 h-11 text-pink-500 mb-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="24" height="24" aria-hidden="true"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>
                <h3 class="text-2xl font-semibold text-white mb-3 group-hover:text-blue-400 transition">TikTok 与直播</h3>
                <p class="text-gray-400 text-base leading-relaxed mb-6">橱窗带货开通、海外账号资源、直播低延迟节点，覆盖东南亚主要站点。</p>
                <span class="text-blue-400 text-sm font-medium inline-flex items-center gap-1">看商品与价格 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></span>
            </a>
        </div>

        <div class="flex items-baseline justify-between mb-10 reveal">
            <h2 class="text-3xl md:text-4xl font-semibold tracking-tight">出海知识库</h2>
            <a href="/wiki/" class="text-blue-400 hover:text-blue-300 text-sm font-medium inline-flex items-center gap-1 transition">全部文章 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></a>
        </div>

        <div class="space-y-5">
            <a href="/wiki/fb-account-types/" class="bento-card group flex flex-col md:flex-row gap-6 p-6 md:p-8 items-start md:items-center reveal">
                <div class="flex-1">
                    <div class="text-xs text-blue-400 font-semibold uppercase tracking-wide mb-2">Facebook</div>
                    <h3 class="text-xl md:text-2xl font-semibold text-white mb-2 group-hover:text-blue-400 transition">FB 账号类型完全指南：白号、三解号、大小黑都是什么</h3>
                    <p class="text-gray-500 text-sm leading-relaxed">11 种账号分类、养号周期、哪些能直接投广告、哪些一登就死。看完你就知道该买哪种。</p>
                </div>
                <span class="text-blue-400 text-sm font-medium shrink-0 inline-flex items-center gap-1">阅读 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></span>
            </a>

            <a href="/wiki/bm-guide/" class="bento-card group flex flex-col md:flex-row gap-6 p-6 md:p-8 items-start md:items-center reveal">
                <div class="flex-1">
                    <div class="text-xs text-purple-400 font-semibold uppercase tracking-wide mb-2">Meta</div>
                    <h3 class="text-xl md:text-2xl font-semibold text-white mb-2 group-hover:text-blue-400 transition">BM 开户与广告账户类型：个人户、企业户、二不限怎么选</h3>
                    <p class="text-gray-500 text-sm leading-relaxed">BM 是什么、三种账户的限额与稳定性差异、什么阶段该换企业户，一次讲清。</p>
                </div>
                <span class="text-blue-400 text-sm font-medium shrink-0 inline-flex items-center gap-1">阅读 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></span>
            </a>

            <a href="/wiki/tiktok-shop-guide/" class="bento-card group flex flex-col md:flex-row gap-6 p-6 md:p-8 items-start md:items-center reveal">
                <div class="flex-1">
                    <div class="text-xs text-pink-400 font-semibold uppercase tracking-wide mb-2">TikTok</div>
                    <h3 class="text-xl md:text-2xl font-semibold text-white mb-2 group-hover:text-blue-400 transition">TikTok 橱窗号怎么开：各国门槛、所需资料与常见坑</h3>
                    <p class="text-gray-500 text-sm leading-relaxed">东南亚六国的开通条件、0 粉挂车的真实限制、为什么自己开的号经常掉。</p>
                </div>
                <span class="text-blue-400 text-sm font-medium shrink-0 inline-flex items-center gap-1">阅读 <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6" /></svg></span>
            </a>
        </div>
    </section>

'''


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    if "内容矩阵：首页不摆价目表" in html:
        print("已经替换过，跳过")
        return 0
    i = html.index(START)
    j = html.index(END, i)
    html = html[:i] + NEW_SECTION + html[j:]
    INDEX.write_text(html, encoding="utf-8")
    print("首页服务卡片区已替换为内容矩阵区")
    return 0


if __name__ == "__main__":
    sys.exit(main())
