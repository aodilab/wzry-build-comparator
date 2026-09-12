# -*- coding: utf-8 -*-
"""
王者荣耀铭文数据库构建器
包含全套五级铭文数值、全英雄推荐铭文组及满配30颗总属性计算
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import URL_MING_LIST, URL_HERO_LIST, ROLE_MAP, COLOR_MAP, OUTPUT_DIR, DOC_ARCANA_NAME
from config.patches import DASIMING_ARCANA_PATCH
from src.core.http import fetch_json, fetch_html
from src.core.cleaner import clean_html, calculate_ten_times_stats
from src.core.hero_validator import get_validated_hero_list

def fetch_hero_mingwen_rec(hero, ming_dict):
    """
    抓取单个英雄的官方推荐铭文套组
    """
    ename = hero.get("ename")
    cname = hero.get("cname")
    title = hero.get("title")
    
    roles = []
    r1 = hero.get("hero_type")
    r2 = hero.get("hero_type2")
    if r1 in ROLE_MAP:
        roles.append(ROLE_MAP[r1])
    if r2 in ROLE_MAP and ROLE_MAP[r2] not in roles:
        roles.append(ROLE_MAP[r2])
    role_str = "/".join(roles)

    detail_url = f"https://pvp.qq.com/web201605/herodetail/{ename}.shtml"
    
    try:
        html_text = fetch_html(detail_url, encoding='gbk', retries=2)
        soup = BeautifulSoup(html_text, 'html.parser')
        
        sugg_u1 = soup.find('ul', class_='sugg-u1')
        ming_ids = []
        if sugg_u1 and sugg_u1.get('data-ming'):
            ming_ids = sugg_u1.get('data-ming').split('|')
        
        sugg_tips_el = soup.find(class_='sugg-tips')
        sugg_tips = sugg_tips_el.get_text(strip=True) if sugg_tips_el else "暂无官方实战搭配建议"
        
        recom_mings = []
        for mid in ming_ids:
            if mid in ming_dict:
                recom_mings.append(ming_dict[mid])
                
        if cname == "大司命" and not recom_mings:
            return DASIMING_ARCANA_PATCH

        return {
            "cname": cname,
            "title": title,
            "role": role_str if role_str else "战士/刺客",
            "recom_mings": recom_mings,
            "sugg_tips": sugg_tips,
            "success": True
        }
    except Exception as e:
        if cname == "大司命":
            return DASIMING_ARCANA_PATCH
        return {
            "cname": cname,
            "success": False,
            "error": str(e)
        }

def build_arcana(output_file=None, max_workers=10):
    """
    构建全量铭文数据库
    """
    print("1. 正在获取最新官方铭文数据库...")
    mings = fetch_json(URL_MING_LIST)

    ming_dict = {}
    for m in mings:
        mid = str(m.get("ming_id"))
        cleaned_des = clean_html(m.get("ming_des", ""))
        ming_info = {
            "id": mid,
            "name": m.get("ming_name", "未知"),
            "color": COLOR_MAP.get(m.get("ming_type"), "未知"),
            "grade": m.get("ming_grade", "1"),
            "single_stats": cleaned_des,
            "ten_stats": calculate_ten_times_stats(cleaned_des)
        }
        ming_dict[mid] = ming_info

    print("2. 正在通过校验引擎获取并纵向比对国服全英雄名单...")
    heroes = get_validated_hero_list()

    print(f"3. 正在并发抓取 {len(heroes)} 位英雄的推荐铭文及实战建议...")
    hero_ming_list = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_hero_mingwen_rec, hero, ming_dict): hero for hero in heroes}
        for future in as_completed(futures):
            result = future.result()
            if result.get("success"):
                hero_ming_list.append(result)
            else:
                print(f"抓取警告: {result['cname']}, 原因: {result.get('error')}")

    # 生成 Markdown
    markdown_content = "# 王者荣耀最新赛季全铭文属性及英雄推荐搭配数据库\n\n"
    markdown_content += "> 本数据库基于官方最新数据接口实时清洗生成，完美支持 NotebookLM 智能检索与关联分析。\n\n"
    
    # 第一部分：铭文图鉴
    markdown_content += "## 第一部分：官方最新五级（高级）铭文图鉴\n\n"
    by_color = {"红色": [], "蓝色": [], "绿色": []}
    for m_info in ming_dict.values():
        if m_info["grade"] == "5":
            c = m_info["color"]
            if c in by_color:
                by_color[c].append(m_info)
            
    for color, m_list in by_color.items():
        markdown_content += f"### {color}五级铭文\n\n"
        for m in m_list:
            markdown_content += f"#### 【{m['name']}】\n"
            markdown_content += f"- **单颗基础属性**：{m['single_stats']}\n"
            markdown_content += f"- **满配（10颗）总属性**：{m['ten_stats']}\n\n"
            
    # 第二部分：英雄搭配
    markdown_content += "## 第二部分：全英雄官方推荐铭文及搭配逻辑\n\n"
    by_role = {}
    for h in hero_ming_list:
        main_role = h["role"].split("/")[0] if h.get("role") else "其他"
        if main_role not in by_role:
            by_role[main_role] = []
        by_role[main_role].append(h)
        
    for role, h_list in by_role.items():
        markdown_content += f"### 定位分类：{role} 英雄铭文推荐\n\n"
        for h in h_list:
            markdown_content += f"#### 英雄：{h['cname']}（{h.get('title', '')}）\n"
            markdown_content += f"- **职业定位**：{h.get('role', '未知')}\n"
            markdown_content += "- **官方推荐铭文套组**：\n"
            
            total_stats_summary = []
            if h.get("recom_mings"):
                for m in h["recom_mings"]:
                    markdown_content += f"  - **{m['name']}** ({m['color']} {m['grade']}级) ｜ 单颗: {m['single_stats']} ｜ 10颗满配: {m['ten_stats']}\n"
                    total_stats_summary.append(m['ten_stats'])
            else:
                markdown_content += "  - 暂无官方推荐铭文\n"
                
            if total_stats_summary:
                markdown_content += f"- **整套铭文（30颗满配）总属性加成**：{' ｜ '.join(total_stats_summary)}\n"
            markdown_content += f"- **官方实战搭配建议**：{h.get('sugg_tips', '暂无')}\n\n"
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

    print(f"【成功】铭文数据库已生成：'{output_file}'")
    return output_file

if __name__ == "__main__":
    build_arcana()
