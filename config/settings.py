# -*- coding: utf-8 -*-
"""
王者荣耀知识库项目 - 基础全局配置
专为 Gemini NotebookLM 优化 6 大战术对局矩阵与中文命名
"""
import os

# 项目路径定义
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Gemini NotebookLM 6 大战术核心交付物命名 (带序号严格排序)
DOC_HERO_SKILLS_NAME = "01_王者荣耀_全英雄技能数值与等级成长库.md"
DOC_HERO_RELATIONS_NAME = "02_王者荣耀_英雄战术克制与阵容搭档拓扑.md"
DOC_HERO_BUILDS_NAME = "03_王者荣耀_五大分路定位与实战出装思路.md"
DOC_ITEMS_NAME = "04_王者荣耀_全装备属性与合成升级图谱.md"
DOC_ARCANA_NAME = "05_王者荣耀_全铭文图鉴与英雄搭配方案.md"
DOC_RULES_NAME = "06_王者荣耀_峡谷战场机制与宏观运营规则.md"

# 官方 API 接口地址
URL_HERO_LIST = "https://pvp.qq.com/web201605/js/herolist.json"
URL_ITEM_LIST = "https://pvp.qq.com/web201605/js/item.json"
URL_MING_LIST = "https://pvp.qq.com/web201605/js/ming.json"
HERO_DETAIL_BASE_URL = "https://pvp.qq.com/web201605/herodetail/"

# HTTP 通用请求头
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 职业代码映射
ROLE_MAP = {
    1: "战士",
    2: "法师",
    3: "坦克",
    4: "刺客",
    5: "射手",
    6: "辅助"
}

# 五大常规分路映射 (主定位对应分路)
LANE_MAP = {
    "战士": "对抗路",
    "坦克": "对抗路/游走",
    "法师": "中路",
    "刺客": "打野",
    "射手": "发育路",
    "辅助": "游走"
}

# 铭文颜色映射
COLOR_MAP = {
    "red": "红色",
    "yellow": "蓝色",
    "blue": "绿色"
}
