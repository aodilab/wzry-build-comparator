# -*- coding: utf-8 -*-
"""
王者荣耀六神装属性计算与合成吞噬引擎
专为玩家日常装备调整设计：
1. 局内背包仅 6 槽位限制，逆向过滤小件原料；
2. 区分固定移速(鞋子+60)与百分比移速，按官方公式 (基础+固定)*(1+百分比) 算最终移速；
3. 计算物理/法术攻击(含博学者之怒+30%AP增幅)、双抗(附带减伤比例)、生命、蓝量、暴击、攻速(含15级自身成长)、吸血与穿透；
4. 自动扫描并诊断同名唯一被动互斥（强击/神速/穿透）。
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.item_recipes import COMPONENTS_MAP

# 鞋类唯一被动神速固定移速映射
BOOTS_SPEED_MAP = {
    "神速之靴": 30, "影忍之足": 60, "抵抗之靴": 60,
    "冷静之靴": 60, "秘法之靴": 60, "急速战靴": 60, "急速之靴": 60, "疾步之靴": 60
}

# 别名映射与老旧ID规范化
ITEM_ALIAS_MAP = {
    "强者破军": "破军", "仁者破晓": "破晓", "贤者天书": "贤者之书",
    "急速之靴": "急速战靴", "1722": "极影·星泉", "1747": "极影·星泉"
}

def clean_item_name(name):
    if not name: return ""
    n = name.strip()
    return ITEM_ALIAS_MAP.get(n, n)

def parse_single_item_stats(item_raw):
    """全量提取单件装备的属性词缀与被动"""
    if not item_raw: return {}
    des1 = item_raw.get("des1", "")
    des2 = item_raw.get("des2", "")
    full_text = re.sub(r'</?[^>]+>', '\n', f"{des1}\n{des2}")
    lines = [l.strip() for l in full_text.split('\n') if l.strip()]
    
    name = clean_item_name(item_raw.get("item_name", ""))
    stats = {
        "name": name, "atk": 0, "ap": 0, "pdef": 0, "mdef": 0, "hp": 0, "mp": 0,
        "crit": 0, "aspeed": 0, "cdr": 0, "percent_speed": 0, "flat_speed": 0,
        "p_lifesteal": 0, "m_lifesteal": 0, "p_pierce_flat": 0, "p_pierce_percent": 0,
        "m_pierce_flat": 0, "m_pierce_percent": 0, "has_hat": (name == "博学者之怒")
    }
    
    if name in BOOTS_SPEED_MAP:
        stats["flat_speed"] = BOOTS_SPEED_MAP[name]
        
    for line in lines:
        m = re.search(r'\+(\d+)\s*(?:物理攻击|物攻|物理)', line)
        if m and "防御" not in line and "吸血" not in line and "穿透" not in line: stats["atk"] += int(m.group(1))
        m = re.search(r'\+(\d+)\s*法术攻击', line)
        if m: stats["ap"] += int(m.group(1))
        m = re.search(r'\+(\d+)\s*(?:物理防御|物防)', line)
        if m: stats["pdef"] += int(m.group(1))
        m = re.search(r'\+(\d+)\s*法术防御', line)
        if m: stats["mdef"] += int(m.group(1))
        m = re.search(r'\+(\d+)\s*(?:最大生命|最大生命值|生命值|生命)', line)
        if m: stats["hp"] += int(m.group(1))
        m = re.search(r'\+(\d+)\s*最大法力', line)
        if m: stats["mp"] += int(m.group(1))
        m = re.search(r'\+(\d+(?:\.\d+)?)%\s*(?:暴击率|暴击)', line)
        if m: stats["crit"] += float(m.group(1))
        m = re.search(r'\+(\d+(?:\.\d+)?)%\s*(?:攻击速度|攻速)', line)
        if m: stats["aspeed"] += float(m.group(1))
        m = re.search(r'\+(\d+(?:\.\d+)?)%\s*(?:冷却缩减|冷却)', line)
        if m: stats["cdr"] += float(m.group(1))
        m = re.search(r'\+(\d+(?:\.\d+)?)%\s*(?:移动速度|移速)', line)
        if m: stats["percent_speed"] += float(m.group(1))
        m = re.search(r'\+(\d+)%\s*物理吸血', line)
        if m: stats["p_lifesteal"] += int(m.group(1))
        m = re.search(r'\+(\d+)%\s*法术吸血', line)
        if m: stats["m_lifesteal"] += int(m.group(1))
        if "暗影战斧" in name and "增加90~180点物理穿透" in line:
            stats["p_pierce_flat"] = 180
        if "碎星锤" in name and "30%物理穿透" in line:
            stats["p_pierce_percent"] = 30
        if "破晓" in name:
            stats["p_pierce_percent"] = 35
        if "虚无法杖" in name and "45%法术穿透" in line:
            stats["m_pierce_percent"] = 45
        if "秘法之靴" in name and "120" in line:
            stats["m_pierce_flat"] = 120
            
    return stats

def filter_effective_six_equips(equip_names):
    """从出装序列中提炼最终生效的最多 6 件终极成装（排除小件）"""
    norm = [clean_item_name(n) for n in equip_names if n]
    effective = []
    for i, current in enumerate(norm):
        is_consumed = False
        for j in range(i + 1, len(norm)):
            recipes = COMPONENTS_MAP.get(norm[j], [])
            if current in recipes:
                is_consumed = True
                break
        if not is_consumed:
            effective.append(current)
    return effective[-6:] if len(effective) > 6 else effective

# 局内主动技能装备列表 (单局默认仅有 1 个主动快捷键)
ACTIVE_SKILL_ITEMS = [
    "辉月", "难知·月神", "纯净苍穹", "不动·天穹", "逐日之弓", "迅疾·日渊",
    "血魔之怒", "侵掠·怒魂", "冰霜冲击", "徐行·凛冬", "幽影袖箭",
    "极影·救赎", "近卫·救赎", "极影·星泉", "近卫·星泉", "极影·奔狼", "近卫·奔狼", "极影·形昭", "近卫·形昭"
]

# 局内打野装备列表 (购买必须绑定惩击技能)
JUNGLE_ITEMS = ["贪婪之噬", "追击刀锋", "巨人之握", "巡守利斧", "符文大剑", "游击弯刀", "狩猎宽刃"]

def diagnose_passive_conflicts(effective_six):
    """自动诊断同名唯一被动、主动装备按键与打野刀技能绑定"""
    conflicts = []
    # 强击
    qiangji_items = [i for i in effective_six if i in ["宗师之力", "冰痕之握", "巫术法杖", "光辉之剑"]]
    if len(qiangji_items) > 1:
        conflicts.append(f"【唯一被动-强击】冲突：同时装备了 {', '.join(qiangji_items)}，仅生效其中一件！")
    # 神速双鞋
    boots = [i for i in effective_six if i in BOOTS_SPEED_MAP]
    if len(boots) > 1:
        conflicts.append(f"【唯一被动-神速】冲突：同时装备了多双鞋子（{', '.join(boots)}），移速不叠加！")
    # 主动技能槽位共存
    actives = [i for i in effective_six if i in ACTIVE_SKILL_ITEMS]
    if len(actives) > 1:
        conflicts.append(f"【主动技能按键共存提醒】：出装包含多件主动装备（{', '.join(actives)}），局内仅能快捷激活1件，其余须在背包手动切换释放！")
    # 打野刀惩击绑定
    jungles = [i for i in effective_six if i in JUNGLE_ITEMS]
    if jungles:
        conflicts.append(f"【召唤师技能绑定提示】：出装包含打野装备（{', '.join(jungles)}），局内必须携带召唤师技能【惩击】方可购买！")
    return conflicts

def calculate_build_stats(equip_names, equip_map_raw, hero_base_stats=None):
    """全维度计算六神装属性增幅、满级实战面板、总金币造价与被动冲突诊断"""
    effective_six = filter_effective_six_equips(equip_names)
    
    totals = {
        "atk": 0, "ap": 0, "pdef": 0, "mdef": 0, "hp": 0, "mp": 0,
        "crit": 0.0, "aspeed": 0.0, "cdr": 0.0, "percent_speed": 0.0,
        "flat_speed": 0, "p_lifesteal": 0, "m_lifesteal": 0,
        "p_pierce_flat": 0, "p_pierce_percent": 0, "m_pierce_flat": 0, "m_pierce_percent": 0,
        "has_hat": False
    }
    
    total_gold = 0
    boots_counted = False
    for name in effective_six:
        item_raw = equip_map_raw.get(name) or equip_map_raw.get(ITEM_ALIAS_MAP.get(name, ""))
        if item_raw:
            total_gold += item_raw.get("total_price", 0)
        st = parse_single_item_stats(item_raw)
        totals["atk"] += st.get("atk", 0)
        totals["ap"] += st.get("ap", 0)
        totals["pdef"] += st.get("pdef", 0)
        totals["mdef"] += st.get("mdef", 0)
        totals["hp"] += st.get("hp", 0)
        totals["mp"] += st.get("mp", 0)
        totals["crit"] += st.get("crit", 0.0)
        totals["aspeed"] += st.get("aspeed", 0.0)
        totals["cdr"] += st.get("cdr", 0.0)
        totals["percent_speed"] += st.get("percent_speed", 0.0)
        totals["p_lifesteal"] += st.get("p_lifesteal", 0)
        totals["m_lifesteal"] += st.get("m_lifesteal", 0)
        totals["p_pierce_flat"] += st.get("p_pierce_flat", 0)
        totals["p_pierce_percent"] = max(totals["p_pierce_percent"], st.get("p_pierce_percent", 0))
        totals["m_pierce_flat"] += st.get("m_pierce_flat", 0)
        totals["m_pierce_percent"] = max(totals["m_pierce_percent"], st.get("m_pierce_percent", 0))
        if st.get("has_hat"): totals["has_hat"] = True
        
        # 鞋子神速移速仅生效一次
        if st.get("flat_speed", 0) > 0 and not boots_counted:
            totals["flat_speed"] = st["flat_speed"]
            boots_counted = True

    # 帽子+30%法强被动
    final_ap = int(totals["ap"] * 1.3) if totals["has_hat"] else totals["ap"]
    capped_cdr = min(int(totals["cdr"]), 40)
    
    # 汇总增幅文案
    parts = []
    if totals["atk"] > 0: parts.append(f"物理攻击 +{totals['atk']}")
    if final_ap > 0:
        ap_desc = f"法术攻击 +{final_ap}" + ("(含帽子+30%增幅)" if totals['has_hat'] else "")
        parts.append(ap_desc)
    if totals["pdef"] > 0: parts.append(f"物理防御 +{totals['pdef']}")
    if totals["mdef"] > 0: parts.append(f"法术防御 +{totals['mdef']}")
    if totals["hp"] > 0: parts.append(f"最大生命 +{totals['hp']}")
    if totals["mp"] > 0: parts.append(f"最大法力 +{totals['mp']}")
    if totals["crit"] > 0: parts.append(f"暴击率 +{int(totals['crit'])}%")
    if totals["aspeed"] > 0: parts.append(f"攻击速度 +{int(totals['aspeed'])}%")
    pspeed_str = f"{totals['percent_speed']:.1f}".rstrip('0').rstrip('.')
    if totals["flat_speed"] > 0 or totals["percent_speed"] > 0:
        parts.append(f"移速 +{totals['flat_speed']}点固定/+{pspeed_str}%百分比")
    if totals["cdr"] > 0: parts.append(f"冷却缩减 +{capped_cdr}%" + ("(达40%上限)" if totals['cdr'] >= 40 else ""))
    if totals["p_lifesteal"] > 0: parts.append(f"物理吸血 +{totals['p_lifesteal']}%")
    if totals["m_lifesteal"] > 0: parts.append(f"法术吸血 +{totals['m_lifesteal']}%")
    if totals["p_pierce_flat"] > 0 or totals["p_pierce_percent"] > 0:
        parts.append(f"物理穿透 {totals['p_pierce_flat']}点固定/{totals['p_pierce_percent']}%比例")
    if totals["m_pierce_flat"] > 0 or totals["m_pierce_percent"] > 0:
        parts.append(f"法术穿透 {totals['m_pierce_flat']}点固定/{totals['m_pierce_percent']}%比例")
        
    summary_str = " ｜ ".join(parts) if parts else "纯功能/无基础属性增幅"
    
    # 终极实战面板预测
    final_panel = {}
    if hero_base_stats:
        b_hp = hero_base_stats["hp"][1]
        b_atk = hero_base_stats["atk"][1]
        b_pdef = hero_base_stats["pdef"][1]
        b_mdef = hero_base_stats["mdef"][1]
        b_speed = hero_base_stats["speed"]
        
        # 英雄攻速成长 (15级自带 14 级成长)
        growth_match = re.search(r'([\d\.]+)%', hero_base_stats.get("aspeed", "+1.0%"))
        growth_val = float(growth_match.group(1)) if growth_match else 1.0
        hero_self_aspeed = int(growth_val * 14)
        total_aspeed = hero_self_aspeed + int(totals["aspeed"])
        
        # 实战移速公式: (基础 + 固定鞋) * (1 + 百分比)
        calc_speed = int((b_speed + totals["flat_speed"]) * (1 + totals["percent_speed"] / 100))
        
        # 二次动态转化计算
        extra_pdef = 0
        extra_mdef = 0
        extra_pdef_note = ""
        extra_mdef_note = ""
        if "时之预言" in effective_six:
            prop_val = min(int(final_ap * 0.1), 250)
            extra_pdef += prop_val
            extra_mdef += prop_val
            extra_pdef_note = f"(含时之预言+{prop_val}) "
            extra_mdef_note = f"(含时之预言+{prop_val}) "
        if "破魔刀" in effective_six:
            pm_val = min(int((b_atk + totals["atk"]) * 0.5), 250)
            extra_mdef += pm_val
            extra_mdef_note += f"(含破魔刀+{pm_val}) "

        # 双抗免伤公式: 抗性 / (抗性 + 602)
        tot_pdef = b_pdef + totals["pdef"] + extra_pdef
        tot_mdef = b_mdef + totals["mdef"] + extra_mdef
        p_reduction = round(tot_pdef / (tot_pdef + 602) * 100, 1)
        m_reduction = round(tot_mdef / (tot_mdef + 602) * 100, 1)
        
        final_panel = {
            "final_hp": f"{b_hp} (基础) + {totals['hp']} (装备) = {b_hp + totals['hp']}",
            "final_atk": f"{b_atk} (基础) + {totals['atk']} (装备) = {b_atk + totals['atk']}",
            "final_ap": f"0 (基础) + {final_ap} (装备) = {final_ap}",
            "final_pdef": f"{b_pdef} (基础) + {totals['pdef']} (装备) = {tot_pdef} {extra_pdef_note}(物理免伤 {p_reduction}%)",
            "final_mdef": f"{b_mdef} (基础) + {totals['mdef']} (装备) = {tot_mdef} {extra_mdef_note}(法术免伤 {m_reduction}%)",
            "final_speed": f"({b_speed}基础 + {totals['flat_speed']}鞋子) × (1 + {pspeed_str}%) = {calc_speed}",
            "final_aspeed": f"{hero_self_aspeed}% (15级自带) + {int(totals['aspeed'])}% (装备) = {total_aspeed}%",
            "final_crit": f"{int(totals['crit'])}%",
            "final_cdr": f"{capped_cdr}%"
        }
        
    return {
        "effective_six": effective_six,
        "total_summary": summary_str,
        "total_gold": total_gold,
        "final_panel": final_panel,
        "conflicts": diagnose_passive_conflicts(effective_six)
    }
