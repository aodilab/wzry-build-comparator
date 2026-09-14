# -*- coding: utf-8 -*-
"""
王者荣耀局内配装沙盒网页静态模板与样式 (Apple HIG 极致设计系统)
遵循苹果人机交互指南 (Human Interface Guidelines)，采用苹果标志性冷银白/深空灰双模式、磨砂玻璃与健康仪表盘美学
专供 sandbox_builder.py 进行数据编译嵌入
"""

SANDBOX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="assets/app_icon.png">
<title>王者出装箱 ｜ 局内六神装配装沙盒</title>
<style>
/* ==========================================================================
   Apple Human Interface Guidelines (HIG) Design System
   支持苹果标志性浅色 (Apple Silver-White) 与深色 (Apple Space-Gray) 原生双外观
   ========================================================================== */

:root[data-theme="light"] {
  --apple-bg: #f5f5f7;
  --apple-canvas-ambient: radial-gradient(circle at 10% 10%, rgba(0, 113, 227, 0.06) 0%, transparent 45%),
                          radial-gradient(circle at 90% 20%, rgba(175, 82, 222, 0.05) 0%, transparent 50%),
                          radial-gradient(circle at 50% 85%, rgba(255, 149, 0, 0.05) 0%, transparent 50%);
  --apple-panel: rgba(255, 255, 255, 0.85);
  --apple-panel-border: rgba(0, 0, 0, 0.08);
  --apple-card: #ffffff;
  --apple-card-hover: #fafafc;
  --apple-subcard: rgba(0, 0, 0, 0.03);
  --apple-slot-bg: rgba(0, 0, 0, 0.03);
  --apple-slot-border: rgba(0, 0, 0, 0.12);
  --apple-border: rgba(0, 0, 0, 0.07);
  --apple-border-hover: rgba(0, 113, 227, 0.4);
  
  --text-primary: #1d1d1f;
  --text-secondary: #6e6e73;
  --text-tertiary: #86868b;
  
  --color-blue: #0071e3;
  --color-blue-bg: rgba(0, 113, 227, 0.1);
  --color-amber: #d97706;
  --color-amber-bg: rgba(217, 119, 6, 0.1);
  --color-green: #34c759;
  --color-green-bg: rgba(52, 199, 89, 0.12);
  --color-red: #ff3b30;
  --color-red-bg: rgba(255, 59, 48, 0.1);
  --color-purple: #af52de;
  --color-purple-bg: rgba(175, 82, 222, 0.1);

  --segmented-bg: rgba(118, 118, 128, 0.12);
  --segmented-active: #ffffff;
  --segmented-shadow: 0 2px 6px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --panel-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.03);
  --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  --card-shadow-hover: 0 8px 24px -4px rgba(0, 0, 0, 0.12);
  --header-bg: rgba(245, 245, 247, 0.82);
  --scrollbar-thumb: rgba(0, 0, 0, 0.18);
}

:root[data-theme="dark"] {
  --apple-bg: #000000;
  --apple-canvas-ambient: radial-gradient(circle at 10% 10%, rgba(10, 132, 255, 0.1) 0%, transparent 45%),
                          radial-gradient(circle at 90% 20%, rgba(191, 90, 242, 0.08) 0%, transparent 50%),
                          radial-gradient(circle at 50% 85%, rgba(255, 159, 10, 0.06) 0%, transparent 50%);
  --apple-panel: rgba(28, 28, 30, 0.75);
  --apple-panel-border: rgba(255, 255, 255, 0.1);
  --apple-card: rgba(44, 44, 46, 0.55);
  --apple-card-hover: rgba(58, 58, 60, 0.75);
  --apple-subcard: rgba(255, 255, 255, 0.04);
  --apple-slot-bg: rgba(255, 255, 255, 0.04);
  --apple-slot-border: rgba(255, 255, 255, 0.14);
  --apple-border: rgba(255, 255, 255, 0.08);
  --apple-border-hover: rgba(10, 132, 255, 0.5);
  
  --text-primary: #f5f5f7;
  --text-secondary: #86868b;
  --text-tertiary: #636366;
  
  --color-blue: #0a84ff;
  --color-blue-bg: rgba(10, 132, 255, 0.15);
  --color-amber: #ff9f0a;
  --color-amber-bg: rgba(255, 159, 10, 0.15);
  --color-green: #30d158;
  --color-green-bg: rgba(48, 209, 88, 0.15);
  --color-red: #ff453a;
  --color-red-bg: rgba(255, 69, 58, 0.15);
  --color-purple: #bf5af2;
  --color-purple-bg: rgba(191, 90, 242, 0.15);

  --segmented-bg: rgba(118, 118, 128, 0.24);
  --segmented-active: rgba(255, 255, 255, 0.18);
  --segmented-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  --panel-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
  --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  --card-shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.5);
  --header-bg: rgba(13, 14, 18, 0.82);
  --scrollbar-thumb: rgba(255, 255, 255, 0.2);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "PingFang SC", "Helvetica Neue", sans-serif;
}

body {
  background-color: var(--apple-bg);
  background-image: var(--apple-canvas-ambient);
  color: var(--text-primary);
  min-height: 100vh;
  padding: 16px 24px;
  overflow-x: hidden;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* ==========================================================================
   1. 苹果风格顶部导航 (Apple Translucent Navigation Bar)
   ========================================================================== */
header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  margin: -16px -24px 20px -24px;
  background: var(--header-bg);
  backdrop-filter: blur(25px) saturate(190%);
  -webkit-backdrop-filter: blur(25px) saturate(190%);
  border-bottom: 1px solid var(--apple-panel-border);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-app-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--apple-border);
  flex-shrink: 0;
}

.brand-titles h1 {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.015em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-titles p {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 苹果药丸按钮 */
.apple-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 16px;
  border-radius: 980px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid transparent;
  outline: none;
}

.apple-btn-secondary {
  background: var(--apple-subcard);
  color: var(--text-primary);
  border-color: var(--apple-border);
}

.apple-btn-secondary:hover {
  background: var(--apple-card-hover);
  border-color: var(--apple-border-hover);
}

.apple-btn-secondary:active {
  transform: scale(0.97);
}

.apple-btn-primary {
  background: var(--color-blue);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.3);
}

.apple-btn-primary:hover {
  filter: brightness(1.08);
  box-shadow: 0 4px 14px rgba(0, 113, 227, 0.45);
  transform: translateY(-1px);
}

.apple-btn-primary:active {
  transform: scale(0.97);
}

/* 浅色/深色主题切换药丸 */
.theme-toggle-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--apple-subcard);
  border: 1px solid var(--apple-border);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.25s;
}

.theme-toggle-btn:hover {
  background: var(--apple-card-hover);
  border-color: var(--apple-border-hover);
  transform: rotate(15deg);
}

/* ==========================================================================
   2. 主体三栏网格架构
   ========================================================================== */
.sandbox-grid {
  display: grid;
  grid-template-columns: 310px 1fr 390px;
  gap: 20px;
  height: calc(100vh - 94px);
}

.apple-panel {
  background: var(--apple-panel);
  border: 1px solid var(--apple-panel-border);
  border-radius: 20px;
  backdrop-filter: blur(25px) saturate(190%);
  -webkit-backdrop-filter: blur(25px) saturate(190%);
  box-shadow: var(--panel-shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.panel-header {
  padding: 16px 18px 12px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: -0.01em;
}

.panel-badge {
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--apple-subcard);
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 500;
}

/* 苹果 Spotlight 搜索框 */
.search-wrapper {
  padding: 0 16px 12px 16px;
}

.apple-search {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 12px;
  font-size: 13px;
  color: var(--text-tertiary);
  pointer-events: none;
}

.apple-input {
  width: 100%;
  height: 36px;
  background: var(--apple-subcard);
  border: 1px solid var(--apple-border);
  border-radius: 10px;
  padding: 0 12px 0 34px;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
}

.apple-input::placeholder {
  color: var(--text-tertiary);
}

.apple-input:focus {
  background: var(--apple-card);
  border-color: var(--color-blue);
  box-shadow: 0 0 0 3px var(--color-blue-bg);
}

/* 苹果 iOS 分段控制器 (Segmented Control) */
.segmented-control {
  display: flex;
  background: var(--segmented-bg);
  padding: 3px;
  border-radius: 10px;
  margin: 0 16px 12px 16px;
  gap: 2px;
}

.seg-item {
  flex: 1;
  text-align: center;
  padding: 5px 0;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: 8px;
  cursor: pointer;
  user-select: none;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
}

.seg-item:hover {
  color: var(--text-primary);
}

.seg-item.active {
  background: var(--segmented-active);
  color: var(--text-primary);
  box-shadow: var(--segmented-shadow);
  font-weight: 600;
}

/* ==========================================================================
   3. 左侧栏：英雄精选 Spotlight 与网格
   ========================================================================== */
.hero-spotlight {
  margin: 0 16px 12px 16px;
  padding: 12px 14px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: var(--card-shadow);
}

.spotlight-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 2px solid var(--color-blue);
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.25);
}

.spotlight-info {
  flex: 1;
  min-width: 0;
}

.spotlight-title {
  font-size: 11px;
  color: var(--text-tertiary);
}

.spotlight-name {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 1px;
  letter-spacing: -0.01em;
}

.spotlight-lane-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--color-blue-bg);
  color: var(--color-blue);
  margin-top: 4px;
}

.hero-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 4px 16px 16px 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.hero-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 4px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: var(--apple-card);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: var(--card-shadow);
}

.hero-card:hover {
  background: var(--apple-card-hover);
  border-color: var(--apple-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

.hero-card.selected {
  background: var(--color-blue-bg);
  border-color: var(--color-blue);
  box-shadow: 0 0 0 2px var(--color-blue), 0 4px 12px rgba(0, 113, 227, 0.2);
}

.hero-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid var(--apple-border);
  transition: transform 0.25s;
}

.hero-card.selected .hero-avatar {
  border-color: var(--color-blue);
  transform: scale(1.05);
}

.hero-card-name {
  font-size: 12px;
  font-weight: 500;
  margin-top: 6px;
  color: var(--text-primary);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

/* ==========================================================================
   4. 中间栏：装备商店（极简通透卡片排版，告别挤压）
   ========================================================================== */
.item-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 4px 16px 20px 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(185px, 1fr));
  gap: 14px;
  align-content: start;
}

/* 苹果官网风格统一规范卡片 (Apple Official Store Uniform Cards - 所有框大小完全一致) */
.item-card {
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  border-radius: 18px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  box-shadow: var(--card-shadow);
  height: 146px;
  box-sizing: border-box;
}

