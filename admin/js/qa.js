// Q&A Handler
class QAHandler {
    async init() {
        await this.loadQASessions();
    }

    async loadQASessions() {
        const tbody = document.querySelector('#qa-table tbody');
        ui.showLoading(tbody);
        try {
            const sessions = await api.getQASessions();
            if (sessions.length === 0) {
                ui.showEmptyState(tbody, 'No Q&A sessions', 7);
                return;
            }
            tbody.innerHTML = sessions.map(session => `
                <tr>
                    <td>${session.id}</td>
                    <td>Lesson ${session.lesson_id}</td>
                    <td>${ui.truncate(session.question_text)}</td>
                    <td>${ui.getBooleanBadge(session.found_answer)}</td>
                    <td>${ui.formatConfidence(session.relevance_score)}</td>
                    <td>${ui.formatDate(session.timestamp)}</td>
                    <td>
                        <button class="btn btn-sm btn-icon" onclick="qa.viewDetails(${session.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-icon" onclick="qa.deleteSession(${session.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            ui.showError('Failed to load Q&A sessions');
        }
    }

    async viewDetails(id) {
        try {
            const session = await api.getQASession(id);
            const content = `
                <div style="margin-bottom: 1rem;">
                    <strong>Question:</strong>
                    <p>${session.question_text}</p>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Answer:</strong>
                    <p>${session.answer_text || 'No answer found'}</p>
                </div>
                <div>
                    <strong>Details:</strong>
                    <p>Lesson ID: ${session.lesson_id}</p>
                    <p>Found Answer: ${session.found_answer ? 'Yes' : 'No'}</p>
                    <p>Relevance: ${ui.formatConfidence(session.relevance_score)}</p>
                    <p>Time: ${ui.formatDate(session.timestamp)}</p>
                </div>
            `;
            ui.showModal('<i class="fas fa-info-circle"></i> Q&A Details', content);
        } catch (error) {
            ui.showError('Failed to load details');
        }
    }

    async deleteSession(id) {
        ui.confirm('Delete this Q&A session?', async () => {
            try {
                await api.deleteQASession(id);
                ui.showSuccess('Session deleted');
                await this.loadQASessions();
            } catch (error) {
                ui.showError('Failed to delete session');
            }
        });
    }
}

const qa = new QAHandler();
