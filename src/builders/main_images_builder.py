"""
淘宝精品详情页切片生成器 (完全继承主图的高级视觉语言：钛金仪表盘、真实图标、饱满质感)
尺寸: 800x1000 像素，与主图 100% 同一风格美学
"""

import os
import subprocess

DETAILS_DIR = r"c:\Users\a1325\Desktop\wzry\taobao\details"
TEMP_HTML_DIR = r"c:\Users\a1325\Desktop\wzry\taobao\temp_details"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

COMMON_STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    width: 800px;
    height: 1000px;
    background: radial-gradient(130% 120% at 50% 0%, #fbfcfd 0%, #f0f3f8 45%, #e2e7f0 100%);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #1d1d1f;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 60px 45px 45px 45px;
    position: relative;
    overflow: hidden;
}
.ambient-glow {
    position: absolute; top: -100px; left: 50%; transform: translateX(-50%);
    width: 750px; height: 380px;
    background: radial-gradient(circle, rgba(0, 113, 227, 0.12) 0%, rgba(0, 113, 227, 0) 70%);
    pointer-events: none; z-index: 0;
}
.header-area { text-align: center; z-index: 2; }
.season-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(16px);
    color: #0071e3; font-size: 16px; font-weight: 700;
    padding: 6px 18px; border-radius: 20px; letter-spacing: 0.04em;
    border: 1px solid rgba(0, 113, 227, 0.22);
    box-shadow: 0 4px 14px rgba(0, 113, 227, 0.08); margin-bottom: 12px;
}
.season-pill .dot { width: 6px; height: 6px; background: #0071e3; border-radius: 50%; box-shadow: 0 0 6px #0071e3; }
.main-title {
    font-size: 58px; font-weight: 850; letter-spacing: -0.03em; line-height: 1.08;
    background: linear-gradient(180deg, #0a0a0c 0%, #2c2c30 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;
}
.subtitle {
    font-size: 22px; color: #48484a; font-weight: 500;
    display: flex; align-items: center; justify-content: center; gap: 10px;
}
.subtitle-badge {
    background: #1c1c1e; color: #ffffff; font-size: 15px; font-weight: 700;
    padding: 3px 12px; border-radius: 6px;
}
.hero-stage { width: 100%; display: flex; justify-content: center; align-items: center; position: relative; z-index: 2; }
.pro-console {
    width: 710px;
    background: linear-gradient(165deg, #1f2024 0%, #111215 100%);
    border-radius: 28px; padding: 18px;
    box-shadow: 0 35px 80px -10px rgba(10, 25, 60, 0.35),
        inset 0 1px 1px rgba(255, 255, 255, 0.3), inset 0 0 0 1px rgba(255, 255, 255, 0.08);
    position: relative;
}
.console-body {
    background: radial-gradient(100% 120% at 50% 0%, #252830 0%, #17181c 100%);
    border-radius: 20px; padding: 22px 24px;
    display: flex; flex-direction: column; gap: 16px;
    border: 1px solid rgba(255, 255, 255, 0.07);
}
.floating-gift {
    position: absolute; bottom: -18px; right: 32px;
    background: linear-gradient(135deg, #0077ed 0%, #0056b3 100%);
    color: #ffffff; font-size: 17px; font-weight: 700;
    padding: 10px 24px; border-radius: 30px;
    box-shadow: 0 10px 25px rgba(0, 113, 227, 0.45);
    display: flex; align-items: center; gap: 8px; border: 1px solid rgba(255, 255, 255, 0.2);
}
.footer-note {
    font-size: 17px; color: #515154; font-weight: 600;
    display: flex; gap: 24px; align-items: center; z-index: 2;
    background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px);
    padding: 10px 26px; border-radius: 24px; border: 1px solid rgba(0,0,0,0.05);
}
.footer-note .dot-sep { color: #c7c7cc; font-size: 16px; }
"""

SLICES = [
    # 01_详情页：开篇 · 旗舰推演面板
    (
        "01_详情页_顶部公告与版本.png",
        "2026 S 赛季 · 官方正式服全量数据清洗",
        "王者全英雄战术手册",
        '<span class="subtitle-badge">PDF 电子版</span> <span>132位英雄克制谱系 ｜ 铭文出装大典</span>',
        """
        <div class="console-body">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:14px;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="position:relative; width:64px; height:64px; border-radius:18px; padding:2px; background:linear-gradient(135deg, #f59e0b, #b45309); box-shadow:0 0 16px rgba(245,158,11,0.35);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg" style="width:100%; height:100%; border-radius:16px; object-fit:cover;">
                        <div style="position:absolute; bottom:-4px; right:-4px; background:#111; border:1px solid #f59e0b; color:#f59e0b; font-size:11px; font-weight:800; padding:1px 5px; border-radius:6px;">15</div>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:26px; font-weight:800; color:#fff;">廉颇</span>
                            <span style="background:rgba(255,255,255,0.12); color:#e5e5ea; font-size:13px; font-weight:700; padding:2px 8px; border-radius:8px;">对抗路 / 坦克</span>
                        </div>
                        <div style="font-size:14px; color:#98989f; margin-top:3px;">正义爆轰 · 满级六神装与铭文最佳协同推演</div>
                    </div>
                </div>
                <div style="background:rgba(0,113,227,0.15); color:#2997ff; font-size:15px; font-weight:700; padding:6px 16px; border-radius:20px; border:1px solid rgba(41,151,255,0.35);">
                    • 实时算分引擎
                </div>
            </div>

            <!-- 六神装 -->
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:13px; font-weight:700; color:#86868b; text-transform:uppercase;">六神装备槽位 (装备被动互斥与协同检测)</span>
                    <span style="color:#30d158; font-size:13px; font-weight:700;">✔ 装备被动无冲突</span>
                </div>
                <div style="display:flex; justify-content:space-between; gap:10px;">
                    <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:10px 4px; display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1133.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #eab308; box-shadow:0 0 10px rgba(234,179,8,0.3);">
                        <span style="font-size:12px; font-weight:700; color:#fff;">暗影战斧</span>
                    </div>
                    <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:10px 4px; display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1332.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #eab308; box-shadow:0 0 10px rgba(234,179,8,0.3);">
                        <span style="font-size:12px; font-weight:700; color:#fff;">不祥征兆</span>
                    </div>
                    <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:10px 4px; display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1331.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #eab308; box-shadow:0 0 10px rgba(234,179,8,0.3);">
                        <span style="font-size:12px; font-weight:700; color:#fff;">暴烈之甲</span>
                    </div>
                    <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:10px 4px; display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1334.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #eab308; box-shadow:0 0 10px rgba(234,179,8,0.3);">
                        <span style="font-size:12px; font-weight:700; color:#fff;">魔女斗篷</span>
                    </div>
                    <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:10px 4px; display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1126.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #eab308; box-shadow:0 0 10px rgba(234,179,8,0.3);">
                        <span style="font-size:12px; font-weight:700; color:#fff;">碎星锤</span>
                    </div>
                    <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:10px 4px; display:flex; flex-direction:column; align-items:center; gap:6px;">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1337.png" style="width:48px; height:48px; border-radius:12px; border:1.5px solid #eab308; box-shadow:0 0 10px rgba(234,179,8,0.3);">
                        <span style="font-size:12px; font-weight:700; color:#fff;">贤者庇护</span>
                    </div>
                </div>
            </div>

            <!-- 三大数据 -->
            <div style="background:rgba(0,0,0,0.4); border-radius:16px; padding:16px 20px; display:flex; justify-content:space-around; align-items:center; border:1px solid rgba(255,255,255,0.08);">
                <div style="text-align:center;">
                    <div style="font-size:13px; color:#86868b; margin-bottom:4px;">最终最大生命</div>
                    <div style="font-size:36px; font-weight:850; color:#fff; line-height:1;">11,280</div>
                    <div style="width:80px; height:4px; background:rgba(255,255,255,0.12); border-radius:2px; margin:6px auto 0 auto;"><div style="width:85%; height:100%; background:#2997ff;"></div></div>
                </div>
                <div style="width:1px; height:45px; background:rgba(255,255,255,0.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:13px; color:#86868b; margin-bottom:4px;">物理抗性免伤率</div>
                    <div style="font-size:36px; font-weight:850; color:#2997ff; line-height:1; text-shadow:0 0 20px rgba(41,151,255,0.4);">64.2%</div>
                    <div style="width:80px; height:4px; background:rgba(255,255,255,0.12); border-radius:2px; margin:6px auto 0 auto;"><div style="width:64.2%; height:100%; background:#2997ff;"></div></div>
                </div>
                <div style="width:1px; height:45px; background:rgba(255,255,255,0.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:13px; color:#86868b; margin-bottom:4px;">机制协同诊断</div>
                    <div style="font-size:36px; font-weight:850; color:#30d158; line-height:1; text-shadow:0 0 20px rgba(48,209,88,0.4);">100分</div>
                    <div style="width:80px; height:4px; background:rgba(255,255,255,0.12); border-radius:2px; margin:6px auto 0 auto;"><div style="width:100%; height:100%; background:#30d158;"></div></div>
                </div>
            </div>
        </div>
        <div class="floating-gift">🎁 独家赠送 · 在线配装推演网页</div>
        """,
        "⚡ 拍下秒发网盘 • 📱 手机电脑秒开 • 🔄 赛季持续同步"
    ),

    # 02_详情页：克制案例全景
    (
        "02_详情页_对局痛点与破局.png",
        "132 位英雄全面覆盖 · 官方级数据",
        "132位英雄克制谱系",
        '<span class="subtitle-badge" style="background:#0071e3;">对位破解</span> <span>对位压制解法 ｜ 最佳搭档阵容 ｜ BP选人秒查</span>',
        """
        <div class="console-body">
            <div style="background:rgba(0,0,0,0.4); border-radius:16px; padding:16px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:58px; height:58px; border-radius:16px; overflow:hidden; border:2px solid #f59e0b; box-shadow:0 0 12px rgba(245,158,11,0.4);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/141/141.jpg" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#fff;">貂蝉</div>
                        <div style="font-size:13px; color:#86868b;">中路 / 法刺核心</div>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:3px;">
                    <span style="background:rgba(48,209,88,0.2); color:#30d158; border:1px solid rgba(48,209,88,0.4); font-size:13px; font-weight:800; padding:3px 12px; border-radius:10px;">绝对压制 ➔</span>
                    <span style="font-size:11px; color:#98989f;">真伤风筝无解</span>
                </div>
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:58px; height:58px; border-radius:16px; overflow:hidden; border:2px solid rgba(255,255,255,0.2);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#fff;">笨重前排 (如廉颇/吕布)</div>
                        <div style="font-size:12px; color:#86868b;">坦度被真实伤害熔断</div>
                    </div>
                </div>
            </div>

            <div style="background:rgba(0,0,0,0.4); border-radius:16px; padding:16px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:58px; height:58px; border-radius:16px; overflow:hidden; border:2px solid #ef4444; box-shadow:0 0 12px rgba(239,68,68,0.4);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/187/187.jpg" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#fff;">东皇太一 / 张良</div>
                        <div style="font-size:13px; color:#86868b;">压制型绝对强控</div>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:3px;">
                    <span style="background:rgba(48,209,88,0.2); color:#30d158; border:1px solid rgba(48,209,88,0.4); font-size:13px; font-weight:800; padding:3px 12px; border-radius:10px;">天克死穴 ➔</span>
                    <span style="font-size:11px; color:#98989f;">净化不可解除</span>
                </div>
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:58px; height:58px; border-radius:16px; overflow:hidden; border:2px solid rgba(255,255,255,0.2);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/146/146.jpg" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#fff;">多位移秀儿 (如露娜/阿离)</div>
                        <div style="font-size:12px; color:#86868b;">大招定身即刻阵亡</div>
                    </div>
                </div>
            </div>

            <div style="background:rgba(0,0,0,0.4); border-radius:16px; padding:16px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:58px; height:58px; border-radius:16px; overflow:hidden; border:2px solid #0071e3; box-shadow:0 0 12px rgba(0,113,227,0.4);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/193/193.jpg" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#fff;">铠 / 典韦</div>
                        <div style="font-size:13px; color:#86868b;">重装战士爆发</div>
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:3px;">
                    <span style="background:rgba(0,113,227,0.2); color:#2997ff; border:1px solid rgba(41,151,255,0.4); font-size:13px; font-weight:800; padding:3px 12px; border-radius:10px;">最佳搭档 ⚡</span>
                    <span style="font-size:11px; color:#2997ff;">群体增益/拉扯</span>
                </div>
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:58px; height:58px; border-radius:16px; overflow:hidden; border:2px solid #0071e3; box-shadow:0 0 12px rgba(0,113,227,0.4);">
                        <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/113/113.jpg" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:800; color:#fff;">庄周 / 孙膑</div>
                        <div style="font-size:12px; color:#86868b;">解控加速，团战无敌</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="floating-gift">📖 手机翻开直接查 · 排位选人破局</div>
        """,
        "⚡ 132位英雄全量收录 • 📱 手机秒开查对位 • 🔄 随版本持续更新"
    ),

    # 03_详情页：6本战术大典矩阵
    (
        "03_详情页_6本手册深度全景.png",
        "全量清洗 · 6 大核心战术维度全覆盖",
        "全套 6 本高清战术手册",
        '<span class="subtitle-badge">高清 PDF</span> <span>从底层机制到实战出装 ｜ 官方级全量数据清洗</span>',
        """
        <div class="console-body" style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
            <div style="background:rgba(41,151,255,0.08); border:1px solid rgba(41,151,255,0.3); border-radius:16px; padding:16px;">
                <div style="color:#2997ff; font-size:12px; font-weight:800;">01 · 数值全解</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin:2px 0;">技能与成长数值</div>
                <div style="font-size:12px; color:#9ca3af;">132位英雄被动机制、等级成长梯度、全量加成系数</div>
            </div>
            <div style="background:rgba(41,151,255,0.08); border:1px solid rgba(41,151,255,0.3); border-radius:16px; padding:16px;">
                <div style="color:#2997ff; font-size:12px; font-weight:800;">02 · 阵容克制</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin:2px 0;">战术克制与搭档</div>
                <div style="font-size:12px; color:#9ca3af;">对位压制破局策略、BP选人针对解法、最佳双排搭档</div>
            </div>
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:16px;">
                <div style="color:#2997ff; font-size:12px; font-weight:800;">03 · 分路神装</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin:2px 0;">五大分路实战出装</div>
                <div style="font-size:12px; color:#9ca3af;">对抗/中/野/射/辅标准六神装、顺逆风备选与变异方案</div>
            </div>
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:16px;">
                <div style="color:#2997ff; font-size:12px; font-weight:800;">04 · 装备图谱</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin:2px 0;">装备属性与合成树</div>
                <div style="font-size:12px; color:#9ca3af;">双向合成拓扑结构、被动冲突警示、合成曲线与性价比</div>
            </div>
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:16px;">
                <div style="color:#2997ff; font-size:12px; font-weight:800;">05 · 铭文搭配</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin:2px 0;">五级铭文流派全鉴</div>
                <div style="font-size:12px; color:#9ca3af;">百穿/88法穿/暴击移速卡阈值配置、全流派英雄装配</div>
            </div>
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:16px;">
                <div style="color:#2997ff; font-size:12px; font-weight:800;">06 · 底层算分</div>
                <div style="font-size:18px; font-weight:800; color:#fff; margin:2px 0;">峡谷战场底层机制</div>
                <div style="font-size:12px; color:#9ca3af;">双抗实际免伤公式、韧性穿透上限、野区经济经验刷新</div>
            </div>
        </div>
        <div class="floating-gift">📚 拍下整套 6 本一键打包提取</div>
        """,
        "⚡ 手机电脑秒开直读 • 📑 纯净排版无广告乱码 • 🤖 赠 AI 投喂原生包"
    ),

    # 04_详情页：沙盒推演三大硬核功能
    (
        "04_详情页_独家在线推演沙盒.png",
        "独家赠礼 · 网页免安装即用",
        "在线配装推演沙盒",
        '<span class="subtitle-badge" style="background:#0071e3;">随包附赠</span> <span>全铭文自由混搭 ｜ 装备动态算分 ｜ 永久云端同步</span>',
        """
        <div class="console-body">
            <div style="background:rgba(0,0,0,0.35); border-radius:16px; padding:16px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="font-size:26px;">💎</div>
                    <div>
                        <div style="font-size:19px; font-weight:800; color:#fff;">30 颗全量铭文自由混搭</div>
                        <div style="font-size:12.5px; color:#86868b; margin-top:2px;">支持 9异变+1纷争、7狩猎+3夺萃等极限卡攻速阈值方案</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/mingwen/1504.png" style="width:38px; height:38px; border-radius:10px; border:1px solid #eab308;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/mingwen/3514.png" style="width:38px; height:38px; border-radius:10px; border:1px solid #eab308;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/mingwen/2517.png" style="width:38px; height:38px; border-radius:10px; border:1px solid #eab308;">
                    <span style="background:rgba(41,151,255,0.15); color:#2997ff; font-size:14px; font-weight:800; padding:4px 12px; border-radius:14px; border:1px solid rgba(41,151,255,0.3);">百穿 +100</span>
                </div>
            </div>

            <div style="background:rgba(0,0,0,0.35); border-radius:16px; padding:16px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="font-size:26px;">⚔️</div>
                    <div>
                        <div style="font-size:19px; font-weight:800; color:#fff;">装备双向合成拓扑树</div>
                        <div style="font-size:12.5px; color:#86868b; margin-top:2px;">大件成装自动回溯前置小件，平滑过渡告别对局空档期</div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1126.png" style="width:38px; height:38px; border-radius:10px; border:1px solid #eab308;">
                    <span style="color:#86868b; font-weight:800;">+</span>
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1133.png" style="width:38px; height:38px; border-radius:10px; border:1px solid #eab308;">
                    <span style="background:rgba(41,151,255,0.15); color:#2997ff; font-size:14px; font-weight:800; padding:4px 12px; border-radius:14px; border:1px solid rgba(41,151,255,0.3);">平滑合成</span>
                </div>
            </div>

            <div style="background:rgba(0,0,0,0.35); border-radius:16px; padding:16px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="font-size:26px;">🛡️</div>
                    <div>
                        <div style="font-size:19px; font-weight:800; color:#fff;">双抗实际免伤率结算引擎</div>
                        <div style="font-size:12.5px; color:#86868b; margin-top:2px;">根据防御力衰减公式动态计算等效生命值，智能诊断被动冲突</div>
                    </div>
                </div>
                <span style="background:rgba(48,209,88,0.15); color:#30d158; border:1px solid rgba(48,209,88,0.4); font-size:15px; font-weight:800; padding:6px 16px; border-radius:16px;">
                    协同 100 分
                </span>
            </div>
        </div>
        <div class="floating-gift">🌐 拍下即送专属网页链接 · 手机电脑随时开</div>
        """,
        "⚡ 免下载 APP • 🌐 浏览器点开即用 • 🔄 游戏平衡云端同步"
    ),

    # 05_详情页：秒级自动发货全平台畅读
    (
        "05_详情页_AI投喂电竞教练.png",
        "24 小时无人值守 · 拍下旺旺秒级发货",
        "秒级发货 · 全端畅读",
        '<span class="subtitle-badge" style="background:#34c759;">自动发卡</span> <span>手机平板随开随查 ｜ 附赠保姆级上手指南</span>',
        """
        <div class="console-body">
            <div style="background:rgba(0,0,0,0.35); border-radius:16px; padding:18px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="font-size:28px;">📱</div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#fff;">手机 / 平板端 · 高清战术手册</div>
                        <div style="font-size:13px; color:#86868b; margin-top:2px;">全彩矢量排版，对局排位随手翻阅，无广告不卡壳</div>
                    </div>
                </div>
                <span style="background:rgba(48,209,88,0.18); color:#30d158; border:1px solid rgba(48,209,88,0.4); font-size:14px; font-weight:800; padding:6px 16px; border-radius:16px;">秒开即读</span>
            </div>

            <div style="background:rgba(0,0,0,0.35); border-radius:16px; padding:18px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="font-size:28px;">💻</div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#fff;">电脑宽屏端 · 在线推演沙盒</div>
                        <div style="font-size:13px; color:#86868b; margin-top:2px;">独家配装动态算分，铭文混搭模拟，阵容协同诊断</div>
                    </div>
                </div>
                <span style="background:rgba(0,113,227,0.18); color:#2997ff; border:1px solid rgba(41,151,255,0.4); font-size:14px; font-weight:800; padding:6px 16px; border-radius:16px;">送专属网址</span>
            </div>

            <div style="background:rgba(0,0,0,0.35); border-radius:16px; padding:18px 20px; border:1px solid rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="font-size:28px;">🤖</div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#fff;">AI 极客专享 · 原生数据包</div>
                        <div style="font-size:13px; color:#86868b; margin-top:2px;">纯净 Markdown 格式，一键投喂 NotebookLM / DeepSeek 打造私人教练</div>
                    </div>
                </div>
                <span style="background:rgba(175,82,222,0.18); color:#bf5af2; border:1px solid rgba(175,82,222,0.4); font-size:14px; font-weight:800; padding:6px 16px; border-radius:16px;">随包附赠</span>
            </div>
        </div>
        <div class="floating-gift">⚡ 拍下后旺旺聊天窗口 1 秒自动推送</div>
        """,
        "⚡ 自动发卡秒发 • 📑 内附新手必读指南 • 🔄 永久享受版本更新"
    ),
]


def render_all():
    os.makedirs(DETAILS_DIR, exist_ok=True)
    os.makedirs(TEMP_HTML_DIR, exist_ok=True)

    # 先清空 details 目录下旧的切片
    for f in os.listdir(DETAILS_DIR):
        fpath = os.path.join(DETAILS_DIR, f)
        if os.path.isfile(fpath):
            os.remove(fpath)

    for filename, pill_text, title_text, subtitle_html, console_html, footer_text in SLICES:
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
{COMMON_STYLE}
</style>
</head>
<body>
<div class="ambient-glow"></div>

<div class="header-area">
    <div class="season-pill"><span class="dot"></span><span>{pill_text}</span></div>
    <div class="main-title">{title_text}</div>
    <div class="subtitle">{subtitle_html}</div>
</div>

<div class="hero-stage">
    <div class="pro-console">
        {console_html}
    </div>
</div>

<div class="footer-note">
    <span>{footer_text}</span>
</div>
</body>
</html>
"""
        temp_html = os.path.join(TEMP_HTML_DIR, f"temp_{filename}.html")
        out_png = os.path.join(DETAILS_DIR, filename)

        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        cmd = [
            CHROME_PATH,
            "--headless",
            "--disable-gpu",
            "--window-size=800,1000",
            f"--screenshot={out_png}",
            temp_html
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ 生成高质感详情页切片: {filename}")

    import shutil
    if os.path.exists(TEMP_HTML_DIR):
        shutil.rmtree(TEMP_HTML_DIR)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    render_all()
