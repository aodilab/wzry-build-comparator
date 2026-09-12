# 王者荣耀全维度结构化知识库 (Honor of Kings Knowledge Base Pipeline)

本项目是专为 **Google Gemini NotebookLM** 及大模型 RAG（检索增强生成）设计的**王者荣耀结构化知识库工程**。

从王者荣耀官方接口实时采集、清洗并拓扑关联全量英雄、装备合成路径、铭文搭配及最新赛季战场运营机制，生成高保真、零幻觉的 Markdown 知识库。

> 🌐 **在线配装沙盒（免安装，浏览器直开）**：[https://13253374290.github.io/wzry-knowledge-base/](https://13253374290.github.io/wzry-knowledge-base/)

---

## 🚀 快速上手

### 1. 环境准备
确保已安装 Python 3.8+，并安装基础依赖：
```bash
pip install -r requirements.txt
```

### 2. 一键构建全量知识库与本地配装沙盒
运行统一构建入口，生成所有知识库至 `output/` 目录并生成本地配装沙盒网页：
```bash
python build.py --all
```

### 3. 本地可视化六神装配装沙盒网页 (`sandbox.html`)
双击根目录下的 `sandbox.html` 即可在浏览器中离线打开：
- 🎮 实时选择 132 位国服英雄，点选装备放入 6 格生效栏；
- ⚡ 实时动态演算：总金币造价、小件吞噬过滤、15 级终极面板（攻/防/血/移速公式/攻速成长/免伤率）；
- 🔍 动态诊断：【强击】互斥、【神速】双鞋冲突、【主动技能按键共存】、【打野刀惩击绑定】；
- 📋 一键复制当前配装方案为 Markdown，直接贴入 NotebookLM。

单独生成沙盒网页：
```bash
python build.py --sandbox        # 快速编译生成单文件 sandbox.html
```

### 4. 分模块按需构建
```bash
python build.py --skills         # 仅构建全英雄技能数值与等级成长库 (包含基础四维)
python build.py --relations      # 仅构建英雄战术克制与阵容搭档拓扑
python build.py --builds         # 仅构建五大分路定位与实战出装思路
python build.py --item           # 仅构建装备属性与合成拓扑树
python build.py --arcana         # 仅构建全铭文图鉴与英雄推荐搭配
python build.py --rules          # 仅构建峡谷战场机制与宏观运营规则
```

---

## 📂 知识库交付产物 (`output/`)

生成的文件采用纯中文与数字序号命名，可**直接全选拖入 Google NotebookLM**，在侧边栏 Sources 中自动保持最佳顺序：

1. **`01_王者荣耀_全英雄技能数值与等级成长库.md`**：132 英雄基础四维属性、全技能 Lv1-Lv6 冷却阶梯、消耗阶梯、基础成长线、加成公式。
2. **`02_王者荣耀_英雄战术克制与阵容搭档拓扑.md`**：最佳搭档体系联动、压制优势对局、被压制反制天敌分析。
3. **`03_王者荣耀_五大分路定位与实战出装思路.md`**：按对抗路、打野、中路、发育路、游走五大分路，官方推荐出装与推荐思路。
4. **`04_王者荣耀_全装备属性与合成升级图谱.md`**：装备基础属性、合成配方路径树、可升级神装方向、唯一被动效果。
5. **`05_王者荣耀_全铭文图鉴与英雄搭配方案.md`**：五级铭文图鉴、全英雄推荐铭文组、30颗满配总加成计算。
6. **`06_王者荣耀_峡谷战场机制与宏观运营规则.md`**：兵线交汇规律、辅助/打野游击机制、远古生物羁绊、防御塔机制。

---

## 🏗️ 项目架构

```text
Honor of Kings/
├── AGENTS.md                  # 架构宪法与行为准则（含求真反迎合最高准则）
├── README.md                  # 项目使用指南与交付说明
├── .gitignore                 # Git 忽略配置（缓存、虚拟环境与临时脚本）
├── build.py                   # 全局统一构建 CLI 入口
├── requirements.txt           # 基础运行依赖
├── config/                    # [配置与静态字典] URL、装备合成树、新英雄补丁
├── src/                       # [核心源码] HTTP 通信、清洗工具、4 大领域 Builder
└── output/                    # [交付产物] 专供 NotebookLM 导入的 Markdown 文件
```

---

## 📖 研发守则

详细的架构分层约束、受控 Patch 补丁机制及 AI 协同认知阈值规范，请参阅 [AGENTS.md](AGENTS.md)。

---

<a id="sponsor"></a>
## ☕ 支持与赞助 (Sponsor)

如果本项目对你的游戏理解、NotebookLM 探索或数值研究有所帮助，欢迎请作者喝杯冰可乐 🥤！  
你的支持是持续维护国服最新赛季数据、优化算法流水线的最大动力。

<div align="center">
  <img src="assets/sponsor_wechat.jpg" width="220" style="border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);" alt="微信赞助收款码">
  <p style="font-size: 13px; color: #666; margin-top: 8px;"><strong>微信扫码支持（开发者：孙奥迪）</strong></p>
</div>

