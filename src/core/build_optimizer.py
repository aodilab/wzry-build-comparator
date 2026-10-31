"""王者荣耀全周期多阶段客观出装推演与【职业×分路×机制+三态主动装备】寻优引擎 (build_optimizer.py)"""

import argparse
import itertools
import json
import sys
from pathlib import Path
from config.hero_base_stats import get_hero_base_stats
from config.hero_arcana_data import ARCANA_LEVEL_5_DICT
from src.core.item_ground_truth_db import get_dynamic_item_profile
from src.core.hero_combo_profiles import HERO_COMBO_PROFILES, extract_hero_skill_model
from src.core.hero_power_curve import analyze_hero_positioning_and_power_curve
from src.core.build_scoring_engine import get_dynamic_role_lane_weights, evaluate_three_combat_states
from src.core.mechanic_taxonomy import C3_STAGE_RAMP_FACTORS, C5_ACTIVE_WINDOW_WEIGHTS, BLUE_BUFF_CYCLE_MODEL, get_hero_c5_coupling

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
with open(ROOT_DIR / "config" / "hero_skills_data.json", "r", encoding="utf-8") as f:
    HERO_SKILLS_DB = json.load(f)
with open(ROOT_DIR / "config" / "official_builds_data.json", "r", encoding="utf-8") as f:
    OFFICIAL_BUILDS_DB = json.load(f)

SPELLBLADE_ITEMS = {"宗师之力", "冰痕之握", "巫术法杖", "符文大剑"}
ACTIVE_ITEMS = {"纯净苍穹", "血魔之怒", "冰霜冲击", "不动·天穹", "侵掠·怒魂", "徐行·凛冬"}


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


