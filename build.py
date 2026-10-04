# -*- coding: utf-8 -*-
"""
王者荣耀全维度知识库统一构建 CLI 入口
基于 8 大战术对局维度矩阵构建，专供 Gemini NotebookLM 与全球 CDN 交付
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
    DOC_RULES_NAME,
    DOC_S45_BUILDS_NAME,
    DOC_COMBOS_NAME
)
from src.builders.hero_skills_builder import build_hero_skills
from src.builders.hero_relations_builder import build_hero_relations
from src.builders.hero_builds_builder import build_hero_builds
from src.builders.item_builder import build_items
from src.builders.arcana_builder import build_arcana
from src.builders.rules_builder import build_rules
from src.builders.sandbox_builder import build_sandbox_html
from src.builders.seo_builder import build_all_seo_assets

# 私有化商业高阶流水线（受控加载，公开开源环境优雅 fallback）
try:
    from src.builders.kb_builder import (
        build_07_s45_builds_markdown,
        build_08_combos_markdown,
        rebuild_official_builds_data,
        sync_markdown_to_dist
    )
    HAS_KB_BUILDER = True
except ImportError:
    HAS_KB_BUILDER = False
    build_07_s45_builds_markdown = None
    build_08_combos_markdown = None
    rebuild_official_builds_data = None
    sync_markdown_to_dist = None

try:
    from src.builders.pdf_builder import build_all_rich_pdfs
    from src.builders.build_07_pdf import render_07_pdf
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    build_all_rich_pdfs = None
    render_07_pdf = None

try:
    from src.builders.xiaohongshu_apple_builder import build_all_xiaohongshu_slides
    HAS_XIAOHONGSHU = True
except ImportError:
    HAS_XIAOHONGSHU = False
    build_all_xiaohongshu_slides = None

try:
    from src.builders.details_builder import render_all as build_details_slices
    HAS_DETAILS = True
except ImportError:
    HAS_DETAILS = False
    build_details_slices = None

def main():
    parser = argparse.ArgumentParser(description="王者荣耀战术对局知识库构建流水线 (Gemini NotebookLM 专属)")
    parser.add_argument("--all", action="store_true", help="一键全量构建战术知识库与配装推演沙盒")
    parser.add_argument("--kb", action="store_true", help="重新编译纯净 Markdown 战术知识库并自动同步至交付端")
    parser.add_argument("--skills", action="store_true", help="构建[01]全英雄技能数值与等级成长库")
    parser.add_argument("--relations", action="store_true", help="构建[02]英雄战术克制与阵容搭档拓扑")
    parser.add_argument("--builds", action="store_true", help="构建[03]五大分路定位与实战出装思路")
    parser.add_argument("--item", action="store_true", help="构建[04]全装备属性与合成升级图谱")
    parser.add_argument("--arcana", action="store_true", help="构建[05]全铭文图鉴与英雄搭配方案")
    parser.add_argument("--rules", action="store_true", help="构建[06]峡谷战场机制与宏观运营规则")
    parser.add_argument("--s45-builds", action="store_true", help="构建[07]S45赛季官方推荐全英雄全分路出装与铭文大全")
    parser.add_argument("--combos", action="store_true", help="构建[08]全英雄实战连招口诀大全")
    parser.add_argument("--sync-builds", action="store_true", help="从 JSON 重新编译官方出装数据至 SSOT 并同步推演室")
    parser.add_argument("--sandbox", action="store_true", help="生成独立可视化配装沙盒网页 (sandbox.html)")
    parser.add_argument("--pdf", action="store_true", help="生成出版级全彩矢量 PDF 手册")
    parser.add_argument("--xiaohongshu", action="store_true", help="生成小红书 3:4 Apple 风格营销图文")
    parser.add_argument("--details", action="store_true", help="生成电商 800x1000 详情页切片及无缝总览")
    parser.add_argument("--seo", action="store_true", help="生成搜索引擎标准 robots.txt 与 sitemap.xml 索引资产")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="自定义生成 Markdown 的输出目录")
    parser.add_argument("--workers", type=int, default=10, help="并发网络请求线程数 (默认10)")

    args = parser.parse_args()

    # 如果没有任何构建参数，默认打印帮助并退出
    has_action = (
        args.all or args.kb or args.skills or args.relations or args.builds or 
        args.item or args.arcana or args.rules or args.s45_builds or args.combos or 
        args.sync_builds or args.sandbox or args.pdf or args.xiaohongshu or 
        args.details or args.seo
    )
    if not has_action:
        parser.print_help()
        print("\n常用快捷命令：")
        print("  python build.py --kb             # 重新编译生成全部 Markdown 战术知识库并同步交付")
        print("  python build.py --all            # 一键全量构建知识库与配装沙盒网页")
        print("  python build.py --sandbox        # 生成本地可视化配装沙盒网页 (sandbox.html) 与全站 SEO 资产")
        print("  python build.py --sync-builds    # 重新编译官方出装数据至 SSOT 并同步推演室")
        print("  python build.py --seo            # 仅生成与更新 robots.txt 与 sitemap.xml")
        return

    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)
    print(f"=== 王者荣耀战术对局知识库构建启动 | 目标路径: {out_dir} ===\n")

    # 0. 官方推荐出装数据对齐 (私有化流水线)
    if args.all or args.sync_builds:
        if HAS_KB_BUILDER and rebuild_official_builds_data:
            print("[出装数据] 开始对齐官方出装数据至单一数据源 SSOT...")
            rebuild_official_builds_data()
            print()
        elif args.sync_builds:
            print("[提示] 当前开源环境未包含私有出装编译流水线，已跳过。")
            print()

    # 1. 技能数值与等级成长库
    if args.all or args.kb or args.skills:
        print("[1/8] 开始构建【01 全英雄技能数值与等级成长库】...")
        skills_path = os.path.join(out_dir, DOC_HERO_SKILLS_NAME)
        build_hero_skills(skills_path, max_workers=args.workers)
        print()

    # 2. 英雄战术克制与阵容搭档拓扑
    if args.all or args.kb or args.relations:
        print("[2/8] 开始构建【02 英雄战术克制与阵容搭档拓扑】...")
        relations_path = os.path.join(out_dir, DOC_HERO_RELATIONS_NAME)
        build_hero_relations(relations_path, max_workers=args.workers)
        print()

    # 3. 五大分路定位与实战出装思路
    if args.all or args.kb or args.builds:
        print("[3/8] 开始构建【03 五大分路定位与实战出装思路】...")
        builds_path = os.path.join(out_dir, DOC_HERO_BUILDS_NAME)
        build_hero_builds(builds_path, max_workers=args.workers)
        print()

    # 4. 全装备属性与合成升级图谱
    if args.all or args.kb or args.item:
        print("[4/8] 开始构建【04 全装备属性与合成升级图谱】...")
        items_path = os.path.join(out_dir, DOC_ITEMS_NAME)
        build_items(items_path)
        print()

    # 5. 全铭文图鉴与英雄搭配方案
    if args.all or args.kb or args.arcana:
        print("[5/8] 开始构建【05 全铭文图鉴与英雄搭配方案】...")
        arcana_path = os.path.join(out_dir, DOC_ARCANA_NAME)
        build_arcana(arcana_path, max_workers=args.workers)
        print()

    # 6. 峡谷战场机制与宏观运营规则
    if args.all or args.kb or args.rules:
        print("[6/8] 开始构建【06 峡谷战场机制与宏观运营规则】...")
        rules_path = os.path.join(out_dir, DOC_RULES_NAME)
        build_rules(rules_path)
        print()

    # 7. S45 官方推荐全英雄全分路出装与铭文大全 (私有化流水线)
    if args.all or args.kb or args.s45_builds:
        if HAS_KB_BUILDER and build_07_s45_builds_markdown:
            print("[7/8] 开始构建【07 S45 官方推荐全英雄全分路出装与铭文大全】...")
            s45_path = os.path.join(out_dir, DOC_S45_BUILDS_NAME)
            build_07_s45_builds_markdown(s45_path)
            print()
        elif args.s45_builds:
            print("[提示] 当前开源环境未包含私有出装构建器，已跳过。")
            print()

    # 8. 全英雄实战连招口诀大全 (私有化流水线)
    if args.all or args.kb or args.combos:
        if HAS_KB_BUILDER and build_08_combos_markdown:
            print("[8/8] 开始构建【08 全英雄实战连招口诀大全】...")
            combos_path = os.path.join(out_dir, DOC_COMBOS_NAME)
            build_08_combos_markdown(combos_path)
            print()
        elif args.combos:
            print("[提示] 当前开源环境未包含私有连招构建器，已跳过。")
            print()

    # 如果更新了任何 Markdown 知识库，自动同步至 dist_pages/md/
    if HAS_KB_BUILDER and sync_markdown_to_dist:
        if args.all or args.kb or args.skills or args.relations or args.builds or args.item or args.arcana or args.rules or args.s45_builds or args.combos:
            sync_markdown_to_dist(out_dir)
            print()

    # 可视化配装沙盒网页
    if args.all or args.sandbox:
        print("[沙盒网页] 开始生成王者荣耀六神装配装沙盒 (sandbox.html)...")
        build_sandbox_html()
        print()

    # 高清图文出版级矢量 PDF 手册 (私有化流水线)
    if args.all or args.pdf:
        if HAS_PDF and build_all_rich_pdfs and render_07_pdf:
            print("[出版物PDF] 开始生成王者荣耀全彩出版级矢量 PDF 手册...")
            build_all_rich_pdfs()
            render_07_pdf()
            print()
        elif args.pdf:
            print("[提示] 当前开源环境未包含私有化 PDF 渲染流水线，已跳过。")
            print()

    # 小红书 3:4 Apple 风格营销图文 (私有化流水线)
    if args.xiaohongshu:
        if HAS_XIAOHONGSHU and build_all_xiaohongshu_slides:
            print("[小红书图文] 开始生成小红书 3:4 Apple 风格营销长图...")
            build_all_xiaohongshu_slides()
            print()

    # 电商 800x1000 详情页切片 (私有化流水线)
    if args.details:
        if HAS_DETAILS and build_details_slices:
            print("[电商详情页] 开始生成电商 800x1000 详情页切片及无缝总览...")
            build_details_slices()
            print()

    # 搜索引擎规范资产 (robots.txt 与 sitemap.xml)
    if args.seo:
        print("[SEO 资产] 开始自动化生成搜索引擎标准 robots.txt 与 sitemap.xml...")
        build_all_seo_assets()
        print()

    print("=== 全部指定构建任务顺利完成！知识库、沙盒与物料已就绪 ===")

if __name__ == "__main__":
    main()
