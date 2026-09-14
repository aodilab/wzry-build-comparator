# -*- coding: utf-8 -*-
"""
王者荣耀五大分路定位与实战出装思路数据库构建器
按对抗路、打野、中路、发育路、游走五大分路组织出装方案
严格排除被吞噬的小件，精准计算最终 6 神装净增幅与 15 级终极面板
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import OUTPUT_DIR, DOC_HERO_BUILDS_NAME, URL_ITEM_LIST, ROLE_MAP, LANE_MAP
from config.patches import HERO_BUILDS_PATCHES
from config.hero_base_stats import get_hero_base_stats
from src.core.http import fetch_json, fetch_html
from src.core.cleaner import clean_plain_text
from src.core.hero_validator import get_validated_hero_list
from src.core.item_calculator import calculate_build_stats

def fetch_single_hero_builds(hero, equip_id_map, equip_name_map):
    """抓取单个英雄的官方推荐出装方案与思路，并计算 6 神装数值"""
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

    primary_role = roles[0] if roles else "战士"
    lane = LANE_MAP.get(primary_role, "对抗路")
    hero_base = get_hero_base_stats(ename, cname, role_str)

    detail_url = f"https://pvp.qq.com/web201605/herodetail/{ename}.shtml"
    
    try:
        html_text = fetch_html(detail_url, encoding='gbk', retries=2)
        soup = BeautifulSoup(html_text, 'html.parser')
        
        equip_recommendations = []
        equip_infos = soup.select('.equip-info')
        equip_tips = soup.select('.equip-tips')
        
        for idx, info in enumerate(equip_infos):
            ul_tag = info.select_one('.equip-list')
            if ul_tag and ul_tag.has_attr('data-item'):
                item_ids = [iid.strip() for iid in ul_tag['data-item'].split('|') if iid.strip()]
                item_names = [equip_id_map.get(iid, f"未知装备({iid})") for iid in item_ids]
                
                tip = "暂无推荐原因。"
                if idx < len(equip_tips):
                    tip = clean_plain_text(equip_tips[idx].get_text(strip=True))
                    tip = re.sub(r'^(提示：|Tips：|提示:|Tips:)\s*', '', tip)
                
                # 计算这套出装的 6 神装净属性
                calc_res = calculate_build_stats(item_names, equip_name_map, hero_base)

                build_title = f"官方推荐出装方案 {idx + 1}"
                equip_recommendations.append({
                    "title": build_title,
                    "items": item_names,
                    "tip": tip,
                    "calc": calc_res
                })
                        
        if not equip_recommendations and cname in HERO_BUILDS_PATCHES:
            # 补丁处理
            for idx, eq in enumerate(HERO_BUILDS_PATCHES[cname]):
                calc_res = calculate_build_stats(eq["items"], equip_name_map, hero_base)
                equip_recommendations.append({
                    "title": eq["title"],
                    "items": eq["items"],
                    "tip": eq["tip"],
                    "calc": calc_res
                })

        return {
            "ename": ename,
            "cname": cname,
            "title": title,
            "role": role_str,
            "lane": lane,
            "equips": equip_recommendations,
            "success": True
        }
    except Exception as e:
        if cname in HERO_BUILDS_PATCHES:
            equip_recs = []
            for eq in HERO_BUILDS_PATCHES[cname]:
                calc_res = calculate_build_stats(eq["items"], equip_name_map, hero_base)
                equip_recs.append({
                    "title": eq["title"],
                    "items": eq["items"],
                    "tip": eq["tip"],
                    "calc": calc_res
                })
            return {
                "ename": ename,
                "cname": cname,
                "title": title,
                "role": role_str,
                "lane": lane,
                "equips": equip_recs,
                "success": True
            }
        return {"ename": ename, "cname": cname, "success": False, "error": str(e)}


def build_hero_builds(output_file=None, max_workers=10):
    """构建五大分路定位与实战出装思路数据库"""
    print("正在获取装备完整数据建立属性映射表...")
    items = fetch_json(URL_ITEM_LIST)
    equip_id_map = {str(item["item_id"]): item["item_name"] for item in items}
    equip_name_map = {item["item_name"]: item for item in items}

    heroes = get_validated_hero_list()
    print(f"开始并发抓取 {len(heroes)} 位国服英雄分路出装、计算六神装净增幅与终极面板...")

    hero_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_hero_builds, hero, equip_id_map, equip_name_map): hero for hero in heroes}
        for future in as_completed(futures):
            res = future.result()
            if res.get("success"):
                hero_results.append(res)
            else:
                print(f"抓取警告: {res['cname']}, 原因: {res.get('error')}")

    # 生成 Markdown 知识库
    markdown_content = "# 王者荣耀最新赛季五大分路定位与实战出装思路库\n\n"
    markdown_content += f"> 本知识库收录国服全量 {len(hero_results)} 位英雄按【对抗路、打野、中路、发育路、游走】分路组织的官方出装。\n"
    markdown_content += "> 核心规则贯彻：严格排除已被合成消耗的原料小件，仅对最终 6 件成装进行净属性叠加，并预测 15 级终极实战面板。专为局内出装决策设计。\n\n"

    by_lane = {"对抗路": [], "打野": [], "中路": [], "发育路": [], "游走": [], "其他": []}
    for h in hero_results:
        lane = h.get("lane", "其他")
        target_lane = "对抗路" if "对抗路" in lane else (lane if lane in by_lane else "其他")
        by_lane[target_lane].append(h)

    for lane_name, h_list in by_lane.items():
        if not h_list:
            continue
        markdown_content += f"## 【峡谷分路：{lane_name}】\n\n"
        for h in h_list:
            markdown_content += f"### 英雄：{h['cname']}（{h.get('title', '')}）\n"
            markdown_content += f"- **常规推荐分路**：{lane_name}（定位：{h.get('role', '未知')}）\n\n"

            equips = h.get("equips", [])
            if equips:
                for eq in equips:
                    calc = eq.get("calc", {})
                    effective_six = calc.get("effective_six", eq['items'])
                    six_str = " + ".join(effective_six)
                    total_sum = calc.get("total_summary", "无")
                    total_gold = calc.get("total_gold", 0)
                    panel = calc.get("final_panel", {})

                    markdown_content += f"#### 🛡️ {eq['title']}\n"
                    build_path = " -> ".join(eq['items']) if eq.get('items') else "暂无装备"
                    markdown_content += f"- **推荐购买顺序路径**：{build_path}\n"
                    markdown_content += f"- **【最终生效 6 件成装 (严格排除已消耗小件)】**：{six_str}\n"
                    markdown_content += f"- **【六神装总金币造价】**：约 {total_gold} 金币\n"
                    markdown_content += f"- **【六神装满配净属性总增幅】**：{total_sum}\n"
                    
                    if panel:
                        markdown_content += "- **【终极成型实战面板预测 (15级英雄基础 + 6神装总属性)】**：\n"
                        markdown_content += f"  - 最终物理攻击力：{panel.get('final_atk', '无')}\n"
                        if "0 (基础) + 0" not in str(panel.get('final_ap', '')):
                            markdown_content += f"  - 最终法术攻击力：{panel.get('final_ap', '无')}\n"
                        markdown_content += f"  - 最终最大生命值：{panel.get('final_hp', '无')}\n"
                        markdown_content += f"  - 最终物理防御(物抗)：{panel.get('final_pdef', '无')}\n"
                        markdown_content += f"  - 最终法术防御(魔抗)：{panel.get('final_mdef', '无')}\n"
                        markdown_content += f"  - 最终移动速度：{panel.get('final_speed', '无')}\n"
                        markdown_content += f"  - 最终攻击速度：{panel.get('final_aspeed', '无')}\n"
                        markdown_content += f"  - 暴击与冷却：暴击率 {panel.get('final_crit', '0%')} ｜ 冷却缩减 {panel.get('final_cdr', '0%')}\n"
                        
                        conflicts = calc.get("conflicts", [])
                        if conflicts:
                            for c in conflicts:
                                markdown_content += f"  - ⚠️ 【唯一被动互斥警告】：{c}\n"
                        else:
                            markdown_content += "  - ✅ 【被动契合度诊断】：6件成装被动无冲突，属性利用率100%\n"
                    
                    markdown_content += f"- **出装思路（推荐原因）**：{eq.get('tip', '暂无')}\n\n"
            else:
                markdown_content += "- 暂无官方推荐出装数据\n\n"
            markdown_content += "---\n\n"

    if not output_file:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, DOC_HERO_BUILDS_NAME)
    else:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"【成功】五大分路定位与实战出装思路库已生成：'{output_file}'")
    return output_file

if __name__ == "__main__":
    build_hero_builds()