def evaluate_hero_build_at_stage(
    hero_cname: str,
    item_names: list,
    lv: int = 15,
    jg_stacks: int = 25,
    arcana_list: list = None,
    lane: str = None,
) -> dict:
    """计算指定英雄在任意等级、分路与装备组合下的【常态期 / 特殊博弈态 / 关键团战态】三态指标与动态加权评分"""
    if arcana_list is None:
        arcana_list = [[9, "异变"], [1, "红月"], [10, "鹰眼"], [10, "狩猎"]] if hero_cname == "杨戬" else [[10, "异变"], [10, "鹰眼"], [10, "隐匿"]]
    if lane is None:
        lane = "打野" if any(k in item_names for k in ("追击刀锋", "贪婪之噬", "巡守利斧", "巨人之握")) else "对抗"

    arc = parse_arcana_totals(arcana_list)
    base_cfg = get_hero_base_stats(0, hero_cname) or {}
    r = max(0.0, min(1.0, (lv - 1) / 14.0))

    hp0, hp15 = base_cfg.get("hp", (3225, 7035)); atk0, atk15 = base_cfg.get("atk", (176, 386))
    pdef0, pdef15 = base_cfg.get("pdef", (102, 396)); mdef0, mdef15 = base_cfg.get("mdef", (50, 169))
    base_speed = base_cfg.get("speed", 380)
    b_hp, b_atk = round(hp0 + (hp15 - hp0) * r), round(atk0 + (atk15 - atk0) * r)
    b_pdef, b_mdef = round(pdef0 + (pdef15 - pdef0) * r), round(mdef0 + (mdef15 - mdef0) * r)

    bonus_atk, bonus_hp, bonus_pdef, bonus_mdef, bonus_ap = arc["atk"], arc["hp"], arc["pdef"], arc["mdef"], arc["ap"]
    cd_raw, speed_pct, combat_speed_pct, speed_flat, ooc_speed_flat = arc["cd"], arc["speed_pct"], 0.0, 0.0, 0.0
    item_pen_flat, pen_pct, item_m_pen_flat, m_pen_pct, raw_eq_ten, slow_resist, on_hit_heal = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    dmg_amp, pojun_amp, passive_dr, active_dr, heal_amp = 0.0, 0.0, 0.0, 0.0, 0.0
    jg_burn_target_hp_ratio, nulong_max_hp_ratio, nulong_heal_max_hp, wave_clear_score = 0.0, 0.0, 0.0, 0.0
    monv_shield, monv_hp_ratio, monv_mdef_to_pdef = 0.0, 0.0, 0.0
    yongye_base, yongye_ratio, xuemo_ratio, on_hit_phys, on_hit_max_hp_ratio = 0.0, 0.0, 0.0, 0.0, 0.0
    on_hit_magic, proc_phys_base, proc_phys_bonus_ad, proc_magic_base, proc_magic_hp_ratio = 0.0, 0.0, 0.0, 0.0, 0.0
    shield_base, shield_hp_ratio = 0.0, 0.0
    has_mingdao = has_bazhe = has_pomo = has_ice = has_frost_shock = has_hat = has_prophecy = has_cocoon = has_sage_book = False
    best_spellblade = None
    total_price, max_gap = 0, 0
    sb_rank = {"zongshi": 4, "binghen": 3, "fuwen": 2, "wushu": 2, "guanghui": 1}

    for raw_name in item_names:
        prof = get_dynamic_item_profile(raw_name, lv=lv, jg_stacks=jg_stacks)
        total_price += prof["price"]; max_gap = max(max_gap, prof["max_gap"])
        bonus_atk += prof["atk"]; bonus_hp += prof["hp"]; bonus_pdef += prof["pdef"]; bonus_mdef += prof["mdef"]; bonus_ap += prof["ap"]
        cd_raw += prof["cd"]; speed_pct += prof["speed_pct"]; combat_speed_pct += prof.get("combat_speed_pct", 0.0)
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
        has_ice |= (raw_name == "冰痕之握"); has_frost_shock |= (raw_name in ("冰霜冲击", "徐行·凛冬"))
        if prof["spellblade"]:
            if not best_spellblade or sb_rank.get(prof["spellblade"][0], 0) > sb_rank.get(best_spellblade[0], 0):
                best_spellblade = prof["spellblade"]

    if has_bazhe: bonus_hp += round(bonus_hp * 0.04)
    if has_cocoon:
        bonus_ap += min(100.0, 20.0 + 20.0 * r + 0.02 * bonus_hp)
        item_m_pen_flat += min(150.0, 30.0 + 30.0 * r + 0.03 * bonus_hp)
    if has_hat: bonus_ap = round(bonus_ap * 1.30)
    if has_prophecy:
        prop_def = 50.0 + 50.0 * r + 0.10 * bonus_ap
        bonus_pdef += prop_def; bonus_mdef += prop_def
    if has_sage_book:
        sage_r = (bonus_ap // 100.0) * 0.005
        dmg_amp += sage_r; passive_dr = min(0.45, passive_dr + sage_r)
    model = extract_hero_skill_model(hero_cname)
    passive_dr = min(0.45, passive_dr + model.get("passive_dr_bonus", 0.0))
    total_atk = b_atk + bonus_atk; total_hp = b_hp + bonus_hp
    combat_max_hp = total_hp + model.get("combat_flat_hp_bonus", 0.0)
    if has_pomo: bonus_mdef += min(250.0, round(total_atk * 0.50))
    if monv_mdef_to_pdef > 0: bonus_pdef += round(bonus_mdef * monv_mdef_to_pdef)
    total_pdef = b_pdef + bonus_pdef; total_mdef = b_mdef + bonus_mdef
    pen_flat = arc["pen_flat"] + item_pen_flat
    m_pen_flat = arc.get("m_pen_flat", 0.0) + item_m_pen_flat
    cd_eff = min(40.0, cd_raw); cd_blue = min(40.0, cd_raw + 20.0)
    roam_speed = round((base_speed + speed_flat + 0.5 * ooc_speed_flat) * (1.0 + speed_pct / 100.0))
    combat_speed = round((base_speed + speed_flat) * (1.0 + (speed_pct + 0.75 * combat_speed_pct) / 100.0))
    s1_r, s2_r = min(1.0, max(0.0, (lv - 1) / 8.0)), min(1.0, max(0.0, (lv - 2) / 10.0))
    s3_lv = 3 if lv >= 12 else (2 if lv >= 8 else (1 if lv >= 4 else 0))
    s3_r = (s3_lv - 1) / 2.0 if s3_lv > 0 else 0.0

    on_hit_total = on_hit_phys + combat_max_hp * on_hit_max_hp_ratio
    s1_dmg = (model["s1_base"][0] + (model["s1_base"][1] - model["s1_base"][0]) * s1_r) + model["s1_bonus_ad"] * bonus_atk
    s2_dmg = (model["s2_base"][0] + (model["s2_base"][1] - model["s2_base"][0]) * s2_r) + model["s2_bonus_ad"] * bonus_atk
    s3_dmg = ((model["s3_base"][0] + (model["s3_base"][1] - model["s3_base"][0]) * s3_r) + model["s3_bonus_ad"] * bonus_atk) if s3_lv > 0 else 0.0
    el0, el1 = model.get("electro_base", (0.0, 0.0))
    electro_dmg = ((el0 + (el1 - el0) * s3_r) + model.get("electro_bonus_ap", 0.0) * bonus_ap) if s3_lv > 0 else 0.0
    ty0, ty1 = model.get("tianyan_base", (0.0, 0.0))
    tianyan_dmg = (ty0 + (ty1 - ty0) * r) + model.get("tianyan_bonus_ad", 0.0) * bonus_atk
    enh_aa_dmg = (model["enh_aa_base"][0] + (model["enh_aa_base"][1] - model["enh_aa_base"][0]) * r) + model.get("enh_aa_total_ad", 0.0) * total_atk + model.get("enh_aa_bonus_ad", 0.0) * bonus_atk + (on_hit_total if model.get("enh_aa_total_ad", 0.0) > 0 else 0.0)
    aa_dmg = 1.0 * total_atk + on_hit_total
    tb0, tb1 = model.get("true_hit_base", (0.0, 0.0))
    true_1hit = (tb0 + (tb1 - tb0) * s2_r) + model.get("true_hit_bonus_ad", 0.0) * bonus_atk

    sb_1hit, sb_cd = 0.0, 3.0
    if best_spellblade:
        _, sb_cd, sb_base, sb_tot_ad, sb_bon_ad, _ = best_spellblade
        sb_1hit = sb_base + sb_tot_ad * total_atk + sb_bon_ad * bonus_atk

    stickiness = 1.0 + (0.030 if has_ice else (0.025 if has_frost_shock else 0.0))
    if combat_speed >= 505:
        stickiness += 0.020 * min(1.5, (combat_speed - 490) / 25.0)

    xm_coup = get_hero_c5_coupling(hero_cname, "血魔之怒") if xuemo_ratio > 0 else {}
    cq_coup = get_hero_c5_coupling(hero_cname, "纯净苍穹") if active_dr > 0 else {}

    def eval_hit_profile(hd: dict, default_sb: tuple, nulong_procs: float, apply_stickiness: bool = False, active_ready: bool = True):
        sb_p = hd.get("sb_procs", default_sb)
        sb_cnt = sb_p[0] if sb_cd <= 1.5 else sb_p[1]
        st_m = stickiness if apply_stickiness else 1.0
        zy_br_bonus = (xm_coup.get("extra_s1_casts_teamfight", 0.0) if apply_stickiness else xm_coup.get("extra_s1_casts_burst", 0.0)) if active_ready else 0.0
        yj_s3_bonus = (cq_coup.get("extra_s3_casts_teamfight", 0.0) if (apply_stickiness and active_ready) else 0.0)
        extra_sb = (0.50 * zy_br_bonus) if (zy_br_bonus > 0 and sb_1hit > 0) else 0.0
        tot_aa = (hd.get("enh_aa", 0) + zy_br_bonus + hd.get("aa", 0)) * st_m
        p_raw = ((hd.get("s1", 0) + zy_br_bonus) * s1_dmg + (hd.get("s2", 0) * st_m) * s2_dmg + (hd.get("s3_phys", 0) + yj_s3_bonus) * s3_dmg
                 + hd.get("tianyan", 0) * tianyan_dmg + ((hd.get("enh_aa", 0) + zy_br_bonus) * st_m) * enh_aa_dmg + (hd.get("aa", 0) * st_m) * aa_dmg
                 + (sb_cnt + extra_sb) * sb_1hit + nulong_procs * (combat_max_hp * nulong_max_hp_ratio)
                 + ((proc_phys_base + proc_phys_bonus_ad * bonus_atk) if active_ready else 0.0))
        m_raw = hd.get("s3_mag", 0) * s3_dmg + hd.get("electro_mag", 0) * electro_dmg + tot_aa * on_hit_magic + proc_magic_base + combat_max_hp * proc_magic_hp_ratio
        t_raw = (hd.get("true_on_hit", 0) * st_m) * true_1hit
        return p_raw, m_raw, t_raw, hd.get("exec_missing_pct", 0.0)

    def calc_mit(p_raw, m_raw, t_raw, exec_pct, t_pdef, t_mdef, t_hp, amp_scale=0.65):
        eff_p = max(0.0, (t_pdef - pen_flat) * (1.0 - pen_pct / 100.0))
        eff_m = max(0.0, (t_mdef - m_pen_flat) * (1.0 - m_pen_pct / 100.0))
        p_mult, m_mult = 602.0 / (602.0 + eff_p), 602.0 / (602.0 + eff_m)
        amp = (1.0 + dmg_amp * amp_scale) * (1.0 + 0.45 * pojun_amp)
        jg_burn_dmg = jg_burn_target_hp_ratio * t_hp
        base_dealt = ((p_raw + jg_burn_dmg) * p_mult + m_raw * m_mult + t_raw) * amp
        if exec_pct > 0:
            base_dealt += (min(t_hp, max(0.25 * t_hp, 0.75 * base_dealt)) * exec_pct) * p_mult * amp
        return round(base_dealt)

    sq_p, sq_m, sq_hp = round(100 + 250 * r), round(60 + 140 * r), round(3200 + 2800 * r)
    br_p, br_m, br_hp = round(180 + 440 * r), round(80 + 220 * r), round(3800 + 4700 * r)
    tk_p, tk_m, tk_hp = round(250 + 850 * r), round(120 + 480 * r), round(4500 + 8500 * r)

    bh, fh = model["burst_hits"], model["full_hits"]
    r_burst, r_norm, r_tf = C3_STAGE_RAMP_FACTORS["burst_2s"], C3_STAGE_RAMP_FACTORS["normal_skirmish"], C3_STAGE_RAMP_FACTORS["sustained_tf"]
    dmg_2s_sq = calc_mit(*eval_hit_profile(bh, (2.0, 1.0), 1.0, False, True), sq_p, sq_m, sq_hp, amp_scale=r_burst)
    dmg_2s_br = calc_mit(*eval_hit_profile(bh, (2.0, 1.0), 1.0, False, True), br_p, br_m, br_hp, amp_scale=r_burst)
    dmg_full_sq = calc_mit(*eval_hit_profile(fh, (3.0, 2.0), 2.0, True, True), sq_p, sq_m, sq_hp, amp_scale=0.70)
    dmg_full_br = calc_mit(*eval_hit_profile(fh, (3.0, 2.0), 2.0, True, True), br_p, br_m, br_hp, amp_scale=r_tf)
    dmg_full_tk = calc_mit(*eval_hit_profile(fh, (3.0, 2.0), 2.0, True, True), tk_p, tk_m, tk_hp, amp_scale=r_tf)
    dmg_normal_downtime = calc_mit(*eval_hit_profile(fh, (3.0, 2.0), 2.0, True, False), sq_p, sq_m, sq_hp, amp_scale=r_norm)
    dmg_special_crisis = round(0.55 * dmg_full_sq + 0.45 * dmg_full_br)

    kh, mh, mlh, aoeh = model.get("kite_hits", fh), model.get("mid_hits", fh), model.get("melee_hits", fh), model.get("aoe_hits", fh)
    dmg_kite_sq = calc_mit(*eval_hit_profile(kh, (1.2, 1.0), 1.5, True, True), sq_p, sq_m, sq_hp)
    dmg_mid_sq = calc_mit(*eval_hit_profile(mh, (1.8, 1.3), 2.0, True, True), sq_p, sq_m, sq_hp)
    dmg_melee_sq = calc_mit(*eval_hit_profile(mlh, (2.5, 1.8), 2.0, True, True), sq_p, sq_m, sq_hp)
    dmg_aoe_br = calc_mit(*eval_hit_profile(aoeh, (1.6, 1.2), 2.0 * aoeh.get("nulong_mult", 1.0), True, True), br_p, br_m, br_hp)

    s1_cd = round((model["s1_cd"][0] + (model["s1_cd"][1] - model["s1_cd"][0]) * s1_r) * (1.0 - cd_eff / 100.0), 2)
    s2_cd = round((model["s2_cd"][0] + (model["s2_cd"][1] - model["s2_cd"][0]) * s2_r) * (1.0 - cd_eff / 100.0), 2)
    s3_cd = round((model["s3_cd"][min(2, max(0, s3_lv - 1))] if s3_lv > 0 else model["s3_cd"][0]) * (1.0 - cd_eff / 100.0), 2)

    hb0, hb1 = model["passive_heal_base"]
    heal_skill_r = s3_r if hb0 >= 250.0 else s2_r
    missing_ten_blocks = (model.get("ult_heal_missing_hp_ratio", 0.50) * 10.0)
    eff_heal_amp = max(heal_amp, missing_ten_blocks * 0.065) if heal_amp > 0 else 0.0
    anti_heal_mult = max(0.30, 1.0 - 0.35 * r + eff_heal_amp)
    heal_per_proc = round(((hb0 + (hb1 - hb0) * heal_skill_r) + model["passive_heal_bonus_hp"] * bonus_hp) * anti_heal_mult)
    # 怒龙剑盾被动【重创】仅对兵线/野怪回血，英雄团战按波及兵野0.25次期望折算
    nulong_heal_total = 0.25 * (combat_max_hp * nulong_heal_max_hp) * (1.0 + eff_heal_amp)
    yongye_heal_total = (yongye_base + combat_max_hp * yongye_ratio) * (1.0 + eff_heal_amp) if (yongye_base > 0 or yongye_ratio > 0) else 0.0
    total_fight_heal = round(model["heal_procs_per_fight"] * heal_per_proc + nulong_heal_total + yongye_heal_total + 4.0 * on_hit_heal * (1.0 + eff_heal_amp))
    star_tuple = model.get("star_shatter_by_ult", (0.0, 0.0, 0.0, 0.0))
    alpha = star_tuple[s3_lv] if s3_lv < len(star_tuple) else 0.0
    star_mult = 1.0 / (1.0 - 0.65 * alpha) if alpha > 0 else 1.0
    eff_self_pdef, eff_self_mdef = max(0.0, (total_pdef - 240.0 * r) * (1.0 - 0.30 * r)), max(0.0, (total_mdef - 150.0 * r) * (1.0 - 0.45 * r))
    p_mit_factor, m_mit_factor = 0.88 * (1.0 + eff_self_pdef / 602.0) + 0.12, 0.88 * (1.0 + eff_self_mdef / 602.0) + 0.12
    mag_shield = (monv_shield + bonus_hp * monv_hp_ratio) if monv_shield > 0 else 0.0
    item_shield = shield_base + combat_max_hp * shield_hp_ratio
    eff_eq_ten = min(raw_eq_ten, model.get("equip_tenacity_cap", 0.60))
    innate_w = model.get("tenacity_synergy_mult", 0.45 if model.get("innate_tenacity", 0.0) >= 0.50 else 1.0)
    tenacity_bonus = 0.91 if (model.get("requires_tenacity_boots") and eff_eq_ten < 0.10) else (1.0 + eff_eq_ten * 0.22 * innate_w + slow_resist * 0.015)

    eff_m_with_shield = m_mit_factor * (1.0 + (0.45 * mag_shield) / max(1.0, total_hp))
    arith_mit, harm_mit = 0.62 * p_mit_factor + 0.38 * eff_m_with_shield, 1.0 / (0.62 / p_mit_factor + 0.38 / eff_m_with_shield)
    balanced_mit, dr_normal, shield_perm = 0.68 * arith_mit + 0.32 * harm_mit, 1.0 / (1.0 - 0.70 * passive_dr), total_hp * model.get("extra_shield_hp_ratio", 0.0)
    hp_normal = total_hp + total_fight_heal * 0.85 + model.get("combat_flat_hp_bonus", 0.0) + shield_perm + item_shield * 0.70
    ehp_normal_downtime = round(hp_normal * balanced_mit * star_mult * dr_normal * tenacity_bonus)

    w_act_spec = min(0.80, C5_ACTIVE_WINDOW_WEIGHTS["state_special_crisis"] + cq_coup.get("crisis_dr_window_bonus", 0.0))
    dr_special = 1.0 / ((1.0 - 0.75 * passive_dr) * (1.0 - w_act_spec * active_dr))
    xm_crisis_r = xm_coup.get("crisis_net_shield_ratio", 0.22) if xuemo_ratio > 0 else 0.0
    cq_heal_m = cq_coup.get("heal_preserve_mult", 1.0)
    hp_special = total_hp + total_fight_heal * 0.95 * cq_heal_m + model.get("combat_flat_hp_bonus", 0.0) + shield_perm + combat_max_hp * xm_crisis_r + item_shield
    ehp_special_crisis = round(hp_special * balanced_mit * star_mult * dr_special * (1.14 if has_mingdao else 1.0) * tenacity_bonus)

    w_act_tf = min(0.80, C5_ACTIVE_WINDOW_WEIGHTS["state_teamfight_peak"] + cq_coup.get("teamfight_dr_window_bonus", 0.0))
    dr_peak = 1.0 / ((1.0 - 0.70 * passive_dr) * (1.0 - w_act_tf * active_dr))
    xm_tf_r = xm_coup.get("teamfight_net_shield_ratio", 0.16) if xuemo_ratio > 0 else 0.0
    peak_raw_hp = total_hp + model.get("combat_flat_hp_bonus", 0.0) + shield_perm + combat_max_hp * xm_tf_r + item_shield + 0.65 * total_fight_heal * cq_heal_m
    entry_burst_ehp = round(peak_raw_hp * balanced_mit * star_mult * dr_peak * (1.12 if has_mingdao else 1.0) * tenacity_bonus)

    mixed_ehp = round(0.42 * ehp_normal_downtime + 0.25 * ehp_special_crisis + 0.33 * entry_burst_ehp)
    phys_ehp, mag_ehp = round(mixed_ehp * (p_mit_factor / arith_mit)), round(mixed_ehp * (eff_m_with_shield / arith_mit))
    mob_score, eff_speed_for_tempo = model.get("mobility_score", 0.70), 0.65 * roam_speed + 0.35 * combat_speed
    tempo_mult = (1.0 + min(0.10, wave_clear_score)) * (1.0 + (1.0 - mob_score) * 0.14 * max(0.0, (eff_speed_for_tempo - 470.0) / 100.0))
    if model.get("needs_red_jg_early_tempo") and any(k in item_names for k in ("巡守利斧", "巨人之握")) and not any("黄盾" in k or "怒龙剑盾" in k for k in item_names):
        tempo_mult *= 0.94

    raw_state_metrics = {
        "ehp_normal_downtime": ehp_normal_downtime, "ehp_special_crisis": ehp_special_crisis, "entry_burst_ehp": entry_burst_ehp,
        "total_fight_heal": total_fight_heal, "eff_self_mdef": eff_self_mdef, "mag_shield": mag_shield,
        "dmg_normal_downtime": dmg_normal_downtime, "dmg_special_crisis": dmg_special_crisis, "dmg_full_squishy": dmg_full_sq,
    }
    state_eval = evaluate_three_combat_states(hero_cname, item_names, raw_state_metrics, model, lane)
    rw = state_eval["role_weights"]

    is_frontline_aoe_warrior = model.get("passive_heal_base", (0.0, 0.0))[1] >= 400
    has_heiqie = "暗影战斧" in item_names
    is_tank_jg = "巨人之握" in item_names
    early_mid_tempo_bonus = 5.5 if (has_heiqie or is_tank_jg) else -4.5

    eff_full_sq = 0.52 * dmg_full_sq + 0.48 * dmg_normal_downtime
    if is_frontline_aoe_warrior:
        burst_kill_score = min(100.0, (0.30 * dmg_2s_sq + 0.35 * eff_full_sq + 0.18 * dmg_full_br + 0.17 * dmg_aoe_br) / 96.0 + (2.5 if has_heiqie else 0.0))
    else:
        burst_kill_score = min(100.0, (0.38 * dmg_2s_sq + 0.42 * eff_full_sq + 0.20 * dmg_full_br) / 96.0 + (2.5 if has_heiqie else 0.0))

    surv_3state_score = state_eval["composite_3state_score"]
    nulong_pve_dps = (combat_max_hp * nulong_max_hp_ratio) / 55.0
    pve_clear_sub = min(100.0, 36.0 + wave_clear_score * 130.0 + nulong_pve_dps + (dmg_full_br / 620.0))
    roam_mob_sub = min(100.0, 42.0 + max(0.0, (0.65 * roam_speed + 0.35 * combat_speed) - 440.0) * 0.65)
    pve_roam_score = round(0.65 * pve_clear_sub + 0.35 * roam_mob_sub, 1)

    u_blue, g_blue = BLUE_BUFF_CYCLE_MODEL["uptime_ratio"], BLUE_BUFF_CYCLE_MODEL["renewal_gap_ratio"]
    gap_cliff_pen = max(0.0, BLUE_BUFF_CYCLE_MODEL["safe_base_cdr_threshold"] - cd_eff) * 0.85 * g_blue
    cd_score_no_blue = min(100.0, 45.0 + (cd_eff / 40.0) * 55.0)
    cd_score_with_blue = max(40.0, min(100.0, 45.0 + (u_blue * (cd_blue / 40.0) + g_blue * (cd_eff / 40.0)) * 55.0 - gap_cliff_pen))
    cc_bonus = 10.0 if has_ice else (8.5 if has_frost_shock else 0.0)
    stickiness_cc_score = min(100.0, 45.0 + max(0.0, (0.4 * roam_speed + 0.6 * combat_speed) - 440.0) * 0.45 + cc_bonus)
    econ_penalty = max(0.0, (total_price - 11000) / 45.0) + max(0.0, (max_gap - 900) / 35.0)
    econ_sub = max(40.0, min(100.0, 95.0 - econ_penalty + early_mid_tempo_bonus))
    pen_sustain_sub = min(100.0, (dmg_full_tk / 95.0) * 0.35 + (total_fight_heal / 70.0) * 0.65)
    econ_sustain_score = 0.48 * econ_sub + 0.52 * pen_sustain_sub

    base_w_sum = rw["burst_kill"] * burst_kill_score + rw["surv_3state"] * surv_3state_score + rw["pve_roam"] * pve_roam_score + rw["stickiness_cc"] * stickiness_cc_score + rw["econ_sustain"] * econ_sustain_score
    score_no_blue = round(base_w_sum + rw["cdr_cycle"] * cd_score_no_blue, 2)
    score_with_blue = round(base_w_sum + rw["cdr_cycle"] * cd_score_with_blue, 2)

    return {
        "items": item_names, "lane": lane, "role_profile": state_eval["role_profile"], "price": total_price, "max_gap": max_gap,
        "total_atk": round(total_atk), "bonus_atk": round(bonus_atk), "total_hp": round(total_hp), "bonus_hp": round(bonus_hp),
        "total_pdef": round(total_pdef), "total_mdef": round(total_mdef), "cd_raw": round(cd_raw, 1), "cd_eff": round(cd_eff, 1),
        "cd_blue": round(cd_blue, 1), "pen_flat": round(pen_flat, 1), "pen_pct": round(pen_pct, 1), "move_speed": roam_speed,
        "combat_speed": combat_speed, "s1_cd": s1_cd, "s2_cd": s2_cd, "s3_cd": s3_cd, "heal_per_proc": heal_per_proc,
        "total_fight_heal": total_fight_heal, "ehp_normal_downtime": ehp_normal_downtime, "ehp_special_crisis": ehp_special_crisis,
        "entry_burst_ehp": entry_burst_ehp, "phys_ehp": phys_ehp, "mag_ehp": mag_ehp, "mixed_ehp": mixed_ehp,
        "wave_clear_mult": round(tempo_mult, 3), "dmg_2s_squishy": dmg_2s_sq, "dmg_2s_bruiser": dmg_2s_br,
        "dmg_kite_squishy": dmg_kite_sq, "dmg_mid_squishy": dmg_mid_sq, "dmg_melee_squishy": dmg_melee_sq,
        "dmg_aoe_bruiser": dmg_aoe_br, "dmg_full_squishy": dmg_full_sq, "dmg_full_bruiser": dmg_full_br,
        "dmg_full_tank": dmg_full_tk, "dmg_per_1k_gold": round(dmg_2s_sq / max(1.0, total_price / 1000.0)),
        "state_scores": {"normal": state_eval["state_normal_score"], "special": state_eval["state_special_score"], "teamfight": state_eval["state_teamfight_score"], "composite_3state": state_eval["composite_3state_score"]},
        "sub_scores": {"burst_kill": round(burst_kill_score, 1), "surv_3state": round(surv_3state_score, 1), "pve_roam": round(pve_roam_score, 1), "cd_nb": round(cd_score_no_blue, 1), "cd_wb": round(cd_score_with_blue, 1), "stickiness_cc": round(stickiness_cc_score, 1), "econ_sustain": round(econ_sustain_score, 1)},
        "score_no_blue": score_no_blue, "score_with_blue": score_with_blue,
    }


def optimize_hero_lifecycle(hero_cname: str, is_jungle: bool = True) -> dict:
    """运行全周期三阶段自动推演"""
    model = extract_hero_skill_model(hero_cname)
    boots_list = model.get("boots_candidates", ["抵抗之靴"])
    lane_key = "打野" if is_jungle else "对抗"

    if is_jungle:
        early_paths = [(f"红刀+{b[:2]}鞋+陨星+铁剑", ["追击刀锋", b, "陨星", "铁剑"], 6, 8) for b in ("抵抗之靴", "冷静之靴", "影忍之足")] + [("肉刀+抵抗鞋+陨星+铁剑", ["巡守利斧", "抵抗之靴", "陨星", "铁剑"], 6, 8), ("红刀+抵抗鞋+暗影战斧", ["追击刀锋", "抵抗之靴", "暗影战斧"], 7, 10)]
        base3 = ["追击刀锋", boots_list[0], "暗影战斧"]
    else:
        early_paths = [("冷静鞋+陨星+荆棘护手", ["冷静之靴", "陨星", "荆棘护手"], 6, 0), ("影忍足+陨星+荆棘护手", ["影忍之足", "陨星", "荆棘护手"], 6, 0), ("抵抗鞋+陨星+日冕", ["抵抗之靴", "陨星", "日冕"], 6, 0)] + [(f"{b[:2]}鞋+暗影战斧+荆棘护手", [b, "暗影战斧", "荆棘护手"], 7, 0) for b in ("冷静之靴", "抵抗之靴")]
        base3 = [boots_list[0], "暗影战斧"]

    eval_fn = lambda it, lv, st: evaluate_hero_build_at_stage(hero_cname, it, lv=lv, jg_stacks=st, lane=lane_key)
    stage1_early = [{**eval_fn(it, lv, st), "label": lb} for lb, it, lv, st in early_paths]
    mid_candidates = ["冰痕之握", "暴烈之甲", "纯净苍穹", "宗师之力", "强者破军", "怒龙剑盾", "碎星锤", "不死鸟之眼", "血魔之怒", "冰霜冲击"]
    stage2_mid4 = [{**eval_fn(base3 + [m4], 10, 16 if is_jungle else 0), "label": f"单核:{m4}"} for m4 in mid_candidates]
    mid5_pairs = [("怒龙剑盾", "不死鸟之眼"), ("冰痕之握", "怒龙剑盾"), ("怒龙剑盾", "血魔之怒"), ("冰痕之握", "纯净苍穹"), ("暴烈之甲", "纯净苍穹"), ("冰痕之握", "暴烈之甲"), ("纯净苍穹", "不死鸟之眼"), ("纯净苍穹", "怒龙剑盾")]
    stage2_mid5 = [{**eval_fn(base3 + [a, b], 12, 20 if is_jungle else 0), "label": f"双核:{a}+{b}"} for a, b in mid5_pairs]

    pool_18 = ["暗影战斧", "宗师之力", "冰痕之握", "暴烈之甲", "纯净苍穹", "强者破军", "碎星锤", "怒龙剑盾", "血魔之怒", "冰霜冲击", "霸者重装", "名刀·司命", "魔女斗篷", "永夜守护", "不死鸟之眼", "反伤刺甲", "不祥征兆", "极寒风暴"]
    all_late = [
        eval_fn(([jg, boot] if jg else [boot]) + list(combo), 15, 25 if is_jungle else 0)
        for jg in (["贪婪之噬", "巨人之握"] if is_jungle else [None])
        for boot in boots_list
        for combo in itertools.combinations(pool_18, 4 if is_jungle else 5)
        if len(SPELLBLADE_ITEMS.intersection(combo)) <= 1 and len(ACTIVE_ITEMS.intersection(combo)) <= 1
    ]

    for res in all_late:
        s = res["sub_scores"]
        res["score_balanced"] = res["score_no_blue"]
        res["score_snowball"] = round(0.45 * s["burst_kill"] + 0.18 * s["surv_3state"] + 0.15 * s["pve_roam"] + 0.12 * s["cd_wb"] + 0.10 * s["stickiness_cc"], 2)
        res["score_behind"] = round(0.42 * s["surv_3state"] + 0.22 * s["burst_kill"] + 0.16 * s["cd_nb"] + 0.12 * s["econ_sustain"] + 0.08 * s["stickiness_cc"], 2)
        res["score_antitank"] = round(0.40 * s["econ_sustain"] + 0.28 * s["burst_kill"] + 0.20 * s["surv_3state"] + 0.12 * s["cd_nb"], 2)

    official_audit = [{**eval_fn(b.get("items", []), 15, 25 if is_jungle else 0), "label": f"官方-{b.get('title', '')}"} for b in OFFICIAL_BUILDS_DB.get(hero_cname, {}).get("lanes", {}).get(lane_key, [])]
    official_audit += [{**eval_fn(vi, 15, 25 if is_jungle else 0), "label": vl} for vl, vi in model.get("viral_builds_jg" if is_jungle else "viral_builds_lane", [])]
    top5 = lambda k: sorted(all_late, key=lambda x: x[k], reverse=True)[:5]

    return {
        "hero": hero_cname, "lane": lane_key, "total_combinations_searched": len(all_late), "hero_positioning": analyze_hero_positioning_and_power_curve(hero_cname),
        "stage1_early": stage1_early, "stage2_mid4": sorted(stage2_mid4, key=lambda x: x["score_no_blue"], reverse=True), "stage2_mid5": sorted(stage2_mid5, key=lambda x: x["score_no_blue"], reverse=True),
        "pareto_balanced": top5("score_no_blue"), "pareto_with_blue": top5("score_with_blue"), "pareto_snowball": top5("score_snowball"), "pareto_behind": top5("score_behind"), "pareto_antitank": top5("score_antitank"), "official_audit": official_audit,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--hero", default="赵云"); p.add_argument("--lane", default="打野", choices=["打野", "对抗"])
    a = p.parse_args()
    rep = optimize_hero_lifecycle(a.hero, is_jungle=(a.lane == "打野"))
    fmt = lambda lbl, r: f"[{lbl}] {' + '.join(r['items'])} | 无蓝:{r['score_no_blue']} 有蓝:{r['score_with_blue']} | 三态EHP[常:{r['ehp_normal_downtime']}/特:{r['ehp_special_crisis']}/团:{r['entry_burst_ehp']}] | 三态分[常:{r['state_scores']['normal']}/特:{r['state_scores']['special']}/团:{r['state_scores']['teamfight']}->合:{r['state_scores']['composite_3state']}]"
    print(f"=== [{a.hero}·{a.lane}] 全周期推演完成 ({rep['pareto_balanced'][0]['role_profile']}) ===")
    for tag, key in [("无蓝综合最优", "pareto_balanced"), ("有蓝综合最优", "pareto_with_blue"), ("顺风切C最优", "pareto_snowball"), ("逆风容错最优", "pareto_behind")]:
        print(fmt(tag, rep[key][0]))
    for oa in rep["official_audit"]:
        print(fmt(oa["label"], oa))

