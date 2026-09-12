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
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚔️</text></svg>">
<title>王者荣耀局内六神装配装沙盒 ｜ Apple HIG Edition</title>
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

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-blue), #004fb0);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
}

.brand-titles h1 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.015em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 980px;
  background: var(--color-blue-bg);
  color: var(--color-blue);
  letter-spacing: 0.02em;
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
  padding: 4px 16px 16px 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(185px, 1fr));
  gap: 12px;
  align-content: start;
}

.item-card {
  background: var(--apple-card);
  border: 1px solid var(--apple-border);
  border-radius: 16px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  box-shadow: var(--card-shadow);
  min-height: 98px;
}

.item-card:hover {
  background: var(--apple-card-hover);
  border-color: var(--apple-border-hover);
  transform: translateY(-2px);
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
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.item-meta {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.item-desc {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 8px;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  padding: 10px 14px;
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

::-webkit-scrollbar-thumb:hover {
  background: var(--color-blue);
}
</style>
</head>
<body>

<!-- 苹果风格顶部导航 -->
<header>
  <div class="brand-wrapper">
    <div class="brand-icon">⚔️</div>
    <div class="brand-titles">
      <h1>王者荣耀六神装配装沙盒 <span class="brand-badge">Apple HIG Edition</span></h1>
      <p>动态数值演算 ｜ 小件吞噬规则 ｜ 双向属性转化 ｜ 装备互斥诊断</p>
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
      <span class="panel-badge" id="slotCount">已选 0 / 6 件</span>
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

<script>
// === 静态内嵌数据 ===
const HEROES_DATA = __HEROES_DATA_PLACEHOLDER__;
const ITEMS_DATA = __ITEMS_DATA_PLACEHOLDER__;
const RECIPES_MAP = __RECIPES_MAP_PLACEHOLDER__;
const BOOTS_MAP = __BOOTS_MAP_PLACEHOLDER__;
const ACTIVE_ITEMS = __ACTIVE_ITEMS_PLACEHOLDER__;
const JUNGLE_ITEMS = __JUNGLE_ITEMS_PLACEHOLDER__;

// === 状态机 ===
let currentHero = HEROES_DATA[0] || {};
let currentSlots = [];
let currentHeroFilter = "全部";
let currentItemFilter = "全部";

window.onload = () => {
  // 读取用户本地保存的主题偏好（默认浅色）
  const savedTheme = localStorage.getItem('apple_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeBtnIcon(savedTheme);

  updateSpotlight();
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

function selectHero(hero) {
  currentHero = hero;
  updateSpotlight();
  renderHeroes();
  recalculate();
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
    card.innerHTML = `
      <span class="item-equipped-badge">已装配</span>
      <div class="item-top">
        <img class="item-icon" alt="${it.item_name}" src="https://game.gtimg.cn/images/yxzj/img201606/itemimg/${it.item_id}.jpg" onerror="this.style.display='none'">
        <div class="item-meta">
          <div class="item-name">${it.item_name}</div>
          <div class="item-price-pill">${it.total_price || 0} G</div>
        </div>
      </div>
      <div class="item-desc">${it.des1 || '基础装备'}</div>
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

  const finalAp = totals.has_hat ? Math.floor(totals.ap * 1.3) : totals.ap;
  const cappedCdr = Math.min(Math.floor(totals.cdr), 40);

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
  const totalAspeed = heroSelfAspeed + Math.floor(totals.aspeed);

  // 二次转化加成
  let extraPdef = 0;
  let extraMdef = 0;
  let extraPdefNote = "";
  let extraMdefNote = "";
  if (effectiveItems.some(i => i.item_name === '时之预言')) {
    const propVal = Math.min(Math.floor(finalAp * 0.1), 250);
    extraPdef += propVal; extraMdef += propVal;
    extraPdefNote = `(含时之预言+${propVal}) `;
    extraMdefNote = `(含时之预言+${propVal}) `;
  }
  if (effectiveItems.some(i => i.item_name === '破魔刀')) {
    const pmVal = Math.min(Math.floor((bAtk + totals.atk) * 0.5), 250);
    extraMdef += pmVal;
    extraMdefNote = `(含破魔刀+${pmVal}) `;
  }

  const totPdef = bPdef + totals.pdef + extraPdef;
  const totMdef = bMdef + totals.mdef + extraMdef;
  const pReduction = (totPdef / (totPdef + 602) * 100).toFixed(1);
  const mReduction = (totMdef / (totMdef + 602) * 100).toFixed(1);

  const pspeedStr = totals.percent_speed > 0 ? totals.percent_speed.toFixed(1).replace(/\\.0$/, '') : '0';
  const calcSpeed = Math.floor((bSpeed + totals.flat_speed) * (1 + totals.percent_speed / 100));

  // 渲染总金币
  document.getElementById('totalGold').innerText = `${totalGold.toLocaleString()} G`;
  
  // 渲染 Apple Health 风格属性面板
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
          <span class="metric-sub">${bHp} 基础 + ${totals.hp} 装备</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${(bHp + totals.hp).toLocaleString()}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">物理防御 (物抗)</span>
          <span class="metric-sub">${extraPdefNote}免伤率 ${pReduction}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totPdef}</span>
          <div class="bar-track"><div class="bar-fill bar-fill-armor" style="width: ${Math.min(pReduction, 100)}%;"></div></div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">法术防御 (魔抗)</span>
          <span class="metric-sub">${extraMdefNote}免伤率 ${mReduction}%</span>
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
          <span class="metric-sub">${bAtk} 基础 + ${totals.atk} 装备</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${bAtk + totals.atk}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">最终法术攻击</span>
          <span class="metric-sub">${totals.has_hat ? '含博学者之怒+30%加成' : '法术装备总和'}</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val" style="color: ${finalAp > 0 ? 'var(--color-purple)' : 'inherit'};">${finalAp}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">暴击率 / 攻速总计</span>
          <span class="metric-sub">成长+${heroSelfAspeed}% ｜ 装备+${Math.floor(totals.aspeed)}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${Math.floor(totals.crit)}% ｜ ${totalAspeed}%</span>
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
          <span class="metric-sub">${totals.cdr >= 40 ? '⚡ 达到 40% 极限制动' : `还差 ${40 - cappedCdr}% 达到满冷缩`}</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${cappedCdr}%</span>
          <div class="bar-track"><div class="bar-fill bar-fill-cdr" style="width: ${(cappedCdr / 40 * 100)}%;"></div></div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">双穿透 (固定/百分比)</span>
          <span class="metric-sub">物穿 ${totals.p_pierce_flat}点(${totals.p_pierce_percent}%) ｜ 魔穿 ${totals.m_pierce_flat}点(${totals.m_pierce_percent}%)</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-highlight">双抗穿透生效</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label-group">
          <span class="metric-name">续航吸血</span>
          <span class="metric-sub">物理吸血 ${totals.p_lifesteal}% ｜ 法术吸血 ${totals.m_lifesteal}%</span>
        </div>
        <div class="metric-value-group">
          <span class="metric-val">${totals.p_lifesteal || totals.m_lifesteal ? `${totals.p_lifesteal}% / ${totals.m_lifesteal}%` : '0%'}</span>
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
  const text = `### 自定义出装方案：${currentHero.cname}\\n- 英雄定位：${currentHero.lane} / ${currentHero.role}\\n- 装备配置：${eff}\\n- 总金币造价：${document.getElementById('totalGold').innerText}\\n- 导出来源：王者荣耀沙盒模拟器 (Apple HIG Edition)`;
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
