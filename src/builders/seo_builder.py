# -*- coding: utf-8 -*-
"""
王者荣耀全维度知识库与沙盒 SEO 自动化资产生成器
负责生成标准符合百度、谷歌、必应等国际搜索引擎规范的：
1. robots.txt 与 sitemap.xml 资产
2. JSON-LD Schema.org 结构化数据 (WebApplication + WebSite)
3. 白帽 133 位英雄官方出装与铭文预渲染语义大典 (SSR Semantic Directory)
遵循 AGENTS.md 业务单一职责规范 (≤ 350行)
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.hero_validator import get_validated_hero_list

SITE_DOMAIN = "https://wzry.aodilab.com"

def get_json_ld_schema_markup() -> str:
    """生成符合 Schema.org 标准的 JSON-LD 结构化数据 (WebApplication + WebSite)"""
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "@id": f"{SITE_DOMAIN}/#webapp",
                "name": "王者出装箱",
                "alternateName": "Honor of Kings Item Box",
                "url": f"{SITE_DOMAIN}/",
                "applicationCategory": "GameApplication",
                "operatingSystem": "All",
                "inLanguage": "zh-CN",
                "description": "专业级王者荣耀六神装配装推演沙盒与五级铭文模拟器。收录S38/S45赛季国服133位全英雄官方出装、五级铭文自由搭配、攻防属性协同算分、技能连招与实战克制大典。",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "CNY"
                },
                "featureList": [
                    "局内六神装配装推演",
                    "30颗全量五级铭文自由混搭",
                    "攻防属性实时演算",
                    "官方推荐出装与实战分路导航",
                    "战术克制与协同算分"
                ],
                "author": {
                    "@type": "Organization",
                    "name": "王者出装箱研发组",
                    "url": f"{SITE_DOMAIN}/"
                }
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE_DOMAIN}/#website",
                "url": f"{SITE_DOMAIN}/",
                "name": "王者出装箱",
                "publisher": {
                    "@id": f"{SITE_DOMAIN}/#webapp"
                }
            }
        ]
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'

def build_semantic_directory_html(processed_heroes, official_builds) -> str:
    """
    生成符合 Apple 官网极简美学的页脚速查大典 (Footer Sitemap)
    默认完全折叠为极简底栏（不打扰用户正常推演），点击可平滑展开 5 列分路速查
    爬虫爬取时通过 DOM 树 100% 抓取全量 133 英雄出装与铭文
    """
    LANE_ORDER = ["对抗路", "中路", "发育路", "打野", "游走"]
    lane_heroes = {l: [] for l in LANE_ORDER}
    fallback_lane = "对抗路"

    for h in processed_heroes:
        primary_lane = h.get("lane") or (h.get("supported_lanes") or [fallback_lane])[0]
        if primary_lane not in lane_heroes:
            matched = next((l for l in LANE_ORDER if l.startswith(primary_lane[:2])), fallback_lane)
            lane_heroes[matched].append(h)
        else:
            lane_heroes[primary_lane].append(h)

    lines = [
        '<footer class="apple-site-footer" id="siteFooter">',
        '  <div class="apple-footer-inner">',
        '    <noscript>',
        '      <style>.apple-footer-directory-content { display: block !important; }</style>',
        '      <div class="seo-noscript-banner">',
        '        <strong>文本速查大典：</strong>已为您直接呈现王者荣耀 133 位英雄官方推荐出装与铭文数据。',
        '      </div>',
        '    </noscript>',
        '    <div class="apple-footer-top-bar">',
        '      <div class="apple-footer-brand">',
        '        <span class="apple-footer-title">王者出装箱</span>',
        '        <span class="apple-footer-desc">· S38/S45 赛季局内六神装配装推演沙盒</span>',
        '      </div>',
        '      <button class="apple-footer-directory-btn" id="seoToggleBtn" onclick="toggleSeoDirectory()" type="button" aria-expanded="false">',
        '        <span id="seoToggleText">S45 全英雄出装与铭文速查索引 (133位)</span>',
        '        <span class="apple-toggle-arrow" id="seoToggleIcon">›</span>',
        '      </button>',
        '    </div>',
        '    <div class="apple-footer-directory-content" id="seoDirectoryContent">',
        '      <div class="apple-footer-lanes-grid">'
    ]

    for lane in LANE_ORDER:
        heroes = lane_heroes.get(lane, [])
        if not heroes:
            continue
        lines.append('        <div class="apple-footer-lane-col">')
        lines.append(f'          <div class="apple-footer-lane-title">{lane} ({len(heroes)})</div>')
        lines.append('          <ul class="apple-footer-hero-list">')
        for h in heroes:
            cname = h.get("cname", "")
            ename = h.get("ename", "")
            role = h.get("role", "")

            b_info = official_builds.get(cname, {})
            build_lane_data = b_info.get("lanes", {})
            first_lane_key = lane if lane in build_lane_data else (list(build_lane_data.keys())[0] if build_lane_data else "")
            first_build = build_lane_data.get(first_lane_key, [{}])[0] if first_lane_key else {}

            items_list = first_build.get("item_names") or first_build.get("items") or ["抵抗之靴", "暗影战斧", "无尽战刃"]
            items_str = " · ".join(items_list)
            arcana_desc = first_build.get("arcana_desc", "")
            if not arcana_desc:
                rec_a = h.get("recommended_arcana", {})
                arcana_desc = f"10{rec_a.get('red', '异变')} 10{rec_a.get('green', '鹰眼')} 10{rec_a.get('blue', '隐匿')}"

            lines.append('            <li class="apple-footer-hero-item">')
            lines.append(f'              <a class="apple-footer-hero-link" href="?hero={ename}" onclick="if(window.selectHeroById){{selectHeroById(\'{ename}\');return false;}}" title="{cname} ({role}) 出装与铭文">{cname}</a>')
            lines.append(f'              <div class="apple-footer-hero-brief" title="出装：{items_str} ｜ 铭文：{arcana_desc}">{items_str}</div>')
            lines.append('            </li>')
        lines.append('          </ul>')
        lines.append('        </div>')

    lines.append('      </div>')
    lines.append('    </div>')
    lines.append('    <div class="apple-footer-legal">')
    lines.append('      <div class="apple-footer-copy">Copyright © 2026 王者出装箱 (wzry.aodilab.com). 保留所有权利。</div>')
    lines.append('      <div class="apple-footer-links">')
    lines.append('        <a href="/download">提货中心</a>')
    lines.append('        <span>·</span>')
    lines.append('        <a href="https://github.com/aodilab/wzry-build-comparator" target="_blank" rel="noopener noreferrer">GitHub 开源仓库</a>')
    lines.append('        <span>·</span>')
    lines.append('        <a href="https://pvp.qq.com/" target="_blank" rel="noopener noreferrer">王者荣耀官网公开数据</a>')
    lines.append('      </div>')
    lines.append('    </div>')
    lines.append('  </div>')
    lines.append('</footer>')
    return "\n".join(lines)

def generate_robots_txt(output_dirs=None):
    """生成标准化 robots.txt，全面放行主流搜索引擎蜘蛛并指明 sitemap"""
    content = f"""# ==============================================================================
