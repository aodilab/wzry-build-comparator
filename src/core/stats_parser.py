# -*- coding: utf-8 -*-
"""
技能数值阶梯与成长解析引擎
将官方技能文本中以斜杠 '/' 分隔的多等级数值自动解析为结构化成长线
"""
import re

def parse_level_sequence(text):
    """
    匹配文本中类似 150/170/190/210/230/250 或 11/10.4/9.8/9.2/8.6/8 的成长序列
    支持带单位如 45s / 40s / 35s
    """
    if not text:
        return []
    normalized = re.sub(r'(\d+(?:\.\d+)?)\s*(?:s|秒)\b', r'\1', text)
    pattern = r'(\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?){2,5})'
    matches = re.findall(pattern, normalized)
    if matches:
        return [re.sub(r'\s+', '', m) for m in matches]
    return []

def format_cd_steps(cd_text, is_ult=False):
    """
    格式化技能冷却时间阶梯
    输入 '11/10.4/9.8/9.2/8.6/8' -> 'Lv1: 11s ｜ Lv2: 10.4s ｜ Lv3: 9.8s ｜ Lv4: 9.2s ｜ Lv5: 8.6s ｜ Lv6: 8s'
    支持 '9(-0.4/Lv)' 或 '9-0.4/Lv'
    """
    if not cd_text or cd_text in ["无", "0", "0秒"]:
        return "无冷却 / 被动触发"

    seqs = parse_level_sequence(cd_text)
    if seqs:
        steps = seqs[0].split('/')
        return " ｜ ".join([f"Lv{i+1}: {v}s" for i, v in enumerate(steps)])

    # 匹配 X(-Y/Lv) 或 X-Y/Lv 递减成长格式
    step_match = re.search(r'(\d+(?:\.\d+)?)\s*\(?-\s*(\d+(?:\.\d+)?)\s*/\s*[Ll][Vv]\)?', cd_text)
    if step_match:
        base = float(step_match.group(1))
        step = float(step_match.group(2))
        max_lv = 3 if (is_ult or base >= 20 or step >= 1.0) else 6
        vals = []
        for i in range(max_lv):
            v = round(base - step * i, 2)
            v_str = str(int(v)) if v.is_integer() else f"{v:g}"
            vals.append(f"Lv{i+1}: {v_str}s")
        extra = re.sub(r'^\d+(?:\.\d+)?\s*\(?-\s*\d+(?:\.\d+)?\s*/\s*[Ll][Vv]\)?', '', cd_text).strip()
        suffix = f" {extra}" if extra else ""
        return " ｜ ".join(vals) + suffix

    # 范围冷却格式如 6s - 4.5s 或 10-7秒
    if "-" in cd_text:
        return cd_text.strip()

    # 固定冷却
    clean_val = re.sub(r'[^\d\.]', '', cd_text)
    return f"固定 {clean_val}s" if clean_val else cd_text

def format_cost_steps(cost_text, is_ult=False):
    """
    格式化法力/能量消耗阶梯
    输入 '50/55/60/65/70/75' -> 'Lv1: 50 ｜ Lv2: 55 ｜ Lv3: 60 ｜ Lv4: 65 ｜ Lv5: 70 ｜ Lv6: 75'
    支持 '50(+10/Lv)' 或 '65+5/lv'
    """
    if not cost_text or cost_text in ["无", "0", "0消耗"]:
        return "无消耗"

    seqs = parse_level_sequence(cost_text)
    if seqs:
        steps = seqs[0].split('/')
        return " ｜ ".join([f"Lv{i+1}: {v}" for i, v in enumerate(steps)])

    step_match = re.search(r'(\d+(?:\.\d+)?)\s*\(?\+\s*(\d+(?:\.\d+)?)\s*/\s*[Ll][Vv]\)?', cost_text)
    if step_match:
        base = float(step_match.group(1))
        step = float(step_match.group(2))
        max_lv = 3 if (is_ult or base >= 80) else 6
        vals = []
        for i in range(max_lv):
            v = round(base + step * i, 2)
            v_str = str(int(v)) if v.is_integer() else f"{v:g}"
            vals.append(f"Lv{i+1}: {v_str}")
        return " ｜ ".join(vals)

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
