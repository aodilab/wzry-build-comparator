# -*- coding: utf-8 -*-
"""王者荣耀开源知识库项目 - 基础全局配置"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

DOC_HERO_SKILLS_NAME = "01_王者荣耀_全英雄技能数值与等级成长库.md"
DOC_HERO_RELATIONS_NAME = "02_王者荣耀_英雄战术克制与阵容搭档拓扑.md"
DOC_HERO_BUILDS_NAME = "03_王者荣耀_五大分路定位与战术流派指南.md"
DOC_ITEMS_NAME = "04_王者荣耀_全装备属性与合成升级图谱.md"
DOC_ARCANA_NAME = "05_王者荣耀_全铭文图鉴与英雄搭配方案.md"
DOC_RULES_NAME = "06_王者荣耀_峡谷战场机制与宏观运营规则.md"

URL_HERO_LIST = "https://pvp.qq.com/web201605/js/herolist.json"
URL_ITEM_LIST = "https://pvp.qq.com/web201605/js/item.json"
URL_MING_LIST = "https://pvp.qq.com/web201605/js/ming.json"
HERO_DETAIL_BASE_URL = "https://pvp.qq.com/web201605/herodetail/"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ROLE_MAP = {
    1: "战士",
    2: "法师",
    3: "坦克",
    4: "刺客",
    5: "射手",
}

LANE_MAP = {
    "战士": "对抗路",
    "坦克": "对抗路/游走",
    "法师": "中路/游走",
    "刺客": "打野",
    "射手": "发育路",
}

COLOR_MAP = {
    "red": "红色",
    "yellow": "蓝色",
    "blue": "绿色",
}
