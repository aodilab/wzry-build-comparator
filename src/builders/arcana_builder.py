# -*- coding: utf-8 -*-
"""
王者荣耀铭文数据库构建器 (S45 官方权威基准 SSOT)
包含全套五级铭文数值、133 位国服全英雄官方推荐出装与铭文协同方案
彻底剔除旧版官网落后爬虫数据，铭文与装备深度捆绑
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import OUTPUT_DIR, DOC_ARCANA_NAME, ROLE_MAP
from config.hero_registry import CN_HERO_MANIFEST
from config.hero_arcana_data import ARCANA_LEVEL_5_DICT
from config.hero_official_builds import OFFICIAL_HERO_BUILDS
from src.core.item_calculator import RAW_TO_COMMON_MAP

# 属性中文字典映射
STAT_NAMES = {
    'magic_atk': '法术攻击力',
    'phys_atk': '物理攻击力',
    'phys_pierce': '物理穿透',
    'magic_pierce': '法术穿透',
    'atk_speed_pct': '攻速加成',
    'crit_rate_pct': '暴击率',
    'crit_effect_pct': '暴击效果',
    'max_hp': '最大生命',
    'phys_def': '物理防御力',
    'magic_def': '法术防御力',
    'phys_vamp_pct': '物理吸血',
    'magic_vamp_pct': '法术吸血',
    'move_speed_pct': '移速',
    'hp_regen': '生命回复',
    'cd_reduction_pct': '冷却缩减'
}

# 预设装备造价缓存（避免实时抓取失败）
ITEM_PRICE_MAP = {
    "暗影战斧": 2090, "宗师之力": 2100, "无尽战刃": 2140, "破军": 2950, "强者破军": 2950,
    "名刀·司命": 1900, "贪婪之噬": 2160, "巨人之握": 2160, "符文大剑": 2160,
    "影忍之足": 710, "抵抗之靴": 710, "冷静之靴": 710, "秘法之靴": 710, "急速战靴": 710, "疾步之靴": 710,
    "破晓": 3400, "仁者破晓": 3400, "幽影袖箭": 2040, "泣血之刃": 1800, "逐日之弓": 2100,
    "影刃": 2070, "末世": 2160, "闪电匕首": 1840, "寒霜袭侵": 2080, "纯净苍穹": 2120,
    "碎星锤": 2100, "暴烈之甲": 1950, "红莲斗篷": 2000, "霸者重装": 2070, "不死鸟之眼": 2100,
    "永夜守护": 2110, "魔女斗篷": 2080, "极寒风暴": 2100, "怒龙剑盾": 1960, "冰痕之握": 2020,
    "近卫·形昭": 1900, "极影·形昭": 1900, "近卫·救赎": 1900, "极影·救赎": 1900,
    "近卫·星泉": 1900, "极影·星泉": 1900, "近卫·奔狼": 1900, "极影·奔狼": 1900,
    "博学者之怒": 2300, "回响之杖": 2100, "痛苦面具": 2040, "日暮之流": 2120, "虚无法杖": 2110,
    "贤者之书": 2990, "贤者天书": 2990, "噬神之书": 2090, "辉月": 1990, "梦魇之牙": 2050,
    "冰霜冲击": 2100, "破魔刀": 2000, "制裁之刃": 1800, "时之预言": 2090, "圣杯": 1900
}

def calc_arcana_stats(arcana_dict):
    """计算整套铭文组合（30颗满配）的净属性总加成"""
    total = {}
    for color, mings in arcana_dict.items():
        for name, cnt in mings.items():
            if name in ARCANA_LEVEL_5_DICT:
                s1 = ARCANA_LEVEL_5_DICT[name].get("stats_1", {})
                for k, v in s1.items():
                    total[k] = total.get(k, 0.0) + v * cnt
    parts = []
    for k, v in total.items():
        label = STAT_NAMES.get(k, k)
        if "pct" in k or k in ["cd_reduction_pct", "crit_rate_pct", "crit_effect_pct", "phys_vamp_pct", "magic_vamp_pct", "move_speed_pct", "atk_speed_pct"]:
            parts.append(f"{label}+{v:.1f}%".replace(".0%", "%"))
        elif k in ["magic_atk", "phys_atk", "max_hp", "phys_def", "magic_def", "phys_pierce", "magic_pierce", "hp_regen"]:
            parts.append(f"{label}+{v:.1f}".replace(".0", ""))
        else:
            parts.append(f"{label}+{v}")
    return " ｜ ".join(parts) if parts else "暂无属性加成"

def calc_items_gold(items):
    """估算六神装总金币"""
    total = 0
    for iname in items:
        clean = RAW_TO_COMMON_MAP.get(iname, iname)
        total += ITEM_PRICE_MAP.get(clean, ITEM_PRICE_MAP.get(iname, 2050))
    return total

def build_arcana(output_file=None, *args, **kwargs):
    """构建王者荣耀 S45 全铭文属性与英雄搭配方案数据库"""
    print("1. 正在加载官方最新五级铭文图鉴数据...")

    # 第一部分：官方最新五级铭文图鉴
    markdown_content = "# 王者荣耀 S45 赛季（月照长安）全铭文属性及全英雄推荐搭配数据库\n\n"
    markdown_content += "> 📌 **版本权威基准与数据溯源 (SSOT)**：\n"
    markdown_content += "> - **唯一数据源**：100% 物理直读王者荣耀 S45 正式服官方推荐实录，彻底取代并删除旧版官网过时的静态网页爬虫建议（Tips）。\n"
    markdown_content += "> - **铭装物理捆绑**：铭文与出装绝对强耦合，每一套方案均完整收录标准五级铭文满配组合、总属性加成及对应的实战协同六神装。\n"
    markdown_content += "> - **国服全量覆盖**：全量收录 133 位国服正式服英雄（含新英雄王维、敖隐、戈娅、元流之子各形态等），涵盖 507 套权威对局方案。\n\n"
    markdown_content += "---\n\n"

    markdown_content += "## 第一部分：官方最新五级（高级）铭文图鉴\n\n"
    by_color = {"红色": [], "蓝色": [], "绿色": []}
    for m in ARCANA_LEVEL_5_DICT.values():
        c = m["color_name"]
        if c in by_color:
            by_color[c].append(m)

    for color, m_list in by_color.items():
        markdown_content += f"### {color}五级铭文\n\n"
        for m in m_list:
            markdown_content += f"#### 【{m['name']}】\n"
            markdown_content += f"- **单颗基础属性**：{m['raw_des']}\n"
            stats_10_list = []
            for k, v in m.get("stats_10", {}).items():
                label = STAT_NAMES.get(k, k)
                if "pct" in k:
                    stats_10_list.append(f"{label}+{v:.1f}%".replace(".0%", "%"))
                else:
                    stats_10_list.append(f"{label}+{v:.1f}".replace(".0", ""))
            markdown_content += f"- **满配（10颗）总属性**：{' / '.join(stats_10_list)}\n\n"

    # 第二部分：全英雄推荐搭配方案
    markdown_content += "---\n\n"
    markdown_content += "## 第二部分：133 位国服全英雄 S45 官方推荐铭文与出装协同方案\n\n"

    # 英雄元数据索引
    hero_meta = {}
    for eid, d in CN_HERO_MANIFEST.items():
        cname = d["cname"]
        roles = []
        r1 = d.get("hero_type")
        r2 = d.get("hero_type2")
        if r1 in ROLE_MAP:
            roles.append(ROLE_MAP[r1])
        if r2 in ROLE_MAP and ROLE_MAP[r2] not in roles:
            roles.append(ROLE_MAP[r2])
        role_str = "/".join(roles) if roles else "战士"
        hero_meta[cname] = {
            "title": d.get("title", ""),
            "role": role_str,
            "roles": roles if roles else ["战士"]
        }

    # 支持英雄双职业分类（严格收拢于游戏内坦克、战士、刺客、法师、射手 5 大真实职业，双职业英雄双端展示）
    role_order = ["坦克", "战士", "刺客", "法师", "射手"]
    by_role = {r: [] for r in role_order}

    for cname, hdata in OFFICIAL_HERO_BUILDS.items():
        meta = hero_meta.get(cname, {"title": "", "role": "战士", "roles": ["战士"]})
        for r in meta["roles"]:
            if r in by_role:
                by_role[r].append((cname, meta, hdata))

    for role_name in role_order:
        heroes_in_role = by_role[role_name]
        if not heroes_in_role:
            continue
        markdown_content += f"### 【职业定位：{role_name}】\n\n"

        for cname, meta, hdata in heroes_in_role:
            title_suffix = f"（{meta['title']}）" if meta['title'] else ""
            markdown_content += f"#### 英雄：{cname}{title_suffix}\n"
            markdown_content += f"- **职业定位**：{meta['role']}\n"
            markdown_content += "- **S45 官方实战出装与铭文协同方案**：\n\n"

            for l_key, blist in hdata.get("lanes", {}).items():
                for s_idx, b in enumerate(blist):
                    items_chain = " ➔ ".join(b.get("items", []))
                    total_gold = calc_items_gold(b.get("items", []))
                    arcana_str = b.get("arcana_desc", "")
                    arcana_stat_summary = calc_arcana_stats(b.get("arcana", {}))

                    markdown_content += f"##### 🛡️ 【{l_key}】方案{s_idx + 1}：【{b.get('title', '官方推荐')}】\n"
                    markdown_content += f"- **标准五级铭文组合 (30颗满配)**：`{arcana_str}`\n"
                    markdown_content += f"- **【铭文满配净属性总加成】**：{arcana_stat_summary}\n"
                    markdown_content += f"- **【实战协同六神装 (按成装顺序)】**：{items_chain}\n"
                    markdown_content += f"- **【协同装备总造价】**：约 {total_gold} 金币\n"
                    if b.get("desc"):
                        markdown_content += f"- **出装思路与战术搭配**：{b['desc']}\n"
                    markdown_content += "\n"

            markdown_content += "---\n\n"

    if not output_file:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, DOC_ARCANA_NAME)
    else:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"【成功】铭文与出装协同数据库已生成：'{output_file}'")
    return output_file

if __name__ == "__main__":
    build_arcana()
