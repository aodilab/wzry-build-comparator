# -*- coding: utf-8 -*-
"""
scripts/notify_wechat.py - 微信消息通知工具 (基于 PushPlus 微信公众号模板消息通道)
"""
import sys
import os
import requests

PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "f98db4acac6443658df6f43fe2578916")
PUSHPLUS_API_URL = "https://www.pushplus.plus/send"

def send_wechat(title: str, content: str, template: str = "markdown") -> bool:
    if not PUSHPLUS_TOKEN:
        print("[Notifier] 未配置 PUSHPLUS_TOKEN，跳过推送")
        return False
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": template
    }
    try:
        resp = requests.post(PUSHPLUS_API_URL, json=payload, timeout=10)
        if resp.status_code == 200:
            res_json = resp.json()
            ok = res_json.get("code") == 200
            if ok:
                print(f"[Notifier] 微信消息推送成功 (msgId: {res_json.get('data')})")
            else:
                print(f"[Notifier] 微信推送失败: {res_json.get('msg')}")
            return ok
        return False
    except Exception as e:
        print(f"[Notifier] 微信推送异常: {e}")
        return False

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "📢 测试消息"
    c = sys.argv[2] if len(sys.argv) > 2 else "这是一条来自王者荣耀知识库系统的测试通知。"
    send_wechat(t, c)
