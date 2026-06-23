(function () {
    const ROLE_PERMISSIONS = {
        PGV: [
            'create_user',
            'view_exam_registration', 'create_exam_registration', 'update_exam_registration', 'delete_exam_registration',
            'view_subject', 'create_subject', 'update_subject', 'delete_subject',
            'view_class', 'create_class', 'update_class', 'delete_class',
            'view_student', 'create_student', 'update_student', 'delete_student',
            'view_teacher', 'create_teacher', 'update_teacher', 'delete_teacher',
            'view_student_score', 'view_score_report', 'view_student_exam', 'print_score_table',
            'view_question', 'create_question', 'update_question', 'delete_question'
        ],
        GIANGVIEN: [
            'view_question', 'create_question', 'update_question', 'delete_question',
            'view_exam_registration', 'create_exam_registration', 'update_exam_registration', 'delete_exam_registration',
            'practice_exam', 'view_student_score', 'view_score_report', 'view_student_exam', 'print_score_table'
        ],
        SINHVIEN: [
            'take_exam', 'view_own_score', 'view_own_exam'
        ]
    };

    function parseList(value) {
        return (value || '')
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean);
    }

    function readUser() {
        if (window.__SERVER_USER__) return window.__SERVER_USER__;

        const userJson = localStorage.getItem('user');
        if (!userJson) return null;

        try {
            return JSON.parse(userJson);
        } catch (error) {
            return null;
        }
    }

    const user = readUser();
    const role = user?.role;
    const permissions = new Set(ROLE_PERMISSIONS[role] || []);

    if (window.__SERVER_USER__) {
        localStorage.setItem('user', JSON.stringify(window.__SERVER_USER__));
    }

    window.currentUser = user || null;
    window.hasPermission = function hasPermission(permission) {
        return permissions.has(permission);
    };

    window.hasAnyPermission = function hasAnyPermission(requiredPermissions) {
        return requiredPermissions.some((permission) => permissions.has(permission));
    };

    function hide(element) {
        element.hidden = true;
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
    }

    function applyRBAC() {
        document.querySelectorAll('[data-roles]').forEach((element) => {
            const allowedRoles = parseList(element.dataset.roles);
            if (!role || !allowedRoles.includes(role)) hide(element);
        });

        document.querySelectorAll('[data-permission]').forEach((element) => {
            if (!permissions.has(element.dataset.permission)) hide(element);
        });

        document.querySelectorAll('[data-any-permission]').forEach((element) => {
            const requiredPermissions = parseList(element.dataset.anyPermission);
            if (!window.hasAnyPermission(requiredPermissions)) hide(element);
        });
    }

    function markActiveNavigation() {
        const currentPath = window.location.pathname.replace(/\/$/, '') || '/home';
        const navLinks = document.querySelectorAll('.sidebar-nav a[data-nav]:not([hidden])');

        navLinks.forEach((link) => {
            const navPath = link.dataset.nav.replace(/\/$/, '');
            if (currentPath === navPath || currentPath.startsWith(navPath + '/')) {
                link.classList.add('is-active');
            }
        });
    }

    function setupSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.body.classList.toggle('sidebar-open');
            });
        }

        document.addEventListener('click', (event) => {
            const sidebar = document.getElementById('dashboardSidebar');
            const clickedToggle = event.target.closest('#sidebarToggle');
            if (!sidebar || clickedToggle || window.innerWidth > 900) return;
            if (!sidebar.contains(event.target)) {
                document.body.classList.remove('sidebar-open');
            }
        });
    }

    function setupAuthArea() {
        const authArea = document.getElementById('authArea');
        if (!authArea) return;

        if (!user) {
            authArea.innerHTML = '<a class="btn btn-outline" href="/user/login">Dang nhap</a>';
            return;
        }

        const initials = (user.ten || user.ma || 'U').charAt(0).toUpperCase();
        const fullName = user.ho ? `${user.ho} ${user.ten}`.trim() : (user.ten || user.ma || 'Nguoi dung');

        authArea.innerHTML = `
            <div class="auth-container">
                <button id="avatarBtn" class="avatar" type="button" aria-label="Thong tin nguoi dung">${initials}</button>
                <div id="userDropdown" class="user-dropdown">
                    <div class="dropdown-header">
                        <div class="dropdown-user-name">${fullName}</div>
                        <div class="dropdown-user-role">${role || 'USER'}</div>
                        <div class="dropdown-user-ma">Mã: ${user.ma}</div>
                    </div>
                    <div class="dropdown-divider"></div>
                    <div class="dropdown-actions">
                        <a href="/user/info" class="dropdown-item btn-profile">Hồ sơ cá nhân</a>
                        <button id="logoutBtn" class="dropdown-item btn-logout" type="button">Đăng xuất</button>
                    </div>
                </div>
            </div>
        `;

        const avatarBtn = document.getElementById('avatarBtn');
        const userDropdown = document.getElementById('userDropdown');

        avatarBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown?.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (userDropdown && !userDropdown.contains(e.target) && e.target !== avatarBtn) {
                userDropdown.classList.remove('show');
            }
        });

        document.getElementById('logoutBtn')?.addEventListener('click', async () => {
            try {
                await fetch('/user/logout');
            } catch (error) {
                window.notify?.('Khong the goi logout, dang xoa session cuc bo', 'error');
            }

            localStorage.removeItem('user');
            window.location.href = '/user/login';
        });
    }

    window.notify = function notify(message, type = 'default') {
        const host = document.getElementById('toastHost');
        if (!host || !message) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        host.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3200);
    };

    applyRBAC();
    document.body.classList.add('rbac-ready');
    markActiveNavigation();
    setupSidebar();
    setupAuthArea();
})();
