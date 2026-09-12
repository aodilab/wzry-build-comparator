# -*- coding: utf-8 -*-
"""
技能数值阶梯与成长解析引擎
将官方技能文本中以斜杠 '/' 分隔的多等级数值自动解析为结构化成长线
"""
import re

def parse_level_sequence(text):
    """
    匹配文本中类似 150/170/190/210/230/250 或 11/10.4/9.8/9.2/8.6/8 的成长序列
    """
    if not text:
        return []
    pattern = r'(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?){2,5})'
    return re.findall(pattern, text)

def format_cd_steps(cd_text):
    """
    格式化技能冷却时间阶梯
    输入 '11/10.4/9.8/9.2/8.6/8' -> 'Lv1: 11s ｜ Lv2: 10.4s ｜ Lv3: 9.8s ｜ Lv4: 9.2s ｜ Lv5: 8.6s ｜ Lv6: 8s'
    """
    if not cd_text or cd_text in ["无", "0", "0秒"]:
        return "无冷却 / 被动触发"
    
    seqs = parse_level_sequence(cd_text)
    if seqs:
        steps = seqs[0].split('/')
        return " ｜ ".join([f"Lv{i+1}: {v}s" for i, v in enumerate(steps)])
    
    # 固定冷却
    clean_val = re.sub(r'[^\d\.]', '', cd_text)
    return f"固定 {clean_val}s" if clean_val else cd_text

def format_cost_steps(cost_text):
    """
    格式化法力/能量消耗阶梯
    输入 '50/55/60/65/70/75' -> 'Lv1: 50 ｜ Lv2: 55 ｜ Lv3: 60 ｜ Lv4: 65 ｜ Lv5: 70 ｜ Lv6: 75'
    """
    if not cost_text or cost_text in ["无", "0", "0消耗"]:
        return "无消耗"
        
    seqs = parse_level_sequence(cost_text)
    if seqs:
        steps = seqs[0].split('/')
        return " ｜ ".join([f"Lv{i+1}: {v}" for i, v in enumerate(steps)])
        
    return cost_text

def extract_desc_growth_lines(desc_text):
    """
    提取技能描述中的数值阶梯线（伤害、护盾、回复等成长数值）
    """
    if not desc_text:
        return []
        
    seqs = parse_level_sequence(desc_text)
    results = []
    for s in seqs:
        vals = s.split('/')
        if len(vals) >= 3:
            try:
                growth = float(vals[1]) - float(vals[0])
                growth_str = f" (每级成长: +{growth:.1f})" if growth > 0 else ""
            except ValueError:
                growth_str = ""
            results.append(f"{' / '.join(vals)}{growth_str}")
            
    return results
