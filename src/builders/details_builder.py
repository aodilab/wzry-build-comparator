# -*- coding: utf-8 -*-
"""
王者荣耀全英雄战术大典 - 淘宝商品详情页切片生成器
设计准则: 
1. 彻底遵循 Apple 极简与呼吸感美学 (统一 #f5f5f7 纯白天幕背景，0 色差无缝拼接)
2. 彻底去黑化: 全量使用悬浮纯白微质感卡片 (#ffffff + 柔和阴影 + 精致微边框)
3. 空间韵律无缝衔接: 消除切缝处撞车的孤立药丸，对称留白 (上下 55px)，长图连续滑动浑然一体
4. 英雄数据全面对齐正式服最新 133 位 (收录新英雄王维)
"""

import os
import sys
import shutil
import subprocess
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from templates.details.details_slices import SLICES

DETAILS_DIR = os.path.join(PROJECT_ROOT, "taobao", "details")
TEMP_HTML_DIR = os.path.join(PROJECT_ROOT, "taobao", "temp_details")
CSS_PATH = os.path.join(PROJECT_ROOT, "templates", "details", "details.css")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def load_common_style() -> str:
    """从解耦样式表中读取详情页公共样式"""
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def render_all():
    """自动化通过 Headless Chrome 精确渲染 800x1000 详情页切片"""
    os.makedirs(DETAILS_DIR, exist_ok=True)
    os.makedirs(TEMP_HTML_DIR, exist_ok=True)

    common_style = load_common_style()

    # 清空旧切片
    for f in os.listdir(DETAILS_DIR):
        fpath = os.path.join(DETAILS_DIR, f)
        if os.path.isfile(fpath):
            os.remove(fpath)

    generated_images = []

    for filename, pill_text, title_text, subtitle_html, card_html in SLICES:
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
{common_style}
</style>
</head>
<body>
<div class="header-area">
    <div class="season-pill"><span class="dot"></span><span>{pill_text}</span></div>
    <div class="main-title">{title_text}</div>
    <div class="subtitle">{subtitle_html}</div>
</div>

<div class="hero-stage">
    {card_html}
</div>
</body>
</html>
"""
        temp_html = os.path.join(TEMP_HTML_DIR, f"temp_{filename}.html")
        out_png = os.path.join(DETAILS_DIR, filename)

        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        cmd = [
            CHROME_PATH,
            "--headless",
            "--disable-gpu",
            "--window-size=800,1000",
            f"--screenshot={out_png}",
            temp_html
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ 生成高质感无缝详情页切片: {filename}")
        generated_images.append(out_png)

    # 自动拼接一张全长图 (800 x 5000)，验证接缝无缝效果
    if generated_images:
        total_height = 1000 * len(generated_images)
        merged_img = Image.new("RGB", (800, total_height), color="#f5f5f7")
        for idx, img_path in enumerate(generated_images):
            with Image.open(img_path) as im:
                merged_img.paste(im, (0, idx * 1000))
        merged_out = os.path.join(DETAILS_DIR, "00_详情页长图无缝总览.png")
        merged_img.save(merged_out, quality=95)
        print(f"✅ 生成详情页完整长图无缝总览: {merged_out}")

    if os.path.exists(TEMP_HTML_DIR):
        shutil.rmtree(TEMP_HTML_DIR)


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    render_all()
