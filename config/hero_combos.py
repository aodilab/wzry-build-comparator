# -*- coding: utf-8 -*-
"""
王者荣耀全英雄实战连招与机制接口模块
读取 config/hero_combos.json 权威连招库
严格遵守 AGENTS.md 约束 (<= 100 行)
"""
import os
import json

_DATA_PATH = os.path.join(os.path.dirname(__file__), "hero_combos.json")
_COMBOS_CACHE = None

def _load_combos():
    global _COMBOS_CACHE
    if _COMBOS_CACHE is None:
        if os.path.exists(_DATA_PATH):
            with open(_DATA_PATH, "r", encoding="utf-8") as f:
                _COMBOS_CACHE = json.load(f)
        else:
            _COMBOS_CACHE = {}
    return _COMBOS_CACHE

def get_hero_combos(hero_name: str) -> list:
    """获取指定英雄的连招列表"""
    data = _load_combos()
    return data.get(hero_name, [])

def get_all_combos() -> dict:
    """获取全量 133 英雄连招字典"""
    return _load_combos().copy()
