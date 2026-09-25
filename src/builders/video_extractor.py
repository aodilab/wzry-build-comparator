# -*- coding: utf-8 -*-
"""
王者荣耀官方录屏出装与铭文全量自动化提取流水线
从 raw_assets/recordings/出装铭文EP1.MP4 和 EP2.MP4 中完整提取：
1. 真实全英雄与官方支持分路 (supported_lanes)
2. 官方推荐3套出装方案 (属性Tag, 流派Genre, 官方思路Desc, 6件神装)
3. 强绑定的150级官方铭文 (通过弹窗描述文字精准关联)
"""
import os
import sys
import re
import json
import glob
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, BASE_DIR)
from config.hero_registry import CN_HERO_MANIFEST
from config.hero_arcana_data import ARCANA_LEVEL_5_DICT

def load_item_templates():
    with open(os.path.join(BASE_DIR, '.cache', 'json', 'a6cd7ea78d2dfc098426715c83bbaadc.json'), 'r', encoding='utf-8') as f:
        items = json.load(f)
    id2name = {str(it['item_id']): it['item_name'] for it in items}
    
    templates = {}
    icon_dir = os.path.join(BASE_DIR, '.cache', 'item_icons')
    for p in glob.glob(os.path.join(icon_dir, '*.*')):
        iid = os.path.splitext(os.path.basename(p))[0]
        img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if img is not None:
            if img.shape[2] == 4:
                b, g, r, a = cv2.split(img)
                h, w = a.shape
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(mask, (w//2, h//2), min(w, h)//2 - 2, 255, -1)
                a = cv2.bitwise_and(a, mask)
                rgb = cv2.merge([b, g, r])
                alpha = a.astype(float) / 255.0
                rgb = (rgb * alpha[:, :, None]).astype(np.uint8)
                templates[iid] = rgb
            else:
                templates[iid] = img
    return id2name, templates

def match_single_item(patch, templates, id2name):
    hp, wp, _ = patch.shape
    best_score = -1
    best_name = ''
    for iid, tpl in templates.items():
        resized = cv2.resize(tpl, (wp, hp))
        res = cv2.matchTemplate(patch, resized, cv2.TM_CCOEFF_NORMED)
        score = np.max(res)
        if score > best_score:
            best_score = score
            best_name = id2name.get(iid, iid)
    return best_name, best_score

def extract_items_from_row(strip, templates, id2name):
    """从出装行的图像条中提取6件装备"""
    gray = cv2.cvtColor(strip, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=70, param1=50, param2=30, minRadius=35, maxRadius=65)
    items = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype('int')
        circles = sorted(circles, key=lambda c: c[0])
        for x, y, r in circles:
            crop = strip[max(0, y-r):min(strip.shape[0], y+r), max(0, x-r):min(strip.shape[1], x+r)]
            if crop.shape[0] < 10 or crop.shape[1] < 10:
                continue
            name, score = match_single_item(crop, templates, id2name)
            if score > 0.45:
                items.append((name, score, x))
    items = sorted(items, key=lambda it: it[2])
    alias_map = {'强者破军': '破军', '仁者破晓': '破晓', '贤者天书': '贤者之书', '急速之靴': '急速战靴'}
    return [alias_map.get(it[0], it[0]) for it in items[:6]]

def parse_arcana_text(text):
    """解析铭文文本，例如 '10异变10隐匿 10鹰眼' -> 字典"""
    all_arcana_names = list(ARCANA_LEVEL_5_DICT.keys())
    result = {'red': {}, 'blue': {}, 'green': {}}
    matches = re.findall(r'(\d+)\s*([\u4e00-\u9fa5]{2,4})', text)
    for count_str, name in matches:
        count = int(count_str)
        matched_name = None
        for a_name in all_arcana_names:
            if a_name == name or (len(name) >= 2 and name in a_name):
                matched_name = a_name
                break
        if matched_name:
            color = ARCANA_LEVEL_5_DICT[matched_name].get('color_type', 'red')
            result[color][matched_name] = count
    return result

def extract_from_video(video_path, existing_data=None):
    if not os.path.exists(video_path):
        print(f'视频未找到: {video_path}')
        return existing_data or {}
    
    ocr = RapidOCR()
    cnames = {v['cname'] for v in CN_HERO_MANIFEST.values()}
    id2name, templates = load_item_templates()
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(total_frames / fps) if fps > 0 else 0
    print(f'正在解析视频 {os.path.basename(video_path)}: 总时长 {duration} 秒...')

    data = existing_data or {}
    current_hero = None
    current_lane = '对抗路'

    # 以 1.5 秒为步长顺序抽帧
    step_sec = 1.5
    sec = 0.0
    while sec < duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, int(sec * 1000))
        ret, frame = cap.read()
        if not ret:
            sec += step_sec
            continue
        
        # 1. 检测当前英雄（底栏 x: 380..540, y: 960..1040）
        hero_crop = frame[960:1040, 380:540]
        res_h, _ = ocr(hero_crop)
        for r in (res_h or []):
            for cn in cnames:
                if cn in r[1]:
                    current_hero = cn
                    break
        
        # 2. 检测当前分路（右上角下拉框 x: 2000..2250, y: 35..90）
        lane_crop = frame[35:90, 2000:2250]
        res_l, _ = ocr(lane_crop)
        for r in (res_l or []):
            for l in ['对抗路', '打野', '中路', '发育路', '游走']:
                if l in r[1]:
                    current_lane = l
                    break

        if not current_hero:
            sec += step_sec
            continue

        # 初始化英雄数据节点
        if current_hero not in data:
            data[current_hero] = {
                'supported_lanes': [],
                'lanes': {}
            }
        if current_lane not in data[current_hero]['supported_lanes']:
            data[current_hero]['supported_lanes'].append(current_lane)
        if current_lane not in data[current_hero]['lanes']:
            data[current_hero]['lanes'][current_lane] = []

        lane_builds = data[current_hero]['lanes'][current_lane]

        # 3. 检查是否处于展开的铭文/出装详情弹窗 (检测应用装备按钮或 150 铭文标志)
        check_modal = frame[960:1040, 450:580]
        res_m, _ = ocr(check_modal)
        is_modal = any('150' in r[1] or '铭文' in r[1] for r in (res_m or []))

        if is_modal:
            # 弹窗顶部文字描述 (用于精准关联到对应的出装行)
            modal_desc_crop = frame[700:760, 800:1800]
            res_md, _ = ocr(modal_desc_crop)
            modal_desc = ' '.join([r[1] for r in (res_md or [])]).strip()

            # 铭文行文字
            modal_arc_crop = frame[980:1045, 600:1500]
            res_ma, _ = ocr(modal_arc_crop)
            arc_text = ' '.join([r[1] for r in (res_ma or [])]).strip()
            parsed_arc = parse_arcana_text(arc_text)

            # 在当前已收集或后续收集的 build 中做文字对齐匹配
            if modal_desc and parsed_arc and any(parsed_arc.values()):
                for b in lane_builds:
                    if b.get('desc') and (b['desc'] in modal_desc or modal_desc in b['desc'] or b['genre'] in modal_desc):
                        b['arcana'] = parsed_arc
                        b['arcana_desc'] = arc_text
                        break
        else:
            # 4. 常态出装抽屉（提取 Row 1, Row 2, Row 3）
            rows_meta = [
                (1, (140, 200), (220, 360)),
                (2, (420, 480), (480, 620)),
                (3, (700, 760), (760, 900))
            ]
            for row_idx, (text_y1, text_y2), (item_y1, item_y2) in rows_meta:
                t_crop = frame[text_y1:text_y2, 650:1800]
                res_t, _ = ocr(t_crop)
                row_text = ' '.join([r[1] for r in (res_t or [])]).strip()
                if not row_text:
                    continue
                
                # 解析 Tag (生存/输出/均衡) 与 Genre (流派)
                tag = '均衡'
                if '生存' in row_text: tag = '生存'
                elif '输出' in row_text: tag = '输出'

                # 提取流派名与思路描述
                genre_match = re.search(r'(半肉流|输出流|纯肉流|暴击流|法球流|法坦流|穿透流|肉装流|CD流|均衡流|游走流|高爆流|坦伤流|极速流|法核流|秒人流)', row_text)
                genre = genre_match.group(1) if genre_match else (row_text.split()[0] if row_text.split() else f'方案{row_idx}')
                desc = row_text.replace(tag, '').replace(genre, '').strip()
                if not desc:
                    desc = f'官方推荐{current_lane}{genre}实战经典搭配。'

                # 提取装备
                items = extract_items_from_row(frame[item_y1:item_y2, 700:1700], templates, id2name)
                if len(items) >= 4:
                    # 检查是否已收录该方案
                    exist = next((b for b in lane_builds if b['genre'] == genre or b['desc'] == desc), None)
                    if not exist:
                        lane_builds.append({
                            'id': f'build_{len(lane_builds)+1}',
                            'tag': tag,
                            'genre': genre,
                            'title': f'{tag}·{genre}',
                            'desc': desc,
                            'items': items,
                            'item_names': items,
                            'arcana': None,
                            'arcana_desc': ''
                        })

        sec += step_sec

    cap.release()
    print(f'视频 {os.path.basename(video_path)} 解析完毕！已收录 {len(data)} 位英雄的出装与铭文数据。')
    return data

def run_full_pipeline():
    v1 = os.path.join(BASE_DIR, 'raw_assets', 'recordings', '出装铭文EP1.MP4')
    v2 = os.path.join(BASE_DIR, 'raw_assets', 'recordings', '出装铭文EP2.MP4')

    data = {}
    if os.path.exists(v1):
        data = extract_from_video(v1, data)
    if os.path.exists(v2):
        data = extract_from_video(v2, data)

    # 导出结构化 Python 字典
    output_py = os.path.join(BASE_DIR, 'config', 'hero_official_builds.py')
    with open(output_py, 'w', encoding='utf-8') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('"""\n')
        f.write('王者荣耀国服全英雄官方真实推荐出装与铭文全量数据库 (SSOT)\n')
        f.write('数据源：局内录屏高清解析 (包含各分路3套官方推荐、流派思路与强绑定150级铭文)\n')
        f.write('"""\n\n')
        f.write('OFFICIAL_HERO_BUILDS = ' + json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    print(f'【成功】全量官方出装与铭文 SSOT 数据已持久化保存至: {output_py}')
    return data

if __name__ == '__main__':
    run_full_pipeline()
