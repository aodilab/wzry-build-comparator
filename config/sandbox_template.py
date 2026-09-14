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
    base_css = _load('base.css')
    modal_css = _load('modal.css')
    html_body = _load('index.html')
    app_core_js = _load('app_core.js')
    app_arcana_js = _load('app_arcana.js')
    synergy_evaluator_js = _load('synergy_evaluator.js')
    synergy_combos_js = _load('synergy_combos.js')
    app_synergy_js = _load('app_synergy.js')

    combined_js = f"{app_core_js}\n\n{app_arcana_js}\n\n{synergy_evaluator_js}\n\n{synergy_combos_js}\n\n{app_synergy_js}"

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="assets/app_icon.png">
<title>王者出装箱 ｜ 局内六神装配装沙盒</title>
<style>
{base_css}
{modal_css}
</style>
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
