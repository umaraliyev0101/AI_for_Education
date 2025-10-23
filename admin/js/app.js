// Main Application
document.addEventListener('DOMContentLoaded', async () => {
    // Page handlers
    const pageHandlers = {
        'dashboard': dashboard,
        'students': students,
        'lessons': lessons,
        'attendance': attendance,
        'qa': qa,
        'users': users
    };

    // Login form handler (must be registered before checkAuth)
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('login-error');
        const submitBtn = e.target.querySelector('button[type="submit"]');
        
        errorDiv.classList.remove('show');
        errorDiv.textContent = '';
        ui.disableButton(submitBtn, 'Logging in...');
        
        try {
            await auth.login(username, password);
            auth.showDashboardPage();
            await initializeDashboard();
            ui.showSuccess('Welcome back!');
        } catch (error) {
            errorDiv.textContent = error.message || 'Login failed';
            errorDiv.classList.add('show');
        } finally {
            ui.enableButton(submitBtn);
        }
    });

    // Initialize dashboard after successful login
    let dashboardInitialized = false;
    
    async function initializeDashboard() {
        if (dashboardInitialized) return;
        dashboardInitialized = true;

        // Load initial page (dashboard)
        await dashboard.init();

        // Navigation
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                
                // Update active nav item
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                
                // Update content
                document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
                document.getElementById(`${page}-content`).classList.add('active');
                
                // Update title
                document.getElementById('page-title').textContent = item.textContent.trim();
                
                // Initialize page handler
                const handler = pageHandlers[page];
                if (handler && typeof handler.init === 'function') {
                    await handler.init();
                }
            });
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            ui.confirm('Are you sure you want to logout?', () => {
                auth.logout();
            });
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', async () => {
            const activeNav = document.querySelector('.nav-item.active');
            const page = activeNav?.dataset?.page || 'dashboard';
            const handler = pageHandlers[page];
            
            if (handler) {
                if (handler.refresh) {
                    await handler.refresh();
                } else if (handler.init) {
                    await handler.init();
                    ui.showSuccess('Page refreshed');
                }
            }
        });
    }

    // Check authentication on page load
    const isAuthenticated = await auth.checkAuth();
    
    if (isAuthenticated) {
        // User is already logged in, initialize dashboard
        await initializeDashboard();
    }
});
