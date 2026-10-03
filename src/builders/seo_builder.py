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
    生成专供搜索引擎爬虫（百度、谷歌、必应）全文索引的白帽预渲染 HTML 语义大典
    包含国服 133 位全英雄六神装出装、分路定位与铭文搭配
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
        '<section class="seo-directory-section" id="seoDirectorySection" aria-label="王者荣耀全英雄出装与铭文速查大典">',
        '  <div class="seo-directory-container">',
        '    <noscript>',
        '      <div class="seo-noscript-banner">',
        '        <strong>提示：</strong>当前浏览器未启用 JavaScript。以下为您呈现王者荣耀 S38/S45 赛季 133 位英雄官方推荐出装与铭文完整文本大典。如需进行动态装配属性实时推演与铭文自由混搭，请在浏览器中启用 JavaScript。',
        '      </div>',
        '    </noscript>',
        '    <header class="seo-directory-header">',
        '      <div class="seo-directory-title-wrap">',
        '        <h2 class="seo-directory-title">王者荣耀全英雄出装与铭文速查大典 (S45/S38赛季)</h2>',
        '        <p class="seo-directory-sub">国服 133 位英雄官方六神装推荐、实战分路配置与五级铭文搭配方案 · 点击任意英雄进入沙盒深度推演</p>',
        '      </div>',
        '      <button class="seo-directory-toggle-btn" id="seoToggleBtn" onclick="toggleSeoDirectory()" type="button" aria-expanded="true">',
        '        <span id="seoToggleText">收起大典</span>',
        '        <svg id="seoToggleIcon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 15l-6-6-6 6"/></svg>',
        '      </button>',
        '    </header>',
        '    <div class="seo-directory-content" id="seoDirectoryContent">'
    ]

    for lane in LANE_ORDER:
        heroes = lane_heroes.get(lane, [])
        if not heroes:
            continue
        lines.append('      <div class="seo-lane-block">')
        lines.append(f'        <h3 class="seo-lane-title"><span class="seo-lane-badge">{lane}</span> {lane}核心英雄官方六神装与铭文速查 ({len(heroes)}位)</h3>')
        lines.append('        <div class="seo-hero-grid">')
        for h in heroes:
            cname = h.get("cname", "")
            ename = h.get("ename", "")
            title = h.get("title", "")
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

            lines.append(f'          <article class="seo-hero-card" id="seo-hero-{ename}">')
            lines.append('            <div class="seo-card-head">')
            lines.append(f'              <a class="seo-hero-link" href="?hero={ename}" onclick="if(window.selectHeroById){{selectHeroById(\'{ename}\');return false;}}" title="{cname}六神装推荐与铭文推演">{cname}</a>')
            if title:
                lines.append(f'              <span class="seo-hero-title-tag">{title}</span>')
            lines.append(f'              <span class="seo-hero-role-tag">{role}</span>')
            lines.append('            </div>')
            lines.append('            <div class="seo-card-body">')
            lines.append(f'              <div class="seo-info-line"><strong>推荐出装：</strong><span class="seo-items-str">{items_str}</span></div>')
            lines.append(f'              <div class="seo-info-line"><strong>推荐铭文：</strong><span class="seo-arcana-str">{arcana_desc}</span></div>')
            lines.append('            </div>')
            lines.append('          </article>')
        lines.append('        </div>')
        lines.append('      </div>')

    lines.append('    </div>')
    lines.append('  </div>')
    lines.append('</section>')
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
    ]

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
