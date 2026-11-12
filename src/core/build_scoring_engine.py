# -*- coding: utf-8 -*-
"""
王者荣耀【官方主副职业 × 分路职能 × 英雄机制与出装流派】动态评分标准引擎 (build_scoring_engine.py)
严格以本地官方权威分类 `config/hero_registry.py` (hero_type 主职业 + hero_type2 副职业：战士/法师/坦克/刺客/射手)
与 `config/official_builds_data.json` (五大分路与出装流派 tag/genre) 为唯一基准：
1. 第一层（官方主副职业基因）：主职业占 70% 权重 + 副职业占 30% 权重（单职业 100%），天然区分纯坦克、坦战、战坦、纯战士、战刺、刺战、纯刺客、法刺、法战、纯法师、射手。
2. 第二层（五大分路职能校准）：根据打野/对抗路/中路/发育路/游走分路，动态校准刷野控龙、无蓝常驻CD、前排承伤或团队增益权重。
3. 第三层（英雄专属技能机制与出装流派耦合）：100% 基于英雄底层技能机制特征（法球倍率、血量档位免伤、溢出转盾、魂链粘人、残血大招回复、法天象地韧性槽等）客观核算常态/绝境/团战三态综合分，零英雄名硬编码加分。
"""

from typing import Dict, Any
from config.hero_registry import CN_HERO_MANIFEST
from config.settings import ROLE_MAP

# ==============================================================================
# 一、 官方 5 大基础职业基准六维权重与三态模板 (源自 config/settings.py ROLE_MAP)
# ==============================================================================
OFFICIAL_BASE_ROLE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "战士": {
        "surv_3state": 0.31,   # 三态生存与续航容错
        "burst_kill": 0.28,    # 连招爆发与持续输出
        "cdr_cycle": 0.14,     # 技能冷却周转
        "pve_roam": 0.12,      # 清线刷野与转线跑图
        "econ_sustain": 0.09,  # 经济平滑度与破甲续航
        "stickiness_cc": 0.06, # 留人粘人与抗风筝
    },
    "法师": {
        "burst_kill": 0.36,
        "cdr_cycle": 0.22,
        "surv_3state": 0.20,
        "stickiness_cc": 0.10,
        "pve_roam": 0.07,
        "econ_sustain": 0.05,
    },
    "坦克": {
        "surv_3state": 0.42,
        "stickiness_cc": 0.18,
        "cdr_cycle": 0.13,
        "econ_sustain": 0.11,
        "pve_roam": 0.09,
        "burst_kill": 0.07,
    },
    "刺客": {
        "burst_kill": 0.38,
        "pve_roam": 0.20,
        "surv_3state": 0.20,
        "cdr_cycle": 0.13,
        "econ_sustain": 0.05,
        "stickiness_cc": 0.04,
    },
    "射手": {
        "burst_kill": 0.40,
        "surv_3state": 0.24,
        "econ_sustain": 0.16,
        "stickiness_cc": 0.10,
        "pve_roam": 0.06,
        "cdr_cycle": 0.04,
    },
}

OFFICIAL_BASE_ROLE_STATE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "战士": {"normal": 0.46, "special": 0.22, "teamfight": 0.32},
    "法师": {"normal": 0.48, "special": 0.24, "teamfight": 0.28},
    "坦克": {"normal": 0.38, "special": 0.18, "teamfight": 0.44},
    "刺客": {"normal": 0.55, "special": 0.23, "teamfight": 0.22},
    "射手": {"normal": 0.45, "special": 0.28, "teamfight": 0.27},
}

HERO_OFFICIAL_ROLES: Dict[str, tuple] = {}
for _id, _info in CN_HERO_MANIFEST.items():
    _r1 = ROLE_MAP.get(_info.get("hero_type", 1), "战士")
    _r2 = ROLE_MAP.get(_info.get("hero_type2", 0), "")
    HERO_OFFICIAL_ROLES[_info["cname"]] = (_r1, _r2)


def get_hero_official_role_tag(hero_cname: str) -> str:
    """获取英雄在官方名册中的主副职业标签，如 '战士/刺客'、'战士/坦克'、'坦克'"""
    r1, r2 = HERO_OFFICIAL_ROLES.get(hero_cname, ("战士", ""))
    return f"{r1}/{r2}" if r2 else r1


