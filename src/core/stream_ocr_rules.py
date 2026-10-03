# -*- coding: utf-8 -*-
"""
王者荣耀 S45 全局 1D 物理长卷轴解析流水线 - 业务校验与铭文出装规则引擎 (SSOT)
"""

from config.hero_arcana_data import HERO_RECOMMENDED_ARCANA

# 基础小件散件过滤黑名单（严禁二级散件与演进装混入常规六神装）
BASIC_COMPONENTS = {
    '铁剑', '匕首', '红玛瑙', '布甲', '抗魔披风', '咒术典籍', '蓝宝石', '学识宝石', 
    '狩猎宽刃', '弃鳞短刃', '提神水晶', '吸血之镰', '雷鸣刃', '风暴巨剑', '日冕',
    '狂暴双刃', '陨星', '熔炼之心', '魅影面罩', '大棒', '光辉之剑', '守护者之铠',
    '神速之靴', '荆棘护手', '血族之书', '血魂刃', '速击之枪', '魔道之石', '破碎圣杯',
    '预言水晶', '结霜预言', '进化水晶', '抗魔长袍', '力量腰带', '神隐斗篷', '雪山圆盾',
    '迅捷长矛', '巡守利斧', '追击刀锋', '游击弯刀',
    '穿云弓', '秘法残页', '近卫', '极影', '云灵木', '圣者法典',
    '玛瑙护心镜', '元流结晶', '元流晶石', '魅影', '出林之怒', '风之长袍',
    '精钢锻刀', '附魔之羽', '天地石', '急速铠甲', '原初遗珠', '搏击拳套',
    '不动·天穹'
}
SHOES = {'影忍之足', '抵抗之靴', '冷静之靴', '秘法之靴', '急速战靴', '疾步之靴'}
SUPPORT_ITEMS = {
    '近卫·形昭', '极影·形昭', '近卫·救赎', '极影·救赎', 
    '近卫·星泉', '极影·星泉', '近卫·奔狼', '极影·奔狼'
}
JUNGLE_BLADES = {'贪婪之噬', '巨人之握', '符文大剑'}

RED_ARCANA = {'圣人', '传承', '异变', '纷争', '无双', '宿命', '梦魇', '凶兆', '祸源', '红月'}
BLUE_ARCANA = {'长生', '贪婪', '夺萃', '兽痕', '冥想', '繁荣', '轮回', '调和', '隐匿', '狩猎'}
GREEN_ARCANA = {'霸者', '均衡', '虚空', '灵山', '献祭', '鹰眼', '心眼', '怜悯', '敬畏', '回声'}
ALL_VALID_ARCANA = RED_ARCANA | BLUE_ARCANA | GREEN_ARCANA

ARCANA_TYPO_MAP = {
    '梦魔': '梦魇', '魔': '梦魇', '特猎': '狩猎', '猎': '狩猎',
    '隐圈': '隐匿', '隐愿': '隐匿', '脆医': '隐匿', '脆': '隐匿', '隐': '隐匿',
    '调合': '调和', '心跟': '心眼', '鹰跟': '鹰眼', '鹰良': '鹰眼', '眼': '鹰眼',
    '祸原': '祸源', '冷焖': '怜悯', '怜帆': '怜悯', '冷': '怜悯', '焖': '怜悯', '帆': '怜悯',
    '怜': '怜悯', '怜阀': '怜悯', '冷阀': '怜悯', '岭焖': '怜悯',
    '贪梦': '贪婪', '贪': '贪婪', '长': '长生'
}

from config.hero_arcana_data import HERO_RECOMMENDED_ARCANA

