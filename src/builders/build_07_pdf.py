# -*- coding: utf-8 -*-
"""
王者荣耀 S45 全英雄全分路官方推荐出装与铭文大全 - 出版级矢量图文 PDF 构建器
对标 Apple 极简出版物排版，全面内嵌官方高清头像、装备图标、铭文图鉴
"""

import os
import sys
import re
import json
import shutil
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.hero_registry import CN_HERO_MANIFEST

CACHE_DIR = os.path.join(PROJECT_ROOT, "taobao", "assets_cache").replace("\\", "/")
CSS_LAYOUT_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_layout.css")
CSS_COMPONENTS_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_components.css")
CSS_BRAND_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_brand.css")
PDF_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_template.html")

HERO_MAP = {data["cname"]: ename for ename, data in CN_HERO_MANIFEST.items()}
HERO_TITLES = {data["cname"]: data.get("title", "") for ename, data in CN_HERO_MANIFEST.items()}

# 载入装备与铭文字典
with open(os.path.join(PROJECT_ROOT, "sandbox.html"), "r", encoding="utf-8") as f:
    sandbox_raw = f.read()

m_items = re.search(r'const ITEMS_DATA = (\[.*?\]);', sandbox_raw)
m_arcana = re.search(r'const ARCANA_DATA = (\{.*?\});', sandbox_raw)

ITEMS_LIST = json.loads(m_items.group(1)) if m_items else []
ARCANA_DICT = json.loads(m_arcana.group(1)) if m_arcana else {}

ITEM_MAP = {item["item_name"]: str(item["item_id"]) for item in ITEMS_LIST}
ARCANA_MAP = {name: str(data["id"]) for name, data in ARCANA_DICT.items()}

RED_ARCANA = {'圣人', '传承', '异变', '纷争', '无双', '宿命', '梦魇', '凶兆', '祸源', '红月'}
BLUE_ARCANA = {'长生', '贪婪', '夺萃', '兽痕', '冥想', '繁荣', '轮回', '调和', '隐匿', '狩猎'}
GREEN_ARCANA = {'霸者', '均衡', '虚空', '灵山', '献祭', '鹰眼', '心眼', '怜悯', '敬畏', '回声'}

HERO_AVATAR_ALIASES = {
    '敖隐': '519', '傲隐': '519',
    '戈娅': '548', '戈雅': '548',
    '弈星': '197', '奕星': '197',
    '元流之子(坦克)': '581', '元流之子（坦克）': '581',
    '元流之子(法师)': '582', '元流之子（法师）': '582', '元流之子(中路)': '582', '元流之子（中路）': '582',
    '元流之子(刺客)': '583', '元流之子（刺客）': '583',
    '元流之子(射手)': '584', '元流之子（射手）': '584',
    '元流之子(辅助)': '585', '元流之子（辅助）': '585',
}

def resolve_item_id(name: str):
    if name in ['贤者天书', '贤者之书']:
        return '1238'
    if name == '幽影袖箭':
        return '1161'
    if name in ITEM_MAP:
        return ITEM_MAP[name]
    for prefix in ['仁者', '强者', '王者', '不动·', '初级']:
        clean = name.replace(prefix, '')
        if clean in ITEM_MAP:
            return ITEM_MAP[clean]
    for iname, iid in ITEM_MAP.items():
        if iname in name or name in iname:
            return iid
    return None

def get_hero_avatar(cname: str) -> str:
    ename = HERO_AVATAR_ALIASES.get(cname) or HERO_MAP.get(cname, "")
    local_p = f"{CACHE_DIR}/hero/{ename}.jpg"
    return f"file:///{local_p}" if os.path.exists(local_p) else ""

def get_item_icon(iname: str) -> str:
    iid = resolve_item_id(iname)
    if iid:
        local_p = f"{CACHE_DIR}/item/{iid}.png"
        if os.path.exists(local_p):
            return f"file:///{local_p}"
    return ""

def get_arcana_icon(aname: str) -> str:
    aid = ARCANA_MAP.get(aname, "")
    if aid:
        local_p = f"{CACHE_DIR}/arcana/{aid}.png"
        if os.path.exists(local_p):
            return f"file:///{local_p}"
    return ""

def get_arcana_color(aname: str) -> str:
    if aname in RED_ARCANA: return "红色"
    if aname in BLUE_ARCANA: return "蓝色"
    if aname in GREEN_ARCANA: return "绿色"
    return "红色"

