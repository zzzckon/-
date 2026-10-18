"""新增长文：Shopify 选品、广告拒登处理、转化率优化。

每篇都带图与 FAQ，面向真实搜索意图。
"""

from wiki_content import fig

SHOPIFY_BODY = """
        <div class="toc">
          <div class="t">本文目录</div>
          <ol>
            <li><a href="#what">独立站和平台店的本质区别</a></li>
            <li><a href="#pick">选品：先排除，再挑选</a></li>
            <li><a href="#validate">用最小成本验证一个品</a></li>
            <li><a href="#page">详情页必须有的 6 个模块</a></li>
            <li><a href="#cost">一个独立站的真实成本</a></li>
            <li><a href="#mistake">新手最常犯的 4 个错</a></li>
          </ol>
        </div>

        <h2 id="what">独立站和平台店的本质区别</h2>
        <p>平台店买的是「现成流量」，独立站买的是「自己的资产」。这个区别决定了后面的所有动作。</p>
        <table>
          <thead><tr><th>维度</th><th>平台店</th><th>独立站</th></tr></thead>
          <tbody>
            <tr><td>流量来源</td><td>平台分配 + 站内搜索</td><td>自己买（广告）或自己做（内容）</td></tr>
            <tr><td>客户归属</td><td>归平台</td><td>归你，可复用、可再营销</td></tr>
            <tr><td>前期成本</td><td>低</td><td>中（建站 + 广告预算）</td></tr>
            <tr><td>起量速度</td><td>有现成流量，快</td><td>慢，要跑通投放模型</td></tr>
            <tr><td>风险</td><td>规则变动、封店</td><td>广告账户、支付通道</td></tr>
          </tbody>
        </table>
        <p>一个常见的错误是：<strong>把独立站当成「更高级的店铺」</strong>去开，结果发现没流量。独立站本质是一台需要燃料的机器，燃料就是广告费或内容。</p>

        <h2 id="pick">选品：先排除，再挑选</h2>
        <p>新手选品最大的问题不是选错，而是在明显不该做的品类上浪费时间。先排除这五类：</p>
        <table>
          <thead><tr><th>要排除的品类</th><th>原因</th></tr></thead>
          <tbody>
            <tr><td>大件重货</td><td>物流成本吃掉利润，退换货更贵</td></tr>
            <tr><td>强售后品类（电子、精密）</td><td>退货率和纠纷率高</td></tr>
            <tr><td>侵权风险品（IP 周边）</td><td>广告被拒、账户被封</td></tr>
            <tr><td>强监管品类（保健、医疗宣称）</td><td>合规成本极高</td></tr>
            <tr><td>纯比价标品（手机壳、数据线）</td><td>价格战，广告跑不出正 ROI</td></tr>
          </tbody>
        </table>
        <p>排除之后，按这三个特征筛选：</p>
        <figure class="fig"><img src="/assets/img/wiki/shopify-funnel.png" width="1200" height="700" loading="lazy" decoding="async" alt="选品排除法与三个筛选特征"><figcaption>先排除五类高风险的品类，再用三个特征筛选；验证顺序是测素材 → 看加购 → 再备货</figcaption></figure>
        <ul>
          <li><strong>视觉可展示</strong>：能在 3 秒内让人看懂效果（解压、对比、前后变化）</li>
          <li><strong>有溢价空间</strong>：毛利率至少 60%，才养得起广告</li>
          <li><strong>复购或连带</strong>：能带来二次购买或组合销售</li>
        </ul>

        <h2 id="validate">用最小成本验证一个品</h2>
        <p>不要一上来就备货。标准做法是<strong>先投广告，再决定要不要压库存</strong>：</p>
        <ol>
          <li>用 3-5 条不同角度的素材，每条小预算测试</li>
          <li>预算是「能买够统计样本」的钱，而不是「买曝光」的钱</li>
          <li>看 CTR 和加购率，而不是只看 ROI（样本太小时 ROI 无意义）</li>
          <li>加购率过关再备货，否则换素材或换品</li>
        </ol>
        <div class="callout">
          <p>判断标准：<strong>如果连加购都很少，问题在产品和页面；如果加购多但不成交，问题在价格和信任。</strong>这两个问题要用不同方法解决。</p>
        </div>

        <h2 id="page">详情页必须有的 6 个模块</h2>
        <ol>
          <li><strong>首屏价值主张</strong>：一句话说清是什么、解决什么、多少钱</li>
          <li><strong>产品演示</strong>：图或视频，展示使用场景而不只是产品白底图</li>
          <li><strong>信任元素</strong>：支付安全、退货政策、真实评价</li>
          <li><strong>规格与物流</strong>：尺寸、材质、发货时效（海外买家极其在意）</li>
          <li><strong>FAQ</strong>：把最常见的 5 个疑虑直接回答掉</li>
          <li><strong>政策页</strong>：隐私政策、退换货条款（支付渠道与广告平台都会审）</li>
        </ol>
        <p>第 6 条最容易被忽略，但它直接影响两件事：<strong>支付通道审核通过率</strong>和<strong>广告账户的落地页合规评分</strong>。</p>

        <h2 id="cost">一个独立站的真实成本</h2>
        <table>
          <thead><tr><th>项目</th><th>说明</th></tr></thead>
          <tbody>
            <tr><td>建站</td><td>主题、支付对接、数据埋点，一次性</td></tr>
            <tr><td>域名与订阅</td><td>按年 / 按月固定支出</td></tr>
            <tr><td>广告测试</td><td>验证阶段的主要成本，最容易低估</td></tr>
            <tr><td>支付手续费</td><td>按交易额比例</td></tr>
            <tr><td>素材制作</td><td>持续投入，不是一次性</td></tr>
          </tbody>
        </table>
        <p>很多人只算了建站费用，忽略了<strong>测试预算才是大头</strong>。合理的预期是：建站成本的 3-10 倍会花在验证和放大上。</p>

        <h2 id="mistake">新手最常犯的 4 个错</h2>
        <ul>
          <li><strong>先备货再测</strong>：库存压死现金流，还没验证就押注</li>
          <li><strong>页面只放美图</strong>：没有价值主张、没有 FAQ、没有政策页</li>
          <li><strong>一个品只测两天就放弃</strong>：数据量不够，结论不可信</li>
          <li><strong>不装数据追踪</strong>：不知道转化发生在哪一步，优化全靠猜</li>
        </ul>
        <p>这四条里，<strong>数据追踪</strong>是最值得优先补齐的——没有它，后面所有优化都没有依据。</p>
"""

