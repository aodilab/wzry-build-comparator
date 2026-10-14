# -*- coding: utf-8 -*-
"""
王者荣耀 01~06 卷高清富媒体矢量 PDF 渲染引擎
"""
import os
import re
import markdown
from playwright.sync_api import sync_playwright
from src.builders.pdf_enrichers import (
    PROJECT_ROOT, OUTPUT_DIR, PDF_DIR, CACHE_DIR,
    CSS_LAYOUT_PATH, CSS_COMPONENTS_PATH,
    HERO_MAP, ITEM_MAP, ARCANA_MAP,
    get_hero_avatar, get_skill_icon, get_item_icon, get_arcana_icon,
    enrich_01_skills, enrich_02_counters, enrich_03_builds,
)
CSS_TABLES_CARDS_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_tables_cards.css")

def enrich_04_items(md_text: str) -> str:
    lines = md_text.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_item = re.match(r'^####\s+装备名称：(.*)', line)
        if m_item:
            iname = m_item.group(1).strip()
            iid = ITEM_MAP.get(iname, "")
            icon = get_item_icon(iid) if iid else ""
            img_tag = f'<img src="{icon}" class="item-avatar-large">' if icon else ''

            i += 1
            price_base, price_total, recipe_raw, upgrade_raw, stats_raw, effect_raw = "", "", "", "", "", ""
            while i < len(lines) and lines[i].startswith("- **"):
                il = lines[i]
                if "基础售价" in il: price_base = il.split("：")[-1].strip()
                elif "合成总价" in il: price_total = il.split("：")[-1].strip()
                elif "【合成配方】" in il: recipe_raw = il.split("：")[-1].strip()
                elif "【升级方向】" in il: upgrade_raw = il.split("：")[-1].strip()
                elif "基础属性" in il: stats_raw = il.split("：")[-1].strip()
                elif "装备效果" in il: effect_raw = il.split("：")[-1].strip()
                i += 1

            def format_chips(text):
                if not text or "无" in text:
                    return '<span style="color:#94a3b8;font-size:7.5pt;">基础小件 / 特殊道具</span>'
                parts = re.split(r'[,、，\s]+', text)
                chips = []
                for p in parts:
                    p = p.strip()
                    if not p: continue
                    piid = ITEM_MAP.get(p, "")
                    picon = get_item_icon(piid) if piid else ""
                    pimg = f'<img src="{picon}">' if picon else ''
                    chips.append(f'<span class="item-chip">{pimg}{p}</span>')
                return " ".join(chips)

            recipe_chips = format_chips(recipe_raw)
            upgrade_chips = format_chips(upgrade_raw)

            effect_html = f'<div class="item-effect-box"><strong>⚡ 唯一被动/效果：</strong>{effect_raw}</div>' if effect_raw and effect_raw != "无" else ''

            card_html = (
                f'<div class="item-entry-card">\n'
                f'<div class="item-entry-header">\n'
                f'<div class="item-entry-title-wrap">{img_tag}<span class="item-name-big">{iname}</span></div>\n'
                f'<div class="item-price-badges"><span class="price-pill">🪙 售价: {price_base}</span><span class="price-pill">💰 总价: {price_total}</span></div>\n'
                f'</div>\n'
                f'<div class="item-stat-row">✦ {stats_raw}</div>\n'
                f'<div class="item-flow-row"><strong>【合成配方】：</strong>{recipe_chips}</div>\n'
                f'<div class="item-flow-row"><strong>【升级方向】：</strong>{upgrade_chips}</div>\n'
                f'{effect_html}\n'
                f'</div>\n'
            )
            new_lines.append(card_html)
            continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def enrich_05_arcana(md_text: str) -> str:
    lines = md_text.split("\n")
    new_lines = []
    for line in lines:
        m_arcana = re.match(r'^####\s+【(.*)】', line)
        if m_arcana:
            aname = m_arcana.group(1).strip()
            if aname in ARCANA_MAP:
                icon = get_arcana_icon(ARCANA_MAP[aname])
                new_lines.append(f'<div class="arcana-card-header"><img src="{icon}" class="arcana-avatar-large"><span class="arcana-name-big">{aname}</span></div>\n')
                continue

        m_hero = re.match(r'^####\s+英雄：([^\s（]+)（([^）]+)）', line)
        if m_hero:
            cname, title = m_hero.group(1), m_hero.group(2)
            ename = HERO_MAP.get(cname, "")
            avatar = get_hero_avatar(ename) if ename else ""
            new_lines.append(f'<div class="hero-card-header"><img src="{avatar}" class="hero-avatar-round"><div class="hero-header-text"><span class="hero-name-big">{cname}</span><span class="hero-title-badge">{title}</span></div></div>\n')
            continue

        m_rec = re.match(r'^(?:\s*-\s+\*\*([^\*]+)\*\*\s*\((红色|蓝色|绿色)\s*5级\))(.*)', line)
        if m_rec:
            aname, color, rest = m_rec.group(1), m_rec.group(2), m_rec.group(3)
            if aname in ARCANA_MAP:
                icon = get_arcana_icon(ARCANA_MAP[aname])
                new_lines.append(f'  - <span class="arcana-chip {color}"><img src="{icon}"><strong>{aname}</strong> ({color} 5级)</span>{rest}\n')
                continue

        new_lines.append(line)
    return "\n".join(new_lines)


