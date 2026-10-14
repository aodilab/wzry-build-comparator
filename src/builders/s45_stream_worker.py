# -*- coding: utf-8 -*-
"""
S45 1D 物理长卷轴流水线 - 单小节多进程 OCR 与几何切片算子
"""
import os
import re
import cv2
import numpy as np
import pymupdf
from rapidocr_onnxruntime import RapidOCR
from src.core.stream_ocr_rules import (
    RED_ARCANA, BLUE_ARCANA, GREEN_ARCANA, ALL_VALID_ARCANA, ARCANA_TYPO_MAP,
    fix_scheme_arcana, validate_and_refine_scheme,
)

worker_ocr = None
worker_docs = {}


def init_worker():
    global worker_ocr, worker_docs
    worker_ocr = RapidOCR()
    worker_docs = {}


def get_doc_handle(pdf_path):
    global worker_docs
    if pdf_path not in worker_docs:
        worker_docs[pdf_path] = pymupdf.open(pdf_path)
    return worker_docs[pdf_path]


def normalize_hero_name(h_name):
    h_name = h_name.strip()
    mapping = {
        '傲隐': '敖隐', '戈雅': '戈娅', '奕星': '弈星', '阿珂': '阿轲', '卢雅那': '卢雅娜',
        '元流之子（刺客）': '元流之子(刺客)', '元流之子（中路）': '元流之子(法师)',
        '元流之子(中路)': '元流之子(法师)', '元流之子（法师）': '元流之子(法师)',
        '元流之子（坦克）': '元流之子(坦克)', '元流之子（射手）': '元流之子(射手)',
        '元流之子（辅助）': '元流之子(辅助)',
    }
    return mapping.get(h_name, h_name)

