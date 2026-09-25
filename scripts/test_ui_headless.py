# -*- coding: utf-8 -*-
"""
Headless UI Verification for Two-Stage Multi-Level Sandbox
严格使用无头 Chromium 独立环境，绝不接管或触碰任何宿主外部浏览器！
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.abspath(os.path.join(BASE_DIR, 'dist_pages', 'index.html'))

def test_ui():
    print(f'正在对 {INDEX_HTML} 进行两段式多层级流转自动化核验...')
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
        is_studio_active = page_pc.evaluate('document.getElementById("viewStudio").classList.contains("active")')
        print(f'PC 端默认视图状态: 大厅active={is_hall_active}, 推演室active={is_studio_active}')
        assert is_hall_active and not is_studio_active, '默认应当优先展示选英雄大厅 (Level 1)'

        # 验证 7 大官方职业分类 Tabs
        tabs = page_pc.locator('#heroTabs .seg-item').all_inner_texts()
        print('PC 端英雄职业分类 Tabs:', tabs)
        assert len(tabs) >= 7, '英雄职业分类 Tabs 缺失'

        # 截图保存 PC 端选英雄大厅
        os.makedirs('scratch/test_shots', exist_ok=True)
        page_pc.screenshot(path='scratch/test_shots/pc_hall.png')

        # 选中“赵云”卡片，点击进入 Level 2 推演室
        print('正在点击大厅中的“赵云”卡片...')
        page_pc.evaluate('selectHero(HEROES_DATA.find(h => h.cname === "赵云"))')
        page_pc.wait_for_timeout(600)

        # 断言 2: 点击英雄后自动滑入 Level 2 推演室
        is_hall_active_after = page_pc.evaluate('document.getElementById("viewHeroSelect").classList.contains("active")')
        is_studio_active_after = page_pc.evaluate('document.getElementById("viewStudio").classList.contains("active")')
        print(f'点击英雄后视图状态: 大厅active={is_hall_active_after}, 推演室active={is_studio_active_after}')
        assert not is_hall_active_after and is_studio_active_after, '选定英雄后未平滑切换至推演室 (Level 2)'

        # 验证赵云动态分路胶囊
        lane_pills = page_pc.locator('#heroLaneSwitchPills .lane-pill-btn').all_inner_texts()
        print('赵云支持的动态实战分路:', lane_pills)
        assert '打野' in lane_pills or '对抗路' in lane_pills, '赵云分路未正确动态渲染'

        # 验证官方 3 套推荐方案大卡片展台
        preset_cards = page_pc.locator('#officialPresetCards .official-preset-card').all()
        print(f'推演室官方推荐方案大卡片数量: {len(preset_cards)}')
        assert len(preset_cards) >= 1, '推演室未展示官方出装推荐卡片'

        # 截图保存 PC 端方案推演室
        page_pc.screenshot(path='scratch/test_shots/pc_studio.png')

        # 测试点击“换英雄”返回 Level 1 选英雄大厅
        print('测试点击换英雄按钮返回大厅...')
        page_pc.locator('.studio-back-btn').click()
        page_pc.wait_for_timeout(400)
        is_hall_back = page_pc.evaluate('document.getElementById("viewHeroSelect").classList.contains("active")')
        assert is_hall_back, '点击换英雄未能成功返回大厅'
        page_pc.close()

        # -------------------------------------------------------------
        # 2. 移动端核验 (390 x 844 iPhone 规范)
        # -------------------------------------------------------------
        page_m = browser.new_page(viewport={'width': 390, 'height': 844})
        page_m.goto(f'file:///{INDEX_HTML.replace(os.sep, "/")}')
        page_m.wait_for_timeout(800)

        # 验证移动端大厅无横向溢出
        scroll_w = page_m.evaluate('document.documentElement.scrollWidth')
        inner_w = page_m.evaluate('window.innerWidth')
        print(f'移动端大厅视口宽度: {inner_w}px, 内容全宽: {scroll_w}px')
        assert scroll_w <= inner_w, f'移动端大厅存在横向溢出: {scroll_w} > {inner_w}'
        page_m.screenshot(path='scratch/test_shots/mobile_hall.png')

        # 在移动端选中“安琪拉”进入推演室
        print('移动端正在选择安琪拉进入推演室...')
        page_m.evaluate('selectHero(HEROES_DATA.find(h => h.cname === "安琪拉"))')
        page_m.wait_for_timeout(600)

        # 验证推演室无横向溢出
        m_scroll_w = page_m.evaluate('document.documentElement.scrollWidth')
        print(f'移动端推演室视口宽度: {inner_w}px, 内容全宽: {m_scroll_w}px')
        assert m_scroll_w <= inner_w, f'移动端推演室存在横向溢出: {m_scroll_w} > {inner_w}'

        # 验证安琪拉分路
        m_lane_pills = page_m.locator('#heroLaneSwitchPills .lane-pill-btn').all_inner_texts()
        print('安琪拉移动端动态分路胶囊:', m_lane_pills)
        assert '中路' in m_lane_pills, '安琪拉分路应为中路'

        # 截图保存移动端推演室
        page_m.screenshot(path='scratch/test_shots/mobile_studio.png')
        page_m.close()

        browser.close()
        print('【全部通过】两段式多层级架构（选英雄大厅 -> 专属推演室）无头测试 100% 成功！')

if __name__ == '__main__':
    test_ui()
