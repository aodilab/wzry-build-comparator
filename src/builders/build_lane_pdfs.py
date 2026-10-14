# -*- coding: utf-8 -*-
"""
S45 五路专属 PDF 构建器 (08~12)
单一职责：组装五路推演数据、读取模板样式并调用 Playwright 渲染矢量 PDF。
"""
import os
import json
from playwright.sync_api import sync_playwright
from config.hero_base_stats import get_hero_base_stats
from config.lane_pdf_config import LANE_CONFIG
from src.core.build_analyzer import analyze_build
from src.builders.lane_pdf_helpers import (
    PROJECT_ROOT, HERO_MAP, HERO_TITLES, ITEMS_LIST,
    resolve_item_id, get_hero_avatar, get_item_icon, get_arcana_icon, get_arcana_color,
    render_lane_scheme_page,
)

def generate_lane_html(lane_id: str, lane_info: dict, builds_data: dict) -> str:
    lane_key = lane_info["lane_key"]
    doc_title = lane_info["title"]
    lane_icon = lane_info["icon"]
    heroes = lane_info["heroes"]

    pages_html = []
    page_num = 1

    # 封面页
    cover_html = f"""
    <div class="pdf-page cover-page">
        <div class="watermark-pattern"></div>
        <div class="brand-bar">
            <span class="brand-name">TING LAB · 王者战策实验室</span>
            <span class="auth-pill">2026 S45 官方正式服认证</span>
        </div>
        <div class="cover-hero">
            <div class="cover-season-pill">2026 S45 赛季 · 月照长安</div>
            <h1 class="cover-title">{lane_icon} {doc_title}</h1>
            <p class="cover-sub">主流热门英雄 · 官方实战出装 · 网站级多维物理数据全解</p>
            <div class="cover-tags">
                <span class="tag-pill">精选 {len(heroes)} 位主流核心英雄</span>
                <span class="tag-pill">1 方案 1 整页深度剖析</span>
                <span class="tag-pill">满级物理抗性与伤害测算</span>
                <span class="tag-pill">附赠在线推演沙盒</span>
            </div>
        </div>
        <div class="cover-box">
            <div class="box-badge">官方数据驱动 · 局内实战推演矩阵</div>
            <div class="box-title">王者出装箱 ｜ 在线推演实验室</div>
            <div class="box-desc">全英雄机制深度协同，测算每一套神装最优解：<strong>https://wzry.aodilab.com</strong></div>
        </div>
        <div class="page-footer">
            <span>第 {page_num} 页 ｜ 淘宝店铺：TING LAB · 在线沙盒：wzry.aodilab.com</span>
        </div>
    </div>
    """
    pages_html.append(cover_html)
    page_num += 1

    # 英雄各方案页（1 方案 1 满页）
    for hero_cname in heroes:
        if hero_cname not in builds_data:
            continue
        hero_lane_builds = builds_data[hero_cname].get(lane_key, [])
        if not hero_lane_builds:
            continue

        avatar_url = get_hero_avatar(hero_cname)
        hero_title = HERO_TITLES.get(hero_cname, "热门英雄")

        for idx, build in enumerate(hero_lane_builds):
            b_name = build.get("name", f"方案 {idx + 1}")
            b_desc = build.get("desc", "官方实战神装推荐")
            items = build.get("items", [])
            arcana_list = build.get("arcana", [])

            # 多维数据计算
            stats = analyze_build(hero_cname, lane_key, items, arcana_list)

            # 装备卡片生成
            items_html = []
            for it_name in items:
                icon_url = get_item_icon(it_name)
                img_tag = f'<img src="{icon_url}" class="eq-icon" alt="{it_name}">' if icon_url else '<div class="eq-icon-placeholder"></div>'
                items_html.append(f"""
                <div class="eq-item-card">
                    {img_tag}
                    <div class="eq-name">{it_name}</div>
                </div>
                """)
            items_row = '<div class="eq-arrow">➔</div>'.join(items_html)

            # 铭文生成
            arc_html = []
            for item in arcana_list:
                if isinstance(item, list) and len(item) == 2:
                    cnt, aname = item
                    color_cls = get_arcana_color(aname)
                    arc_html.append(f'<span class="arc-pill {color_cls}">{cnt}{aname}</span>')
            arc_row = "".join(arc_html)

            # 多维数据面板（根据分路差异化）
            if lane_key in ["发育", "中路", "对抗"]:
                atk_label = "法术攻击 (AP)" if stats["is_magic"] else "物理攻击 (AD)"
                atk_val = stats["ap"] if stats["is_magic"] else stats["atk"]
                pen_label = "法术穿透" if stats["is_magic"] else "物理穿透"
                pen_val = f"固定 {stats['m_pierce_flat']} + {stats['m_pierce_pct']}%" if stats["is_magic"] else f"固定 {stats['p_pierce_flat']} + {stats['p_pierce_pct']}%"

                spec_cards_html = f"""
                <div class="specs-grid cols-4">
                    <div class="spec-card">
                        <div class="spec-label">⚔️ 输出核心</div>
                        <div class="spec-main-val">{atk_val} <span class="spec-unit">点</span></div>
                        <div class="spec-sub">{atk_label}</div>
                        <div class="spec-foot">{pen_label}: {pen_val}</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">💥 暴击与攻速</div>
                        <div class="spec-main-val">{stats['crit']}%</div>
                        <div class="spec-sub">暴击效果: {stats['crit_eff']}%</div>
                        <div class="spec-foot">攻速加成: +{stats['aspeed']}%</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">🛡️ 生存坦度</div>
                        <div class="spec-main-val">{stats['hp']} <span class="spec-unit">HP</span></div>
                        <div class="spec-sub">物防 {stats['pdef']} ({stats['pdef_dr']}%)</div>
                        <div class="spec-foot">法防 {stats['mdef']} ({stats['mdef_dr']}%)</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">⚡ 机能与转速</div>
                        <div class="spec-main-val">{stats['cdr']}% <span class="spec-unit">CDR</span></div>
                        <div class="spec-sub">移速: {stats['speed']} 点</div>
                        <div class="spec-foot">技能循环与续航拉满</div>
                    </div>
                </div>
                <div class="dummy-row">
                    <div class="dummy-card squishy">
                        <span class="dummy-icon">🎯</span>
                        <div class="dummy-info">
                            <span class="dummy-title">实战打靶：打中射脆皮（400 防御靶子）</span>
                            <span class="dummy-desc">单套连招净爆发输出伤害</span>
                        </div>
                        <div class="dummy-val">{stats['dmg_squishy']} <span class="unit">净伤害</span></div>
                    </div>
                    <div class="dummy-card tank">
                        <span class="dummy-icon">🛡️</span>
                        <div class="dummy-info">
                            <span class="dummy-title">实战打靶：打前排肉坦（1200 防御靶子）</span>
                            <span class="dummy-desc">抗性折算后单套实际穿透净伤</span>
                        </div>
                        <div class="dummy-val">{stats['dmg_tank']} <span class="unit">净伤害</span></div>
                    </div>
                </div>
                """
            elif lane_key == "打野":
                atk_val = stats["ap"] if stats["is_magic"] else stats["atk"]
                atk_label = "法攻" if stats["is_magic"] else "物攻"
                spec_cards_html = f"""
                <div class="specs-grid cols-4">
                    <div class="spec-card highlight">
                        <div class="spec-label">🗡️ 巡守野刀</div>
                        <div class="spec-main-val" style="font-size:16px;font-weight:700;">{stats['knife_name']}</div>
                        <div class="spec-sub">刷野提速 · 惩戒进阶</div>
                        <div class="spec-foot">控龙与野区经济压制</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">⚔️ 爆发斩杀</div>
                        <div class="spec-main-val">{atk_val} <span class="spec-unit">{atk_label}</span></div>
                        <div class="spec-sub">暴击率: {stats['crit']}%</div>
                        <div class="spec-foot">物穿 {stats['p_pierce_flat']} (+{stats['p_pierce_pct']}%)</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">🛡️ 进场容错</div>
                        <div class="spec-main-val">{stats['hp']} <span class="spec-unit">HP</span></div>
                        <div class="spec-sub">物防 {stats['pdef']} ({stats['pdef_dr']}%)</div>
                        <div class="spec-foot">法防 {stats['mdef']} ({stats['mdef_dr']}%)</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">⚡ 突进机动</div>
                        <div class="spec-main-val">{stats['speed']} <span class="spec-unit">移速</span></div>
                        <div class="spec-sub">冷缩: {stats['cdr']}% CDR</div>
                        <div class="spec-foot">抓人转线极速支援</div>
                    </div>
                </div>
                <div class="dummy-row">
                    <div class="dummy-card squishy">
                        <span class="dummy-icon">🎯</span>
                        <div class="dummy-info">
                            <span class="dummy-title">切后瞬秒能力（打 400 防脆皮）</span>
                            <span class="dummy-desc">野区突袭切入一套单点净伤害</span>
                        </div>
                        <div class="dummy-val">{stats['dmg_squishy']} <span class="unit">净伤</span></div>
                    </div>
                    <div class="dummy-card tank">
                        <span class="dummy-icon">🛡️</span>
                        <div class="dummy-info">
                            <span class="dummy-title">抗性承伤与肉坦威慑（打 1200 防）</span>
                            <span class="dummy-desc">前排拉扯与持续作战折算伤害</span>
                        </div>
                        <div class="dummy-val">{stats['dmg_tank']} <span class="unit">净伤</span></div>
                    </div>
                </div>
                """
            else: # 游走辅助
                spec_cards_html = f"""
                <div class="specs-grid cols-4">
                    <div class="spec-card highlight">
                        <div class="spec-label">🕊️ 主动团队技</div>
                        <div class="spec-main-val" style="font-size:14.5px;font-weight:700;">{stats['support_active']}</div>
                        <div class="spec-sub">开团 / 保排关键释放</div>
                        <div class="spec-foot">瞬间扭转团战局势</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">🌟 团队光环</div>
                        <div class="spec-main-val" style="font-size:14.5px;font-weight:700;">{stats['support_aura']}</div>
                        <div class="spec-sub">范围全队属性共享</div>
                        <div class="spec-foot">大幅强化C位生存输出</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">🛡️ 自身承伤坦度</div>
                        <div class="spec-main-val">{stats['hp']} <span class="spec-unit">HP</span></div>
                        <div class="spec-sub">物防 {stats['pdef']} ({stats['pdef_dr']}%)</div>
                        <div class="spec-foot">法防 {stats['mdef']} ({stats['mdef_dr']}%)</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">⚡ 游走支援机动</div>
                        <div class="spec-main-val">{stats['speed']} <span class="spec-unit">移速</span></div>
                        <div class="spec-sub">冷缩: {stats['cdr']}% CDR</div>
                        <div class="spec-foot">快速探草与全图防抓</div>
                    </div>
                </div>
                <div class="support-utility-banner">
                    <span class="utility-icon">🤝</span>
                    <div class="utility-texts">
                        <strong>游走核心使命：</strong>保障双 C 视野与发育空间，主动装适时抵消敌方首轮爆发伤害，严禁单人盲目追残血。
                    </div>
                </div>
                """

            page_html = render_lane_scheme_page(
                lane_icon, lane_key, avatar_url, hero_cname, hero_title,
                idx, b_name, b_desc, items, items_row, arc_row, spec_cards_html, page_num
            )
            pages_html.append(page_html)
            page_num += 1

    css_base_path = os.path.join(PROJECT_ROOT, "templates", "pdf", "lane_pdf_base.css")
    css_cards_path = os.path.join(PROJECT_ROOT, "templates", "pdf", "lane_pdf_cards.css")
    with open(css_base_path, "r", encoding="utf-8") as f:
        lane_css_a = f.read()
    with open(css_cards_path, "r", encoding="utf-8") as f:
        lane_css_b = f.read()

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{doc_title}</title>
<style>
{lane_css_a}
{lane_css_b}
</style>
</head>
<body>
{"".join(pages_html)}
</body>
</html>
"""
    return html_content

def build_all_lane_pdfs():
    with open(os.path.join(PROJECT_ROOT, "config", "hero_s45_official_builds.json"), "r", encoding="utf-8") as f:
        builds_data = json.load(f)

    out_dir = os.path.join(PROJECT_ROOT, "taobao", "pdf")
    dist_dir = os.path.join(PROJECT_ROOT, "dist_pages", "pdf")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for lane_id, lane_info in LANE_CONFIG.items():
            print(f"📄 正在构建 {lane_info['title']}...")
            html_content = generate_lane_html(lane_id, lane_info, builds_data)
            
            # 临时保存 html 进行渲染
            tmp_html = os.path.join(PROJECT_ROOT, f"scratch_lane_{lane_id}.html")
            with open(tmp_html, "w", encoding="utf-8") as f:
                f.write(html_content)

            page = browser.new_page()
            page.goto(f"file:///{tmp_html.replace(os.sep, '/')}", wait_until="networkidle")
            
            pdf_filename = f"{lane_id}_{lane_info['title']}.pdf"
            target_pdf = os.path.join(out_dir, pdf_filename)
            dist_pdf = os.path.join(dist_dir, pdf_filename)

            page.pdf(
                path=target_pdf,
                format="A4",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            page.close()

            if os.path.exists(tmp_html):
                os.remove(tmp_html)

            # 同步至 dist_pages/pdf/
            import shutil
            shutil.copy2(target_pdf, dist_pdf)
            pdf_size_mb = os.path.getsize(target_pdf) / (1024 * 1024)
            print(f"✅ 完成构建: {pdf_filename} ({pdf_size_mb:.2f} MB)")

        browser.close()
    print("🚀 全部 5 大分路出版级 PDF 构建完成！")

if __name__ == "__main__":
    build_all_lane_pdfs()
