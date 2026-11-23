# -*- coding: utf-8 -*-
"""
王者荣耀六神装属性计算与合成吞噬引擎
专为玩家日常装备调整设计：
1. 局内背包仅 6 槽位限制，逆向过滤小件原料；
2. 区分固定移速(鞋子+60)与百分比移速，按官方公式 (基础+固定)*(1+百分比) 算最终移速；
3. 计算物理/法术攻击(含博学者之怒+30%AP增幅)、双抗(附带减伤比例)、生命、蓝量、暴击、攻速(含15级自身成长)、吸血与穿透；
4. 自动扫描并诊断同名唯一被动互斥（强击/神速/穿透）。
"""
import re, sys, os, json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)
from config.item_recipes import COMPONENTS_MAP
from config.hero_registry import CN_HERO_MANIFEST
try:
    from config.hero_arcana_data import ARCANA_LEVEL_5_DICT
except ImportError:
    ARCANA_LEVEL_5_DICT = {}
try:
    from src.core.item_ground_truth_db import resolve_gt_name
except ImportError:
    _FALLBACK_ALIAS = {
        "破军": "强者破军", "破晓": "仁者破晓", "贤者之书": "贤者天书", "急速之靴": "急速战靴",
        "炽热支配者": "炽热支配", "铸梦·逐风": "逐风", "黑切": "暗影战斧", "红刀": "贪婪之噬",
        "小红刀": "追击刀锋", "肉刀": "巨人之握", "小肉刀": "巡守利斧", "蓝刀": "符文大剑",
        "小蓝刀": "游击弯刀", "抵抗鞋": "抵抗之靴", "布甲鞋": "影忍之足", "冷静鞋": "冷静之靴",
        "攻速鞋": "急速战靴", "法穿鞋": "秘法之靴", "疾步鞋": "疾步之靴", "冰脉": "冰痕之握",
        "冰痕": "冰痕之握", "冰心": "极寒风暴", "黄盾": "怒龙剑盾", "火甲": "红莲斗篷",
        "反甲": "反伤刺甲", "暴烈": "暴烈之甲", "不祥": "不祥征兆", "魔女": "魔女斗篷",
        "不死鸟": "不死鸟之眼", "永夜": "永夜守护", "霸者": "霸者重装", "血手": "血魔之怒",
        "苍穹": "纯净苍穹", "名刀": "名刀·司命", "复活甲": "贤者的庇护", "帽子": "博学者之怒",
        "面具": "痛苦面具", "血书": "噬神之书", "日暮": "日暮之流", "法穿棒": "虚无法杖",
    }
    def resolve_gt_name(name: str) -> str:
        n = (name or "").strip()
        return _FALLBACK_ALIAS.get(n, n)

def get_ground_truth_items(api_items=None):
    """以用户115张全装备截图(items_ground_truth.json)为唯一权威本地数据源，绝不向外网接口爬取"""
    gt_path = os.path.join(ROOT_DIR, "config", "items_ground_truth.json")
    gt_map = {}
    if os.path.exists(gt_path):
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_map = json.load(f)
    merged = []
    for cname, gt in gt_map.items():
        merged.append({
            "item_id": gt.get("item_id") or 9999,
            "item_name": cname,
            "item_type": gt.get("item_type", 1),
            "price": gt["total_price"],
            "total_price": gt["total_price"],
            "des1": gt["des1"],
            "des2": gt["des2"]
        })
    return merged

BOOTS_SPEED_MAP = {
    "神速之靴": 30, "影忍之足": 50, "抵抗之靴": 50,
    "冷静之靴": 50, "秘法之靴": 50, "急速战靴": 50, "急速之靴": 50, "疾步之靴": 70
}
RAW_TO_COMMON_MAP = {
    "强者破军": "破军", "仁者破晓": "破晓", "贤者天书": "贤者之书",
    "急速之靴": "急速战靴", "1722": "极影·星泉", "1747": "极影·星泉"
}
COMMON_TO_RAW_MAP = {
    "破军": "强者破军", "破晓": "仁者破晓", "贤者之书": "贤者天书",
    "急速之靴": "急速战靴"
}
ITEM_ALIAS_MAP = {**RAW_TO_COMMON_MAP, **COMMON_TO_RAW_MAP}

def clean_item_name(name):
    if not name: return ""
    gt = resolve_gt_name(name.strip())
    return RAW_TO_COMMON_MAP.get(gt, gt)

def get_raw_item_object(name, equip_map_raw):
    if not name or not equip_map_raw: return None
    gt = resolve_gt_name(name)
    for k in (name, gt, COMMON_TO_RAW_MAP.get(name), COMMON_TO_RAW_MAP.get(gt), RAW_TO_COMMON_MAP.get(name), RAW_TO_COMMON_MAP.get(gt)):
        if k and k in equip_map_raw: return equip_map_raw[k]
    return None

