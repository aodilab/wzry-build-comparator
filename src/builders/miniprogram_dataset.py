# -*- coding: utf-8 -*-
"""
微信小程序全量离线数据集构建器 (Dataset Builder for WeChat Mini Program & Preview)
单一职责：清洗装备、英雄、铭文、技能与官方出装并输出 dataset.js / dataset_preview.js。
"""
import json
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.hero_arcana_data import ARCANA_LEVEL_5_DICT, HERO_RECOMMENDED_ARCANA
from config.hero_base_stats import get_hero_base_stats
from config.hero_combos import get_all_combos
from config.hero_official_builds import OFFICIAL_HERO_BUILDS
from config.hero_registry import CN_HERO_MANIFEST
from config.hero_skills_data import HERO_SKILLS_DATA
from config.item_recipes import COMPONENTS_MAP
from config.patches import REWORKED_HERO_SKILLS_PATCHES
from config.patches.hero_builds_patch import HERO_BUILDS_PATCHES
from config.settings import ROLE_MAP, URL_ITEM_LIST
from src.core.hero_validator import get_validated_hero_list
from src.core.http import fetch_json
from src.core.item_calculator import (
    ACTIVE_SKILL_ITEMS,
    BOOTS_SPEED_MAP,
    JUNGLE_ITEMS,
    parse_single_item_stats,
)

INVALID_ITEM_IDS = set()

WUXIANG_OVERRIDES = {
    22026: ("防御", "无象神器(坦克/坦辅)"),
    22027: ("攻击", "无象神器(战士)"),
    22028: ("攻击", "无象神器(刺客)"),
    22029: ("法术", "无象神器(法师)"),
    22030: ("攻击", "无象神器(射手)"),
    22031: ("游走", "无象神器(法辅)"),
}

ITEM_TYPE_CAT = {1: "攻击", 2: "法术", 3: "防御", 4: "移动", 5: "打野", 7: "游走"}


def _build_processed_items(raw_items):
    processed_items = []
    for it in raw_items:
        iid = it.get("item_id")
        if iid in INVALID_ITEM_IDS:
            continue
        stats = parse_single_item_stats(it)
        cat = ITEM_TYPE_CAT.get(it.get("item_type", 1), "攻击")
        clean_name = stats.get("name", it.get("item_name"))
        if iid in WUXIANG_OVERRIDES:
            cat, clean_name = WUXIANG_OVERRIDES[iid]
        icon_url = f"https://game.gtimg.cn/images/yxzj/img201606/itemimgo/{iid}.png"

        raw_d1 = it.get("des1") or ""
        raw_d2 = it.get("des2") or ""
        clean_d1 = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw_d1)).strip()
        for k, v in [
            ("物理攻击", "物攻"), ("法术攻击", "法攻"), ("最大生命", "生命"),
            ("物理防御", "物防"), ("法术防御", "法防"), ("物理吸血", "吸血"),
            ("法术吸血", "法吸"), ("攻击速度", "攻速"), ("移动速度", "移速"),
            ("冷却缩减", "冷缩"), ("暴击率", "暴击"),
        ]:
            clean_d1 = clean_d1.replace(k, v)
        stats_chips = [c for c in clean_d1.split(" ") if c]

        raw_lines = [
            re.sub(r"<[^>]+>", "", l).strip()
            for l in re.split(r"<br\s*/?>|</?p>", raw_d2)
            if re.sub(r"<[^>]+>", "", l).strip()
        ]
        passives = []
        for l in raw_lines:
            m = re.match(r"^(?:唯一)?(被动|主动)[-—：:]\s*([^：:，,\s]+)[：:]\s*(.*)$", l)
            if m:
                kind, pname, desc = m.groups()
                cd_m = re.search(
                    r"冷却时间[:：]?\s*(\d+(?:\.\d+)?)\s*秒?|(?<!\w)CD[:：]?\s*(\d+(?:\.\d+)?)\s*秒?|(\d+(?:\.\d+)?)\s*秒(?:的)?(?:CD|cd|冷却)",
                    desc, re.I,
                )
                sec = (cd_m.group(1) or cd_m.group(2) or cd_m.group(3)) if cd_m else ""
                passives.append({
                    "kind": kind, "name": pname, "title": f"{kind} · {pname}",
                    "cd": f"冷却 {sec}秒" if sec else "", "desc": desc.strip(),
                })
            else:
                passives.append({
                    "kind": "机制", "name": "效果", "title": "机制效果", "cd": "", "desc": l.strip(),
                })

        processed_items.append({
            "item_id": iid, "item_name": clean_name, "category": cat,
            "total_price": it.get("total_price", 0), "stats": stats, "icon": icon_url,
            "des1": clean_d1, "des2": re.sub(r"</?[^>]+>", " ", raw_d2).strip(),
            "stats_chips": stats_chips, "passives": passives,
        })
    return processed_items


