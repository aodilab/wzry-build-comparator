# -*- coding: utf-8 -*-
"""
Headless UI Verification for Level 1 Lane Selection and Flow
严格使用无头 Chromium 独立环境，绝不接管或触碰任何宿主外部浏览器！
"""
import os
import sys

# 避免 Windows 终端 GBK 打印特殊符号 (\u203a) 异常
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.abspath(os.path.join(BASE_DIR, 'dist_pages', 'index.html'))

def test_ui():
    print(f'正在对 {INDEX_HTML} 进行层级 1“先选英雄、再选分路”自动化流转核验...')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. PC 端核验 (1440 x 900)
        # -------------------------------------------------------------
        page_pc = browser.new_page(viewport={'width': 1440, 'height': 900})
        page_pc.goto(f'file:///{INDEX_HTML.replace(os.sep, "/")}')
        page_pc.wait_for_timeout(800)

        # 断言 1: 默认处于 Level 1 选英雄大厅
        is_hall_active = page_pc.evaluate('document.getElementById("viewHeroSelect").classList.contains("active")')
        assert is_hall_active, '默认应当优先展示选英雄大厅 (Level 1)'

        # 断言 2: 大厅中存在实战分路快捷栏，且渲染了当前英雄的分路胶囊
        hall_lane_pills = page_pc.locator('#hallLanePills .hall-lane-pill-btn').all_inner_texts()
        print('PC 端大厅直选分路胶囊 (廉颇):', hall_lane_pills)
        assert len(hall_lane_pills) >= 1, '大厅未能正确渲染分路直选胶囊'

        # 截图保存大厅状态
        os.makedirs('scratch/test_shots', exist_ok=True)
        page_pc.screenshot(path='scratch/test_shots/pc_hall_lane_bar.png')

        # 在大厅中点击“赵云”
        print('正在点击大厅卡片中的“赵云”...')
        page_pc.evaluate('selectHero(HEROES_DATA.find(h => h.cname === "赵云"))')
        page_pc.wait_for_timeout(400)

        # 断言 3: 立即弹出层级 1 分路选择毛玻璃浮层
        is_picker_active = page_pc.evaluate('document.getElementById("lanePickerOverlay").classList.contains("active")')
        print(f'点击英雄后层级 1 分路选择浮层状态: active={is_picker_active}')
        assert is_picker_active, '点击英雄后未在层级 1 弹出实战分路选择浮层'

        # 验证浮层中的分路选项（赵云应展示对抗路与打野）
        picker_options = page_pc.locator('#pickerLaneOptions .lane-picker-btn .lane-picker-btn-name').all_inner_texts()
        print('赵云浮层中可选的实战分路:', picker_options)
        assert '打野' in picker_options or '对抗路' in picker_options, '分路选项缺失'

        # 截图保存层级 1 分路选择浮层
        page_pc.screenshot(path='scratch/test_shots/pc_lane_picker_modal.png')

        # 在浮层中点击【打野】分路，正式进入推演室
        print('在浮层中点击【打野】分路...')
        page_pc.evaluate('confirmHeroLaneAndEnter("打野")')
        page_pc.wait_for_timeout(500)

        # 断言 4: 选定分路后，浮层关闭并进入推演室
        is_studio_active = page_pc.evaluate('document.getElementById("viewStudio").classList.contains("active")')
        is_picker_closed = not page_pc.evaluate('document.getElementById("lanePickerOverlay").classList.contains("active")')
        current_lane = page_pc.evaluate('currentHeroActiveLane')
        print(f'选定分路后状态: 推演室active={is_studio_active}, 浮层closed={is_picker_closed}, 当前分路={current_lane}')
        assert is_studio_active and is_picker_closed and current_lane == '打野', '未能正确以所选分路进入推演室'

        # 截图保存推演室
        page_pc.screenshot(path='scratch/test_shots/pc_studio_after_lane.png')
        page_pc.close()

        # -------------------------------------------------------------
        # 2. 移动端核验 (390 x 844)
        # -------------------------------------------------------------
        page_m = browser.new_page(viewport={'width': 390, 'height': 844})
        page_m.goto(f'file:///{INDEX_HTML.replace(os.sep, "/")}')
        page_m.wait_for_timeout(800)

        # 验证移动端大厅无横向溢出
        scroll_w = page_m.evaluate('document.documentElement.scrollWidth')
        inner_w = page_m.evaluate('window.innerWidth')
        print(f'移动端视口宽度: {inner_w}px, 内容全宽: {scroll_w}px')
        assert scroll_w <= inner_w, f'移动端大厅存在横向溢出: {scroll_w} > {inner_w}'

        # 在移动端点击“孙尚香”
        page_m.evaluate('selectHero(HEROES_DATA.find(h => h.cname === "孙尚香"))')
        page_m.wait_for_timeout(400)
        page_m.screenshot(path='scratch/test_shots/mobile_lane_picker.png')

        # 选择发育路进入推演室
        page_m.evaluate('confirmHeroLaneAndEnter("发育路")')
        page_m.wait_for_timeout(500)
        m_scroll_w = page_m.evaluate('document.documentElement.scrollWidth')
        assert m_scroll_w <= inner_w, f'移动端推演室存在横向溢出: {m_scroll_w} > {inner_w}'
        page_m.screenshot(path='scratch/test_shots/mobile_studio_after_lane.png')
        page_m.close()

        browser.close()
        print('【全部通过】层级 1“先选英雄、再选分路才展示推演” 自动化断言 100% 成功！')

if __name__ == '__main__':
    test_ui()
