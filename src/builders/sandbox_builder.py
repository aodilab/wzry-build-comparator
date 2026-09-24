# -*- coding: utf-8 -*-
"""
王者荣耀局内配装沙盒网页生成器 (Web UI Sandbox Builder)
从 config/sandbox_template.py 载入模板，将官方清洗后的全英雄与装备数据编译为单文件 sandbox.html
"""
import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import URL_ITEM_LIST, ROLE_MAP, LANE_MAP
from config.item_recipes import COMPONENTS_MAP
from config.hero_base_stats import get_hero_base_stats
from config.hero_arcana_data import ARCANA_LEVEL_5_DICT, HERO_RECOMMENDED_ARCANA
from config.hero_skills_data import HERO_SKILLS_DATA
from config.hero_official_builds import OFFICIAL_HERO_BUILDS
from config.patches import REWORKED_HERO_SKILLS_PATCHES
from config.sandbox_template import SANDBOX_HTML_TEMPLATE
from src.core.http import fetch_json
from src.core.hero_validator import get_validated_hero_list
from src.core.item_calculator import parse_single_item_stats, BOOTS_SPEED_MAP, ACTIVE_SKILL_ITEMS, JUNGLE_ITEMS

def build_sandbox_html(output_file=None):
    """
    编译生成单文件 sandbox.html
    """
    print("正在加载王者荣耀官方全英雄与全装备数据集...")
    raw_items = fetch_json(URL_ITEM_LIST)
    heroes = get_validated_hero_list()

    # 1. 结构化装备库 (官方公开接口全量 121 件装备，均具备官方高清透明PNG图标)
    processed_items = []
    for it in raw_items:
        iid = it.get("item_id")
        stats = parse_single_item_stats(it)
        cat = "攻击装备"
        t = it.get("item_type", 1)
        if t == 2: cat = "法术装备"
        elif t == 3: cat = "防御装备"
        elif t == 4: cat = "移动装备"
        elif t == 5: cat = "打野装备"
        elif t == 6 or t == 7: cat = "游走装备"

        # 提取结构化属性行与唯一被动
        raw_des1 = it.get("des1", "") or ""
        raw_des2 = it.get("des2", "") or ""
        des1_lines = [re.sub(r'</?[^>]+>', '', line).strip() for line in re.split(r'<br\s*/?>|</?p>', raw_des1) if re.sub(r'</?[^>]+>', '', line).strip()]
        des2_lines = [re.sub(r'</?[^>]+>', '', line).strip() for line in re.split(r'<br\s*/?>|</?p>', raw_des2) if re.sub(r'</?[^>]+>', '', line).strip()]

        clean_name = stats.get("name", it.get("item_name"))
        processed_items.append({
            "item_id": iid,
            "item_name": clean_name,
            "category": cat,
            "total_price": it.get("total_price", 0),
            "des1": " ".join(des1_lines),
            "des2": " ".join(des2_lines),
            "des1_lines": des1_lines,
            "des2_lines": des2_lines,
            "stats": stats
        })

    # 2. 结构化英雄库并注入官方推荐铭文套组
    processed_heroes = []
    for h in heroes:
        ename = str(h.get("ename"))
        cname = h.get("cname")
        title = h.get("title", "")
        r1 = h.get("hero_type")
        r2 = h.get("hero_type2")
        roles = []
        if r1 in ROLE_MAP: roles.append(ROLE_MAP[r1])
        if r2 in ROLE_MAP and ROLE_MAP[r2] not in roles: roles.append(ROLE_MAP[r2])
        role_str = "/".join(roles) if roles else "战士"
        lane = LANE_MAP.get(roles[0] if roles else "战士", "对抗路")
        base = get_hero_base_stats(ename, cname, role_str)
        rec_arcana = HERO_RECOMMENDED_ARCANA.get(cname, {"red": "异变", "green": "鹰眼", "blue": "隐匿"})

        processed_heroes.append({
            "ename": ename,
            "cname": cname,
            "title": title,
            "role": role_str,
            "lane": lane,
            "base_stats": base,
            "recommended_arcana": rec_arcana
        })

    # 3. 渲染单文件 HTML (贯彻单一数据源 SSOT，优先合并权威受控技能补丁)
    unified_skills_data = dict(HERO_SKILLS_DATA)
    for hero_name, patch in REWORKED_HERO_SKILLS_PATCHES.items():
        if "skills" in patch:
            unified_skills_data[hero_name] = patch["skills"]

    html_content = SANDBOX_HTML_TEMPLATE
    html_content = html_content.replace("__HEROES_DATA_PLACEHOLDER__", json.dumps(processed_heroes, ensure_ascii=False))
    html_content = html_content.replace("__HERO_SKILLS_DATA_PLACEHOLDER__", json.dumps(unified_skills_data, ensure_ascii=False))
    html_content = html_content.replace("__ITEMS_DATA_PLACEHOLDER__", json.dumps(processed_items, ensure_ascii=False))
    html_content = html_content.replace("__ARCANA_DATA_PLACEHOLDER__", json.dumps(ARCANA_LEVEL_5_DICT, ensure_ascii=False))
    html_content = html_content.replace("__RECIPES_MAP_PLACEHOLDER__", json.dumps(COMPONENTS_MAP, ensure_ascii=False))
    html_content = html_content.replace("__BOOTS_MAP_PLACEHOLDER__", json.dumps(BOOTS_SPEED_MAP, ensure_ascii=False))
    html_content = html_content.replace("__ACTIVE_ITEMS_PLACEHOLDER__", json.dumps(ACTIVE_SKILL_ITEMS, ensure_ascii=False))
    html_content = html_content.replace("__JUNGLE_ITEMS_PLACEHOLDER__", json.dumps(JUNGLE_ITEMS, ensure_ascii=False))
    html_content = html_content.replace("__OFFICIAL_HERO_BUILDS_PLACEHOLDER__", json.dumps(OFFICIAL_HERO_BUILDS, ensure_ascii=False))

    target = output_file or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sandbox.html")
    with open(target, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 同步输出一份到 index.html，供 GitHub Pages 直接在线托管
    index_target = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "index.html")
    with open(index_target, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 同步输出一份到 dist_pages/index.html，供 Cloudflare Pages 全球托管
    dist_target = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "dist_pages", "index.html")
    if os.path.exists(os.path.dirname(dist_target)):
        with open(dist_target, "w", encoding="utf-8") as f:
            f.write(html_content)

    print(f"【成功】王者荣耀六神装配装沙盒单文件已生成：'{target}'、'{index_target}' 与 '{dist_target}'（包含 30 颗全量五级铭文库与全英雄推荐铭文）")
    return target

if __name__ == "__main__":
    build_sandbox_html()