def _build_processed_heroes(heroes):
    processed_heroes = []
    for h in heroes:
        ename = str(h.get("ename"))
        cname = h.get("cname")
        m_info = CN_HERO_MANIFEST.get(int(ename), {})
        r1 = m_info.get("hero_type") or h.get("hero_type")
        r2 = m_info.get("hero_type2") or h.get("hero_type2")
        roles = [ROLE_MAP[r] for r in (r1, r2) if r in ROLE_MAP]
        roles = list(dict.fromkeys(roles))
        role_str = "/".join(roles) if roles else "坦克"
        base = get_hero_base_stats(ename, cname, role_str)
        rec_arcana = HERO_RECOMMENDED_ARCANA.get(cname, {"red": "异变", "green": "鹰眼", "blue": "隐匿"})

        build_info = OFFICIAL_HERO_BUILDS.get(cname, {})
        raw_lanes = list(build_info.get("lanes", {}).keys()) or build_info.get("supported_lanes", [])
        lanes = []
        for l in raw_lanes:
            nl = "对抗路" if l == "对抗" else ("发育路" if l == "发育" else l)
            if nl not in lanes:
                lanes.append(nl)
        if not lanes:
            lanes = (
                ["发育路"] if "射手" in role_str else
                ["中路"] if "法师" in role_str else
                ["游走"] if "辅助" in role_str else
                ["打野"] if "刺客" in role_str else ["对抗路"]
            )
        rec_builds = HERO_BUILDS_PATCHES.get(cname, [])
        rec_items = rec_builds[0]["items"] if rec_builds and "items" in rec_builds[0] else []

        processed_heroes.append({
            "ename": ename, "cname": cname, "title": h.get("title", ""), "role": role_str,
            "lane": lanes[0], "supported_lanes": lanes, "base_stats": base,
            "recommended_arcana": rec_arcana, "recommended_equips": rec_items,
        })
    return processed_heroes


def write_miniprogram_dataset(data_dir: str):
    raw_items = fetch_json(URL_ITEM_LIST)
    heroes = get_validated_hero_list()
    processed_items = _build_processed_items(raw_items)
    processed_heroes = _build_processed_heroes(heroes)

    normalized_official_builds = {}
    for hero_name, b_info in OFFICIAL_HERO_BUILDS.items():
        copy_info = dict(b_info)
        if "lanes" in copy_info:
            new_lanes = {}
            for l_name, b_list in copy_info["lanes"].items():
                norm_l = "对抗路" if l_name in ("对抗", "对抗路") else ("发育路" if l_name in ("发育", "发育路") else l_name)
                new_lanes[norm_l] = b_list
            copy_info["lanes"] = new_lanes
        normalized_official_builds[hero_name] = copy_info

    unified_skills_data = dict(HERO_SKILLS_DATA)
    for hero_name, patch in REWORKED_HERO_SKILLS_PATCHES.items():
        if "skills" in patch:
            unified_skills_data[hero_name] = patch["skills"]
    combos_data = get_all_combos()

    body_fields = f"""  HEROES_DATA: {json.dumps(processed_heroes, ensure_ascii=False)},
  ITEMS_DATA: {json.dumps(processed_items, ensure_ascii=False)},
  ARCANA_DATA: {json.dumps(ARCANA_LEVEL_5_DICT, ensure_ascii=False)},
  HERO_SKILLS: {json.dumps(unified_skills_data, ensure_ascii=False)},
  OFFICIAL_HERO_BUILDS: {json.dumps(normalized_official_builds, ensure_ascii=False)},
  HERO_COMBOS: {json.dumps(combos_data, ensure_ascii=False)},
  OFFICIAL_ATTACK_ICON: "/assets/icon_attack.png",
  RECIPES_MAP: {json.dumps(COMPONENTS_MAP, ensure_ascii=False)},
  BOOTS_MAP: {json.dumps(BOOTS_SPEED_MAP, ensure_ascii=False)},
  ACTIVE_ITEMS: {json.dumps(ACTIVE_SKILL_ITEMS, ensure_ascii=False)},
  JUNGLE_ITEMS: {json.dumps(JUNGLE_ITEMS, ensure_ascii=False)}"""

    # 1. 微信原生小程序工程数据 (严格控制单包体量 < 1.5MB)
    with open(os.path.join(data_dir, "dataset.js"), "w", encoding="utf-8") as f:
        f.write(f"// 王者荣耀全量离线数据集\nmodule.exports = {{\n{body_fields}\n}};\n")

    # 清理历史遗留的 dataset_preview.js，防止进入小程序主包
    stale_preview = os.path.join(data_dir, "dataset_preview.js")
    if os.path.exists(stale_preview):
        try:
            os.remove(stale_preview)
        except OSError:
            pass

    # 2. 网页端预览外壳数据 (独立存放于 templates/preview/，不计入小程序上传包)
    preview_data_dir = os.path.join(ROOT_DIR, "templates", "preview")
    os.makedirs(preview_data_dir, exist_ok=True)
    with open(os.path.join(preview_data_dir, "dataset_preview.js"), "w", encoding="utf-8") as f:
        f.write(f"// 王者荣耀预览沙盒全量数据集\nwindow.DATASET = {{\n{body_fields}\n}};\n")