def build_pdf_html(md_path: str) -> str:
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    with open(CSS_LAYOUT_PATH, "r", encoding="utf-8") as f:
        css_layout = f.read()
    with open(CSS_COMPONENTS_PATH, "r", encoding="utf-8") as f:
        css_components = f.read()
    with open(CSS_BRAND_PATH, "r", encoding="utf-8") as f:
        brand_css = f.read()

    css_layout = css_layout.replace(
        'content: "第 " counter(page) " 页 ｜ 王者荣耀全维度战术知识库 (附赠在线推演沙盒)";',
        'content: "第 " counter(page) " 页 ｜ 淘宝店铺：TING LAB ｜ S45 官方实战出装与铭文大全";'
    )

    # 自定义专属 Apple 风格出装卡片 CSS
    custom_card_css = """
    .cover {
        height: 85vh !important;
        max-height: 88vh !important;
        page-break-after: always !important;
        break-after: page !important;
    }
    .hero-section-box {
        margin-top: 18px;
        margin-bottom: 22px;
    }
    .hero-card-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 10px 16px;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e5e5ea;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        margin-bottom: 12px;
        page-break-after: avoid;
    }
    .hero-avatar-round {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #0071e3;
    }
    .hero-header-text {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .hero-name-big {
        font-size: 15pt;
        font-weight: 800;
        color: #1d1d1f;
    }
    .hero-title-badge {
        font-size: 9pt;
        font-weight: 600;
        color: #86868b;
        background: #f5f5f7;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .lane-group-title {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 10.5pt;
        font-weight: 700;
        color: #0071e3;
        margin: 10px 0 8px 4px;
        page-break-after: avoid;
    }
    .scheme-card {
        background: #ffffff;
        border-radius: 10px;
        border: 1px solid #e5e5ea;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        page-break-inside: avoid;
    }
    .scheme-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        border-bottom: 1px dashed #f0f0f2;
        padding-bottom: 6px;
    }
    .scheme-badge {
        font-size: 9.5pt;
        font-weight: 700;
        color: #1d1d1f;
    }
    .scheme-tag-pill {
        font-size: 8pt;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        background: #e0f2fe;
        color: #0369a1;
    }
    .scheme-desc-text {
        font-size: 8.5pt;
        color: #64748b;
        line-height: 1.4;
        margin-bottom: 8px;
    }
    .items-flow-box {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
        margin-bottom: 8px;
        background: #f8fafc;
        padding: 6px 10px;
        border-radius: 8px;
    }
    .items-flow-label {
        font-size: 8.5pt;
        font-weight: 700;
        color: #334155;
        margin-right: 4px;
    }
    .item-chip-gold {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 6px 2px 3px;
        border-radius: 6px;
        font-size: 8pt;
        font-weight: 700;
        background: #fffbeb;
        border: 1px solid #fde68a;
        color: #92400e;
    }
    .item-chip-gold img {
        width: 17px;
        height: 17px;
        border-radius: 3px;
    }
    .flow-arrow {
        color: #0284c7;
        font-weight: 800;
        font-size: 8.5pt;
        margin: 0 1px;
    }
    .arcana-flow-box {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        padding: 4px 10px;
        background: #fdfdfd;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .arcana-flow-label {
        font-size: 8.5pt;
        font-weight: 700;
        color: #475569;
        margin-right: 4px;
    }
    .situational-box {
        font-size: 7.5pt;
        color: #94a3b8;
        padding-left: 10px;
    }
    """

    css_code = f"{css_layout}\n\n{css_components}\n\n{brand_css}\n\n{custom_card_css}"

    # 解析 Markdown 结构
    lines = md_text.split("\n")
    html_parts = []
    
    current_hero = ""
    current_lane = ""
    in_scheme = False
    scheme_title = ""
    scheme_desc = ""
    scheme_items = []
    scheme_arcana = ""
    scheme_situational = ""

    def flush_scheme():
        nonlocal in_scheme, scheme_title, scheme_desc, scheme_items, scheme_arcana, scheme_situational
        if not in_scheme:
            return
        
        # 格式化出装
        item_chips = []
        for it in scheme_items:
            it = it.strip()
            if not it: continue
            icon = get_item_icon(it)
            img_tag = f'<img src="{icon}">' if icon else ''
            item_chips.append(f'<span class="item-chip-gold">{img_tag}<span>{it}</span></span>')
        items_html = ' <span class="flow-arrow">➔</span> '.join(item_chips)

        # 格式化铭文
        arcana_chips = []
        for match in re.finditer(r'(\d{1,2})\s*([^\d\s\+]{2,4})', scheme_arcana):
            cnt, aname = match.group(1), match.group(2)
            color = get_arcana_color(aname)
            icon = get_arcana_icon(aname)
            img_tag = f'<img src="{icon}">' if icon else ''
            arcana_chips.append(f'<span class="arcana-chip {color}">{img_tag}<strong>{cnt}{aname}</strong></span>')
        arcana_html = ' '.join(arcana_chips) if arcana_chips else f'<code>{scheme_arcana}</code>'

        card = f"""
        <div class="scheme-card">
            <div class="scheme-header-bar">
                <span class="scheme-badge">{scheme_title}</span>
                <span class="scheme-tag-pill">{current_lane}实战</span>
            </div>
            <div class="scheme-desc-text"><strong>官方推荐思路：</strong>{scheme_desc}</div>
            <div class="items-flow-box">
                <span class="items-flow-label">核心六神装：</span>
                {items_html}
            </div>
            <div class="arcana-flow-box">
                <span class="arcana-flow-label">五级铭文组合：</span>
                {arcana_html}
            </div>
            <div class="situational-box">
                <strong>后期保命与备选：</strong>{scheme_situational}
            </div>
        </div>
        """
        html_parts.append(card)
        in_scheme = False
        scheme_title = ""
        scheme_desc = ""
        scheme_items = []
        scheme_arcana = ""
        scheme_situational = ""

    for line in lines:
        line_s = line.strip()
        
        # 匹配英雄标题
        m_hero = re.match(r'^##\s+【(.*?)】', line_s)
        if m_hero:
            flush_scheme()
            current_hero = m_hero.group(1)
            avatar = get_hero_avatar(current_hero)
            title = HERO_TITLES.get(current_hero, "王者英雄")
            avatar_img = f'<img src="{avatar}" class="hero-avatar-round">' if avatar else ''
            header = f"""
            <div class="hero-section-box">
                <div class="hero-card-header">
                    {avatar_img}
                    <div class="hero-header-text">
                        <span class="hero-name-big">{current_hero}</span>
                        <span class="hero-title-badge">{title}</span>
                    </div>
                </div>
            """
            html_parts.append(header)
            continue

        # 匹配分路
        m_lane = re.match(r'^###\s+.*?分路：【(.*?)】', line_s)
        if m_lane:
            flush_scheme()
            current_lane = m_lane.group(1)
            html_parts.append(f'<div class="lane-group-title">📍 推荐分路：{current_lane}</div>')
            continue

        # 匹配方案
        m_sch = re.match(r'^####\s+(方案\d+：【.*?】)', line_s)
        if m_sch:
            flush_scheme()
            in_scheme = True
            scheme_title = m_sch.group(1).replace("【", "").replace("】", "")
            continue

        if in_scheme:
            if line_s.startswith("- **官方推荐思路**："):
                scheme_desc = line_s.replace("- **官方推荐思路**：", "").strip()
            elif line_s.startswith("- **核心六神装 (按实战成装顺序)**："):
                raw_items = line_s.replace("- **核心六神装 (按实战成装顺序)**：", "").strip()
                scheme_items = raw_items.split("➔")
            elif line_s.startswith("- **标准五级铭文组合"):
                m_code = re.search(r'`(.*?)`', line_s)
                scheme_arcana = m_code.group(1) if m_code else line_s.split("：")[-1].strip()
            elif line_s.startswith("- **后期保命与备选神装**："):
                scheme_situational = line_s.replace("- **后期保命与备选神装**：", "").strip()
            elif line_s.startswith("---"):
                flush_scheme()
                html_parts.append("</div>") # 关闭 hero-section-box

    flush_scheme()
    html_parts.append("</div>") # 关闭最后一个 hero-section-box

    body_html = "\n".join(html_parts)

    logo_url = f"file:///{CACHE_DIR}/brand/ting_lab_logo.png"
    qr_url = f"file:///{CACHE_DIR}/brand/qr_code.png"

    with open(PDF_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = f.read()

    return tpl.format(
        title="王者荣耀 S45 全英雄全分路官方出装与铭文大全",
        clean_title="王者荣耀 S45 全英雄官方出装与铭文大全",
        sub="全英雄 · 全分路 · 513套实战神装 · 官方实录直出",
        logo_url=logo_url,
        qr_url=qr_url,
        css_code=css_code,
        body_html=body_html
    )

def render_07_pdf():
    MD_PATH = os.path.join(PROJECT_ROOT, "output", "07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.md")
    TARGET_PDF = os.path.join(PROJECT_ROOT, "taobao", "pdf", "07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.pdf")
    TEMP_HTML = os.path.join(PROJECT_ROOT, "taobao", "pdf", "temp_07.html")
    
    os.makedirs(os.path.dirname(TARGET_PDF), exist_ok=True)

    print("📄 正在生成 Apple 风格图文排版 HTML...")
    html_code = build_pdf_html(MD_PATH)
    with open(TEMP_HTML, "w", encoding="utf-8") as f:
        f.write(html_code)

    print("🚀 启动 Playwright 高清排版引擎进行 PDF 渲染...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--allow-file-access-from-files", "--disable-web-security"]
        )
        page = browser.new_page()
        page.goto(f"file:///{TEMP_HTML.replace(os.sep, '/')}", wait_until="load")
        page.pdf(
            path=TARGET_PDF,
            format="A4",
            print_background=True,
            margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"}
        )
        browser.close()

    if os.path.exists(TEMP_HTML):
        os.remove(TEMP_HTML)

    pdf_size_mb = os.path.getsize(TARGET_PDF) / (1024 * 1024)
    print(f"✅ 成功生成出版级矢量 PDF: {TARGET_PDF} ({pdf_size_mb:.2f} MB)")

    # 同步复制一份至 output/ 与 dist_pages/pdf/
    out_copy = os.path.join(PROJECT_ROOT, "output", "07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.pdf")
    shutil.copyfile(TARGET_PDF, out_copy)
    dist_dir = os.path.join(PROJECT_ROOT, "dist_pages", "pdf")
    if os.path.exists(dist_dir):
        shutil.copyfile(TARGET_PDF, os.path.join(dist_dir, "07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.pdf"))
    print(f"📦 已同步部署至: {out_copy}")

if __name__ == "__main__":
    render_07_pdf()
