// 状态渲染脚本
(function() {
    // 加载状态数据
    async function loadStatus() {
        try {
            const response = await fetch('status.json?t=' + Date.now());
            const data = await response.json();
            renderStatus(data);
        } catch (error) {
            console.error('加载状态失败:', error);
            document.getElementById('lastUpdate').textContent = '加载失败';
        }
    }

    // 渲染状态
    function renderStatus(data) {
        // 更新时间
        document.getElementById('lastUpdate').textContent = data.lastUpdate;
        document.getElementById('yuanling').textContent = data.ayuan.yuanling;

        // 渲染五脏
        renderZang(data.ayuan.body);
        
        // 渲染六腑
        renderFu(data.ayuan.fu);
        
        // 渲染经络
        renderMeridians(data.ayuan.meridians);
        
        // 渲染记忆
        renderMemory(data.ayuan.memory);
        
        // 渲染LLM状态
        renderLLM(data.ayuan.llm);
        
        // 渲染任务
        renderTasks(data.tasks);
        
        // 渲染日志
        renderLogs(data.logs);
    }

    // 五脏渲染
    function renderZang(body) {
        const zangOrder = ['heart', 'liver', 'spleen', 'lung', 'kidney'];
        const html = zangOrder.map(key => {
            const organ = body[key];
            const qiColor = organ.qi >= 80 ? '#4ade80' : organ.qi >= 60 ? '#fbbf24' : '#f87171';
            return `
                <div class="organ-card">
                    <h3>${organ.name}</h3>
                    <div class="role">${organ.role}</div>
                    <div class="qi-bar">
                        <div class="qi-fill" style="width: ${organ.qi}%; background: linear-gradient(90deg, ${qiColor}, #ffd700);"></div>
                    </div>
                    <div class="status ${organ.status}">气 ${organ.qi}%</div>
                </div>
            `;
        }).join('');
        document.getElementById('zangGrid').innerHTML = html;
    }

    // 六腑渲染
    function renderFu(fu) {
        const fuOrder = ['gallbladder', 'stomach', 'smallIntestine', 'largeIntestine', 'bladder', 'sanjiao'];
        const html = fuOrder.map(key => {
            const organ = fu[key];
            return `
                <div class="fu-card">
                    <h4>${organ.name}</h4>
                    <div class="role">${organ.role}</div>
                    <div class="status ${organ.status}">● 运行中</div>
                </div>
            `;
        }).join('');
        document.getElementById('fuGrid').innerHTML = html;
    }

    // 经络渲染
    function renderMeridians(meridians) {
        const html = Object.values(meridians).map(m => `
            <div class="meridian-card">
                <div>
                    <div class="name">${m.name}</div>
                    <div class="function">${m.function}</div>
                </div>
                <div class="status ${m.status}">● 流通</div>
            </div>
        `).join('');
        document.getElementById('meridianGrid').innerHTML = html;
    }

    // 记忆渲染
    function renderMemory(memory) {
        const html = `
            <div class="memory-stat">
                <div class="value">${memory.entities}</div>
                <div class="label">实体数量</div>
            </div>
            <div class="memory-stat">
                <div class="value">${memory.skills}</div>
                <div class="label">技能数量</div>
            </div>
            <div class="memory-stat">
                <div class="value">${memory.evolutionPool}</div>
                <div class="label">进化能力</div>
            </div>
        `;
        document.getElementById('memoryStats').innerHTML = html;
    }

    // LLM渲染
    function renderLLM(llm) {
        const statusDiv = document.getElementById('llmStatus');
        if (llm.connected) {
            statusDiv.className = 'llm-status connected';
            statusDiv.innerHTML = `<span class="label">LLM推理: ${llm.model || '已连接'}</span>`;
        } else {
            statusDiv.className = 'llm-status';
            statusDiv.innerHTML = `<span class="label">LLM推理: ${llm.note || '待接入'}</span>`;
        }
    }

    // 任务渲染
    function renderTasks(tasks) {
        const html = Object.values(tasks).map(t => `
            <div class="task-item">
                <div>
                    <div class="task-name">${t.name}</div>
                    <div class="task-schedule">${t.schedule}</div>
                </div>
                <div class="task-status ${t.status}">${t.status === 'running' ? '运行中' : t.status === 'pending' ? '待启动' : '异常'}</div>
            </div>
        `).join('');
        document.getElementById('taskList').innerHTML = html;
    }

    // 日志渲染
    function renderLogs(logs) {
        const html = logs.map(log => `
            <div class="log-entry ${log.type}">
                <span class="log-time">${log.time}</span>
                <span class="log-event">${log.event}</span>
            </div>
        `).join('');
        document.getElementById('logList').innerHTML = html;
    }

    // 登录成功后加载状态
    document.addEventListener('DOMContentLoaded', function() {
        // 检查是否已登录
        if (localStorage.getItem('tianyuan_auth') === 'true') {
            loadStatus();
        }
        
        // 监听登录成功事件
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (document.getElementById('privateContent').classList.contains('visible')) {
                    loadStatus();
                }
            });
        });
        
        observer.observe(document.getElementById('privateContent'), {
            attributes: true,
            attributeFilter: ['class']
        });
    });
})();