def get_dynamic_role_lane_weights(hero_cname: str, lane: str, model: dict) -> Dict[str, Any]:
    """
    基于【1. 官方主副职业 (70%主 + 30%副) × 2. 分路职能 × 3. 英雄技能机制特征】动态合成六维考核权重：
    完全由官方分类与 `model` 机制参数决定，不硬编码英雄名。
    """
    r1, r2 = HERO_OFFICIAL_ROLES.get(hero_cname, ("战士", ""))
    w1 = OFFICIAL_BASE_ROLE_WEIGHTS.get(r1, OFFICIAL_BASE_ROLE_WEIGHTS["战士"])
    s1 = OFFICIAL_BASE_ROLE_STATE_WEIGHTS.get(r1, OFFICIAL_BASE_ROLE_STATE_WEIGHTS["战士"])

    if r2 and r2 in OFFICIAL_BASE_ROLE_WEIGHTS:
        w2 = OFFICIAL_BASE_ROLE_WEIGHTS[r2]
        s2 = OFFICIAL_BASE_ROLE_STATE_WEIGHTS[r2]
        weights = {k: 0.70 * w1[k] + 0.30 * w2[k] for k in w1}
        state_weights = {k: 0.70 * s1[k] + 0.30 * s2[k] for k in s1}
        role_tag = f"{r1}/{r2}"
    else:
        weights = w1.copy()
        state_weights = s1.copy()
        role_tag = r1

    lane_norm = lane.replace("路", "")
    has_true_dmg = model.get("true_hit_base", (0.0, 0.0))[1] > 0
    high_heal = (model.get("passive_heal_base", (0.0, 0.0))[1] >= 400) or (model.get("ult_heal_base", (0.0, 0.0))[1] >= 1000)
    tier_passive = model.get("passive_dr_bonus", 0.0) > 0
    mob = model.get("mobility_score", 0.70)

    if lane_norm == "打野":
        if role_tag == "战士/刺客" or (tier_passive and mob >= 0.80):
            role_profile = f"官方[{role_tag}]·机动战刺打野（高AD加成秒C + 三态档位免伤/护盾 + 刷野控龙 + 无蓝/控蓝CD）"
            weights = {
                "burst_kill": 0.30, "surv_3state": 0.28, "pve_roam": 0.18,
                "cdr_cycle": 0.14, "econ_sustain": 0.06, "stickiness_cc": 0.04,
            }
            state_weights = {"normal": 0.52, "special": 0.20, "teamfight": 0.28}
        elif model.get("orb_proc_mult", 1.0) > 1.2 and high_heal:
            role_profile = f"官方[{role_tag}]·魂链法球重装打野（3秒魂链高频攻速移速粘人 + 法球/暴击斩杀 + 苍穹不死鸟残血群吸闭环）"
            weights = {
                "surv_3state": 0.31, "burst_kill": 0.28, "pve_roam": 0.16,
                "stickiness_cc": 0.10, "econ_sustain": 0.09, "cdr_cycle": 0.06,
            }
            state_weights = {"normal": 0.42, "special": 0.25, "teamfight": 0.33}
        elif has_true_dmg and high_heal:
            role_profile = f"官方[{role_tag}]·重装真伤回血打野（三态双抗群吸闭环 + 秒C与贴脸真伤 + 黄盾控龙移速）"
            weights = {
                "surv_3state": 0.32, "burst_kill": 0.25, "pve_roam": 0.18,
                "econ_sustain": 0.11, "cdr_cycle": 0.10, "stickiness_cc": 0.04,
            }
            state_weights = {"normal": 0.42, "special": 0.23, "teamfight": 0.35}
        else:
            weights["pve_roam"] += 0.05
            weights["stickiness_cc"] = max(0.03, weights["stickiness_cc"] - 0.03)
            weights["econ_sustain"] = max(0.04, weights["econ_sustain"] - 0.02)
            role_profile = f"官方[{role_tag}]·打野分路标准"
    elif lane_norm == "对抗":
        if has_true_dmg and high_heal:
            role_profile = f"官方[{role_tag}]·对抗路重装战神（三态抗集火回血 + 单挑斩杀切C + 无蓝常驻CD）"
            weights = {
                "surv_3state": 0.33, "burst_kill": 0.28, "cdr_cycle": 0.16,
                "econ_sustain": 0.11, "pve_roam": 0.07, "stickiness_cc": 0.05,
            }
            state_weights = {"normal": 0.45, "special": 0.22, "teamfight": 0.33}
        else:
            weights["surv_3state"] += 0.02
            weights["cdr_cycle"] += 0.02
            weights["pve_roam"] = max(0.05, weights["pve_roam"] - 0.04)
            role_profile = f"官方[{role_tag}]·对抗路分路标准"
    elif lane_norm == "游走":
        if r1 == "坦克" or r2 == "坦克":
            role_profile = f"官方[{role_tag}]·硬辅开团承伤游走（三态前排承伤 + 控制开团 + 救赎/奔狼/形昭主动增益）"
            weights = {
                "surv_3state": 0.40, "stickiness_cc": 0.25, "cdr_cycle": 0.17,
                "econ_sustain": 0.12, "pve_roam": 0.03, "burst_kill": 0.03,
            }
            state_weights = {"normal": 0.35, "special": 0.20, "teamfight": 0.45}
        else:
            role_profile = f"官方[{role_tag}]·功能/增益保护游走（满40%CD技能频率 + 护盾治疗控制增益 + 防切自保）"
            weights = {
                "cdr_cycle": 0.30, "econ_sustain": 0.26, "surv_3state": 0.24,
                "stickiness_cc": 0.10, "pve_roam": 0.06, "burst_kill": 0.04,
            }
            state_weights = {"normal": 0.40, "special": 0.30, "teamfight": 0.30}
    else:
        role_profile = f"官方[{role_tag}]·{lane_norm}路分路标准"

    total_w = sum(weights.values())
    weights = {k: round(v / total_w, 4) for k, v in weights.items()}
    total_sw = sum(state_weights.values())
    state_weights = {k: round(v / total_sw, 4) for k, v in state_weights.items()}

    return {
        "official_role_tag": role_tag,
        "role_profile": role_profile,
        "weights": weights,
        "state_weights": state_weights,
    }


