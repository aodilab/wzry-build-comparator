"""
PDF 图文并茂升级版构建器 (全面内嵌英雄高清头像、装备图标、铭文图鉴、技能图标)
对标 Apple 出版物排版，纯前端/本地缓存极速渲染
"""

import os
import sys
import re
import json
import markdown
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.hero_registry import CN_HERO_MANIFEST

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
PDF_DIR = os.path.join(PROJECT_ROOT, "taobao", "pdf")
CACHE_DIR = os.path.join(PROJECT_ROOT, "taobao", "assets_cache").replace("\\", "/")
CSS_LAYOUT_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_layout.css")
CSS_COMPONENTS_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_components.css")

# 1. 基础数据字典
HERO_MAP = {data["cname"]: ename for ename, data in CN_HERO_MANIFEST.items()}

with open(os.path.join(PROJECT_ROOT, "sandbox.html"), "r", encoding="utf-8") as f:
    sandbox_raw = f.read()

m_items = re.search(r'const ITEMS_DATA = (\[.*?\]);', sandbox_raw)
m_arcana = re.search(r'const ARCANA_DATA = (\{.*?\});', sandbox_raw)

ITEMS_LIST = json.loads(m_items.group(1)) if m_items else []
ARCANA_DICT = json.loads(m_arcana.group(1)) if m_arcana else {}

ITEM_MAP = {item["item_name"]: str(item["item_id"]) for item in ITEMS_LIST}
ARCANA_MAP = {name: str(data["id"]) for name, data in ARCANA_DICT.items()}


def get_hero_avatar(ename: str) -> str:
    local_p = f"{CACHE_DIR}/hero/{ename}.jpg"
    return f"file:///{local_p}" if os.path.exists(local_p) else f"https://game.gtimg.cn/images/yxzj/img201606/heroimg/{ename}/{ename}.jpg"


def get_skill_icon(ename: str, suffix: str) -> str:
    local_p = f"{CACHE_DIR}/skill/{ename}{suffix}.png"
    return f"file:///{local_p}" if os.path.exists(local_p) else ""


def get_item_icon(iid: str) -> str:
    local_p = f"{CACHE_DIR}/item/{iid}.png"
    return f"file:///{local_p}" if os.path.exists(local_p) else f"https://game.gtimg.cn/images/yxzj/img201606/itemimgo/{iid}.png"


def get_arcana_icon(aid: str) -> str:
    local_p = f"{CACHE_DIR}/arcana/{aid}.png"
    return f"file:///{local_p}" if os.path.exists(local_p) else f"https://game.gtimg.cn/images/yxzj/img201606/mingwen/{aid}.png"


def enrich_01_skills(md_text: str) -> str:
    lines = md_text.split("\n")
    new_lines = []
    current_ename = ""
    for line in lines:
        m_hero = re.match(r'^##\s+英雄：([^\s（]+)（([^）]+)）', line)
        if m_hero:
            cname, title = m_hero.group(1), m_hero.group(2)
            current_ename = HERO_MAP.get(cname, "")
            avatar = get_hero_avatar(current_ename) if current_ename else ""
            new_lines.append(f'<div class="hero-card-header"><img src="{avatar}" class="hero-avatar-round"><div class="hero-header-text"><span class="hero-name-big">{cname}</span><span class="hero-title-badge">{title}</span></div></div>\n')
            continue

        m_skill = re.match(r'^####\s+(被动技能|主动技能\s*\d+)：(.*)', line)
        if m_skill and current_ename:
            stype, sname = m_skill.group(1).replace(" ", ""), m_skill.group(2).strip()
            if not sname and "4" in stype:
                continue
            suffix = "00" if "被动" in stype else ("10" if "1" in stype else ("20" if "2" in stype else ("30" if "3" in stype else "40")))
            icon_url = get_skill_icon(current_ename, suffix)
            tag_name = "被动" if "被动" in stype else ("一技能" if "1" in stype else ("二技能" if "2" in stype else ("三技能" if "3" in stype else "四技能")))
            img_tag = f'<img src="{icon_url}" class="skill-icon-round">' if icon_url else ''
            new_lines.append(f'<div class="skill-banner">{img_tag}<span class="skill-tag">{tag_name}</span><span class="skill-name">{sname or tag_name}</span></div>\n')
            continue

        new_lines.append(line)
    return "\n".join(new_lines)


def enrich_02_counters(md_text: str) -> str:
    lines = md_text.split("\n")
    new_lines = []
    for line in lines:
        m_hero = re.match(r'^##\s+英雄：([^\s（]+)（([^）]+)）', line)
        if m_hero:
            cname, title = m_hero.group(1), m_hero.group(2)
            ename = HERO_MAP.get(cname, "")
            avatar = get_hero_avatar(ename) if ename else ""
            new_lines.append(f'<div class="hero-card-header"><img src="{avatar}" class="hero-avatar-round"><div class="hero-header-text"><span class="hero-name-big">{cname}</span><span class="hero-title-badge">{title}</span></div></div>\n')
            continue

        m_partner = re.match(r'^-\s+\*\*([^\*]+)\*\*：(.*)', line)
        if m_partner:
            pname, desc = m_partner.group(1), m_partner.group(2)
            if pname in HERO_MAP:
                p_ename = HERO_MAP[pname]
                p_avatar = get_hero_avatar(p_ename)
                new_lines.append(f'<div class="matchup-row"><img src="{p_avatar}" class="matchup-avatar"><div class="matchup-content"><strong class="matchup-name">{pname}</strong>：{desc}</div></div>\n')
                continue
        new_lines.append(line)
    return "\n".join(new_lines)


