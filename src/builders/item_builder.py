# -*- coding: utf-8 -*-
"""
王者荣耀装备全量数据库构建器（带双向合成拓扑）
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import URL_ITEM_LIST, OUTPUT_DIR, DOC_ITEMS_NAME
from config.item_recipes import ITEM_TYPE_MAP, COMPONENTS_MAP, get_upgrades_map
from src.core.http import fetch_json
from src.core.cleaner import clean_html

def build_items(output_file=None):
    """
    抓取官方装备接口，整合合成拓扑树，生成 Markdown 知识库
    """
    print("正在从王者荣耀官网获取最新装备数据...")
    items = fetch_json(URL_ITEM_LIST)
    upgrades_map = get_upgrades_map()
    
    markdown_content = "# 王者荣耀 S45 赛季（月照长安）全装备属性与双向合成拓扑图谱\n\n"
    markdown_content += "> 提示：本文件专为 NotebookLM / RAG 优化，已同步王者荣耀 S45 赛季“月照长安”最新装备调整数值（暴烈之甲+1000生命、破魔刀+700生命、制裁之刃重做普攻吸血与攻速、不死鸟之眼增强等），并计算出了完整的双向合成拓扑关系（合成配方与升级方向）。\n\n"

    # --- 注入局内装备栏与槽位机制核心法则 ---
    markdown_content += "## 一、 局内装备槽位机制与合成互斥核心法则\n\n"
    markdown_content += "### 1. 局内 6 格生效栏 VS 局外 12 槽位预设队列\n"
    markdown_content += "*   **局内背包装备栏（严格上限 6 件）**：任何英雄在战场中，背包装备栏永远只有 **6 个有效格子**，任何时刻最多只能同时享受 **6 件装备** 的属性与被动效果。\n"
    markdown_content += "*   **备战方案 12 槽位平滑购买队列**：王者荣耀局外预设系统支持最多 **12 个槽位**。这 12 个槽位并非让英雄同时携带 12 件装备，而是**“局内平滑出装引导序列”**（例如：先预设神速之靴、迅捷长矛、陨星，再合成暗影战斧）。系统会在对局中按此平滑顺序推荐小件，防止玩家盲目憋大件导致战斗力出现空档期。\n\n"

    markdown_content += "### 2. 小件原料吞噬与属性覆盖规则（数值严禁重复叠加）\n"
    markdown_content += "*   **合成瞬间小件消失**：当玩家购买小件并最终合成为大件成装时（例如：陨星 + 日冕 -> 暗影战斧），前置小件从背包中永久消耗移除，不再占用装备栏格子。\n"
    markdown_content += "*   **数值覆盖机制**：英雄最终仅享受合成后大件的成装属性，已被消耗的小件属性**完全失效并被大件覆盖，严禁将小件属性与大件属性重复叠加计算**。\n\n"

    markdown_content += "### 3. 全局唯一被动同名互斥黑名单（出装防坑准则）\n"
    markdown_content += "装备效果分为【基础属性】（可自由叠加）与【唯一被动】。**带有相同名称的唯一被动不可叠加，只生效优先级最高或先出的一件**：\n"
    markdown_content += "*   **【唯一被动 - 强击】互斥**：`宗师之力`、`冰痕之握`、`巫术法杖`、`光辉之剑` 共享强击被动。同时出时，仅生效优先级更高的一件伤害效果，绝不会双重触发，切忌同时出装！\n"
    markdown_content += "*   **【唯一被动 - 神速】互斥**：所有二级鞋子（`抵抗之靴`、`影忍之足`、`急速之靴` 等）均带有“唯一被动-神速：+60移动速度”。同时购买两双鞋子，移动速度**只生效一双（+60移速）**，移速绝不叠加！\n"
    markdown_content += "*   **【唯一被动 - 穿透/破甲】计算顺序**：`暗影战斧`（固定物理穿透）与 `破晓 / 碎星锤`（百分比物理穿透）。计算公式：先按百分比破甲折算防御，再扣除固定穿透值，二者虽不属于同名互斥，但后期面对高护甲前排时，百分比穿透（破晓/碎星锤）收益远大于暗影战斧。\n"
    markdown_content += "*   **【唯一被动 - 回响】互斥**：`回响之杖` 与 `凝冰之息` 等法术爆炸被动。\n\n"
    markdown_content += "---\n\n"
    markdown_content += "## 二、 局内全装备全维度图鉴与双向合成树\n\n"

    # 按装备大类进行分组
    grouped_items = {}
    for item in items:
        item_type = item.get("item_type", 0)
        if item_type not in grouped_items:
            grouped_items[item_type] = []
        grouped_items[item_type].append(item)

    for item_type, cat_name in ITEM_TYPE_MAP.items():
        if item_type not in grouped_items:
            continue
        markdown_content += f"### 【分类：{cat_name}】\n\n"
        
        for item in grouped_items[item_type]:
            name = item.get("item_name", "未知装备")
            price = item.get("price", "未知")
            total_price = item.get("total_price", "未知")

            stats = clean_html(item.get("des1", ""), sep=" ； ")
            passive = clean_html(item.get("des2", ""), sep=" ； ")
            
            # 获取合成路径
            recipe = COMPONENTS_MAP.get(name, [])
            recipe_str = " + ".join(recipe) if recipe else "无（本身是基础小件/特殊道具）"
            
            # 获取能够升级的方向
            upgrades = upgrades_map.get(name, [])
            upgrades_str = " 、 ".join(upgrades) if upgrades else "无（已是该路径的终极神装）"
            
            markdown_content += f"#### 装备名称：{name}\n"
            markdown_content += f"- **基础售价**：{price} 金币\n"
            markdown_content += f"- **合成总价**：{total_price} 金币\n"
            markdown_content += f"- **【合成配方】（需要以下原料）**：{recipe_str}\n"
            markdown_content += f"- **【升级方向】（可作为原料合成）**：{upgrades_str}\n"
            markdown_content += f"- **基础属性**：{stats}\n"
            markdown_content += f"- **装备效果（被动/主动）**：{passive}\n\n"

    if not output_file:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, DOC_ITEMS_NAME)
    else:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"【成功】装备数据库已生成：'{output_file}'")
    return output_file

if __name__ == "__main__":
    build_items()
