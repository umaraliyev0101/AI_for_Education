// Dashboard Handler
class DashboardHandler {
    async init() {
        await this.loadStats();
        await this.loadUpcomingLessons();
        await this.loadRecentActivity();
    }

    async loadStats() {
        try {
            // Load all stats in parallel
            const [students, lessons, attendance, qaSessions] = await Promise.all([
                api.getStudents(),
                api.getLessons(),
                api.getAttendance(),
                api.getQASessions()
            ]);

            document.getElementById('total-students').textContent = students.length;
            document.getElementById('total-lessons').textContent = lessons.length;
            document.getElementById('total-attendance').textContent = attendance.length;
            document.getElementById('total-qa').textContent = qaSessions.length;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadUpcomingLessons() {
        const container = document.getElementById('upcoming-lessons');
        
        try {
            const lessons = await api.getLessons(0, 5, 'scheduled');
            
            if (lessons.length === 0) {
                container.innerHTML = '<p class="loading">No upcoming lessons</p>';
                return;
            }

            container.innerHTML = lessons.map(lesson => `
                <div style="padding: 1rem; border-bottom: 1px solid var(--border);">
                    <h4 style="margin-bottom: 0.5rem;">${lesson.title}</h4>
                    <p style="color: var(--secondary); font-size: 0.875rem; margin-bottom: 0.25rem;">
                        <i class="fas fa-calendar"></i> ${ui.formatDateOnly(lesson.date)}
                    </p>
                    <p style="color: var(--secondary); font-size: 0.875rem;">
                        <i class="fas fa-clock"></i> ${lesson.duration_minutes || 0} minutes
                        ${lesson.subject ? ` • ${lesson.subject}` : ''}
                    </p>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p class="loading">Error loading lessons</p>';
            console.error('Error loading upcoming lessons:', error);
        }
    }

    async loadRecentActivity() {
        const container = document.getElementById('recent-activity');
        
        try {
            const attendance = await api.getAttendance(0, 5);
            
            if (attendance.length === 0) {
                container.innerHTML = '<p class="loading">No recent activity</p>';
                return;
            }

            container.innerHTML = attendance.map(record => `
                <div style="padding: 1rem; border-bottom: 1px solid var(--border);">
                    <p style="margin-bottom: 0.5rem;">
                        <strong>Student ID ${record.student_id}</strong> attended
                        <strong>Lesson ${record.lesson_id}</strong>
                    </p>
                    <p style="color: var(--secondary); font-size: 0.875rem;">
                        <i class="fas fa-clock"></i> ${ui.formatDate(record.timestamp)}
                        ${record.recognition_confidence ? ` • ${ui.formatConfidence(record.recognition_confidence)} confidence` : ''}
                    </p>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p class="loading">Error loading activity</p>';
            console.error('Error loading recent activity:', error);
        }
    }

    async refresh() {
        await this.init();
        ui.showSuccess('Dashboard refreshed');
    }
}

// Initialize dashboard handler
const dashboard = new DashboardHandler();
