# -*- coding: utf-8 -*-
"""
王者荣耀英雄战术克制与阵容搭档拓扑构建器
专注 BP 禁选、选人克制与阵容协同：最佳搭档、压制英雄、被压制反制
100% 锁定本地权威数据集 (config/hero_relations_data.json & config/patches/)，绝不向外网爬取
专为 NotebookLM 与大模型 RAG 设计
"""
import os
import sys
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)
from config.settings import OUTPUT_DIR, DOC_HERO_RELATIONS_NAME, ROLE_MAP
from config.patches import HERO_RELATIONS_PATCHES
from src.core.hero_validator import get_validated_hero_list


def _load_local_relations_data():
    json_path = os.path.join(ROOT_DIR, "config", "hero_relations_data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def fetch_single_hero_relations(hero, local_relations_map):
    """从本地权威数据集中读取单个英雄的战术配合与克制关系，绝不向外网爬取"""
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

    relations = HERO_RELATIONS_PATCHES.get(cname) or local_relations_map.get(cname) or {
        "最佳搭档": [],
        "压制英雄": [],
        "被压制英雄": []
    }
    return {
        "ename": ename,
        "cname": cname,
        "title": title,
        "role": role_str,
        "relations": relations,
        "success": True
    }


def build_hero_relations(output_file=None, max_workers=10):
    """构建英雄战术克制与阵容搭档拓扑数据库 (100% 本地权威数据源)"""
    heroes = get_validated_hero_list()
    local_relations_map = _load_local_relations_data()
    print(f"开始从本地权威库加载 {len(heroes)} 位国服英雄克制与阵容搭档数据...")

    hero_results = [fetch_single_hero_relations(hero, local_relations_map) for hero in heroes]

    markdown_content = "# 王者荣耀 S45 赛季（月照长安）英雄战术克制与阵容搭档拓扑库\n\n"
    markdown_content += f"> 本知识库收录王者荣耀 S45 赛季“月照长安”国服全量 {len(hero_results)} 位英雄的克制与协同关系网络（包含第133位新英雄王维及重做英雄），专为 BP 选人决策、阵容搭配与反制分析设计。\n\n"

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
