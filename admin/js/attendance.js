// Attendance, QA, Users handlers - simplified versions
class AttendanceHandler {
    async init() {
        await this.loadAttendance();
    }

    async loadAttendance() {
        const tbody = document.querySelector('#attendance-table tbody');
        ui.showLoading(tbody);
        try {
            const records = await api.getAttendance();
            if (records.length === 0) {
                ui.showEmptyState(tbody, 'No attendance records', 7);
                return;
            }
            tbody.innerHTML = records.map(record => `
                <tr>
                    <td>${record.id}</td>
                    <td>Student ${record.student_id}</td>
                    <td>Lesson ${record.lesson_id}</td>
                    <td>${ui.formatDate(record.timestamp)}</td>
                    <td><span class="badge badge-info">${record.entry_method}</span></td>
                    <td>${ui.formatConfidence(record.recognition_confidence)}</td>
                    <td>
                        <button class="btn btn-sm btn-icon" onclick="attendance.deleteRecord(${record.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            ui.showError('Failed to load attendance');
        }
    }

    async deleteRecord(id) {
        ui.confirm('Delete this attendance record?', async () => {
            try {
                await api.deleteAttendance(id);
                ui.showSuccess('Record deleted');
                await this.loadAttendance();
            } catch (error) {
                ui.showError('Failed to delete record');
            }
        });
    }
}

const attendance = new AttendanceHandler();
