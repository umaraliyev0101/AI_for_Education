// Users Handler (Admin only)
class UsersHandler {
    async init() {
        if (!auth.hasPermission('admin')) {
            document.getElementById('users-content').innerHTML = '<p class="loading">Access Denied: Admin only</p>';
            return;
        }
        await this.loadUsers();
    }

    async loadUsers() {
        const tbody = document.querySelector('#users-table tbody');
        ui.showLoading(tbody);
        // Since we don't have a users endpoint, show current user only
        if (auth.currentUser) {
            tbody.innerHTML = `
                <tr>
                    <td>${auth.currentUser.id}</td>
                    <td><strong>${auth.currentUser.username}</strong></td>
                    <td>${auth.currentUser.email}</td>
                    <td>${auth.currentUser.full_name || 'N/A'}</td>
                    <td><span class="badge badge-danger">${auth.currentUser.role.toUpperCase()}</span></td>
                    <td>${ui.getActiveBadge(auth.currentUser.is_active)}</td>
                    <td>${ui.formatDate(auth.currentUser.last_login)}</td>
                    <td>
                        <span class="badge badge-info">Current User</span>
                    </td>
                </tr>
            `;
        }
    }
}

const users = new UsersHandler();
