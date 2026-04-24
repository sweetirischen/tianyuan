"""
天垣本地服务 - 远程访问DuMate
功能：
1. 代码执行API - 运行Python代码并返回结果
2. DuMate调用接口 - 调用DuMate执行复杂任务
3. 文件浏览API - 浏览本地文件系统
4. 项目管理API - 管理本地项目

启动方式：python server.py
默认端口：5000
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import json
import base64
import tempfile
import time
import threading
import sys
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 配置
CONFIG = {
    'secret_key': 'aheng',  # 访问密钥
    'timeout': 60,  # 代码执行超时（秒）
    'max_output': 100000,  # 最大输出字符数
    'workspace': r'C:\Users\Administrator',  # 工作空间根目录
    'allowed_extensions': ['.py', '.txt', '.md', '.json', '.csv', '.html', '.js', '.css', '.png', '.jpg', '.gif'],
}

# ========== 认证 ==========
def check_auth(req):
    """验证访问密钥"""
    # 优先检查header
    key = req.headers.get('X-Auth-Key')
    if key:
        return key == CONFIG['secret_key']
    # 如果有JSON body，检查authKey字段
    if req.is_json:
        try:
            key = req.json.get('authKey')
            if key:
                return key == CONFIG['secret_key']
        except:
            pass
    return False

@app.before_request
def auth_middleware():
    """请求前验证"""
    # 允许OPTIONS请求
    if request.method == 'OPTIONS':
        return None
    # 允许静态资源和首页
    if request.path.startswith('/static') or request.path == '/' or request.path.endswith('.html') or request.path.endswith('.js') or request.path.endswith('.css'):
        return None
    # API接口需要验证密钥
    if request.path.startswith('/api/'):
        if not check_auth(request):
            return jsonify({'error': '未授权访问'}), 401

# ========== 代码执行 ==========
@app.route('/api/run', methods=['POST'])
def run_code():
    """执行Python代码"""
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({'error': '代码为空'}), 400
    
    # 创建临时文件执行
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        # 执行代码
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=CONFIG['timeout'],
            cwd=CONFIG['workspace']
        )
        elapsed = time.time() - start_time
        
        # 清理临时文件
        os.unlink(temp_file)
        
        # 处理输出
        stdout = result.stdout[-CONFIG['max_output']:] if len(result.stdout) > CONFIG['max_output'] else result.stdout
        stderr = result.stderr[-CONFIG['max_output']:] if len(result.stderr) > CONFIG['max_output'] else result.stderr
        
        return jsonify({
            'success': result.returncode == 0,
            'stdout': stdout,
            'stderr': stderr,
            'returncode': result.returncode,
            'elapsed': round(elapsed, 2)
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': f'执行超时（{CONFIG["timeout"]}秒）'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== DuMate调用 ==========
@app.route('/api/dumate', methods=['POST'])
def call_dumate():
    """调用DuMate执行任务"""
    import json
    
    data = request.json
    task = data.get('task', '')
    context = data.get('context', {})
    
    if not task:
        return jsonify({'error': '任务为空'}), 400
    
    try:
        # DuMate任务处理
        # 当前实现：将任务保存到任务文件，等待DuMate处理
        # 实际调用需要通过千帆API或其他方式
        
        task_file = os.path.join(os.path.dirname(__file__), 'pending_tasks.json')
        
        # 读取现有任务
        tasks = []
        if os.path.exists(task_file):
            with open(task_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        
        # 添加新任务
        new_task = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'task': task,
            'context': context,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        tasks.append(new_task)
        
        # 保存任务
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'task_id': new_task['id'],
            'message': '任务已添加到队列，DuMate将尽快处理',
            'hint': '任务已保存到 pending_tasks.json，请在此对话中告诉我执行任务'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== 文件浏览 ==========
@app.route('/api/files/list', methods=['POST'])
def list_files():
    """列出目录内容"""
    data = request.json
    path = data.get('path', CONFIG['workspace'])
    
    # 安全检查：只允许访问工作空间内的文件
    try:
        path = os.path.abspath(path)
        if not path.startswith(CONFIG['workspace']) and path != CONFIG['workspace']:
            return jsonify({'error': '无权访问此目录'}), 403
        
        if not os.path.exists(path):
            return jsonify({'error': '路径不存在'}), 404
        
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            items.append({
                'name': item,
                'path': full_path,
                'type': 'directory' if os.path.isdir(full_path) else 'file',
                'size': os.path.getsize(full_path) if os.path.isfile(full_path) else 0,
                'modified': datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
            })
        
        # 排序：文件夹优先
        items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        
        return jsonify({
            'path': path,
            'parent': os.path.dirname(path) if path != CONFIG['workspace'] else None,
            'items': items
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/read', methods=['POST'])
def read_file():
    """读取文件内容"""
    data = request.json
    path = data.get('path', '')
    
    try:
        path = os.path.abspath(path)
        if not path.startswith(CONFIG['workspace']):
            return jsonify({'error': '无权访问此文件'}), 403
        
        if not os.path.exists(path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查文件大小
        size = os.path.getsize(path)
        if size > 1024 * 1024:  # 1MB
            return jsonify({'error': '文件过大，请下载查看'}), 400
        
        # 读取文件
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return jsonify({
            'path': path,
            'content': content,
            'size': size
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/write', methods=['POST'])
def write_file():
    """写入文件"""
    data = request.json
    path = data.get('path', '')
    content = data.get('content', '')
    
    try:
        path = os.path.abspath(path)
        if not path.startswith(CONFIG['workspace']):
            return jsonify({'error': '无权写入此文件'}), 403
        
        # 创建目录
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'path': path,
            'message': '文件已保存'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== 项目管理 ==========
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    projects_file = os.path.join(os.path.dirname(__file__), 'projects.json')
    
    if os.path.exists(projects_file):
        with open(projects_file, 'r', encoding='utf-8') as f:
            projects = json.load(f)
    else:
        projects = []
    
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def save_projects():
    """保存项目列表"""
    data = request.json
    projects = data.get('projects', [])
    
    projects_file = os.path.join(os.path.dirname(__file__), 'projects.json')
    
    with open(projects_file, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    
    return jsonify({'success': True, 'message': '项目已保存'})

# ========== 智能体数据 ==========
@app.route('/api/agents', methods=['GET'])
def get_agents():
    """获取智能体数据"""
    agents_file = os.path.join(os.path.dirname(__file__), 'agents.json')
    
    if os.path.exists(agents_file):
        with open(agents_file, 'r', encoding='utf-8') as f:
            agents = json.load(f)
    else:
        agents = {}
    
    return jsonify(agents)

@app.route('/api/agents', methods=['POST'])
def save_agents():
    """保存智能体数据"""
    data = request.json
    agents = data.get('agents', {})
    
    agents_file = os.path.join(os.path.dirname(__file__), 'agents.json')
    
    with open(agents_file, 'w', encoding='utf-8') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    
    return jsonify({'success': True, 'message': '智能体数据已保存'})

# ========== 系统状态 ==========
@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    import psutil
    
    return jsonify({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('C:\\').percent,
        'time': datetime.now().isoformat(),
        'uptime': time.time() - start_time
    })

# ========== 静态文件服务 ==========
@app.route('/')
def index():
    """返回私有空间页面"""
    return send_file(os.path.join(os.path.dirname(__file__), 'docs', 'private.html'))

@app.route('/<path:path>')
def static_files(path):
    """静态文件服务"""
    return send_file(os.path.join(os.path.dirname(__file__), 'docs', path))

# ========== 启动 ==========
if __name__ == '__main__':
    start_time = time.time()
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                  天垣本地服务 - 启动成功                    ║
╠═══════════════════════════════════════════════════════════╣
║  本地访问: http://localhost:5000                           ║
║  密钥: {CONFIG['secret_key']}                                          ║
║  工作空间: {CONFIG['workspace']}                 ║
╠═══════════════════════════════════════════════════════════╣
║  API接口:                                                 ║
║    POST /api/run        - 执行Python代码                  ║
║    POST /api/dumate     - 调用DuMate                      ║
║    POST /api/files/list - 浏览目录                        ║
║    POST /api/files/read - 读取文件                        ║
║    POST /api/files/write- 写入文件                        ║
║    GET  /api/status     - 系统状态                        ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