# Honor of Kings Knowledge Base & Tactical Sandbox (wzry.aodilab.com)
# Robots Exclusion Protocol
# ==============================================================================

User-agent: *
Allow: /
Allow: /assets/
Allow: /download

# Sitemaps
Sitemap: {SITE_DOMAIN}/sitemap.xml
"""
    if output_dirs is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dirs = [
            os.path.join(root_dir, "dist_pages"),
            root_dir
        ]

    for d in output_dirs:
        if os.path.exists(d):
            file_path = os.path.join(d, "robots.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[SEO] robots.txt 已生成并写入: {file_path}")

def generate_sitemap_xml(output_dirs=None):
    """
    生成符合 Sitemaps.org 标准的 sitemap.xml
    收录全站顶级枢纽页面与 130+ 英雄专属推演深层链接
    """
    now_date = datetime.now().strftime("%Y-%m-%d")
    heroes = get_validated_hero_list()

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{SITE_DOMAIN}/</loc>',
        f'    <lastmod>{now_date}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{SITE_DOMAIN}/download</loc>',
        f'    <lastmod>{now_date}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.8</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{SITE_DOMAIN}/compare</loc>',
        f'    <lastmod>{now_date}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.8</priority>',
        '  </url>',
    ]

    # 收录 8 卷官方 RAG / NotebookLM 纯净 Markdown 核心知识库
    md_files = [
        "01_王者荣耀_全英雄技能数值与等级成长库.md",
        "02_王者荣耀_英雄战术克制与搭档谱系.md",
        "03_王者荣耀_五大分路定位与实战出装思路.md",
        "04_王者荣耀_全装备属性与合成升级图谱.md",
        "05_王者荣耀_全铭文图鉴与英雄搭配方案.md",
        "06_王者荣耀_峡谷战场机制与宏观运营规则.md",
        "07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.md",
        "08_王者荣耀_全英雄实战连招口诀大全.md",
    ]
    for mdf in md_files:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{SITE_DOMAIN}/md/{mdf}</loc>')
        xml_lines.append(f'    <lastmod>{now_date}</lastmod>')
        xml_lines.append('    <changefreq>daily</changefreq>')
        xml_lines.append('    <priority>0.85</priority>')
        xml_lines.append('  </url>')


    for h in heroes:
        cname = h.get("cname", "")
        ename = h.get("ename", "")
        if not cname:
            continue
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{SITE_DOMAIN}/?hero={ename}</loc>')
        xml_lines.append(f'    <lastmod>{now_date}</lastmod>')
        xml_lines.append('    <changefreq>weekly</changefreq>')
        xml_lines.append('    <priority>0.7</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')
    xml_content = "\n".join(xml_lines)

    if output_dirs is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dirs = [
            os.path.join(root_dir, "dist_pages"),
            root_dir
        ]

    for d in output_dirs:
        if os.path.exists(d):
            file_path = os.path.join(d, "sitemap.xml")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            print(f"[SEO] sitemap.xml 已成功生成: {file_path} (收录 {len(heroes) + 2} 个页面链接)")

def build_all_seo_assets():
    """一键构建全套 SEO 规范资产"""
    generate_robots_txt()
    generate_sitemap_xml()

if __name__ == "__main__":
    build_all_seo_assets()
