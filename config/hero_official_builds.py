# -*- coding: utf-8 -*-
"""
王者荣耀 133 位国服正式服英雄官方出装与铭文字典 (SSOT Loader)
静态海量数据解耦存储于 config/official_builds_data.json，保持 100% 向后兼容导出。
"""
import json
import os

_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "official_builds_data.json")

with open(_DATA_FILE, "r", encoding="utf-8") as _f:
    OFFICIAL_HERO_BUILDS = json.load(_f)


def save_official_hero_builds(database: dict):
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
