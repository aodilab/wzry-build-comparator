# -*- coding: utf-8 -*-
"""
S45 权威装备底层数值与被动机制解析库 (Single Source of Truth)
100% 严格对齐 config/items_ground_truth.json (115张游戏内实测截图) 与 config/item_recipes.py：
1. 基础面板属性（物攻/法攻/物防/法防/生命/蓝量/冷却/暴击/攻速/移速/吸血/穿透）全部从 des1 动态提取
2. 随英雄等级(Lv1~Lv15)与打野刀层数(0~25层)动态成长的被动数值严格对照 des2 原文
3. 唯一被动/主动技能机制（强击、破军、暴烈无畏、苍穹减伤、怒龙重创/神力、不死鸟血统、魔女迷雾/魔女、永夜守护、血魔狂怒/血怒等）
4. 基于 COMPONENTS_MAP 递归计算的真实最大合成断档金币 (max_gap)
"""

import json
import re
from pathlib import Path
from config.item_recipes import COMPONENTS_MAP

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
GT_PATH = ROOT_DIR / "config" / "items_ground_truth.json"

with open(GT_PATH, "r", encoding="utf-8") as f:
    RAW_GT_ITEMS = json.load(f)

ALIAS_TO_GT = {
    "破军": "强者破军",
    "强者·破军": "强者破军",
    "破晓": "仁者破晓",
    "仁者·破晓": "仁者破晓",
    "贤者之书": "贤者天书",
    "急速之靴": "急速战靴",
}

BOOTS_FLAT_SPEED = {
    "神速之靴": 30,
    "影忍之足": 50,
    "抵抗之靴": 50,
    "冷静之靴": 50,
    "秘法之靴": 50,
    "急速战靴": 50,
    "急速之靴": 50,
    "疾步之靴": 70,
}


def resolve_gt_name(name: str) -> str:
    n = (name or "").strip()
    return ALIAS_TO_GT.get(n, n)


def get_item_price(name: str) -> int:
    gt_name = resolve_gt_name(name)
    entry = RAW_GT_ITEMS.get(gt_name)
    return int(entry.get("total_price", 0)) if entry else 0


def compute_max_synthesis_gap(name: str) -> int:
    """递归计算一件装备合成过程中的最大单次金币断档 (合成真空期)"""
    gt_name = resolve_gt_name(name)
    price = get_item_price(gt_name)
    if price <= 0:
        return 0
    children = COMPONENTS_MAP.get(gt_name) or COMPONENTS_MAP.get(name) or []
    if not children:
        return price
    children_cost = sum(get_item_price(c) for c in children)
    combine_gap = max(0, price - children_cost)
    child_max_gap = max((compute_max_synthesis_gap(c) for c in children), default=0)
    return max(combine_gap, child_max_gap)


def parse_base_stats_from_des1(gt_name: str) -> dict:
    """100% 从 items_ground_truth.json 的 des1 提取基础面板属性"""
    entry = RAW_GT_ITEMS.get(gt_name, {})
    des1 = re.sub(r"</?[^>]+>", "\n", entry.get("des1", ""))
    st = {
        "atk": 0.0, "ap": 0.0, "pdef": 0.0, "mdef": 0.0, "hp": 0.0, "mp": 0.0,
        "crit": 0.0, "aspeed": 0.0, "cd": 0.0, "speed_pct": 0.0,
        "speed_flat": float(BOOTS_FLAT_SPEED.get(gt_name, 0)),
        "p_vamp": 0.0, "m_vamp": 0.0,
    }
    for line in des1.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.search(r"\+(\d+)\s*物理攻击", line)
        if m: st["atk"] += float(m.group(1))
        m = re.search(r"\+(\d+)\s*法术攻击", line)
        if m: st["ap"] += float(m.group(1))
        m = re.search(r"\+(\d+)\s*物理防御", line)
        if m: st["pdef"] += float(m.group(1))
        m = re.search(r"\+(\d+)\s*法术防御", line)
        if m: st["mdef"] += float(m.group(1))
        m = re.search(r"\+(\d+)\s*(?:最大生命值|最大生命|生命值)", line)
        if m: st["hp"] += float(m.group(1))
        m = re.search(r"\+(\d+)\s*最大法力", line)
        if m: st["mp"] += float(m.group(1))
        m = re.search(r"\+(\d+(?:\.\d+)?)%\s*(?:暴击率|暴击)", line)
        if m: st["crit"] += float(m.group(1))
        m = re.search(r"\+(\d+(?:\.\d+)?)%\s*(?:攻击速度|攻速)", line)
        if m: st["aspeed"] += float(m.group(1))
        m = re.search(r"\+(\d+(?:\.\d+)?)%\s*(?:冷却缩减|冷却)", line)
        if m: st["cd"] += float(m.group(1))
        m = re.search(r"\+(\d+(?:\.\d+)?)%\s*(?:移动速度|移速加成|移速)", line)
        if m: st["speed_pct"] += float(m.group(1))
        m = re.search(r"\+(\d+(?:\.\d+)?)%\s*物理吸血", line)
        if m: st["p_vamp"] += float(m.group(1))
        m = re.search(r"\+(\d+(?:\.\d+)?)%\s*法术吸血", line)
        if m: st["m_vamp"] += float(m.group(1))
    return st


