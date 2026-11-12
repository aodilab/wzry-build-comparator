"""王者荣耀全周期多阶段客观出装推演与【职业×分路×底层技能机制+三态主动装备】寻优引擎 (build_optimizer.py)"""

import argparse
import itertools
import json
import sys
from pathlib import Path
from src.core.hero_combo_profiles import extract_hero_skill_model
from src.core.hero_power_curve import analyze_hero_positioning_and_power_curve
from src.core.build_stage_evaluator import evaluate_hero_build_at_stage

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
with open(ROOT_DIR / "config" / "hero_skills_data.json", "r", encoding="utf-8") as f:
    HERO_SKILLS_DB = json.load(f)
_OFF_BUILDS_PATH = ROOT_DIR / "config" / "official_builds_data.json"
OFFICIAL_BUILDS_DB = json.loads(_OFF_BUILDS_PATH.read_text(encoding="utf-8")) if _OFF_BUILDS_PATH.exists() else {}

SPELLBLADE_ITEMS = {"宗师之力", "冰痕之握", "巫术法杖", "符文大剑"}
ACTIVE_ITEMS = {"纯净苍穹", "血魔之怒", "冰霜冲击", "不动·天穹", "侵掠·怒魂", "徐行·凛冬"}


def optimize_hero_lifecycle(hero_cname: str, is_jungle: bool = True) -> dict:
    """运行全周期三阶段自动推演"""
    model = extract_hero_skill_model(hero_cname)
    boots_list = model.get("boots_candidates", ["抵抗之靴"])
    lane_key = "打野" if is_jungle else "对抗"

    if is_jungle:
        early_paths = [(f"红刀+{b[:2]}鞋+陨星+铁剑", ["追击刀锋", b, "陨星", "铁剑"], 6, 8) for b in ("抵抗之靴", "冷静之靴", "影忍之足")] + [("肉刀+抵抗鞋+陨星+铁剑", ["巡守利斧", "抵抗之靴", "陨星", "铁剑"], 6, 8), ("红刀+抵抗鞋+暗影战斧", ["追击刀锋", "抵抗之靴", "暗影战斧"], 7, 10), ("红刀+抵抗鞋+怒龙剑盾", ["追击刀锋", "抵抗之靴", "怒龙剑盾"], 7, 10)]
        base3 = ["追击刀锋", boots_list[0], "怒龙剑盾" if model.get("orb_proc_mult", 1.0) > 1.2 else "暗影战斧"]
    else:
        early_paths = [("冷静鞋+陨星+荆棘护手", ["冷静之靴", "陨星", "荆棘护手"], 6, 0), ("影忍足+陨星+荆棘护手", ["影忍之足", "陨星", "荆棘护手"], 6, 0), ("抵抗鞋+陨星+日冕", ["抵抗之靴", "陨星", "日冕"], 6, 0)] + [(f"{b[:2]}鞋+暗影战斧+荆棘护手", [b, "暗影战斧", "荆棘护手"], 7, 0) for b in ("冷静之靴", "抵抗之靴")]
        base3 = [boots_list[0], "暗影战斧"]

    eval_fn = lambda it, lv, st: evaluate_hero_build_at_stage(hero_cname, it, lv=lv, jg_stacks=st, lane=lane_key)
    stage1_early = [{**eval_fn(it, lv, st), "label": lb} for lb, it, lv, st in early_paths]
    mid_candidates = ["冰痕之握", "暴烈之甲", "纯净苍穹", "宗师之力", "强者破军", "怒龙剑盾", "碎星锤", "不死鸟之眼", "血魔之怒", "冰霜冲击", "影刃", "闪电匕首", "末世", "制裁之刃", "寒霜袭侵"]
    stage2_mid4 = [{**eval_fn(base3 + [m4], 10, 16 if is_jungle else 0), "label": f"单核:{m4}"} for m4 in mid_candidates if m4 not in base3]
    mid5_pairs = [("怒龙剑盾", "不死鸟之眼"), ("冰痕之握", "怒龙剑盾"), ("怒龙剑盾", "血魔之怒"), ("冰痕之握", "纯净苍穹"), ("暴烈之甲", "纯净苍穹"), ("冰痕之握", "暴烈之甲"), ("纯净苍穹", "不死鸟之眼"), ("纯净苍穹", "怒龙剑盾"), ("影刃", "纯净苍穹"), ("末世", "纯净苍穹")]
    stage2_mid5 = [{**eval_fn(base3 + [a, b], 12, 20 if is_jungle else 0), "label": f"双核:{a}+{b}"} for a, b in mid5_pairs if a not in base3 and b not in base3]

    pool_all = ["暗影战斧", "宗师之力", "冰痕之握", "暴烈之甲", "纯净苍穹", "强者破军", "碎星锤", "怒龙剑盾", "血魔之怒", "冰霜冲击", "霸者重装", "名刀·司命", "魔女斗篷", "永夜守护", "不死鸟之眼", "反伤刺甲", "不祥征兆", "极寒风暴", "影刃", "闪电匕首", "末世", "制裁之刃", "寒霜袭侵", "无尽战刃"]
    all_late = [
        eval_fn(([jg, boot] if jg else [boot]) + list(combo), 15, 25 if is_jungle else 0)
        for jg in (["贪婪之噬", "巨人之握"] if is_jungle else [None])
        for boot in boots_list
        for combo in itertools.combinations(pool_all, 4 if is_jungle else 5)
        if len(SPELLBLADE_ITEMS.intersection(combo)) <= 1 and len(ACTIVE_ITEMS.intersection(combo)) <= 1
    ]

    for res in all_late:
        s = res["sub_scores"]
        res["score_balanced"] = res["score_no_blue"]
        res["score_snowball"] = round(0.45 * s["burst_kill"] + 0.18 * s["surv_3state"] + 0.15 * s["pve_roam"] + 0.12 * s["cd_wb"] + 0.10 * s["stickiness_cc"], 2)
        res["score_behind"] = round(0.42 * s["surv_3state"] + 0.22 * s["burst_kill"] + 0.16 * s["cd_nb"] + 0.12 * s["econ_sustain"] + 0.08 * s["stickiness_cc"], 2)
        res["score_antitank"] = round(0.40 * s["econ_sustain"] + 0.28 * s["burst_kill"] + 0.20 * s["surv_3state"] + 0.12 * s["cd_nb"], 2)

    official_audit = [{**eval_fn(b.get("items", []), 15, 25 if is_jungle else 0), "label": f"官方-{b.get('title', '')}"} for b in OFFICIAL_BUILDS_DB.get(hero_cname, {}).get("lanes", {}).get(lane_key, [])]
    official_audit += [{**eval_fn(vi, 15, 25 if is_jungle else 0), "label": vl} for vl, vi in model.get("viral_builds_jg" if is_jungle else "viral_builds_lane", [])]
    top5 = lambda k: sorted(all_late, key=lambda x: x[k], reverse=True)[:5]

    return {
        "hero": hero_cname, "lane": lane_key, "total_combinations_searched": len(all_late), "hero_positioning": analyze_hero_positioning_and_power_curve(hero_cname),
        "stage1_early": stage1_early, "stage2_mid4": sorted(stage2_mid4, key=lambda x: x["score_no_blue"], reverse=True), "stage2_mid5": sorted(stage2_mid5, key=lambda x: x["score_no_blue"], reverse=True),
        "pareto_balanced": top5("score_no_blue"), "pareto_with_blue": top5("score_with_blue"), "pareto_snowball": top5("score_snowball"), "pareto_behind": top5("score_behind"), "pareto_antitank": top5("score_antitank"), "official_audit": official_audit,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--hero", default="赵云"); p.add_argument("--lane", default="打野", choices=["打野", "对抗"])
    a = p.parse_args()
    rep = optimize_hero_lifecycle(a.hero, is_jungle=(a.lane == "打野"))
    fmt = lambda lbl, r: f"[{lbl}] {' + '.join(r['items'])} | 无蓝:{r['score_no_blue']} 有蓝:{r['score_with_blue']} | 三态EHP[常:{r['ehp_normal_downtime']}/特:{r['ehp_special_crisis']}/团:{r['entry_burst_ehp']}] | 三态分[常:{r['state_scores']['normal']}/特:{r['state_scores']['special']}/团:{r['state_scores']['teamfight']}->合:{r['state_scores']['composite_3state']}]"
    print(f"=== [{a.hero}·{a.lane}] 全周期推演完成 ({rep['pareto_balanced'][0]['role_profile']}) ===")
    for tag, key in [("无蓝综合最优", "pareto_balanced"), ("有蓝综合最优", "pareto_with_blue"), ("顺风切C最优", "pareto_snowball"), ("逆风容错最优", "pareto_behind")]:
        print(fmt(tag, rep[key][0]))
    for oa in rep["official_audit"]:
        print(fmt(oa["label"], oa))
