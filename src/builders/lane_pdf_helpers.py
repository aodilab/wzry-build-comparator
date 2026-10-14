# -*- coding: utf-8 -*-
"""
王者荣耀 S45 五大分路主流英雄官方出装多维全解 - 出版级矢量 PDF 构建器
每套出装独占完整 1 页，无跨页折断，差异化分析双C、打野与辅助。
"""

import os
import sys
import re
import json
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.hero_registry import CN_HERO_MANIFEST
from src.core.build_analyzer import analyze_build

CACHE_DIR = os.path.join(PROJECT_ROOT, "taobao", "assets_cache").replace("\\", "/")
HERO_MAP = {data["cname"]: ename for ename, data in CN_HERO_MANIFEST.items()}
HERO_TITLES = {data["cname"]: data.get("title", "") for ename, data in CN_HERO_MANIFEST.items()}

with open(os.path.join(PROJECT_ROOT, "sandbox.html"), "r", encoding="utf-8") as f:
    sandbox_raw = f.read()

m_items = re.search(r'const ITEMS_DATA = (\[.*?\]);', sandbox_raw)
m_arcana = re.search(r'const ARCANA_DATA = (\{.*?\});', sandbox_raw)
ITEMS_LIST = json.loads(m_items.group(1)) if m_items else []
ITEM_MAP = {item["item_name"]: str(item["item_id"]) for item in ITEMS_LIST}

with open(os.path.join(PROJECT_ROOT, "config", "hero_arcana_data.py"), "r", encoding="utf-8") as f:
    arc_text = f.read()

ARCANA_MAP = {}
for m in re.finditer(r'"([^"]+)":\s*\{\'id\':\s*\'(\d+)\'', arc_text):
    ARCANA_MAP[m.group(1)] = m.group(2)

RED_ARCANA = {'圣人', '传承', '异变', '纷争', '无双', '宿命', '梦魇', '凶兆', '祸源', '红月'}
BLUE_ARCANA = {'长生', '贪婪', '夺萃', '兽痕', '冥想', '繁荣', '轮回', '调和', '隐匿', '狩猎'}
GREEN_ARCANA = {'霸者', '均衡', '虚空', '灵山', '献祭', '鹰眼', '心眼', '怜悯', '敬畏', '回声'}

HERO_AVATAR_ALIASES = {
    '敖隐': '519', '戈娅': '548', '弈星': '197',
    '少司缘': '577', '大司命': '517', '亚连': '548', '影': '586'
}


from config.lane_pdf_config import LANE_CONFIG, ITEM_ROLES, HERO_TACTICAL_DETAILS

def resolve_item_id(name: str):
    if name in ['贤者天书', '贤者之书']: return '1238'
    if name == '幽影袖箭': return '1161'
    if name in ITEM_MAP: return ITEM_MAP[name]
    for prefix in ['仁者', '强者', '王者', '不动·', '初级']:
        clean = name.replace(prefix, '')
        if clean in ITEM_MAP: return ITEM_MAP[clean]
    for iname, iid in ITEM_MAP.items():
        if iname in name or name in iname: return iid
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


def render_lane_scheme_page(
    lane_icon, lane_key, avatar_url, hero_cname, hero_title,
    idx, b_name, b_desc, items, items_row, arc_row, spec_cards_html, page_num
) -> str:
    # 装备逐件解析
    item_breakdown_html = []
    for it_name in items:
        it_icon = get_item_icon(it_name)
        it_role = ITEM_ROLES.get(it_name, "提供基础属性支撑与核心被动协同")
        img_tag = f'<img src="{it_icon}" class="it-mini-icon" alt="{it_name}">' if it_icon else ''
        item_breakdown_html.append(f"""
        <div class="item-role-cell">
            {img_tag}
            <div class="it-role-text">
                <span class="it-role-name">{it_name}</span>
                <span class="it-role-desc">{it_role}</span>
            </div>
        </div>
        """)
    item_breakdown_grid = "".join(item_breakdown_html)

    # 英雄战术细节 (技能加点/召唤师技能/连招细节)
    tactical = HERO_TACTICAL_DETAILS.get(hero_cname, {
        "skill_pri": "主升核心消耗技能，副升辅助位移，有大点大",
        "spells": "闪现 / 净化（根据敌方控制与突进灵活调整）",
        "combo_tip": "核心输出手法：利用短CD技能配合被动打满伤害，进场前注意观察敌方关键控制技能释放状态。"
    })

    page_html = f"""
    <div class="pdf-page scheme-page">
        <div class="watermark-pattern"></div>
        <div class="top-nav-bar">
            <span class="nav-brand">TING LAB ｜ S45 实战出装多维全解</span>
            <span class="nav-lane">{lane_icon} {lane_key}路专卷</span>
        </div>

        <div class="hero-header-card">
            <img src="{avatar_url}" class="hero-avatar" alt="{hero_cname}">
            <div class="hero-title-box">
                <div class="hero-name-row">
                    <span class="hero-name">{hero_cname}</span>
                    <span class="hero-title-tag">{hero_title}</span>
                </div>
                <div class="scheme-name-badge">方案 {idx + 1}：{b_name}</div>
            </div>
        </div>

        <div class="section-card">
            <div class="card-section-title">核心神装拓扑与五级铭文</div>
            <div class="eq-flow-row">
                {items_row}
            </div>
            <div class="arcana-row">
                <span class="arc-title">专属铭文搭配：</span>
                {arc_row}
            </div>
        </div>

        <div class="section-card">
            <div class="card-section-title">网站推演台 · 多维度满级物理数据看板</div>
            {spec_cards_html}
        </div>

        <div class="section-card">
            <div class="card-section-title">六神装逐件定位与实战收益拆解</div>
            <div class="item-roles-grid">
                {item_breakdown_grid}
            </div>
        </div>

        <div class="section-card analysis-card">
            <div class="card-section-title">战术操作细节与机制详解</div>
            <div class="tactical-row">
                <div class="tactical-col">
                    <span class="tactical-label">🎯 技能加点：</span>
                    <span class="tactical-val">{tactical['skill_pri']}</span>
                </div>
                <div class="tactical-col">
                    <span class="tactical-label">⚡ 召唤师技能：</span>
                    <span class="tactical-val">{tactical['spells']}</span>
                </div>
            </div>
            <div class="analysis-item" style="margin-top:6px;">
                <span class="analysis-dot blue"></span>
                <div class="analysis-content">
                    <strong>官方思路解析：</strong>{b_desc}
                </div>
            </div>
            <div class="analysis-item">
                <span class="analysis-dot green"></span>
                <div class="analysis-content">
                    <strong>核心机制要点：</strong>{tactical['combo_tip']}
                </div>
            </div>
            <div class="analysis-item">
                <span class="analysis-dot orange"></span>
                <div class="analysis-content">
                    <strong>后期神装轮换顺序：</strong>名刀·司命 ➔ 贤者的庇护（复活甲）➔ 极寒/天穹，经济溢出时秒换保命装。
                </div>
            </div>
        </div>

        <div class="page-footer">
            <span>第 {page_num} 页 ｜ 💡 自由换装与双轨实时对决请访问王者推演沙盒：wzry.aodilab.com</span>
        </div>
    </div>
    """
    return page_html
