"""王者荣耀全周期多阶段客观出装推演与帕累托寻优引擎 (build_optimizer.py)"""

import argparse
import itertools
import json
import re
import sys
from pathlib import Path
from config.hero_base_stats import get_hero_base_stats
from config.hero_arcana_data import ARCANA_LEVEL_5_DICT
from src.core.item_ground_truth_db import get_dynamic_item_profile

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
with open(ROOT_DIR / "config" / "hero_skills_data.json", "r", encoding="utf-8") as f:
    HERO_SKILLS_DB = json.load(f)
with open(ROOT_DIR / "config" / "official_builds_data.json", "r", encoding="utf-8") as f:
    OFFICIAL_BUILDS_DB = json.load(f)

SPELLBLADE_ITEMS = {"宗师之力", "冰痕之握", "巫术法杖", "光辉之剑", "符文大剑"}

from src.core.hero_combo_profiles import HERO_COMBO_PROFILES, extract_hero_skill_model


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
) -> dict:
    """计算指定英雄在任意等级(lv)、打野刀层数(jg_stacks)与装备列表下的全维实战指标"""
    if arcana_list is None:
        arcana_list = [[10, "异变"], [10, "鹰眼"], [10, "隐匿"]]
    arc = parse_arcana_totals(arcana_list)
    base_cfg = get_hero_base_stats(0, hero_cname) or {}
    r = max(0.0, min(1.0, (lv - 1) / 14.0))

    hp0, hp15 = base_cfg.get("hp", (3225, 7035))
    atk0, atk15 = base_cfg.get("atk", (176, 386))
    pdef0, pdef15 = base_cfg.get("pdef", (102, 396))
    mdef0, mdef15 = base_cfg.get("mdef", (50, 169))
    base_speed = base_cfg.get("speed", 380)

    b_hp = round(hp0 + (hp15 - hp0) * r)
    b_atk = round(atk0 + (atk15 - atk0) * r)
    b_pdef = round(pdef0 + (pdef15 - pdef0) * r)
    b_mdef = round(mdef0 + (mdef15 - mdef0) * r)

    bonus_atk, bonus_hp, bonus_pdef, bonus_mdef = arc["atk"], arc["hp"], arc["pdef"], arc["mdef"]
    cd_raw, speed_pct, combat_speed_pct, speed_flat = arc["cd"], arc["speed_pct"], 0.0, 0.0
    item_pen_flat, pen_pct = 0.0, 0.0
    dmg_amp, pojun_amp, passive_dr, active_dr, heal_amp = 0.0, 0.0, 0.0, 0.0, 0.0
    nulong_max_hp_ratio, nulong_heal_max_hp, wave_clear_score = 0.0, 0.0, 0.0
    monv_shield, monv_hp_ratio, monv_mdef_to_pdef = 0.0, 0.0, 0.0
    yongye_base, yongye_ratio, xuemo_ratio, on_hit_phys, on_hit_max_hp_ratio = 0.0, 0.0, 0.0, 0.0, 0.0
    on_hit_magic, proc_phys_base, proc_phys_bonus_ad, proc_magic_base, proc_magic_hp_ratio = 0.0, 0.0, 0.0, 0.0, 0.0
    shield_base, shield_hp_ratio = 0.0, 0.0
    has_mingdao, has_bazhe, has_pomo = False, False, False
    best_spellblade = None
    total_price, max_gap = 0, 0
    sb_rank = {"zongshi": 4, "binghen": 3, "fuwen": 2, "wushu": 2, "guanghui": 1}

    for raw_name in item_names:
        prof = get_dynamic_item_profile(raw_name, lv=lv, jg_stacks=jg_stacks)
        total_price += prof["price"]
        max_gap = max(max_gap, prof["max_gap"])
        bonus_atk += prof["atk"]; bonus_hp += prof["hp"]; bonus_pdef += prof["pdef"]; bonus_mdef += prof["mdef"]
        cd_raw += prof["cd"]; speed_pct += prof["speed_pct"]; combat_speed_pct += prof.get("combat_speed_pct", 0.0)
        if prof["speed_flat"] > 0 and speed_flat == 0: speed_flat = prof["speed_flat"]
        item_pen_flat = max(item_pen_flat, prof["pen_flat"]); pen_pct = max(pen_pct, prof["pen_pct"])
        dmg_amp += prof["dmg_amp"]; pojun_amp = max(pojun_amp, prof["pojun_amp"])
        passive_dr = min(0.45, passive_dr + prof["passive_dr"]); active_dr = max(active_dr, prof["active_dr"])
        heal_amp = max(heal_amp, prof["heal_amp"])
        nulong_max_hp_ratio = max(nulong_max_hp_ratio, prof["nulong_max_hp_ratio"])
        nulong_heal_max_hp = max(nulong_heal_max_hp, prof["nulong_heal_max_hp"])
        wave_clear_score += prof["wave_clear_score"]
        monv_shield = max(monv_shield, prof["monv_shield"]); monv_hp_ratio = max(monv_hp_ratio, prof["monv_hp_ratio"])
        monv_mdef_to_pdef = max(monv_mdef_to_pdef, prof["monv_mdef_to_pdef"])
        yongye_base += prof["yongye_heal_base"]; yongye_ratio += prof["yongye_hp_ratio"]
        xuemo_ratio = max(xuemo_ratio, prof["xuemo_hp_ratio"])
        on_hit_phys += prof["on_hit_phys"]; on_hit_max_hp_ratio = max(on_hit_max_hp_ratio, prof["on_hit_max_hp_ratio"])
        on_hit_magic += prof.get("on_hit_magic", 0.0)
        proc_phys_base += prof.get("proc_phys_base", 0.0); proc_phys_bonus_ad += prof.get("proc_phys_bonus_ad", 0.0)
        proc_magic_base += prof.get("proc_magic_base", 0.0); proc_magic_hp_ratio += prof.get("proc_magic_hp_ratio", 0.0)
        shield_base += prof.get("shield_base", 0.0); shield_hp_ratio += prof.get("shield_hp_ratio", 0.0)
        if prof["has_mingdao"]: has_mingdao = True
        if prof["has_bazhe"]: has_bazhe = True
        if prof["has_pomo"]: has_pomo = True
        if prof["spellblade"]:
            if not best_spellblade or sb_rank.get(prof["spellblade"][0], 0) > sb_rank.get(best_spellblade[0], 0):
                best_spellblade = prof["spellblade"]

    if has_bazhe:
        bonus_hp += round(bonus_hp * 0.04)
    model = extract_hero_skill_model(hero_cname)
    total_atk = b_atk + bonus_atk
    total_hp = b_hp + bonus_hp
    combat_max_hp = total_hp + model.get("combat_flat_hp_bonus", 0.0)
    if has_pomo:
        bonus_mdef += min(250.0, round(total_atk * 0.50))
    if monv_mdef_to_pdef > 0:
        bonus_pdef += round(bonus_mdef * monv_mdef_to_pdef)
    total_pdef = b_pdef + bonus_pdef
    total_mdef = b_mdef + bonus_mdef
    pen_flat = arc["pen_flat"] + item_pen_flat
    cd_eff = min(40.0, cd_raw)
    cd_blue = min(40.0, cd_raw + 20.0)
    roam_speed = round((base_speed + speed_flat) * (1.0 + speed_pct / 100.0))
    combat_speed = round((base_speed + speed_flat) * (1.0 + (speed_pct + 0.70 * combat_speed_pct) / 100.0))
    move_speed = roam_speed

    s1_r = min(1.0, max(0.0, (lv - 1) / 8.0))
    s2_r = min(1.0, max(0.0, (lv - 2) / 10.0))
    s3_lv = 3 if lv >= 12 else (2 if lv >= 8 else (1 if lv >= 4 else 0))
    s3_r = (s3_lv - 1) / 2.0 if s3_lv > 0 else 0.0

    on_hit_total = on_hit_phys + combat_max_hp * on_hit_max_hp_ratio
    s1_dmg = (model["s1_base"][0] + (model["s1_base"][1] - model["s1_base"][0]) * s1_r) + model["s1_bonus_ad"] * bonus_atk
    s2_dmg = (model["s2_base"][0] + (model["s2_base"][1] - model["s2_base"][0]) * s2_r) + model["s2_bonus_ad"] * bonus_atk
    s3_dmg = ((model["s3_base"][0] + (model["s3_base"][1] - model["s3_base"][0]) * s3_r) + model["s3_bonus_ad"] * bonus_atk) if s3_lv > 0 else 0.0
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

    def eval_hit_profile(hd: dict, default_sb: tuple, nulong_procs: float):
        sb_p = hd.get("sb_procs", default_sb)
        sb_cnt = sb_p[0] if sb_cd <= 1.5 else sb_p[1]
        tot_aa = hd.get("enh_aa", 0) + hd.get("aa", 0)
        p_raw = (
            hd.get("s1", 0) * s1_dmg
            + hd.get("s2", 0) * s2_dmg
            + hd.get("s3_phys", 0) * s3_dmg
            + hd.get("tianyan", 0) * tianyan_dmg
            + hd.get("enh_aa", 0) * enh_aa_dmg
            + hd.get("aa", 0) * aa_dmg
            + sb_cnt * sb_1hit
            + nulong_procs * (combat_max_hp * nulong_max_hp_ratio)
            + (proc_phys_base + proc_phys_bonus_ad * bonus_atk)
        )
        m_raw = hd.get("s3_mag", 0) * s3_dmg + tot_aa * on_hit_magic + proc_magic_base + combat_max_hp * proc_magic_hp_ratio
        t_raw = hd.get("true_on_hit", 0) * true_1hit
        return p_raw, m_raw, t_raw, hd.get("exec_missing_pct", 0.0)

    def calc_mit(p_raw, m_raw, t_raw, exec_pct, t_pdef, t_mdef, t_hp, amp_scale=0.65):
        eff_p = max(0.0, (t_pdef - pen_flat) * (1.0 - pen_pct / 100.0))
        p_mult = 602.0 / (602.0 + eff_p)
        m_mult = 602.0 / (602.0 + max(0.0, t_mdef))
        amp = (1.0 + dmg_amp * amp_scale) * (1.0 + 0.45 * pojun_amp)
        base_dealt = (p_raw * p_mult + m_raw * m_mult + t_raw) * amp
        if exec_pct > 0:
            missing_hp = min(t_hp, max(0.25 * t_hp, 0.75 * base_dealt))
            base_dealt += (missing_hp * exec_pct) * p_mult * amp
        return round(base_dealt)

    sq_p, sq_m, sq_hp = round(100 + 250 * r), round(60 + 140 * r), round(3200 + 2800 * r)
    br_p, br_m, br_hp = round(180 + 440 * r), round(80 + 220 * r), round(3800 + 4700 * r)
    tk_p, tk_m, tk_hp = round(250 + 850 * r), round(120 + 480 * r), round(4500 + 8500 * r)

    bh, fh = model["burst_hits"], model["full_hits"]
    p2, m2, t2, ex2 = eval_hit_profile(bh, (2.0, 1.0), 1.0)
    pf, mf, tf, exf = eval_hit_profile(fh, (3.0, 2.0), 2.0)

    dmg_2s_sq = calc_mit(p2, m2, t2, ex2, sq_p, sq_m, sq_hp, amp_scale=0.35)
    dmg_2s_br = calc_mit(p2, m2, t2, ex2, br_p, br_m, br_hp, amp_scale=0.35)
    dmg_full_sq = calc_mit(pf, mf, tf, exf, sq_p, sq_m, sq_hp, amp_scale=0.70)
    dmg_full_br = calc_mit(pf, mf, tf, exf, br_p, br_m, br_hp, amp_scale=0.70)
    dmg_full_tk = calc_mit(pf, mf, tf, exf, tk_p, tk_m, tk_hp, amp_scale=0.75)

    kh = model.get("kite_hits", fh)
    mh = model.get("mid_hits", fh)
    mlh = model.get("melee_hits", fh)
    aoeh = model.get("aoe_hits", fh)
    dmg_kite_sq = calc_mit(*eval_hit_profile(kh, (1.2, 1.0), 1.5), sq_p, sq_m, sq_hp)
    dmg_mid_sq = calc_mit(*eval_hit_profile(mh, (1.8, 1.3), 2.0), sq_p, sq_m, sq_hp)
    dmg_melee_sq = calc_mit(*eval_hit_profile(mlh, (2.5, 1.8), 2.0), sq_p, sq_m, sq_hp)
    dmg_aoe_br = calc_mit(*eval_hit_profile(aoeh, (1.6, 1.2), 2.0 * aoeh.get("nulong_mult", 1.0)), br_p, br_m, br_hp)

    s1_cd_base = model["s1_cd"][0] + (model["s1_cd"][1] - model["s1_cd"][0]) * s1_r
    s2_cd_base = model["s2_cd"][0] + (model["s2_cd"][1] - model["s2_cd"][0]) * s2_r
    s3_cd_base = model["s3_cd"][min(2, max(0, s3_lv - 1))] if s3_lv > 0 else model["s3_cd"][0]
    s1_cd = round(s1_cd_base * (1.0 - cd_eff / 100.0), 2)
    s2_cd = round(s2_cd_base * (1.0 - cd_eff / 100.0), 2)
    s3_cd = round(s3_cd_base * (1.0 - cd_eff / 100.0), 2)

    hb0, hb1 = model["passive_heal_base"]
    missing_ten_blocks = (model.get("ult_heal_missing_hp_ratio", 0.50) * 10.0)
    eff_heal_amp = max(heal_amp, missing_ten_blocks * 0.065) if heal_amp > 0 else 0.0
    heal_per_proc = round(((hb0 + (hb1 - hb0) * r) + model["passive_heal_bonus_hp"] * bonus_hp) * (1.0 + eff_heal_amp))
    nulong_heal_total = 2.0 * (combat_max_hp * nulong_heal_max_hp) * (1.0 + eff_heal_amp)
    yongye_heal_total = (yongye_base + combat_max_hp * yongye_ratio) * (1.0 + eff_heal_amp) if (yongye_base > 0 or yongye_ratio > 0) else 0.0
    total_fight_heal = round(model["heal_procs_per_fight"] * heal_per_proc + nulong_heal_total + yongye_heal_total)
    extra_hp = total_fight_heal + model.get("combat_flat_hp_bonus", 0.0)
    extra_hp += total_hp * model.get("extra_shield_hp_ratio", 0.0)
    extra_hp += combat_max_hp * xuemo_ratio
    mag_shield = (monv_shield + bonus_hp * monv_hp_ratio) if monv_shield > 0 else 0.0

    star_tuple = model.get("star_shatter_by_ult", (0.0, 0.0, 0.0, 0.0))
    alpha = star_tuple[s3_lv] if s3_lv < len(star_tuple) else 0.0
    star_mult = 1.0 / (1.0 - 0.65 * alpha) if alpha > 0 else 1.0
    dr_mult = 1.0 / ((1.0 - 0.60 * passive_dr) * (1.0 - 0.65 * active_dr))
    mingdao_mult = 1.18 if has_mingdao else 1.0

    eff_self_pdef = max(0.0, (total_pdef - 240.0 * r) * (1.0 - 0.18 * r))
    eff_self_mdef = max(0.0, (total_mdef - 150.0 * r) * (1.0 - 0.22 * r))
    p_mit_factor = 0.88 * (1.0 + eff_self_pdef / 602.0) + 0.12
    m_mit_factor = 0.88 * (1.0 + eff_self_mdef / 602.0) + 0.12

    item_shield = shield_base + combat_max_hp * shield_hp_ratio
    entry_raw_hp = total_hp + model.get("combat_flat_hp_bonus", 0.0) + combat_max_hp * xuemo_ratio + item_shield + 0.5 * mag_shield
    entry_burst_ehp = round(entry_raw_hp * (0.60 * p_mit_factor + 0.40 * m_mit_factor) * star_mult * dr_mult * mingdao_mult)

    gate = model.get("anti_burst_entry_gate", 18000) * r
    heal_realization = min(1.0, (entry_burst_ehp / max(1.0, gate)) ** 1.2)
    realized_extra_hp = total_fight_heal * heal_realization + model.get("combat_flat_hp_bonus", 0.0) + total_hp * model.get("extra_shield_hp_ratio", 0.0) + combat_max_hp * xuemo_ratio + item_shield

    phys_ehp = round((total_hp + realized_extra_hp) * p_mit_factor * star_mult * dr_mult * mingdao_mult)
    mag_ehp = round((total_hp + realized_extra_hp + mag_shield) * m_mit_factor * star_mult * dr_mult * mingdao_mult)
    mixed_ehp = round(0.60 * phys_ehp + 0.40 * mag_ehp)

    mob_score = model.get("mobility_score", 0.70)
    speed_bonus_weight = (1.0 - mob_score) * 0.14
    eff_speed_for_tempo = 0.65 * roam_speed + 0.35 * combat_speed
    tempo_mult = (1.0 + min(0.10, wave_clear_score)) * (1.0 + speed_bonus_weight * max(0.0, (eff_speed_for_tempo - 470.0) / 100.0))
    if model.get("needs_red_jg_early_tempo") and any(k in item_names for k in ("巡守利斧", "巨人之握")) and not any("黄盾" in k or "怒龙剑盾" in k for k in item_names):
        tempo_mult *= 0.94

    return {
        "items": item_names, "price": total_price, "max_gap": max_gap, "total_atk": round(total_atk),
        "bonus_atk": round(bonus_atk), "total_hp": round(total_hp), "bonus_hp": round(bonus_hp),
        "total_pdef": round(total_pdef), "total_mdef": round(total_mdef), "cd_raw": round(cd_raw, 1),
        "cd_eff": round(cd_eff, 1), "cd_blue": round(cd_blue, 1), "pen_flat": round(pen_flat, 1),
        "pen_pct": round(pen_pct, 1), "move_speed": roam_speed, "combat_speed": combat_speed, "s1_cd": s1_cd, "s2_cd": s2_cd, "s3_cd": s3_cd,
        "heal_per_proc": heal_per_proc, "total_fight_heal": total_fight_heal, "entry_burst_ehp": entry_burst_ehp,
        "wave_clear_mult": round(tempo_mult, 3), "dmg_2s_squishy": dmg_2s_sq, "dmg_2s_bruiser": dmg_2s_br,
        "dmg_kite_squishy": dmg_kite_sq, "dmg_mid_squishy": dmg_mid_sq, "dmg_melee_squishy": dmg_melee_sq,
        "dmg_aoe_bruiser": dmg_aoe_br, "dmg_full_squishy": dmg_full_sq, "dmg_full_bruiser": dmg_full_br,
        "dmg_full_tank": dmg_full_tk, "phys_ehp": phys_ehp, "mag_ehp": mag_ehp, "mixed_ehp": mixed_ehp,
        "dmg_per_1k_gold": round(dmg_2s_sq / max(1.0, total_price / 1000.0)),
    }


