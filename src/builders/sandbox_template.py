# -*- coding: utf-8 -*-
"""
王者荣耀双轨实战配装推演台网页静态模板聚合器 (符合 AGENTS.md 模块化规范)
从 templates/sandbox/ 目录解耦加载 15 个 CSS、3 个 HTML 与 17 个 JS 模块组件，
按需组装为单文件运行模板 SANDBOX_HTML_TEMPLATE。
"""

import os

TPL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "templates", "sandbox")

CSS_MODULES = [
    "css_01_base_and_nav.css",
    "css_02_cards_and_metrics.css",
    "css_03_combos_and_builds.css",
    "css_04_slots_and_arcana_bar.css",
    "css_05_specs_and_passives.css",
    "css_06_modal_item_shop.css",
    "css_07_modal_arcana.css",
    "css_08_modal_skill_breakdown.css",
    "css_09_skill_dual_rows.css",
    "css_10_hero_hall_gallery.css",
    "css_11_studio_and_lane_sheet.css",
    "css_12_seo_footer.css",
    "css_13_guides_and_verdict.css",
    "css_14_compare_layout.css",
    "css_15_guides_column.css",
]

JS_MAIN_MODULES = [
    "js_01_state_and_boot.js",
    "js_02_hero_and_schemes.js",
    "js_03_slots_and_combos.js",
    "js_04_verdict_and_slots_ui.js",
    "js_05_calc_stats.js",
    "js_06_calc_combo.js",
    "js_06b_calc_sustain.js",
    "js_07_render_panels.js",
    "js_08_render_passives.js",
    "js_09_modal_shop.js",
    "js_10_modal_arcana.js",
    "js_11_skill_custom_and_effect.js",
    "js_12_skill_general_and_rows.js",
    "js_13_skill_modal_render.js",
    "js_15_compare_layout.js",
    "js_16_guides_column.js",
]


def _load(filename: str) -> str:
    path = os.path.join(TPL_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().rstrip("\n")


def get_sandbox_html_template() -> str:
    """按单一职责原则组合拼装完整的单文件 HTML 运行模板 (各子模块均 ≤ 334 行)"""
    security_js = _load("js_00_security_shield.js")
    combined_css = "\n".join(_load(fn) for fn in CSS_MODULES)
    html_part1 = _load("html_01_nav_and_views.html")
    html_part2 = _load("html_02_modals.html")
    html_part3 = _load("html_03_lane_and_guides.html")
    combined_main_js = "\n".join(_load(fn) for fn in JS_MAIN_MODULES)
    seo_guides_js = _load("js_14_guides_data.js") + "\n" + _load("js_14_seo_and_guides.js")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>王者出装箱 ｜ 王者荣耀出装推荐与实战伤害推演模拟器_全英雄六神装对比</title>
<meta name="description" content="王者出装箱（wzry.aodilab.com）是专业级王者荣耀出装推荐与实战伤害推演模拟器。支持S45全英雄双轨六神装对照方案VS实战方案伤害对决，靶子防御实时折算净伤害，五级铭文自由混搭，秒查全英雄战术克制与最佳出装。">
<meta name="keywords" content="王者出装箱,王者出装箱官网,王者荣耀出装推演实验室,王者荣耀配装推演实验室,王者荣耀出装,王者荣耀出装推荐,王者出装模拟器,王者荣耀装备伤害计算器,双轨实战对决,六神装推演沙盒,打中射伤害,打坦克伤害,铭文搭配">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="baidu-site-verification" content="codeva-zrVGsSF3M8" />
<meta name="msvalidate.01" content="496C1C17B1E56D30088DFDE842DB4C59" />
<link rel="canonical" href="https://wzry.aodilab.com/">
<link rel="icon" type="image/x-icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192x192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<!-- Open Graph & Social Cards -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="王者出装箱">
<meta property="og:title" content="王者出装箱 ｜ 王者荣耀出装推荐与实战伤害推演模拟器">
<meta property="og:description" content="王者出装箱（wzry.aodilab.com）官方推演平台。收录S45全英雄双轨六神装对照方案VS实战方案伤害对决，靶子防御实时折算净伤害，五级铭文自由混搭，秒查全英雄战术克制与最佳出装。">
<meta property="og:image" content="https://wzry.aodilab.com/social_preview.png">
<meta property="og:url" content="https://wzry.aodilab.com/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="王者出装箱 ｜ 王者荣耀出装推荐与实战伤害推演模拟器">
<meta name="twitter:description" content="王者出装箱（wzry.aodilab.com）官方推演平台。收录S45全英雄双轨六神装对照方案VS实战方案伤害对决，靶子防御实时折算净伤害，五级铭文自由混搭。">
<meta name="twitter:image" content="https://wzry.aodilab.com/social_preview.png">
<!-- 国内权威统计 (51.la) -->
<script charset="UTF-8" id="LA_COLLECT" async src="https://sdk.51.la/js-sdk-pro.min.js"></script>
<script>
{security_js}
if(window.LA)LA.init({{id:"3RHV2P1v28aZF1yy",ck:"3RHV2P1v28aZF1yy",autoTrack:true}})</script>
<style>
{combined_css}
</style>
__JSON_LD_SCHEMA_PLACEHOLDER__
</head>
<body>
{html_part1}
{html_part2}

<script>
// 基础常量数据注入
__HEROES_DATA_PLACEHOLDER__
__ITEMS_DATA_PLACEHOLDER__
__OFFICIAL_BUILDS_PLACEHOLDER__
__ARCANA_DICT_PLACEHOLDER__
__HERO_COMBOS_PLACEHOLDER__
__HERO_SKILLS_DATA_PLACEHOLDER__
{combined_main_js}
</script>

{html_part3}

<script>
{seo_guides_js}
</script>

</body>
</html>
"""


# 向后兼容导出
SANDBOX_HTML_TEMPLATE = get_sandbox_html_template()
