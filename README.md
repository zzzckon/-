# 玄澜跨境官网

线上地址：<https://xuanlanch.dpdns.org/>　托管：Vercel　形态：纯静态单页

## 目录结构

```
index.html              首页（唯一需要频繁编辑的文件）
privacy.html            隐私政策
terms.html              服务条款
robots.txt              爬虫规则
sitemap.xml             站点地图
tailwind.config.js      Tailwind 配置（主题色、字体、动画）
src/input.css           Tailwind 源文件
assets/css/site.css     Tailwind 构建产物（勿手改）
assets/img/             站内图片（分享封面、文章配图、USDT 二维码）
assets/icons/           Lucide 图标源文件（图标已内联进 HTML，仅作留档）
scripts/gen_images.py   重新生成分享封面图
scripts/inline_icons.py 把 Lucide 图标转成内联 SVG（一次性脚本）
scripts/verify.py       静态校验：结构、资源、锚点、JSON-LD
baseline/               改造前的线上快照，用于对比回滚
```

## 改完页面后必做两件事

```powershell
# 1) HTML 里新增/修改了 Tailwind class 时，重新构建 CSS
node node_modules\tailwindcss\lib\cli.js -c tailwind.config.js -i src/input.css -o assets/css/site.css --minify

# 2) 跑静态校验（必须输出 PASSED）
python scripts\verify.py
```

> 本机没有全局 python/node，用的是 DSH 自带运行时：
> `C:\Users\xx\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\{python\python.exe,node\bin\node.exe}`

## 线上体检（每周跑一次）

`powershell
python scripts\audit_live.py
`

直接检查 https://xuanlanch.dpdns.org 的首页、og 分享图、robots、sitemap、
全部站内资源、第三方依赖、传输体积与缓存头。全部通过会输出 PASS，退出码 0。

## 本地预览

```powershell
<python.exe> -m http.server 8099 --bind 127.0.0.1
# 浏览器打开 http://127.0.0.1:8099/
```

## 部署

Vercel 若已连接本仓库的 `main` 分支：推上去即自动上线，约 30 秒。
未连接时改用 `vercel --prod`（需 Vercel token）。

## 已知待办

- [ ] `index.html` 里「最新洞察」的「查看公众号」链接已移除，拿到公众号主页地址后补回
- [ ] `privacy.html` / `terms.html` 顶部的经营主体全称、注册地待补充
- [ ] 微信二维码（如需）加入「联系我们」区域
- [ ] 接入访问统计与转化事件埋点
