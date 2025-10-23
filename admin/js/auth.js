// Authentication Handler
class AuthHandler {
    constructor() {
        this.currentUser = null;
    }

    async login(username, password) {
        try {
            await api.login(username, password);
            this.currentUser = await api.getCurrentUser();
            return true;
        } catch (error) {
            throw error;
        }
    }

    logout() {
        api.logout();
        this.currentUser = null;
        window.location.reload();
    }

    async checkAuth() {
        const token = localStorage.getItem('token');
        if (!token) {
            this.showLoginPage();
            return false;
        }

        try {
            this.currentUser = await api.getCurrentUser();
            this.showDashboardPage();
            return true;
        } catch (error) {
            this.showLoginPage();
            return false;
        }
    }

    showLoginPage() {
        document.getElementById('login-page').classList.add('active');
        document.getElementById('dashboard-page').classList.remove('active');
    }

    showDashboardPage() {
        document.getElementById('login-page').classList.remove('active');
        document.getElementById('dashboard-page').classList.add('active');
        
        // Update user info
        if (this.currentUser) {
            document.getElementById('current-user').textContent = this.currentUser.username;
            document.getElementById('user-role-badge').textContent = this.currentUser.role.toUpperCase();
            document.getElementById('user-role-badge').className = `badge badge-${this.getRoleBadgeClass(this.currentUser.role)}`;
        }
    }

    getRoleBadgeClass(role) {
        const badges = {
            'admin': 'danger',
            'teacher': 'success',
            'viewer': 'info'
        };
        return badges[role] || 'secondary';
    }

    hasPermission(requiredRole) {
        if (!this.currentUser) return false;
        
        const roleHierarchy = {
            'viewer': 0,
            'teacher': 1,
            'admin': 2
        };
        
        return roleHierarchy[this.currentUser.role] >= roleHierarchy[requiredRole];
    }
}

// Initialize auth handler
const auth = new AuthHandler();