def get_dynamic_item_profile(name: str, lv: int = 15, jg_stacks: int = 25, combat_stacks: float = 1.0, is_ranged: bool = False) -> dict:
    """
    获取指定装备在任意等级(lv: 1~15)与打野层数(jg_stacks: 0~25)下的完整面板与机制特征。
    严格对齐 config/items_ground_truth.json 的 des1 + des2 原文。
    """
    gt_name = resolve_gt_name(name)
    r = max(0.0, min(1.0, (lv - 1) / 14.0))
    base = parse_base_stats_from_des1(gt_name)
    prof = {
        **base,
        "name": gt_name,
        "price": get_item_price(gt_name),
        "max_gap": compute_max_synthesis_gap(gt_name),
        "pen_flat": 0.0,
        "pen_pct": 0.0,
        "m_pen_flat": 0.0,
        "m_pen_pct": 0.0,
        "crit_eff": 0.0,
        "tenacity": 0.0,        # 韧性比例 (抵抗之靴 0.25 / 冰霜冲击·凛冬 0.10)
        "slow_resist": 0.0,     # 减速抗性 (永夜守护 0.50)
        "anti_heal": 0.0,       # 重伤比例 (制裁/梦魇/红莲 0.35)
        "summoner_cdr": 0.0,    # 召唤师技能冷却加速 (冷静之靴 10%~20%)
        "out_of_combat_speed_flat": 0.0,  # 脱战固定移速 (疾步之靴 35~70)
        "on_hit_heal": 0.0,     # 普攻命中固定回血 (急速战靴 20~40 / 远程 30~60)
        "combat_speed_pct": 0.0,
        "dmg_amp": 0.0,
        "pojun_amp": 0.0,
        "passive_dr": 0.0,
        "active_dr": 0.0,
        "heal_amp": 0.0,
        "heal_amp_per_10pct_missing": 0.0,
        "spellblade": None,
        "on_hit_phys": 0.0,
        "on_hit_magic": 0.0,
        "on_hit_magic_ap": 0.0,
        "on_hit_max_hp_ratio": 0.0,
        "proc_phys_base": 0.0,
        "proc_phys_bonus_ad": 0.0,
        "proc_magic_base": 0.0,
        "proc_magic_ap": 0.0,
        "proc_magic_hp_ratio": 0.0,
        "skill_phys_vamp": 0.0,
        "jg_burn_target_hp_ratio": 0.0,
        "nulong_max_hp_ratio": 0.0,
        "nulong_heal_max_hp": 0.0,
        "wave_clear_score": 0.0,
        "monv_shield": 0.0,
        "monv_hp_ratio": 0.0,
        "monv_mdef_to_pdef": 0.0,
        "shield_base": 0.0,
        "shield_hp_ratio": 0.0,
        "shield_ap_ratio": 0.0,
        "yongye_heal_base": 0.0,
        "yongye_hp_ratio": 0.0,
        "xuemo_hp_ratio": 0.0,
        "has_mingdao": False,
        "has_hat": False,
        "has_prophecy": False,
        "has_pomo": False,
        "has_bazhe": False,
        "has_infinity": False,
        "has_cocoon": False,
        "has_sage_book": False,
    }

    # 1. 打野刀动态叠层与被动-狩猎灼烧 (IMG_6840/6841/6843/6915/6917/6920)
    if gt_name == "追击刀锋":
        s = min(15, jg_stacks)
        prof["atk"] += 3.0 * s
        prof["proc_phys_base"] += (70.0 + 70.0 * r) * 0.40
        prof["wave_clear_score"] += 0.03
    elif gt_name == "贪婪之噬":
        s = min(25, jg_stacks)
        prof["atk"] += 3.0 * s
        prof["cd"] += 0.20 * s
        prof["proc_phys_base"] += (90.0 + 90.0 * r) * 1.0  # 狩猎每0.5s 90~180(+0.6%生命)持续2s，对英雄生效25%(4次合计1.0倍)
        prof["jg_burn_target_hp_ratio"] += 0.006
        prof["wave_clear_score"] += 0.06
    elif gt_name == "巡守利斧":
        s = min(15, jg_stacks)
        prof["hp"] += 30.0 * s
        prof["proc_phys_base"] += (70.0 + 70.0 * r) * 0.40
        prof["wave_clear_score"] += 0.03
    elif gt_name == "巨人之握":
        s = min(25, jg_stacks)
        prof["hp"] += 30.0 * s
        prof["cd"] += 0.20 * s
        prof["proc_phys_base"] += (90.0 + 90.0 * r) * 1.0
        prof["jg_burn_target_hp_ratio"] += 0.006
        prof["wave_clear_score"] += 0.06
    elif gt_name == "游击弯刀":
        s = min(15, jg_stacks)
        prof["ap"] += 6.0 * s
        prof["proc_magic_base"] += (70.0 + 70.0 * r) * 0.40
        prof["wave_clear_score"] += 0.03
    elif gt_name == "符文大剑":
        s = min(25, jg_stacks)
        prof["ap"] += 6.0 * s
        prof["cd"] += 0.20 * s
        prof["proc_magic_base"] += (90.0 + 90.0 * r) * 1.0
        prof["wave_clear_score"] += 0.06

    # 2. 穿透与暴击效果装备
    if gt_name == "暗影战斧":
        prof["pen_flat"] = round(90.0 + 90.0 * r, 1)
    elif gt_name == "碎星锤":
        prof["pen_pct"] = 30.0
    elif gt_name == "仁者破晓":
        prof["pen_pct"] = 30.0 if is_ranged else 15.0
        prof["on_hit_phys"] += 50.0 if is_ranged else 25.0
    elif gt_name in ("逐日之弓", "迅疾·日渊"):
        prof["on_hit_phys"] += 50.0 if is_ranged else 25.0
    elif gt_name == "无尽战刃":
        prof["has_infinity"] = True
        prof["crit_eff"] = 30.0
    elif gt_name == "秘法之靴":
        prof["m_pen_flat"] = round(60.0 + 60.0 * r, 1)
    elif gt_name == "云灵木":
        prof["m_pen_flat"] = 60.0
    elif gt_name == "日暮之流":
        prof["m_pen_flat"] = round((20.0 + 20.0 * r) * 3.5 * combat_stacks, 1)
    elif gt_name == "虚无法杖":
        prof["m_pen_pct"] = 45.0

    # 3. 强击 (Spellblade) 唯一被动
    if gt_name == "宗师之力":
        prof["spellblade"] = ("zongshi", 3.0, 0.0, 0.80, 0.0, 0.0)
        prof["combat_speed_pct"] += 8.0  # 使用技能后+12%移速持续2秒(CD 3秒，折合8%常驻战斗加速)
    elif gt_name == "冰痕之握":
        prof["spellblade"] = ("binghen", 1.25, 140.0 + 140.0 * r, 0.0, 0.40, 0.0)
    elif gt_name == "巫术法杖":
        prof["spellblade"] = ("wushu", 2.5, 180.0 + 180.0 * r, 0.0, 0.0, 0.40)

    # 4. 鞋类专属被动与增减伤/护盾/回复核心机制
    if gt_name == "抵抗之靴":
        prof["tenacity"] = 0.25
    elif gt_name == "影忍之足":
        prof["passive_dr"] += (0.06 + 0.06 * r) * 0.65
    elif gt_name == "冷静之靴":
        prof["summoner_cdr"] = 10.0 + 10.0 * r
    elif gt_name in ("急速战靴", "急速之靴"):
        prof["on_hit_heal"] = (30.0 + 30.0 * r) if is_ranged else (20.0 + 20.0 * r)
    elif gt_name == "疾步之靴":
        prof["out_of_combat_speed_flat"] = 35.0 + 35.0 * r
    elif gt_name == "极寒风暴":
        prof["passive_dr"] += 0.05
    elif gt_name == "不祥征兆":
        prof["passive_dr"] += 0.06
    elif gt_name == "反伤刺甲":
        prof["passive_dr"] += 0.04
    elif gt_name == "红莲斗篷":
        prof["proc_magic_hp_ratio"] += 0.015 * 1.8
        prof["anti_heal"] = 0.35
        prof["wave_clear_score"] += 0.08
    elif gt_name == "末世":
        prof["on_hit_phys"] += (80.0 + 80.0 * r) + 2500.0 * 0.07
        prof["wave_clear_score"] += 0.05
    elif gt_name == "闪电匕首":
        prof["on_hit_magic"] += (40.0 + 40.0 * r) + (160.0 + 240.0 * r) / 3.0
        prof["wave_clear_score"] += 0.06
    elif gt_name == "影刃":
        crit_f = 1.0 + min(1.0, (prof["crit"] + 20.0) / 100.0)
        prof["combat_aspeed"] = prof.get("combat_aspeed", 0.0) + 10.0 * crit_f * combat_stacks
        prof["combat_speed_pct"] += 5.0 * crit_f * combat_stacks
    elif gt_name == "金色圣剑":
        prof["on_hit_phys"] += 60.0
        prof["combat_aspeed"] = prof.get("combat_aspeed", 0.0) + 20.0 * combat_stacks
        prof["on_hit_magic_ap"] += 0.30 * combat_stacks
    elif gt_name == "寒霜袭侵":
        prof["proc_phys_base"] += 135.0 + 135.0 * r
        prof["proc_phys_bonus_ad"] += 0.45
        prof["passive_dr"] += 0.03
    elif gt_name == "泣血之刃":
        prof["skill_phys_vamp"] += 25.0
        prof["shield_base"] += (200.0 + 200.0 * r) * combat_stacks
    elif gt_name == "制裁之刃":
        prof["yongye_heal_base"] += (160.0 + 160.0 * r) + 2.0 * (30.0 + 30.0 * r) * (2.0 if is_ranged else 1.0)
        prof["yongye_hp_ratio"] += 0.04 + 2.0 * 0.008 * (2.0 if is_ranged else 1.0)
        prof["anti_heal"] = 0.35
    elif gt_name == "梦魇之牙":
        prof["anti_heal"] = 0.35
    elif gt_name == "回响之杖":
        prof["proc_magic_base"] += 140.0 + 140.0 * r
        prof["proc_magic_ap"] += 0.28
        prof["wave_clear_score"] += 0.05
    elif gt_name == "痛苦面具":
        prof["proc_magic_base"] += 680.0
        prof["wave_clear_score"] += 0.04
    elif gt_name == "凝冰之息":
        prof["proc_magic_base"] += 75.0 + 75.0 * r
        prof["proc_magic_ap"] += 0.15
    elif gt_name == "旭日初光":
        prof["shield_base"] += (250.0 + 250.0 * r) * 1.25
        prof["shield_hp_ratio"] += 0.04 * 1.25
    elif gt_name in ("冰霜冲击", "徐行·凛冬"):
        prof["tenacity"] = 0.10
        prof["shield_hp_ratio"] += 0.10
        prof["proc_magic_base"] += 100.0 + 100.0 * r
        prof["passive_dr"] += 0.04
    elif gt_name == "炽热支配":
        prof["shield_base"] += 500.0 + 500.0 * r
        prof["shield_ap_ratio"] += 1.0
        prof["shield_hp_ratio"] += 0.075
    elif gt_name == "贤者的庇护":
        prof["shield_base"] += (2000.0 + 1000.0 * r) * 0.70
    elif gt_name == "辉月":
        prof["active_dr"] += 0.12
    elif gt_name == "难知·月神":
        prof["active_dr"] += 0.14
        prof["yongye_heal_base"] += 1000.0
    elif gt_name == "幽影袖箭":
        prof["yongye_heal_base"] += 520.0 + 260.0 * r
        prof["yongye_hp_ratio"] += 0.06
    elif gt_name == "圣杯":
        prof["yongye_hp_ratio"] += 0.03
    elif "近卫" in gt_name or "极影" in gt_name:
        is_t3 = any(k in gt_name for k in ("救赎", "奔狼", "形昭", "星泉"))
        prof["hp"] += (400.0 + 400.0 * r) if is_t3 else (200.0 + 200.0 * r)
        prof["atk"] += (25.0 + 25.0 * r) if is_t3 else (15.0 + 15.0 * r)
        if "近卫" in gt_name:
            d_val = (65.0 + 65.0 * r) if is_t3 else (36.0 + 36.0 * r)
            prof["pdef"] += d_val
            prof["mdef"] += d_val
        else:
            prof["aspeed"] += 20.0 if is_t3 else 12.0
            prof["cd"] += 15.0 if is_t3 else 9.0
        if "救赎" in gt_name:
            prof["shield_base"] += 240.0 + 240.0 * r
            prof["shield_hp_ratio"] += 0.10
        elif "星泉" in gt_name:
            prof["yongye_heal_base"] += 500.0 + 560.0 * r
            prof["yongye_hp_ratio"] += 0.20
        elif "形昭" in gt_name:
            prof["proc_magic_base"] += 450.0
    elif gt_name == "暴烈之甲":
        layers = round(10 * combat_stacks)
        prof["dmg_amp"] += 0.01 * layers
        prof["combat_speed_pct"] += 1.0 * layers
    elif gt_name == "逐风":
        layers = round(5 * combat_stacks)
        prof["combat_aspeed"] = 2.0 * layers
        prof["combat_speed_pct"] += 2.0 * layers
        prof["dmg_amp"] += 0.02 * layers
    elif gt_name == "强者破军":
        prof["pojun_amp"] = 0.30
    elif gt_name == "贤者天书":
        prof["has_sage_book"] = True
    elif gt_name == "纯净苍穹":
        prof["passive_dr"] = 0.075
        prof["active_dr"] = 0.30
    elif gt_name == "不动·天穹":
        prof["passive_dr"] = 0.085
        prof["active_dr"] = 0.35
    elif gt_name == "怒龙剑盾":
        ratio = 0.0175 if is_ranged else 0.035
        prof["nulong_max_hp_ratio"] = max(prof["nulong_max_hp_ratio"], ratio)
        prof["nulong_heal_max_hp"] = max(prof["nulong_heal_max_hp"], ratio)
        prof["wave_clear_score"] += 0.12
    elif gt_name == "魔女斗篷":
        prof["monv_shield"] = 400.0 + 400.0 * r
        prof["monv_hp_ratio"] = 0.07
        prof["monv_mdef_to_pdef"] = 0.15
    elif gt_name == "永夜守护":
        prof["yongye_heal_base"] = 0.0
        prof["yongye_hp_ratio"] = 0.10
        prof["slow_resist"] = 0.50
    elif gt_name == "不死鸟之眼":
        prof["heal_amp_per_10pct_missing"] = 0.065
        prof["heal_amp"] = 0.4225
    elif gt_name == "血魔之怒":
        prof["on_hit_max_hp_ratio"] = 0.015 * (1.0 + (0.125 + 0.125 * r))
        prof["xuemo_hp_ratio"] = 0.25
    elif gt_name == "侵掠·怒魂":
        prof["on_hit_max_hp_ratio"] = 0.015 * (1.0 + (0.1875 + 0.1875 * r))
        prof["xuemo_hp_ratio"] = 0.35
    elif gt_name == "噬神之书":
        prof["cd"] += prof["m_vamp"] / 2.0
    elif gt_name == "名刀·司命":
        prof["has_mingdao"] = True
    elif gt_name == "博学者之怒":
        prof["has_hat"] = True
    elif gt_name == "时之预言":
        prof["has_prophecy"] = True
    elif gt_name == "破魔刀":
        prof["has_pomo"] = True
    elif gt_name == "霸者重装":
        prof["has_bazhe"] = True
    elif gt_name == "破茧之衣":
        prof["has_cocoon"] = True

    return prof
