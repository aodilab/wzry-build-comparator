# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('console', lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == 'error' else None)
    page.on('pageerror', lambda err: errors.append(f"[pageerror] {err}"))
    page.goto('https://wzry.aodilab.com', wait_until='networkidle')
    page.wait_for_timeout(1500)
    print("Online errors on load:", errors)

    # 尝试在大厅点击英雄进入推演室
    lane_info = page.evaluate('''() => {
        const h = HEROES_DATA.find(x => x.cname === "赵云");
        selectHero(h);
        return {
            hero: h,
            keys: Object.keys(h),
            lanes: h.lanes || h.official_lanes,
            pickerActive: document.getElementById("lanePickerOverlay").classList.contains("active")
        };
    }''')
    print("Lane info:", lane_info)
    page.wait_for_timeout(400)
    # 点击浮层中的第一个分路按钮
    page.locator('#pickerLaneOptions .lane-picker-btn').first.click()
    page.wait_for_timeout(800)
    print("Online errors after enter studio:", errors)

    # 检查对比看板的内容
    grid_html = page.evaluate('document.getElementById("compareGridCards").innerHTML')
    print("compareGridCards HTML length:", len(grid_html))
    print("compareGridCards HTML snippet:", grid_html[:200])

    # 检查右侧面板样式和滚动
    panel_info = page.evaluate('''() => {
        const p = document.querySelector('.slots-stats-section-panel');
        const s = window.getComputedStyle(p);
        return {
            overflowY: s.overflowY,
            height: s.height,
            clientHeight: p.clientHeight,
            scrollHeight: p.scrollHeight,
            scrollTop: p.scrollTop
        };
    }''')
    print("Panel computed info BEFORE wheel:", panel_info)

    # 模拟真实鼠标移动到右侧面板中央并滚动滚轮
    panel_box = page.locator('.slots-stats-section-panel').bounding_box()
    print("Panel bounding box:", panel_box)
    if panel_box:
        page.mouse.move(panel_box['x'] + panel_box['width'] / 2, panel_box['y'] + panel_box['height'] / 2)
        print("Mouse moved over panel center. Dispatching wheel deltaY=400...")
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(400)

    panel_info_after = page.evaluate('''() => {
        const p = document.querySelector('.slots-stats-section-panel');
        return {
            scrollTop: p.scrollTop,
            scrollHeight: p.scrollHeight
        };
    }''')
    print("Panel info AFTER wheel:", panel_info_after)
    os.makedirs('scratch/test_shots', exist_ok=True)
    page.screenshot(path='scratch/test_shots/pc_after_mouse_wheel.png')

    b.close()
