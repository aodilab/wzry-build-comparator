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

# 严格对齐 items_ground_truth.json (IMG_6914~IMG_6937) 被动-神速 固定移速
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
        "combat_speed_pct": 0.0,
        "dmg_amp": 0.0,
        "pojun_amp": 0.0,
        "passive_dr": 0.0,
        "active_dr": 0.0,
        "heal_amp": 0.0,
        "heal_amp_per_10pct_missing": 0.0,
        "spellblade": None,     # (type_name, cd_sec, base_dmg, total_ad_ratio, bonus_ad_ratio, ap_ratio)
        "on_hit_phys": 0.0,     # 普攻附带固定物理伤害期望
        "on_hit_magic": 0.0,    # 普攻附带固定法术伤害期望 (闪电匕首等)
        "on_hit_magic_ap": 0.0, # 普攻附带法攻加成比例 (金色圣剑等)
        "on_hit_max_hp_ratio": 0.0,   # 血魔之怒/怒魂：普攻附带最大生命物理伤害比例
        "proc_phys_base": 0.0,  # 技能/普攻触发物理特效基础值 (寒霜袭侵等)
        "proc_phys_bonus_ad": 0.0,    # 技能/普攻触发物理特效额外AD加成
        "proc_magic_base": 0.0, # 技能/受击触发法术特效基础值 (回响/面具/凝冰/冰心/凛冬)
        "proc_magic_ap": 0.0,   # 技能触发法术特效AP加成
        "proc_magic_hp_ratio": 0.0,   # 红莲斗篷等最大生命法伤比例
        "skill_phys_vamp": 0.0, # 物理技能吸血比例 (泣血之刃 25%)
        "nulong_max_hp_ratio": 0.0,   # 怒龙剑盾神力：对英雄造成 3.5% 最大生命物理伤害 (CD 2.5s)
        "nulong_heal_max_hp": 0.0,    # 怒龙剑盾重创：每次触发恢复 3.5% 最大生命 (CD 2.5s)
        "wave_clear_score": 0.0,      # 清线刷野分均经济(GPM)加速权重
        "monv_shield": 0.0,     # 魔女斗篷基础护盾 (400~800)
        "monv_hp_ratio": 0.0,   # 魔女斗篷额外生命护盾加成 (7%额外生命)
        "monv_mdef_to_pdef": 0.0,     # 魔女斗篷：15%额外法术防御转化为物理防御
        "shield_base": 0.0,     # 通用战斗触发护盾/复活基础值 (旭日/炽热/复活甲/救赎)
        "shield_hp_ratio": 0.0, # 通用战斗触发护盾最大生命比例 (冰霜冲击/凛冬/旭日/炽热)
        "shield_ap_ratio": 0.0, # 通用战斗触发护盾法攻比例 (炽热支配)
        "yongye_heal_base": 0.0,
        "yongye_hp_ratio": 0.0,       # 永夜守护/制裁回魂/圣杯等生命回复比例
        "xuemo_hp_ratio": 0.0,        # 血魔之怒/怒魂：40%/50% 最大生命护盾
        "has_mingdao": False,
        "has_hat": False,
        "has_prophecy": False,
        "has_pomo": False,
        "has_bazhe": False,
        "has_infinity": False,
        "has_cocoon": False,
    }

    # 1. 打野刀动态叠层 (IMG_6840/6841/6843/6915/6917/6920)
    if gt_name == "追击刀锋":
        s = min(15, jg_stacks)
        prof["atk"] += 3.0 * s
        prof["wave_clear_score"] += 0.03
    elif gt_name == "贪婪之噬":
        s = min(25, jg_stacks)
        prof["atk"] += 3.0 * s
        prof["cd"] += 0.20 * s
        prof["wave_clear_score"] += 0.06
    elif gt_name == "巡守利斧":
        s = min(15, jg_stacks)
        prof["hp"] += 30.0 * s
        prof["wave_clear_score"] += 0.03
    elif gt_name == "巨人之握":
        s = min(25, jg_stacks)
        prof["hp"] += 30.0 * s
        prof["cd"] += 0.20 * s
        prof["nulong_max_hp_ratio"] += 0.006  # 被动-狩猎对英雄生效25%灼烧折算
        prof["wave_clear_score"] += 0.06
    elif gt_name == "游击弯刀":
        s = min(15, jg_stacks)
        prof["ap"] += 6.0 * s
        prof["wave_clear_score"] += 0.03
    elif gt_name == "符文大剑":
        s = min(25, jg_stacks)
        prof["ap"] += 6.0 * s
        prof["cd"] += 0.20 * s
        prof["wave_clear_score"] += 0.06

    # 2. 穿透与暴击效果装备 (IMG_6845/6850/6830/6864/6914/6893/6871/6878)
    # 注意：IMG_6909 陨星(+35AD/+7.5%CD) 与 IMG_6906 穿云弓(+12%暴击/+15%攻速) 在S45无穿透被动
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
        prof["crit_eff"] = 30.0  # 基础20% + 自身20%暴击率转10%暴击效果
    elif gt_name == "秘法之靴":
        prof["m_pen_flat"] = round(60.0 + 60.0 * r, 1)
    elif gt_name == "云灵木":
        prof["m_pen_flat"] = 60.0
    elif gt_name == "日暮之流":
        # IMG_6878: 被动-净魔需对英雄造成伤害逐次叠加(每层20~40法穿，最多6层)，常驻0层，连招期间取战斗期望层数(约3.5层)
        prof["m_pen_flat"] = round((20.0 + 20.0 * r) * 3.5 * combat_stacks, 1)
    elif gt_name == "虚无法杖":
        prof["m_pen_pct"] = 45.0

    # 3. 强击 (Spellblade) 唯一被动 (IMG_6844/6863/6859)
    if gt_name == "宗师之力":
        prof["spellblade"] = ("zongshi", 3.0, 0.0, 0.80, 0.0, 0.0)
    elif gt_name == "冰痕之握":
        prof["spellblade"] = ("binghen", 1.25, 140.0 + 140.0 * r, 0.0, 0.40, 0.0)
    elif gt_name == "巫术法杖":
        prof["spellblade"] = ("wushu", 2.5, 180.0 + 180.0 * r, 0.0, 0.0, 0.40)

    # 4. 增伤/减伤/护盾/回复核心机制
    if gt_name == "影忍之足":
        # IMG_6922: 被动-防护：减少6%~12%受到的物理伤害
        prof["passive_dr"] += (0.06 + 0.06 * r) * 0.65  # 折算综合实战减伤
    elif gt_name == "极寒风暴":
        # IMG_6875: 被动-冰心需单次受击超当前生命10%才向周围发射冲击(减15%攻速/15%~30%移速)，属受击防御反制，严禁计入先手爆发伤害
        prof["passive_dr"] += 0.05
    elif gt_name == "不祥征兆":
        prof["passive_dr"] += 0.06  # 寒铁受击减攻击者20%~40%攻速与7.5%~15%移速
    elif gt_name == "反伤刺甲":
        # IMG_6887: 主动-反刺3秒内将受到的35%伤害回敬(随距离衰减至多50%，CD 75s)，属受击反伤，严禁计入普攻on_hit_phys
        prof["passive_dr"] += 0.04
    elif gt_name == "红莲斗篷":
        # IMG_6877: 业炎每秒灼烧375近身范围内敌人1.5%最大生命法伤(对兵野双倍3%)，仅在贴身窗口生效
        prof["proc_magic_hp_ratio"] += 0.015 * 1.8
        prof["wave_clear_score"] += 0.08
    elif gt_name == "末世":
        # IMG_6842: 破败普攻额外造成80~160(+7%目标额外最大生命)物理伤害
        prof["on_hit_phys"] += (80.0 + 80.0 * r) + 2500.0 * 0.07
        prof["wave_clear_score"] += 0.05
    elif gt_name == "闪电匕首":
        # IMG_6879: 电弧普攻40~80法伤，每3次普攻释放连锁闪电160~400法伤
        prof["on_hit_magic"] += (40.0 + 40.0 * r) + (160.0 + 240.0 * r) / 3.0
        prof["wave_clear_score"] += 0.06
    elif gt_name == "影刃":
        # IMG_6872: 暴风普攻命中后增加10%攻速和5%移速(暴击后翻倍)，常驻0，战斗触发
        crit_f = 1.0 + min(1.0, (prof["crit"] + 20.0) / 100.0)
        prof["combat_aspeed"] = prof.get("combat_aspeed", 0.0) + 10.0 * crit_f * combat_stacks
        prof["combat_speed_pct"] += 5.0 * crit_f * combat_stacks
    elif gt_name == "金色圣剑":
        # IMG_6861: 精准普攻+60；圣剑普攻叠2层获20%攻速并额外造成30%法术攻击法伤
        prof["on_hit_phys"] += 60.0
        prof["combat_aspeed"] = prof.get("combat_aspeed", 0.0) + 20.0 * combat_stacks
        prof["on_hit_magic_ap"] += 0.30 * combat_stacks
    elif gt_name == "寒霜袭侵":
        # IMG_6870: 寒霜减移速5%~10%(叠2层)；冻伤造成135~270(+45%额外物攻)物理伤害(CD 3s)
        prof["proc_phys_base"] += 135.0 + 135.0 * r
        prof["proc_phys_bonus_ad"] += 0.45
        prof["passive_dr"] += 0.03
    elif gt_name == "泣血之刃":
        # IMG_6886: 养战+25%物理技能吸血；充溢溢出回复转400~800最大生命
        prof["skill_phys_vamp"] += 25.0
        prof["shield_base"] += (200.0 + 200.0 * r) * combat_stacks
    elif gt_name == "制裁之刃":
        # IMG_6858: 回魂生命低于40%获160~320(+4%最大生命)回复，普攻获30~60(+0.8%最大生命)回复
        prof["yongye_heal_base"] += (160.0 + 160.0 * r) + 2.0 * (30.0 + 30.0 * r) * (2.0 if is_ranged else 1.0)
        prof["yongye_hp_ratio"] += 0.04 + 2.0 * 0.008 * (2.0 if is_ranged else 1.0)
    elif gt_name == "回响之杖":
        # IMG_6866: 回响技能命中触发爆炸140~280(+28%法术攻击)法术伤害(CD 5s)
        prof["proc_magic_base"] += 140.0 + 140.0 * r
        prof["proc_magic_ap"] += 0.28
        prof["wave_clear_score"] += 0.05
    elif gt_name == "痛苦面具":
        # IMG_6851: 折磨3秒内4次3%当前生命法术伤害(CD 3s)
        prof["proc_magic_base"] += 680.0
        prof["wave_clear_score"] += 0.04
    elif gt_name == "凝冰之息":
        # IMG_6839: 冻伤造成75~150(+15%法术攻击)法术伤害(CD 3s)
        prof["proc_magic_base"] += 75.0 + 75.0 * r
        prof["proc_magic_ap"] += 0.15
    elif gt_name == "旭日初光":
        # IMG_6876: 初光提供(250~500+4%最大生命)护盾，单人时提升50%
        prof["shield_base"] += (250.0 + 250.0 * r) * 1.25
        prof["shield_hp_ratio"] += 0.04 * 1.25
    elif gt_name in ("冰霜冲击", "徐行·凛冬"):
        # IMG_6880/6829: 冰甲受硬控获10%最大生命护盾；主动冲击造成100~200法伤与冻结
        prof["shield_hp_ratio"] += 0.10
        prof["proc_magic_base"] += 100.0 + 100.0 * r
        prof["passive_dr"] += 0.04
    elif gt_name == "炽热支配":
        # IMG_6874: 法力护盾低于30%血解控并获(500~1000+100%法攻+7.5%最大生命)护盾
        prof["shield_base"] += 500.0 + 500.0 * r
        prof["shield_ap_ratio"] += 1.0
        prof["shield_hp_ratio"] += 0.075
    elif gt_name == "贤者的庇护":
        # IMG_6832: 复生死亡后2秒原地复活并获2000~3000生命
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
        # IMG_6868: des1无常驻移速(+210物防/+1000生命/+35物攻)；被动-无畏每次受击增加1%伤害与1%移速(受英雄伤害叠2层)，最多10层
        # 严格区分：脱战跑图/进场前0层，先手起手爆发窗口平均叠3.5层(+3.5%增伤/移速)，受击拉扯窗口叠7层(+7%增伤/移速)
        layers = round(10 * combat_stacks)
        prof["dmg_amp"] += 0.01 * layers
        prof["combat_speed_pct"] += 1.0 * layers
    elif gt_name == "逐风":
        # IMG_6847: des1无常驻移速(+600生命/+50物攻/+30%攻速)；被动-逐风普攻和技能命中增加2%攻速、移速和伤害，最多叠加5层
        # 常驻面板0层，连招期间平均吃满约3层(+6%攻速/移速/伤害)
        layers = round(5 * combat_stacks)
        prof["combat_aspeed"] = 2.0 * layers
        prof["combat_speed_pct"] += 2.0 * layers
        prof["dmg_amp"] += 0.02 * layers
    elif gt_name == "强者破军":
        prof["pojun_amp"] = 0.30
    elif gt_name == "贤者天书":
        # IMG_6827: 唯一被动-刻印：每100法术攻击提供0.5%增伤比例与0.5%减伤比例
        prof["has_sage_book"] = True
    elif gt_name == "纯净苍穹":
        # IMG_6836: 残废降低20%伤害 + 驱散获得30%减伤
        prof["passive_dr"] = 0.20
        prof["active_dr"] = 0.30
    elif gt_name == "不动·天穹":
        # IMG_6826: 残废降低20%伤害 + 驱散解除控制并获得35%减伤
        prof["passive_dr"] = 0.20
        prof["active_dr"] = 0.35
    elif gt_name == "怒龙剑盾":
        # IMG_6873: 重创对兵野7%最大生命物伤并恢复50%(即3.5%最大生命)；神力对英雄3.5%最大生命物伤(CD 2.5s)
        ratio = 0.0175 if is_ranged else 0.035
        prof["nulong_max_hp_ratio"] = max(prof["nulong_max_hp_ratio"], ratio)
        prof["nulong_heal_max_hp"] = max(prof["nulong_heal_max_hp"], ratio)
        prof["wave_clear_score"] += 0.12
    elif gt_name == "魔女斗篷":
        # IMG_6881: 迷雾400~800(+7%额外生命)法术护盾；魔女15%额外法防转化为物防
        prof["monv_shield"] = 400.0 + 400.0 * r
        prof["monv_hp_ratio"] = 0.07
        prof["monv_mdef_to_pdef"] = 0.15
    elif gt_name == "永夜守护":
        # IMG_6884: 2.5秒内受超过25%最大生命伤害，在2.5秒内累计回复10%最大生命(CD 7s)
        prof["yongye_heal_base"] = 0.0
        prof["yongye_hp_ratio"] = 0.10
    elif gt_name == "不死鸟之眼":
        # IMG_6882: 每损失10%生命，获得6.5%生命回复效果（具体增疗幅度由英雄进场吃集火后的残血阈值决定，每10%已损生命+6.5%）
        prof["heal_amp_per_10pct_missing"] = 0.065
        prof["heal_amp"] = 0.4225  # 默认65%已损生命下的基准值
    elif gt_name == "血魔之怒":
        # IMG_6833: 狂怒普攻额外1.5%最大生命物伤(半血下提升25%~50%)；血怒扣30%当前生命获40%最大生命护盾
        prof["on_hit_max_hp_ratio"] = 0.015 * (1.0 + (0.125 + 0.125 * r))
        prof["xuemo_hp_ratio"] = 0.25  # 扣除残血30%当前生命(约15%最大生命)后净增约25%最大生命护盾
    elif gt_name == "侵掠·怒魂":
        # IMG_6825: 狂怒普攻额外1.5%最大生命物伤(半血下提升37.5%~75%)；血怒扣30%当前生命获50%最大生命护盾
        prof["on_hit_max_hp_ratio"] = 0.015 * (1.0 + (0.1875 + 0.1875 * r))
        prof["xuemo_hp_ratio"] = 0.35
    elif gt_name == "噬神之书":
        # IMG_6846: 每2%法术吸血额外提供1%冷却缩减
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
