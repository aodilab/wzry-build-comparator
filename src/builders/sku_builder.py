# -*- coding: utf-8 -*-
import os
import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TAOBAO_DIR = os.path.join(PROJECT_ROOT, "taobao")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "preview_server")
os.makedirs(TAOBAO_DIR, exist_ok=True)

html_code = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #e5e5ea;
    display: flex;
    gap: 60px;
    padding: 60px;
    -webkit-font-smoothing: antialiased;
  }

  /* 800x800 1:1 Apple 纯白银灰极简美学卡片 */
  .apple-card {
    width: 800px;
    height: 800px;
    background: #ffffff;
    border-radius: 36px;
    padding: 64px 60px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.04);
    border: 1.5px solid rgba(0, 0, 0, 0.08);
    position: relative;
    color: #1d1d1f;
  }

  /* 尊享版: 纯净亮色体系，通过更高级的质感细节体现尊贵，拒绝沉闷纯黑 */
  .apple-card.vip {
    background: linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%);
    border: 2px solid #0071e3;
    box-shadow: 0 12px 40px rgba(0, 113, 227, 0.1);
  }

  /* 顶部标签行 */
  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .eyebrow {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: #86868b;
  }
  .eyebrow.vip-tag {
    color: #0071e3;
    background: rgba(0, 113, 227, 0.08);
    padding: 4px 12px;
    border-radius: 6px;
  }
  .brand-tag {
    font-size: 13px;
    font-weight: 600;
    color: #86868b;
    letter-spacing: 0.02em;
  }

  /* 标题区域 */
  .card-header {
    margin-top: 24px;
  }
  .headline {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #1d1d1f;
    line-height: 1.15;
  }
  .subhead {
    font-size: 18px;
    font-weight: 500;
    color: #86868b;
    margin-top: 10px;
    letter-spacing: -0.01em;
  }
  .apple-card.vip .subhead {
    color: #0071e3;
  }

  /* 留白充足的极简特性清单 (Apple 官网排版) */
  .feature-specs {
    margin: 36px 0;
    display: flex;
    flex-direction: column;
    gap: 22px;
  }
  .spec-item {
    display: flex;
    align-items: baseline;
    gap: 14px;
    font-size: 18px;
    font-weight: 500;
    color: #1d1d1f;
    line-height: 1.4;
  }
  .spec-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #0071e3;
    flex-shrink: 0;
    transform: translateY(-3px);
  }
  .apple-card.vip .spec-dot {
    background: #0071e3;
    box-shadow: 0 0 6px rgba(0, 113, 227, 0.5);
  }
  .spec-highlight {
    font-weight: 700;
    color: #1d1d1f;
  }

  /* 底部价格与动作栏 */
  .card-bottom {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding-top: 28px;
    border-top: 1.5px solid #f2f2f7;
  }
  .apple-card.vip .card-bottom {
    border-top-color: rgba(0, 113, 227, 0.15);
  }

  .price-lockup {
    display: flex;
    align-items: baseline;
    gap: 4px;
  }
  .price-unit {
    font-size: 26px;
    font-weight: 700;
    color: #1d1d1f;
  }
  .price-num {
    font-size: 64px;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #1d1d1f;
    line-height: 1;
  }
  .apple-card.vip .price-num {
    color: #0071e3;
  }
  .apple-card.vip .price-unit {
    color: #0071e3;
  }
  .price-suffix {
    font-size: 14px;
    font-weight: 600;
    color: #86868b;
    margin-left: 8px;
  }

  .bottom-tag {
    font-size: 14px;
    font-weight: 700;
    color: #86868b;
    letter-spacing: 0.02em;
  }
  .apple-card.vip .bottom-tag {
    color: #0071e3;
    background: #e8f2fd;
    padding: 6px 16px;
    border-radius: 980px;
  }
</style>
</head>
<body>

