# -*- coding: utf-8 -*-
"""王者荣耀核心英雄连招与技能倍率建模配置 (hero_combo_profiles.py)"""

import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
with open(ROOT_DIR / "config" / "hero_skills_data.json", "r", encoding="utf-8") as f:
    HERO_SKILLS_DB = json.load(f)

HERO_COMBO_PROFILES = {
    "曜": {
        "burst_window_sec": 1.8,
        "full_window_sec": 3.5,
        "boots_candidates": ["抵抗之靴"],
        "mobility_score": 0.90,
        "ult_heal_missing_hp_ratio": 0.45,
        "needs_red_jg_early_tempo": True,
        "burst_hits": {"s1": 3.0, "s2": 1.0, "s3_mag": 1.0, "enh_aa": 1.0, "aa": 1.0},
        "full_hits": {"s1": 3.0, "s2": 3.0, "s3_mag": 1.0, "enh_aa": 2.0, "aa": 0.0},
        "s1_base": (340.0, 680.0), "s1_bonus_ad": 1.15, "s1_cd": (6.0, 5.0),
        "s2_base": (180.0, 360.0), "s2_bonus_ad": 0.70, "s2_cd": (7.5, 6.0),
        "s3_base": (420.0, 840.0), "s3_bonus_ad": 1.40, "s3_cd": (15.0, 12.5, 10.0),
        "enh_aa_base": (80.0, 160.0), "enh_aa_total_ad": 1.27,
        "passive_heal_base": (70.0, 140.0), "passive_heal_bonus_hp": 0.02, "heal_procs_per_fight": 3.0,
        "star_shatter_by_ult": (0.0, 0.25, 0.375, 0.50),
    },
    "杨戬": {
        "burst_window_sec": 2.0, "full_window_sec": 4.0,
        "boots_candidates": ["影忍之足", "冷静之靴", "抵抗之靴"],
        "mobility_score": 0.35, "ult_heal_missing_hp_ratio": 0.65,
        "needs_red_jg_early_tempo": True, "anti_burst_entry_gate": 20500,
        "viral_builds_jg": [
            ("精选打野-黄盾不死鸟苍穹流(一寒打野教学)", ["贪婪之噬", "抵抗之靴", "暗影战斧", "怒龙剑盾", "不死鸟之眼", "纯净苍穹"]),
            ("半肉续航-影忍足黄盾不死鸟苍穹流", ["贪婪之噬", "影忍之足", "暗影战斧", "怒龙剑盾", "不死鸟之眼", "纯净苍穹"]),
            ("半肉双效-冰痕苍穹不死鸟满CD流", ["贪婪之噬", "影忍之足", "暗影战斧", "冰痕之握", "纯净苍穹", "不死鸟之眼"]),
            ("半肉收割-暴烈破军苍穹流", ["贪婪之噬", "抵抗之靴", "暗影战斧", "暴烈之甲", "强者破军", "纯净苍穹"]),
            ("全输出-宗师破军双穿流", ["贪婪之噬", "抵抗之靴", "暗影战斧", "宗师之力", "强者破军", "碎星锤"]),
            ("纯肉蓝领-肉刀黄盾不死鸟", ["巨人之握", "影忍之足", "怒龙剑盾", "不死鸟之眼", "极寒风暴", "霸者重装"]),
        ],
        "viral_builds_lane": [
            ("绝活/国服榜9-苍穹不死鸟暴烈黄盾流(开开/好男01)", ["影忍之足", "暗影战斧", "纯净苍穹", "不死鸟之眼", "暴烈之甲", "怒龙剑盾"]),
            ("绝活均衡-苍穹冰脉不死鸟黄盾流(梦修奉)", ["影忍之足", "暗影战斧", "纯净苍穹", "冰霜冲击", "不死鸟之眼", "怒龙剑盾"]),
            ("国服榜6-苍穹暴烈不死鸟冰脉流(馬嘉灲的祺友)", ["影忍之足", "暗影战斧", "纯净苍穹", "暴烈之甲", "不死鸟之眼", "冰霜冲击"]),
        ],
        "kite_hits": {"s1": 1.0, "s2": 1.0, "s3_phys": 3.5, "tianyan": 3.0, "aa": 1.0, "true_on_hit": 1.0, "sb_procs": (1.2, 1.0), "exec_missing_pct": 0.15},
        "mid_hits": {"s1": 1.0, "s2": 1.0, "s3_phys": 3.5, "tianyan": 3.0, "aa": 2.0, "true_on_hit": 2.0, "sb_procs": (1.8, 1.3), "exec_missing_pct": 0.15},
        "melee_hits": {"s1": 1.0, "s2": 1.0, "s3_phys": 3.6, "tianyan": 3.0, "aa": 3.8, "true_on_hit": 3.8, "sb_procs": (2.5, 1.8), "exec_missing_pct": 0.15},
        "scenario_weights": (0.50, 0.35, 0.15),
        "burst_hits": {"s1": 1.0, "s2": 1.0, "s3_phys": 1.3, "tianyan": 2.0, "aa": 1.0, "true_on_hit": 1.0, "sb_procs": (1.0, 1.0), "exec_missing_pct": 0.15},
        "full_hits": {"s1": 1.0, "s2": 1.0, "s3_phys": 3.52, "tianyan": 3.0, "aa": 1.77, "true_on_hit": 1.77, "sb_procs": (1.61, 1.23), "exec_missing_pct": 0.15},
        "aoe_hits": {"s1": 1.0, "s2": 1.45, "s3_phys": 5.45, "tianyan": 3.0, "aa": 1.77, "true_on_hit": 1.77, "sb_procs": (1.61, 1.23), "exec_missing_pct": 0.15, "nulong_mult": 1.35},
        "s1_base": (500.0, 1000.0), "s1_bonus_ad": 1.50, "s1_cd": (7.5, 6.0),
        "s2_base": (350.0, 700.0), "s2_bonus_ad": 1.00, "s2_cd": (10.0, 8.0),
        "true_hit_base": (125.0, 250.0), "true_hit_bonus_ad": 0.36,
        "s3_base": (340.0, 680.0), "s3_bonus_ad": 1.10, "s3_cd": (35.0, 31.5, 28.0),
        "tianyan_base": (80.0, 160.0), "tianyan_bonus_ad": 0.25,
        "enh_aa_base": (0.0, 0.0), "enh_aa_total_ad": 0.0, "enh_aa_bonus_ad": 0.0,
        "combat_flat_hp_bonus": 600.0,
        "passive_heal_base": (320.0, 640.0), "passive_heal_bonus_hp": 0.045, "heal_procs_per_fight": 6.2,
        "needs_wave_clear_aid": True,
    },
    "赵云": {
        "burst_window_sec": 1.6, "full_window_sec": 3.2, "boots_candidates": ["抵抗之靴", "冷静之靴", "影忍之足"],
        "mobility_score": 0.78, "ult_heal_missing_hp_ratio": 0.55, "needs_red_jg_early_tempo": True,
        "burst_hits": {"s1": 1.0, "s2": 4.0, "s3_phys": 1.0, "enh_aa": 1.0, "aa": 1.0},
        "full_hits": {"s1": 2.0, "s2": 5.0, "s3_phys": 1.0, "enh_aa": 2.0, "aa": 1.0},
        "s1_base": (200.0, 400.0), "s1_bonus_ad": 0.65, "s1_cd": (5.5, 4.5),
        "s2_base": (155.0, 310.0), "s2_bonus_ad": 0.55, "s2_cd": (6.5, 5.5),
        "s3_base": (450.0, 900.0), "s3_bonus_ad": 1.30, "s3_cd": (16.0, 13.0, 10.0),
        "enh_aa_base": (85.0, 170.0), "enh_aa_total_ad": 1.35,
        "passive_heal_base": (100.0, 200.0), "passive_heal_bonus_hp": 0.02, "heal_procs_per_fight": 4.0,
        "extra_shield_hp_ratio": 0.18,
        "viral_builds_jg": [
            ("极端网红-魔刀流(血魔+名刀)", ["贪婪之噬", "抵抗之靴", "暗影战斧", "冰痕之握", "血魔之怒", "名刀·司命"]),
            ("传统主播-纯输出宗师破军", ["贪婪之噬", "抵抗之靴", "暗影战斧", "宗师之力", "强者破军", "名刀·司命"]),
        ],
    },
}


