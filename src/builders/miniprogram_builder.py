# -*- coding: utf-8 -*-
"""
王者荣耀微信原生小程序项目生成器 (Native WeChat Mini Program Builder)
单一职责：组装 templates/miniprogram 模块化模板与工程配置。
"""
import json
import os
import shutil

from src.builders.miniprogram_dataset import write_miniprogram_dataset

APPID = "wxf3e8255a219a851c"
PROJECT_NAME = "王者出装箱"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL_DIR = os.path.join(ROOT_DIR, "templates", "miniprogram")


def _read_tpl(filename: str) -> str:
    path = os.path.join(TPL_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _assemble_duel_js() -> str:
    duel_raw = _read_tpl("duel.js")
    shop_raw = _read_tpl("duel_shop.js")
    arcana_raw = _read_tpl("duel_arcana_touch.js")

    def _extract_methods(content: str) -> str:
        idx = content.find("module.exports = {")
        if idx == -1:
            return ""
        start = idx + len("module.exports = {")
        end = content.rfind("}")
        return content[start:end].strip().rstrip(",").rstrip()

    duel_clean = duel_raw.replace("const duelShopMethods = require('./duel_shop.js');\n", "")
    duel_clean = duel_clean.replace("const duelArcanaTouchMethods = require('./duel_arcana_touch.js');\n", "")
    duel_clean = duel_clean.replace("Page(Object.assign({", "Page({")

    shop_methods = _extract_methods(shop_raw)
    arcana_methods = _extract_methods(arcana_raw)

    tail = "\n}, duelShopMethods, duelArcanaTouchMethods));"
    replacement = (
        "\n\n  // === 装备商店与推演计算方法 ===\n  "
        + shop_methods
        + ",\n\n  // === 铭文与交互手势方法 ===\n  "
        + arcana_methods
        + "\n});"
    )
    return duel_clean.replace(tail, replacement)


def generate_miniprogram_project(mp_dir: str = None):
    if not mp_dir:
        mp_dir = os.path.join(ROOT_DIR, "miniprogram")
    os.makedirs(mp_dir, exist_ok=True)
    pages_dir = os.path.join(mp_dir, "pages", "index")
    duel_dir = os.path.join(mp_dir, "pages", "duel")
    data_dir = os.path.join(mp_dir, "data")
    assets_out_dir = os.path.join(mp_dir, "assets")
    for d in (pages_dir, duel_dir, data_dir, assets_out_dir):
        os.makedirs(d, exist_ok=True)

    attack_src = os.path.join(ROOT_DIR, "assets", "icon_attack.png")
    if os.path.exists(attack_src):
        shutil.copy2(attack_src, os.path.join(assets_out_dir, "icon_attack.png"))
    mp_icons_dir = os.path.join(ROOT_DIR, "assets", "mp_icons")
    if os.path.isdir(mp_icons_dir):
        for fn in os.listdir(mp_icons_dir):
            if fn.endswith(".png"):
                shutil.copy2(os.path.join(mp_icons_dir, fn), os.path.join(assets_out_dir, fn))

    print("正在抓取并准备小程序全量数据集...")
    write_miniprogram_dataset(data_dir)

    project_config = {
        "projectname": PROJECT_NAME,
        "description": "王者出装箱 - 微信原生双轨推演小程序",
        "appid": APPID,
        "setting": {"urlCheck": False, "es6": True, "postcss": True, "minified": True},
        "compileType": "miniprogram",
        "condition": {
            "miniprogram": {
                "list": [
                    {"name": "挑选演练英雄大厅", "pathName": "pages/index/index", "query": ""},
                    {"name": "双轨实战推演室", "pathName": "pages/duel/duel", "query": "heroName=赵云&lane=打野"},
                ]
            }
        },
    }
    with open(os.path.join(mp_dir, "project.config.json"), "w", encoding="utf-8") as f:
        json.dump(project_config, f, ensure_ascii=False, indent=2)

    sitemap = {"desc": "Sitemap", "rules": [{"action": "allow", "page": "*"}]}
    with open(os.path.join(mp_dir, "sitemap.json"), "w", encoding="utf-8") as f:
        json.dump(sitemap, f, ensure_ascii=False, indent=2)

    app_json = {
        "pages": ["pages/index/index", "pages/duel/duel"],
        "window": {
            "navigationBarBackgroundColor": "#ffffff",
            "navigationBarTextStyle": "black",
            "navigationBarTitleText": "王者出装推演",
            "backgroundColor": "#f8f9fa",
            "backgroundTextStyle": "light",
        },
        "sitemapLocation": "sitemap.json",
    }
    with open(os.path.join(mp_dir, "app.json"), "w", encoding="utf-8") as f:
        json.dump(app_json, f, ensure_ascii=False, indent=2)

    with open(os.path.join(mp_dir, "app.js"), "w", encoding="utf-8") as f:
        f.write("App({\n  onLaunch() {\n    console.log('王者出装推演小程序已启动');\n  }\n});\n")
    with open(os.path.join(mp_dir, "app.wxss"), "w", encoding="utf-8") as f:
        f.write(_read_tpl("app.wxss"))

    # Page 1: 英雄大厅 (pages/index/)
    hall_json = {
        "navigationBarTitleText": "王者出装推演",
        "navigationBarBackgroundColor": "#ffffff",
        "navigationBarTextStyle": "black",
    }
    with open(os.path.join(pages_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(hall_json, f, ensure_ascii=False, indent=2)
    with open(os.path.join(pages_dir, "index.wxml"), "w", encoding="utf-8") as f:
        f.write(_read_tpl("hall.wxml"))
    with open(os.path.join(pages_dir, "index.wxss"), "w", encoding="utf-8") as f:
        f.write(_read_tpl("hall.wxss"))
    with open(os.path.join(pages_dir, "index.js"), "w", encoding="utf-8") as f:
        f.write(_read_tpl("hall.js"))

    # Page 2: 双轨实战推演室 (pages/duel/)
    duel_json = {
        "navigationBarTitleText": "双轨实战推演",
        "navigationBarBackgroundColor": "#ffffff",
        "navigationBarTextStyle": "black",
    }
    with open(os.path.join(duel_dir, "duel.json"), "w", encoding="utf-8") as f:
        json.dump(duel_json, f, ensure_ascii=False, indent=2)
    with open(os.path.join(duel_dir, "duel.wxml"), "w", encoding="utf-8") as f:
        f.write("\n".join([
            _read_tpl("duel_top_builds.wxml"),
            _read_tpl("duel_combat_stats.wxml"),
            _read_tpl("duel_modals.wxml"),
        ]))
    wxss_files = sorted(fn for fn in os.listdir(TPL_DIR) if fn.startswith("duel_wxss_") and fn.endswith(".wxss"))
    with open(os.path.join(duel_dir, "duel.wxss"), "w", encoding="utf-8") as f:
        f.write("\n".join(_read_tpl(fn) for fn in wxss_files))

    with open(os.path.join(duel_dir, "duel.js"), "w", encoding="utf-8") as f:
        f.write(_assemble_duel_js())

    helper_js_files = [
        "calc.js", "calc_combat.js",
        "mechanic_engine.js",
        "skill_breakdown.js", "skill_breakdown_cards.js",
        "sheet_gesture.wxs",
    ]
    for js_name in helper_js_files:
        with open(os.path.join(duel_dir, js_name), "w", encoding="utf-8") as f:
            f.write(_read_tpl(js_name))

    print(f"成功构建 1:1 复刻版微信小程序项目至：'{mp_dir}'！")


if __name__ == "__main__":
    generate_miniprogram_project()
