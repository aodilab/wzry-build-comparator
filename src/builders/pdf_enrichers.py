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
    i = 0
    role_icons = {
        '法师': ('🔮', 'MAGE'), '战士': ('⚔️', 'WARRIOR'),
        '坦克': ('🛡️', 'TANK'), '刺客': ('⚡', 'ASSASSIN'),
        '射手': ('🏹', 'MARKSMAN'), '辅助': ('🌿', 'SUPPORT')
    }

    while i < len(lines):
        line = lines[i]

        # 1. 职业分界横幅
        m_role = re.match(r'^#\s+={3,}\s+【职业领域：(.*?)】\s+={3,}', line)
        if m_role:
            role = m_role.group(1).strip()
            icon, en = role_icons.get(role, ('⭐', 'HERO'))
            banner = (
                f'<div class="role-division-banner">\n'
                f'<div class="role-banner-left"><span class="role-banner-icon">{icon}</span><span class="role-banner-title">{role}领域 · {en} DOMAIN</span></div>\n'
                f'<span class="role-banner-sub">S45 国服正式服微观成长数值</span>\n'
                f'</div>\n'
            )
            new_lines.append(banner)
            i += 1
            continue

        # 2. 英雄头像与名称
        m_hero = re.match(r'^##\s+英雄：([^\s（]+)（([^）]+)）', line)
        if m_hero:
            cname, title = m_hero.group(1), m_hero.group(2)
            current_ename = HERO_MAP.get(cname, "")
            avatar = get_hero_avatar(current_ename) if current_ename else ""
            new_lines.append(f'<div class="hero-card-header"><img src="{avatar}" class="hero-avatar-round"><div class="hero-header-text"><span class="hero-name-big">{cname}</span><span class="hero-title-badge">{title}</span></div></div>\n')
            i += 1
            continue

        # 3. 基础属性 6 宫格面板
        if line.startswith("### 【英雄核心基础属性面板"):
            stats_raw = {}
            i += 1
            while i < len(lines) and lines[i].startswith("- **"):
                l = lines[i]
                if "生命值" in l: stats_raw['hp'] = l.split("：")[-1].strip()
                elif "物理攻击力" in l: stats_raw['ad'] = l.split("：")[-1].strip()
                elif "物理防御力" in l: stats_raw['def'] = l.split("：")[-1].strip()
                elif "法术防御力" in l: stats_raw['mdef'] = l.split("：")[-1].strip()
                elif "移动速度" in l: stats_raw['spd'] = l.split("：")[-1].strip()
                elif "攻击速度" in l: stats_raw['as'] = l.split("：")[-1].strip()
                i += 1

            def parse_stat(raw, fallback_growth=""):
                if not raw: return ("--", fallback_growth)
                m = re.match(r'^([^\s\(]+)(?:\s*\((.*?)\))?', raw)
                if m:
                    val = m.group(1)
                    growth = m.group(2) or fallback_growth
                    return (val, growth)
                return (raw, fallback_growth)

            hp_val, hp_grow = parse_stat(stats_raw.get('hp', ''), '满级 6000+')
            ad_val, ad_grow = parse_stat(stats_raw.get('ad', ''), '满级 300+')
            def_val, def_grow = parse_stat(stats_raw.get('def', ''), '满级 300+')
            mdef_val, mdef_grow = parse_stat(stats_raw.get('mdef', ''), '满级 169')
            spd_val, _ = parse_stat(stats_raw.get('spd', '360'), '基础移速')
            as_val = stats_raw.get('as', '+1.0%/级')

            grid_html = (
                f'<div class="hero-stats-matrix">\n'
                f'<div class="stat-card"><span class="stat-k">最大生命</span><span class="stat-v">{hp_val}</span><span class="stat-growth">{hp_grow}</span></div>\n'
                f'<div class="stat-card"><span class="stat-k">物理攻击</span><span class="stat-v">{ad_val}</span><span class="stat-growth">{ad_grow}</span></div>\n'
                f'<div class="stat-card"><span class="stat-k">物理防御</span><span class="stat-v">{def_val}</span><span class="stat-growth">{def_grow}</span></div>\n'
                f'<div class="stat-card"><span class="stat-k">法术防御</span><span class="stat-v">{mdef_val}</span><span class="stat-growth">{mdef_grow}</span></div>\n'
                f'<div class="stat-card"><span class="stat-k">移动速度</span><span class="stat-v">{spd_val}</span><span class="stat-growth">常态跑图</span></div>\n'
                f'<div class="stat-card"><span class="stat-k">攻速成长</span><span class="stat-v">{as_val}</span><span class="stat-growth">每级固定增益</span></div>\n'
                f'</div>\n'
            )
            new_lines.append(grid_html)
            continue

        # 4. 技能模块卡片
        m_skill = re.match(r'^####\s+(被动技能|主动技能\s*\d+)：(.*)', line)
        if m_skill and current_ename:
            stype, sname = m_skill.group(1).replace(" ", ""), m_skill.group(2).strip()
            suffix = "00" if "被动" in stype else ("10" if "1" in stype else ("20" if "2" in stype else ("30" if "3" in stype else "40")))
            tag_name = "被动" if "被动" in stype else ("一技能" if "1" in stype else ("二技能" if "2" in stype else ("三技能" if "3" in stype else "四技能")))

            i += 1
            cd_val, cost_val, growth_val, desc_val = "", "", "", ""
            while i < len(lines) and lines[i].startswith("- **"):
                sl = lines[i]
                if "冷却时间" in sl: cd_val = sl.split("：")[-1].strip()
                elif "消耗" in sl: cost_val = sl.split("：")[-1].strip()
                elif "技能数值等级成长线" in sl: growth_val = sl.split("：")[-1].strip()
                elif "技能完整机制" in sl: desc_val = sl.split("：")[-1].strip()
                i += 1

            if not sname and not desc_val and "4" in stype:
                continue

            icon_url = get_skill_icon(current_ename, suffix)
            img_tag = f'<img src="{icon_url}" class="skill-icon-round">' if icon_url else ''

            pills_html = []
            if cd_val and "无冷却" not in cd_val: pills_html.append(f'<span class="skill-meta-pill">⏱️ CD: {cd_val}</span>')
            elif cd_val: pills_html.append(f'<span class="skill-meta-pill">⏱️ {cd_val}</span>')
            if cost_val and "无消耗" not in cost_val: pills_html.append(f'<span class="skill-meta-pill">💧 消耗: {cost_val}</span>')
            pills_joined = "".join(pills_html)

            growth_html = f'<div class="skill-growth-line"><span class="growth-lbl">📈 数值成长</span><code>{growth_val}</code></div>' if growth_val else ''

            card_html = (
                f'<div class="skill-module-card">\n'
                f'<div class="skill-banner-row">\n'
                f'<div class="skill-banner-left">{img_tag}<span class="skill-tag">{tag_name}</span><span class="skill-name">{sname or tag_name}</span></div>\n'
                f'<div class="skill-meta-pills">{pills_joined}</div>\n'
                f'</div>\n'
                f'{growth_html}\n'
                f'<div class="skill-desc-box">{desc_val}</div>\n'
                f'</div>\n'
            )
            new_lines.append(card_html)
            continue

        if "官方实战技巧" in line or line.startswith("### 【技能机制与各等级数值阶梯】") or line.startswith("- **职业定位**："):
            i += 1
            continue

        new_lines.append(line)
        i += 1

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
    i = 0
    while i < len(lines):
        line = lines[i]
        m_lane = re.match(r'^##\s+【峡谷分路：(.*?)】', line)
        if m_lane:
            lane_name = m_lane.group(1)
            banner = (
                f'<div class="lane-verify-banner">'
                f'<span class="lane-verify-tag">{lane_name}核心战术</span>'
                f'<span>{lane_name}英雄战术定位、流派打法与攻防节奏。成套神装购买序列、六神装满配面板与实战斩杀线已全面接入「王者推演沙盒」（'
                f'<a href="https://wzry.aodilab.com" target="_blank">wzry.aodilab.com</a>），支持结合对局阵容实时验算。</span>'
                f'</div>'
            )
            new_lines.append(f'## 【峡谷分路：{lane_name}】\n\n{banner}\n')
            i += 1
            continue

        m_hero = re.match(r'^###\s+英雄：([^\s（]+)（([^）]+)）', line)
        if m_hero:
            cname, title = m_hero.group(1), m_hero.group(2)
            ename = HERO_MAP.get(cname, "")
            avatar = get_hero_avatar(ename) if ename else ""
            new_lines.append(f'<div class="hero-card-header"><img src="{avatar}" class="hero-avatar-round"><div class="hero-header-text"><span class="hero-name-big">{cname}</span><span class="hero-title-badge">{title}</span></div></div>\n')
            i += 1
            continue

        # Match scheme headers: #### 🛡️ 【对抗路】战术方案1：【半肉流】
        m_scheme = re.match(r'^####\s*([^\s]+)\s*【(.*?)】战术方案(\d+)[：:]\s*【(.*?)】', line)
        if m_scheme:
            icon, lane, idx, style = m_scheme.group(1), m_scheme.group(2), m_scheme.group(3), m_scheme.group(4)
            i += 1
            reason = ""
            while i < len(lines) and not lines[i].startswith(('####', '###', '##', '---')):
                subline = lines[i]
                if "核心打法思路" in subline:
                    m_r = re.search(r'[:：]\s*(.*?)$', subline)
                    if m_r: reason = m_r.group(1).strip()
                i += 1
            if not reason:
                reason = f"契合{lane}对线节奏与团战需求，注重攻防节奏平衡。"

            card_html = (
                f'<div class="tactical-scheme-card">\n'
                f'<div class="tactical-scheme-header">{icon} <strong>{lane}战术方案 {idx} · {style}</strong></div>\n'
                f'<div class="tactical-scheme-body">\n'
                f'<div class="tactical-reason"><strong>🎯 核心打法思路：</strong>{reason}</div>\n'
                f'<div class="tactical-sandbox-cta">\n'
                f'<span>⚡ 实时神装购买序列、六神装满配属性与实操斩杀线已接入 <strong>在线推演沙盒</strong></span>\n'
                f'<a href="https://wzry.aodilab.com" target="_blank" class="sandbox-verify-badge">前往沙盒验算 ↗</a>\n'
                f'</div>\n'
                f'</div>\n'
                f'</div>\n'
            )
            new_lines.append(card_html)
            continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)



