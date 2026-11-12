"""出装属性累加：铭文五级属性汇总 + 逐件装备动态属性累加 (build_item_aggregator.py)"""

from config.hero_arcana_data import ARCANA_LEVEL_5_DICT
from src.core.item_ground_truth_db import get_dynamic_item_profile

ITEM_AGG_KEYS = ("bonus_atk", "bonus_hp", "bonus_pdef", "bonus_mdef", "bonus_ap", "cd_raw", "speed_pct", "combat_speed_pct", "speed_flat", "ooc_speed_flat", "aspeed_pct", "combat_aspeed_pct", "crit_rate", "crit_eff", "p_vamp_pct", "item_pen_flat", "pen_pct", "item_m_pen_flat", "m_pen_pct", "raw_eq_ten", "slow_resist", "on_hit_heal", "dmg_amp", "pojun_amp", "passive_dr", "active_dr", "heal_amp", "jg_burn_target_hp_ratio", "nulong_max_hp_ratio", "nulong_heal_max_hp", "wave_clear_score", "monv_shield", "monv_hp_ratio", "monv_mdef_to_pdef", "yongye_base", "yongye_ratio", "xuemo_ratio", "on_hit_phys", "on_hit_max_hp_ratio", "on_hit_magic", "proc_phys_base", "proc_phys_bonus_ad", "proc_magic_base", "proc_magic_hp_ratio", "shield_base", "shield_hp_ratio", "has_mingdao", "has_bazhe", "has_pomo", "has_ice", "has_frost_shock", "has_hat", "has_prophecy", "has_cocoon", "has_sage_book", "has_infinity", "has_frostbite", "best_spellblade", "total_price", "max_gap")


def parse_arcana_totals(arcana_list: list) -> dict:
    totals = {"atk": 0.0, "ap": 0.0, "hp": 0.0, "pdef": 0.0, "mdef": 0.0, "pen_flat": 0.0, "m_pen_flat": 0.0, "aspeed": 0.0, "crit": 0.0, "crit_eff": 0.0, "cd": 0.0, "speed_pct": 0.0, "p_vamp": 0.0}
    mapping = [("atk", "phys_atk"), ("ap", "magic_atk"), ("hp", "max_hp"), ("pdef", "phys_def"), ("mdef", "magic_def"), ("pen_flat", "phys_pierce"), ("m_pen_flat", "magic_pierce"), ("aspeed", "atk_speed_pct"), ("crit", "crit_rate_pct"), ("crit_eff", "crit_effect_pct"), ("cd", "cd_reduction_pct"), ("speed_pct", "move_speed_pct"), ("p_vamp", "phys_vamp_pct")]
    for entry in (arcana_list or []):
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            cnt, aname = entry
            s1 = ARCANA_LEVEL_5_DICT.get(aname, {}).get("stats_1", {})
            for k, sk in mapping:
                totals[k] += s1.get(sk, 0.0) * cnt
    return totals

