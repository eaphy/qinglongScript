"""
需添加环境变量 URL_LIST ，值如下

[
    "host1.example.com",
    "host2.example.com"
]

cron: 0 15 15 * *
const $ = new Env("URL");
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import json
from urllib.parse import urlparse

# 配置
ENV_NAME = "URL_LIST"    # 环境变量名称
RETRY_TIMES = 3          # 失败重试次数
TIMEOUT = 10             # 超时时间（秒）
NOTIFY = True            # 是否发送青龙面板通知

# -------------------------- 工具函数 --------------------------
def ql_notify(title, content):
    """发送青龙面板通知（如果可用）"""
    try:
        from notify import send
        if NOTIFY:
            send(title, content)
    except:
        pass

def ql_env(name, default=""):
    """读取环境变量并解析JSON"""
    raw = os.environ.get(name, default)
    try:
        # 尝试解析为JSON
        return json.loads(raw)
    except json.JSONDecodeError:
        # 如果解析失败，兼容旧版逗号分隔（optional）
        return raw.split(",") if raw else []

# -------------------------- 主逻辑 --------------------------
def check_url(url):
    """检查单个URL的可访问性"""
    try:
        r = requests.get(url, timeout=TIMEOUT)
        return {
            "status": r.status_code,
            "success": r.ok,
            "url": url,
            "final_url": r.url,  # 处理重定向后的最终URL
            "elapsed": round(r.elapsed.total_seconds(), 2)
        }
    except Exception as e:
        return {
            "error": str(e),
            "url": url
        }

def process_urls(url_list):
    """批量检查URL并生成报告"""
    results = []
    for url in url_list:
        url = str(url).strip()
        if not url:
            continue
        
        # 自动补全协议
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        
        # 重试逻辑
        for _ in range(RETRY_TIMES):
            result = check_url(url)
            if result.get("success", False):
                break
        results.append(result)
    return results

def report_results(results):
    """生成报告"""
    success = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    msg = [
        f"✅ 成功: {len(success)}",
        f"❌ 失败: {len(failed)}",
        "",
        "📝 详细结果:"
    ]
    msg.extend(
        f"[{'OK' if r.get('success') else 'ERR'}] {r['url']} "
        # f"{r.get('final_url', '')} "
        f"{r.get('status', '')} "
        f"{r.get('error', '')}".strip()
        for r in results
    )

    report = "\n".join(msg)
    print(report)
    ql_notify("URL检测报告", report)

# -------------------------- 入口 --------------------------
if __name__ == '__main__':
    url_list = ql_env(ENV_NAME)
    if not url_list:
        print(f"❌ 请设置环境变量 {ENV_NAME}（JSON数组格式，如：[\"https://example.com\"]）")
        exit(1)

    print(f"🔍 检测目标（共 {len(url_list)} 个）:\n" + "\n".join(f"  - {u}" for u in url_list))
    results = process_urls(url_list)
    report_results(results)
