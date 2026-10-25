# -*- coding: utf-8 -*-
"""
王者荣耀全英雄技能数值与等级成长数据库构建器
专注微观操作与数值成长：基础属性、技能Lv1-Lv6数值阶梯、冷却消耗、加成公式
100% 锁定本地权威数据集 (config/hero_skills_data.py & config/patches/)，绝不向外网爬取
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import OUTPUT_DIR, DOC_HERO_SKILLS_NAME, ROLE_MAP
try:
    from config.patches import REWORKED_HERO_SKILLS_PATCHES
except ImportError:
    REWORKED_HERO_SKILLS_PATCHES = {}
from config.hero_base_stats import get_hero_base_stats
from config.hero_skills_data import HERO_SKILLS_DATA
from src.core.stats_parser import format_cd_steps, format_cost_steps, extract_desc_growth_lines
from src.core.hero_validator import get_validated_hero_list


def fetch_single_hero_skills(hero):
    """
    从本地权威基准库 (HERO_SKILLS_DATA & REWORKED_HERO_SKILLS_PATCHES) 读取单个英雄的技能全量数值与机制，绝不向外网爬取
    """
    ename = str(hero.get("ename"))
    cname = hero.get("cname")
    title = hero.get("title", "")

    roles = []
    r1 = hero.get("hero_type")
    r2 = hero.get("hero_type2")
    if r1 in ROLE_MAP:
        roles.append(ROLE_MAP[r1])
    if r2 in ROLE_MAP and ROLE_MAP[r2] not in roles:
        roles.append(ROLE_MAP[r2])
    role_str = "/".join(roles) if roles else "战士"

    base_list = [dict(s) for s in HERO_SKILLS_DATA.get(cname, [])]
    if cname in REWORKED_HERO_SKILLS_PATCHES and "skills" in REWORKED_HERO_SKILLS_PATCHES[cname]:
        patch_list = REWORKED_HERO_SKILLS_PATCHES[cname]["skills"]
        if len(base_list) == len(patch_list):
            skills_list = [{**b, **p} for b, p in zip(base_list, patch_list)]
        else:
            skills_list = [dict(p) for p in patch_list]
    else:
        skills_list = base_list

    base_stats = get_hero_base_stats(ename, cname, role_str)
    return {
        "ename": ename,
        "cname": cname,
        "title": title,
        "role": role_str,
        "base_stats": base_stats,
        "skills": skills_list,
        "success": bool(skills_list)
    }


def build_hero_skills(output_file=None, max_workers=10):
    """
    构建全英雄技能数值与等级成长数据库 (100% 本地权威数据源)
    """
    heroes = get_validated_hero_list()
    print(f"开始从本地权威库加载 {len(heroes)} 位国服英雄全技能等级数值与微观基础属性...")

    hero_results = []
    for hero in heroes:
        res = fetch_single_hero_skills(hero)
        if res.get("success"):
            hero_results.append(res)
        else:
            print(f"缺失警告: {res['cname']}")

    markdown_content = "# 王者荣耀 S45 赛季（月照长安）全英雄技能数值与等级成长数据库\n\n"
    markdown_content += f"> 本知识库收录王者荣耀 S45 赛季“月照长安”国服全量 {len(hero_results)} 位正统英雄（含第133位新英雄王维及技能重做英雄）的微观数值面板：包含1~15级基础属性、技能Lv1-Lv6等级数值阶梯、冷却消耗与加成公式。专为 NotebookLM / RAG 优化。\n\n"

    by_role = {}
    for h in hero_results:
        role = h["role"].split("/")[0]
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(h)

    for role, h_list in by_role.items():
        markdown_content += f"# ============= 【职业领域：{role}】 =============\n\n"
        for h in h_list:
            markdown_content += f"## 英雄：{h['cname']}（{h.get('title', '')}）\n"
            markdown_content += f"- **职业定位**：{h.get('role', '未知')}\n\n"

            stats = h.get("base_stats", {})
            if stats:
                hp_min, hp_max = stats.get("hp", (3000, 6000))
                atk_min, atk_max = stats.get("atk", (160, 350))
                pdef_min, pdef_max = stats.get("pdef", (90, 350))
                mdef_min, mdef_max = stats.get("mdef", (50, 169))
                speed = stats.get("speed", 380)
                aspeed = stats.get("aspeed", "+1.0%")

                markdown_content += "### 【英雄核心基础属性面板 (1级基础 / 15级满级)】\n"
                markdown_content += f"- **基础最大生命值**：{hp_min} (15级满级: {hp_max}，每级成长: +{(hp_max-hp_min)/14:.1f})\n"
                markdown_content += f"- **基础物理攻击力 (物攻)**：{atk_min} (15级满级: {atk_max}，每级成长: +{(atk_max-atk_min)/14:.1f})\n"
                markdown_content += f"- **基础物理防御力 (物抗)**：{pdef_min} (15级满级: {pdef_max}，每级成长: +{(pdef_max-pdef_min)/14:.1f})\n"
                markdown_content += f"- **基础法术防御力 (魔抗)**：{mdef_min} (15级满级: {mdef_max}，每级成长: +{(mdef_max-mdef_min)/14:.1f})\n"
                markdown_content += f"- **基础移动速度 (移速)**：{speed}\n"
                markdown_content += f"- **攻击速度每级成长**：{aspeed}/级\n\n"

            markdown_content += "### 【技能机制与各等级数值阶梯】\n"
            for s_idx, skill in enumerate(h.get("skills", [])):
                skill_type = "被动技能" if s_idx == 0 else f"主动技能 {s_idx}"
                markdown_content += f"#### {skill_type}：{skill.get('name', '未知技能')}\n"
                is_ult = (s_idx >= 3)
                cd_formatted = format_cd_steps(skill.get('cd', ''), is_ult=is_ult)
                markdown_content += f"- **各等级冷却时间 (CD)**：{cd_formatted}\n"

                cost_formatted = format_cost_steps(skill.get('cost', ''), is_ult=is_ult)
                markdown_content += f"- **各等级法力/能量消耗**：{cost_formatted}\n"

                growth_lines = extract_desc_growth_lines(skill.get('desc', ''))
                if growth_lines:
                    growth_str = " ； ".join(growth_lines)
                    markdown_content += f"- **【技能数值等级成长线】**：{growth_str}\n"

                markdown_content += f"- **技能完整机制**：{skill.get('desc', '无')}\n"
                markdown_content += f"- **官方实战技巧**：{skill.get('tips', '无')}\n\n"

            markdown_content += "---\n\n"

    if not output_file:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, DOC_HERO_SKILLS_NAME)
    else:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"【成功】全英雄技能数值与等级成长库已生成：'{output_file}'")
    return output_file


if __name__ == "__main__":
    build_hero_skills()