def extract_hero_skill_model(hero_cname: str) -> dict:
    if hero_cname in HERO_COMBO_PROFILES:
        return HERO_COMBO_PROFILES[hero_cname]
    skills = HERO_SKILLS_DB.get(hero_cname, [])
    s1_ad, s2_ad, s3_ad = 1.0, 0.8, 1.2
    for idx, sk in enumerate(skills[1:4], start=1):
        desc = sk.get("desc", "")
        m_ad = re.search(r"\(\+(\d+)%额外物理攻击\)", desc) or re.search(r"\(\+(\d+)%物理攻击\)", desc)
        ratio = float(m_ad.group(1)) / 100.0 if m_ad else (1.0 if idx == 1 else 0.8)
        if idx == 1: s1_ad = ratio
        elif idx == 2: s2_ad = ratio
        elif idx == 3: s3_ad = ratio
    return {
        "burst_window_sec": 1.8, "full_window_sec": 3.5, "boots_candidates": ["抵抗之靴"],
        "burst_hits": {"s1": 1.5, "s2": 1.5, "s3_phys": 1.0, "enh_aa": 1.0, "aa": 1.5},
        "full_hits": {"s1": 2.5, "s2": 2.0, "s3_phys": 1.0, "enh_aa": 2.0, "aa": 2.0},
        "s1_base": (300.0, 600.0), "s1_bonus_ad": s1_ad, "s1_cd": (6.0, 5.0),
        "s2_base": (250.0, 500.0), "s2_bonus_ad": s2_ad, "s2_cd": (7.0, 5.5),
        "s3_base": (450.0, 900.0), "s3_bonus_ad": s3_ad, "s3_cd": (15.0, 12.5, 10.0),
        "enh_aa_base": (80.0, 160.0), "enh_aa_total_ad": 1.20,
        "passive_heal_base": (60.0, 120.0), "passive_heal_bonus_hp": 0.015, "heal_procs_per_fight": 2.5,
    }


