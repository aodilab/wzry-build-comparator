# 王者荣耀全维度结构化知识库与推演沙盒 (Honor of Kings Knowledge Base Pipeline)

[![Site Status](https://img.shields.io/badge/Production-wzry.aodilab.com-0071e3?style=flat&logo=cloudflare)](https://wzry.aodilab.com)
[![WeChat MiniProgram](https://img.shields.io/badge/WeChat-王者出装箱-07c160?style=flat&logo=wechat)](https://wzry.aodilab.com)
[![Season](https://img.shields.io/badge/Season-S45%20月照长安-blueviolet?style=flat)](https://wzry.aodilab.com)
[![Heroes](https://img.shields.io/badge/Heroes-133%20全量国服基准-orange?style=flat)](https://wzry.aodilab.com)

本项目是专为 **Kimi、DeepSeek、豆包、腾讯元宝** 以及 **Google Gemini NotebookLM** 等大模型 RAG（检索增强生成）设计的**王者荣耀全维度结构化知识体系与局内推演沙盒工程**。

从王者荣耀官方接口实时采集、严格清洗并拓扑关联 133 位国服英雄、121 件全量装备双向合成路径、五级铭文库及 S45 最新赛季战场机制，生成高保真、零幻觉的 Markdown 知识库与单文件推演沙盒。

> 🌐 **官方 Web 在线推演沙盒**：[https://wzry.aodilab.com](https://wzry.aodilab.com)（Cloudflare 全球 CDN 托管，支持深层路由直达）  
> 📦 **官方数字交付提货门户**：[https://wzry.aodilab.com/download](https://wzry.aodilab.com/download)  
> 📱 **微信原生小程序【王者出装箱】**：微信搜索「**王者出装箱**」，随时随地畅享配装推演与满级属性演算。

---

## 🌟 核心架构与功能演进

本项目的配装推演沙盒已全面重构为**两段式极简工作台**，彻底告别单页挤压逻辑：

### 1. 两段式流转工作台 (Two-Stage Studio Flow)
- **阶段一：选英雄大厅 (Hero Hall)**
  - 收录 133 位国服基准英雄（包含第 133 位新英雄「王维」及变异机制）；
  - 5 大游戏内真实职业与官方分路检索，支持拼音/汉字实时模糊过滤；
  - **实战分路快捷栏 (Lane Bar & Picker)**：支持在进入推演室前先定对局分路（如孙策选打野/对抗路，阿古朵选打野/发育路）。
- **阶段二：专属方案与推演室 (Hero Studio)**
  - 顶部动态展示当前英雄专属分路、15 级满级基准属性与官方专属推荐方案；
  - **六神装自由装配槽**：支持动态添加、点击卸下、一键清空、一键加载官方国服神装；
  - **30 颗全量五级铭文自由混搭 (Arcana HIG Sheet)**：红/蓝/绿三色支持任意颗数自由微调混搭（如 7异变 3祸源 10鹰眼 5狩猎 5隐匿），属性实时精准累加；
  - **满级属性实时演算面板**：生命、物攻、法强、物理/法术防御、移速公式、攻速阈值成长及综合物理免伤率；
  - **被动互斥与规则诊断**：自动诊断【强击】互斥、【神速】双鞋减速失效、【打野刀惩击绑定】与【唯一被动】同名合并。

### 2. 深度战术协同与算分引擎 (Tactical Synergy Engine)
- **多维度战术协同简报**：针对已选装备与铭文，自动推演输出倾向、防御韧性、续航与功能性得分；
- **物法错位惩罚与核心装协同**：法师出纯物理或射手出纯法术自动触发错位衰减；
- **全英雄实战克制与阵容搭档图谱**：精准展示当前英雄的最佳搭档、对线克制与天敌反制；
- **实战连招口诀与操作解析**：按对局情境（起手式、消耗连招、蹲草秒人、团战进场）拆解技能释放时序与操作细节。

### 3. Apple 银白极简设计美学与全端响应
- 遵循 Apple 官网级纯白银灰极简美学（`#f5f5f7` 底色 + 纯白微阴影卡片），支持浅色 / 深色外观一键切换；
- 移动端适配：768px 以下自动开启移动端原生卡片与底部抽屉交互；
- **白帽技术 SEO 规范**：集成 Schema.org JSON-LD 结构化数据、Apple 极简页脚速查大典与深层直达参数（`?hero=105` 或 `?hero=孙悟空`）。

---

## 🚀 快速上手与 CLI 构建调度

本项目统一采用 `build.py` 调度总入口进行多端构建：

### 1. 环境准备
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# 安装核心依赖
pip install -r requirements.txt
```

### 2. 构建调度命令
```bash
# 一键编译全套 Markdown 知识库与本地沙盒网页
python build.py --all

# 编译 Web 推演沙盒 (生成 sandbox.html、index.html 与 dist_pages/index.html)
python build.py --sandbox

# 构建 SEO 资产 (自动化生成 robots.txt 与 sitemap.xml)
python build.py --seo

# 构建全分路出装与铭文出版级矢量 PDF (基于 Playwright 高清渲染)
python build.py --pdf

# 构建微信小程序模板页面与代码
python build.py --miniprogram
```

### 3. 本地推演沙盒体验
直接在浏览器中双击打开根目录下的 `sandbox.html` 即可离线体验完整配装推演沙盒，无需任何后端服务器支撑。

---

## 📂 交付产物矩阵

### 1. RAG 核心知识库 (`output/`)
专供 **Google Gemini NotebookLM、Kimi、DeepSeek** 导入的纯净 Markdown 文件，全选拖入即可构建高保真王者战术私域知识库：

1. **`01_王者荣耀_全英雄技能数值与等级成长库.md`**：133 位英雄面板、Lv1-Lv6 冷却与消耗阶梯、变异技能机制。
2. **`02_王者荣耀_英雄战术克制与阵容搭档拓扑.md`**：最佳体系搭配、对线优势克制、反制天敌战术分析。
3. **`03_王者荣耀_五大分路定位与实战出装思路.md`**：各分路打法思路、官方国服出装搭配与满级面板推演。
4. **`04_王者荣耀_全装备属性与合成升级图谱.md`**：121 件全装备双向合成拓扑树、被动唯一性与 S45 平衡调整。
5. **`05_王者荣耀_全铭文图鉴与英雄搭配方案.md`**：30 颗全量五级铭文数值图鉴与 133 位英雄官方推荐套组。
6. **`06_王者荣耀_峡谷战场机制与宏观运营规则.md`**：S45 赛季“月照长安”机制、雾行千山技能、野区视野精灵规则。
7. **`07_王者荣耀_S45官方推荐全英雄全分路出装与铭文大全.md`**：133 位英雄官方全分路出装、铭文与装备标签全量大图鉴。
8. **`08_王者荣耀_全英雄实战连招口诀与操作解析大全.md`**：全英雄起手技能、连招节奏口诀、团战切入与技能打断全解。

### 2. 线上发布与 CDN 交付层 (`dist_pages/`)
Cloudflare 静态托管发布目录，通过 `npx wrangler deploy` 实现秒级全球无缝更新。

### 3. 出版物交付层 (`output/pdf/` 与 `taobao/`)
Playwright 高清驱动的矢量出版级全彩数字战术手册。

---

## 🏗️ 架构拓扑规范

遵循 `AGENTS.md` 架构总纲中的单一职责与认知阈值约束（业务源码 ≤ 350 行，配置 ≤ 300 行）：

```text
Honor of Kings/
├── AGENTS.md                  # 架构总纲与求真反迎合最高准则 (SSOT)
├── README.md                  # 项目使用指南与交付说明
├── build.py                   # 统一构建 CLI 调度总入口
├── wrangler.json              # 线上交付端网络配置 (wzry.aodilab.com)
├── config/                    # [配置与静态字典] 英雄注册表、装备合成树、补丁包
│   └── patches/               # 英雄重做/新英雄/变态分支解耦补丁包
├── src/                       # [核心源码] HTTP 通信、清洗治理、多端构建流水线
│   ├── core/                  # 网络层 http.py、清洗 cleaner.py、校验 hero_validator.py
│   └── builders/              # 知识库、沙盒、PDF 与小程序多端构建流水线
├── templates/                 # [多端解耦组件模板] 模块化 CSS / JS / HTML
│   ├── sandbox/               # 沙盒布局、样式、算分引擎、铭文模态框组件
│   └── pdf/                   # 出版物矢量排版样式与模板
├── output/                    # [交付层] 专供 RAG 切片分析的纯净 Markdown 与矢量 PDF
└── dist_pages/                # [发布层] Cloudflare 线上交付网络资产
```

---

<a id="sponsor"></a>
## ☕ 支持与赞助 (Sponsor)

如果本项目对你的游戏理解、NotebookLM 知识库搭建或局内对局决策有所帮助，欢迎赞助支持！  
你的支持是持续维护国服最新赛季数据、保障算法流水线精度的最大动力。

<div align="center">
  <img src="assets/sponsor_wechat.jpg" width="220" style="border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);" alt="微信赞助收款码">
  <p style="font-size: 13px; color: #666; margin-top: 8px;"><strong>微信扫码支持（开发者：Aodi）</strong></p>
</div>
