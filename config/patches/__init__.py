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
    WANGWEI_HERO_PATCH,
    WANGWEI_ARCANA_PATCH,
)

from .variants import (
    YANGJIAN_HERO_PATCH,
    CANG_HERO_PATCH,
)

from .s45_heroes_patch import (
    NIUMO_HERO_PATCH,
    GUANYU_HERO_PATCH,
    LIBAI_HERO_PATCH,
    MENGYA_HERO_PATCH,
    XIAHOUDUN_HERO_PATCH,
    KONGKONGER_HERO_PATCH,
    LUBU_HERO_PATCH,
)

from .hero_builds_patch import HERO_BUILDS_PATCHES
from .hero_arcana_patch import HERO_ARCANA_PATCHES
from .hero_relations_patch import HERO_RELATIONS_PATCHES

# 补齐大司命已有补丁到统一字典
if "大司命" not in HERO_BUILDS_PATCHES:
    HERO_BUILDS_PATCHES["大司命"] = DASIMING_HERO_PATCH.get("equips", [])
if "大司命" not in HERO_ARCANA_PATCHES:
    HERO_ARCANA_PATCHES["大司命"] = DASIMING_ARCANA_PATCH
if "大司命" not in HERO_RELATIONS_PATCHES:
    HERO_RELATIONS_PATCHES["大司命"] = DASIMING_HERO_PATCH.get("relations", {})

# 补齐王维已有补丁到统一字典
if "王维" not in HERO_BUILDS_PATCHES:
    HERO_BUILDS_PATCHES["王维"] = WANGWEI_HERO_PATCH.get("equips", [])
if "王维" not in HERO_ARCANA_PATCHES:
    HERO_ARCANA_PATCHES["王维"] = WANGWEI_ARCANA_PATCH
if "王维" not in HERO_RELATIONS_PATCHES:
    HERO_RELATIONS_PATCHES["王维"] = WANGWEI_HERO_PATCH.get("relations", {})

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
    "王维": WANGWEI_HERO_PATCH,
    "牛魔": NIUMO_HERO_PATCH,
    "关羽": GUANYU_HERO_PATCH,
    "李白": LIBAI_HERO_PATCH,
    "蒙犽": MENGYA_HERO_PATCH,
    "夏侯惇": XIAHOUDUN_HERO_PATCH,
    "空空儿": KONGKONGER_HERO_PATCH,
    "吕布": LUBU_HERO_PATCH,
}


