# -*- coding: utf-8 -*-
"""
新英雄与重做英雄权威推荐铭文补丁库 (Hero Arcana Patch)
针对官方 2016 静态站缺失铭文数据的英雄，提供满配 30 颗五级铭文权威方案与实战搭配思路。
严格保证铭文属性真实准确，支持 30 颗满配属性无缝合成。
"""

M_YIBIAN = {"id": "1504", "name": "异变", "color": "红色", "grade": "5", "single_stats": "物理攻击力+2 / 物理穿透+3.6", "ten_stats": "物理攻击力+20 / 物理穿透+36"}
M_WUSHUANG = {"id": "1510", "name": "无双", "color": "红色", "grade": "5", "single_stats": "暴击率+0.7% / 暴击效果+3.6%", "ten_stats": "暴击率+7% / 暴击效果+36%"}
M_SUMING = {"id": "1512", "name": "宿命", "color": "红色", "grade": "5", "single_stats": "攻速加成+1% / 最大生命+33.7 / 物理防御力+2.3", "ten_stats": "攻速加成+10% / 最大生命+337 / 物理防御力+23"}
M_MENGYAN = {"id": "1514", "name": "梦魇", "color": "红色", "grade": "5", "single_stats": "法术攻击力+4.2 / 法术穿透+2.4", "ten_stats": "法术攻击力+42 / 法术穿透+24"}
M_HUOYUAN = {"id": "1519", "name": "祸源", "color": "红色", "grade": "5", "single_stats": "暴击率+1.6%", "ten_stats": "暴击率+16%"}
M_HONGYUE = {"id": "1520", "name": "红月", "color": "红色", "grade": "5", "single_stats": "攻速加成+1.6% / 暴击率+0.5%", "ten_stats": "攻速加成+16% / 暴击率+5%"}

M_DUOCUI = {"id": "2504", "name": "夺萃", "color": "蓝色", "grade": "5", "single_stats": "物理吸血+1.6%", "ten_stats": "物理吸血+16%"}
M_TIAOHE = {"id": "2515", "name": "调和", "color": "蓝色", "grade": "5", "single_stats": "最大生命+45 / 生命回复+5.2 / 移速+0.4%", "ten_stats": "最大生命+450 / 生命回复+52 / 移速+4%"}
M_YINNI = {"id": "2517", "name": "隐匿", "color": "蓝色", "grade": "5", "single_stats": "物理攻击力+1.6 / 移速+1%", "ten_stats": "物理攻击力+16 / 移速+10%"}
M_SHOULIE = {"id": "2520", "name": "狩猎", "color": "蓝色", "grade": "5", "single_stats": "攻速加成+1% / 移速+1%", "ten_stats": "攻速加成+10% / 移速+10%"}

M_XUKONG = {"id": "3509", "name": "虚空", "color": "绿色", "grade": "5", "single_stats": "最大生命+37.5 / 冷却缩减+0.6%", "ten_stats": "最大生命+375 / 冷却缩减+6%"}
M_YINGYAN = {"id": "3514", "name": "鹰眼", "color": "绿色", "grade": "5", "single_stats": "物理攻击力+0.9 / 物理穿透+6.4", "ten_stats": "物理攻击力+9 / 物理穿透+64"}
M_XINYAN = {"id": "3515", "name": "心眼", "color": "绿色", "grade": "5", "single_stats": "攻速加成+0.6% / 法术穿透+6.4", "ten_stats": "攻速加成+6% / 法术穿透+64"}
M_LIANMIN = {"id": "3516", "name": "怜悯", "color": "绿色", "grade": "5", "single_stats": "冷却缩减+1%", "ten_stats": "冷却缩减+10%"}