def classify_build_style(item_names: list) -> str:
    """根据当前 6 件装备组合客观识别出装流派方向"""
    def_items = {
        "红莲斗篷", "霸者重装", "不祥征兆", "不死鸟之眼", "魔女斗篷", "永夜守护",
        "极寒风暴", "反伤刺甲", "暴烈之甲", "冰痕之握", "怒龙剑盾", "冰霜冲击",
        "旭日初光", "血魔之怒", "巨人之握", "巡守利斧",
    }
    pure_def_items = {
        "红莲斗篷", "霸者重装", "不祥征兆", "不死鸟之眼", "魔女斗篷", "永夜守护",
        "极寒风暴", "冰霜冲击", "旭日初光", "巨人之握",
    }
    def_cnt = sum(1 for it in item_names if it in def_items)
    pure_def_cnt = sum(1 for it in item_names if it in pure_def_items)
    if pure_def_cnt >= 3 or def_cnt >= 4:
        return "纯肉抗伤流"
    if def_cnt == 0 and "纯净苍穹" not in item_names and "时之预言" not in item_names and "破茧之衣" not in item_names:
        return "全输出爆发流"
    return "半肉均衡流"


def evaluate_three_combat_states(
    hero_cname: str,
    item_names: list,
    raw_metrics: dict,
    model: dict,
    lane: str,
) -> Dict[str, Any]:
    """
    100% 基于英雄底层技能机制特征（`model`）与面板/三态实测数值（`raw_metrics`），
    客观计算【状态一：常态期 / 状态二：特殊危机博弈态 / 状态三：关键团战节点】三态得分（零英雄名硬编码）。
    """
    ehp_normal = raw_metrics["ehp_normal_downtime"]
    ehp_special = raw_metrics["ehp_special_crisis"]
    ehp_teamfight = raw_metrics["entry_burst_ehp"]
    fight_heal = raw_metrics.get("total_fight_heal", 0.0)
    eff_mdef = raw_metrics.get("eff_self_mdef", 200.0)
    mag_shield = raw_metrics.get("mag_shield", 0.0)

    dmg_normal = raw_metrics["dmg_normal_downtime"]
    dmg_special = raw_metrics["dmg_special_crisis"]
    dmg_teamfight = raw_metrics["dmg_full_squishy"]

    # 英雄底层机制属性提取（无任何英雄名 if-else）
    orb_mult = model.get("orb_proc_mult", 1.0)
    tether_rel = model.get("tether_reliance", 0.0)
    tier_dr = model.get("passive_dr_bonus", 0.0)
    overheal_shield = model.get("extra_shield_hp_ratio", 0.0)
    ult_missing_ratio = model.get("ult_heal_missing_hp_ratio", 0.50)
    high_heal = (model.get("passive_heal_base", (0.0, 0.0))[1] >= 400) or (model.get("ult_heal_base", (0.0, 0.0))[1] >= 1000)

    # 装备提供的机制属性（由 raw_metrics 传入或客观识别机制属性）
    active_dr = raw_metrics.get("active_dr", 0.0)
    xuemo_ratio = raw_metrics.get("xuemo_ratio", 0.0)
    heal_amp = raw_metrics.get("heal_amp", 0.0)
    nulong_ratio = raw_metrics.get("nulong_max_hp_ratio", 0.0)
    dmg_amp = raw_metrics.get("dmg_amp", 0.0)
    on_hit_orb_power = raw_metrics.get("on_hit_orb_power", 0.0)
    eff_combat_aspeed = raw_metrics.get("eff_combat_aspeed", 0.0)
    tether_comp = raw_metrics.get("tether_completion", 1.0)
    exposure_comp = raw_metrics.get("exposure_completion", 1.0)
    ult_reliability = raw_metrics.get("ult_cast_reliability", 1.0)
    has_mingdao = raw_metrics.get("has_mingdao", False)
    has_frost = raw_metrics.get("has_frost_shock", False)
    has_spellblade = raw_metrics.get("has_spellblade", False)
    pen_flat = raw_metrics.get("pen_flat", 0.0)

    if high_heal:
        div_norm, div_spec, div_tf = 345.0, 455.0, 355.0
        min_safe_tf_ehp = 23500.0
    else:
        div_norm, div_spec, div_tf = 248.0, 285.0, 255.0
        min_safe_tf_ehp = 17500.0

    mage_burst_vulnerability = 0.0
    if eff_mdef < 165.0 and mag_shield == 0:
        mage_burst_vulnerability = (165.0 - eff_mdef) * (0.12 if high_heal else 0.05)

    fragility_penalty = 0.0
    if ehp_teamfight < min_safe_tf_ehp:
        fragility_penalty = ((min_safe_tf_ehp - ehp_teamfight) / 1000.0) * 3.2

    # 1. 状态一：常态期（75s主动技能CD真空期 + 刷野清线 + 常态遭遇拉扯）
    s_norm_surv = min(100.0, ehp_normal / div_norm)
    s_norm_dmg = min(100.0, dmg_normal / 108.0)

    # 机制驱动的常态节奏耦合分（代替原有的按英雄名点名装备加分）：
    # - 刷野/重创被动物流（怒龙剑盾 nulong_ratio、强击法球 spellblade、固定穿透 pen_flat）
    # - 多段法球/攻速魂链英雄（orb_mult > 1.2）：由实际触发的法球强度、实战攻速频率与不断链完成度决定
    # - 常态受击叠层增伤移速（dmg_amp 如暴烈之甲）与法术防御护盾闭环
    mdef_closure_bonus = 4.0 if heal_amp > 0 and high_heal else (3.2 if (eff_mdef >= 180.0 or mag_shield > 0) else 0.0)
    pve_camp_bonus = (5.5 if nulong_ratio > 0 else 0.0) + (2.5 if has_spellblade else 0.0) + (2.2 if pen_flat >= 150.0 else 0.0)
    if orb_mult > 1.2:
        orb_aspeed_synergy = min(7.5, (eff_combat_aspeed / 65.0) * 4.5 + (on_hit_orb_power / 450.0) * 3.5) * tether_comp
        norm_tempo_bonus = orb_aspeed_synergy + 0.75 * pve_camp_bonus + mdef_closure_bonus
    else:
        ramp_synergy = min(6.5, dmg_amp * 65.0)
        norm_tempo_bonus = ramp_synergy + pve_camp_bonus + mdef_closure_bonus

    score_state_normal = round(
        max(20.0, min(100.0, 0.70 * s_norm_surv + 0.18 * s_norm_dmg + norm_tempo_bonus - 0.5 * mage_burst_vulnerability - 0.6 * fragility_penalty)),
        1,
    )

    # 2. 状态二：特殊危机博弈态（残血反杀 / 跨档位刷新 / 法天象地或神巫开大锁血）
    special_synergy = 0.0
    # (A) 血量档位免伤/溢出转盾机制（如赵云 tier_dr > 0, overheal_shield > 0）：受击叠层、主动血怒跨档与重创回血转盾
    if tier_dr > 0 or overheal_shield > 0:
        special_synergy += min(5.5, dmg_amp * 55.0)
        special_synergy += 4.8 if xuemo_ratio > 0 else (4.0 if active_dr > 0 else 0.0)
        special_synergy += 3.0 if nulong_ratio > 0 else 0.0
    # (B) 高回血/残血大招爆发回复机制（如杨戬、大司命 high_heal, ult_missing_ratio >= 0.55）：
    #     需要纯净苍穹/血魔之怒防残血开大前摇被秒（ult_reliability），加上不死鸟之眼放大残血回血量
    if high_heal and ult_missing_ratio >= 0.55:
        special_synergy += (7.0 if active_dr > 0 else (6.2 if xuemo_ratio > 0 else (4.5 if has_frost else 0.0))) * ult_reliability
        if heal_amp > 0:
            special_synergy += 6.2 if (nulong_ratio > 0 or on_hit_orb_power > 200.0) else 3.8
    # (C) 多段魂链法球/线性攻速驱动回血频次机制（orb_mult > 1.2，无攻速阈值档位，纯连续线性收益）：
    if orb_mult > 1.2:
        aspeed_linear_gain = (eff_combat_aspeed / 70.0) * 3.8 + (on_hit_orb_power / 420.0) * 3.2
        special_synergy += (min(6.5, aspeed_linear_gain) - max(0.0, (45.0 - eff_combat_aspeed) * 0.12 if on_hit_orb_power < 150.0 else 0.0)) * tether_comp
    if has_mingdao:
        special_synergy += 4.0

    s_spec_surv = min(100.0, (ehp_special + (fight_heal * 0.9 if high_heal else fight_heal * 0.3)) / div_spec)
    s_spec_dmg = min(100.0, dmg_special / 108.0)
    score_state_special = round(
        max(20.0, min(100.0, 0.68 * s_spec_surv + 0.18 * s_spec_dmg + special_synergy - 0.6 * mage_burst_vulnerability - 0.8 * fragility_penalty)),
        1,
    )

    # 3. 状态三：关键团战节点（5v5进场抗第一波集火 + 持续站场/AOE收割）
    tf_synergy = 0.0
    if orb_mult > 1.2:
        tf_linear_gain = (eff_combat_aspeed / 70.0) * 4.0 + (on_hit_orb_power / 420.0) * 3.8
        tf_synergy += (min(7.5, tf_linear_gain) - max(0.0, (45.0 - eff_combat_aspeed) * 0.12 if on_hit_orb_power < 150.0 else 0.0)) * tether_comp * exposure_comp
    tf_synergy += min(5.5, dmg_amp * 55.0)
    if active_dr > 0:
        tf_synergy += 5.2 * ult_reliability
    elif xuemo_ratio > 0:
        tf_synergy += 5.8 if overheal_shield > 0 else 4.5
    if has_frost:
        tf_synergy += 5.2
    if nulong_ratio > 0 and (heal_amp > 0 or eff_mdef >= 180.0 or mag_shield > 0):
        tf_synergy += 5.2
    elif nulong_ratio > 0:
        tf_synergy += 2.8

    s_tf_surv = min(100.0, (ehp_teamfight + (fight_heal * 0.6 if high_heal else fight_heal * 0.2)) / div_tf)
    s_tf_dmg = min(100.0, dmg_teamfight / 110.0)
    score_state_teamfight = round(
        max(20.0, min(100.0, 0.68 * s_tf_surv + 0.18 * s_tf_dmg + tf_synergy - mage_burst_vulnerability - fragility_penalty)),
        1,
    )

    cfg = get_dynamic_role_lane_weights(hero_cname, lane, model)
    sw = cfg["state_weights"]
    composite_3state_score = round(
        sw["normal"] * score_state_normal
        + sw["special"] * score_state_special
        + sw["teamfight"] * score_state_teamfight,
        2,
    )

    return {
        "official_role_tag": cfg["official_role_tag"],
        "build_style": classify_build_style(item_names),
        "role_profile": cfg["role_profile"],
        "role_weights": cfg["weights"],
        "state_weights": sw,
        "state_normal_score": score_state_normal,
        "state_special_score": score_state_special,
        "state_teamfight_score": score_state_teamfight,
        "composite_3state_score": composite_3state_score,
    }
