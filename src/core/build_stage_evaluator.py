"""单阶段出装评估：指定英雄在任意等级/分路/装备组合下的三态指标与动态加权评分 (build_stage_evaluator.py)"""

from config.hero_base_stats import get_hero_base_stats
from config.hero_arcana_data import HERO_RECOMMENDED_ARCANA
from src.core.build_item_aggregator import ITEM_AGG_KEYS, parse_arcana_totals, aggregate_item_stats
from src.core.hero_combo_profiles import extract_hero_skill_model
from src.core.build_scoring_engine import evaluate_three_combat_states
from src.core.mechanic_taxonomy import C3_STAGE_RAMP_FACTORS, C5_ACTIVE_WINDOW_WEIGHTS, BLUE_BUFF_CYCLE_MODEL, get_hero_c5_coupling


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
        arcana_list = [[9, "异变"], [1, "红月"], [10, "鹰眼"], [10, "狩猎"]] if hero_cname == "杨戬" else ([[10, HERO_RECOMMENDED_ARCANA[hero_cname]["red"]], [10, HERO_RECOMMENDED_ARCANA[hero_cname]["green"]], [10, HERO_RECOMMENDED_ARCANA[hero_cname]["blue"]]] if hero_cname in HERO_RECOMMENDED_ARCANA else [[10, "异变"], [10, "鹰眼"], [10, "隐匿"]])
    if lane is None:
        lane = "打野" if any(k in item_names for k in ("追击刀锋", "贪婪之噬", "巡守利斧", "巨人之握")) else "对抗"

    arc = parse_arcana_totals(arcana_list)
    base_cfg = get_hero_base_stats(0, hero_cname) or {}
    r = max(0.0, min(1.0, (lv - 1) / 14.0))

    hp0, hp15 = base_cfg.get("hp", (3400, 7300)); atk0, atk15 = base_cfg.get("atk", (175, 350))
    pdef0, pdef15 = base_cfg.get("pdef", (150, 402)); mdef0, mdef15 = base_cfg.get("mdef", (75, 173))
    base_speed = base_cfg.get("speed", 380)
    aspeed_str = str(base_cfg.get("aspeed", "")).replace("+", "").replace("%", "").strip()
    aspeed_growth = float(aspeed_str) if aspeed_str else base_cfg.get("aspeed_growth", 1.0)
    base_aspeed = round(float(base_cfg.get("aspeed_base", 0.0)) + aspeed_growth * (lv - 1), 1)
    b_hp, b_atk = round(hp0 + (hp15 - hp0) * r), round(atk0 + (atk15 - atk0) * r)
    b_pdef, b_mdef = round(pdef0 + (pdef15 - pdef0) * r), round(mdef0 + (mdef15 - mdef0) * r)

    _agg = aggregate_item_stats(item_names, lv, jg_stacks, arc, base_aspeed)
    bonus_atk, bonus_hp, bonus_pdef, bonus_mdef, bonus_ap, cd_raw, speed_pct, combat_speed_pct, speed_flat, ooc_speed_flat, aspeed_pct, combat_aspeed_pct, crit_rate, crit_eff, p_vamp_pct, item_pen_flat, pen_pct, item_m_pen_flat, m_pen_pct, raw_eq_ten, slow_resist, on_hit_heal, dmg_amp, pojun_amp, passive_dr, active_dr, heal_amp, jg_burn_target_hp_ratio, nulong_max_hp_ratio, nulong_heal_max_hp, wave_clear_score, monv_shield, monv_hp_ratio, monv_mdef_to_pdef, yongye_base, yongye_ratio, xuemo_ratio, on_hit_phys, on_hit_max_hp_ratio, on_hit_magic, proc_phys_base, proc_phys_bonus_ad, proc_magic_base, proc_magic_hp_ratio, shield_base, shield_hp_ratio, has_mingdao, has_bazhe, has_pomo, has_ice, has_frost_shock, has_hat, has_prophecy, has_cocoon, has_sage_book, has_infinity, has_frostbite, best_spellblade, total_price, max_gap = (_agg[k] for k in ITEM_AGG_KEYS)

    if has_infinity:
        crit_eff += min(50.0, 20.0 + 0.50 * crit_rate)
    crit_conf = 0.30 if crit_rate < 20.0 else (0.65 if crit_rate < 38.0 else 1.0)
    crit_mult = 1.0 + (min(100.0, crit_rate) / 100.0) * crit_conf * ((crit_eff - 100.0) / 100.0)
    eff_combat_aspeed = min(200.0, max(0.0, aspeed_pct + combat_aspeed_pct))
    aspeed_linear_mult = 1.0 + eff_combat_aspeed * 0.0030

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

    orb_mult = model.get("orb_proc_mult", 1.0)
    can_crit_enh = model.get("can_crit_enh_aa", False)
    s1_is_magic = model.get("s1_is_magic", False)
    aspeed_drives_heal = model.get("aspeed_drives_heal_ticks", False)
    chain_tick_mult = (1.0 + eff_combat_aspeed * 0.0040) if aspeed_drives_heal else aspeed_linear_mult

    # 物理与法术法球统一吃英雄法球倍率与攻速频率（末世/血魔狂怒 + 闪电匕首电弧）
    on_hit_phys_total = (on_hit_phys + combat_max_hp * on_hit_max_hp_ratio) * orb_mult * chain_tick_mult
    on_hit_mag_total = on_hit_magic * orb_mult * chain_tick_mult
    on_hit_orb_power = on_hit_phys_total + on_hit_mag_total + combat_max_hp * nulong_max_hp_ratio * 1.4

    s1_dmg = (model["s1_base"][0] + (model["s1_base"][1] - model["s1_base"][0]) * s1_r) + model["s1_bonus_ad"] * bonus_atk
    s2_dmg = (model["s2_base"][0] + (model["s2_base"][1] - model["s2_base"][0]) * s2_r) + model["s2_bonus_ad"] * bonus_atk
    s2m0, s2m1 = model.get("s2_mag_base", (0.0, 0.0))
    s2_mag_dmg = (s2m0 + (s2m1 - s2m0) * s2_r) + model.get("s2_mag_bonus_ad", 0.0) * bonus_atk
    s3_dmg = ((model["s3_base"][0] + (model["s3_base"][1] - model["s3_base"][0]) * s3_r) + model["s3_bonus_ad"] * bonus_atk) if s3_lv > 0 else 0.0
    s3_spirit_dmg = (model.get("s3_spirit_total_ad", 0.0) * total_atk * crit_mult * aspeed_linear_mult) if s3_lv > 0 else 0.0
    cm0, cm1 = model.get("chain_end_mag_base", (0.0, 0.0))
    chain_end_mag_dmg = (cm0 + (cm1 - cm0) * r) + model.get("chain_end_mag_total_ad", 0.0) * total_atk
    el0, el1 = model.get("electro_base", (0.0, 0.0))
    electro_dmg = ((el0 + (el1 - el0) * s3_r) + model.get("electro_bonus_ap", 0.0) * bonus_ap) if s3_lv > 0 else 0.0
    ty0, ty1 = model.get("tianyan_base", (0.0, 0.0))
    tianyan_dmg = (ty0 + (ty1 - ty0) * r) + model.get("tianyan_bonus_ad", 0.0) * bonus_atk
    enh_phys_part = (model.get("enh_aa_total_ad", 0.0) * total_atk + model.get("enh_aa_bonus_ad", 0.0) * bonus_atk) * (crit_mult * chain_tick_mult if can_crit_enh else chain_tick_mult)
    enh_aa_dmg = (model["enh_aa_base"][0] + (model["enh_aa_base"][1] - model["enh_aa_base"][0]) * r) + enh_phys_part + (on_hit_phys_total if model.get("enh_aa_total_ad", 0.0) > 0 else 0.0)
    aa_dmg = 1.0 * total_atk * crit_mult * aspeed_linear_mult + on_hit_phys_total
    tb0, tb1 = model.get("true_hit_base", (0.0, 0.0))
    true_1hit = ((tb0 + (tb1 - tb0) * s2_r) + model.get("true_hit_bonus_ad", 0.0) * bonus_atk) * aspeed_linear_mult

    sb_1hit, sb_cd = 0.0, 3.0
    if best_spellblade:
        _, sb_cd, sb_base, sb_tot_ad, sb_bon_ad, _ = best_spellblade
        sb_1hit = sb_base + sb_tot_ad * total_atk + sb_bon_ad * bonus_atk

    # 3秒魂链粘人完成度 (tether_completion)：无硬控魂链英雄极度依赖移速与减速防止目标挣脱魂链
    tether_rel = model.get("tether_reliance", 0.0)
    item_slow_bonus = 0.06 if has_frostbite else (0.04 if (has_ice or has_frost_shock) else 0.0)
    if tether_rel > 0:
        tether_completion = min(1.08, max(0.82, 0.85 + max(0.0, (combat_speed - 455.0) / 380.0) + item_slow_bonus))
        stickiness = tether_completion
    else:
        tether_completion = 1.0
        stickiness = 1.0 + (0.030 if has_ice else (0.025 if (has_frost_shock or has_frostbite) else 0.0))
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
        enh_cnt = (hd.get("enh_aa", 0) + zy_br_bonus) * st_m
        aa_cnt = hd.get("aa", 0) * st_m
        s1_phys_cnt = 0.0 if s1_is_magic else (hd.get("s1", 0) + zy_br_bonus)
        s1_mag_cnt = (hd.get("s1", 0) + zy_br_bonus) if s1_is_magic else 0.0
        p_raw = (s1_phys_cnt * s1_dmg + (hd.get("s2", 0) * st_m) * s2_dmg + (hd.get("s3_phys", 0) + yj_s3_bonus) * (s3_dmg + s3_spirit_dmg)
                 + hd.get("tianyan", 0) * tianyan_dmg + enh_cnt * enh_aa_dmg + aa_cnt * aa_dmg
                 + (sb_cnt + extra_sb) * sb_1hit + nulong_procs * (combat_max_hp * nulong_max_hp_ratio)
                 + ((proc_phys_base + proc_phys_bonus_ad * bonus_atk) if active_ready else 0.0))
        m_raw = (s1_mag_cnt * s1_dmg + (hd.get("s2_mag", 0) * st_m) * s2_mag_dmg + enh_cnt * chain_end_mag_dmg
                 + hd.get("s3_mag", 0) * s3_dmg + hd.get("electro_mag", 0) * electro_dmg
                 + (enh_cnt + aa_cnt * 0.35) * on_hit_mag_total + proc_magic_base + combat_max_hp * proc_magic_hp_ratio)
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
            # 大司命神巫斩杀(10%无视护盾直接斩杀) vs 杨戬1技能二段(15%已损生命物伤)
            if s1_is_magic and exec_pct <= 0.12:
                base_dealt += (0.10 * t_hp) * amp
            else:
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
    eff_heal_procs = model["heal_procs_per_fight"] * (chain_tick_mult * tether_completion if aspeed_drives_heal else 1.0)
    # 残血大招瞬发回复（如大司命 3技能 750~1500 + 12%额外生命，按开大前防秒可靠度 ult_cast_reliability 折算）
    uh0, uh1 = model.get("ult_heal_base", (0.0, 0.0))
    pre_ult_burst_shield = total_hp * (1.0 + xuemo_ratio * 0.55) / max(0.35, 1.0 - passive_dr - 0.55 * active_dr)
    ult_cast_reliability = min(1.0, max(0.55, pre_ult_burst_shield / (5200.0 + 5400.0 * r))) if uh1 > 0 else 1.0
    ult_heal_total = (((uh0 + (uh1 - uh0) * s3_r) + model.get("ult_heal_bonus_hp", 0.0) * bonus_hp) * model.get("ult_heal_aoe_mult", 1.0) * anti_heal_mult * ult_cast_reliability) if (uh1 > 0 and s3_lv > 0) else 0.0
    nulong_heal_total = 0.25 * (combat_max_hp * nulong_heal_max_hp) * (1.0 + eff_heal_amp)
    yongye_heal_total = (yongye_base + combat_max_hp * yongye_ratio) * anti_heal_mult if (yongye_base > 0 or yongye_ratio > 0) else 0.0
    vamp_heal_total = (0.45 * dmg_full_br * (p_vamp_pct / 100.0)) * anti_heal_mult
    total_fight_heal = round(eff_heal_procs * heal_per_proc + ult_heal_total + nulong_heal_total + yongye_heal_total + vamp_heal_total + 4.0 * on_hit_heal * (1.0 + eff_heal_amp))

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

    req_exp_sec = model.get("required_exposure_sec", model.get("full_window_sec", 3.2))
    exposure_completion = min(1.06, max(0.72, (entry_burst_ehp / (7000.0 * req_exp_sec))))

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
        "active_dr": active_dr, "xuemo_ratio": xuemo_ratio, "heal_amp": heal_amp, "nulong_max_hp_ratio": nulong_max_hp_ratio,
        "dmg_amp": dmg_amp, "on_hit_orb_power": on_hit_orb_power, "eff_combat_aspeed": eff_combat_aspeed,
        "tether_completion": tether_completion, "exposure_completion": exposure_completion, "ult_cast_reliability": ult_cast_reliability,
        "has_mingdao": has_mingdao, "has_frost_shock": has_frost_shock, "has_spellblade": bool(best_spellblade), "pen_flat": pen_flat,
    }
    state_eval = evaluate_three_combat_states(hero_cname, item_names, raw_state_metrics, model, lane)
    rw = state_eval["role_weights"]

    is_frontline_aoe_warrior = (model.get("passive_heal_base", (0.0, 0.0))[1] >= 400) or (model.get("ult_heal_base", (0.0, 0.0))[1] >= 1000)
    has_heiqie = "暗影战斧" in item_names
    is_tank_jg = "巨人之握" in item_names
    # 前中期刷野与Gank过渡平滑度：肉刀(0物攻)若不配怒龙剑盾或电刀而直接裸末世(野怪无额外生命加成)，4~9分钟刷野与抓人伤害存在明显断档
    if is_tank_jg and nulong_max_hp_ratio == 0 and on_hit_magic == 0 and bonus_atk < 160:
        early_mid_tempo_bonus = -3.5
    elif has_heiqie or nulong_max_hp_ratio > 0 or (bonus_atk >= 220 and eff_combat_aspeed >= 65.0) or (is_tank_jg and (nulong_max_hp_ratio > 0 or on_hit_magic > 0)):
        early_mid_tempo_bonus = 5.5
    else:
        early_mid_tempo_bonus = 1.0

    eff_full_sq = (0.52 * dmg_full_sq + 0.48 * dmg_normal_downtime) * (tether_completion if tether_rel > 0 else 1.0)
    heiqie_burst_bonus = 2.5 if (has_heiqie and not s1_is_magic) else 0.0
    if is_frontline_aoe_warrior and not s1_is_magic:
        burst_kill_score = min(100.0, (0.30 * dmg_2s_sq + 0.35 * eff_full_sq + 0.18 * dmg_full_br + 0.17 * dmg_aoe_br) / 96.0 + heiqie_burst_bonus)
    else:
        burst_kill_score = min(100.0, (0.35 * dmg_2s_sq + 0.43 * eff_full_sq + 0.22 * dmg_full_br) / 96.0 + heiqie_burst_bonus)

    surv_3state_score = state_eval["composite_3state_score"]
    # 野怪无“额外最大生命”，末世【破败】对野怪仅生效基础值，刷野速率由总物攻、攻速、怒龙重创与电刀电弧决定
    nulong_pve_dps = (combat_max_hp * nulong_max_hp_ratio * 2.0) / 45.0
    monster_dps_proxy = (total_atk * (1.0 + eff_combat_aspeed / 100.0) * 8.5 + on_hit_mag_total * 2.2) / 620.0
    pve_clear_sub = min(100.0, 36.0 + wave_clear_score * 130.0 + nulong_pve_dps + monster_dps_proxy)
    roam_mob_sub = min(100.0, 42.0 + max(0.0, (0.65 * roam_speed + 0.35 * combat_speed) - 440.0) * 0.65)
    pve_roam_score = round(0.65 * pve_clear_sub + 0.35 * roam_mob_sub, 1)

    u_blue, g_blue = BLUE_BUFF_CYCLE_MODEL["uptime_ratio"], BLUE_BUFF_CYCLE_MODEL["renewal_gap_ratio"]
    gap_cliff_pen = max(0.0, BLUE_BUFF_CYCLE_MODEL["safe_base_cdr_threshold"] - cd_eff) * 0.85 * g_blue
    cd_score_no_blue = min(100.0, 45.0 + (cd_eff / 40.0) * 55.0)
    cd_score_with_blue = max(40.0, min(100.0, 45.0 + (u_blue * (cd_blue / 40.0) + g_blue * (cd_eff / 40.0)) * 55.0 - gap_cliff_pen))
    cc_bonus = (9.5 if (combat_speed >= 490 and has_frostbite) else (8.5 if (combat_speed >= 490 or has_frostbite or has_frost_shock) else (5.0 if has_ice else 0.0))) if orb_mult > 1.2 else (10.0 if has_ice else (8.5 if (has_frost_shock or has_frostbite) else 0.0))
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
        "total_pdef": round(total_pdef), "total_mdef": round(total_mdef), "aspeed_pct": round(aspeed_pct, 1), "eff_combat_aspeed": round(eff_combat_aspeed, 1),
        "crit_rate": round(crit_rate, 1), "p_vamp_pct": round(p_vamp_pct, 1), "cd_raw": round(cd_raw, 1), "cd_eff": round(cd_eff, 1),
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
