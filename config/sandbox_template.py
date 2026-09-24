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
    """按单一职责原则组合拼装完整的单文件 HTML 运行模板"""
    theme_layout_css = _load('theme_layout.css')
    sandbox_panels_css = _load('sandbox_panels.css')
    item_shop_css = _load('item_shop.css')
    dock_metrics_css = _load('dock_and_metrics.css')
    modal_arcana_css = _load('modal_arcana.css')
    modal_synergy_layout_css = _load('modal_synergy_layout.css')
    modal_synergy_cards_css = _load('modal_synergy_cards.css')
    synergy_css = _load('synergy.css')
    mobile_native_css = _load('mobile_native.css')
    html_body = _load('index.html')
    app_core_js = _load('app_core.js')
    app_stats_js = _load('app_stats.js')
    app_arcana_js = _load('app_arcana.js')
    synergy_evaluator_js = _load('synergy_evaluator.js')
    synergy_combos_js = _load('synergy_combos.js')
    app_synergy_js = _load('app_synergy.js')
    app_mobile_js = _load('app_mobile.js')

    combined_css = f"{theme_layout_css}\n\n{sandbox_panels_css}\n\n{item_shop_css}\n\n{dock_metrics_css}\n\n{modal_arcana_css}\n\n{modal_synergy_layout_css}\n\n{modal_synergy_cards_css}\n\n{synergy_css}\n\n{mobile_native_css}"
    combined_js = f"{app_core_js}\n\n{app_stats_js}\n\n{app_arcana_js}\n\n{synergy_evaluator_js}\n\n{synergy_combos_js}\n\n{app_synergy_js}\n\n{app_mobile_js}"

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<link rel="icon" href="assets/app_icon.png">
<title>王者出装箱 ｜ S45赛季六神装推演沙盒</title>
<style>
{combined_css}
</style>
<script charset="UTF-8" id="LA_COLLECT" src="//sdk.51.la/js-sdk-pro.min.js"></script>
<script>if(window.LA)LA.init({{id:"3RHV2P1v28aZF1yy",ck:"3RHV2P1v28aZF1yy",autoTrack:true}})</script>
</head>

<body>
{html_body}
<script>
{combined_js}
</script>
</body>
</html>
"""

# 向后兼容导出
SANDBOX_HTML_TEMPLATE = get_sandbox_html_template()
