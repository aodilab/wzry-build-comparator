# -*- coding: utf-8 -*-
"""
王者荣耀局内配装沙盒网页静态模板聚合器 (符合 AGENTS.md 行数规范)
从 templates/sandbox/ 目录解耦加载 HTML、CSS、JS 模块组件，
按需组装为单文件运行模板 SANDBOX_HTML_TEMPLATE。
"""

import os

TPL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'sandbox')

def _load(filename: str) -> str:
    path = os.path.join(TPL_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_sandbox_html_template() -> str:
    """按单一职责原则组合拼装完整的单文件 HTML 运行模板 (各子模块均 ≤ 350行)"""
    # 样式模块解耦加载
    theme_layout_css = _load('theme_layout.css')
    hero_hall_css = _load('hero_hall.css')
    lane_picker_css = _load('lane_picker.css')
    hero_studio_css = _load('hero_studio.css')
    item_shop_css = _load('item_shop.css')
    dock_metrics_css = _load('dock_and_metrics.css')
    arcana_dock_card_css = _load('arcana_dock_card.css')
    modal_arcana_css = _load('modal_arcana.css')
    modal_synergy_layout_css = _load('modal_synergy_layout.css')
    modal_synergy_cards_css = _load('modal_synergy_cards.css')
    modal_benchmark_cards_css = _load('modal_benchmark_cards.css')
    modal_combo_calc_css = _load('modal_combo_calc.css')
    synergy_css = _load('synergy.css')
    mobile_layout_css = _load('mobile_layout.css')
    mobile_components_css = _load('mobile_components.css')
    seo_directory_css = _load('seo_directory.css')
    html_body = _load('index.html')

    # 逻辑脚本模块解耦加载
    app_core_js = _load('app_core.js')
    app_hero_select_js = _load('app_hero_select.js')
    app_stats_js = _load('app_stats.js')
    app_arcana_js = _load('app_arcana.js')
    synergy_benchmarks_js = _load('synergy_benchmarks.js')
    synergy_comparator_js = _load('synergy_comparator.js')
    synergy_evaluator_js = _load('synergy_evaluator.js')
    synergy_combos_js = _load('synergy_combos.js')
    app_synergy_js = _load('app_synergy.js')
    app_mobile_js = _load('app_mobile.js')

    combined_css = f"{theme_layout_css}\n\n{hero_hall_css}\n\n{lane_picker_css}\n\n{hero_studio_css}\n\n{item_shop_css}\n\n{dock_metrics_css}\n\n{arcana_dock_card_css}\n\n{modal_arcana_css}\n\n{modal_synergy_layout_css}\n\n{modal_synergy_cards_css}\n\n{modal_benchmark_cards_css}\n\n{modal_combo_calc_css}\n\n{synergy_css}\n\n{mobile_layout_css}\n\n{mobile_components_css}\n\n{seo_directory_css}"
    combined_js = f"{app_core_js}\n\n{app_hero_select_js}\n\n{app_stats_js}\n\n{app_arcana_js}\n\n{synergy_benchmarks_js}\n\n{synergy_comparator_js}\n\n{synergy_evaluator_js}\n\n{synergy_combos_js}\n\n{app_synergy_js}\n\n{app_mobile_js}"

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="description" content="专业级王者荣耀六神装配装推演沙盒与铭文模拟器。收录S38/S45赛季国服133位全英雄官方出装、五级铭文自由搭配、攻防属性协同算分、技能连招与实战克制大典。">
<meta name="keywords" content="王者荣耀出装,王者荣耀铭文搭配,王者出装箱,王者荣耀S38出装,王者荣耀S45出装,六神装推演沙盒,国服英雄出装推荐,装备模拟器,王者大典,英雄克制关系">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="baidu-site-verification" content="codeva-zrVGsSF3M8" />
<meta name="msvalidate.01" content="496C1C17B1E56D30088DFDE842DB4C59" />
<link rel="canonical" href="https://wzry.aodilab.com/">
<!-- Open Graph / 微信与社交媒体分享卡片 -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://wzry.aodilab.com/">
<meta property="og:title" content="王者出装箱 ｜ S38/S45赛季六神装推演沙盒_全英雄铭文搭配与战术克制大典">
<meta property="og:description" content="支持130+全英雄配装推演、五级铭文自由混搭、攻防属性协同算分与克制关系查询。">
<meta property="og:image" content="https://wzry.aodilab.com/apple-touch-icon.png">
<meta property="og:site_name" content="王者出装箱">
<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="王者出装箱 ｜ 六神装推演沙盒">
<meta name="twitter:description" content="专业级王者荣耀六神装配装推演沙盒。">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>王者出装箱 ｜ S38/S45赛季六神装推演沙盒_全英雄铭文搭配与战术克制大典</title>
<!-- 搜索引擎规范化 JSON-LD 结构化数据 -->
__JSON_LD_SCHEMA_PLACEHOLDER__
<style>
{combined_css}
</style>
<!-- 国内权威统计 (51.la) -->
<script charset="UTF-8" id="LA_COLLECT" src="//sdk.51.la/js-sdk-pro.min.js"></script>
<script>if(window.LA)LA.init({{id:"3RHV2P1v28aZF1yy",ck:"3RHV2P1v28aZF1yy",autoTrack:true}})</script>
<!-- 百度统计异步注入点 (站长平台获取 ID 后在此生效) -->
<script>
var _hmt = _hmt || [];
(function() {{
  if (window.BAIDU_TONGJI_ID) {{
    var hm = document.createElement("script");
    hm.src = "https://hm.baidu.com/hm.js?" + window.BAIDU_TONGJI_ID;
    var s = document.getElementsByTagName("script")[0]; 
    s.parentNode.insertBefore(hm, s);
  }}
}})();
</script>
</head>

<body>
{html_body}

<!-- 搜索引擎爬虫白帽 SSR 静态语义大典 -->
__SEO_DIRECTORY_PLACEHOLDER__

<script>
{combined_js}
</script>
</body>
</html>
"""

# 向后兼容导出
SANDBOX_HTML_TEMPLATE = get_sandbox_html_template()
