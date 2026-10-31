# -*- coding: utf-8 -*-
"""王者荣耀英雄定位、技能倍率拓扑与全期强势期曲线算法引擎 (hero_power_curve.py)"""

import re
from config.hero_base_stats import get_hero_base_stats
from src.core.hero_combo_profiles import HERO_SKILLS_DB, extract_hero_skill_model


def analyze_hero_positioning_and_power_curve(hero_cname: str) -> dict:
    """基于本地权威技能库(hero_skills_data.json)与连招模型，算法化推演英雄定位、前中后期强势曲线与隐藏实战机制"""
    skills = HERO_SKILLS_DB.get(hero_cname, [])
    model = extract_hero_skill_model(hero_cname)
    base_cfg = get_hero_base_stats(0, hero_cname) or {}

    all_desc = "\n".join(f"【{s.get('name', '')}】{s.get('desc', '')}" for s in skills)
    bonus_ad_ratios = [float(x) / 100.0 for x in re.findall(r"\(\+(\d+)%额外物理攻击\)", all_desc)]
    total_ad_ratios = [float(x) / 100.0 for x in re.findall(r"\(\+(\d+)%物理攻击\)", all_desc)]
    extra_hp_ratios = [float(x) / 100.0 for x in re.findall(r"\(\+(\d+(?:\.\d+)?)%额外生命\)", all_desc)]
    has_true_dmg = "真实伤害" in all_desc
    has_missing_hp_dmg = ("已损生命" in all_desc) or (model.get("full_hits", {}).get("exec_missing_pct", 0.0) > 0)
    has_pct_dr = bool(re.search(r"获得\d+%免伤|减少\d+%所受伤害|免伤", all_desc))
    has_tenacity = "韧性" in all_desc
    has_overflow_shield = ("转化为永久护盾" in all_desc) or ("护盾" in all_desc)
    has_cd_refund = ("返还" in all_desc and "冷却" in all_desc) or ("刷新" in all_desc)
    has_tier_extra_skill = "获得一次额外" in all_desc

    fh = model.get("full_hits", {})
    combo_bonus_ad_total = round(
        fh.get("s1", 0) * model.get("s1_bonus_ad", 0.0)
        + fh.get("s2", 0) * model.get("s2_bonus_ad", 0.0)
        + (fh.get("s3_phys", 0) + fh.get("s3_mag", 0)) * model.get("s3_bonus_ad", 0.0)
        + fh.get("enh_aa", 0) * model.get("enh_aa_bonus_ad", 0.0)
        + fh.get("true_on_hit", 0) * model.get("true_hit_bonus_ad", 0.0),
        2,
    )
    combo_base_lv1 = round(
        fh.get("s1", 0) * model.get("s1_base", (0, 0))[0]
        + fh.get("s2", 0) * model.get("s2_base", (0, 0))[0]
        + (fh.get("s3_phys", 0) + fh.get("s3_mag", 0)) * model.get("s3_base", (0, 0))[0]
    )

    mob_score = model.get("mobility_score", 0.65)
    if mob_score <= 0.45:
        mobility_type = "目标锁定型单段突进（需先命中目标才可位移，缺乏无条件空放穿墙/撤退手段）"
    elif has_tier_extra_skill or has_cd_refund:
        mobility_type = "多段自由位移+机制刷新/返还CD（可无条件空放穿墙、跨档位存位移或空大返还50%冷却）"
    else:
        mobility_type = "多段自由机动突进（可自主选择进场与撤退角度）"

    if has_pct_dr and has_overflow_shield:
        surv_type = "百分比免伤+溢出回血转永久护盾（免伤无视敌方破晓/虚无法杖穿透，护盾不受35%重伤直接扣减）"
    elif has_tenacity and not has_pct_dr:
        surv_type = "高额韧性免控+固定生命/大招直接回血（中前期不怕控制链，但大后期纯双抗与纯回血易受百分比穿透+35%重伤双克制）"
    else:
        surv_type = "常规双抗与技能回复结合"

    if has_true_dmg and has_missing_hp_dmg and mob_score <= 0.45:
        curve_type = "前中期强势、大后期偏吃力型（2级~12分钟黄金期，14分钟+团战容错下降）"
        early_eval = "强势（2~4级）：自带高基础真实伤害与已损生命斩杀，无需大件即可在野区与小规模团战打出压制力。"
        mid_eval = "黄金强势期（4~12分钟）：暗影战斧+核心防装成型，敌方C位尚未补齐破晓/虚无法杖，高韧性+大招回血可正面统治双龙团。"
        late_eval = "相对吃力（14~15分钟+）：仅靠1技能命中才可突进、缺乏无条件撤退位移；真伤额外AD加成低(0.36)，被动仅加600固定血量无百分比免伤，面对神装射手破晓+制裁/梦魇时正面进场易被集火。"
    elif combo_bonus_ad_total >= 4.5 and has_pct_dr:
        curve_type = "1~3级偏弱、4级发力、中后期至六神装全程强势型（装备驱动多轮拉扯战刺）"
        early_eval = "偏弱需稳刷（1~3级）：1/2/3技能全部依赖【额外物理攻击】与【额外生命】加成，1级1技能冷却8秒且位移短，无装备与大招前野区对拼弱于前期真伤英雄，需稳刷到4级做出陨星。"
        mid_eval = "发力黄金期（4~12分钟）：做出暗影战斧+冰痕之握+贪婪之噬后，全套超530%额外物攻加成与冰痕1.25秒双强击成型，32.5%冷却抓边与控龙效率极高。"
        late_eval = "持续强势不疲软（12~15分钟+六神装）：被动最高20%免伤无视穿透，2技能溢出回血转永久护盾，跨档位刷新额外1技能且空大返还50%冷却（满CD仅4.4秒），六神装兼具秒C爆发与七进七出拉扯容错；仅需注意补法防与打肉换碎星锤。"
    else:
        curve_type = "全期均衡成长型战刺"
        early_eval = "均衡过渡（1~4级）：依托基础技能机制平稳刷野发育。"
        mid_eval = "核心发力期（5~12分钟）：双核装备成型后具备高机动切C能力。"
        late_eval = "后期团战期（12分钟+）：依托冷却与免伤机制拉扯切入后排。"

    hidden_mechanics = []
    for sk in skills:
        nm, desc = sk.get("name", ""), sk.get("desc", "")
        if "存储一次额外" in desc or "获得一次额外" in desc:
            hidden_mechanics.append(f"【{nm}·跨档位存额外1技能】血量跨越70%/40%分界线（掉血或回血升档均触发）时额外存储1次1技能，团战掉血+回血可连打多发1A强普与50%减速。")
        if "转化为永久护盾" in desc:
            hidden_mechanics.append(f"【{nm}·跨档位溢出回血转永久白盾 & 填满升档转真血】仅在二档(40%~70%)或三档(≤40%)回血触及并跨过70%/40%档位刻度线时，绿血锁在档位线且溢出回血转化为永久白盾（满血一档或档位内未跨线回血不产盾）；当『当前绿血+白盾（血盾总量）』填满下一档位上限时，档位线以下的白盾瞬间消失并1:1转化为永久真实绿血，同时升档并刷新额外1技能。")
        if "返还50%冷却" in desc:
            hidden_mechanics.append(f"【{nm}·空大返还50%冷却】大招未命中敌方英雄直接返还50%冷却（满CD下仅4.8秒），逆风带线撤退、穿厚墙逃生或远距离赶路时可果断空放当位移用。")
        if "位移距离随技能等级增加" in desc:
            hidden_mechanics.append(f"【{nm}·位移随等级变远】1技能位移距离随技能等级提升明显加长，满级穿厚墙与追击手感远优于1级。")
        if "后续每枪效果降低8%" in desc:
            hidden_mechanics.append(f"【{nm}·5枪衰减系数与冰痕双强击】2技能连刺5枪（后续每枪效果降低8%，合计为首枪4.2倍伤害与4.2倍回血），耗时约1.3秒，在13A2A连招中首尾两发平A刚好卡过冰痕之握1.25秒冷却打出2次强击。")
        if "韧性" in desc and ("法天象地" in nm or "法天象地" in desc):
            hidden_mechanics.append(f"【{nm}·满韧性槽变身法天象地】普攻与技能造成伤害积攒60%~90%韧性（达到60%全局韧性上限，且其他途径至多获得25%韧性），满槽进入临界霸体并与英雄战斗变身法天象地（+600生命），鞋位可灵活选择影忍之足或冷静之靴。")
        if "生命值比例高于" in desc or "0.5/1秒" in desc:
            hidden_mechanics.append(f"【{nm}·血量百分比判定1秒眩晕】基础造成0.5秒晕眩，当目标生命值比例高于或等于杨戬时晕眩延长至1秒；残血或开血魔之怒（扣30%当前血且白盾不计入生命百分比）可稳定打出1秒硬控。")
        if "刷新冷却" in desc or "冷却时间全部刷新" in desc or "刷新【逆转乾坤】" in desc:
            hidden_mechanics.append(f"【{nm}·标记击杀刷新与回收哮天犬减CD】目标在被标记期间死亡直接100%刷新1技能冷却；未命中时哮天犬停留在终点，杨戬靠近回收可减少当前25%~50%冷却时间。")
        if "远离杨戬时" in desc or "天眼发射激光" in desc:
            hidden_mechanics.append(f"【{nm}·目标远离触发天眼激光】技能命中攒1~3层天眼能量，当目标远离杨戬时天眼发射激光造成物伤并回血，克制敌方位移逃生与风筝拉扯。")

    return {
        "hero": hero_cname,
        "base_stats_lv1_15": base_cfg,
        "combo_bonus_ad_total_ratio": combo_bonus_ad_total,
        "combo_base_dmg_lv1": combo_base_lv1,
        "bonus_ad_skill_ratios": bonus_ad_ratios,
        "total_ad_skill_ratios": total_ad_ratios,
        "extra_hp_skill_ratios": extra_hp_ratios,
        "mobility_score": mob_score,
        "mobility_type": mobility_type,
        "survivability_type": surv_type,
        "power_curve_type": curve_type,
        "power_curve_stages": {
            "early_1_3": early_eval,
            "mid_4_12": mid_eval,
            "late_12_plus": late_eval,
        },
        "hidden_mechanics": hidden_mechanics,
    }