def aggregate_item_stats(item_names: list, lv: int, jg_stacks: int, arc: dict, base_aspeed: float) -> dict:
    """在铭文属性基础上逐件累加装备属性，返回 ITEM_AGG_KEYS 对应的累加结果"""
    bonus_atk, bonus_hp, bonus_pdef, bonus_mdef, bonus_ap = arc["atk"], arc["hp"], arc["pdef"], arc["mdef"], arc["ap"]
    cd_raw, speed_pct, combat_speed_pct, speed_flat, ooc_speed_flat = arc["cd"], arc["speed_pct"], 0.0, 0.0, 0.0
    aspeed_pct, combat_aspeed_pct, crit_rate, crit_eff, p_vamp_pct = base_aspeed + arc["aspeed"], 0.0, arc["crit"], 200.0 + arc["crit_eff"], arc["p_vamp"]
    item_pen_flat, pen_pct, item_m_pen_flat, m_pen_pct, raw_eq_ten, slow_resist, on_hit_heal = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    dmg_amp, pojun_amp, passive_dr, active_dr, heal_amp = 0.0, 0.0, 0.0, 0.0, 0.0
    jg_burn_target_hp_ratio, nulong_max_hp_ratio, nulong_heal_max_hp, wave_clear_score = 0.0, 0.0, 0.0, 0.0
    monv_shield, monv_hp_ratio, monv_mdef_to_pdef = 0.0, 0.0, 0.0
    yongye_base, yongye_ratio, xuemo_ratio, on_hit_phys, on_hit_max_hp_ratio = 0.0, 0.0, 0.0, 0.0, 0.0
    on_hit_magic, proc_phys_base, proc_phys_bonus_ad, proc_magic_base, proc_magic_hp_ratio = 0.0, 0.0, 0.0, 0.0, 0.0
    shield_base, shield_hp_ratio = 0.0, 0.0
    has_mingdao = has_bazhe = has_pomo = has_ice = has_frost_shock = has_hat = has_prophecy = has_cocoon = has_sage_book = has_infinity = has_frostbite = False
    best_spellblade = None
    total_price, max_gap = 0, 0
    sb_rank = {"zongshi": 4, "binghen": 3, "fuwen": 2, "wushu": 2, "guanghui": 1}

    for raw_name in item_names:
        prof = get_dynamic_item_profile(raw_name, lv=lv, jg_stacks=jg_stacks)
        total_price += prof["price"]; max_gap = max(max_gap, prof["max_gap"])
        bonus_atk += prof["atk"]; bonus_hp += prof["hp"]; bonus_pdef += prof["pdef"]; bonus_mdef += prof["mdef"]; bonus_ap += prof["ap"]
        cd_raw += prof["cd"]; speed_pct += prof["speed_pct"]; combat_speed_pct += prof.get("combat_speed_pct", 0.0)
        aspeed_pct += prof.get("aspeed", 0.0); combat_aspeed_pct += prof.get("combat_aspeed", 0.0)
        crit_rate += prof.get("crit", 0.0); p_vamp_pct += prof.get("p_vamp", 0.0)
        ooc_speed_flat = max(ooc_speed_flat, prof.get("out_of_combat_speed_flat", 0.0))
        raw_eq_ten += prof.get("tenacity", 0.0); slow_resist = max(slow_resist, prof.get("slow_resist", 0.0)); on_hit_heal += prof.get("on_hit_heal", 0.0)
        if prof["speed_flat"] > 0 and speed_flat == 0: speed_flat = prof["speed_flat"]
        item_pen_flat = max(item_pen_flat, prof["pen_flat"]); pen_pct = max(pen_pct, prof["pen_pct"])
        item_m_pen_flat += prof.get("m_pen_flat", 0.0); m_pen_pct = max(m_pen_pct, prof.get("m_pen_pct", 0.0))
        dmg_amp += prof["dmg_amp"]; pojun_amp = max(pojun_amp, prof["pojun_amp"])
        passive_dr = min(0.45, passive_dr + prof["passive_dr"]); active_dr = max(active_dr, prof["active_dr"])
        heal_amp = max(heal_amp, prof["heal_amp"]); jg_burn_target_hp_ratio = max(jg_burn_target_hp_ratio, prof.get("jg_burn_target_hp_ratio", 0.0))
        nulong_max_hp_ratio = max(nulong_max_hp_ratio, prof["nulong_max_hp_ratio"]); nulong_heal_max_hp = max(nulong_heal_max_hp, prof["nulong_heal_max_hp"])
        wave_clear_score += prof["wave_clear_score"]; monv_shield = max(monv_shield, prof["monv_shield"]); monv_hp_ratio = max(monv_hp_ratio, prof["monv_hp_ratio"])
        monv_mdef_to_pdef = max(monv_mdef_to_pdef, prof["monv_mdef_to_pdef"]); yongye_base += prof["yongye_heal_base"]; yongye_ratio += prof["yongye_hp_ratio"]
        xuemo_ratio = max(xuemo_ratio, prof["xuemo_hp_ratio"]); on_hit_phys += prof["on_hit_phys"]; on_hit_max_hp_ratio = max(on_hit_max_hp_ratio, prof["on_hit_max_hp_ratio"])
        on_hit_magic += prof.get("on_hit_magic", 0.0); proc_phys_base += prof.get("proc_phys_base", 0.0); proc_phys_bonus_ad += prof.get("proc_phys_bonus_ad", 0.0)
        proc_magic_base += prof.get("proc_magic_base", 0.0); proc_magic_hp_ratio += prof.get("proc_magic_hp_ratio", 0.0); shield_base += prof.get("shield_base", 0.0); shield_hp_ratio += prof.get("shield_hp_ratio", 0.0)
        has_mingdao |= bool(prof["has_mingdao"]); has_bazhe |= bool(prof["has_bazhe"]); has_pomo |= bool(prof["has_pomo"])
        has_hat |= bool(prof["has_hat"]); has_prophecy |= bool(prof["has_prophecy"]); has_cocoon |= bool(prof["has_cocoon"]); has_sage_book |= bool(prof.get("has_sage_book"))
        has_infinity |= bool(prof.get("has_infinity")); has_frostbite |= (raw_name == "寒霜袭侵")
        has_ice |= (raw_name == "冰痕之握"); has_frost_shock |= (raw_name in ("冰霜冲击", "徐行·凛冬"))
        if prof["spellblade"]:
            if not best_spellblade or sb_rank.get(prof["spellblade"][0], 0) > sb_rank.get(best_spellblade[0], 0):
                best_spellblade = prof["spellblade"]
    _loc = locals()
    return {k: _loc[k] for k in ITEM_AGG_KEYS}
