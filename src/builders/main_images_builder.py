"""
淘宝精品详情页切片生成器 (完全继承主图的高级视觉语言：钛金仪表盘、真实图标、饱满质感)
尺寸: 800x1000 像素，与主图 100% 同一风格美学
"""

import os
import subprocess

DETAILS_DIR = r"c:\Users\a1325\Desktop\wzry\taobao\details"
TEMP_HTML_DIR = r"c:\Users\a1325\Desktop\wzry\taobao\temp_details"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


from templates.details.main_images_slices_a import COMMON_STYLE, SLICES_A
from templates.details.main_images_slices_b import SLICES_B

SLICES = SLICES_A + SLICES_B

def render_all():
    os.makedirs(DETAILS_DIR, exist_ok=True)
    os.makedirs(TEMP_HTML_DIR, exist_ok=True)

    # 先清空 details 目录下旧的切片
    for f in os.listdir(DETAILS_DIR):
        fpath = os.path.join(DETAILS_DIR, f)
        if os.path.isfile(fpath):
            os.remove(fpath)

    for filename, pill_text, title_text, subtitle_html, console_html, footer_text in SLICES:
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
{COMMON_STYLE}
</style>
</head>
<body>
<div class="ambient-glow"></div>

<div class="header-area">
    <div class="season-pill"><span class="dot"></span><span>{pill_text}</span></div>
    <div class="main-title">{title_text}</div>
    <div class="subtitle">{subtitle_html}</div>
</div>

<div class="hero-stage">
    <div class="pro-console">
        {console_html}
    </div>
</div>

<div class="footer-note">
    <span>{footer_text}</span>
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
        print(f"✅ 生成高质感详情页切片: {filename}")

    import shutil
    if os.path.exists(TEMP_HTML_DIR):
        shutil.rmtree(TEMP_HTML_DIR)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    render_all()