def enrich_03_builds(md_text: str) -> str:
    lines = md_text.split("\n")
    new_lines = []
    for line in lines:
        m_lane = re.match(r'^##\s+【峡谷分路：(.*?)】', line)
        if m_lane:
            lane_name = m_lane.group(1)
            banner = (
                f'<div class="lane-verify-banner">'
                f'<span class="lane-verify-tag">{lane_name}推演</span>'
                f'<span>{lane_name}英雄承伤免伤率、爆发斩杀线与边际效应，已接入「王者出装箱」推演系统（'
                f'<a href="https://wzry.aodilab.com" target="_blank">wzry.aodilab.com</a>），支持自由更换装备及铭文进行实时验算。</span>'
                f'</div>'
            )
            new_lines.append(f'## 【峡谷分路：{lane_name}】\n\n{banner}\n')
            continue

        m_hero = re.match(r'^###\s+英雄：([^\s（]+)（([^）]+)）', line)
        if m_hero:
            cname, title = m_hero.group(1), m_hero.group(2)
            ename = HERO_MAP.get(cname, "")
            avatar = get_hero_avatar(ename) if ename else ""
            new_lines.append(f'<div class="hero-card-header"><img src="{avatar}" class="hero-avatar-round"><div class="hero-header-text"><span class="hero-name-big">{cname}</span><span class="hero-title-badge">{title}</span></div></div>\n')
            continue

        m_order = re.match(r'^(?:-\s+\*\*推荐购买顺序路径\*\*：)(.*)', line)
        if m_order:
            items_raw = m_order.group(1).split("->")
            chips = []
            for ir in items_raw:
                it = ir.strip()
                if it in ITEM_MAP:
                    icon = get_item_icon(ITEM_MAP[it])
                    chips.append(f'<span class="item-chip"><img src="{icon}">{it}</span>')
                else:
                    chips.append(f'<span>{it}</span>')
            arrow = ' <span class="path-arrow">➜</span> '
            new_lines.append(f'- **推荐购买顺序路径**：{arrow.join(chips)}\n')
            continue

        m_six = re.match(r'^(?:-\s+\*\*【最终生效 6 件成装 \(严格排除已消耗小件\)】\*\*：)(.*)', line)
        if m_six:
            items_raw = m_six.group(1).split("+")
            chips = []
            for ir in items_raw:
                it = ir.strip()
                if it in ITEM_MAP:
                    icon = get_item_icon(ITEM_MAP[it])
                    chips.append(f'<span class="item-chip gold"><img src="{icon}"><strong>{it}</strong></span>')
                else:
                    chips.append(f'<span>{it}</span>')
            plus = '<span class="plus-sign">✚</span>'
            badge_html = '<a class="sandbox-verify-badge" href="https://wzry.aodilab.com" target="_blank">🔍 沙盒实时验算 ↗</a>'
            items_joined = f" {plus} ".join(chips)
            new_lines.append(f'<div class="build-slot-line"><span class="build-slot-label">【最终生效 6 件成装】：</span><span class="build-slot-items">{items_joined}</span>{badge_html}</div>\n')
            continue

        new_lines.append(line)
    return "\n".join(new_lines)


def enrich_04_items(md_text: str) -> str:
    lines = md_text.split("\n")
    new_lines = []
    for line in lines:
        m_item = re.match(r'^####\s+装备名称：(.*)', line)
        if m_item:
            iname = m_item.group(1).strip()
            if iname in ITEM_MAP:
                icon = get_item_icon(ITEM_MAP[iname])
                new_lines.append(f'<div class="item-card-header"><img src="{icon}" class="item-avatar-large"><span class="item-name-big">{iname}</span></div>\n')
                continue

        m_tree = re.match(r'^(?:-\s+\*\*【(?:合成配方|升级方向)】.*?\*\*：)(.*)', line)
        if m_tree:
            raw_list = m_tree.group(1)
            for iname, iid in ITEM_MAP.items():
                if len(iname) >= 2 and iname in raw_list:
                    icon = get_item_icon(iid)
                    raw_list = re.sub(rf'(?<!>)({re.escape(iname)})(?!<)', f'<span class="item-chip"><img src="{icon}">\\1</span>', raw_list)
            prefix = line.split("：")[0] + "："
            new_lines.append(f"{prefix}{raw_list}\n")
            continue

        new_lines.append(line)
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
    logo_url = f"file:///{CACHE_DIR}/ting_lab_logo.png"
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
        ("03_王者荣耀_五大分路定位与实战出装思路.md", "03_五大分路定位与实战核心出装.pdf", "分路打法 · 核心出装 · 装备替换", enrich_03_builds),
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

        for md_name, pdf_name, sub, enrich_fn in files:
            md_path = os.path.join(OUTPUT_DIR, md_name)
            if not os.path.exists(md_path):
                continue

            with open(md_path, "r", encoding="utf-8") as f:
                raw_md = f.read()

            title = md_name.replace(".md", "").replace("王者荣耀_", "")
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

            pdf_size_kb = os.path.getsize(pdf_target) / 1024
            print(f"✅ 生成全彩图文化 PDF: {pdf_name} ({pdf_size_kb:.1f} KB, 包含 {img_count} 个官方高清图标/头像)")

        browser.close()


if __name__ == "__main__":
    build_all_rich_pdfs()
