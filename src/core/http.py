# -*- coding: utf-8 -*-
"""
统一 HTTP 通信模块
提供重试、超时、反爬 User-Agent 封装
"""
import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import DEFAULT_HEADERS

import hashlib
import json

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".cache")
CACHE_TTL = 86400  # 缓存有效期 24 小时

def _get_cache_path(url, ext):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    d = os.path.join(CACHE_DIR, ext)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{url_hash}.{ext}")

def fetch_json(url, headers=None, retries=3, delay=1, use_cache=True):
    """带本地缓存与重试的 JSON 请求接口"""
    cache_file = _get_cache_path(url, "json")
    if use_cache and os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < CACHE_TTL:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

    h = headers or DEFAULT_HEADERS
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=h, timeout=10)
            resp.encoding = 'utf-8'
            data = resp.json()
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            except Exception:
                pass
            return data
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                # 降级：网络故障尝试读旧缓存
                if os.path.exists(cache_file):
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f)
                raise e

def fetch_html(url, headers=None, encoding='gbk', retries=3, delay=1, use_cache=True):
    """带本地缓存与重试的 HTML 抓取接口"""
    cache_file = _get_cache_path(url, "html")
    if use_cache and os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < CACHE_TTL:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass

    h = headers or DEFAULT_HEADERS
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=h, timeout=10)
            resp.encoding = encoding
            text = resp.text
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(text)
            except Exception:
                pass
            return text
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                if os.path.exists(cache_file):
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return f.read()
                raise e
