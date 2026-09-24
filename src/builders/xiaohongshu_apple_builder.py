# -*- coding: utf-8 -*-
"""
小红书 3:4 Apple 官网级一体化营销图文生成器 (Apple 官网商品页排版 · 统治力大金句 · 统一数值看板)
架构规范:
- 符合 AGENTS.md 单一职责规范，HTML 与 CSS 模板已全面解耦至 templates/xiaohongshu/
- 纯 Python 构建逻辑调度器，代码行数严格控制在适宜区间 (150 ~ 250 行)
"""

import os
import sys
import base64
import subprocess
import shutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "taobao", "xiaohongshu")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp_apple_html")
TPL_DIR = os.path.join(PROJECT_ROOT, "templates", "xiaohongshu")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def get_base64_img(rel_path: str) -> str:
    """读取本地图片并转为 base64 data URI，保证 100% 离线高清渲染"""
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(full_path):
        return ""
    ext = os.path.splitext(full_path)[1].lower()
    mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    with open(full_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def load_assets() -> dict:
    """预加载核心图片 Base64 字典"""
    return {
        "IMG_YANGJIAN": get_base64_img(r"taobao\assets_cache\hero\178.jpg"),
        "IMG_ROUDAO": get_base64_img(r"taobao\assets_cache\item\1532.png"),
        "IMG_BUJIAXIE": get_base64_img(r"taobao\assets_cache\item\1421.png"),
        "IMG_HEIQIE": get_base64_img(r"taobao\assets_cache\item\1133.png"),
        "IMG_CANGQIONG": get_base64_img(r"taobao\assets_cache\item\1138.png"),
        "IMG_BAOLIE": get_base64_img(r"taobao\assets_cache\item\1335.png"),
        "IMG_MONV": get_base64_img(r"taobao\assets_cache\item\1337.png"),
        "IMG_DIKANGXIE": get_base64_img(r"taobao\assets_cache\item\1423.png"),
        "IMG_HUOJIA": get_base64_img(r"taobao\assets_cache\item\1327.png"),
        "IMG_ZONGSHI": get_base64_img(r"taobao\assets_cache\item\1126.png"),
        "IMG_BINGHEN": get_base64_img(r"taobao\assets_cache\item\1325.png"),
        "IMG_YIBIAN": get_base64_img(r"taobao\assets_cache\arcana\1504.png"),
        "IMG_YINGYAN": get_base64_img(r"taobao\assets_cache\arcana\3514.png"),
        "IMG_SHOULIE": get_base64_img(r"taobao\assets_cache\arcana\2520.png"),
    }


def render_slide_html(slide_idx: int, assets: dict) -> str:
    """从 templates/xiaohongshu/ 加载并装配单张切片的完整 HTML 代码"""
    common_css_path = os.path.join(TPL_DIR, "common.css")
    slide_css_path = os.path.join(TPL_DIR, f"slide{slide_idx}.css")
    slide_html_path = os.path.join(TPL_DIR, f"slide{slide_idx}.html")

    with open(common_css_path, "r", encoding="utf-8") as f:
        common_css = f.read()
    with open(slide_css_path, "r", encoding="utf-8") as f:
        slide_css = f.read()
    with open(slide_html_path, "r", encoding="utf-8") as f:
        html_tpl = f.read()

    context = dict(assets)
    context["common_css"] = common_css
    context["slide_css"] = slide_css

    return html_tpl.format(**context)


def render_html_to_png(html_content: str, output_png_path: str):
    """通过 Headless Chrome 精确渲染 1242x1656 像素小红书 3:4 图文"""
    os.makedirs(TEMP_DIR, exist_ok=True)
    temp_html_path = os.path.join(TEMP_DIR, "render_temp.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1242,1656",
        f"--screenshot={output_png_path}",
        temp_html_path
    ]
    subprocess.run(cmd, check=True)


def build_all_xiaohongshu_slides():
    """批量构建小红书 5 大核心长图图文"""
    print("=" * 60)
    print("🚀 启动小红书 Apple 官网级 3:4 一体化营销图文生成流水线...")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    assets = load_assets()

    tasks = [
        (1, "01_全量数值推演仪表盘_打野杨戬.png", "图1: 全维数值推演看板 (3大分类9项全量指标)"),
        (2, "02_出装对比与互斥诊断_打野杨戬.png", "图2: 顺逆风出装变异对比与互斥诊断"),
        (3, "03_技能机制与装备联动分析_打野杨戬.png", "图3: 英雄机制与神装深度联动分析"),
        (4, "04_战术协同评分与诊断简报_打野杨戬.png", "图4: 战术协同诊断简报与六维综合算分"),
        (5, "05_推演沙盒线上入口与体验指引.png", "图5: 官方配装推演沙盒线上入口与指引")
    ]

    for idx, filename, desc in tasks:
        print(f"\n正在生成 [{idx}/5] {desc}...")
        html = render_slide_html(idx, assets)
        out_png = os.path.join(OUTPUT_DIR, filename)
        render_html_to_png(html, out_png)
        size_kb = os.path.getsize(out_png) / 1024
        print(f"✅ 生成成功: {filename} ({size_kb:.1f} KB)")

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    print("\n" + "=" * 60)
    print("🎉 小红书 Apple 风格全套营销图文已全量生成完毕！")
    print("=" * 60)


if __name__ == "__main__":
    build_all_xiaohongshu_slides()
