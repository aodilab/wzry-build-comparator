# -*- coding: utf-8 -*-
"""
王者荣耀出装多维数据分析引擎
专为分路 PDF 构建器计算 15 级神装满配下的真实物理数据与打靶净伤害
"""

import math
import re
from config.hero_base_stats import get_hero_base_stats
from config.hero_arcana_data import ARCANA_LEVEL_5_DICT

BOOTS_MAP = {
    "神速之靴": 30, "影忍之足": 60, "抵抗之靴": 60,
    "冷静之靴": 60, "秘法之靴": 60, "急速战靴": 60, "疾步之靴": 60
}

# 基础装备属性词缀提取字典
ITEM_STATS_CACHE = {
    "暗影战斧": {"atk": 85, "cdr": 15, "hp": 500, "p_pierce_flat": 170},
    "无尽战刃": {"atk": 110, "crit": 20, "crit_eff": 20},
    "宗师之力": {"atk": 80, "crit": 20, "hp": 500, "mp": 400, "has_master": True},
    "破晓": {"atk": 50, "aspeed": 35, "crit": 10, "p_pierce_pct": 40},
    "碎星锤": {"atk": 80, "cdr": 10, "p_pierce_pct": 40},
    "泣血之刃": {"atk": 100, "hp": 500, "p_lifesteal": 25},
    "末世": {"atk": 60, "aspeed": 30, "p_lifesteal": 10, "has_moshi": True},
    "影刃": {"atk": 0, "aspeed": 35, "crit": 25, "pct_speed": 5},
    "逐风": {"atk": 65, "aspeed": 25, "crit": 15},
    "闪电匕首": {"aspeed": 35, "pct_speed": 8},
    "暴烈之甲": {"atk": 30, "pdef": 220, "hp": 900, "pct_speed": 5},
    "不祥征兆": {"pdef": 270, "hp": 1200},
    "霸者重装": {"hp": 2000, "pdef": 100, "mdef": 50},
    "红莲斗篷": {"pdef": 240, "hp": 1000},
    "魔女斗篷": {"mdef": 300, "hp": 1000},
    "永夜守护": {"mdef": 360, "hp": 1000},
    "不死鸟之眼": {"mdef": 240, "hp": 1200},
    "极寒风暴": {"pdef": 360, "cdr": 20, "mp": 500},
    "反伤刺甲": {"atk": 30, "pdef": 360},
    "冰痕之握": {"atk": 40, "pdef": 240, "hp": 500, "cdr": 10, "mp": 500, "has_ice": True},
    "纯净苍穹": {"atk": 100, "cdr": 10, "hp": 500},
    "名刀·司命": {"atk": 50, "cdr": 5},
    "贤者的庇护": {"pdef": 140, "mdef": 140},
    "回响之杖": {"ap": 240, "pct_speed": 7},
    "博学者之怒": {"ap": 240, "has_hat": True},
    "虚无法杖": {"ap": 240, "hp": 500, "m_pierce_pct": 45},
    "日暮之流": {"ap": 200, "cdr": 10, "hp": 300, "m_pierce_flat": 240},
    "痛苦面具": {"ap": 120, "cdr": 5, "hp": 800},
    "噬神之书": {"ap": 180, "cdr": 10, "hp": 1000, "m_lifesteal": 25},
    "时之预言": {"ap": 140, "mp": 500, "hp": 800, "has_prophecy": True},
    "凝冰之息": {"ap": 160, "cdr": 5, "hp": 600},
    "贤者之书": {"ap": 400, "cdr": 10},
    "破茧之衣": {"ap": 160, "hp": 1000, "m_pierce_flat": 150},
    "金色圣剑": {"ap": 140, "aspeed": 20, "pct_speed": 5},
    "贪婪之噬": {"atk": 90, "cdr": 8, "pct_speed": 8, "knife_type": "红刀·贪婪之噬"},
    "巨人之握": {"hp": 1200, "pdef": 120, "mdef": 60, "pct_speed": 6, "knife_type": "肉刀·巨人之握"},
    "符文大剑": {"ap": 180, "cdr": 7, "pct_speed": 7, "knife_type": "蓝刀·符文大剑"},
    "极影·救赎": {"hp": 1200, "pct_speed": 8, "cdr": 10, "support_active": "救赎 (为周围友军提供高额护盾)", "support_aura": "极影 (提升友军攻速/冷缩/双抗)"},
    "近卫·救赎": {"hp": 1200, "pct_speed": 8, "pdef": 120, "mdef": 60, "support_active": "救赎 (为周围友军提供高额护盾)", "support_aura": "近卫 (提升友军高额双抗)"},
    "极影·奔狼": {"hp": 1200, "pct_speed": 8, "cdr": 10, "support_active": "奔狼 (全队瞬间极限提速冲锋)", "support_aura": "极影 (提升友军攻速/冷缩/双抗)"},
    "近卫·形昭": {"hp": 1200, "pct_speed": 8, "pdef": 120, "mdef": 60, "support_active": "形昭 (探草显形并大范围减速)", "support_aura": "近卫 (提升友军高额双抗)"},
    "极影·形昭": {"hp": 1200, "pct_speed": 8, "cdr": 10, "support_active": "形昭 (探草显形并大范围减速)", "support_aura": "极影 (提升友军攻速/冷缩/双抗)"},
    "极影·星泉": {"hp": 1200, "pct_speed": 8, "cdr": 10, "support_active": "星泉 (分摊伤害并持续回血回蓝)", "support_aura": "极影 (提升友军攻速/冷缩/双抗)"},
}

