// UI Utilities
class UI {
    // Toast Notifications
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${icons[type]}"></i>
            </div>
            <div class="toast-message">${message}</div>
            <button class="toast-close">&times;</button>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showWarning(message) {
        this.showToast(message, 'warning');
    }

    showInfo(message) {
        this.showToast(message, 'info');
    }

    // Modal
    showModal(title, content, footer = '') {
        const container = document.getElementById('modal-container');
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
            </div>
        `;
        
        container.appendChild(modal);
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
        
        // Close button
        modal.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal();
        });
        
        return modal;
    }

    closeModal() {
        const container = document.getElementById('modal-container');
        container.innerHTML = '';
    }

    // Confirm Dialog
    confirm(message, onConfirm) {
        const footer = `
            <button class="btn btn-secondary" id="cancel-btn">Cancel</button>
            <button class="btn btn-danger" id="confirm-btn">Confirm</button>
        `;
        
        const modal = this.showModal(
            '<i class="fas fa-exclamation-triangle"></i> Confirmation',
            `<p>${message}</p>`,
            footer
        );
        
        modal.querySelector('#confirm-btn').addEventListener('click', () => {
            onConfirm();
            this.closeModal();
        });
        
        modal.querySelector('#cancel-btn').addEventListener('click', () => {
            this.closeModal();
        });
    }

    // Loading State
    showLoading(element, message = 'Loading...') {
        element.innerHTML = `
            <tr>
                <td colspan="10" class="loading">
                    <i class="fas fa-spinner fa-spin"></i> ${message}
                </td>
            </tr>
        `;
    }

    showEmptyState(element, message = 'No data found', colspan = 10) {
        element.innerHTML = `
            <tr>
                <td colspan="${colspan}" class="loading">
                    <i class="fas fa-inbox"></i> ${message}
                </td>
            </tr>
        `;
    }

    // Format Date
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Format Date Only
    formatDateOnly(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // Status Badge
    getStatusBadge(status) {
        const badges = {
            'scheduled': 'info',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        };
        const badgeClass = badges[status] || 'secondary';
        return `<span class="badge badge-${badgeClass}">${status.replace('_', ' ')}</span>`;
    }

    // Boolean Badge
    getBooleanBadge(value, trueText = 'Yes', falseText = 'No') {
        const badgeClass = value ? 'success' : 'danger';
        const text = value ? trueText : falseText;
        return `<span class="badge badge-${badgeClass}">${text}</span>`;
    }

    // Active/Inactive Badge
    getActiveBadge(isActive) {
        return this.getBooleanBadge(isActive, 'Active', 'Inactive');
    }

    // Truncate Text
    truncate(text, maxLength = 50) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    // Format Confidence Score
    formatConfidence(confidence) {
        if (confidence === null || confidence === undefined) return 'N/A';
        return `${(confidence * 100).toFixed(1)}%`;
    }

    // Disable Button
    disableButton(button, text = 'Processing...') {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    }

    // Enable Button
    enableButton(button) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

// Initialize UI
const ui = new UI();
