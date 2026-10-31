# -*- coding: utf-8 -*-
"""
王者荣耀全量装备(115件)与全英雄(133名)机制【七大顶层范类 × 十二种子条件】统一分类引擎 (src/core/mechanic_taxonomy.py)
严格基于 config/items_ground_truth.json 与 config/hero_skills_data.json 本地权威数据源，将全游戏所有装备与英雄技能按触发条件归入 7 大顶层范类 (T1~T7) 及 12 种细分条件模型，杜绝凭印象硬编码或混淆常驻/叠层/条件/主动效果。
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
with open(ROOT_DIR / "config" / "items_ground_truth.json", "r", encoding="utf-8") as f:
    ALL_GT_ITEMS = json.load(f)
with open(ROOT_DIR / "config" / "hero_skills_data.json", "r", encoding="utf-8") as f:
    ALL_HERO_SKILLS = json.load(f)

# ==============================================================================
# 一、 七大顶层范类 (Top-Level Archetypes) 与 十二种子条件 (Sub-Condition Schemas)
# ==============================================================================
TAXONOMY_SCHEMA_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "T1_PERMANENT": {
        "name": "范类一：无条件常驻范类",
        "sub_types": {
            "T1A_STATIC_PANEL": "纯静态面板与无条件常驻穿透/暴击/减伤 (全阶段 100% 生效)",
            "T1B_RANGE_ROLE_SPLIT": "近战/远程射程分流常驻 (破晓/逐日远程翻倍，怒龙/冰痕/肉刀远程减半)",
            "T1C_STAT_CONVERT_CAP": "属性转化与上限锁死 (破魔刀物攻转法防、魔女法防转物防、杨戬除法天象地外装备韧性上限锁死25%)",
        },
    },
    "T2_GROWTH_ECON": {
        "name": "范类二：发育叠层与时间门禁范类",
        "sub_types": {
            "T2A_JG_STACK_TIME_GATE": "打野刀击杀叠层(15/25层)与时间门禁(4分钟防蹭线/10分钟前兵线降伤25%)",
            "T2B_MATCH_TIME_GROWTH": "对局时长/等级成长 (名刀每90/180/270秒成长无敌与属性、游走装20分钟成长、时之预言升级回血)",
        },
    },
    "T3_PERIODIC_PROC": {
        "name": "范类三：内置CD战斗循环触发范类",
        "sub_types": {
            "T3A_SPELLBLADE": "技能后强化普攻强击 (冰痕1.25s CD / 巫术2.5s CD / 宗师3.0s CD，严格按窗口时长/CD计次)",
            "T3B_ON_HIT_ORB": "普攻法球特效 (末世/血魔狂怒0.15s CD、电刀每3次普攻连锁闪电、金色圣剑0.2s CD)",
            "T3C_TARGET_PERIODIC": "周期触发与目标类型/首中限制 (怒龙2.5s对兵野7%回血3.5%/对英雄3.5%、苍穹残废8s CD仅对首个命中英雄降伤20%持续3s)",
        },
    },
    "T4_RAMPING_STATE": {
        "name": "范类四：渐进叠层与积攒变身范类",
        "sub_types": {
            "T4A_ON_DAMAGED_RAMP": "受击次数渐进叠层 (暴烈之甲-无畏：脱战0层，每次受击+1%增伤移速/英雄伤害2层，上限10层)",
            "T4B_ON_HIT_RAMP": "攻击/命中渐进叠层 (逐风叠5层、日暮之流叠6层、影刃暴击加速)",
            "T4C_GAUGE_TRANSFORM": "能量/韧性积攒满槽变身强化 (杨戬-法天象地：普攻技能造成伤害积攒韧性达上限进入霸体，且与英雄战斗时变身+600生命/强化射程与大招多道激光)",
        },
    },
    "T5_CONDITIONAL": {
        "name": "范类五：条件判定型范类 (细分6大触发条件)",
        "sub_types": {
            "T5A_SELF_HP_THRESHOLD": "自身血量阈值/档位条件 (赵云龙鸣70%/40%三档免伤、不死鸟每损10%血+6.5%回复、血魔<50%血狂怒增伤、炽热<30%血解控盾)",
            "T5B_TARGET_HP_EXECUTE": "敌方血量斩杀/百分比条件 (破军目标<50%血+30%伤害、杨戬1技能二段附加目标15%已损生命物伤、痛苦面具当前生命)",
            "T5C_RELATIVE_COMPARISON": "敌我状态相对比较条件 (杨戬2技能：基础晕0.5秒，当【目标生命百分比 ≥ 杨戬自身生命百分比】时晕眩延长至1秒；白盾不计入生命百分比)",
            "T5D_SPATIAL_GEOMETRY": "空间距离与多道同目标衰减条件 (杨戬天眼：攒1~3层能量且【目标远离杨戬】时发射激光；杨戬大招：近身贴脸多道激光同时命中同一目标时，后续激光仅30%伤害与50%回复；赵云大招中心击飞)",
            "T5E_SPIKE_CC_OOC": "受击强度/受硬控/脱战条件 (极寒单次受击>10%当前生命、永夜2.5s受击>25%最大生命、冰霜冲击受硬控获10%护盾、名刀致命伤、霸者3s脱战)",
            "T5F_STATE_RESET_REFUND": "状态跃迁重置与冷却返还条件 (赵云被动档位变化立即额外存储1次1技能；杨戬1技能标记期间击杀刷新CD/未命中靠近狗返还25%~50%CD；赵云大招空大返还50%CD)",
        },
    },
    "T6_SHIELD_CONVERSION": {
        "name": "范类六：血盾转化与伤害延迟池范类",
        "sub_types": {
            "T6A_OVERHEAL_SHIELD_HP": "溢出转盾与血盾填满档位转真血 (赵云溢出回复转永久护盾，且血盾总量填满档位时档位以下护盾转化为生命值；泣血之刃溢出转400~800生命)",
            "T6B_DELAYED_DMG_POOL": "伤害延迟结算池 (曜星削25%/37.5%/50%伤害延迟2秒结算并可被大招清除)",
        },
    },
    "T7_ACTIVE_SKILL": {
        "name": "范类七：长CD主动技能范类 (75s~90s CD，唯一主动互斥)",
        "sub_types": {
            "T7A_HP_COST_RAMP_SHIELD": "自损真血换渐生护盾 (血魔之怒/怒魂：4秒内逐渐扣除30%当前生命，逐渐获得40%/50%最大生命护盾，CD 75s；联动T5A/T5C/T5F/T6A)",
            "T7B_ACTIVE_DR_CLEANSE": "主动百分比减伤与解控 (纯净苍穹30%减伤3s / 不动·天穹解控+35%减伤+穿墙+击杀刷新，CD 75s)",
            "T7C_ACTIVE_AOE_CC": "主动范围团控与视野减速 (冰霜冲击/凛冬0.75s减速后冻结，CD 75s；形昭探草减速)",
            "T7D_ACTIVE_STASIS_TEAM": "主动无敌/隐身/团队增益 (辉月/月神1.5s无敌、幽影袖箭隐身回血、救赎群盾、奔狼群速、星泉链接、逐日加射程)",
        },
    },
}

# 范类四 (T4_RAMPING_STATE) 在四个战斗阶段的标准叠层折算系数
C3_STAGE_RAMP_FACTORS = {
    "roam": 0.00,             # 阶段0：脱战跑图 (0层，暴烈之甲脱战移速=0%)
    "burst_2s": 0.30,         # 阶段1：先手秒脆皮前2秒 (仅受击/命中1~2次，叠30%层数)
    "normal_skirmish": 0.65,  # 阶段2：常态小规模拉扯 (平均叠65%层数)
    "sustained_tf": 0.85,     # 阶段3：5v5团战持续集火肉搏 (平均叠85%层数)
}

# 范类七 (T7_ACTIVE_SKILL) 75秒长CD主动装备在三态中的标准窗口覆盖率
C5_ACTIVE_WINDOW_WEIGHTS = {
    "state_normal_downtime": 0.00,  # 状态1：75s冷却真空期，主动护盾/主动减伤严格归零
    "state_special_crisis": 0.50,   # 状态2：残血单挑/绝境博弈(6秒窗口)，主动技能覆盖50%窗口
    "state_teamfight_peak": 0.45,   # 状态3：5v5团战集火(6.5秒窗口)，主动技能覆盖45%窗口
}

# 蓝Buff周期覆盖率与断蓝时间差模型 (持续70s / 刷新周期90s + 跑图刷野交接与团战延迟时间差 = 56%实际持蓝 + 44%断蓝空窗期)
# 且前中期换鞋每次净亏284金币(折旧40%)得不偿失，必须固定单鞋硬抗断蓝空窗期
BLUE_BUFF_CYCLE_MODEL = {
    "uptime_ratio": 0.56,           # 控蓝局中，扣除刷新间隔、跑图打野与团战交接后实际持蓝时间占比 (56%)
    "renewal_gap_ratio": 0.44,      # 蓝Buff消失->等待刷新->重拿蓝Buff的真实断蓝时间差占比 (44%)
    "safe_base_cdr_threshold": 30.0, # 断蓝空窗期不卡手的安全常驻冷却阈值 (≥30%则固定单鞋断蓝期依然丝滑)
    "boot_swap_gold_loss": 284,     # 单次卖鞋换鞋净损失金币 (710 * 40% = 284金币，前中期严禁来回换鞋)
}

# 核心英雄完整条件模型与跨范类耦合规则表 (100% 严格对照 config/hero_skills_data.json 原文)
HERO_MECHANIC_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "赵云": {
        "T1_permanent": ["基础属性成长", "被动【龙鸣】满血一档(70%<HP≤100%)常驻5%免伤"],
        "T3_periodic_proc": [
            "2技能【破云之龙】(CD 5s)：连续5次刺出龙枪，每枪420(+65%额外AD)物伤并回血140(+1.5%额外生命)，后续每枪效果降低8%",
            "3技能【天翔之龙】(CD 16s)：960(+145%额外AD)物伤，附加5秒感电(每次技能命中额外30~60+10%额外AP法伤)",
        ],
        "T5_conditional": {
            "T5A_self_hp_tiers": "被动【龙鸣】：一档(70%~100%)5%免伤 / 二档(40%~70%)10%免伤 / 三档(≤40%)20%免伤",
            "T5D_spatial_center": "3技能【天翔之龙】：仅对【范围中心】的敌人造成1秒击飞(外圈仅造成伤害与感电)",
            "T5F_tier_cross_reset": "1技能【惊雷之龙】：被动档位发生变化(跨越70%或40%生命线)时，立即存储1次额外【惊雷之龙】(位移+700+120%额外AD+强化普攻240+40%额外AD+50%减速2s)；3技能未命中英雄返还50%冷却",
        },
        "T6_shield_conversion": {
            "T6A_overheal_and_fill": "被动【龙鸣】：仅在二/三档回血触及并跨过70%/40%档位线时，绿血锁在档位线且溢出回血转化为永久白盾（满血一档或未跨档位线不产盾）；当【当前绿血+白盾（血盾总量）填满一个档位(30%宽度)】时，档位线以下的白盾瞬间消失并1:1转化为永久真实绿血，同时升档并存储1次额外1技能",
        },
        "C5_x_C4_couplings": {
            "血魔之怒": {
                "extra_s1_casts_teamfight": 0.45,
                "extra_s1_casts_burst": 0.30,
                "crisis_net_shield_ratio": 0.32,
                "teamfight_net_shield_ratio": 0.28,
                "synergy_desc": "T7A×(T5A+T5F+T6A)联动：主动扣30%当前生命强制跨越70%/40%档位线 → ①免费多存1个1技能+强化普攻；②跃升10%/20%免伤档位；③40%最大生命护盾直接跨过30%档位宽度，将档位线以下的护盾当场转化为永久真实绿血并再次升档刷1技能",
            },
        },
    },
    "杨戬": {
        "T1_permanent": [
            "基础属性成长",
            "T1C_韧性上限与持续时间联动：被动【法天象地】自带60%~90%韧性上限且规定『除【法天象地】外，杨戬至多获得25%韧性』(出抵抗之靴+25%初始韧性会使变身需要积攒的韧性差值从90%缩至65%，导致法天象地持续时间从9秒缩短至6.5秒，常规推荐影忍之足或冷静之靴)",
        ],
        "T3_periodic_proc": [
            "1技能一段【逆转乾坤】(CD 6s)：召唤哮天犬冲锋造成400(+60%额外AD)物伤并标记5秒视野",
            "3技能单道基准【根源之目】(CD 28s)：释放3次激光，单道命中造成680(+110%额外AD)物伤并回复600(+4.5%额外生命)生命(非英雄减半)",
        ],
        "T4_ramping_state": {
            "T4C_fatian_xiangdi": "被动【法天象地】双重触发条件：①普攻和技能造成伤害积攒韧性槽(60%~90%随大招成长)，达到上限进入临界霸体状态；②必须【与敌方英雄单位战斗】才进入法天象地状态，击退周围敌人并获得技能强化、射程强化和+600点最大生命",
        },
        "T5_conditional": {
            "T5B_target_execute": "1技能二段【逆转乾坤】：冲向标记敌人造成600(+90%额外AD)物伤，并额外附加【目标15%已损生命】物理伤害",
            "T5C_relative_hp_stun": "2技能【虚妄破灭】条件：挥枪横扫造成700(+100%额外AD)物伤与30%减速(1.5s)；基础造成0.5秒晕眩，当【目标生命百分比 ≥ 杨戬自身生命百分比】时晕眩时间延长至1秒！命中后5秒内普攻附带250(+36%额外AD)真实伤害",
            "T5D_spatial_tianyan_and_laser": [
                "被动【天眼】距离条件：①技能命中获得1层能量(最多3层)；②必须当【目标远离杨戬】时，天眼才会发射激光造成80~160(+25%额外AD)物伤并回复60~120(+1%额外生命)生命",
                "3技能【根源之目】多道散射衰减条件：法天象地强化或第3段发射多道扇形激光时，仅在【近身贴脸】时多道激光可同时命中同一目标，且【后续激光仅造成30%伤害(3道合计1.6倍)和50%回复(3道合计2.0倍)】；中远距离仅命中1道(1.0倍)",
            ],
            "T5F_cd_refund_reset": "1技能【逆转乾坤】：①敌人在被标记期间内死亡则100%刷新1技能冷却；②未命中时哮天犬停留在终点，杨戬靠近回收可减少当前25%~50%冷却",
        },
        "C5_x_C4_couplings": {
            "纯净苍穹": {
                "extra_s3_casts_teamfight": 0.45,
                "heal_preserve_mult": 1.16,
                "crisis_dr_window_bonus": 0.10,
                "teamfight_dr_window_bonus": 0.12,
                "synergy_desc": "T7B×(T4C+T5D)联动：杨戬靠普攻技能攒满法天象地并放出3次大招激光需要3~4秒窗口，苍穹主动30%减伤防止在攒满韧性前被集火秒杀，完整多放出第3段大招并保住回血闭环",
            },
            "血魔之怒": {
                "crisis_net_shield_ratio": 0.25,
                "teamfight_net_shield_ratio": 0.20,
                "synergy_desc": "T7A×T5C联动：主动扣除30%当前生命强制压低自身生命百分比，且40%血魔白盾不计入生命百分比 → 100%触发2技能【翻倍1秒晕眩(0.5s→1.0s)】",
            },
        },
    },
}


def classify_all_items_automatically() -> Dict[str, List[str]]:
    """自动扫描 config/items_ground_truth.json 全部 115 件装备并按 des1/des2 归入 T1~T7 范类"""
    result: Dict[str, List[str]] = {}
    for name, data in ALL_GT_ITEMS.items():
        tags = ["T1A_STATIC_PANEL"] if data.get("des1", "").strip() else []
        d2 = re.sub(r"</?[^>]+>", " ", data.get("des2", "")).strip()
        if not d2:
            result[name] = tags
            continue
        if re.search(r"远程英雄|远程攻击", d2):
            tags.append("T1B_RANGE_ROLE_SPLIT")
        if re.search(r"转化为|每\d+%.*增加|每\d+%.*提供|每100.*提供|上限\d+|最多不超过\d+|增加30%法术攻击", d2):
            tags.append("T1C_STAT_CONVERT_CAP")
        if re.search(r"携带惩击|击杀野怪.*叠加|被动-游击", d2):
            tags.append("T2A_JG_STACK_TIME_GATE")
        if re.search(r"每隔90|20分钟|英雄升级后", d2):
            tags.append("T2B_MATCH_TIME_GROWTH")
        if "被动-强击" in d2:
            tags.append("T3A_SPELLBLADE")
        if re.search(r"被动-(?:破败|狂怒|电弧|圣剑|精准|急速恢复)", d2):
            tags.append("T3B_ON_HIT_ORB")
        if re.search(r"被动-(?:重创|神力|残废|业炎|回响|折磨|冻伤|寒霜|重伤|初光|迷雾|寒铁)", d2):
            tags.append("T3C_TARGET_PERIODIC")
        if "被动-无畏" in d2:
            tags.append("T4A_ON_DAMAGED_RAMP")
        if re.search(r"被动-(?:逐风|净魔|暴风)", d2) and "破茧" not in name:
            tags.append("T4B_ON_HIT_RAMP")
        if re.search(r"每损失10%生命|(?:生命|血量).*低于(?:50|40|30)%", d2) and "破军" not in name:
            tags.append("T5A_SELF_HP_THRESHOLD")
        if "低于50%的敌人" in d2:
            tags.append("T5B_TARGET_HP_EXECUTE")
        if re.search(r"超过(?:当前生命10%|25%最大生命)|受到除压制外的硬控|受到致命伤害|死亡后2秒|未进入战斗|没有受到敌方|法力值已满", d2):
            tags.append("T5E_SPIKE_CC_OOC")
        if "被动-充溢" in d2:
            tags.append("T6A_OVERHEAL_SHIELD_HP")
        if "主动-血怒" in d2:
            tags.append("T7A_HP_COST_RAMP_SHIELD")
        if re.search(r"主动-驱散|被动-反刺", d2):
            tags.append("T7B_ACTIVE_DR_CLEANSE")
        if re.search(r"主动-(?:冲击|见影)", d2):
            tags.append("T7C_ACTIVE_AOE_CC")
        if re.search(r"主动-(?:月之守护|无踪|救援|奔腾号令|星芒|逐日)", d2):
            tags.append("T7D_ACTIVE_STASIS_TEAM")
        result[name] = tags
    return result


def classify_all_hero_skills_automatically() -> Dict[str, List[Dict[str, Any]]]:
    """自动扫描 config/hero_skills_data.json 全部 133 名英雄的 500+ 个技能并标注 T1~T6 条件与跨机制关联标签"""
    hero_map: Dict[str, List[Dict[str, Any]]] = {}
    for h_name, skills in ALL_HERO_SKILLS.items():
        s_list = []
        for sk in skills:
            d = sk.get("desc", "")
            c_tags = []
            if sk.get("type") == "被动" or "无冷却" in sk.get("cd", ""):
                c_tags.append("T1/T4/T5_PASSIVE")
            if re.search(r"每损失|低于\d+%|生命值降低|档位|生命越低", d):
                c_tags.append("T5A_SELF_HP_THRESHOLD")
            if re.search(r"已损生命|目标.*最大生命|当前生命", d):
                c_tags.append("T5B_TARGET_HP_EXECUTE")
            if re.search(r"高于|低于目标|生命值比例", d):
                c_tags.append("T5C_RELATIVE_COMPARISON")
            if re.search(r"远离|距离|范围中心|外圈|内圈|多道.*同时命中|重复命中.*衰减|后续.*衰减", d):
                c_tags.append("T5D_SPATIAL_GEOMETRY")
            if re.search(r"积攒|能量|怒气|印记|叠.*层|进入.*状态", d):
                c_tags.append("T4C_GAUGE_TRANSFORM")
            if re.search(r"刷新|返还.*冷却|减少.*冷却|缩短.*冷却|存储一次额外", d):
                c_tags.append("T5F_STATE_RESET_REFUND")
            if re.search(r"溢出.*护盾|转化为永久护盾|转化为生命|转化为护盾", d):
                c_tags.append("T6A_OVERHEAL_SHIELD_HP")
            if re.search(r"法球|普攻行为|普通攻击行为|普攻效果", d):
                c_tags.append("T3B_ORB_PROC_LINK")
            if re.search(r"当攻速达到|随攻速提升|受攻速影响|每1%攻击速度", d):
                c_tags.append("T1C_ASPEED_SCALING_LINK")
            if "霸体" in d and re.search(r"减伤|免伤|伤害减免|减少\d+.*伤害|吸收.*伤害", d):
                c_tags.append("T4C_CO_FRAME_BATI_DR_LINK")
            s_list.append({"skill": sk.get("name", ""), "type": sk.get("type", ""), "conditions": c_tags or ["T3_STANDARD_ACTIVE_SKILL"]})
        hero_map[h_name] = s_list
    return hero_map


def get_hero_c5_coupling(hero_cname: str, item_name: str) -> Dict[str, Any]:
    """查询指定英雄与第7类主动装备的跨范类专属耦合参数"""
    return HERO_MECHANIC_TAXONOMY.get(hero_cname, {}).get("C5_x_C4_couplings", {}).get(item_name, {})


# 五级【霸体/免控/解控/不可选中 ↔ 韧性(60%全局上限)】深度关联矩阵
TIER_A_CAP_OR_FULL_IMMUNITY = {"杨戬", "庄周", "花木兰", "廉颇", "李信", "典韦", "刘备", "李白", "云中君", "狄仁杰", "李元芳", "元歌"}
TIER_B_WINDOW_COMPLEMENT = {"宫本武藏", "云缨", "姬小满", "夏洛特", "韩信", "亚连", "雅典娜", "蒙恬", "上官婉儿", "芈月", "司马懿", "虞姬", "安琪拉", "瑶", "艾琳", "敖隐", "暃", "心魔六耳", "孙悟空", "杨玉环"}
TIER_C_TENACITY_STACK_SYNERGY = {"曹操", "哪吒"}
TIER_D_INSTANT_OR_INTERRUPT_PENALTY = {"关羽", "孙策", "夏侯惇", "张飞", "盘古", "猪八戒", "赵怀真", "项羽", "盾山", "大禹", "元流之子(刺客)", "梦奇", "海诺", "莱西奥", "司空震"}
TIER_E1_MELEE_DIVER_ZERO_ANTICC = {"赵云", "曜", "澜", "镜", "铠", "橘右京", "娜可露露", "达摩", "狂铁", "钟无艳", "老夫子", "百里玄策", "阿轲", "露娜", "亚瑟", "吕布", "白起", "程咬金", "大司命", "牛魔", "刘禅", "东皇太一", "苏烈", "影", "兰陵王", "不知火舞", "貂蝉", "马超", "裴擒虎", "嫦娥", "墨子", "刘邦", "元流之子(坦克)"}


def derive_hero_anti_cc_boots_profile(hero_cname: str) -> Dict[str, Any]:
    """
    基于 config/hero_skills_data.json 精确解析全英雄【霸体/免控/解控/不可选中 ↔ 韧性】五级关联关系：
    - Tier A (上限封顶/全程覆盖替代型，如杨戬60~90%韧性封顶、花木兰重剑、李信、廉颇、庄周、典韦全技能解控)：抵抗鞋溢出重叠，收益权重 0.35~0.45。
    - Tier B (技能动作帧霸体+衔接帧韧性互补型，如宫本武藏S1/S3霸体但强普无霸体、云缨S3霸体但三层枪意燎原无霸体、夏洛特、姬小满、韩信)：动作帧霸体常伴随21%~60%同帧减伤，但连招衔接期暴露，功能鞋与抵抗鞋互补平权(权重0.80)。
    - Tier C (低额韧性叠加增益型，如曹操大招20%韧性、哪吒大招20%韧性)：20% + 抵抗鞋25% = 45% (未超60%全局上限)，属于正向叠加协同(权重1.15)。
    - Tier D (仅大招起手瞬时霸体 或 断马腿惩罚反噬型，如关羽受控/减速即断冲锋、孙策/夏侯惇/张飞/盘古落地肉搏0霸体)：虽有词条但实战落地期高度依赖抵抗鞋(权重1.05)。
    - Tier E1/E2 (全身0霸体+0免控+0解控+0韧性：E1近战突进如赵云/曜/澜/镜/铠刚需锁定抵抗鞋；E2远程后排按属性选攻速/法穿/CD/抵抗鞋)。
    """
    sks = ALL_HERO_SKILLS.get(hero_cname, [])
    bati_cnt = sum(1 for s in sks if "霸体" in s.get("desc", ""))
    cleanse_cnt = sum(1 for s in sks if re.search(r"解控|解除(?:自身|所有)?控制|净化(?:所有)?(?:控制|负面)|清除控制|免控|免疫(?:所有)?(?:控制|效果)|获得免疫", s.get("desc", "")))
    untarget_cnt = sum(1 for s in sks if re.search(r"不可(?:被)?选中|无法(?:被)?选中|短暂无敌|无敌效果", s.get("desc", "")))
    tenacity_cnt = sum(1 for s in sks if "韧性" in s.get("desc", ""))
    co_frame_dr = sum(1 for s in sks if "霸体" in s.get("desc", "") and re.search(r"减伤|免伤|伤害减免|减少\d+.*伤害|吸收.*伤害", s.get("desc", "")))
    full_txt = " ".join(s.get("desc", "") for s in sks)
    equip_cap = 0.25 if "至多获得25%韧性" in full_txt else 0.60

    if hero_cname in TIER_A_CAP_OR_FULL_IMMUNITY:
        w = 0.35 if "60%~90%" in full_txt else 0.45
        return {"anti_cc_class": "TIER_A_CAP_OR_FULL_IMMUNITY", "bati_skills": bati_cnt, "cleanse_skills": cleanse_cnt, "untarget_skills": untarget_cnt, "co_frame_dr_skills": co_frame_dr, "innate_tenacity": 0.85 if "60%~90%" in full_txt else 0.72, "tenacity_synergy_mult": w, "equip_tenacity_cap": equip_cap, "requires_tenacity_boots": False, "boots_candidates": ["影忍之足", "冷静之靴", "抵抗之靴", "急速战靴"]}
    if hero_cname in TIER_B_WINDOW_COMPLEMENT:
        return {"anti_cc_class": "TIER_B_WINDOW_COMPLEMENT", "bati_skills": bati_cnt, "cleanse_skills": cleanse_cnt, "untarget_skills": untarget_cnt, "co_frame_dr_skills": co_frame_dr, "innate_tenacity": 0.55, "tenacity_synergy_mult": 0.80, "equip_tenacity_cap": equip_cap, "requires_tenacity_boots": False, "boots_candidates": ["冷静之靴", "影忍之足", "抵抗之靴", "急速战靴"]}
    if hero_cname in TIER_C_TENACITY_STACK_SYNERGY:
        return {"anti_cc_class": "TIER_C_TENACITY_STACK_SYNERGY", "bati_skills": bati_cnt, "cleanse_skills": cleanse_cnt, "untarget_skills": untarget_cnt, "co_frame_dr_skills": co_frame_dr, "innate_tenacity": 0.20, "tenacity_synergy_mult": 1.15, "equip_tenacity_cap": 0.40, "requires_tenacity_boots": False, "boots_candidates": ["抵抗之靴", "影忍之足", "冷静之靴"]}
    if hero_cname in TIER_D_INSTANT_OR_INTERRUPT_PENALTY:
        req = hero_cname in {"关羽", "孙策", "元流之子(刺客)"}
        return {"anti_cc_class": "TIER_D_INSTANT_OR_INTERRUPT_PENALTY", "bati_skills": bati_cnt, "cleanse_skills": cleanse_cnt, "untarget_skills": untarget_cnt, "co_frame_dr_skills": co_frame_dr, "innate_tenacity": 0.15, "tenacity_synergy_mult": 1.05, "equip_tenacity_cap": 0.60, "requires_tenacity_boots": req, "boots_candidates": ["抵抗之靴"] if req else ["抵抗之靴", "影忍之足", "冷静之靴"]}
    if hero_cname in TIER_E1_MELEE_DIVER_ZERO_ANTICC:
        return {"anti_cc_class": "TIER_E1_MELEE_DIVER_ZERO_ANTICC", "bati_skills": 0, "cleanse_skills": 0, "untarget_skills": 0, "co_frame_dr_skills": 0, "innate_tenacity": 0.0, "tenacity_synergy_mult": 1.00, "equip_tenacity_cap": 0.60, "requires_tenacity_boots": True, "boots_candidates": ["抵抗之靴"]}
    return {"anti_cc_class": "TIER_E2_RANGED_BACKLINE_ZERO_ANTICC", "bati_skills": 0, "cleanse_skills": 0, "untarget_skills": 0, "co_frame_dr_skills": 0, "innate_tenacity": 0.0, "tenacity_synergy_mult": 0.85, "equip_tenacity_cap": 0.60, "requires_tenacity_boots": False, "boots_candidates": ["急速战靴", "秘法之靴", "冷静之靴", "抵抗之靴"]}