def enrich_06_rules(md_text: str) -> str:
    # 注入战场核心卡片、蓝Buff、红Buff、双抗公式
    md_text = re.sub(
        r'(###\s*1\.\s*蔚蓝石像之力.*)',
        r'<div class="mechanic-card blue">\n\1\n</div>',
        md_text
    )
    md_text = re.sub(
        r'(\*\s+\*\*蔚蓝石像之力（蓝Buff）效果\*\*：)',
        r'<span class="arcana-chip 蓝色">💙 蔚蓝石像之力 (冷却缩减+20% & 每秒回蓝2%)</span>\n\1',
        md_text
    )
    md_text = re.sub(
        r'(\*\s+\*\*猩红石像之力（红Buff）效果\*\*：)',
        r'<span class="arcana-chip 红色">❤️ 猩红石像之力 (普通攻击减速 & 真实伤害附带)</span>\n\1',
        md_text
    )
    
    # 替换其中的装备名称为图文微标签
    for iname in ['名刀·司命', '暗影战斧', '炽热支配', '辉月', '血魔之怒', '不死鸟之眼', '冰痕之握', '贤者的庇护', '抵抗之靴', '巨人之握', '破晓', '碎星锤']:
        if iname in ITEM_MAP:
            icon = get_item_icon(ITEM_MAP[iname])
            chip = f'<span class="item-chip"><img src="{icon}">{iname}</span>'
            md_text = re.sub(rf'(`|\*\*)?({re.escape(iname)})(`|\*\*)?', chip, md_text)
            
    # 格式化双抗免伤公式
    md_text = re.sub(
        r'(\*\*免伤比例\s*=\s*抗性数值\s*/\s*\(抗性数值\s*\+\s*602\)\*\*)',
        r'<div class="formula-box"><div class="formula-title">📐 王者荣耀底层免伤核心算法公式</div>免伤比例 (%) = 实际抗性 / (实际抗性 + 602) × 100%<br><small style="color:#a1a1a6;">注：当抗性达到 602 点时减免 50% 伤害；抗性达到 1405 点时减免 70% 伤害。</small></div>',
        md_text
    )
    return md_text


CSS_BRAND_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_brand.css")
HTML_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_template.html")


