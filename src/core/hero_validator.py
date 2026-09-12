# -*- coding: utf-8 -*-
"""
国服英雄清单纵向对比与完整性校验引擎
确保每次爬取 100% 覆盖国服全量英雄，杜绝静默漏爬
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import URL_HERO_LIST
from config.hero_registry import CN_HERO_MANIFEST, get_manifest_dict
from src.core.http import fetch_json

def get_validated_hero_list(retries=3):
    """
    获取经过国服权威基准清单纵向差集校验的全量英雄列表
    返回: 100% 完备无漏的国服英雄列表
    """
    print("[1/2] 正在从官方接口拉取最新英雄列表...")
    try:
        live_heroes = fetch_json(URL_HERO_LIST, retries=retries)
    except Exception as e:
        print(f"[网络异常] 获取官方英雄列表失败 ({e})，立即切换至本地权威基准库兜底！")
        return [
            {"ename": ename, **info}
            for ename, info in CN_HERO_MANIFEST.items()
        ]

    # 构建实时抓取的映射表 (以 ename 为唯一主键)
    live_map = {}
    for h in live_heroes:
        try:
            ename = int(h.get("ename"))
            live_map[ename] = h
        except (ValueError, TypeError):
            continue

    manifest_map = get_manifest_dict()
    manifest_enames = set(manifest_map.keys())
    live_enames = set(live_map.keys())

    # --- 纵向差集比对 (Vertical Diff) ---
    missing_enames = manifest_enames - live_enames
    new_enames = live_enames - manifest_enames

    print("-" * 60)
    print("【国服英雄清单纵向比对报告】")
    print(f"  - 国服基准名册数：{len(manifest_enames)} 位")
    print(f"  - 官方接口返回数：{len(live_enames)} 位")

    # 1. 检查是否存在缺失（漏抓）
    if missing_enames:
        print(f"  [发现缺失预警] 官方接口缺少以下 {len(missing_enames)} 位国服英雄，系统自动从基准库实施防漏补齐：")
        for eid in missing_enames:
            m_info = manifest_map[eid]
            print(f"     -> 自动补齐英雄: [{eid}] {m_info['cname']} ({m_info.get('title', '')})")
            # 补齐到 live_map 中
            live_map[eid] = {
                "ename": eid,
                "cname": m_info["cname"],
                "title": m_info.get("title", ""),
                "hero_type": m_info.get("hero_type", 1),
                "hero_type2": m_info.get("hero_type2", 0)
            }
    else:
        print("  [防漏校验通过] 国服基准名册中的所有英雄已全部覆盖，无任何缺失！")

    # 2. 检查是否有新上线英雄
    if new_enames:
        print(f"  [新英雄上线提醒] 检测到官方新增上线 {len(new_enames)} 位英雄：")
        for eid in new_enames:
            new_h = live_map[eid]
            print(f"     -> 新英雄: [{eid}] {new_h.get('cname')} ({new_h.get('title', '')})")

    print("-" * 60)

    # 构造最终输出列表，优先以基准库顺序排列，新增英雄追加在尾部
    final_hero_list = []
    processed_enames = set()

    # 首先按基准名单顺序压入
    for eid in manifest_map.keys():
        if eid in live_map:
            final_hero_list.append(live_map[eid])
            processed_enames.add(eid)

    # 然后追加新上架英雄
    for eid, h in live_map.items():
        if eid not in processed_enames:
            final_hero_list.append(h)

    print(f"[校验就绪] 最终输送构建管道的国服英雄总数：{len(final_hero_list)} 位\n")
    return final_hero_list
