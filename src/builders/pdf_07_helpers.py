# -*- coding: utf-8 -*-
"""
王者荣耀 S45 全英雄全分路官方推荐出装与铭文大全 - 出版级矢量图文 PDF 构建器
对标 Apple 极简出版物排版，全面内嵌官方高清头像、装备图标、铭文图鉴
"""

import os
import sys
import re
import json
import shutil
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.hero_registry import CN_HERO_MANIFEST

CACHE_DIR = os.path.join(PROJECT_ROOT, "taobao", "assets_cache").replace("\\", "/")
CSS_LAYOUT_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_layout.css")
CSS_COMPONENTS_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_components.css")
CSS_BRAND_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_brand.css")
PDF_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "templates", "pdf", "pdf_template.html")

HERO_MAP = {data["cname"]: ename for ename, data in CN_HERO_MANIFEST.items()}
HERO_TITLES = {data["cname"]: data.get("title", "") for ename, data in CN_HERO_MANIFEST.items()}

# 载入装备与铭文字典
with open(os.path.join(PROJECT_ROOT, "sandbox.html"), "r", encoding="utf-8") as f:
    sandbox_raw = f.read()

m_items = re.search(r'const ITEMS_DATA = (\[.*?\]);', sandbox_raw)
m_arcana = re.search(r'const ARCANA_DATA = (\{.*?\});', sandbox_raw)

ITEMS_LIST = json.loads(m_items.group(1)) if m_items else []
ARCANA_DICT = json.loads(m_arcana.group(1)) if m_arcana else {}

ITEM_MAP = {item["item_name"]: str(item["item_id"]) for item in ITEMS_LIST}
ARCANA_MAP = {name: str(data["id"]) for name, data in ARCANA_DICT.items()}

RED_ARCANA = {'圣人', '传承', '异变', '纷争', '无双', '宿命', '梦魇', '凶兆', '祸源', '红月'}
BLUE_ARCANA = {'长生', '贪婪', '夺萃', '兽痕', '冥想', '繁荣', '轮回', '调和', '隐匿', '狩猎'}
GREEN_ARCANA = {'霸者', '均衡', '虚空', '灵山', '献祭', '鹰眼', '心眼', '怜悯', '敬畏', '回声'}

HERO_AVATAR_ALIASES = {
    '敖隐': '519', '傲隐': '519',
    '戈娅': '548', '戈雅': '548',
    '弈星': '197', '奕星': '197',
    '元流之子(坦克)': '581', '元流之子（坦克）': '581',
    '元流之子(法师)': '582', '元流之子（法师）': '582', '元流之子(中路)': '582', '元流之子（中路）': '582',
    '元流之子(刺客)': '583', '元流之子（刺客）': '583',
    '元流之子(射手)': '584', '元流之子（射手）': '584',
    '元流之子(辅助)': '585', '元流之子（辅助）': '585',
}

MAINSTREAM_HEROES = {
    # 对抗路主流
    "吕布", "孙策", "亚瑟", "铠", "夏洛特", "花木兰", "司空震", "李信", "马超", "狂铁", 
    "芈月", "姬小满", "亚连", "大司命", "影", "老夫子", "达摩", "关羽", "项羽", "程咬金",
    # 打野主流
    "孙悟空", "韩信", "李白", "赵云", "典韦", "兰陵王", "阿轲", "百里玄策", "露娜", "曜", 
    "云缨", "娜可露露", "橘右京", "刘备", "宫本武藏", "裴擒虎", "暃", "云中君",
    # 中路主流
    "安琪拉", "妲己", "甄姬", "小乔", "王昭君", "诸葛亮", "貂蝉", "墨子", "张良", "上官婉儿", 
    "干将莫邪", "不知火舞", "海月", "少司缘", "沈梦溪", "西施", "周瑜", "嬴政",
    # 发育路主流
    "鲁班七号", "孙尚香", "马可波罗", "后羿", "狄仁杰", "百里守约", "伽罗", "黄忠", "公孙离", 
    "虞姬", "李元芳", "莱西奥", "敖隐", "蒙犽",
    # 游走主流
    "瑶", "蔡文姬", "庄周", "东皇太一", "大乔", "朵莉亚", "孙膑", "刘禅", "钟馗", "张飞", "桑启", "牛魔"
}

def resolve_item_id(name: str):
    if name in ['贤者天书', '贤者之书']:
        return '1238'
    if name == '幽影袖箭':
        return '1161'
    if name in ITEM_MAP:
        return ITEM_MAP[name]
    for prefix in ['仁者', '强者', '王者', '不动·', '初级']:
        clean = name.replace(prefix, '')
        if clean in ITEM_MAP:
            return ITEM_MAP[clean]
    for iname, iid in ITEM_MAP.items():
        if iname in name or name in iname:
            return iid
    return None

def get_hero_avatar(cname: str) -> str:
    ename = HERO_AVATAR_ALIASES.get(cname) or HERO_MAP.get(cname, "")
    local_p = f"{CACHE_DIR}/hero/{ename}.jpg"
    return f"file:///{local_p}" if os.path.exists(local_p) else ""

def get_item_icon(iname: str) -> str:
    iid = resolve_item_id(iname)
    if iid:
        local_p = f"{CACHE_DIR}/item/{iid}.png"
        if os.path.exists(local_p):
            return f"file:///{local_p}"
    return ""

def get_arcana_icon(aname: str) -> str:
    aid = ARCANA_MAP.get(aname, "")
    if aid:
        local_p = f"{CACHE_DIR}/arcana/{aid}.png"
        if os.path.exists(local_p):
            return f"file:///{local_p}"
    return ""

def get_arcana_color(aname: str) -> str:
    if aname in RED_ARCANA: return "红色"
    if aname in BLUE_ARCANA: return "蓝色"
    if aname in GREEN_ARCANA: return "绿色"
    return "红色"