def render_html_page(title: str, sub: str, body_html: str, css_code: str) -> str:
    logo_url = f"file:///{CACHE_DIR}/ting_lab_logo_trans.png"
    qr_url = f"file:///{CACHE_DIR}/sandbox_qr.png"
    clean_title = title.replace("王者荣耀_", "").replace("01_", "01 ").replace("02_", "02 ").replace("03_", "03 ").replace("04_", "04 ").replace("05_", "05 ").replace("06_", "06 ")
    with open(HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = f.read()
    return tpl.format(
        title=title,
        clean_title=clean_title,
        sub=sub,
        logo_url=logo_url,
        qr_url=qr_url,
        css_code=css_code,
        body_html=body_html
    )


def build_all_rich_pdfs():
    os.makedirs(PDF_DIR, exist_ok=True)

    with open(CSS_LAYOUT_PATH, "r", encoding="utf-8") as f:
        css_layout = f.read()
    with open(CSS_COMPONENTS_PATH, "r", encoding="utf-8") as f:
        css_components = f.read()
    with open(CSS_BRAND_PATH, "r", encoding="utf-8") as f:
        brand_css = f.read()

    # 增强页脚：每页底端自带淘宝店铺暗纹与沙盒引流
    css_layout = css_layout.replace(
        'content: "第 " counter(page) " 页 ｜ 王者荣耀全维度战术知识库 (附赠在线推演沙盒)";',
        'content: "第 " counter(page) " 页 ｜ 淘宝店铺：TING LAB ｜ 沙盒：wzry.aodilab.com";'
    )

    css_code = f"{css_layout}\n\n{css_components}\n\n{brand_css}"

    files = [
        ("01_王者荣耀_全英雄技能数值与等级成长库.md", "01_全英雄核心机制与技能数值全解.pdf", "技能数值 · 等级成长 · 加成系数", enrich_01_skills),
        ("02_王者荣耀_英雄战术克制与阵容搭档拓扑.md", "02_英雄战术克制关系与搭档谱系.pdf", "战术克制 · 阵容搭档 · BP推荐", enrich_02_counters),
        ("03_王者荣耀_五大分路定位与战术流派指南.md", "03_五大分路定位与战术流派指南.pdf", "分路打法 · 战术流派 · 节奏运营", enrich_03_builds),
        ("04_王者荣耀_全装备属性与合成升级图谱.md", "04_全装备属性效果与双向合成图谱.pdf", "装备属性 · 唯一被动 · 合成路径", enrich_04_items),
        ("05_王者荣耀_全铭文图鉴与英雄搭配方案.md", "05_五级铭文图鉴与主流流派搭配.pdf", "五级铭文 · 属性搭配 · 英雄实配", enrich_05_arcana),
        ("06_王者荣耀_峡谷战场机制与宏观运营规则.md", "06_峡谷底层机制与伤害防御算分.pdf", "防御抗性 · 经济野区 · 伤害计算", enrich_06_rules),
    ]

    print("🚀 启动 Playwright 高清印刷引擎 (已配置本地高权安全通道)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--allow-file-access-from-files", "--disable-web-security"]
        )
        page = browser.new_page()

        target_filter = sys.argv[1] if len(sys.argv) > 1 else None
        for md_name, pdf_name, sub, enrich_fn in files:
            if target_filter and target_filter not in pdf_name and target_filter not in md_name:
                continue
            md_path = os.path.join(OUTPUT_DIR, md_name)
            if not os.path.exists(md_path):
                continue

            with open(md_path, "r", encoding="utf-8") as f:
                raw_md = f.read()

            title = pdf_name.replace(".pdf", "").replace("_", " ")
            enriched_md = enrich_fn(raw_md)
            img_count = enriched_md.count("<img")
            body_html = markdown.markdown(enriched_md, extensions=["tables", "fenced_code"])
            html_code = render_html_page(title, sub, body_html, css_code)

            temp_html = os.path.join(PDF_DIR, f"temp_{pdf_name}.html")
            pdf_target = os.path.join(PDF_DIR, pdf_name)

            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_code)

            page.goto(f"file:///{temp_html.replace(os.sep, '/')}", wait_until="load")
            page.pdf(
                path=pdf_target,
                format="A4",
                print_background=True,
                margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"}
            )

            if os.path.exists(temp_html):
                os.remove(temp_html)

            # PyMuPDF 工业级无损流压缩，确保体积严格低于 Cloudflare 25MB 上限并加速下载
            try:
                import pymupdf
                doc = pymupdf.open(pdf_target)
                opt_tmp = pdf_target + ".opt.pdf"
                doc.save(opt_tmp, garbage=4, deflate=True)
                doc.close()
                if os.path.exists(opt_tmp):
                    os.replace(opt_tmp, pdf_target)
            except Exception as e:
                print(f"PyMuPDF 优化跳过: {e}")

            pdf_size_kb = os.path.getsize(pdf_target) / 1024
            print(f"✅ 生成全彩图文化 PDF: {pdf_name} ({pdf_size_kb:.1f} KB, 包含 {img_count} 个官方高清图标/头像)")

            dist_pdf_dir = os.path.join(PROJECT_ROOT, "dist_pages", "pdf")
            if os.path.exists(dist_pdf_dir):
                import shutil
                shutil.copy2(pdf_target, os.path.join(dist_pdf_dir, pdf_name))

        browser.close()


if __name__ == "__main__":
    build_all_rich_pdfs()