HERO_BENCHMARK = dict(HERO_RECOMMENDED_ARCANA)
HERO_BENCHMARK.update({
    '敖隐': {'red': '祸源', 'blue': '夺萃', 'green': '鹰眼'},
    '傲隐': {'red': '祸源', 'blue': '夺萃', 'green': '鹰眼'},
    '戈娅': {'red': '祸源', 'blue': '狩猎', 'green': '鹰眼'},
    '戈雅': {'red': '祸源', 'blue': '狩猎', 'green': '鹰眼'},
    '弈星': {'red': '梦魇', 'blue': '狩猎', 'green': '心眼'},
    '奕星': {'red': '梦魇', 'blue': '狩猎', 'green': '心眼'},
    '阿轲': {'red': '无双', 'blue': '隐匿', 'green': '鹰眼'},
    '阿珂': {'red': '无双', 'blue': '隐匿', 'green': '鹰眼'},
    '元流之子(刺客)': {'red': '异变', 'blue': '隐匿', 'green': '鹰眼'},
    '元流之子(法师)': {'red': '梦魇', 'blue': '狩猎', 'green': '心眼'},
    '元流之子(坦克)': {'red': '宿命', 'blue': '调和', 'green': '虚空'},
    '元流之子(射手)': {'red': '祸源', 'blue': '夺萃', 'green': '鹰眼'},
    '元流之子(辅助)': {'red': '宿命', 'blue': '调和', 'green': '虚空'},
    '海月': {'red': '圣人', 'blue': '调和', 'green': '献祭'},
    '橘右京': {'red': '异变', 'blue': '隐匿', 'green': '鹰眼'},
    '刘备': {'red': '异变', 'blue': '狩猎', 'green': '鹰眼'},
    '李信': {'red': '异变', 'blue': '隐匿', 'green': '鹰眼'},
    '卢雅娜': {'red': '祸源', 'blue': '狩猎', 'green': '鹰眼'},
    '吕布': {'red': '传承', 'blue': '隐匿', 'green': '虚空'},
    '娜可露露': {'red': '异变', 'blue': '隐匿', 'green': '鹰眼'},
    '钟馗': {'red': '梦魇', 'blue': '调和', 'green': '心眼'},
    '雅典娜': {'red': '祸源', 'blue': '夺萃', 'green': '鹰眼'},
})

def fix_scheme_arcana(hero, lane, s_name, arcana):
    # 用户明确校准：海月官方标准铭文
    if hero == '海月':
        return [[10, '圣人'], [9, '调和'], [1, '轮回'], [10, '献祭']]
    # 艾琳法装输出流官方标准暴击吸血铭文
    if hero == '艾琳' and ('法装' in s_name or ('输出' in s_name and '物' not in s_name)):
        return [[10, '无双'], [10, '贪婪'], [10, '心眼']]

    merged = {}
    for item in arcana:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            cnt, name = item
        else:
            continue
        name = ARCANA_TYPO_MAP.get(name, name)
        if name in ALL_VALID_ARCANA:
            merged[name] = merged.get(name, 0) + cnt
            
    red_sum = sum(c for n, c in merged.items() if n in RED_ARCANA)
    blue_sum = sum(c for n, c in merged.items() if n in BLUE_ARCANA)
    green_sum = sum(c for n, c in merged.items() if n in GREEN_ARCANA)
    
    bench = HERO_BENCHMARK.get(hero, {'red': '异变', 'blue': '隐匿', 'green': '鹰眼'})
    
    # OCR 边缘粘连纠错：当某色铭文仅单一类型且识别为 9 时，自动修正为 10
    for n, c in list(merged.items()):
        if c == 9:
            if (n in RED_ARCANA and red_sum == 9) or (n in BLUE_ARCANA and blue_sum == 9) or (n in GREEN_ARCANA and green_sum == 9):
                merged[n] = 10
                
    red_sum = sum(c for n, c in merged.items() if n in RED_ARCANA)
    blue_sum = sum(c for n, c in merged.items() if n in BLUE_ARCANA)
    green_sum = sum(c for n, c in merged.items() if n in GREEN_ARCANA)
    
    if red_sum < 10:
        diff = 10 - red_sum
        r_name = bench['red']
        merged[r_name] = merged.get(r_name, 0) + diff
    if blue_sum < 10:
        diff = 10 - blue_sum
        b_name = bench['blue']
        merged[b_name] = merged.get(b_name, 0) + diff
    if green_sum < 10:
        diff = 10 - green_sum
        g_name = bench['green']
        merged[g_name] = merged.get(g_name, 0) + diff
        
    res = []
    for n in sorted(merged.keys(), key=lambda x: (0 if x in RED_ARCANA else (1 if x in BLUE_ARCANA else 2), -merged[x])):
        res.append([merged[n], n])
    return res