def optimize_hero_lifecycle(hero_cname: str, is_jungle: bool = True) -> dict:
    """运行全周期三阶段 (前期过渡 -> 中期第4/5件分水岭 -> 后期六神装全组合帕累托前沿) 自动推演"""
    model = extract_hero_skill_model(hero_cname)
    boots_list = model.get("boots_candidates", ["抵抗之靴"])

    if is_jungle:
        early_paths = [
            ("红刀+抵抗鞋+陨星+铁剑 (高穿过渡)", ["追击刀锋", "抵抗之靴", "陨星", "铁剑"], 6, 8),
            ("红刀+冷静鞋+陨星+铁剑 (速CD过渡)", ["追击刀锋", "冷静之靴", "陨星", "铁剑"], 6, 8),
            ("红刀+影忍足+陨星+铁剑 (抗物过渡)", ["追击刀锋", "影忍之足", "陨星", "铁剑"], 6, 8),
            ("肉刀+抵抗鞋+陨星+铁剑 (肉刀过渡)", ["巡守利斧", "抵抗之靴", "陨星", "铁剑"], 6, 8),
            ("红刀+抵抗鞋+暗影战斧 (首大件成型)", ["追击刀锋", "抵抗之靴", "暗影战斧"], 7, 10),
        ]
        base3 = ["追击刀锋", boots_list[0], "暗影战斧"]
    else:
        early_paths = [
            ("冷静鞋+陨星+荆棘护手 (CD物防对线过渡)", ["冷静之靴", "陨星", "荆棘护手"], 6, 0),
            ("影忍足+陨星+荆棘护手 (高压抗物对线过渡)", ["影忍之足", "陨星", "荆棘护手"], 6, 0),
            ("抵抗鞋+陨星+日冕 (标准黑切组件过渡)", ["抵抗之靴", "陨星", "日冕"], 6, 0),
            ("冷静鞋+暗影战斧+荆棘护手 (边路首大件成型)", ["冷静之靴", "暗影战斧", "荆棘护手"], 7, 0),
            ("抵抗鞋+暗影战斧+荆棘护手 (稳健首大件成型)", ["抵抗之靴", "暗影战斧", "荆棘护手"], 7, 0),
        ]
        base3 = [boots_list[0], "暗影战斧"]

    stage1_early = [{**evaluate_hero_build_at_stage(hero_cname, it, lv=lv, jg_stacks=st), "label": lb} for lb, it, lv, st in early_paths]

    mid_candidates = ["冰痕之握", "暴烈之甲", "纯净苍穹", "宗师之力", "强者破军", "怒龙剑盾", "碎星锤", "不死鸟之眼"]
    stage2_mid4 = [
        {**evaluate_hero_build_at_stage(hero_cname, base3 + [m4], lv=10, jg_stacks=16 if is_jungle else 0), "label": f"核心单品: {m4}"}
        for m4 in mid_candidates
    ]
    mid5_pairs = [
        ("怒龙剑盾", "不死鸟之眼"), ("冰痕之握", "纯净苍穹"), ("暴烈之甲", "纯净苍穹"), ("冰痕之握", "暴烈之甲"),
        ("纯净苍穹", "不死鸟之眼"), ("冰痕之握", "不死鸟之眼"), ("冰痕之握", "强者破军"), ("纯净苍穹", "怒龙剑盾"),
    ]
    stage2_mid5 = [
        {**evaluate_hero_build_at_stage(hero_cname, base3 + [a, b], lv=12, jg_stacks=20 if is_jungle else 0), "label": f"双核组合: {a}+{b}"}
        for a, b in mid5_pairs
    ]

    pool_16 = [
        "暗影战斧", "宗师之力", "冰痕之握", "暴烈之甲", "纯净苍穹",
        "强者破军", "碎星锤", "怒龙剑盾", "血魔之怒", "名刀·司命",
        "魔女斗篷", "永夜守护", "不死鸟之眼", "反伤刺甲", "不祥征兆", "极寒风暴",
    ]
    active_items_set = {"纯净苍穹", "血魔之怒", "不动·天穹", "侵掠·怒魂"}
    all_late = []
    if is_jungle:
        for jg in ["贪婪之噬", "巨人之握"]:
            for boot in boots_list:
                for combo in itertools.combinations(pool_16, 4):
                    if len(SPELLBLADE_ITEMS.intersection(combo)) > 1 or len(active_items_set.intersection(combo)) > 1:
                        continue
                    items = [jg, boot] + list(combo)
                    res = evaluate_hero_build_at_stage(hero_cname, items, lv=15, jg_stacks=25)
                    all_late.append(res)
    else:
        for boot in boots_list:
            for combo in itertools.combinations(pool_16, 5):
                if len(SPELLBLADE_ITEMS.intersection(combo)) > 1 or len(active_items_set.intersection(combo)) > 1:
                    continue
                items = [boot] + list(combo)
                res = evaluate_hero_build_at_stage(hero_cname, items, lv=15, jg_stacks=0)
                all_late.append(res)

    for res in all_late:
        cd_f = 1.0 + 0.008 * res["cd_eff"]
        wc_f = res["wave_clear_mult"]
        kill_gate = 1.0 if res["dmg_kite_squishy"] >= 6200 else (res["dmg_kite_squishy"] / 6200.0) ** 1.8
        res["score_balanced"] = round(((0.30 * res["dmg_2s_squishy"] + 0.30 * res["dmg_full_bruiser"] + 0.25 * res["dmg_aoe_bruiser"] + 0.15 * res["dmg_2s_bruiser"]) ** 0.52) * (res["mixed_ehp"] ** 0.48) * cd_f * wc_f * kill_gate)
        res["score_snowball"] = round((0.50 * res["dmg_2s_squishy"] + 0.30 * res["dmg_kite_squishy"] + 0.20 * res["dmg_aoe_bruiser"]) * cd_f * (min(res["mixed_ehp"], 32000) / 26000.0) ** 0.35)
        res["score_behind"] = round((res["mixed_ehp"] ** 0.60) * ((0.5 * res["dmg_full_bruiser"] + 0.5 * res["dmg_aoe_bruiser"]) ** 0.40) * cd_f * wc_f * kill_gate)
        res["score_antitank"] = round(((0.50 * res["dmg_full_tank"] + 0.50 * res["dmg_full_bruiser"]) ** 0.60) * (res["mixed_ehp"] ** 0.40) * cd_f)

    official_audit = []
    lane_key = "打野" if is_jungle else "对抗"
    for b in OFFICIAL_BUILDS_DB.get(hero_cname, {}).get("lanes", {}).get(lane_key, []):
        ev = evaluate_hero_build_at_stage(hero_cname, b.get("items", []), lv=15, jg_stacks=25 if is_jungle else 0)
        ev["label"] = f"官方-{b.get('title', '')}"
        official_audit.append(ev)
    for v_label, v_items in model.get("viral_builds_jg" if is_jungle else "viral_builds_lane", []):
        ev = evaluate_hero_build_at_stage(hero_cname, v_items, lv=15, jg_stacks=25 if is_jungle else 0)
        ev["label"] = v_label
        official_audit.append(ev)

    return {
        "hero": hero_cname, "lane": lane_key, "total_combinations_searched": len(all_late),
        "stage1_early": stage1_early,
        "stage2_mid4": sorted(stage2_mid4, key=lambda x: x["dmg_2s_squishy"] * (x["mixed_ehp"] ** 0.45) * (1 + 0.008 * x["cd_eff"]), reverse=True),
        "stage2_mid5": sorted(stage2_mid5, key=lambda x: x["dmg_full_bruiser"] * (x["mixed_ehp"] ** 0.45) * (1 + 0.008 * x["cd_eff"]), reverse=True),
        "pareto_balanced": sorted(all_late, key=lambda x: x["score_balanced"], reverse=True)[:5],
        "pareto_snowball": sorted(all_late, key=lambda x: x["score_snowball"], reverse=True)[:5],
        "pareto_behind": sorted(all_late, key=lambda x: x["score_behind"], reverse=True)[:5],
        "pareto_antitank": sorted(all_late, key=lambda x: x["score_antitank"], reverse=True)[:5],
        "official_audit": official_audit,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="王者荣耀全周期客观出装推演引擎")
    parser.add_argument("--hero", type=str, default="曜", help="英雄名称，如：曜、杨戬、赵云")
    parser.add_argument("--lane", type=str, default="打野", choices=["打野", "对抗"], help="分路：打野 或 对抗")
    args = parser.parse_args()
    report = optimize_hero_lifecycle(args.hero, is_jungle=(args.lane == "打野"))
    print(f"=== [{args.hero}·{args.lane}] 全周期出装推演完成 (穷举 {report['total_combinations_searched']} 种六神装组合) ===")
    for tag, key in [("均势全能最优", "pareto_balanced"), ("顺风切C最优", "pareto_snowball"), ("逆风容错最优", "pareto_behind"), ("破甲攻坚最优", "pareto_antitank")]:
        top = report[key][0]
        print(f"[{tag}] {' + '.join(top['items'])} | 造价:{top['price']}G | 无蓝CD:{top['cd_eff']}% | 2s爆发:{top['dmg_2s_squishy']} | 完整连招:{top['dmg_full_squishy']}(打肉:{top['dmg_full_tank']}) | 综合EHP:{top['mixed_ehp']}")
    for oa in report["official_audit"]:
        print(f"[{oa['label']}] {' + '.join(oa['items'])} | 造价:{oa['price']}G | 无蓝CD:{oa['cd_eff']}% | 2s爆发:{oa['dmg_2s_squishy']} | 完整连招:{oa['dmg_full_squishy']}(打肉:{oa['dmg_full_tank']}) | 综合EHP:{oa['mixed_ehp']}")
