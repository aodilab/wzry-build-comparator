# -*- coding: utf-8 -*-
"""
百度搜索资源平台 API 自动推送工具
自动化提取 sitemap.xml 核心 URL 并按百度每日配额主动推送给百度蜘蛛
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 避免当前目录下的 http.py 遮蔽 Python 标准库 http
_curr_dir = os.path.dirname(os.path.abspath(__file__))
if _curr_dir in sys.path:
    sys.path.remove(_curr_dir)

import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

BAIDU_PUSH_API = "http://data.zz.baidu.com/urls?site=https://wzry.aodilab.com&token=XuU72gS9oWBr6WVM"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITEMAP_PATH = os.path.join(PROJECT_ROOT, "dist_pages", "sitemap.xml")
LOG_PATH = os.path.join(PROJECT_ROOT, "config", "baidu_pushed_urls.json")

def get_sitemap_urls():
    if not os.path.exists(SITEMAP_PATH):
        return []
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    urls = []
    for child in root:
        loc = child.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls

def push_urls_to_baidu(limit=10):
    all_urls = get_sitemap_urls()
    if not all_urls:
        print("❌ 未找到 sitemap.xml 或 URL 列表为空")
        return

    # 读取历史已推送记录
    pushed_set = set()
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                pushed_set = set(json.load(f))
        except Exception:
            pushed_set = set()

    # 优先筛选未推送的 URL，如果全推过了则循环推前排核心页
    pending_urls = [u for u in all_urls if u not in pushed_set]
    if not pending_urls:
        print("ℹ️ 全站 URL 均已推送过一轮，本次将重复推送前排核心页面进行保活更新...")
        pending_urls = all_urls

    batch = pending_urls[:limit]
    data = "\n".join(batch).encode("utf-8")
    req = urllib.request.Request(BAIDU_PUSH_API, data=data, headers={"Content-Type": "text/plain"})

    try:
        with urllib.request.urlopen(req) as resp:
            res_str = resp.read().decode("utf-8")
            res_data = json.loads(res_str)
            success_count = res_data.get("success", 0)
            remain = res_data.get("remain", 0)
            print(f"✅ 成功推送 {success_count} 条 URL 到百度搜索资源平台！")
            print(f"📊 今日剩余提交配额: {remain} 条")
            
            # 更新记录
            pushed_set.update(batch[:success_count])
            with open(LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(list(pushed_set), f, ensure_ascii=False, indent=2)

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        if "over quota" in err_msg:
            print(f"ℹ️ 今日百度推送配额已耗尽 (新站每日限额 10 条)，今日推送已完成，请明日零点后再执行。")
        else:
            print(f"❌ 百度 API 报错 (HTTP {e.code}): {err_msg}")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

if __name__ == "__main__":
    push_urls_to_baidu(limit=10)
