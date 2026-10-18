# -*- coding: utf-8 -*-
"""
王者荣耀五大分路定位与实战出装思路数据库构建器
按对抗路、打野、中路、发育路、游走五大分路组织出装方案
严格排除被吞噬的小件，精准计算最终 6 神装净增幅与 15 级终极面板
100% 对齐 S45 真机实测出装与绑定的官方铭文方案，彻底剔除旧版官网爬虫数据
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import OUTPUT_DIR, DOC_HERO_BUILDS_NAME, ROLE_MAP
from config.hero_registry import CN_HERO_MANIFEST
from config.hero_base_stats import get_hero_base_stats
try:
    from config.hero_official_builds import OFFICIAL_HERO_BUILDS
except (ImportError, ModuleNotFoundError, Exception):
    OFFICIAL_HERO_BUILDS = {}

from src.core.http import fetch_json
from src.core.item_calculator import calculate_build_stats

LANE_MAPPING = {
    "对抗": "对抗路",
    "打野": "打野",
    "中路": "中路",
    "发育": "发育路",
    "游走": "游走"
}

def get_equip_maps():
    """获取装备映射表"""
    cache_item = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                              ".cache", "json", "a6cd7ea78d2dfc098426715c83bbaadc.json")
    if os.path.exists(cache_item):
        with open(cache_item, "r", encoding="utf-8") as f:
            items = json.load(f)
    else:
        items = fetch_json("https://pvp.qq.com/web201605/js/item.json")
    return {item["item_name"]: item for item in items}

def build_hero_builds(output_file=None, *args, **kwargs):
    """构建五大分路定位与实战出装思路数据库 (S45 官方基准 SSOT)"""
    equip_name_map = get_equip_maps()
    hero_meta = {}
    for eid, d in CN_HERO_MANIFEST.items():
        cname = d["cname"]
        roles = []
        r1 = d.get("hero_type")
        r2 = d.get("hero_type2")
        if r1 in ROLE_MAP:
            roles.append(ROLE_MAP[r1])
        if r2 in ROLE_MAP and ROLE_MAP[r2] not in roles:
            roles.append(ROLE_MAP[r2])
        role_str = "/".join(roles) if roles else "战士"
        hero_meta[cname] = {
            "ename": str(eid),
            "title": d.get("title", ""),
            "role": role_str
        }

    # 按五大分路聚合
    lane_heroes = {
        "对抗路": [],
        "打野": [],
        "中路": [],
        "发育路": [],
        "游走": []
    }

    for cname, hdata in OFFICIAL_HERO_BUILDS.items():
        meta = hero_meta.get(cname, {"ename": "0", "title": "", "role": "战士"})
        hero_base = get_hero_base_stats(meta["ename"], cname, meta["role"])

        for l_key, blist in hdata.get("lanes", {}).items():
            full_lane = LANE_MAPPING.get(l_key, l_key)
            if full_lane not in lane_heroes:
                continue

            hero_schemes = []
            for b in blist:
                calc_res = calculate_build_stats(b.get("items", []), equip_name_map, hero_base)
                hero_schemes.append({
                    "title": b.get("title", "官方推荐"),
                    "desc": b.get("desc", ""),
                    "items": b.get("items", []),
                    "arcana_desc": b.get("arcana_desc", ""),
                    "calc": calc_res
                })

            if hero_schemes:
                lane_heroes[full_lane].append({
                    "cname": cname,
                    "title": meta["title"],
                    "role": meta["role"],
                    "schemes": hero_schemes
                })

    # 生成 Markdown 知识库（公开版脱敏：仅输出战术流派与打法思路，不暴露507套原始六神装底库）
    markdown_content = "# 王者荣耀 S45 赛季（月照长安）五大分路定位与战术流派指南\n\n"
    markdown_content += "> 📌 **分路战术定位基准 (Tactical Framework)**：\n"
    markdown_content += "> - **分路覆盖**：按国服五大实战分路【对抗路、打野、中路、发育路、游走】全景收录 133 位英雄实战职能与战术流派演进。\n"
    markdown_content += "> - **实战思维**：深度提炼各战术流派的核心攻防打法、切入时机与团队协同要点，建立高阶竞技大局观。\n"
    markdown_content += "> - **沙盒动态验算**：各流派的具体六神装购买序列、满配属性面板与实战斩杀线已全面接入「王者推演沙盒」（[wzry.aodilab.com](https://wzry.aodilab.com)），支持结合局内敌我阵容实时演算。\n\n"
    markdown_content += "---\n\n"

    for lane_name in ["对抗路", "打野", "中路", "发育路", "游走"]:
        h_list = lane_heroes[lane_name]
        markdown_content += f"## 【峡谷分路：{lane_name}】\n\n"
        for h in h_list:
            title_suffix = f"（{h['title']}）" if h['title'] else ""
            markdown_content += f"### 英雄：{h['cname']}{title_suffix}\n"
            markdown_content += f"- **常规推荐分路**：{lane_name}（定位：{h['role']}）\n\n"

            for idx, s in enumerate(h["schemes"]):
                markdown_content += f"#### 🛡️ 【{lane_name}】战术方案{idx + 1}：【{s['title']}】\n"
                if s.get("desc"):
                    markdown_content += f"- **核心打法思路**：{s['desc']}\n"
                markdown_content += "- **神装推演与实操验算**：此方案完整购买顺序、六神装满配面板与实战斩杀线已接入「王者出装推演沙盒」（[wzry.aodilab.com](https://wzry.aodilab.com)），支持结合局内敌我阵容实时模拟。\n\n"

            markdown_content += "---\n\n"

    if not output_file:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, DOC_HERO_BUILDS_NAME)
    else:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"【成功】五大分路定位与实战出装思路库已生成：'{output_file}'")
    return output_file

if __name__ == "__main__":
    build_hero_builds()
