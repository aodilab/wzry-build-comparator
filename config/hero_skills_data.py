# -*- coding: utf-8 -*-
"""
王者荣耀 133 位国服正式服英雄全技能数值与等级成长真值字典 (SSOT Loader)
静态海量数据解耦存储于 config/hero_skills_data.json，保持 100% 向后兼容导出。
"""
import json
import os

_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hero_skills_data.json")

with open(_DATA_FILE, "r", encoding="utf-8") as _f:
    HERO_SKILLS_DATA = json.load(_f)


def save_hero_skills_data(database: dict):
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
