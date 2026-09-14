# -*- coding: utf-8 -*-
"""
受控补丁包统一导出模块 (Controlled Patches Package)
严格遵守 AGENTS.md 规范：横向解耦为 reworked_heroes, new_heroes, variants。
对外保持 100% 向后兼容导出。
"""

from .reworked_heroes import (
    ZHAOYUN_HERO_PATCH,
    NEZHA_HERO_PATCH,
    DAMO_HERO_PATCH,
    YUNZHONGJUN_HERO_PATCH,
    ZHENJI_HERO_PATCH,
    PANGU_HERO_PATCH,
)

from .new_heroes import (
    DASIMING_HERO_PATCH,
    DASIMING_ARCANA_PATCH,
    AOYIN_HERO_PATCH,
    SHAOSIYUAN_HERO_PATCH,
    YING_HERO_PATCH,
    YUANLIU_TANK_HERO_PATCH,
    YUANLIU_MAGE_HERO_PATCH,
)

from .variants import (
    YANGJIAN_HERO_PATCH,
    CANG_HERO_PATCH,
)

# 全局受控重做技能补丁统一注册字典
REWORKED_HERO_SKILLS_PATCHES = {
    "赵云": ZHAOYUN_HERO_PATCH,
    "哪吒": NEZHA_HERO_PATCH,
    "达摩": DAMO_HERO_PATCH,
    "云中君": YUNZHONGJUN_HERO_PATCH,
    "甄姬": ZHENJI_HERO_PATCH,
    "盘古": PANGU_HERO_PATCH,
    "杨戬": YANGJIAN_HERO_PATCH,
    "大司命": DASIMING_HERO_PATCH,
    "敖隐": AOYIN_HERO_PATCH,
    "少司缘": SHAOSIYUAN_HERO_PATCH,
    "影": YING_HERO_PATCH,
    "苍": CANG_HERO_PATCH,
    "元流之子(坦克)": YUANLIU_TANK_HERO_PATCH,
    "元流之子(法师)": YUANLIU_MAGE_HERO_PATCH,
}