HERO_ARCANA_PATCHES = {
    "敖隐": {
        "cname": "敖隐",
        "title": "凌霄真龙",
        "role": "射手",
        "recom_mings": [M_HUOYUAN, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "敖隐依赖火剑真实伤害与双剑普攻暴击，祸源提供高额基础暴击率，鹰眼百穿保障前期清线与穿透伤害，狩猎提供10%移速与10%攻速，显著改善走A手感与风剑拉扯机动性。"
    },
    "少司缘": {
        "cname": "少司缘",
        "title": "聆愿之祝",
        "role": "辅助",
        "recom_mings": [M_SUMING, M_XUKONG, M_TIAOHE],
        "sugg_tips": "少司缘属于功能型游走，需要频繁施法挂缘与飞身套盾。千血千抗铭文（宿命+虚空+调和）提供超高开局血量与物理防御，虚空补充6%冷却缩减，调和增强脱战续航与跑图移速。"
    },
    "影": {
        "cname": "影",
        "title": "黯羽东君",
        "role": "战士",
        "recom_mings": [M_YIBIAN, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "影以物理穿透与攻速走A为核心，百穿铭文（异变+鹰眼）将近战二技能突进爪击与大招范围斩杀的基础物理伤害拉满，狩猎提供10%移速与攻速，加速远程羽刃风筝与近战三次强化普攻的连贯性。"
    },
    "苍": {
        "cname": "苍",
        "title": "苍狼末裔",
        "role": "射手",
        "recom_mings": [M_HONGYUE, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "苍的巨狼伙伴与骑狼狂猎高度受益于攻击速度与暴击，红月提供16%攻速与5%暴击率，搭配狩猎达成26%初始攻速加成，出草瞬间高频触发两连射，压制力极强。"
    },
    "元流之子(坦克)": {
        "cname": "元流之子(坦克)",
        "title": "止戈之道",
        "role": "坦克",
        "recom_mings": [M_SUMING, M_XUKONG, M_TIAOHE],
        "sugg_tips": "元流之子坦克的护盾厚度直接与最大生命值挂钩，千血千抗铭文在开局赋予极强的生存韧性与换血资本，调和的回血让其在对抗路抗压或游走开团时拥有持久战力。"
    },
    "元流之子(法师)": {
        "cname": "元流之子(法师)",
        "title": "万妙之心",
        "role": "法师",
        "recom_mings": [M_MENGYAN, M_XINYAN, M_SHOULIE],
        "sugg_tips": "88法术穿透组合（梦魇+心眼）是法师通用顶级配置，前期射线无视敌方魔抗打出真伤级压制，狩猎提升10%移速利于远距离走位拉扯与支援边路。"
    },
    "元流之子(射手)": {
        "cname": "元流之子(射手)",
        "title": "沉舟之志",
        "role": "射手",
        "recom_mings": [M_HONGYUE, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "经典26攻速铭文组，红月与狩猎赋予极致走A攻速与移速，鹰眼百穿确保点射前排的破甲输出。"
    },
    "元流之子(辅助)": {
        "cname": "元流之子(辅助)",
        "title": "守望之诺",
        "role": "辅助",
        "recom_mings": [M_SUMING, M_XUKONG, M_TIAOHE],
        "sugg_tips": "千血千抗标准辅助配置，提供高额坦度与持续回复，兼顾前期游走支援与团战开团承伤。"
    },
    "元流之子(刺客)": {
        "cname": "元流之子(刺客)",
        "title": "守望之诺",
        "role": "刺客",
        "recom_mings": [M_YIBIAN, M_YINGYAN, M_YINNI],
        "sugg_tips": "隐匿百穿铭文提供极致初始物理攻击与物理穿透，10%跑图移速大幅提升野区刷野效率与线上突袭Gank成功率。"
    },
    "杨戬": {
        "cname": "杨戬",
        "title": "根源之目",
        "role": "战士",
        "recom_mings": [M_YIBIAN, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "百穿狩猎铭文提供充足物理穿透与攻速移速，二技能横扫后配合普攻真实伤害走A输出拉满，移速利于积攒韧性条进入法天象地状态。"
    },
    "空空儿": {
        "cname": "空空儿",
        "title": "笑面诡手",
        "role": "辅助/法师",
        "recom_mings": [M_MENGYAN, M_LIANMIN, M_TIAOHE],
        "sugg_tips": "怜悯提供10%极限冷却缩减，配合调和回血与梦魇法强，显著提高控场技能释放频率与自保能力。"
    },
    "蚩奼": {
        "cname": "蚩奼",
        "title": "五兵之主",
        "role": "战士",
        "recom_mings": [M_YIBIAN, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "百穿攻速配置，异变与鹰眼破甲保障五兵切换时的瞬间斩击伤害，狩猎移速加快战场近身。"
    },
    "孙权": {
        "cname": "孙权",
        "title": "定旌之谋",
        "role": "射手",
        "recom_mings": [M_HUOYUAN, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "高额暴击与物理穿透兼备，在军令阵地展开时倾泻密集的暴击弹幕，穿透前排护甲。"
    },
    "大禹": {
        "cname": "大禹",
        "title": "鼎镇山河",
        "role": "坦克/辅助",
        "recom_mings": [M_SUMING, M_XUKONG, M_TIAOHE],
        "sugg_tips": "九鼎护体极致千血铭文，提供最大生命值与物理防御，强化控场抗打能力。"
    },
    "心魔六耳": {
        "cname": "心魔六耳",
        "title": "孙悟空命格",
        "role": "刺客",
        "recom_mings": [M_WUSHUANG, M_YINGYAN, M_DUOCUI],
        "sugg_tips": "无双铭文直接拉高暴击效果上限，夺萃提供16%物理吸血保障无伤刷野与续航，鹰眼百穿确保暴击伤害刀刀见血。"
    },
    "卢雅那": {
        "cname": "卢雅那",
        "title": "蛇焰使者",
        "role": "射手",
        "recom_mings": [M_HONGYUE, M_YINGYAN, M_SHOULIE],
        "sugg_tips": "环刃附魔依赖高攻速触发，26攻速铭文组显著加快攻击判定，配合鹰眼穿透快速清理兵线与敌人。"
    }
}