<!-- SKU 1: 标准版 (纯白底色 · 极简标准配置) -->
<div id="skuStandard" class="apple-card">
  <div>
    <div class="card-top">
      <span class="eyebrow">2026 S45 赛季 · 月照长安</span>
      <span class="brand-tag">TING LAB 出版物</span>
    </div>
    <div class="card-header">
      <div class="headline">当前赛季·标准版</div>
      <div class="subhead">全量战术出版物矩阵 ＋ 在线推演沙盒</div>
    </div>
  </div>

  <div class="feature-specs">
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">全套 6 册矢量 PDF 手册</strong> ｜ 技能数值 · 出装拓扑 · 战场机制</span>
    </div>
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">133 位国服英雄全收录</strong> ｜ 同步新英雄王维及 7 位平衡调整</span>
    </div>
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">在线推演沙盒使用权</strong> ｜ 自由配装混搭 · 实时算分验证</span>
    </div>
    <div class="spec-item" style="color: #86868b;">
      <span class="spec-dot" style="background: #d2d2d7;"></span>
      <span>当前赛季单次买断交付 · 自动秒发提货</span>
    </div>
  </div>

  <div class="card-bottom">
    <div class="price-lockup">
      <span class="price-unit">¥</span>
      <span class="price-num">9.90</span>
      <span class="price-suffix">/ 单次交付</span>
    </div>
    <span class="bottom-tag">即开即读 ↗</span>
  </div>
</div>

<!-- SKU 2: 尊享版 (纯白银灰亮色体系 · Apple 蓝微光高级细节，不沉闷) -->
<div id="skuVip" class="apple-card vip">
  <div>
    <div class="card-top">
      <span class="eyebrow vip-tag">🔥 80%玩家首选 · 终身免费包更新</span>
      <span class="brand-tag">TING LAB 旗舰专供</span>
    </div>
    <div class="card-header">
      <div class="headline">终身更新·尊享版</div>
      <div class="subhead">一次购买 · 永久免费享受新英雄与跨赛季更新</div>
    </div>
  </div>

  <div class="feature-specs">
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">全套 6 册手册 ＋ 在线推演沙盒</strong> 包含标准版全部资产</span>
    </div>
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">终身免费包更新</strong> ｜ 跨赛季 · 新英雄 · 装备重做永久推送</span>
    </div>
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">VIP 专属云端网盘</strong> ｜ 独家长期更新通道 · 永不失效</span>
    </div>
    <div class="spec-item">
      <span class="spec-dot"></span>
      <span><strong class="spec-highlight">官方算法调优优先权</strong> ｜ 局内底层机制改动即时同步</span>
    </div>
  </div>

  <div class="card-bottom">
    <div class="price-lockup">
      <span class="price-unit">¥</span>
      <span class="price-num">19.90</span>
      <span class="price-suffix">/ 一次付费 · 终身受用</span>
    </div>
    <span class="bottom-tag">终身特权 ↗</span>
  </div>
</div>

</body>
</html>
"""

temp_html = os.path.join(TAOBAO_DIR, "temp_apple_sku.html")
with open(temp_html, "w", encoding="utf-8") as f:
    f.write(html_code)

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chrome",
        headless=True,
        args=["--allow-file-access-from-files", "--disable-web-security"]
    )
    page = browser.new_page(viewport={"width": 1850, "height": 950})
    page.goto(f"file:///{temp_html.replace(os.sep, '/')}", wait_until="load")

    # 保存到 taobao 文件夹
    std_path = os.path.join(TAOBAO_DIR, "sku_standard_9_9.png")
    vip_path = os.path.join(TAOBAO_DIR, "sku_vip_19_9.png")

    page.query_selector("#skuStandard").screenshot(path=std_path)
    page.query_selector("#skuVip").screenshot(path=vip_path)

    if os.path.exists(PREVIEW_DIR):
        page.query_selector("#skuStandard").screenshot(path=os.path.join(PREVIEW_DIR, "sku_standard_9_9.png"))
        page.query_selector("#skuVip").screenshot(path=os.path.join(PREVIEW_DIR, "sku_vip_19_9.png"))

    browser.close()

if os.path.exists(temp_html):
    os.remove(temp_html)

print(f"✅ 生成白银灰极简标准版: {std_path}")
print(f"✅ 生成纯亮色系 Apple 蓝尊享版: {vip_path}")