def analyze_build(hero_cname: str, lane: str, items: list, arcana_list: list):
    """
    计算英雄在指定神装与铭文下的满级全维度数据
    """
    base = get_hero_base_stats(0, hero_cname) or {}
    b_hp = base.get("hp", (3200, 6800))[1]
    b_atk = base.get("atk", (170, 380))[1]
    b_pdef = base.get("pdef", (90, 360))[1]
    b_mdef = base.get("mdef", (50, 169))[1]
    b_speed = base.get("speed", 370)
    
    # 攻速成长 14 级累加
    as_raw = base.get("aspeed", "+2.0%")
    m_as = re.search(r'([\d\.]+)%', as_raw)
    as_growth = float(m_as.group(1)) if m_as else 2.0
    b_aspeed = as_growth * 14

    # 累加铭文
    arc_atk = 0
    arc_ap = 0
    arc_pdef = 0
    arc_mdef = 0
    arc_hp = 0
    arc_p_pierce = 0
    arc_m_pierce = 0
    arc_aspeed = 0
    arc_crit = 0
    arc_crit_eff = 0
    arc_cdr = 0
    arc_speed_pct = 0
    arc_p_vamp = 0
    arc_m_vamp = 0

    for item in arcana_list:
        if isinstance(item, list) and len(item) == 2:
            cnt, aname = item
        elif isinstance(item, tuple) and len(item) == 2:
            cnt, aname = item
        else:
            continue
        
        adef = ARCANA_LEVEL_5_DICT.get(aname, {})
        s1 = adef.get("stats_1", {})
        arc_atk += s1.get("phys_atk", 0) * cnt
        arc_ap += s1.get("magic_atk", 0) * cnt
        arc_pdef += s1.get("phys_def", 0) * cnt
        arc_mdef += s1.get("magic_def", 0) * cnt
        arc_hp += s1.get("max_hp", 0) * cnt
        arc_p_pierce += s1.get("phys_pierce", 0) * cnt
        arc_m_pierce += s1.get("magic_pierce", 0) * cnt
        arc_aspeed += s1.get("atk_speed_pct", 0) * cnt
        arc_crit += s1.get("crit_rate_pct", 0) * cnt
        arc_crit_eff += s1.get("crit_effect_pct", 0) * cnt
        arc_cdr += s1.get("cd_reduction_pct", 0) * cnt
        arc_speed_pct += s1.get("move_speed_pct", 0) * cnt
        arc_p_vamp += s1.get("phys_vamp_pct", 0) * cnt
        arc_m_vamp += s1.get("magic_vamp_pct", 0) * cnt

    # 累加装备
    eq_atk = 0
    eq_ap = 0
    eq_pdef = 0
    eq_mdef = 0
    eq_hp = 0
    eq_mp = 0
    eq_crit = 0
    eq_crit_eff = 0
    eq_aspeed = 0
    eq_cdr = 0
    eq_pct_speed = 0
    eq_flat_speed = 0
    eq_p_pierce_flat = 0
    eq_p_pierce_pct = 0
    eq_m_pierce_flat = 0
    eq_m_pierce_pct = 0
    eq_p_lifesteal = 0
    eq_m_lifesteal = 0
    has_hat = False
    has_prophecy = False
    knife_name = ""
    support_active = ""
    support_aura = ""

    for iname in items:
        # 鞋子移速
        if iname in BOOTS_MAP and eq_flat_speed == 0:
            eq_flat_speed = BOOTS_MAP[iname]
        
        st = ITEM_STATS_CACHE.get(iname, {})
        eq_atk += st.get("atk", 0)
        eq_ap += st.get("ap", 0)
        eq_pdef += st.get("pdef", 0)
        eq_mdef += st.get("mdef", 0)
        eq_hp += st.get("hp", 0)
        eq_mp += st.get("mp", 0)
        eq_crit += st.get("crit", 0)
        eq_crit_eff += st.get("crit_eff", 0)
        eq_aspeed += st.get("aspeed", 0)
        eq_cdr += st.get("cdr", 0)
        eq_pct_speed += st.get("pct_speed", 0)
        eq_p_pierce_flat += st.get("p_pierce_flat", 0)
        eq_p_pierce_pct = max(eq_p_pierce_pct, st.get("p_pierce_pct", 0))
        eq_m_pierce_flat += st.get("m_pierce_flat", 0)
        eq_m_pierce_pct = max(eq_m_pierce_pct, st.get("m_pierce_pct", 0))
        eq_p_lifesteal += st.get("p_lifesteal", 0)
        eq_m_lifesteal += st.get("m_lifesteal", 0)
        if st.get("has_hat"): has_hat = True
        if st.get("has_prophecy"): has_prophecy = True
        if st.get("knife_type"): knife_name = st["knife_type"]
        if st.get("support_active"): support_active = st["support_active"]
        if st.get("support_aura"): support_aura = st["support_aura"]

    # 最终结算
    final_raw_ap = eq_ap + arc_ap
    final_ap = math.floor(final_raw_ap * 1.3) if has_hat else final_raw_ap
    
    # 时之预言双抗转化 (每100点AP转16点双抗，上限250)
    if has_prophecy:
        proph_def = min(250, math.floor(final_ap / 100 * 16))
        eq_pdef += proph_def
        eq_mdef += proph_def

    final_atk = math.floor(b_atk + eq_atk + arc_atk)
    final_hp = math.floor(b_hp + eq_hp + arc_hp)
    final_pdef = math.floor(b_pdef + eq_pdef + arc_pdef)
    final_mdef = math.floor(b_mdef + eq_mdef + arc_mdef)
    final_pdef_dr = round(final_pdef / (final_pdef + 602) * 100, 1)
    final_mdef_dr = round(final_mdef / (final_mdef + 602) * 100, 1)
    
    final_crit = round(eq_crit + arc_crit, 1)
    final_crit_eff = round(200 + eq_crit_eff + arc_crit_eff, 1)
    final_aspeed = round(b_aspeed + eq_aspeed + arc_aspeed, 1)
    final_cdr = min(40, math.floor(eq_cdr + arc_cdr))
    
    total_speed_pct = eq_pct_speed + arc_speed_pct
    final_speed = math.floor((b_speed + eq_flat_speed) * (1 + total_speed_pct / 100))
    
    final_p_pierce_flat = math.floor(eq_p_pierce_flat + arc_p_pierce)
    final_m_pierce_flat = math.floor(eq_m_pierce_flat + arc_m_pierce)

    # 打靶伤害测算 (物理或法系)
    is_magic_hero = final_ap > 300
    if is_magic_hero:
        # 法系伤害测算
        # 靶子 1: 脆皮 200 魔抗
        eff_mdef_sq = max(0, (200 - final_m_pierce_flat) * (1 - eq_m_pierce_pct / 100))
        dr_sq = 1 - (eff_mdef_sq / (eff_mdef_sq + 602))
        dmg_squishy = math.floor((final_ap * 2.8 + 2000) * dr_sq)

        # 靶子 2: 坦克 600 魔抗
        eff_mdef_tk = max(0, (600 - final_m_pierce_flat) * (1 - eq_m_pierce_pct / 100))
        dr_tk = 1 - (eff_mdef_tk / (eff_mdef_tk + 602))
        dmg_tank = math.floor((final_ap * 2.8 + 2000) * dr_tk)
    else:
        # 物理伤害测算 (普攻+技能综合单套)
        # 靶子 1: 脆皮 400 物防
        eff_pdef_sq = max(0, (400 - final_p_pierce_flat) * (1 - eq_p_pierce_pct / 100))
        dr_sq = 1 - (eff_pdef_sq / (eff_pdef_sq + 602))
        crit_mult = 1 + (final_crit / 100) * ((final_crit_eff - 100) / 100)
        dmg_squishy = math.floor((final_atk * 3.2 + 1800) * crit_mult * dr_sq)

        # 靶子 2: 坦克 1200 物防
        eff_pdef_tk = max(0, (1200 - final_p_pierce_flat) * (1 - eq_p_pierce_pct / 100))
        dr_tk = 1 - (eff_pdef_tk / (eff_pdef_tk + 602))
        dmg_tank = math.floor((final_atk * 3.2 + 1800) * crit_mult * dr_tk)

    return {
        "atk": final_atk,
        "ap": final_ap,
        "hp": final_hp,
        "pdef": final_pdef,
        "pdef_dr": final_pdef_dr,
        "mdef": final_mdef,
        "mdef_dr": final_mdef_dr,
        "crit": final_crit,
        "crit_eff": final_crit_eff,
        "aspeed": final_aspeed,
        "cdr": final_cdr,
        "speed": final_speed,
        "p_pierce_flat": final_p_pierce_flat,
        "p_pierce_pct": eq_p_pierce_pct,
        "m_pierce_flat": final_m_pierce_flat,
        "m_pierce_pct": eq_m_pierce_pct,
        "dmg_squishy": dmg_squishy,
        "dmg_tank": dmg_tank,
        "knife_name": knife_name or "未装备专属野刀",
        "support_active": support_active or "通用主动辅助技能",
        "support_aura": support_aura or "近卫/极影光环增益",
        "is_magic": is_magic_hero
    }