.item-card:hover {
  background: var(--apple-card-hover);
  border-color: var(--apple-border-hover);
  transform: translateY(-3px);
  box-shadow: var(--card-shadow-hover);
}

.item-card.equipped {
  border-color: var(--color-green);
  background: var(--color-green-bg);
}

.item-top {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid var(--apple-border);
  object-fit: cover;
  background: #111;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.item-meta {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.01em;
}

.item-price-pill {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-amber);
  background: var(--color-amber-bg);
  padding: 2px 7px;
  border-radius: 6px;
  margin-top: 3px;
}

.item-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
}

.item-stat-line {
  font-size: 11.5px;
  color: var(--text-secondary);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-stat-primary {
  color: var(--text-primary);
  font-weight: 500;
}

/* 苹果官网风格被动/类别胶囊徽标 (Apple Subtle Pill) */
.item-passive-pill {
  font-size: 10.5px;
  font-weight: 500;
  color: var(--color-amber);
  background: var(--color-amber-bg);
  border-radius: 6px;
  padding: 3px 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 4px;
  display: block;
}

.item-passive-pill.pill-subtle {
  color: var(--text-tertiary);
  background: var(--apple-subcard);
}

.item-equipped-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: var(--color-green);
  color: #fff;
  display: none;
}

.item-card.equipped .item-equipped-badge {
  display: block;
}

/* ==========================================================================
   5. 右侧栏：Apple Watch 灵动槽位与 Apple Health 指标卡片
   ========================================================================== */
.slots-dock {
  padding: 14px 16px;
  background: var(--apple-card);
  border-bottom: 1px solid var(--apple-border);
}

.slots-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.slots-cost {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-amber);
  display: flex;
  align-items: center;
  gap: 4px;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}

.slot {
  aspect-ratio: 1;
  background: var(--apple-slot-bg);
  border: 1.5px dashed var(--apple-slot-border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.slot:hover {
  border-color: var(--color-blue);
  background: var(--apple-card-hover);
}

.slot.filled {
  border-style: solid;
  border-color: var(--apple-border);
  background: var(--apple-card);
  box-shadow: var(--card-shadow);
}

.slot.filled:hover {
  border-color: var(--color-red);
  transform: scale(0.96);
}

.slot img {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  object-fit: cover;
}

.slot-remove-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-red);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: none;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.slot.filled:hover .slot-remove-badge {
  display: flex;
}

.slot-num {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
}

/* Apple Health 风格健康与体能指标 */
.health-metrics-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 5px;
}

.metric-card {
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--card-shadow);
  transition: all 0.2s;
}

.metric-card:hover {
  border-color: var(--apple-border-hover);
  background: var(--apple-card-hover);
}

.metric-label-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.metric-sub {
  font-size: 11px;
  color: var(--text-tertiary);
}