def validate_and_refine_scheme(hero, lane, scheme_name, items):
    refined = list(items)
    # 1. 过滤任何二级散件与不动天穹，规范官方标准装备名
    for i in range(len(refined)):
        if refined[i] in BASIC_COMPONENTS or refined[i] == '不动·天穹':
            if refined[i] in ['穿云弓', '金色圣剑']:
                refined[i] = '幽影袖箭'
            elif refined[i] == '不动·天穹':
                refined[i] = '纯净苍穹'
        if refined[i] == '贤者天书':
            refined[i] = '贤者之书'

    # 2. 游走与打野分路硬性约束 (规则①与规则④)
    is_support_lane = (lane == '游走')
    is_jungle_lane = (lane == '打野')

    if is_support_lane:
        if not (refined[0] in SUPPORT_ITEMS):
            for idx, it in enumerate(refined):
                if it in SUPPORT_ITEMS:
                    refined.pop(idx)
                    refined.insert(0, it)
                    break
            else:
                refined[0] = '近卫·形昭'
    else:
        for i in range(len(refined)):
            if refined[i] in SUPPORT_ITEMS:
                refined[i] = '暴烈之甲' if '暴烈之甲' not in refined else '魔女斗篷'

    if is_jungle_lane:
        if not (refined[0] in JUNGLE_BLADES):
            for idx, it in enumerate(refined):
                if it in JUNGLE_BLADES:
                    refined.pop(idx)
                    refined.insert(0, it)
                    break
            else:
                if hero in ['嫦娥', '司空震', '司马懿', '诸葛亮']:
                    refined[0] = '符文大剑'
                elif hero in ['白起', '夏侯惇', '亚瑟', '猪八戒', '程咬金', '赵怀真', '钟无艳'] or '肉' in scheme_name:
                    refined[0] = '巨人之握'
                else:
                    refined[0] = '贪婪之噬'
    else:
        for i in range(len(refined)):
            if refined[i] in JUNGLE_BLADES:
                refined[i] = '暗影战斧' if '暗影战斧' not in refined else '纯净苍穹'

    # 3. 射手幽影袖箭纠错（针对射手把幽影袖箭误判为金色圣剑/穿云弓的问题）
    if hero in ['百里守约', '苍', '后羿', '黄忠', '伽罗', '莱西奥', '元流之子(射手)', '狄仁杰']:
        for i in range(len(refined)):
            if refined[i] in ['金色圣剑', '穿云弓']:
                refined[i] = '幽影袖箭'

    # 4. 特定英雄鞋子与专属流派真机纠偏 (解决用户 55 处具体反馈)
    if hero == '赵云' and lane == '对抗':
        if '肉' in scheme_name:
            refined[0] = '影忍之足'
        elif len(refined) > 1 and refined[1] in SHOES:
            refined[1] = '影忍之足'
    if hero == '关羽':
        for i in range(len(refined)):
            if refined[i] in SHOES:
                refined[i] = '抵抗之靴'
    if hero == '钟无艳' and lane == '打野':
        for i in range(len(refined)):
            if refined[i] in SHOES:
                refined[i] = '抵抗之靴'
    if hero == '庄周' and lane == '对抗':
        for i in range(len(refined)):
            if refined[i] in SHOES:
                refined[i] = '影忍之足'

    return refined

# 全局 Worker 变量
worker_ocr = None
worker_tpl_list = []
doc_handles = {}

def init_worker():
    global worker_ocr, worker_tpl_list
    worker_ocr = RapidOCR()
    
    with open('.cache/json/a6cd7ea78d2dfc098426715c83bbaadc.json', 'r', encoding='utf-8') as f:
        items_raw = json.load(f)
    item_dict = {str(item['item_id']): item['item_name'] for item in items_raw}
    
    worker_tpl_list = []
    for p in glob.glob('.cache/item_icons/*.png'):
        iid = os.path.splitext(os.path.basename(p))[0]
        name = item_dict.get(iid, iid)
        tpl = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if tpl is None or tpl.shape[2] != 4:
            continue
        if name in BASIC_COMPONENTS and name not in SHOES:
            continue
        worker_tpl_list.append((iid, name, tpl))

def match_slot_fast(crop, exclude_shoes=False):
    global worker_tpl_list
    h_c, w_c = crop.shape[:2]
    best_item = ''
    best_score = -1
    for iid, name, tpl in worker_tpl_list:
        if exclude_shoes and name in SHOES:
            continue
        tw, th = int(w_c * 0.90), int(h_c * 0.90)
        t_resized = cv2.resize(tpl, (tw, th))
        mask = (t_resized[:, :, 3] > 128).astype(np.uint8) * 255
        if np.sum(mask) < 200:
            continue
        t_bgr = t_resized[:, :, :3]
        res = cv2.matchTemplate(crop, t_bgr, cv2.TM_CCOEFF_NORMED, mask=mask)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_score:
            best_score = max_val
            best_item = name
    return best_item, best_score

def get_doc_handle(pdf_path):
    global doc_handles
    if pdf_path not in doc_handles:
        doc_handles[pdf_path] = pymupdf.open(pdf_path)
    return doc_handles[pdf_path]

