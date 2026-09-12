# -*- coding: utf-8 -*-
"""
数据清洗与富文本格式化工具
去除网页脏标签，针对 Markdown 与 RAG 检索进行优化
"""
import re
import html
import unicodedata

def normalize_text(text):
    """将全角字符、特殊空格进行 NFKC 标准化"""
    if not text:
        return ""
    return unicodedata.normalize('NFKC', str(text))

def clean_html(text, sep=" / "):
    """
    清洗带有 HTML 标签的富文本并转为纯文本
    """
    if not text:
        return "无"
    text = normalize_text(html.unescape(text))
    text = re.sub(r'</?(p|br|span|div)[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return sep.join(lines) if lines else "无"

def clean_plain_text(text):
    """
    清洗去除换行符与多余空格
    """
    if not text:
        return ""
    text = normalize_text(html.unescape(text))
    text = re.sub(r'<[^>]+>', '', text)
    return text.replace('\n', ' ').replace('\r', ' ').strip()

def calculate_ten_times_stats(cleaned_des):
    """
    智能计算 10 颗满配铭文属性的函数
    将 '物理攻击+2 / 物理穿透+3.6' 自动转换为 '物理攻击+20 / 物理穿透+36'
    """
    if not cleaned_des or cleaned_des == "无":
        return "无"
        
    parts = cleaned_des.split(" / ")
    ten_parts = []
    
    for p in parts:
        # 正则匹配属性名与数值，兼容小数与整数
        match = re.match(r'^(.*?)\+([0-9\.]+)(%?)$', p.strip())
        if match:
            attr_name = match.group(1)
            val = float(match.group(2))
            is_percent = match.group(3)
            
            ten_val = val * 10
            # 如果是整数则去除小数点
            formatted_val = f"{ten_val:.1f}" if ten_val % 1 != 0 else f"{int(ten_val)}"
            ten_parts.append(f"{attr_name}+{formatted_val}{is_percent}")
        else:
            ten_parts.append(p)
            
    return " / ".join(ten_parts)