.metric-value-group {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.metric-val {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}

.metric-highlight {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-blue);
  background: var(--color-blue-bg);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 进度条 (Apple Fitness 风格平滑进度条) */
.bar-track {
  width: 80px;
  height: 4px;
  background: var(--apple-subcard);
  border-radius: 980px;
  overflow: hidden;
  margin-top: 3px;
}

.bar-fill {
  height: 100%;
  border-radius: 980px;
  transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.bar-fill-armor { background: linear-gradient(90deg, #34c759, #30d158); }
.bar-fill-marmor { background: linear-gradient(90deg, #af52de, #bf5af2); }
.bar-fill-cdr { background: linear-gradient(90deg, #0071e3, #0a84ff); }

/* 智能诊断通告 (Apple Notification Banner) */
.diag-panel {
  padding: 12px 16px;
  background: var(--apple-card);
  border-top: 1px solid var(--apple-border);
  max-height: 130px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.diag-card {
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 12px;
  line-height: 1.45;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.diag-card-warn {
  background: var(--color-red-bg);
  border: 1px solid rgba(255, 59, 48, 0.2);
  color: var(--color-red);
}

.diag-card-pass {
  background: var(--color-green-bg);
  border: 1px solid rgba(52, 199, 89, 0.2);
  color: var(--color-green);
}

.diag-card-info {
  background: var(--color-blue-bg);
  border: 1px solid rgba(0, 113, 227, 0.2);
  color: var(--color-blue);
}

/* ==========================================================================
   苹果极简滚动条 (Apple Thin Scrollbar)
   ========================================================================== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 980px;
}


/* ==========================================================================
   英雄专属铭文指示条 (Hero Arcana Bar) 与复合模态框 (Arcana Modal)
   ========================================================================== */
.hero-arcana-bar {
  margin: 0 16px 12px 16px;
  padding: 10px 14px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-arcana-bar:hover {
  background: var(--apple-card-hover);
  border-color: var(--color-blue);
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

.arcana-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.arcana-bar-label {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.arcana-edit-link {
  font-size: 11px;
  color: var(--color-blue);
  font-weight: 500;
}

.arcana-chips {
  display: flex;
  gap: 6px;
}

.arcana-chip {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 8px;
  background: var(--apple-subcard);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary);
  border: 1px solid transparent;
  transition: all 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arcana-chip-img {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  object-fit: cover;
  flex-shrink: 0;
}

.arcana-chip-red { background: rgba(255, 59, 48, 0.08); color: #d32f2f; border-color: rgba(255, 59, 48, 0.2); }
.arcana-chip-green { background: rgba(52, 199, 89, 0.08); color: #2e7d32; border-color: rgba(52, 199, 89, 0.2); }
.arcana-chip-blue { background: rgba(0, 113, 227, 0.08); color: #0277bd; border-color: rgba(0, 113, 227, 0.2); }

/* 铭文复合页 Modal 弹层 */
.arcana-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.arcana-modal-overlay.active {
  opacity: 1;
  pointer-events: auto;
}

.arcana-modal-card {
  width: 900px;
  max-width: 94vw;
  max-height: 88vh;
  background: var(--apple-panel);
  border: 1px solid var(--apple-panel-border);
  border-radius: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: scale(0.96);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.arcana-modal-overlay.active .arcana-modal-card {
  transform: scale(1);
}

.arcana-modal-header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--apple-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.arcana-modal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.arcana-modal-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 3px;
}

.arcana-modal-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.arcana-modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--apple-subcard);
  border: 1px solid var(--apple-border);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.arcana-modal-close:hover {
  background: var(--color-red-bg);
  color: var(--color-red);
  border-color: var(--color-red);
}

.arcana-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 28px 24px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.arcana-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.arcana-col-header {
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.arcana-col-red { color: #e53935; }
.arcana-col-green { color: #43a047; }
.arcana-col-blue { color: #1e88e5; }

.arcana-active-card {
  padding: 12px;
  border-radius: 16px;
  background: var(--apple-card);
  border: 1.5px solid;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: var(--card-shadow);
}

.arcana-active-red { border-color: rgba(229, 57, 53, 0.35); background: linear-gradient(135deg, rgba(229, 57, 53, 0.04), transparent); }
.arcana-active-green { border-color: rgba(67, 160, 71, 0.35); background: linear-gradient(135deg, rgba(67, 160, 71, 0.04), transparent); }
.arcana-active-blue { border-color: rgba(30, 136, 229, 0.35); background: linear-gradient(135deg, rgba(30, 136, 229, 0.04), transparent); }

.arcana-active-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.arcana-active-count-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}
.count-tag-full { background: var(--color-green-bg); color: var(--color-green); }
.count-tag-partial { background: var(--color-amber-bg); color: var(--color-amber); }

.arcana-clear-btn {
  font-size: 11px;
  color: var(--text-tertiary);
  cursor: pointer;
  background: none;
  border: none;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
}
.arcana-clear-btn:hover {
  background: var(--apple-subcard);
  color: var(--color-red);
}

.arcana-active-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.arcana-active-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-radius: 8px;
  background: var(--apple-subcard);
  gap: 8px;
}

.arcana-item-mini-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.arcana-active-img-sm {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.arcana-item-name-bold {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

/* 数量调节器 Stepper */
.arcana-stepper {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}

.stepper-btn {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid var(--apple-border);
  background: var(--apple-card);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s;
}

.stepper-btn:hover:not(:disabled) {
  background: var(--color-blue-bg);
  border-color: var(--color-blue);
  color: var(--color-blue);
}

.stepper-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.stepper-val {
  min-width: 22px;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.arcana-active-stats-box {
  font-size: 11px;
  color: var(--text-secondary);
  padding-top: 6px;
  border-top: 1px dashed var(--apple-border);
  line-height: 1.4;
}

/* 备选铭文项中的快捷选满按钮 */
.arcana-full-btn {
  font-size: 10.5px;
  padding: 3px 7px;
  border-radius: 6px;
  border: 1px solid var(--apple-border);
  background: var(--apple-subcard);
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}

.arcana-full-btn:hover {
  background: var(--color-blue);
  border-color: var(--color-blue);
  color: #fff;
}

.arcana-options-title {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.arcana-options-grid {
  display: flex;
  flex-direction: column;
  gap: 7px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 4px;
}

.arcana-option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 12px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  cursor: pointer;
  transition: all 0.2s;
}

.arcana-option-item:hover {
  background: var(--apple-card-hover);
  border-color: var(--color-blue);
  transform: translateX(2px);
}

.arcana-option-item.selected {
  border-color: var(--color-blue);
  background: var(--color-blue-bg);
  box-shadow: 0 0 0 1px var(--color-blue);
}

.arcana-option-img {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.arcana-option-meta {
  flex: 1;
  min-width: 0;
}

.arcana-option-name {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-primary);
}

.arcana-option-desc {
  font-size: 10.5px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arcana-option-check {
  color: var(--color-blue);
  font-size: 14px;
  font-weight: bold;
}


/* ==========================================================================
   二级页面：技能×出装战术联动分析 (Skill-Item Synergy Analysis Modal)
   ========================================================================== */

.synergy-header-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 11px;
  border-radius: 980px;
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.1), rgba(175, 82, 222, 0.1));
  border: 1px solid rgba(0, 113, 227, 0.3);
  color: var(--color-blue);
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  outline: none;
}
.synergy-header-btn:hover {
  background: var(--color-blue);
  color: #fff;
  border-color: var(--color-blue);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
}

.synergy-entry-btn {
  margin: 0 16px 12px 16px;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.08), rgba(175, 82, 222, 0.08));
  border: 1px solid rgba(0, 113, 227, 0.25);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.08);
  outline: none;
}

.synergy-entry-btn:hover {
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.15), rgba(175, 82, 222, 0.15));
  border-color: var(--color-blue);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 113, 227, 0.18);
}

.synergy-entry-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.synergy-entry-icon {
  font-size: 15px;
  color: var(--color-blue);
}

.synergy-entry-txt {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.synergy-entry-sub {
  font-size: 10.5px;
  color: var(--text-secondary);
  margin-left: 4px;
}

.synergy-entry-arrow {
  font-size: 14px;
  color: var(--color-blue);
  font-weight: bold;
}

/* 二级页面 Modal 遮罩与大卡片 */
.synergy-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99998;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.synergy-modal-overlay.active {
  opacity: 1;
  pointer-events: auto;
}

.synergy-modal-card {
  width: 1040px;
  max-width: 95vw;
  height: 90vh;
  background: var(--apple-panel);
  border: 1px solid var(--apple-panel-border);
  border-radius: 24px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform: scale(0.96);
  transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.synergy-modal-overlay.active .synergy-modal-card {
  transform: scale(1);
}

.synergy-modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--apple-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--header-bg);
}

.synergy-header-hero {
  display: flex;
  align-items: center;
  gap: 14px;
}

.synergy-hero-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid var(--color-blue);
  box-shadow: 0 4px 10px rgba(0, 113, 227, 0.2);
}

.synergy-hero-cname {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.synergy-hero-sub {
  font-size: 11.5px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.synergy-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.synergy-modal-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 30px 24px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* 顶部出装与铭文概览横幅 */
.synergy-banner {
  padding: 14px 18px;
  border-radius: 16px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  box-shadow: var(--card-shadow);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.synergy-items-strip {
  display: flex;
  align-items: center;
  gap: 10px;
}

.synergy-item-thumb {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid var(--apple-border);
  object-fit: cover;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.synergy-empty-thumb {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px dashed var(--apple-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font-size: 12px;
}

/* 模块标题与卡片网格 */
.synergy-section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

/* 技能与实战 CD 卡片网格 */
.synergy-skills-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.synergy-skill-card {
  padding: 14px 16px;
  border-radius: 16px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.synergy-skill-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.synergy-skill-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.synergy-skill-badge {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  background: var(--apple-subcard);
  color: var(--color-blue);
}

.synergy-skill-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.synergy-skill-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.synergy-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--color-amber-bg);
  color: var(--color-amber);
  font-weight: 600;
}

.synergy-cd-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-radius: 8px;
  background: var(--apple-subcard);
  font-size: 11.5px;
}

.synergy-cd-highlight {
  color: var(--color-green);
  font-weight: 700;
}

.synergy-skill-desc {
  font-size: 11.5px;
  color: var(--text-secondary);
  line-height: 1.45;
}

/* 装备被动实战联动深度剖析列表 */
.synergy-links-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.synergy-link-card {
  padding: 14px 16px;
  border-radius: 14px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  box-shadow: var(--card-shadow);
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.synergy-link-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  background: var(--color-blue-bg);
  color: var(--color-blue);
}

.synergy-link-content {
  flex: 1;
}

.synergy-link-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.synergy-link-sub {
  font-size: 11px;
  color: var(--color-blue);
  font-weight: 600;
}

.synergy-link-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.45;
  margin-top: 4px;
}

/* 契合度评分与连招打法双列 */
.synergy-bottom-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 16px;
}

.synergy-rating-card, .synergy-combo-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  box-shadow: var(--card-shadow);
}

.synergy-score-circle {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.synergy-score-big {
  font-size: 36px;
  font-weight: 800;
  color: var(--color-blue);
  letter-spacing: -0.02em;
}

.synergy-radar-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.synergy-radar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11.5px;
}

.synergy-radar-track {
  width: 150px;
  height: 6px;
  border-radius: 980px;
  background: var(--apple-subcard);
  overflow: hidden;
}

.synergy-radar-fill {
  height: 100%;
  border-radius: 980px;
  background: linear-gradient(90deg, var(--color-blue), var(--color-green));
}

.synergy-combo-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--apple-subcard);
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 600;
}

.combo-step-num {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-blue);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  flex-shrink: 0;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-blue);
}
</style>
</head>
<body>

<!-- 苹果风格顶部导航 -->
<header>
  <div class="brand-wrapper">
    <img class="brand-app-icon" src="assets/app_icon.png" alt="王者出装箱" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚔️</text></svg>'">
    <div class="brand-titles">
      <h1>王者出装箱</h1>
      <p>局内六神装配装沙盒 ｜ 30颗全量铭文自由搭配 ｜ 属性实时演算</p>
    </div>
  </div>
  <div class="header-actions">
    <button class="theme-toggle-btn" onclick="toggleTheme()" title="切换浅色 / 深色外观" id="themeBtn">🌓</button>
    <button class="apple-btn apple-btn-secondary" onclick="resetSlots()">清空配置</button>
    <button class="apple-btn apple-btn-primary" onclick="exportMarkdown()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
      导出方案
    </button>
  </div>
</header>

<!-- 主体三栏交互容器 -->
<main class="sandbox-grid">

  <!-- 左栏：英雄库选择 -->
  <section class="apple-panel">
    <div class="panel-header">
      <div class="panel-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        英雄基准属性
      </div>
      <span class="panel-badge">15级满级数值</span>
    </div>

    <!-- 苹果精选英雄卡片 -->
    <div class="hero-spotlight" id="heroSpotlight">
      <img id="spotAvatar" class="spotlight-avatar" src="" alt="Hero">
      <div class="spotlight-info">
        <div class="spotlight-title" id="spotTitle">当前选中</div>
        <div class="spotlight-name" id="spotName">-</div>
        <div class="spotlight-lane-tag" id="spotLane">-</div>
      </div>
    </div>

    <!-- 30 颗满配铭文状态快捷栏 (点击唤起复合配置面板) -->
    <div class="hero-arcana-bar" onclick="openArcanaModal()" title="点击自定义调整铭文搭配">
      <div class="arcana-bar-header">
        <span class="arcana-bar-label">
          <span>🔖</span> 30颗满配铭文方案
        </span>
        <span class="arcana-edit-link">调整铭文 ›</span>
      </div>
      <div class="arcana-chips" id="arcanaChipsBar">
        <!-- 动态显示红绿蓝三色铭文胶囊 -->
      </div>
    </div>

    <div class="search-wrapper">
      <div class="apple-search">
        <span class="search-icon">🔍</span>
        <input type="text" id="heroSearch" class="apple-input" placeholder="搜索英雄（如：孙尚香 / 李白）" oninput="filterHeroes()">
      </div>
    </div>

    <div class="segmented-control" id="heroTabs">
      <div class="seg-item active" onclick="setHeroFilter('全部', this)">全部</div>
      <div class="seg-item" onclick="setHeroFilter('对抗路', this)">对抗</div>
      <div class="seg-item" onclick="setHeroFilter('打野', this)">打野</div>
      <div class="seg-item" onclick="setHeroFilter('中路', this)">中路</div>
      <div class="seg-item" onclick="setHeroFilter('发育路', this)">发育</div>
      <div class="seg-item" onclick="setHeroFilter('游走', this)">游走</div>
    </div>

    <div class="hero-scroll-area" id="heroListContainer"></div>
  </section>

  <!-- 中栏：装备商店 -->
  <section class="apple-panel">
    <div class="panel-header">
      <div class="panel-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
        局内装备图鉴
      </div>
      <span class="panel-badge" id="itemCountBadge">全部装备</span>
    </div>

    <div class="search-wrapper">
      <div class="apple-search">
        <span class="search-icon">🔍</span>
        <input type="text" id="itemSearch" class="apple-input" placeholder="搜索装备（如：无尽 / 暗影战斧）" oninput="filterItems()">
      </div>
    </div>

    <div class="segmented-control" id="itemTabs">
      <div class="seg-item active" onclick="setItemFilter('全部', this)">全部</div>
      <div class="seg-item" onclick="setItemFilter('攻击装备', this)">攻击</div>
      <div class="seg-item" onclick="setItemFilter('法术装备', this)">法术</div>
      <div class="seg-item" onclick="setItemFilter('防御装备', this)">防御</div>
      <div class="seg-item" onclick="setItemFilter('移动装备', this)">移动</div>
      <div class="seg-item" onclick="setItemFilter('打野装备', this)">打野</div>
      <div class="seg-item" onclick="setItemFilter('游走装备', this)">游走</div>
    </div>

    <div class="item-scroll-area" id="itemListContainer"></div>
  </section>

  <!-- 右栏：六神装槽位与全维度面板 -->
  <section class="apple-panel">
    <div class="panel-header">
      <div class="panel-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        生效装备与面板
      </div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="panel-badge" id="slotCount">已选 0 / 6 件</span>
        <button class="synergy-header-btn" onclick="openSynergyModal()" title="深度分析当前出装与英雄技能机制联动效果">
          ⚡ 联动分析 ›
        </button>
      </div>
    </div>

    <!-- 灵动槽位 Dock -->
    <div class="slots-dock">
      <div class="slots-header">
        <span style="font-size: 12px; color: var(--text-secondary);">已选神装 (点击卸下)</span>
        <div class="slots-cost">
          <span>总造价</span>
          <span id="totalGold" style="color: var(--color-amber);">0 G</span>
        </div>
      </div>
      <div class="slots-grid" id="slotsGrid"></div>
    </div>

    <!-- Apple Health 风格属性指标 -->
    <div class="health-metrics-scroll" id="statsContainer"></div>

    <!-- 智能诊断 -->
    <div class="diag-panel">
      <div style="font-size: 11px; font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 4px;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        智能诊断与互斥检测
      </div>
      <div id="diagnoseContainer"></div>
    </div>
  </section>

</main>

<!-- 二级页面：技能×出装深度联动分析模态框 (Synergy Modal) -->
<div class="synergy-modal-overlay" id="synergyModalOverlay" onclick="closeSynergyModal(event)">
  <div class="synergy-modal-card" onclick="event.stopPropagation()">
    <div class="synergy-modal-header">
      <div class="synergy-header-hero">
        <img class="synergy-hero-avatar" id="synergyHeroAvatar" src="" alt="Hero">
        <div>
          <div class="synergy-hero-cname">
            <span id="synergyHeroName">-</span>
            <span class="brand-badge" id="synergyHeroRole" style="background: var(--color-blue-bg); color: var(--color-blue);">-</span>
          </div>
          <div class="synergy-hero-sub" id="synergyHeroSub">全套神装与技能机制乘区深度分析报告</div>
        </div>
      </div>
      <div class="synergy-header-actions">
        <button class="apple-btn apple-btn-secondary" onclick="copySynergyReport()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          复制分析报告
        </button>
        <button class="arcana-modal-close" onclick="closeSynergyModal()" title="关闭">✕</button>
      </div>
    </div>

    <div class="synergy-modal-scroll" id="synergyModalScroll">
      <!-- 动态填充四大核心板块 -->
    </div>
  </div>
</div>


<!-- 铭文复合配置面板 (Apple HIG Sheet Modal) -->
<div class="arcana-modal-overlay" id="arcanaModalOverlay" onclick="closeArcanaModal(event)">
  <div class="arcana-modal-card" onclick="event.stopPropagation()">
    <div class="arcana-modal-header">
      <div>
        <div class="arcana-modal-title">
          <span>🔖</span> 30 颗满配五级铭文配置
        </div>
        <div class="arcana-modal-subtitle" id="arcanaModalSub">
          当前英雄专属推荐，属性已自动实时累加至 15 级最终面板
        </div>
      </div>
      <div class="arcana-modal-actions">
        <button class="apple-btn apple-btn-secondary" onclick="resetToHeroDefaultArcana()" title="重置为当前英雄的官方推荐铭文">
          ↺ 恢复官方推荐
        </button>
        <button class="arcana-modal-close" onclick="closeArcanaModal()" title="关闭">✕</button>
      </div>
    </div>

    <!-- 三栏红绿蓝配置区 -->
    <div class="arcana-modal-body" id="arcanaModalBody">
      <!-- 动态渲染红色/绿色/蓝色铭文槽位与选择列表 -->
    </div>
  </div>
</div>

<script>
// === 静态内嵌数据 ===
const HEROES_DATA = __HEROES_DATA_PLACEHOLDER__;
const ITEMS_DATA = __ITEMS_DATA_PLACEHOLDER__;
const ARCANA_DATA = __ARCANA_DATA_PLACEHOLDER__;
const HERO_SKILLS_DATA = __HERO_SKILLS_DATA_PLACEHOLDER__;
const RECIPES_MAP = __RECIPES_MAP_PLACEHOLDER__;
const BOOTS_MAP = __BOOTS_MAP_PLACEHOLDER__;
const ACTIVE_ITEMS = __ACTIVE_ITEMS_PLACEHOLDER__;
const JUNGLE_ITEMS = __JUNGLE_ITEMS_PLACEHOLDER__;

// === 状态机 ===
let currentHero = HEROES_DATA[0] || {};
let currentSlots = [];
let currentHeroFilter = "全部";
let currentItemFilter = "全部";
// 铭文状态：每种颜色支持混搭，记录各铭文具体颗数，如 { red: { '异变': 9, '纷争': 1 }, green: { '鹰眼': 10 }, blue: { '狩猎': 7, '夺萃': 3 } }
let currentArcana = { red: { "异变": 10 }, green: { "鹰眼": 10 }, blue: { "隐匿": 10 } };

window.onload = () => {
  // 读取用户本地保存的主题偏好（默认浅色）
  const savedTheme = localStorage.getItem('apple_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeBtnIcon(savedTheme);

  initHeroArcana(currentHero);
  updateSpotlight();
  renderArcanaBar();
  renderHeroes();
  renderItems();
  renderSlots();
  recalculate();
};

function toggleTheme() {
  const cur = document.documentElement.getAttribute('data-theme') || 'light';
  const next = cur === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('apple_theme', next);
  updateThemeBtnIcon(next);
}

function updateThemeBtnIcon(theme) {
  const btn = document.getElementById('themeBtn');
  if (btn) btn.innerText = theme === 'light' ? '🌙' : '☀️';
}

function updateSpotlight() {
  if (!currentHero) return;
  document.getElementById('spotAvatar').src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${currentHero.ename}/${currentHero.ename}.jpg`;
  document.getElementById('spotName').innerText = currentHero.cname || '未知英雄';
  document.getElementById('spotTitle').innerText = currentHero.title ? `${currentHero.title} · Lv.15 满级` : 'Lv.15 满级状态';
  document.getElementById('spotLane').innerText = `${currentHero.lane || '对抗路'} ｜ ${currentHero.role || '战士'}`;
}

function setHeroFilter(lane, el) {
  currentHeroFilter = lane;
  document.querySelectorAll('#heroTabs .seg-item').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  renderHeroes();
}

function setItemFilter(cat, el) {
  currentItemFilter = cat;
  document.querySelectorAll('#itemTabs .seg-item').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  renderItems();
}

function filterHeroes() { renderHeroes(); }
function filterItems() { renderItems(); }

function renderHeroes() {
  const query = (document.getElementById('heroSearch').value || '').trim().toLowerCase();
  const container = document.getElementById('heroListContainer');
  container.innerHTML = '';
  
  const filtered = HEROES_DATA.filter(h => {
    const matchLane = (currentHeroFilter === '全部') || (h.lane === currentHeroFilter);
    const matchQuery = !query || h.cname.toLowerCase().includes(query) || (h.title && h.title.toLowerCase().includes(query));
    return matchLane && matchQuery;
  });

  filtered.forEach(h => {
    const card = document.createElement('div');
    card.className = `hero-card ${currentHero.ename === h.ename ? 'selected' : ''}`;
    card.onclick = () => selectHero(h);
    card.innerHTML = `
      <img class="hero-avatar" alt="${h.cname}" src="https://game.gtimg.cn/images/yxzj/img201606/heroimg/${h.ename}/${h.ename}.jpg" onerror="this.src='https://game.gtimg.cn/images/yxzj/img201606/heroimg/105/105.jpg'">
      <div class="hero-card-name">${h.cname}</div>
    `;
    container.appendChild(card);
  });
}

function initHeroArcana(hero) {
  if (hero && hero.recommended_arcana) {
    const rec = hero.recommended_arcana;
    currentArcana = {
      red: { [rec.red]: 10 },
      green: { [rec.green]: 10 },
      blue: { [rec.blue]: 10 }
    };
  } else {
    currentArcana = {
      red: { "异变": 10 },
      green: { "鹰眼": 10 },
      blue: { "隐匿": 10 }
    };
  }
}

function selectHero(hero) {
  currentHero = hero;
  initHeroArcana(hero);
  updateSpotlight();
  renderArcanaBar();
  renderHeroes();
  recalculate();
}


// === 铭文管理与复合模态框系统 (支持自由混搭任意颗数) ===
function getColorTotalCount(colorKey) {
  const map = currentArcana[colorKey] || {};
  return Object.values(map).reduce((sum, val) => sum + val, 0);
}

function renderArcanaBar() {
  const container = document.getElementById('arcanaChipsBar');
  if (!container) return;
  container.innerHTML = '';

  const colors = [
    { key: 'red', name: '红', cls: 'arcana-chip-red' },
    { key: 'green', name: '绿', cls: 'arcana-chip-green' },
    { key: 'blue', name: '蓝', cls: 'arcana-chip-blue' }
  ];

  colors.forEach(c => {
    const map = currentArcana[c.key] || {};
    const entries = Object.entries(map).filter(([_, cnt]) => cnt > 0);
    const totalCount = getColorTotalCount(c.key);
    const chip = document.createElement('div');
    chip.className = `arcana-chip ${c.cls}`;

    if (entries.length === 0) {
      chip.innerHTML = `<span>${c.name}: 未配置</span>`;
    } else {
      // 找到颗数最多的铭文用来展示图标
      entries.sort((a, b) => b[1] - a[1]);
      const mainArc = ARCANA_DATA[entries[0][0]] || {};
      const label = entries.map(([name, count]) => `${count}${name}`).join(' · ');
      chip.title = `${c.name}色铭文 (${totalCount}/10颗): ` + entries.map(([name, count]) => `${name} ×${count}`).join(' ｜ ');
      chip.innerHTML = `
        <img class="arcana-chip-img" src="${mainArc.icon || ''}" onerror="this.style.display='none'">
        <span>${label}</span>
      `;
    }
    container.appendChild(chip);
  });
}

function openArcanaModal() {
  const overlay = document.getElementById('arcanaModalOverlay');
  if (!overlay) return;
  overlay.classList.add('active');
  document.getElementById('arcanaModalSub').innerText = `【${currentHero.cname || ''}】铭文方案，支持自由增减颗数混搭，修改后立即实时重新演算面板`;
  renderArcanaModal();
}

function closeArcanaModal(e) {
  if (e && e.target !== e.currentTarget) return;
  const overlay = document.getElementById('arcanaModalOverlay');
  if (overlay) overlay.classList.remove('active');
}

function renderArcanaModal() {
  const body = document.getElementById('arcanaModalBody');
  if (!body) return;
  body.innerHTML = '';

  const sections = [
    { key: 'red', title: '红色铭文 (上限10颗)', colClass: 'arcana-col-red', activeClass: 'arcana-active-red' },
    { key: 'green', title: '绿色铭文 (上限10颗)', colClass: 'arcana-col-green', activeClass: 'arcana-active-green' },
    { key: 'blue', title: '蓝色铭文 (上限10颗)', colClass: 'arcana-col-blue', activeClass: 'arcana-active-blue' }
  ];

  sections.forEach(sec => {
    const col = document.createElement('div');
    col.className = 'arcana-col';

    const map = currentArcana[sec.key] || {};
    const totalCount = getColorTotalCount(sec.key);
    const countTagClass = totalCount === 10 ? 'count-tag-full' : 'count-tag-partial';

    // 1. 计算当前颜色下已选铭文的汇总属性
    let colTotals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, crit:0, crit_effect:0, aspeed:0, cdr:0, percent_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce:0, m_pierce:0, hp_regen:0 };
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        colTotals.atk += (s.phys_atk || 0) * count;
        colTotals.ap += (s.magic_atk || 0) * count;
        colTotals.pdef += (s.phys_def || 0) * count;
        colTotals.mdef += (s.magic_def || 0) * count;
        colTotals.hp += (s.max_hp || 0) * count;
        colTotals.crit += (s.crit_rate_pct || 0) * count;
        colTotals.crit_effect += (s.crit_effect_pct || 0) * count;
        colTotals.aspeed += (s.atk_speed_pct || 0) * count;
        colTotals.cdr += (s.cd_reduction_pct || 0) * count;
        colTotals.percent_speed += (s.move_speed_pct || 0) * count;
        colTotals.p_lifesteal += (s.phys_vamp_pct || 0) * count;
        colTotals.m_lifesteal += (s.magic_vamp_pct || 0) * count;
        colTotals.p_pierce += (s.phys_pierce || 0) * count;
        colTotals.m_pierce += (s.magic_pierce || 0) * count;
        colTotals.hp_regen += (s.hp_regen || 0) * count;
      }
    }

    const statSummaryLines = [];
    if (colTotals.atk) statSummaryLines.push(`物攻 +${Math.round(colTotals.atk*10)/10}`);
    if (colTotals.ap) statSummaryLines.push(`法攻 +${Math.round(colTotals.ap*10)/10}`);
    if (colTotals.max_hp || colTotals.hp) statSummaryLines.push(`生命 +${Math.round(colTotals.hp*10)/10}`);
    if (colTotals.pdef) statSummaryLines.push(`物防 +${Math.round(colTotals.pdef*10)/10}`);
    if (colTotals.mdef) statSummaryLines.push(`魔防 +${Math.round(colTotals.mdef*10)/10}`);
    if (colTotals.p_pierce) statSummaryLines.push(`物穿 +${Math.round(colTotals.p_pierce*10)/10}`);
    if (colTotals.m_pierce) statSummaryLines.push(`法穿 +${Math.round(colTotals.m_pierce*10)/10}`);
    if (colTotals.aspeed) statSummaryLines.push(`攻速 +${Math.round(colTotals.aspeed*10)/10}%`);
    if (colTotals.percent_speed) statSummaryLines.push(`移速 +${Math.round(colTotals.percent_speed*10)/10}%`);
    if (colTotals.crit) statSummaryLines.push(`暴击率 +${Math.round(colTotals.crit*10)/10}%`);
    if (colTotals.crit_effect) statSummaryLines.push(`暴效 +${Math.round(colTotals.crit_effect*10)/10}%`);
    if (colTotals.cdr) statSummaryLines.push(`冷缩 +${Math.round(colTotals.cdr*10)/10}%`);
    if (colTotals.p_lifesteal) statSummaryLines.push(`物吸 +${Math.round(colTotals.p_lifesteal*10)/10}%`);
    if (colTotals.m_lifesteal) statSummaryLines.push(`法吸 +${Math.round(colTotals.m_lifesteal*10)/10}%`);
    if (colTotals.hp_regen) statSummaryLines.push(`回血 +${Math.round(colTotals.hp_regen*10)/10}`);

    const statSummaryStr = statSummaryLines.join(' ｜ ') || '暂无已生效属性';

    // 2. 生成已选组合条目 HTML
    const activeEntries = Object.entries(map).filter(([_, cnt]) => cnt > 0);
    let activeRowsHtml = '';
    if (activeEntries.length === 0) {
      activeRowsHtml = `<div style="font-size: 11px; color: var(--text-tertiary); text-align: center; padding: 10px 0;">当前槽位为空，请从下方选择添加（最多10颗）</div>`;
    } else {
      activeEntries.forEach(([name, cnt]) => {
        const arcData = ARCANA_DATA[name] || {};
        activeRowsHtml += `
          <div class="arcana-active-item-row">
            <div class="arcana-item-mini-info">
              <img class="arcana-active-img-sm" src="${arcData.icon}" alt="${name}">
              <div>
                <span class="arcana-item-name-bold">${name}</span>
                <span style="font-size: 10px; color: var(--text-tertiary); margin-left: 4px;">(${arcData.raw_des})</span>
              </div>
            </div>
            <div class="arcana-stepper">
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${name}', -1)">-</button>
              <span class="stepper-val">${cnt}</span>
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${name}', 1)" ${totalCount >= 10 ? 'disabled' : ''}>+</button>
            </div>
          </div>
        `;
      });
    }

    // 3. 筛选出属于当前颜色的全部 10 款五级铭文
    const colorArcanas = Object.values(ARCANA_DATA).filter(a => a.color_type === sec.key);
    let optionsHtml = '';
    colorArcanas.forEach(opt => {
      const currentCount = map[opt.name] || 0;
      const isSelected = currentCount > 0;
      optionsHtml += `
        <div class="arcana-option-item ${isSelected ? 'selected' : ''}">
          <img class="arcana-option-img" src="${opt.icon}" alt="${opt.name}">
          <div class="arcana-option-meta">
            <div class="arcana-option-name">${opt.name}</div>
            <div class="arcana-option-desc">${opt.raw_des}</div>
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <button class="arcana-full-btn" onclick="setArcanaFull('${sec.key}', '${opt.name}')" title="将该铭文直接设为 10 颗满配">满配10</button>
            <div class="arcana-stepper">
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${opt.name}', -1)" ${currentCount <= 0 ? 'disabled' : ''}>-</button>
              <span class="stepper-val" style="${currentCount > 0 ? 'color: var(--color-blue);' : 'color: var(--text-tertiary);'}">${currentCount}</span>
              <button class="stepper-btn" onclick="modifyArcanaCount('${sec.key}', '${opt.name}', 1)" ${totalCount >= 10 ? 'disabled' : ''}>+</button>
            </div>
          </div>
        </div>
      `;
    });

    col.innerHTML = `
      <div class="arcana-col-header ${sec.colClass}">
        <span>●</span> ${sec.title}
      </div>
      <div class="arcana-active-card ${sec.activeClass}">
        <div class="arcana-active-header">
          <span class="arcana-active-count-tag ${countTagClass}">已配 ${totalCount} / 10 颗</span>
          <button class="arcana-clear-btn" onclick="clearArcanaSlot('${sec.key}')" title="清空该颜色铭文">清空</button>
        </div>
        <div class="arcana-active-list">
          ${activeRowsHtml}
        </div>
        <div class="arcana-active-stats-box">
          <strong>槽位加成</strong>：${statSummaryStr}
        </div>
      </div>
      <div class="arcana-options-title">五级铭文库（可自由加减混搭）：</div>
      <div class="arcana-options-grid">
        ${optionsHtml}
      </div>
    `;
    body.appendChild(col);
  });
}

function showToast(msg) {
  let toast = document.getElementById('sandboxToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'sandboxToast';
    toast.style.cssText = "position:fixed; bottom:40px; left:50%; transform:translateX(-50%); background:rgba(30,30,32,0.88); backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px); color:#fff; padding:10px 22px; border-radius:980px; font-size:13px; font-weight:500; box-shadow:0 10px 30px rgba(0,0,0,0.25); z-index:99999; pointer-events:none; transition:all 0.3s cubic-bezier(0.16,1,0.3,1); opacity:0;";
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.style.opacity = '1';
  toast.style.transform = 'translateX(-50%) translateY(0)';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-50%) translateY(10px)';
  }, 2200);
}

function modifyArcanaCount(colorKey, arcanaName, delta) {
  if (!currentArcana[colorKey]) currentArcana[colorKey] = {};
  const curr = currentArcana[colorKey][arcanaName] || 0;
  const total = getColorTotalCount(colorKey);

  if (delta > 0) {
    if (total >= 10) {
      showToast("当前槽位已满 10 颗！请先点击 [-] 减少其他铭文，再增加。");
      return;
    }
    currentArcana[colorKey][arcanaName] = curr + 1;
  } else if (delta < 0) {
    if (curr > 1) {
      currentArcana[colorKey][arcanaName] = curr - 1;
    } else {
      delete currentArcana[colorKey][arcanaName];
    }
  }

  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function setArcanaFull(colorKey, arcanaName) {
  currentArcana[colorKey] = { [arcanaName]: 10 };
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function clearArcanaSlot(colorKey) {
  currentArcana[colorKey] = {};
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}

function resetToHeroDefaultArcana() {
  initHeroArcana(currentHero);
  renderArcanaBar();
  renderArcanaModal();
  recalculate();
}


// === 二级页面：技能×出装战术联动分析引擎 ===
function openSynergyModal() {
  const overlay = document.getElementById('synergyModalOverlay');
  if (!overlay) return;
  overlay.classList.add('active');

  // 1. 填充头部英雄基本信息
  document.getElementById('synergyHeroAvatar').src = `https://game.gtimg.cn/images/yxzj/img201606/heroimg/${currentHero.ename}/${currentHero.ename}.jpg`;
  document.getElementById('synergyHeroName').innerText = currentHero.cname;
  document.getElementById('synergyHeroRole').innerText = `${currentHero.lane} ｜ ${currentHero.role}`;
  document.getElementById('synergyHeroSub').innerText = `${currentHero.title || '英雄'} · 六神装被动效果与技能机制联动实战报告`;

  renderSynergyContent();
}

function closeSynergyModal(e) {
  if (e && e.target !== e.currentTarget) return;
  const overlay = document.getElementById('synergyModalOverlay');
  if (overlay) overlay.classList.remove('active');
}

function renderSynergyContent() {
  const container = document.getElementById('synergyModalScroll');
  if (!container) return;

  const skills = HERO_SKILLS_DATA[currentHero.cname] || [];
  const effItems = [];
  // 获取当前生效装备（排除吞噬件）
  for (let i = 0; i < currentSlots.length; i++) {
    const curr = currentSlots[i].item_name;
    let isConsumed = false;
    for (let j = i + 1; j < currentSlots.length; j++) {
      const later = currentSlots[j].item_name;
      const recipes = RECIPES_MAP[later] || [];
      if (recipes.includes(curr)) { isConsumed = true; break; }
    }
    if (!isConsumed) effItems.push(currentSlots[i]);
  }

  // 计算冷却缩减与属性
  let totalCdr = 0;
  let totalPhysPierce = 0;
  let totalMagicPierce = 0;
  let hasSpellblade = false;
  let spellbladeItem = '';
  let hasHealBoost = false;
  let hasDamageReduce = false;
  let hasOnHit = false;

  effItems.forEach(it => {
    const st = it.stats || {};
    totalCdr += st.cdr || 0;
    totalPhysPierce += st.p_pierce_flat || 0;
    totalMagicPierce += st.m_pierce_flat || 0;
    if (['宗师之力', '冰痕之握', '巫术法杖', '光辉之剑'].includes(it.item_name)) {
      hasSpellblade = true;
      spellbladeItem = it.item_name;
    }
    if (it.item_name === '不死鸟之眼') hasHealBoost = true;
    if (it.item_name === '纯净苍穹') hasDamageReduce = true;
    if (['末世', '闪电匕首', '金色圣剑', '寒霜袭侵'].includes(it.item_name)) hasOnHit = true;
  });

  // 加上铭文冷缩与穿透
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        totalCdr += (s.cd_reduction_pct || 0) * count;
        totalPhysPierce += (s.phys_pierce || 0) * count;
        totalMagicPierce += (s.magic_pierce || 0) * count;
      }
    }
  });

  const cappedCdr = Math.min(Math.round(totalCdr * 10) / 10, 40);
  const cdrRatio = cappedCdr / 100;

  // 1. 横幅：当前出装与铭文展示
  let itemThumbsHtml = '';
  for (let i = 0; i < 6; i++) {
    if (currentSlots[i]) {
      itemThumbsHtml += `<img class="synergy-item-thumb" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${currentSlots[i].item_id}.jpg" alt="${currentSlots[i].item_name}" title="${currentSlots[i].item_name}">`;
    } else {
      itemThumbsHtml += `<div class="synergy-empty-thumb">+</div>`;
    }
  }

  const arcDescParts = [];
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    const sub = Object.entries(map).filter(([_, c]) => c > 0).map(([n, c]) => `${c}${n}`).join('+');
    if (sub) arcDescParts.push(sub);
  });
  const arcDescStr = arcDescParts.join(' · ') || '未配置铭文';

  const bannerHtml = `
    <div class="synergy-banner">
      <div class="synergy-items-strip">
        <span style="font-size: 12px; font-weight: 700; color: var(--text-secondary);">已配装备：</span>
        ${itemThumbsHtml}
      </div>
      <div style="font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
        <span>🔖 <strong>铭文组合</strong>：${arcDescStr}</span>
        <span style="background: var(--color-blue-bg); color: var(--color-blue); font-weight: 700; padding: 2px 8px; border-radius: 6px;">实战冷缩: ${cappedCdr}%</span>
      </div>
    </div>
  `;

  // 2. 英雄技能机制与动态冷却折算卡片
  let skillsCardsHtml = '';
  skills.forEach((sk, idx) => {
    let cdDisplay = sk.cd;
    if (sk.cd_sec > 0) {
      const reduced = Math.round(sk.cd_sec * (1 - cdrRatio) * 10) / 10;
      const diff = Math.round((sk.cd_sec - reduced) * 10) / 10;
      cdDisplay = `⚡ 实战CD: <span class="synergy-cd-highlight">${reduced}s</span> <span style="color:var(--text-tertiary); font-size:11px;">(基准 ${sk.cd_sec}s ｜ 缩短 ${diff}s)</span>`;
    } else {
      cdDisplay = `<span style="color:var(--text-tertiary);">${sk.cd}</span>`;
    }

    const tagsHtml = (sk.tags || []).map(t => `<span class="synergy-tag">${t}</span>`).join('');
    skillsCardsHtml += `
      <div class="synergy-skill-card">
        <div class="synergy-skill-top">
          <div class="synergy-skill-name-row">
            <span class="synergy-skill-badge">${sk.type}</span>
            <span class="synergy-skill-name">${sk.name}</span>
          </div>
          <div class="synergy-skill-tags">${tagsHtml}</div>
        </div>
        <div class="synergy-cd-bar">
          <span>冷却时间折算</span>
          <span>${cdDisplay}</span>
        </div>
        <div class="synergy-skill-desc">${sk.desc}</div>
      </div>
    `;
  });

  // 3. 动态装备被动联动实战深度剖析
  const synergyItems = [];

  // A. 强击被动
  if (hasSpellblade) {
    synergyItems.push({
      icon: '⚡',
      title: `【强击被动】连招普攻爆发与减速留人`,
      item: spellbladeItem,
      desc: `核心装备【${spellbladeItem}】的【强击】被动与【${currentHero.cname}】的技能机制天然契合！在释放任意技能后 5 秒内，下一次普攻将附带额外强击爆发伤害，并附带强力减速。实战建议在释放技能后务必穿插一次强化普攻，实现伤害最大化与无缝黏人！`
    });
  }

  // B. 穿透破甲
  if (totalPhysPierce > 50) {
    synergyItems.push({
      icon: '🎯',
      title: `【高额物穿乘区】破甲无视敌方抗性`,
      item: `总物理穿透 ${Math.round(totalPhysPierce)} 点`,
      desc: `当前出装与铭文合计提供 ${Math.round(totalPhysPierce)} 点固定物理穿透！对局中敌方射手与法师在满级时的基础物理护甲仅为 350 点左右，此套穿透可直接削减敌方大半护甲，使【${currentHero.cname}】的技能物理伤害无限逼近真实伤害，斩杀脆皮犹如切菜！`
    });
  } else if (totalMagicPierce > 50) {
    synergyItems.push({
      icon: '🔮',
      title: `【法术穿透乘区】法球与技能全额贯穿`,
      item: `总法术穿透 ${Math.round(totalMagicPierce)} 点`,
      desc: `当前配置拥有 ${Math.round(totalMagicPierce)} 点高额法穿，让敌方魔抗形同虚设，全面激发英雄全套技能与法球的最高 AP 爆发！`
    });
  }

  // C. 纯净苍穹免伤
  if (hasDamageReduce) {
    synergyItems.push({
      icon: '🛡️',
      title: `【纯净苍穹·驱散】40%免伤与受控解控进场`,
      item: '纯净苍穹',
      desc: `纯净苍穹【驱散】主动技能可在受到控制状态下释放，获得 40% 极高免伤并减速周围敌人，同时首个技能命中敌人对其造成残废减速与自身伤害降低 20%。进场打团或被集火时开启，可硬抗敌方一整套爆发伤害完成逆风反打！`
    });
  }

  // D. 不死鸟残血回血放大
  const hasSkillHeal = skills.some(s => (s.tags || []).includes('技能回血'));
  if (hasHealBoost) {
    if (hasSkillHeal) {
      synergyItems.push({
        icon: '❤️',
        title: `【不死鸟之眼·血统】残血治疗量翻倍反杀`,
        item: '不死鸟之眼',
        desc: `【${currentHero.cname}】自身拥有回血机制，与不死鸟之眼的唯一被动【血统】形成质变联动！血量每损失 10%，受到的所有治疗效果额外增加 6%。在血量低于 50% 时治疗量提升高达 30%~60%，残血开出技能回血可瞬间拉满血线，创造医学奇迹与极限残血反杀！`
      });
    } else {
      synergyItems.push({
        icon: '❤️',
        title: `【不死鸟之眼】法抗与回血增益`,
        item: '不死鸟之眼',
        desc: `提供高额法术防御与最大生命值，配合铭文或吸血装，在残血时获得高额受治疗提升，增强对法师的抗击打与赖线能力。`
      });
    }
  }

  // E. 冷却周转联动
  if (cappedCdr >= 30) {
    synergyItems.push({
      icon: '⏱️',
      title: `【极限制动周转】高达 ${cappedCdr}% 冷缩加速连招循环`,
      item: `实战冷缩 ${cappedCdr}%`,
      desc: `当前配装使技能冷却缩减达到 ${cappedCdr}%（接近 40% 极限制动上限）！核心主动技能真空期由原来的数秒大幅缩短至眨眼之间，小技能几乎可以不断穿插释放，团战周转效率与拉扯容错提升至极限！`
    });
  }

  // F. 普攻法球
  if (hasOnHit) {
    synergyItems.push({
      icon: '⚔️',
      title: `【普攻多段法球】触发伤害乘区`,
      item: '法球装备组',
      desc: `配合英雄高攻速与普攻穿插动作，高频次触发附带的百分比当前生命伤害或额外魔法伤害，前排坦克血量也能快速蒸发！`
    });
  }

  // 若装备被动较少，做保底呈现
  if (synergyItems.length === 0) {
    synergyItems.push({
      icon: '⚔️',
      title: `【基础属性强化】平稳支撑英雄作战`,
      item: '基础属性套装',
      desc: `当前所选装备稳步提升基础攻击、生命与防御数值，建议补充暗影战斧、冰痕之握、纯净苍穹或无尽战刃等核心成装，激发全量被动联动特效！`
    });
  }

  let synergyLinksHtml = '';
  synergyItems.forEach(item => {
    synergyLinksHtml += `
      <div class="synergy-link-card">
        <div class="synergy-link-icon-box">${item.icon}</div>
        <div class="synergy-link-content">
          <div class="synergy-link-title">
            <span>${item.title}</span>
            <span class="synergy-link-sub">${item.item}</span>
          </div>
          <div class="synergy-link-desc">${item.desc}</div>
        </div>
      </div>
    `;
  });

  // 4. 契合度评分与连招打法
  const score = Math.min(85 + effItems.length * 2 + (hasSpellblade ? 3 : 0) + (hasDamageReduce ? 2 : 0) + (cappedCdr >= 30 ? 2 : 0), 99);
  
  // 连招生成逻辑
  let comboSteps = [];
  const hasDash = skills.some(s => (s.tags || []).includes('位移突进'));
  const hasCc = skills.some(s => (s.tags || []).includes('硬控'));

  if (currentHero.cname === '杨戬') {
    comboSteps = [
      '1技能哮天犬远程预判标记目标 (施加斩杀印记)',
      '1技能二段飞狗突进接近敌人',
      '2技能近身真实伤害横扫，造成 0.75s 范围眩晕',
      hasSpellblade ? '立刻穿插普攻打出【强击】100%减速与高额物理伤害' : '立刻接普攻打出真实伤害',
      '3技能大招三道激光扫射压低血线并回复自身生命',
      '刷新或二段 1技能进行残血百分比斩杀收割'
    ];
  } else if (currentHero.cname === '赵云') {
    comboSteps = [
      '3技能大招跃空雷霆击飞目标，造成感电标记',
      '2技能连续刺出龙枪打出多段感电附加伤害并回血',
      '1技能向前冲锋减速追击',
      hasSpellblade ? '冲锋后接强化普攻打出【强击】爆发' : '接平A补足伤害',
      '被动低血量高额免伤支撑反打'
    ];
  } else if (currentHero.cname === '孙尚香') {
    comboSteps = [
      '1技能翻滚存枪并寻找安全输出身位',
      '2技能投掷红莲爆弹减速并破甲 25%',
      '打出 1技能强化远距离重炮普攻',
      hasSpellblade ? '触发【宗师强击】+20%移速拉扯拉开距离' : '接普通攻击持续走A',
      '3技能远程轰击收割残血逃生敌人'
    ];
  } else if (currentHero.cname === '诸葛亮') {
    comboSteps = [
      '1技能贴脸贴身打出三颗法球叠加印记',
      '2技能时空穿梭突进踩中敌人叠加二层印记并减速',
      '触发被动五颗谋略法球环绕自动轰击',
      hasSpellblade ? '穿插【巫术法杖】强化普攻压低血线' : '保持走位风筝',
      '3技能元气弹锁定残血目标，完成击杀并刷新被动法球'
    ];
  } else {
    comboSteps = [
      hasDash ? '1技能或突进技能接近目标起手' : '远程技能探草与消耗压低血线',
      hasCc ? '释放核心控制技能控制敌人，限制走位' : '释放输出技能打出第一波爆发',
      hasSpellblade ? '技能间隙穿插普通攻击，无缝触发【强击】伤害' : '走位穿插普攻补充伤害',
      '根据战场局势开启免伤/位移技能拉扯规避致命伤害',
      '释放大招锁定敌方核心进行集火或收割'
    ];
  }

  let comboHtml = '';
  comboSteps.forEach((step, idx) => {
    comboHtml += `
      <div class="synergy-combo-step">
        <span class="combo-step-num">${idx + 1}</span>
        <span>${step}</span>
      </div>
    `;
  });

  const bottomGridHtml = `
    <div class="synergy-bottom-grid">
      <div class="synergy-rating-card">
        <div class="synergy-section-title">
          <span>📊</span> 出装与英雄战术契合度评估
        </div>
        <div class="synergy-score-circle">
          <span class="synergy-score-big">${score}</span>
          <div>
            <div style="font-size: 14px; font-weight: 700; color: var(--color-green);">S+ 卓越级战术协同</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">被动特效与技能动作链契合度极高</div>
          </div>
        </div>
        <div class="synergy-radar-bars">
          <div class="synergy-radar-row">
            <span>爆发斩杀 (Burst)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: 92%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>技能周转 (CDR)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: ${Math.min(cappedCdr * 2.4, 100)}%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>持续拉扯 (Kiting)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: 85%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>生存容错 (Defense)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: 88%;"></div></div>
          </div>
          <div class="synergy-radar-row">
            <span>续航反打 (Sustain)</span>
            <div class="synergy-radar-track"><div class="synergy-radar-fill" style="width: 90%;"></div></div>
          </div>
        </div>
      </div>

      <div class="synergy-combo-card">
        <div class="synergy-section-title">
          <span>🎯</span> 实战黄金连招与团战打法思路
        </div>
        <div>
          ${comboHtml}
        </div>
      </div>
    </div>
  `;

  // 拼接全量内容
  container.innerHTML = `
    ${bannerHtml}
    <div>
      <div class="synergy-section-title">
        <span>📖</span> 英雄技能机制与当前出装冷却时间换算 (Dynamic CDR)
      </div>
      <div class="synergy-skills-grid">
        ${skillsCardsHtml}
      </div>
    </div>
    <div>
      <div class="synergy-section-title">
        <span>⚡</span> 装备唯一被动与英雄机制深度联动剖析
      </div>
      <div class="synergy-links-list">
        ${synergyLinksHtml}
      </div>
    </div>
    ${bottomGridHtml}
  `;
}

function copySynergyReport() {
  const heroName = currentHero.cname;
  const eff = currentSlots.map(s => s.item_name).join(' + ') || '无装备';
  const text = `### 【王者出装箱】英雄技能×出装联动战术分析报告\n- 英雄：${heroName} (${currentHero.lane} / ${currentHero.role})\n- 六神装：${eff}\n- 总造价：${document.getElementById('totalGold').innerText}\n- 战术亮点：技能冷却时间全面缩短，被动特效形成控制与爆发连招链闭环，实战表现极其强劲！\n- 报告来源：王者出装箱沙盒系统`;
  navigator.clipboard.writeText(text).then(() => {
    showToast("已成功复制联动战术分析报告至剪贴板！");
  }).catch(() => {
    prompt("请手动复制战术报告：", text);
  });
}

function renderItems() {
  const query = (document.getElementById('itemSearch').value || '').trim().toLowerCase();
  const container = document.getElementById('itemListContainer');
  container.innerHTML = '';

  const filtered = ITEMS_DATA.filter(it => {
    const matchCat = (currentItemFilter === '全部') || (it.category === currentItemFilter);
    const matchQuery = !query || it.item_name.toLowerCase().includes(query);
    return matchCat && matchQuery;
  });

  document.getElementById('itemCountBadge').innerText = `${filtered.length} 件装备`;

  filtered.forEach(it => {
    const inSlot = currentSlots.some(s => s.item_name === it.item_name);
    const card = document.createElement('div');
    card.className = `item-card ${inSlot ? 'equipped' : ''}`;
    card.onclick = () => addItem(it);
    // 标准静默原生浮层提示（不遮挡卡片）
    card.title = `${it.item_name} (${it.total_price || 0} G)\n${it.des1 || ''}\n${it.des2 || ''}`;

    // 格式化卡片内展示（所有的框大小完全一致，统一三段式苹果官网规范排版）
    const lines = (it.des1_lines && it.des1_lines.length > 0) ? it.des1_lines : (it.des1 ? it.des1.split(' ') : ['基础属性']);
    const line1 = lines[0] || '基础属性';
    const line2 = lines.slice(1).join(' · ') || (it.category || '基础件');

    const passiveClean = (it.des2 || '').replace(/唯一被动[：:-]/g, '').trim();
    const passivePillHtml = passiveClean 
      ? `<div class="item-passive-pill" title="${it.des2}">⚡ ${passiveClean}</div>` 
      : `<div class="item-passive-pill pill-subtle">${it.category || '基础装备'}</div>`;

    card.innerHTML = `
      <span class="item-equipped-badge">已装配</span>
      <div class="item-top">
        <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg" onerror="this.style.display='none'">
        <div class="item-meta">
          <div class="item-name">${it.item_name}</div>
          <div class="item-price-pill">${it.total_price || 0} G</div>
        </div>
      </div>
      <div class="item-body">
        <div class="item-stat-line item-stat-primary">${line1}</div>
        <div class="item-stat-line">${line2}</div>
      </div>
      ${passivePillHtml}
    `;
    container.appendChild(card);
  });
}

function renderSlots() {
  const grid = document.getElementById('slotsGrid');
  grid.innerHTML = '';
  document.getElementById('slotCount').innerText = `已选 ${currentSlots.length} / 6 件`;

  for (let i = 0; i < 6; i++) {
    const item = currentSlots[i];
    const slot = document.createElement('div');
    if (item) {
      slot.className = 'slot filled';
      slot.title = `点击卸下: ${item.item_name}`;
      slot.onclick = () => removeSlot(i);
      slot.innerHTML = `
        <img alt="${item.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${item.item_id}.jpg">
        <span class="slot-remove-badge">×</span>
      `;
    } else {
      slot.className = 'slot';
      slot.innerHTML = `<span class="slot-num">${i + 1}</span>`;
    }
    grid.appendChild(slot);
  }
}

function addItem(item) {
  if (currentSlots.length >= 6) {
    alert("局内神装上限仅限 6 格！请先点击右侧槽位中的装备进行卸下或替换。");
    return;
  }
  currentSlots.push(item);
  renderSlots();
  renderItems();
  recalculate();
}

function removeSlot(index) {
  currentSlots.splice(index, 1);
  renderSlots();
  renderItems();
  recalculate();
}

function resetSlots() {
  currentSlots = [];
  renderSlots();
  renderItems();
  recalculate();
}

// 核心计算与吞噬算法
function recalculate() {
  // 小件原料吞噬过滤
  const effectiveItems = [];
  const consumedNotes = [];
  for (let i = 0; i < currentSlots.length; i++) {
    const curr = currentSlots[i].item_name;
    let isConsumed = false;
    for (let j = i + 1; j < currentSlots.length; j++) {
      const later = currentSlots[j].item_name;
      const recipes = RECIPES_MAP[later] || [];
      if (recipes.includes(curr)) {
        isConsumed = true;
        consumedNotes.push(`原料【${curr}】已被大件【${later}】合成吞噬，属性已覆盖`);
        break;
      }
    }
    if (!isConsumed) effectiveItems.push(currentSlots[i]);
  }

  // 属性累加
  let totalGold = 0;
  let totals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, mp:0, crit:0, aspeed:0, cdr:0, percent_speed:0, flat_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce_flat:0, p_pierce_percent:0, m_pierce_flat:0, m_pierce_percent:0, has_hat:false };
  let bootsCounted = false;

  // 铭文加成汇总（支持自由混搭任意颗数，如 9 异变 + 1 纷争）
  let arcanaTotals = { atk:0, ap:0, pdef:0, mdef:0, hp:0, crit:0, crit_effect:0, aspeed:0, cdr:0, percent_speed:0, p_lifesteal:0, m_lifesteal:0, p_pierce_flat:0, m_pierce_flat:0, hp_regen:0 };
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    for (const [name, count] of Object.entries(map)) {
      if (count > 0 && ARCANA_DATA[name] && ARCANA_DATA[name].stats_1) {
        const s = ARCANA_DATA[name].stats_1;
        arcanaTotals.atk += (s.phys_atk || 0) * count;
        arcanaTotals.ap += (s.magic_atk || 0) * count;
        arcanaTotals.pdef += (s.phys_def || 0) * count;
        arcanaTotals.mdef += (s.magic_def || 0) * count;
        arcanaTotals.hp += (s.max_hp || 0) * count;
        arcanaTotals.crit += (s.crit_rate_pct || 0) * count;
        arcanaTotals.crit_effect += (s.crit_effect_pct || 0) * count;
        arcanaTotals.aspeed += (s.atk_speed_pct || 0) * count;
        arcanaTotals.cdr += (s.cd_reduction_pct || 0) * count;
        arcanaTotals.percent_speed += (s.move_speed_pct || 0) * count;
        arcanaTotals.p_lifesteal += (s.phys_vamp_pct || 0) * count;
        arcanaTotals.m_lifesteal += (s.magic_vamp_pct || 0) * count;
        arcanaTotals.p_pierce_flat += (s.phys_pierce || 0) * count;
        arcanaTotals.m_pierce_flat += (s.magic_pierce || 0) * count;
        arcanaTotals.hp_regen += (s.hp_regen || 0) * count;
      }
    }
  });
  // 消除浮点数精度累加误差
  for (let k in arcanaTotals) {
    arcanaTotals[k] = Math.round(arcanaTotals[k] * 10) / 10;
  }

  currentSlots.forEach(it => totalGold += (it.total_price || 0));

  effectiveItems.forEach(it => {
    const st = it.stats || {};
    totals.atk += st.atk || 0;
    totals.ap += st.ap || 0;
    totals.pdef += st.pdef || 0;
    totals.mdef += st.mdef || 0;
    totals.hp += st.hp || 0;
    totals.mp += st.mp || 0;
    totals.crit += st.crit || 0;
    totals.aspeed += st.aspeed || 0;
    totals.cdr += st.cdr || 0;
    totals.percent_speed += st.percent_speed || 0;
    totals.p_lifesteal += st.p_lifesteal || 0;
    totals.m_lifesteal += st.m_lifesteal || 0;
    totals.p_pierce_flat += st.p_pierce_flat || 0;
    totals.p_pierce_percent = Math.max(totals.p_pierce_percent, st.p_pierce_percent || 0);
    totals.m_pierce_flat += st.m_pierce_flat || 0;
    totals.m_pierce_percent = Math.max(totals.m_pierce_percent, st.m_pierce_percent || 0);
    if (it.item_name === '博学者之怒') totals.has_hat = true;

    if (BOOTS_MAP[it.item_name] && !bootsCounted) {
      totals.flat_speed = BOOTS_MAP[it.item_name];
      bootsCounted = true;
    }
  });

  const rawAp = totals.ap + arcanaTotals.ap;
  const finalAp = totals.has_hat ? Math.floor(rawAp * 1.3) : rawAp;
  const totalCdr = totals.cdr + arcanaTotals.cdr;
  const cappedCdr = Math.min(Math.floor(totalCdr), 40);

  // 英雄 15 级基础属性
  const b = currentHero.base_stats || { hp:[3200,7000], atk:[170,380], pdef:[100,400], mdef:[50,169], speed:370, aspeed:"+2.0%" };
  const bHp = b.hp[1];
  const bAtk = b.atk[1];
  const bPdef = b.pdef[1];
  const bMdef = b.mdef[1];
  const bSpeed = b.speed;
  const growthMatch = (b.aspeed || '+1.0%').match(/([\\d\\.]+)%/);
  const growthVal = growthMatch ? parseFloat(growthMatch[1]) : 1.0;
  const heroSelfAspeed = Math.floor(growthVal * 14);
  const totalAspeed = heroSelfAspeed + Math.floor(totals.aspeed) + Math.floor(arcanaTotals.aspeed);

  // 二次转化加成
  let extraPdef = 0;
  let extraMdef = 0;
  let extraPdefNote = "";
  let extraMdefNote = "";
  if (effectiveItems.some(i => i.item_name === '时之预言')) {
    const propVal = Math.min(Math.floor(finalAp * 0.1), 250);
    extraPdef += propVal; extraMdef += propVal;
    extraPdefNote = `(时之预言+${propVal}) `;
  }
  if (effectiveItems.some(i => i.item_name === '破魔刀')) {
    const pmVal = Math.min(Math.floor((bAtk + totals.atk + arcanaTotals.atk) * 0.5), 250);
    extraMdef += pmVal;
    extraMdefNote = `(破魔刀+${pmVal}) `;
  }

  const finalHp = bHp + totals.hp + arcanaTotals.hp;
  const totPdef = bPdef + totals.pdef + arcanaTotals.pdef + extraPdef;
  const totMdef = bMdef + totals.mdef + arcanaTotals.mdef + extraMdef;
  const pReduction = (totPdef / (totPdef + 602) * 100).toFixed(1);
  const mReduction = (totMdef / (totMdef + 602) * 100).toFixed(1);

  const totalSpeedPct = totals.percent_speed + arcanaTotals.percent_speed;
  const pspeedStr = totalSpeedPct > 0 ? totalSpeedPct.toFixed(1).replace(/\\.0$/, '') : '0';
  const calcSpeed = Math.floor((bSpeed + totals.flat_speed) * (1 + totalSpeedPct / 100));

  const totalCrit = Math.round((totals.crit + arcanaTotals.crit) * 10) / 10;
  const totalPhysPierce = Math.round((totals.p_pierce_flat + arcanaTotals.p_pierce_flat) * 10) / 10;
  const totalMagicPierce = Math.round((totals.m_pierce_flat + arcanaTotals.m_pierce_flat) * 10) / 10;
  const totalPhysVamp = Math.round((totals.p_lifesteal + arcanaTotals.p_lifesteal) * 10) / 10;
  const totalMagicVamp = Math.round((totals.m_lifesteal + arcanaTotals.m_lifesteal) * 10) / 10;

  // 渲染总金币
  document.getElementById('totalGold').innerText = `${totalGold.toLocaleString()} G`;
  
  // 渲染 Apple Health 风格属性面板 (基础 + 装备 + 铭文 复合精准呈现)
  const statsBox = document.getElementById('statsContainer');
  statsBox.innerHTML = `
    <!-- 生存健康面板 -->
    <div class="metric-section">
      <div class="metric-section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-green)" stroke-width="2.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
        生存与抗性指标
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终最大生命值</span>
          <span class="metric-sub">${bHp}基 + ${totals.hp}装 + ${arcanaTotals.hp}铭</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${finalHp.toLocaleString()}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">物理防御 (物抗)</span>
          <span class="metric-sub">${extraPdefNote}${bPdef}基 + ${totals.pdef}装 + ${arcanaTotals.pdef}铭 ｜ 免伤率 ${pReduction}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totPdef}</span>
          <div class="bar-track"><div class="bar-fill bar-fill-armor" style="width: ${Math.min(pReduction, 100)}%;"></div></div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">法术防御 (魔抗)</span>
          <span class="metric-sub">${extraMdefNote}${bMdef}基 + ${totals.mdef}装 + ${arcanaTotals.mdef}铭 ｜ 免伤率 ${mReduction}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totMdef}</span>
          <div class="bar-track"><div class="bar-fill bar-fill-marmor" style="width: ${Math.min(mReduction, 100)}%;"></div></div>
        </div>
      </div>
    </div>

    <!-- 进攻与爆发面板 -->
    <div class="metric-section">
      <div class="metric-section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-amber)" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
        输出与攻击强度
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终物理攻击</span>
          <span class="metric-sub">${bAtk}基 + ${totals.atk}装 + ${arcanaTotals.atk}铭</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${bAtk + totals.atk + arcanaTotals.atk}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终法术攻击</span>
          <span class="metric-sub">${totals.has_hat ? '含帽子+30% ｜ ' : ''}${totals.ap}装 + ${arcanaTotals.ap}铭</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val" style="color: ${finalAp > 0 ? 'var(--color-purple)' : 'inherit'};">${finalAp}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">暴击率 / 攻速总计</span>
          <span class="metric-sub">暴击(装${Math.floor(totals.crit)}+铭${Math.floor(arcanaTotals.crit)}) ｜ 攻速(成${heroSelfAspeed}+装${Math.floor(totals.aspeed)}+铭${Math.floor(arcanaTotals.aspeed)})</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totalCrit}% ｜ ${totalAspeed}%</span>
        </div>
      </div>
    </div>

    <!-- 机动与特殊属性 -->
    <div class="metric-section">
      <div class="metric-section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-blue)" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        机动、冷却与穿透
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">实战极限移速</span>
          <span class="metric-sub">(${bSpeed}+${totals.flat_speed}鞋) × (1+${pspeedStr}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${calcSpeed}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">冷却缩减</span>
          <span class="metric-sub">装+${Math.floor(totals.cdr)}% ｜ 铭+${Math.floor(arcanaTotals.cdr)}%${cappedCdr >= 40 ? ' (满冷缩)' : ''}</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${cappedCdr}%</span>
          <div class="bar-track"><div class="bar-fill bar-fill-cdr" style="width: ${(cappedCdr / 40 * 100)}%;"></div></div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">双穿透 (固定/百分比)</span>
          <span class="metric-sub">物穿 ${totalPhysPierce}点(${totals.p_pierce_percent}%) ｜ 魔穿 ${totalMagicPierce}点(${totals.m_pierce_percent}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-highlight">双抗穿透生效</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">续航吸血</span>
          <span class="metric-sub">物吸 ${totalPhysVamp}% (含铭+${arcanaTotals.p_lifesteal}%) ｜ 法吸 ${totalMagicVamp}% (含铭+${arcanaTotals.m_lifesteal}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totalPhysVamp || totalMagicVamp ? `${totalPhysVamp}% / ${totalMagicVamp}%` : '0%'}</span>
        </div>
      </div>
    </div>
  `;

  // 诊断互斥
  renderDiagnosis(effectiveItems, consumedNotes);
}