SHOPIFY_FAQ = [
    (
        "独立站一定要用 Shopify 吗？",
        "不一定，但 Shopify 在支付、主题、应用生态上最成熟，适合快速上线。其他方案在定制性和成本上各有取舍。",
    ),
    (
        "建站要多久？",
        "标准配置（主题定制 + 支付对接 + 数据埋点 + 基础 SEO）通常 7-10 个工作日，取决于页面数量和支付通道审核时间。",
    ),
    (
        "需要准备什么资质？",
        "主要是收款主体与支付通道（PayPal / Stripe）。企业主体需要的资质更完整，个人主体可以选的通道相对少一些。",
    ),
    (
        "独立站没有流量怎么办？",
        "独立站的流量只能自己解决：广告投放或内容运营。商品页再好，没有流量也不会出单。",
    ),
]


# ================================================================= 拒登

REJECT_BODY = """
        <div class="toc">
          <div class="t">本文目录</div>
          <ol>
            <li><a href="#diff">拒登和封号不是一回事</a></li>
            <li><a href="#locate">先定位问题在哪一层</a></li>
            <li><a href="#common">8 种高频拒登原因</a></li>
            <li><a href="#appeal">申诉怎么写才有用</a></li>
            <li><a href="#prevent">预防比申诉更省钱</a></li>
          </ol>
        </div>

        <h2 id="diff">拒登和封号不是一回事</h2>
        <p>新手常把两者混为一谈，但处理方式完全不同：</p>
        <table>
          <thead><tr><th>现象</th><th>性质</th><th>影响范围</th><th>处理方式</th></tr></thead>
          <tbody>
            <tr><td>广告被拒登</td><td>单条素材不合规</td><td>这一条广告</td><td>改素材重提，账户不受影响</td></tr>
            <tr><td>账户被限制</td><td>账户层面风险</td><td>该账户所有广告</td><td>申诉或换户</td></tr>
            <tr><td>BM 被限制</td><td>组织层面问题</td><td>名下所有资产</td><td>走 BM 申诉，周期较长</td></tr>
          </tbody>
        </table>
        <figure class="fig"><img src="/assets/img/wiki/reject-layers.png" width="1200" height="660" loading="lazy" decoding="async" alt="拒登、账户受限、BM 受限三层对比"><figcaption>三层问题的影响范围和处理方式完全不同，先定位再动手</figcaption></figure>
        <p><strong>先分清是哪一层</strong>，否则会用错力：改了半天素材，其实是账户问题；或者急着换户，其实只是文案里有个绝对化用语。</p>

        <h2 id="locate">先定位问题在哪一层</h2>
        <p>一个简单有效的诊断方法：</p>
        <ol>
          <li>新建一条<strong>肯定合规</strong>的广告（纯产品图 + 中性文案）</li>
          <li>如果能正常通过 → 问题在原素材，属于<strong>内容层</strong></li>
          <li>如果同样被拒 → 问题在账户或落地页，属于<strong>账户层</strong></li>
        </ol>
        <p>这个动作花不到十分钟，但能省掉大量盲目修改。</p>

        <h2 id="common">8 种高频拒登原因</h2>
        <table>
          <thead><tr><th>原因</th><th>典型表现</th><th>怎么改</th></tr></thead>
          <tbody>
            <tr><td>绝对化用语</td><td>「最好」「第一」「保证效果」</td><td>改成具体、可验证的描述</td></tr>
            <tr><td>夸大收益</td><td>承诺收入、承诺减肥效果</td><td>删除效果承诺，只描述产品</td></tr>
            <tr><td>成人 / 敏感暗示</td><td>暴露度过高的图片</td><td>换素材，或调整展示方式</td></tr>
            <tr><td>前后对比图</td><td>减肥、护肤的前后对比</td><td>多数平台禁止，直接去掉</td></tr>
            <tr><td>落地页与广告不一致</td><td>广告说 A，页面卖 B</td><td>确保主推商品完全一致</td></tr>
            <tr><td>落地页缺少信息</td><td>无联系方式、无隐私政策</td><td>补齐页脚与政策页</td></tr>
            <tr><td>仿冒 / 侵权</td><td>带知名品牌 logo 或外观</td><td>换原创素材</td></tr>
            <tr><td>支付方式异常</td><td>频繁拒付记录</td><td>更换支付方式，联系平台</td></tr>
          </tbody>
        </table>

        <h2 id="appeal">申诉怎么写才有用</h2>
        <p>申诉成功率低，很大一部分原因是<strong>申诉内容没有针对性</strong>。有效的申诉应该包含：</p>
        <ul>
          <li><strong>具体说明</strong>你理解的问题是什么（而不是泛泛说「请联系我」）</li>
          <li><strong>已经做的修改</strong>：改了哪条文案、换了哪张图</li>
          <li><strong>业务说明</strong>：卖什么、卖给谁、合规依据</li>
          <li><strong>联系方式</strong>：真实可回应的邮箱</li>
        </ul>
        <div class="callout">
          <p>反复提交相同内容的申诉，通常只会延后处理。<strong>每次申诉都要带上「这次改了什么」</strong>。</p>
        </div>

        <h2 id="prevent">预防比申诉更省钱</h2>
        <ul>
          <li><strong>素材过检清单</strong>：发布前先自查绝对化用语、对比图、敏感品类</li>
          <li><strong>落地页合规</strong>：联系方式、隐私政策、退换货条款齐全</li>
          <li><strong>多账户备用</strong>：主力账户被限时能立刻切换，不至于断流</li>
          <li><strong>记录拒登原因</strong>：形成自己的红线清单，越跑越少踩</li>
        </ul>
        <p>投放做久了会发现：<strong>稳定投放的人不是没遇到拒登，而是有一套快速纠错的流程</strong>。</p>
"""

REJECT_FAQ = [
    (
        "广告被拒登会扣钱吗？",
        "被拒登的广告不会产生消耗。但如果账户整体被限制，账户余额和未结算部分可能受影响，需要走申诉。",
    ),
    (
        "同一个素材换个账户能过吗？",
        "如果是内容层问题，换账户通常还是会被拒。先按上文方法定位问题在哪一层，再决定换素材还是换户。",
    ),
    (
        "拒登多少条会导致账户被限？",
        "平台不公布具体阈值，但拒登率过高会显著增加账户风险。建议将拒登率控制在较低水平，并持续优化素材。",
    ),
    (
        "落地页需要哪些必备页面？",
        "至少包含隐私政策、退换货或服务条款，以及可用的联系方式。这三项是广告与支付审核的常见检查点。",
    ),
]