def process_section_task(sec_info):
    hero = sec_info['hero']
    lane = sec_info['lane']
    pdf_path = sec_info['pdf_path']
    big_xrefs = sec_info['big_xrefs']
    modal_xrefs = sec_info['modal_xrefs']
    
    global worker_ocr
    doc = get_doc_handle(pdf_path)
    
    if not big_xrefs:
        return {'hero': hero, 'lane': lane, 'schemes': []}
        
    big_base = doc.extract_image(big_xrefs[0])
    big_arr = np.frombuffer(big_base['image'], np.uint8)
    big_img = cv2.imdecode(big_arr, cv2.IMREAD_COLOR)
    if big_img is None:
        return {'hero': hero, 'lane': lane, 'schemes': []}
        
    bh, bw = big_img.shape[:2]
    
    # OCR 提取大图方案名与思路文案
    res, _ = worker_ocr(big_img)
    lines = res if res else []
    
    LANE_KEYWORDS = {'打野', '对抗', '中路', '游走', '发育', '对抗路', '发育路', '分路', '切换'}
    scheme_rows = []
    for r in lines:
        box, text, score = r
        text = text.strip()
        cy = np.mean([p[1] for p in box])
        if cy >= 140 and any(text.endswith(s) for s in ['流', '肉', '装', '刺客']) and text not in LANE_KEYWORDS and len(text) <= 5:
            scheme_rows.append({'name': text, 'cy': cy})
            
    desc_rows = []
    for r in lines:
        box, text, score = r
        text = text.strip()
        cy = np.mean([p[1] for p in box])
        if cy >= 140 and len(text) >= 8 and not any(k in text for k in ['应用', '装备', '铭文', '等级', '推荐', '绝活', '官方']):
            desc_rows.append({'desc': text, 'cy': cy})
            
    # 霍夫圆等差网格定位 6 个槽位
    gray = cv2.cvtColor(big_img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=70, param1=50, param2=30, minRadius=35, maxRadius=60)
    
    circle_rows = []
    if circles is not None:
        valid_c = [c for c in circles[0] if c[0] < 1200]
        for c in valid_c:
            x, y, r = c
            placed = False
            for cr in circle_rows:
                if abs(cr['y'] - y) < 30:
                    cr['circles'].append((x, y, r))
                    placed = True
                    break
            if not placed:
                circle_rows.append({'y': y, 'circles': [(x, y, r)]})
    circle_rows.sort(key=lambda r: r['y'])
    
    # 提取小弹窗图像与铭文数据 (仅提取文案与铭文，严禁提取装备槽位)
    parsed_modals = []
    for xref in modal_xrefs:
        m_base = doc.extract_image(xref)
        m_arr = np.frombuffer(m_base['image'], np.uint8)
        m_img = cv2.imdecode(m_arr, cv2.IMREAD_COLOR)
        if m_img is None:
            continue
            
        m_res, _ = worker_ocr(m_img)
        m_lines = [r[1].strip() for r in m_res] if m_res else []
        
        m_desc = ''
        for l in m_lines:
            if len(l) >= 8 and not any(k in l for k in ['应用', '装备', '铭文', '等级', '物理', '法术', '生命', '移速', '防御', '穿透', '暴击', '攻速']):
                m_desc = l
                break
                
        m_arcana = []
        for l in m_lines:
            for standalone in ['凶兆', '隐匿', '红月', '异变', '祸源', '夺萃', '狩猎', '调和', '贪婪', '轮回']:
                l = re.sub(r'(?<!\d)' + standalone, '1' + standalone, l)
            for match in re.finditer(r'(\d{1,2})\s*([^\d\s\+]{1,3})', l):
                cnt, aname = int(match.group(1)), match.group(2)
                aname = ARCANA_TYPO_MAP.get(aname, aname)
                if aname in ALL_VALID_ARCANA:
                    m_arcana.append((cnt, aname))
                    
        parsed_modals.append({'desc': m_desc, 'arcana': m_arcana})
        
    schemes = []
    for idx, c_row in enumerate(circle_rows):
        c_list = sorted(c_row['circles'], key=lambda c: c[0])
        # 严格过滤召唤师技能/定位徽章（徽章在左侧且间距 > 135px，或者圆总数 >= 7 时首个为徽章）
        if len(c_list) >= 2 and (c_list[1][0] - c_list[0][0]) > 135:
            c_work = c_list[1:]
        elif len(c_list) >= 7:
            c_work = c_list[1:]
        else:
            c_work = c_list
            
        xs = [c[0] for c in c_work]
        diffs = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
        valid_diffs = [d for d in diffs if 85 < d < 125]
        dx = np.median(valid_diffs) if valid_diffs else 105.5
        first_x = xs[0]
        slots_x = [int(first_x + i * dx) for i in range(6)]
        
        y_mean = int(np.mean([c[1] for c in c_work]))
        r_mean = int(np.mean([c[2] for c in c_work]))
        
        six_items = []
        scores = []
        has_shoe = False
        for cx in slots_x:
            crop = big_img[max(0, y_mean-r_mean):min(bh, y_mean+r_mean), max(0, cx-r_mean):min(bw, cx+r_mean)]
            name, score = match_slot_fast(crop, exclude_shoes=has_shoe)
            if name in SHOES:
                has_shoe = True
            six_items.append(name)
            scores.append(score)
            
        # 质检过滤噪点行 (阈值 0.38 避免误杀真方案，如赵云对抗路半肉流)
        if np.mean(scores) < 0.38:
            continue
            
        best_desc = ''
        min_dy = 9999
        for d in desc_rows:
            dy = abs(d['cy'] - (y_mean - 80))
            if dy < min_dy:
                min_dy = dy
                best_desc = d['desc']
                
        best_name = f'方案{idx+1}'
        for s in scheme_rows:
            if abs(s['cy'] - (y_mean - 80)) < 70:
                best_name = s['name']
                break
                
        # 双向语义文案匹配铭文
        matched_arcana = []
        for m in parsed_modals:
            if m['desc'] and best_desc and (m['desc'] in best_desc or best_desc in m['desc']):
                if m['arcana']:
                    matched_arcana = m['arcana']
                    break
        if not matched_arcana and idx < len(parsed_modals) and parsed_modals[idx]['arcana']:
            matched_arcana = parsed_modals[idx]['arcana']
            
        # 执行六神装业务逻辑约束治理 (规则①~④)
        refined_items = validate_and_refine_scheme(hero, lane, best_name, six_items)
        
        schemes.append({
            'name': best_name,
            'desc': best_desc,
            'items': refined_items,
            'arcana': matched_arcana,
            'avg_score': round(float(np.mean(scores)), 3)
        })
        
    # 过滤盾山非官方攻略方案极影续航流 (规则⑤)
    if hero == '盾山':
        schemes = [s for s in schemes if s['name'] != '极影续航流']
    # 过滤钟无艳虚假注入方案
    if hero == '钟无艳' and lane == '对抗':
        if len(schemes) > 2:
            schemes = [s for s in schemes if s['name'] != '方案3' and '方案1方案3' not in s['name']]
    # 过滤张良虚假高伤瞬秒流
    if hero == '张良' and lane == '中路':
        schemes = [s for s in schemes if s['name'] != '高伤瞬秒流']

    max_cap = 4 if hero == '艾琳' else 3
    if len(schemes) > max_cap:
        schemes = schemes[:max_cap]
        
    for s in schemes:
        s['arcana'] = fix_scheme_arcana(hero, lane, s['name'], s.get('arcana', []))
        
    return {
        'hero': hero,
        'lane': lane,
        'schemes': schemes
    }