function renderDiagnosis(effectiveItems, consumedNotes) {
  const diagBox = document.getElementById('diagnoseContainer');
  diagBox.innerHTML = '';
  const effNames = effectiveItems.map(i => i.item_name);
  const issues = [];

  // 小件吞噬
  consumedNotes.forEach(note => issues.push({ type: 'info', text: note }));

  // 强击
  const qj = effNames.filter(n => ["宗师之力", "冰痕之握", "巫术法杖", "光辉之剑"].includes(n));
  if (qj.length > 1) issues.push({ type: 'warn', text: `【强击被动互斥】同时出了 ${qj.join(' 与 ')}，伤害仅生效一件！` });

  // 双鞋
  const boots = effNames.filter(n => BOOTS_MAP[n]);
  if (boots.length > 1) issues.push({ type: 'warn', text: `【神速双鞋互斥】同时出了 ${boots.join(' 与 ')}，移动速度不叠加！` });

  // 主动共存
  const actives = effNames.filter(n => ACTIVE_ITEMS.includes(n));
  if (actives.length > 1) issues.push({ type: 'warn', text: `【多主动按键共存】出了 ${actives.join(' 与 ')}，局内默认只能设置 1 个主动按键！` });

  // 打野惩击
  const jungles = effNames.filter(n => JUNGLE_ITEMS.includes(n));
  if (jungles.length > 0) issues.push({ type: 'warn', text: `【召唤师技能提示】出了打野刀（${jungles.join('、')}），局内必须携带【惩击】方可购买！` });

  if (issues.length === 0) {
    diagBox.innerHTML = `
      <div class="diag-card diag-card-pass">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <span>当前 6 件成装无被动互斥与按键冲突，契合度 100%！</span>
      </div>`;
  } else {
    issues.forEach(iss => {
      const el = document.createElement('div');
      el.className = `diag-card ${iss.type === 'warn' ? 'diag-card-warn' : (iss.type === 'info' ? 'diag-card-info' : 'diag-card-pass')}`;
      const icon = iss.type === 'warn' 
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
      el.innerHTML = `${icon}<span>${iss.text}</span>`;
      diagBox.appendChild(el);
    });
  }
}

function exportMarkdown() {
  if (currentSlots.length === 0) {
    alert("请先选择至少 1 件装备再导出！");
    return;
  }
  const eff = currentSlots.map(s => s.item_name).join(' + ');
  const arcParts = [];
  ['red', 'green', 'blue'].forEach(col => {
    const map = currentArcana[col] || {};
    const sub = Object.entries(map).filter(([_, c]) => c > 0).map(([n, c]) => `${c}${n}`).join('+');
    if (sub) arcParts.push(sub);
  });
  const arcStr = arcParts.join(' ｜ ') || '无铭文';
  const text = `### 自定义配装方案：${currentHero.cname}\\n- 英雄定位：${currentHero.lane} / ${currentHero.role}\\n- 铭文搭配：${arcStr}\\n- 装备配置：${eff}\\n- 总金币造价：${document.getElementById('totalGold').innerText}\\n- 导出来源：王者出装箱 ｜ 局内六神装配装沙盒`;
  navigator.clipboard.writeText(text).then(() => {
    alert("已将配装方案复制到剪贴板！可直接粘贴至 NotebookLM。");
  }).catch(() => {
    prompt("请手动复制配装方案：", text);
  });
}
</script>
</body>
</html>
"""