_HERO_MANIFEST_BY_CNAME = {v["cname"]: v for v in CN_HERO_MANIFEST.values()}
_MELEE_MAGE_FALLBACK = frozenset({"东皇太一", "鬼谷子", "墨子"})


def _fmt_num(val):
    v = round(float(val), 1)
    return str(int(v)) if v.is_integer() else f"{v:.1f}"


def _is_ranged_hero(hero_base_stats):
    """判定英雄是否为远程攻击英雄（与 build_stage_evaluator 同源：优先 attack_type=='ranged' 或 role_primary=='射手'）"""
    if not hero_base_stats:
        return False
    if "attack_type" in hero_base_stats or "role_primary" in hero_base_stats:
        return bool(hero_base_stats.get("attack_type") == "ranged" or hero_base_stats.get("role_primary") == "射手")
    cname = (hero_base_stats.get("cname") or "").strip()
    if cname and cname in _HERO_MANIFEST_BY_CNAME:
        try:
            from src.core.hero_mechanism_profiler import extract_hero_mechanism_profile
            prof = extract_hero_mechanism_profile(cname)
            return bool(prof.get("attack_type") == "ranged" or prof.get("role_primary") == "射手")
        except ImportError:
            meta = _HERO_MANIFEST_BY_CNAME.get(cname)
            if not meta:
                return False
            t1, t2 = meta.get("hero_type", 0), meta.get("hero_type2", 0)
            if t1 == 5 or t2 == 5:
                return True
            if t1 == 2 and cname not in _MELEE_MAGE_FALLBACK:
                return True
            return False
    if "is_ranged" in hero_base_stats:
        return bool(hero_base_stats["is_ranged"])
    return False


def _is_ap_hero(hero_base_stats):
    """判定英雄默认是否为法系主攻英雄（用于游走装 0 额外物攻/法攻时的自适应回退）"""
    if not hero_base_stats:
        return False
    if "is_ap_hero" in hero_base_stats:
        return bool(hero_base_stats["is_ap_hero"])
    cname = (hero_base_stats.get("cname") or "").strip()
    if not cname:
        return False
    try:
        from src.core.hero_combo_profiles import extract_hero_skill_model
        model = extract_hero_skill_model(cname)
        if model:
            return bool(model.get("is_ap_hero"))
    except ImportError:
        pass
    meta = _HERO_MANIFEST_BY_CNAME.get(cname)
    if not meta:
        return False
    t1, t2 = meta.get("hero_type", 0), meta.get("hero_type2", 0)
    return t1 == 2 or t2 == 2


_SKILLS_DB_CACHE = None


def _get_hero_crit_spec(hero_base_stats):
    """提取英雄天生暴击率、初始暴击效果与暴击率转暴效系数（优先机制画像，缺失时回退本地技能真值）。"""
    if not hero_base_stats:
        return 0.0, 200.0, 0.0
    if any(k in hero_base_stats for k in ("innate_crit_rate", "innate_crit_eff", "crit_rate_to_ceff_ratio")):
        return (
            float(hero_base_stats.get("innate_crit_rate", 0.0)),
            float(hero_base_stats.get("innate_crit_eff", 200.0)),
            float(hero_base_stats.get("crit_rate_to_ceff_ratio", 0.0)),
        )
    cname = (hero_base_stats.get("cname") or "").strip()
    if not cname:
        return 0.0, 200.0, 0.0
    try:
        from src.core.hero_mechanism_profiler import extract_hero_mechanism_profile
        prof = extract_hero_mechanism_profile(cname)
        return (
            float(prof.get("innate_crit_rate", 0.0)),
            float(prof.get("innate_crit_eff", 200.0)),
            float(prof.get("crit_rate_to_ceff_ratio", 0.0)),
        )
    except ImportError:
        global _SKILLS_DB_CACHE
        if _SKILLS_DB_CACHE is None:
            sk_path = os.path.join(ROOT_DIR, "config", "hero_skills_data.json")
            if os.path.exists(sk_path):
                with open(sk_path, "r", encoding="utf-8") as _sf:
                    _SKILLS_DB_CACHE = json.load(_sf)
            else:
                _SKILLS_DB_CACHE = {}
        full_text = " ".join((sk.get("desc") or "") for sk in (_SKILLS_DB_CACHE.get(cname) or []))
        m_cr = re.search(r"天生拥有\s*(\d+(?:\.\d+)?)%\s*暴击率", full_text)
        m_ce = re.search(r"初始(?:(?:只能)?(?:造成|暴击伤害为)\s*(\d+(?:\.\d+)?)%|(\d+(?:\.\d+)?)%\s*暴击(?:效果|伤害))", full_text)
        m_r = re.search(r"每\s*1%\s*暴击(?:率|几率)[^。；\n]{0,14}增加\s*(\d+(?:\.\d+)?)%\s*暴击(?:效果|伤害)", full_text)
        return (
            float(m_cr.group(1)) if m_cr else 0.0,
            float(m_ce.group(1) or m_ce.group(2)) if m_ce else 200.0,
            float(m_r.group(1)) if m_r else 0.0,
        )


