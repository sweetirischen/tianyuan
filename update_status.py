# 阿垣状态更新脚本
# 用法: python update_status.py

import json
import os
import subprocess
from datetime import datetime

# 配置
TIANYUAN_DIR = r"C:\Users\Administrator\tianyuan"
STATUS_FILE = os.path.join(TIANYUAN_DIR, "docs", "status.json")

def update_status():
    """更新status.json并推送到GitHub"""

    # 读取当前状态
    with open(STATUS_FILE, 'r', encoding='utf-8') as f:
        status = json.load(f)

    # 更新时间
    status['lastUpdate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 更新日志（添加本次更新）
    new_log = {
        "time": status['lastUpdate'],
        "event": "状态自动更新",
        "type": "success"
    }
    if new_log not in status['logs']:
        status['logs'].insert(0, new_log)
        status['logs'] = status['logs'][:10]  # 只保留最近10条

    # 写入文件
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    print(f"[OK] Status updated: {status['lastUpdate']}")

    # 推送到GitHub
    os.chdir(TIANYUAN_DIR)

    # 复制到根目录
    subprocess.run(['cp', 'docs/status.json', 'status.json'], shell=True)

    # Git操作
    subprocess.run(['git', 'add', '.'], shell=True)
    subprocess.run(['git', 'commit', '-m', f'Update status: {status["lastUpdate"]}'], shell=True)
    result = subprocess.run(['git', 'push', 'origin', 'gh-pages'], shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("[OK] Pushed to GitHub")
    else:
        print(f"[ERROR] Push failed: {result.stderr}")

    return status['lastUpdate']

if __name__ == "__main__":
    update_status()
