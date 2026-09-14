# -*- coding: utf-8 -*-
"""
王者荣耀英雄战术克制与阵容搭档拓扑构建器
专注 BP 禁选、选人克制与阵容协同：最佳搭档、压制英雄、被压制反制
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import OUTPUT_DIR, DOC_HERO_RELATIONS_NAME, ROLE_MAP
from config.patches import HERO_RELATIONS_PATCHES
from src.core.http import fetch_html
from src.core.cleaner import clean_plain_text
from src.core.hero_validator import get_validated_hero_list


def format_desc(target_cname, raw_desc):
    """格式化关系描述，将英雄名字加粗"""
    if not raw_desc:
        return f"**{target_cname}**：暂无详细描述。"
    pattern_cn = rf"^{target_cname}：\s*"
    pattern_en = rf"^{target_cname}:\s*"
    if re.match(pattern_cn, raw_desc):
        return re.sub(pattern_cn, f"**{target_cname}**：", raw_desc)
    elif re.match(pattern_en, raw_desc):
        return re.sub(pattern_en, f"**{target_cname}**：", raw_desc)
    else:
        return f"**{target_cname}**：{raw_desc}"

def fetch_single_hero_relations(hero, hero_map):
    """抓取单个英雄的战术配合与克制关系"""
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
        
        relations = {
            "最佳搭档": [],
            "压制英雄": [],
            "被压制英雄": []
        }
        
        info_box = soup.select_one('.hero-info-box')
        if info_box:
            info_divs = info_box.select('.hero-info')
            relation_types = ["最佳搭档", "压制英雄", "被压制英雄"]
            
            for idx, div in enumerate(info_divs):
                if idx >= len(relation_types):
                    break
                rel_type = relation_types[idx]
                
                a_tags = div.select('a')
                p_tags = div.select('p')
                
                descs = []
                for p in p_tags:
                    p_text = clean_plain_text(p.get_text())
                    if p_text in ["最佳搭档", "压制英雄", "被压制英雄", "英雄关系"] or not p_text:
                        continue
                    descs.append(p_text)
                
                for i, a in enumerate(a_tags):
                    href = a.get('href', '')
                    match = re.search(r'(\d+)\.shtml', href)
                    if match:
                        target_ename = match.group(1)
                        target_cname = hero_map.get(target_ename, "未知英雄")
                        raw_desc = descs[i] if i < len(descs) else ""
                        formatted_rel = format_desc(target_cname, raw_desc)
                        relations[rel_type].append(formatted_rel)
                        
        if not relations["最佳搭档"] and cname in HERO_RELATIONS_PATCHES:
            relations = HERO_RELATIONS_PATCHES[cname]

        return {
            "ename": ename,
            "cname": cname,
            "title": title,
            "role": role_str,
            "relations": relations,
            "success": True
        }
    except Exception as e:
        if cname in HERO_RELATIONS_PATCHES:
            return {
                "ename": ename,
                "cname": cname,
                "title": title,
                "role": role_str,
                "relations": HERO_RELATIONS_PATCHES[cname],
                "success": True
            }
        return {"ename": ename, "cname": cname, "success": False, "error": str(e)}


def build_hero_relations(output_file=None, max_workers=10):
    """构建英雄战术克制与阵容搭档拓扑数据库"""
    heroes = get_validated_hero_list()
    hero_map = {str(h["ename"]): h["cname"] for h in heroes}
    print(f"开始并发抓取 {len(heroes)} 位国服英雄克制与阵容搭档数据...")

    hero_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_hero_relations, hero, hero_map): hero for hero in heroes}
        for future in as_completed(futures):
            res = future.result()
            if res.get("success"):
                hero_results.append(res)
            else:
                print(f"抓取警告: {res['cname']}, 原因: {res.get('error')}")

    # 生成 Markdown
    markdown_content = "# 王者荣耀最新赛季英雄战术克制与阵容搭档拓扑库\n\n"
    markdown_content += f"> 本知识库收录国服全量 {len(hero_results)} 位英雄的克制与协同关系网络，专为 BP 选人决策、阵容搭配与反制分析设计。\n\n"

    by_role = {}
    for h in hero_results:
        role = h["role"].split("/")[0]
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(h)

    for role, h_list in by_role.items():
        markdown_content += f"# ============= 【定位领域：{role}】 =============\n\n"
        for h in h_list:
            markdown_content += f"## 英雄：{h['cname']}（{h.get('title', '')}）\n"
            markdown_content += f"- **职业定位**：{h.get('role', '未知')}\n\n"

            rel = h.get("relations", {})
            markdown_content += "### 🤝 最佳搭档（阵容协同与体系联动）\n"
            if rel.get("最佳搭档"):
                for item in rel["最佳搭档"]:
                    markdown_content += f"- {item}\n"
            else:
                markdown_content += "- 暂无官方推荐搭档\n"
            markdown_content += "\n"

            markdown_content += "### ⚔️ 压制英雄（该英雄克制谁 / 优势对局）\n"
            if rel.get("压制英雄"):
                for item in rel["压制英雄"]:
                    markdown_content += f"- {item}\n"
            else:
                markdown_content += "- 暂无压制数据\n"
            markdown_content += "\n"

            markdown_content += "### 🛡️ 被压制英雄（谁克制该英雄 / 天敌与反制手段）\n"
            if rel.get("被压制英雄"):
                for item in rel["被压制英雄"]:
                    markdown_content += f"- {item}\n"
            else:
                markdown_content += "- 暂无被压制数据\n"
            markdown_content += "\n---\n\n"

    if not output_file:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, DOC_HERO_RELATIONS_NAME)
    else:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"【成功】英雄战术克制与阵容搭档拓扑库已生成：'{output_file}'")
    return output_file

if __name__ == "__main__":
    build_hero_relations()