def _parse_arcana_for_calc(arcana):
    """兼容 dict / [(cnt, name)] / 字符串格式的五级铭文属性汇总。"""
    out = {
        "atk": 0.0, "ap": 0.0, "hp": 0.0, "pdef": 0.0, "mdef": 0.0,
        "crit": 0.0, "crit_eff": 0.0, "aspeed": 0.0, "cdr": 0.0,
        "percent_speed": 0.0, "p_lifesteal": 0.0, "m_lifesteal": 0.0,
        "p_pierce_flat": 0.0, "m_pierce_flat": 0.0,
    }
    if not arcana or not ARCANA_LEVEL_5_DICT:
        return out
    pairs = []
    if isinstance(arcana, dict):
        for k, v in arcana.items():
            if isinstance(v, dict):
                for nm, cnt in v.items():
                    pairs.append((int(cnt or 0), str(nm).strip()))
            elif k in ARCANA_LEVEL_5_DICT and isinstance(v, (int, float)):
                pairs.append((int(v), k))
    else:
        seq = [x for x in re.split(r"[,，+|/\s]+", arcana.strip()) if x] if isinstance(arcana, str) else arcana
        for entry in (seq or []):
            if isinstance(entry, (list, tuple)) and len(entry) == 2:
                a, b = entry
                pairs.append((int(a), str(b).strip()) if isinstance(a, (int, float)) else (int(b), str(a).strip()))
            elif isinstance(entry, str):
                for tok in re.split(r"[,，+|/\s]+", entry.strip()):
                    m1 = re.match(r"^(\d+)\s*[xX×*]?\s*([\u4e00-\u9fa5]+)$", tok)
                    m2 = re.match(r"^([\u4e00-\u9fa5]+)\s*[xX×*]?\s*(\d+)$", tok)
                    if m1: pairs.append((int(m1.group(1)), m1.group(2)))
                    elif m2: pairs.append((int(m2.group(2)), m2.group(1)))
                    elif tok in ARCANA_LEVEL_5_DICT: pairs.append((10, tok))
    key_map = (
        ("atk", "phys_atk"), ("ap", "magic_atk"), ("hp", "max_hp"), ("pdef", "phys_def"), ("mdef", "magic_def"),
        ("crit", "crit_rate_pct"), ("crit_eff", "crit_effect_pct"), ("aspeed", "atk_speed_pct"), ("cdr", "cd_reduction_pct"),
        ("percent_speed", "move_speed_pct"), ("p_lifesteal", "phys_vamp_pct"), ("m_lifesteal", "magic_vamp_pct"),
        ("p_pierce_flat", "phys_pierce"), ("m_pierce_flat", "magic_pierce"),
    )
    for cnt, nm in pairs:
        if cnt <= 0:
            continue
        s1 = ARCANA_LEVEL_5_DICT.get(nm, {}).get("stats_1", {})
        for ok, sk in key_map:
            out[ok] += float(s1.get(sk, 0.0)) * cnt
    return out


def parse_single_item_stats(item_raw, is_ranged=False):
    """全量提取单件装备的基础面板属性词缀(100%严格只从 des1 提取，杜绝 des2 条件被动混入静态面板)"""
    if not item_raw: return {}
    full_text = re.sub(r'</?[^>]+>', '\n', f"{item_raw.get('des1', '')}")
    lines = [l.strip() for l in full_text.split('\n') if l.strip()]
    name = clean_item_name(item_raw.get("item_name", ""))
    stats = {
        "name": name, "atk": 0, "ap": 0, "pdef": 0, "mdef": 0, "hp": 0, "mp": 0,
        "crit": 0, "aspeed": 0, "cdr": 0, "percent_speed": 0, "flat_speed": BOOTS_SPEED_MAP.get(name, 0),
        "p_lifesteal": 0, "m_lifesteal": 0, "p_pierce_flat": 0, "p_pierce_percent": 0,
        "m_pierce_flat": 0, "m_pierce_percent": 0, "has_hat": (name == "博学者之怒")
    }
    for line in lines:
        if line.startswith("被动") or line.startswith("唯一") or line.startswith("主动"):
            continue
        m = re.search(r'\+(\d+)\s*(?:物理攻击|物攻|物理)', line)
        if m and not any(x in line for x in ("防御", "吸血", "穿透")): stats["atk"] += int(m.group(1))
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
        m = re.search(r'\+(\d+(?:\.\d+)?)%?\s*(?:移动速度|移速)', line)
        if m and name not in BOOTS_SPEED_MAP and float(m.group(1)) <= 20:
            stats["percent_speed"] += float(m.group(1))
        m = re.search(r'\+(\d+)%\s*物理吸血', line)
        if m: stats["p_lifesteal"] += int(m.group(1))
        m = re.search(r'\+(\d+)%\s*法术吸血', line)
        if m: stats["m_lifesteal"] += int(m.group(1))

    if "暗影战斧" in name: stats["p_pierce_flat"] = 180
    elif "碎星锤" in name: stats["p_pierce_percent"] = 30
    elif "破晓" in name: stats["p_pierce_percent"] = 30 if is_ranged else 15
    elif "虚无法杖" in name: stats["m_pierce_percent"] = 45
    elif "秘法之靴" in name: stats["m_pierce_flat"] = 120
    elif "云灵木" in name: stats["m_pierce_flat"] = 60
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
    "血魔之怒", "侵掠·怒魂", "冰霜冲击", "徐行·凛冬", "反伤刺甲", "幽影袖箭",
    "极影·救赎", "近卫·救赎", "极影·星泉", "近卫·星泉", "极影·奔狼", "近卫·奔狼", "极影·形昭", "近卫·形昭"
]

