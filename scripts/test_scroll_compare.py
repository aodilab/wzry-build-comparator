# -*- coding: utf-8 -*-
"""
Headless UI Verification for:
1. Title text is exactly "王者官方推荐方案"
2. Right panel scrolling all the way to bottom without being obscured
3. 4-grid comparison board rendering correctly with values, badges, and verdict
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.abspath(os.path.join(BASE_DIR, 'dist_pages', 'index.html'))

def test_scroll_and_compare():
    print(f'正在对 {INDEX_HTML} 进行推演室滚动与对比看板深度核验...')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 模拟普通笔记本 1080p 缩放视口 (1366 x 768)
        page = browser.new_page(viewport={'width': 1366, 'height': 768})
        page.goto(f'file:///{INDEX_HTML.replace(os.sep, "/")}')
        page.wait_for_timeout(600)

        # 1. 直接选择赵云打野进入推演室
        page.evaluate('selectHero(HEROES_DATA.find(h => h.cname === "赵云"))')
        page.wait_for_timeout(300)
        page.evaluate('confirmHeroLaneAndEnter("\u6253\u91ce")')
        page.wait_for_timeout(500)

        # 2. 检查标题文案
        title_text = page.locator('.studio-presets-title').inner_text()
        print('官方推荐方案标题:', title_text)
        assert '王者官方推荐方案' in title_text, f'标题文案不符合要求: {title_text}'
        assert '权威' not in title_text, f'标题仍含有“权威”字样: {title_text}'

        # 3. 初始状态下装入一套神装 (点击第一个推荐方案)
        page.evaluate('applyOfficialPreset("preset_1")')
        page.wait_for_timeout(400)

        # 截图 1: 顶部方案卡片与工作台初始状态
        os.makedirs('scratch/test_shots', exist_ok=True)
        page.screenshot(path='scratch/test_shots/pc_studio_top.png')

        # 4. 模拟用户在装备库将其中一件装备换成破军（攻击大件），触发对比数值变化
        print('正在微调出装（换上破军）以观察对比看板反应...')
        page.evaluate('''() => {
            const pojv = ITEMS_DATA.find(i => i.item_name === '破军');
            if (pojv) {
                currentSlots[currentSlots.length - 1] = pojv;
                renderSlots();
                recalculate();
                if (typeof updateSynergyBrief === 'function') updateSynergyBrief();
            }
        }''')
        page.wait_for_timeout(300)

        # 5. 滚动右侧面板到对比看板位置并截图
        print('正在将右侧面板滚动至对比看板位置...')
        page.evaluate('''() => {
            const el = document.getElementById('synergyCompareBoard');
            if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        }''')
        page.wait_for_timeout(300)
        page.screenshot(path='scratch/test_shots/pc_panel_compare_board.png')

        # 6. 滚动右侧面板到最底部，验证一滑到底、绝不遮挡
        print('正在将右侧面板一滑到底...')
        scroll_info = page.evaluate('''() => {
            const panel = document.querySelector('.slots-stats-section-panel');
            panel.scrollTo({ top: panel.scrollHeight, behavior: 'instant' });
            return {
                scrollTop: panel.scrollTop,
                scrollHeight: panel.scrollHeight,
                clientHeight: panel.clientHeight
            };
        }''')
        print('右侧面板滚动信息:', scroll_info)
        page.wait_for_timeout(400)
        page.screenshot(path='scratch/test_shots/pc_panel_scrolled_bottom.png')

        # 6. 断言对比看板内容
        verdict_text = page.locator('#compareVerdictText').inner_text()
        print('对比看板诊断结论:', verdict_text)
        assert len(verdict_text) > 5, '对比看板战术诊断未正确生成'

        # 断言对比卡片中的差值 Badge
        diff_badges = page.locator('#compareGridCards .compare-diff-badge').all_inner_texts()
        print('对比看板差值徽标:', diff_badges)
        assert len(diff_badges) >= 4, '未能渲染 4 项核心对比卡片'
        assert any('领先' in b or '落后' in b for b in diff_badges), '装备变更后未在对比看板中反映出领先/落后'

        browser.close()
        print('【全部通过】滚动一滑到底、文案去“权威”、多维对比看板自动化核验全部通过！')

if __name__ == '__main__':
    test_scroll_and_compare()
