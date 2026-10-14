# -*- coding: utf-8 -*-
"""
王者荣耀淘宝 1200x1200 高清主图矩阵生成器 (Apple 钛金仪表盘极简风)
全面同步 2026 S45 赛季“月照长安”与 133 位国服英雄数据。
"""

import os
import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMG_DIR = os.path.join(PROJECT_ROOT, "taobao", "images")
os.makedirs(IMG_DIR, exist_ok=True)

# 1200x1200 超高清 Apple 钛金风模板样式
MAIN_STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    width: 1200px;
    height: 1200px;
    background: radial-gradient(130% 120% at 50% 0%, #fbfcfd 0%, #f2f5fa 45%, #e5eaf2 100%);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #1d1d1f;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 70px 50px 50px 50px;
    position: relative;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
}
.ambient-glow {
    position: absolute; top: -120px; left: 50%; transform: translateX(-50%);
    width: 900px; height: 450px;
    background: radial-gradient(circle, rgba(0, 113, 227, 0.12) 0%, rgba(0, 113, 227, 0) 70%);
    pointer-events: none; z-index: 0;
}
.header-area { text-align: center; z-index: 2; }
.season-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(16px);
    color: #0071e3; font-size: 20px; font-weight: 700;
    padding: 8px 24px; border-radius: 980px; letter-spacing: 0.04em;
    border: 1.5px solid rgba(0, 113, 227, 0.25);
    box-shadow: 0 4px 16px rgba(0, 113, 227, 0.1); margin-bottom: 16px;
}
.season-pill .dot { width: 8px; height: 8px; background: #0071e3; border-radius: 50%; box-shadow: 0 0 8px #0071e3; }
.main-title {
    font-size: 68px; font-weight: 850; letter-spacing: -0.03em; line-height: 1.1;
    background: linear-gradient(180deg, #0a0a0c 0%, #2c2c30 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 14px;
}
.subtitle {
    font-size: 26px; color: #48484a; font-weight: 500;
    display: flex; align-items: center; justify-content: center; gap: 12px;
}
.subtitle-badge {
    background: #1c1c1e; color: #ffffff; font-size: 18px; font-weight: 700;
    padding: 4px 14px; border-radius: 8px;
}
.highlight-blue { color: #0071e3; font-weight: 700; }
.stage-area { width: 100%; display: flex; justify-content: center; align-items: center; position: relative; z-index: 2; }
.pro-card {
    width: 1080px;
    background: linear-gradient(180deg, #18181c 0%, #111114 100%);
    border-radius: 32px;
    border: 1.5px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    padding: 36px 40px;
    display: flex; flex-direction: column; gap: 24px;
}
.footer-row {
    font-size: 20px; color: #48484a; font-weight: 600;
    display: flex; gap: 30px; align-items: center; z-index: 2;
    background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(16px);
    padding: 12px 36px; border-radius: 980px; border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.footer-row .sep { color: #c7c7cc; }
"""

def generate_main_01_html():
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{MAIN_STYLE}
</style>
</head>
<body>
<div class="ambient-glow"></div>

<div class="header-area">
    <div class="season-pill"><span class="dot"></span>2026 S45 赛季 · 月照长安最新版</div>
    <div class="main-title">王者全英雄战术手册</div>
    <div class="subtitle">
        <span class="subtitle-badge">PDF 电子版</span>
        <span>133位国服英雄克制谱系 ｜ 铭文出装大典 · <span class="highlight-blue">附赠在线推演沙盒</span></span>
    </div>
</div>

<div class="stage-area">
    <div class="pro-card">
        <!-- 英雄抬头 -->
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:18px;">
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="position:relative; width:76px; height:76px; border-radius:20px; padding:2.5px; background:linear-gradient(135deg, #f59e0b, #b45309); box-shadow:0 0 20px rgba(245,158,11,0.4);">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg" style="width:100%; height:100%; border-radius:18px; object-fit:cover;">
                    <div style="position:absolute; bottom:-4px; right:-4px; background:#111; border:1px solid #f59e0b; color:#f59e0b; font-size:13px; font-weight:800; padding:1px 6px; border-radius:6px;">15</div>
                </div>
                <div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:32px; font-weight:800; color:#fff;">廉颇</span>
                        <span style="background:rgba(255,255,255,0.12); color:#e5e5ea; font-size:15px; font-weight:700; padding:3px 10px; border-radius:8px;">对抗路 / 坦克</span>
                    </div>
                    <div style="font-size:16px; color:#98989f; margin-top:4px;">正义爆轰 · 满级六神装与铭文最佳协同推演</div>
                </div>
            </div>
            <div style="background:rgba(0,113,227,0.18); color:#2997ff; font-size:18px; font-weight:700; padding:8px 20px; border-radius:980px; border:1px solid rgba(41,151,255,0.4);">
                • 实时算分引擎
            </div>
        </div>

        <!-- 六神装 -->
        <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-size:15px; font-weight:700; color:#86868b; letter-spacing:0.04em;">六神装备槽位 (装备被动互斥与协同检测)</span>
                <span style="color:#30d158; font-size:15px; font-weight:700;">✔ 装备被动无冲突</span>
            </div>
            <div style="display:flex; justify-content:space-between; gap:12px;">
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1133.png" style="width:60px; height:60px; border-radius:14px; border:1.5px solid #eab308; box-shadow:0 0 12px rgba(234,179,8,0.3);">
                    <span style="font-size:14px; font-weight:700; color:#fff;">暗影战斧</span>
                </div>
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1332.png" style="width:60px; height:60px; border-radius:14px; border:1.5px solid #eab308; box-shadow:0 0 12px rgba(234,179,8,0.3);">
                    <span style="font-size:14px; font-weight:700; color:#fff;">不祥征兆</span>
                </div>
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1331.png" style="width:60px; height:60px; border-radius:14px; border:1.5px solid #eab308; box-shadow:0 0 12px rgba(234,179,8,0.3);">
                    <span style="font-size:14px; font-weight:700; color:#fff;">暴烈之甲</span>
                </div>
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1334.png" style="width:60px; height:60px; border-radius:14px; border:1.5px solid #eab308; box-shadow:0 0 12px rgba(234,179,8,0.3);">
                    <span style="font-size:14px; font-weight:700; color:#fff;">魔女斗篷</span>
                </div>
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1126.png" style="width:60px; height:60px; border-radius:14px; border:1.5px solid #eab308; box-shadow:0 0 12px rgba(234,179,8,0.3);">
                    <span style="font-size:14px; font-weight:700; color:#fff;">碎星锤</span>
                </div>
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:12px 6px; display:flex; flex-direction:column; align-items:center; gap:8px;">
                    <img src="https://game.gtimg.cn/images/yxzj/img201606/itemimgo/1335.png" style="width:60px; height:60px; border-radius:14px; border:1.5px solid #eab308; box-shadow:0 0 12px rgba(234,179,8,0.3);">
                    <span style="font-size:14px; font-weight:700; color:#fff;">贤者庇护</span>
                </div>
            </div>
        </div>

        <!-- 3项指标 -->
        <div style="display:flex; justify-content:space-around; align-items:center; background:rgba(0,0,0,0.35); border-radius:20px; padding:18px 24px; border:1px solid rgba(255,255,255,0.05);">
            <div style="text-align:center;">
                <div style="font-size:13px; font-weight:700; color:#86868b; margin-bottom:4px;">最终最大生命</div>
                <div style="font-size:36px; font-weight:800; color:#fff;">11,280</div>
                <div style="width:40px; height:3px; background:#0071e3; border-radius:2px; margin:4px auto 0;"></div>
            </div>
            <div style="width:1px; height:40px; background:rgba(255,255,255,0.1);"></div>
            <div style="text-align:center;">
                <div style="font-size:13px; font-weight:700; color:#86868b; margin-bottom:4px;">物理抗性免伤率</div>
                <div style="font-size:36px; font-weight:800; color:#2997ff;">64.2%</div>
                <div style="width:40px; height:3px; background:#2997ff; border-radius:2px; margin:4px auto 0;"></div>
            </div>
            <div style="width:1px; height:40px; background:rgba(255,255,255,0.1);"></div>
            <div style="text-align:center;">
                <div style="font-size:13px; font-weight:700; color:#86868b; margin-bottom:4px;">机制协同诊断</div>
                <div style="font-size:36px; font-weight:800; color:#30d158;">100分</div>
                <div style="width:40px; height:3px; background:#30d158; border-radius:2px; margin:4px auto 0;"></div>
            </div>
        </div>
    </div>
</div>

<div class="footer-row">
    <span>• 纯净数据无水印</span>
    <span class="sep">|</span>
    <span>• 133位英雄全量收录 (含王维)</span>
    <span class="sep">|</span>
    <span>• 独家在线沙盒永久直开</span>
</div>

</body>
</html>"""

def build_all_main_images():
    """使用 Playwright 将 1200x1200 核心主图渲染输出为高清 PNG"""
    print("🚀 启动 Playwright 高清主图渲染引擎 (1200x1200)...")
    temp_html = os.path.join(IMG_DIR, "temp_main_01.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(generate_main_01_html())

    target_path = os.path.join(IMG_DIR, "01_主图_王者战术手册.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--allow-file-access-from-files", "--disable-web-security"]
        )
        page = browser.new_page(viewport={"width": 1200, "height": 1200})
        page.goto(f"file:///{temp_html.replace(os.sep, '/')}", wait_until="load")
        page.screenshot(path=target_path)
        browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    print(f"✅ 【成功】核心搜索主图 01 已更新为 S45 最新赛季版：{target_path} (1200x1200)")

if __name__ == "__main__":
    build_all_main_images()
