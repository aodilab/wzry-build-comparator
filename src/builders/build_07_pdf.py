# -*- coding: utf-8 -*-
"""
07 卷 S45 全英雄官方实战出装与铭文精选大典 PDF 构建器
"""
import os
import re
from playwright.sync_api import sync_playwright
from src.builders.pdf_07_helpers import (
    PROJECT_ROOT, CACHE_DIR, CSS_LAYOUT_PATH, CSS_COMPONENTS_PATH,
    CSS_BRAND_PATH, PDF_TEMPLATE_PATH, HERO_MAP, HERO_TITLES,
    ITEM_MAP, ARCANA_MAP, RED_ARCANA, BLUE_ARCANA, GREEN_ARCANA,
    HERO_AVATAR_ALIASES, MAINSTREAM_HEROES,
    resolve_item_id, get_hero_avatar, get_item_icon, get_arcana_icon, get_arcana_color,
)
CSS_TABLES_CARDS_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_tables_cards.css")
CSS_07_CARDS_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_07_cards.css")

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
    with open(CSS_TABLES_CARDS_PATH, "r", encoding="utf-8") as f:
        css_tables = f.read()
    with open(CSS_07_CARDS_PATH, "r", encoding="utf-8") as f:
        custom_card_css = f.read()

    css_code = f"{css_layout}\n\n{css_components}\n\n{css_tables}\n\n{brand_css}\n\n{custom_card_css}"
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

    skip_hero = False
    for line in lines:
        line_s = line.strip()
        
        # 匹配英雄标题
        m_hero = re.match(r'^##\s+【(.*?)】', line_s)
        if m_hero:
            flush_scheme()
            hero_cname = m_hero.group(1)
            if hero_cname not in MAINSTREAM_HEROES:
                skip_hero = True
                continue
            skip_hero = False
            current_hero = hero_cname
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

        if skip_hero:
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

    logo_url = f"file:///{CACHE_DIR}/ting_lab_logo_trans.png"
    qr_url = f"file:///{CACHE_DIR}/sandbox_qr.png"

    with open(PDF_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = f.read()

    return tpl.format(
        title="王者荣耀 S45 主流热门英雄官方实战出装与铭文精选",
        clean_title="王者荣耀 S45 主流热门英雄官方出装精选",
        sub="S45 热门主流英雄 · 官方实战出装 · 核心铭文方案 · 过滤冷门冗余",
        logo_url=logo_url,
        qr_url=qr_url,
        css_code=css_code,
        body_html=body_html
    )

def render_07_pdf():
    MD_PATH = os.path.join(PROJECT_ROOT, "output", "07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.md")
    TARGET_PDF = os.path.join(PROJECT_ROOT, "taobao", "pdf", "07_S45主流热门英雄官方实战出装与铭文精选.pdf")
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

    # PyMuPDF 工业级无损流压缩，确保低于 Cloudflare 25MB 上限并加速下载
    try:
        import pymupdf
        doc = pymupdf.open(TARGET_PDF)
        opt_tmp = TARGET_PDF + ".opt.pdf"
        doc.save(opt_tmp, garbage=4, deflate=True)
        doc.close()
        if os.path.exists(opt_tmp):
            os.replace(opt_tmp, TARGET_PDF)
    except Exception as e:
        print(f"PyMuPDF 优化跳过: {e}")

    pdf_size_mb = os.path.getsize(TARGET_PDF) / (1024 * 1024)
    print(f"✅ 成功生成出版级矢量 PDF: {TARGET_PDF} ({pdf_size_mb:.2f} MB)")

    # 仅同步复制至 dist_pages/pdf/ (严禁复制入 output/ 保持纯净 MD 库)
    dist_dir = os.path.join(PROJECT_ROOT, "dist_pages", "pdf")
    if os.path.exists(dist_dir):
        shutil.copyfile(TARGET_PDF, os.path.join(dist_dir, "07_S45主流热门英雄官方实战出装与铭文精选.pdf"))
    print(f"📦 已同步部署至: dist_pages/pdf/")

if __name__ == "__main__":
    render_07_pdf()
