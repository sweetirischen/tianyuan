// 私有空间密码验证脚本
(function() {
    function checkPassword() {
        const input = document.getElementById('passwordInput').value;
        if (input === 'aheng') {
            document.getElementById('loginContainer').classList.add('hidden');
            document.getElementById('privateContent').classList.add('visible');
            localStorage.setItem('tianyuan_auth', 'true');
        } else {
            document.getElementById('errorMsg').style.display = 'block';
            document.getElementById('passwordInput').value = '';
        }
    }

    function logout() {
        localStorage.removeItem('tianyuan_auth');
        location.reload();
    }

    // 检查是否已登录
    if (localStorage.getItem('tianyuan_auth') === 'true') {
        document.getElementById('loginContainer').classList.add('hidden');
        document.getElementById('privateContent').classList.add('visible');
    }

    // 绑定事件
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('passwordInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkPassword();
            }
        });
        
        document.getElementById('loginBtn').addEventListener('click', checkPassword);
        
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
    });
})();