# 局内打野装备列表 (购买必须绑定惩击技能)
JUNGLE_ITEMS = ["贪婪之噬", "追击刀锋", "巨人之握", "巡守利斧", "符文大剑", "游击弯刀", "狩猎宽刃"]

def diagnose_passive_conflicts(effective_six):
    """自动诊断同名唯一被动、主动装备按键与打野刀技能绑定"""
    effective_six = [clean_item_name(x) for x in effective_six if x]
    conflicts = []
    # 强击
    qiangji_items = [i for i in effective_six if i in ["宗师之力", "冰痕之握", "巫术法杖"]]
    if len(qiangji_items) > 1:
        conflicts.append(f"【唯一被动-强击】冲突：同时装备了 {', '.join(qiangji_items)}，仅生效其中一件")
    # 冻伤
    dongshang_items = [i for i in effective_six if i in ["凝冰之息", "寒霜袭侵"]]
    if len(dongshang_items) > 1:
        conflicts.append(f"【唯一被动-冻伤】冲突：同时装备了 {', '.join(dongshang_items)}，同名冻伤被动不叠加")
    # 净魔
    jingmo_items = [i for i in effective_six if i in ["日暮之流", "破茧之衣"]]
    if len(jingmo_items) > 1:
        conflicts.append(f"【唯一被动-净魔】冲突：同时装备了 {', '.join(jingmo_items)}，同名法穿被动不叠加")
    # 破甲
    pojia_items = [i for i in effective_six if i in ["碎星锤", "破晓", "仁者破晓"]]
    if len(pojia_items) > 1:
        conflicts.append(f"【唯一被动-破甲】冲突：同时装备了 {', '.join(pojia_items)}，百分比物穿不叠加")
    # 重伤
    zhongshang_items = [i for i in effective_six if i in ["制裁之刃", "梦魇之牙", "红莲斗篷"]]
    if len(zhongshang_items) > 1:
        conflicts.append(f"【唯一被动-重伤】重叠：同时装备了 {', '.join(zhongshang_items)}，35%减疗效果不叠加")
    # 精准
    jingzhun_items = [i for i in effective_six if i in ["逐日之弓", "迅疾·日渊", "金色圣剑"]]
    if len(jingzhun_items) > 1:
        conflicts.append(f"【唯一被动-精准】冲突：同时装备了 {', '.join(jingzhun_items)}，同名普攻精准伤害不叠加")
    # 冰甲
    bingjia_items = [i for i in effective_six if i in ["冰霜冲击", "徐行·凛冬"]]
    if len(bingjia_items) > 1:
        conflicts.append(f"【唯一被动-冰甲】冲突：同时装备了 {', '.join(bingjia_items)}，同名冰甲韧性与护盾被动不叠加")
    # 狂怒
    kuangnu_items = [i for i in effective_six if i in ["血魔之怒", "侵掠·怒魂"]]
    if len(kuangnu_items) > 1:
        conflicts.append(f"【唯一被动-狂怒】冲突：同时装备了 {', '.join(kuangnu_items)}，同名狂怒普攻附伤被动不叠加")
    # 残废
    canfei_items = [i for i in effective_six if i in ["纯净苍穹", "不动·天穹"]]
    if len(canfei_items) > 1:
        conflicts.append(f"【唯一被动-残废】冲突：同时装备了 {', '.join(canfei_items)}，同名残废减速与降伤被动不叠加")
    # 月之守护
    yueshen_items = [i for i in effective_six if i in ["辉月", "难知·月神"]]
    if len(yueshen_items) > 1:
        conflicts.append(f"【唯一主动-月之守护】冲突：同时装备了 {', '.join(yueshen_items)}，同名月之守护金身主动不叠加")
    # 神速双鞋
    boots = [i for i in effective_six if i in BOOTS_SPEED_MAP]
    if len(boots) > 1:
        conflicts.append(f"【唯一被动-神速】冲突：同时装备了多双鞋子（{', '.join(boots)}），移速不叠加")
    # 游击多辅助装
    sup_items = [i for i in effective_six if any(k in i for k in ("近卫", "极影", "学识宝石"))]
    if len(sup_items) > 1:
        conflicts.append(f"【唯一被动-游击】冲突：同时装备了多件游走装（{', '.join(sup_items)}），光环与奖赏不叠加")
    # 主动技能槽位共存
    actives = [i for i in effective_six if i in ACTIVE_SKILL_ITEMS]
    if len(actives) > 1:
        conflicts.append(f"【主动技能按键共存提醒】：出装包含多件主动装备（{', '.join(actives)}），局内仅能快捷激活1件，其余须在背包手动切换释放")
    # 打野刀惩击绑定
    jungles = [i for i in effective_six if i in JUNGLE_ITEMS]
    if len(jungles) > 1:
        conflicts.append(f"【唯一被动-狩猎】冲突：同时装备了多把打野刀（{', '.join(jungles)}），叠层与灼烧不叠加")
    elif jungles:
        conflicts.append(f"【召唤师技能绑定提示】：出装包含打野装备（{', '.join(jungles)}），局内必须携带召唤师技能【惩击】方可购买")
    return conflicts

