# -*- coding: utf-8 -*-
"""
王者荣耀全英雄技能数值与等级成长数据库构建器
专注微观操作与数值成长：基础属性、技能Lv1-Lv6数值阶梯、冷却消耗、加成公式
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import OUTPUT_DIR, DOC_HERO_SKILLS_NAME, ROLE_MAP
from config.patches import REWORKED_HERO_SKILLS_PATCHES
from config.hero_base_stats import get_hero_base_stats
from src.core.http import fetch_html
from src.core.cleaner import clean_plain_text
from src.core.stats_parser import format_cd_steps, format_cost_steps, extract_desc_growth_lines
from src.core.hero_validator import get_validated_hero_list

def fetch_single_hero_skills(hero):
    """
    抓取单个英雄的技能全量数值与机制
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

    detail_url = f"https://pvp.qq.com/web201605/herodetail/{ename}.shtml"
    
    try:
        html_text = fetch_html(detail_url, encoding='gbk', retries=2)
        soup = BeautifulSoup(html_text, 'html.parser')
        
        skill_show = soup.select('.skill-show .show-list')
        skills_list = []
        for idx, el in enumerate(skill_show):
            name_tag = el.find(class_='skill-name')
            if not name_tag:
                continue
            skill_name = name_tag.find('b').get_text(strip=True) if name_tag.find('b') else f"未知技能 {idx}"
            spans = name_tag.find_all('span')
            raw_cd = clean_plain_text(spans[0].get_text(strip=True)) if len(spans) > 0 else "无"
            raw_cost = clean_plain_text(spans[1].get_text(strip=True)) if len(spans) > 1 else "无"
            
            # 去除前缀
            raw_cd = raw_cd.replace("冷却值：", "").replace("冷却值:", "").strip()
            raw_cost = raw_cost.replace("消耗：", "").replace("消耗:", "").strip()
            
            desc_tag = el.find(class_='skill-desc')
            desc = clean_plain_text(desc_tag.get_text(strip=True)) if desc_tag else "无描述"
            
            tips_tag = el.find(class_='skill-tips')
            tips = clean_plain_text(tips_tag.get_text(strip=True)) if tips_tag else "无"
            
            skills_list.append({
                "name": skill_name,
                "cd": raw_cd,
                "cost": raw_cost,
                "desc": desc,
                "tips": tips
            })
            
        # 官方旧页面未同步重做机制英雄，优先注入权威受控补丁
        if cname in REWORKED_HERO_SKILLS_PATCHES:
            skills_list = REWORKED_HERO_SKILLS_PATCHES[cname]["skills"]

        base_stats = get_hero_base_stats(ename, cname, role_str)

        return {
            "ename": ename,
            "cname": cname,
            "title": title,
            "role": role_str,
            "base_stats": base_stats,
            "skills": skills_list,
            "success": True
        }
    except Exception as e:
        if cname in REWORKED_HERO_SKILLS_PATCHES:
            base_stats = get_hero_base_stats(ename, cname, role_str)
            return {
                "ename": ename,
                "cname": cname,
                "title": title,
                "role": role_str,
                "base_stats": base_stats,
                "skills": REWORKED_HERO_SKILLS_PATCHES[cname]["skills"],
                "success": True
            }
        return {"ename": ename, "cname": cname, "success": False, "error": str(e)}

def build_hero_skills(output_file=None, max_workers=10):
    """
    构建全英雄技能数值与等级成长数据库
    """
    heroes = get_validated_hero_list()
    print(f"开始并发提取 {len(heroes)} 位国服英雄全技能等级数值与微观基础属性...")

    hero_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_hero_skills, hero): hero for hero in heroes}
        for future in as_completed(futures):
            res = future.result()
            if res.get("success"):
                hero_results.append(res)
            else:
                print(f"抓取警告: {res['cname']}, 原因: {res.get('error')}")

    # 生成 Markdown 知识库
    markdown_content = "# 王者荣耀最新赛季全英雄技能数值与等级成长数据库\n\n"
    markdown_content += f"> 本知识库收录国服全量 {len(hero_results)} 位正统英雄的微观数值面板：包含1~15级基础属性、技能Lv1-Lv6等级数值阶梯、冷却消耗与加成公式。专为 NotebookLM 优化。\n\n"

    # 按职业归类展示
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

            # 1. 基础属性面板 (微观属性：物攻、物抗、魔抗、生命、移速、攻速)
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

            # 2. 技能数值与等级成长阶梯
            markdown_content += "### 【技能机制与各等级数值阶梯】\n"
            for s_idx, skill in enumerate(h.get("skills", [])):
                skill_type = "被动技能" if s_idx == 0 else f"主动技能 {s_idx}"
                markdown_content += f"#### {skill_type}：{skill.get('name', '未知技能')}\n"
                
                # 结构化冷却阶梯
                cd_formatted = format_cd_steps(skill.get('cd', ''))
                markdown_content += f"- **各等级冷却时间 (CD)**：{cd_formatted}\n"

                # 结构化消耗阶梯
                cost_formatted = format_cost_steps(skill.get('cost', ''))
                markdown_content += f"- **各等级法力/能量消耗**：{cost_formatted}\n"

                # 提取成长数值线
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
