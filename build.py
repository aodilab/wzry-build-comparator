# -*- coding: utf-8 -*-
"""
王者荣耀全维度知识库统一构建 CLI 入口
基于 6 大战术对局维度矩阵构建，专供 Gemini NotebookLM
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    OUTPUT_DIR,
    DOC_HERO_SKILLS_NAME,
    DOC_HERO_RELATIONS_NAME,
    DOC_HERO_BUILDS_NAME,
    DOC_ITEMS_NAME,
    DOC_ARCANA_NAME,
    DOC_RULES_NAME
)
from src.builders.hero_skills_builder import build_hero_skills
from src.builders.hero_relations_builder import build_hero_relations
from src.builders.hero_builds_builder import build_hero_builds
from src.builders.item_builder import build_items
from src.builders.arcana_builder import build_arcana
from src.builders.rules_builder import build_rules
from src.builders.sandbox_builder import build_sandbox_html

def main():
    parser = argparse.ArgumentParser(description="王者荣耀 6 大战术对局知识库构建流水线 (Gemini NotebookLM 专属)")
    parser.add_argument("--all", action="store_true", help="一键全量构建所有 6 大对局知识库与配装沙盒网页")
    parser.add_argument("--skills", action="store_true", help="构建[01]全英雄技能数值与等级成长库")
    parser.add_argument("--relations", action="store_true", help="构建[02]英雄战术克制与阵容搭档拓扑")
    parser.add_argument("--builds", action="store_true", help="构建[03]五大分路定位与实战出装思路")
    parser.add_argument("--item", action="store_true", help="构建[04]全装备属性与合成升级图谱")
    parser.add_argument("--arcana", action="store_true", help="构建[05]全铭文图鉴与英雄搭配方案")
    parser.add_argument("--rules", action="store_true", help="构建[06]峡谷战场机制与宏观运营规则")
    parser.add_argument("--sandbox", action="store_true", help="生成独立可视化配装沙盒网页 (sandbox.html)")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="自定义生成 Markdown 的输出目录")
    parser.add_argument("--workers", type=int, default=10, help="并发网络请求线程数 (默认10)")

    args = parser.parse_args()

    # 如果没有任何构建参数，默认打印帮助并退出
    if not (args.all or args.skills or args.relations or args.builds or args.item or args.arcana or args.rules or args.sandbox):
        parser.print_help()
        print("\n常用快捷命令：")
        print("  python build.py --all            # 一键全量构建 6 大对局知识库与配装沙盒网页")
        print("  python build.py --sandbox        # 生成本地可视化配装沙盒网页 (sandbox.html)")
        print("  python build.py --skills         # 仅更新技能数值与等级成长")
        print("  python build.py --relations      # 仅更新战术克制与搭档")
        print("  python build.py --builds         # 仅更新分路出装思路")
        print("  python build.py --item           # 仅更新装备图谱")
        print("  python build.py --arcana         # 仅更新铭文搭配")
        print("  python build.py --rules          # 仅更新战场规则")
        return

    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)
    print(f"=== 王者荣耀 6 大战术对局知识库构建启动 | 目标路径: {out_dir} ===\n")

    # 1. 技能数值与等级成长库
    if args.all or args.skills:
        print("[1/6] 开始构建【01 全英雄技能数值与等级成长库】...")
        skills_path = os.path.join(out_dir, DOC_HERO_SKILLS_NAME)
        build_hero_skills(skills_path, max_workers=args.workers)
        print()

    # 2. 英雄战术克制与阵容搭档拓扑
    if args.all or args.relations:
        print("[2/6] 开始构建【02 英雄战术克制与阵容搭档拓扑】...")
        relations_path = os.path.join(out_dir, DOC_HERO_RELATIONS_NAME)
        build_hero_relations(relations_path, max_workers=args.workers)
        print()

    # 3. 五大分路定位与实战出装思路
    if args.all or args.builds:
        print("[3/6] 开始构建【03 五大分路定位与实战出装思路】...")
        builds_path = os.path.join(out_dir, DOC_HERO_BUILDS_NAME)
        build_hero_builds(builds_path, max_workers=args.workers)
        print()

    # 4. 全装备属性与合成升级图谱
    if args.all or args.item:
        print("[4/6] 开始构建【04 全装备属性与合成升级图谱】...")
        items_path = os.path.join(out_dir, DOC_ITEMS_NAME)
        build_items(items_path)
        print()

    # 5. 全铭文图鉴与英雄搭配方案
    if args.all or args.arcana:
        print("[5/6] 开始构建【05 全铭文图鉴与英雄搭配方案】...")
        arcana_path = os.path.join(out_dir, DOC_ARCANA_NAME)
        build_arcana(arcana_path, max_workers=args.workers)
        print()

    # 6. 峡谷战场机制与宏观运营规则
    if args.all or args.rules:
        print("[6/6] 开始构建【06 峡谷战场机制与宏观运营规则】...")
        rules_path = os.path.join(out_dir, DOC_RULES_NAME)
        build_rules(rules_path)
        print()

    # 7. 可视化配装沙盒网页
    if args.all or args.sandbox:
        print("[沙盒网页] 开始生成王者荣耀六神装配装沙盒 (sandbox.html)...")
        build_sandbox_html()
        print()

    print("=== 全部指定构建任务顺利完成！6 大知识库已就绪，可直接拖入 NotebookLM ===")

if __name__ == "__main__":
    main()