def calculate_build_stats(equip_names, equip_map_raw, hero_base_stats=None, arcana=None):
    """全维度计算六神装（及可选五级铭文）属性增幅、满级实战面板、总金币造价与被动冲突诊断"""
    effective_six = filter_effective_six_equips(equip_names)
    is_ranged = _is_ranged_hero(hero_base_stats)
    arc_st = _parse_arcana_for_calc(arcana)
    has_arc = bool(arcana and any(v != 0 for v in arc_st.values()))

    totals = {
        "atk": 0, "ap": 0, "pdef": 0, "mdef": 0, "hp": 0, "mp": 0,
        "crit": 0.0, "aspeed": 0.0, "cdr": 0.0, "percent_speed": 0.0,
        "flat_speed": 0, "p_lifesteal": 0, "m_lifesteal": 0,
        "p_pierce_flat": 0, "p_pierce_percent": 0, "m_pierce_flat": 0, "m_pierce_percent": 0,
        "tenacity": 0, "has_hat": False
    }

    def _jg_tier_of(nm: str) -> int:
        gt = resolve_gt_name(nm)
        if gt in ("贪婪之噬", "巨人之握", "符文大剑"):
            return 3
        if gt in ("追击刀锋", "巡守利斧", "游击弯刀"):
            return 2
        if gt == "狩猎宽刃":
            return 1
        return 0

    def _sup_tier_of(nm: str) -> int:
        gt = resolve_gt_name(nm)
        if any(k in gt for k in ("救赎", "奔狼", "形昭", "星泉")):
            return 3
        if "近卫" in gt or "极影" in gt:
            return 2
        return 0

    best_sup_idx = max(
        (i for i, nm in enumerate(effective_six) if _sup_tier_of(nm) > 0),
        key=lambda i: _sup_tier_of(effective_six[i]),
        default=-1,
    )
    best_jg_idx = max(
        (i for i, nm in enumerate(effective_six) if _jg_tier_of(nm) > 0),
        key=lambda i: _jg_tier_of(effective_six[i]),
        default=-1,
    )

    total_gold = 0
    tenacity_boots, tenacity_ice = False, False
    qiege_pen, mboots_pen, yunling_pen = 0, 0, 0
    sup_main_atk_bonus = 0
    for idx, name in enumerate(effective_six):
        item_raw = get_raw_item_object(name, equip_map_raw)
        if item_raw:
            total_gold += item_raw.get("total_price", 0)
        st = parse_single_item_stats(item_raw, is_ranged=is_ranged)
        for k in ("atk", "ap", "pdef", "mdef", "hp", "mp", "crit", "aspeed", "cdr", "percent_speed", "p_lifesteal", "m_lifesteal"):
            totals[k] += st.get(k, 0)
        if st.get("p_pierce_flat", 0) > 0:
            qiege_pen = max(qiege_pen, st["p_pierce_flat"])
        if st.get("m_pierce_flat", 0) > 0:
            if "秘法之靴" in name: mboots_pen = max(mboots_pen, st["m_pierce_flat"])
            elif "云灵木" in name: yunling_pen = max(yunling_pen, st["m_pierce_flat"])
            else: totals["m_pierce_flat"] += st["m_pierce_flat"]
        totals["p_pierce_percent"] = max(totals["p_pierce_percent"], st.get("p_pierce_percent", 0))
        totals["m_pierce_percent"] = max(totals["m_pierce_percent"], st.get("m_pierce_percent", 0))
        if st.get("has_hat"): totals["has_hat"] = True
        if st.get("flat_speed", 0) > 0:
            totals["flat_speed"] = max(totals["flat_speed"], st["flat_speed"])
        if name == "抵抗之靴": tenacity_boots = True
        elif name in ("冰霜冲击", "徐行·凛冬", "凛冬"): tenacity_ice = True

        gt_name = resolve_gt_name(name)
        if idx == best_sup_idx:
            is_tier3_sup = _sup_tier_of(gt_name) == 3
            totals["hp"] += 800 if is_tier3_sup else 400
            sup_main_atk_bonus = 50 if is_tier3_sup else 30
            if "近卫" in gt_name:
                def_b = 130 if is_tier3_sup else 72
                totals["pdef"] += def_b; totals["mdef"] += def_b
            else:
                totals["aspeed"] += 20 if is_tier3_sup else 12
                totals["cdr"] += 15 if is_tier3_sup else 9

        if idx == best_jg_idx:
            if "贪婪之噬" in gt_name: totals["atk"] += 75; totals["cdr"] += 5
            elif "巨人之握" in gt_name: totals["hp"] += 750; totals["cdr"] += 5
            elif "符文大剑" in gt_name: totals["ap"] += 150; totals["cdr"] += 5
            elif "追击刀锋" in gt_name: totals["atk"] += 45
            elif "巡守利斧" in gt_name: totals["hp"] += 450
            elif "游击弯刀" in gt_name: totals["ap"] += 90

    if sup_main_atk_bonus > 0:
        extra_ap = totals["ap"] + arc_st["ap"]
        extra_atk = totals["atk"] + arc_st["atk"]
        is_ap_hero = _is_ap_hero(hero_base_stats)
        if (extra_ap > extra_atk * 1.5) or (extra_ap == 0 and extra_atk == 0 and is_ap_hero):
            totals["ap"] += sup_main_atk_bonus * 2
        else:
            totals["atk"] += sup_main_atk_bonus

    max_tenacity = 25 if (hero_base_stats and hero_base_stats.get("cname") == "杨戬") else 60
    totals["tenacity"] = min(max_tenacity, (25 if tenacity_boots else 0) + (10 if tenacity_ice else 0))
    totals["p_pierce_flat"] += qiege_pen
    totals["m_pierce_flat"] += mboots_pen + yunling_pen
    bonus_hp_all = totals["hp"] + round(arc_st["hp"])
    if "霸者重装" in effective_six:
        bazhe_add = int(bonus_hp_all * 0.04)
        totals["hp"] += int(totals["hp"] * 0.04) if not has_arc else bazhe_add
        bonus_hp_all += bazhe_add
    if "破茧之衣" in effective_six:
        totals["ap"] += min(100, 40 + int(bonus_hp_all * 0.02))
        totals["m_pierce_flat"] += min(150, 60 + int(bonus_hp_all * 0.03))
    if "噬神之书" in effective_six:
        totals["cdr"] += int((totals["m_lifesteal"] + arc_st["m_lifesteal"]) / 2) if has_arc else int(totals["m_lifesteal"] / 2)
    # 注意：日暮之流(对英雄造成伤害叠层)、金色圣剑(普攻叠2层)、逐风(普攻技能命中叠5层)、影刃(普攻命中触发)均为战斗触发被动，严禁计入常驻静态面板！

    innate_cr, innate_ceff, ceff_per_cr = _get_hero_crit_spec(hero_base_stats)
    eff_crit_rate = min(100.0, round(innate_cr + arc_st["crit"] + totals["crit"], 1))
    has_infinity = ("无尽战刃" in effective_six or "无尽战刃" in [resolve_gt_name(x) for x in effective_six])
    inf_extra_ceff = min(50.0, 20.0 + int(eff_crit_rate // 2)) if has_infinity else 0.0
    extra_ceff = min(50.0, round(arc_st["crit_eff"], 1) + inf_extra_ceff)
    eff_crit_eff = innate_ceff + extra_ceff + (round(int(eff_crit_rate) * ceff_per_cr, 1) if ceff_per_cr > 0 else 0.0)
    eff_crit_eff = min(250.0, round(eff_crit_eff, 1))

    raw_ap_all = totals["ap"] + round(arc_st["ap"])
    final_ap = int(totals["ap"] * 1.3) if totals["has_hat"] else totals["ap"]
    panel_ap = int(raw_ap_all * 1.3) if totals["has_hat"] else raw_ap_all
    sb_cdr_bonus = 15.0 if (hero_base_stats and hero_base_stats.get("cname") == "孙膑") else 0.0
    capped_cdr = min(round(totals["cdr"], 1), 40.0)
    panel_cdr = min(round(totals["cdr"] + arc_st["cdr"] + sb_cdr_bonus, 1), 40.0) if has_arc else min(round(totals["cdr"] + sb_cdr_bonus, 1), 40.0)
    capped_cdr_str = _fmt_num(capped_cdr)
    panel_cdr_str = _fmt_num(panel_cdr if sb_cdr_bonus == 0 or has_arc else capped_cdr)
    crit_str = _fmt_num(totals["crit"])
    panel_crit_str = _fmt_num(eff_crit_rate)
    panel_ceff_str = _fmt_num(eff_crit_eff)
    aspeed_str = _fmt_num(totals["aspeed"])
    pspeed_str = _fmt_num(totals["percent_speed"])

    b_atk_ref = hero_base_stats["atk"][1] if hero_base_stats else 0
    atk_for_pomo = b_atk_ref + totals["atk"] + (round(arc_st["atk"]) if has_arc else 0)
    ap_for_prop = panel_ap if has_arc else final_ap
    base_eq_mdef = totals["mdef"] + (round(arc_st["mdef"]) if has_arc else 0)
    extra_pdef, extra_mdef = 0, 0
    extra_pdef_parts, extra_mdef_parts = [], []
    if "时之预言" in effective_six:
        prop_val = 100 + int(ap_for_prop * 0.1)
        extra_pdef += prop_val
        extra_mdef += prop_val
        extra_pdef_parts.append(f"时之预言{prop_val}")
        extra_mdef_parts.append(f"时之预言{prop_val}")
    if "破魔刀" in effective_six:
        pm_val = min(int(atk_for_pomo * 0.5), 250)
        extra_mdef += pm_val
        extra_mdef_parts.append(f"破魔刀{pm_val}")
    if "魔女斗篷" in effective_six:
        mn_val = int((base_eq_mdef + extra_mdef) * 0.15)
        extra_pdef += mn_val
        extra_pdef_parts.append(f"魔女{mn_val}")
    equip_pdef = totals["pdef"] + extra_pdef
    equip_mdef = totals["mdef"] + extra_mdef
    extra_pdef_desc = "、".join(extra_pdef_parts)
    extra_mdef_desc = "、".join(extra_mdef_parts)

    parts = []
    if totals["atk"] > 0: parts.append(f"物理攻击 +{totals['atk']}")
    if final_ap > 0:
        parts.append(f"法术攻击 +{final_ap}" + ("(含帽子+30%增幅)" if totals['has_hat'] else ""))
    if equip_pdef > 0:
        parts.append(f"物理防御 +{equip_pdef}" + (f"(含{extra_pdef_desc})" if extra_pdef_parts else ""))
    if equip_mdef > 0:
        parts.append(f"法术防御 +{equip_mdef}" + (f"(含{extra_mdef_desc})" if extra_mdef_parts else ""))
    if totals["hp"] > 0: parts.append(f"最大生命 +{totals['hp']}")
    if totals["mp"] > 0: parts.append(f"最大法力 +{totals['mp']}")
    if totals["crit"] > 0: parts.append(f"暴击率 +{crit_str}%")
    if totals["aspeed"] > 0: parts.append(f"攻击速度 +{aspeed_str}%")
    if totals["flat_speed"] > 0 or totals["percent_speed"] > 0:
        parts.append(f"移速 +{totals['flat_speed']}点固定/+{pspeed_str}%百分比")
    if totals["cdr"] > 0: parts.append(f"冷却缩减 +{capped_cdr_str}%" + ("(达40%上限)" if totals['cdr'] >= 40 else ""))
    if totals["p_lifesteal"] > 0: parts.append(f"物理吸血 +{totals['p_lifesteal']}%")
    if totals["m_lifesteal"] > 0: parts.append(f"法术吸血 +{totals['m_lifesteal']}%")
    if totals["p_pierce_flat"] > 0 or totals["p_pierce_percent"] > 0:
        parts.append(f"物理穿透 {totals['p_pierce_flat']}点固定/{totals['p_pierce_percent']}%比例")
    if totals["m_pierce_flat"] > 0 or totals["m_pierce_percent"] > 0:
        parts.append(f"法术穿透 {totals['m_pierce_flat']}点固定/{totals['m_pierce_percent']}%比例")
    summary_str = " ｜ ".join(parts) if parts else "纯功能/无基础属性增幅"

    final_panel = {}
    if hero_base_stats:
        b_hp, b_atk = hero_base_stats["hp"][1], hero_base_stats["atk"][1]
        b_pdef, b_mdef, b_speed = hero_base_stats["pdef"][1], hero_base_stats["mdef"][1], hero_base_stats["speed"]
        growth_match = re.search(r'([\d\.]+)%', hero_base_stats.get("aspeed", "+1.0%"))
        growth_val = float(growth_match.group(1)) if growth_match else 1.0
        raw_self_aspeed = round(float(hero_base_stats.get("aspeed_base", 0.0)) + growth_val * 14, 1)
        hero_self_aspeed = int(raw_self_aspeed) if raw_self_aspeed.is_integer() else raw_self_aspeed
        arc_as_add = arc_st["aspeed"] if has_arc else 0.0
        raw_tot_aspeed = round(raw_self_aspeed + totals["aspeed"] + arc_as_add, 1)
        total_aspeed = int(raw_tot_aspeed) if raw_tot_aspeed.is_integer() else raw_tot_aspeed
        tot_pspeed = totals["percent_speed"] + (arc_st["percent_speed"] if has_arc else 0.0)
        tot_pspeed_str = _fmt_num(tot_pspeed)
        calc_speed = round((b_speed + totals["flat_speed"]) * (1 + tot_pspeed / 100)) if has_arc else int((b_speed + totals["flat_speed"]) * (1 + totals["percent_speed"] / 100))

        arc_hp_i, arc_atk_i = (round(arc_st["hp"]) if has_arc else 0), (round(arc_st["atk"]) if has_arc else 0)
        arc_pdef_i, arc_mdef_i = (round(arc_st["pdef"]) if has_arc else 0), (round(arc_st["mdef"]) if has_arc else 0)
        tot_hp = b_hp + (bonus_hp_all if has_arc else totals["hp"])
        tot_atk = b_atk + totals["atk"] + arc_atk_i
        tot_ap = panel_ap if has_arc else final_ap
        # 双抗免伤公式: 抗性 / (抗性 + 602)
        tot_pdef = b_pdef + equip_pdef + arc_pdef_i
        tot_mdef = b_mdef + equip_mdef + arc_mdef_i
        p_reduction = round(tot_pdef / (tot_pdef + 602) * 100, 1)
        m_reduction = round(tot_mdef / (tot_mdef + 602) * 100, 1)
        arc_p_seg = f" + {arc_pdef_i} (铭文)" if arc_pdef_i > 0 else ""
        arc_m_seg = f" + {arc_mdef_i} (铭文)" if arc_mdef_i > 0 else ""
        pdef_extra_seg = f" + {extra_pdef} (被动转化:{extra_pdef_desc})" if extra_pdef > 0 else ""
        mdef_extra_seg = f" + {extra_mdef} (被动转化:{extra_mdef_desc})" if extra_mdef > 0 else ""
        hp_lhs = f"{b_hp} (基础) + {bonus_hp_all} (装备+铭文)" if has_arc else f"{b_hp} (基础) + {totals['hp']} (装备)"
        atk_lhs = f"{b_atk} (基础) + {totals['atk']} (装备) + {arc_atk_i} (铭文)" if arc_atk_i > 0 else f"{b_atk} (基础) + {totals['atk']} (装备)"
        as_arc_seg = f" + {_fmt_num(arc_as_add)}% (铭文)" if arc_as_add > 0 else ""

        final_panel = {
            "final_hp": f"{hp_lhs} = {tot_hp}",
            "final_atk": f"{atk_lhs} = {tot_atk}",
            "final_ap": f"0 (基础) + {tot_ap} ({'装备+铭文' if has_arc else '装备'}) = {tot_ap}",
            "final_pdef": f"{b_pdef} (基础) + {totals['pdef']} (装备){arc_p_seg}{pdef_extra_seg} = {tot_pdef} (物理免伤 {p_reduction}%)",
            "final_mdef": f"{b_mdef} (基础) + {totals['mdef']} (装备){arc_m_seg}{mdef_extra_seg} = {tot_mdef} (法术免伤 {m_reduction}%)",
            "final_speed": f"({b_speed}基础 + {totals['flat_speed']}鞋子) × (1 + {tot_pspeed_str}%) = {calc_speed}",
            "final_aspeed": f"{hero_self_aspeed}% (15级自带) + {aspeed_str}% (装备){as_arc_seg} = {total_aspeed}%",
            "final_crit": f"{panel_crit_str}%",
            "final_crit_eff": f"{panel_ceff_str}%",
            "final_cdr": f"{panel_cdr_str}%"
        }

    return {
        "effective_six": effective_six,
        "total_summary": summary_str,
        "total_gold": total_gold,
        "crit_rate": eff_crit_rate,
        "crit_eff": eff_crit_eff,
        "final_panel": final_panel,
        "conflicts": diagnose_passive_conflicts(effective_six)
    }
