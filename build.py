# -*- coding: utf-8 -*-
"""王者荣耀开源战术知识库构建 CLI 入口 (01~06 卷)"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    OUTPUT_DIR,
    DOC_HERO_SKILLS_NAME,
    DOC_HERO_RELATIONS_NAME,
    DOC_HERO_BUILDS_NAME,
    DOC_ITEMS_NAME,
    DOC_ARCANA_NAME,
    DOC_RULES_NAME,
)
from src.builders.hero_skills_builder import build_hero_skills
from src.builders.hero_relations_builder import build_hero_relations
from src.builders.hero_builds_builder import build_hero_builds
from src.builders.item_builder import build_items
from src.builders.arcana_builder import build_arcana
from src.builders.rules_builder import build_rules


def main():
    parser = argparse.ArgumentParser(description="王者荣耀开源战术知识库构建工具 (01~06 卷)")
    parser.add_argument("--kb", action="store_true", help="重新构建全部 6 卷 Markdown 战术知识库")
    parser.add_argument("--skills", action="store_true", help="构建[01]全英雄技能数值与等级成长库")
    parser.add_argument("--relations", action="store_true", help="构建[02]英雄战术克制与阵容搭档拓扑")
    parser.add_argument("--builds", action="store_true", help="构建[03]五大分路定位与战术流派指南")
    parser.add_argument("--item", action="store_true", help="构建[04]全装备属性与合成升级图谱")
    parser.add_argument("--arcana", action="store_true", help="构建[05]全铭文图鉴")
    parser.add_argument("--rules", action="store_true", help="构建[06]峡谷战场机制与宏观运营规则")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="自定义 Markdown 输出目录")
    parser.add_argument("--workers", type=int, default=10, help="并发线程数 (默认 10)")

    args = parser.parse_args()
    has_action = args.kb or args.skills or args.relations or args.builds or args.item or args.arcana or args.rules
    if not has_action:
        parser.print_help()
        print("\n常用命令：")
        print("  python build.py --kb     # 构建 01~06 卷 Markdown 战术知识库")
        return

    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)
    print(f"=== 王者荣耀战术知识库构建启动 | 输出目录: {out_dir} ===\n")

    if args.kb or args.skills:
        print("[1/6] 构建【01 全英雄技能数值与等级成长库】...")
        build_hero_skills(os.path.join(out_dir, DOC_HERO_SKILLS_NAME), max_workers=args.workers)
        print()

    if args.kb or args.relations:
        print("[2/6] 构建【02 英雄战术克制与阵容搭档拓扑】...")
        build_hero_relations(os.path.join(out_dir, DOC_HERO_RELATIONS_NAME), max_workers=args.workers)
        print()

    if args.kb or args.builds:
        print("[3/6] 构建【03 五大分路定位与战术流派指南】...")
        build_hero_builds(os.path.join(out_dir, DOC_HERO_BUILDS_NAME), max_workers=args.workers)
        print()

    if args.kb or args.item:
        print("[4/6] 构建【04 全装备属性与合成升级图谱】...")
        build_items(os.path.join(out_dir, DOC_ITEMS_NAME))
        print()

    if args.kb or args.arcana:
        print("[5/6] 构建【05 全铭文图鉴】...")
        build_arcana(os.path.join(out_dir, DOC_ARCANA_NAME), max_workers=args.workers)
        print()

    if args.kb or args.rules:
        print("[6/6] 构建【06 峡谷战场机制与宏观运营规则】...")
        build_rules(os.path.join(out_dir, DOC_RULES_NAME))
        print()

    print("=== 指定知识库构建完成 ===")


if __name__ == "__main__":
    main()
