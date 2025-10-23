// Lessons Handler
class LessonsHandler {
    async init() {
        await this.loadLessons();
        this.initEventListeners();
    }

    initEventListeners() {
        document.getElementById('add-lesson-btn').addEventListener('click', () => {
            this.showAddLessonModal();
        });
    }

    async loadLessons() {
        const tbody = document.querySelector('#lessons-table tbody');
        ui.showLoading(tbody, 'Loading lessons...');

        try {
            const lessons = await api.getLessons();
            
            if (lessons.length === 0) {
                ui.showEmptyState(tbody, 'No lessons found', 7);
                return;
            }

            tbody.innerHTML = lessons.map(lesson => `
                <tr>
                    <td>${lesson.id}</td>
                    <td><strong>${lesson.title}</strong></td>
                    <td>${lesson.subject || 'N/A'}</td>
                    <td>${ui.formatDateOnly(lesson.date)}</td>
                    <td>${lesson.duration_minutes || 0} min</td>
                    <td>${ui.getStatusBadge(lesson.status)}</td>
                    <td class="action-buttons">
                        ${lesson.status === 'scheduled' ? `
                            <button class="btn btn-sm btn-success" onclick="lessons.startLesson(${lesson.id})" title="Start">
                                <i class="fas fa-play"></i>
                            </button>
                        ` : ''}
                        ${lesson.status === 'in_progress' ? `
                            <button class="btn btn-sm btn-danger" onclick="lessons.endLesson(${lesson.id})" title="End">
                                <i class="fas fa-stop"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-icon" onclick="lessons.uploadMaterials(${lesson.id})" title="Upload Materials">
                            <i class="fas fa-upload"></i>
                        </button>
                        <button class="btn btn-sm btn-icon" onclick="lessons.editLesson(${lesson.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-icon" onclick="lessons.deleteLesson(${lesson.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            ui.showError('Failed to load lessons');
            console.error('Error loading lessons:', error);
        }
    }

    showAddLessonModal() {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const defaultDate = tomorrow.toISOString().slice(0, 16);

        const content = `
            <form id="add-lesson-form">
                <div class="form-group">
                    <label for="title">Lesson Title *</label>
                    <input type="text" id="title" name="title" required>
                </div>
                <div class="form-group">
                    <label for="subject">Subject</label>
                    <input type="text" id="subject" name="subject">
                </div>
                <div class="form-group">
                    <label for="date">Date & Time *</label>
                    <input type="datetime-local" id="date" name="date" value="${defaultDate}" required>
                </div>
                <div class="form-group">
                    <label for="duration_minutes">Duration (minutes)</label>
                    <input type="number" id="duration_minutes" name="duration_minutes" value="90" min="1">
                </div>
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label for="notes">Notes</label>
                    <textarea id="notes" name="notes" rows="2"></textarea>
                </div>
            </form>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
            <button class="btn btn-primary" id="submit-lesson-btn">Add Lesson</button>
        `;

        const modal = ui.showModal('<i class="fas fa-book-plus"></i> Add New Lesson', content, footer);

        modal.querySelector('#submit-lesson-btn').addEventListener('click', async () => {
            await this.submitAddLesson();
        });
    }

    async submitAddLesson() {
        const form = document.getElementById('add-lesson-form');
        const formData = new FormData(form);
        
        const lessonData = {
            title: formData.get('title'),
            subject: formData.get('subject') || null,
            date: new Date(formData.get('date')).toISOString(),
            duration_minutes: parseInt(formData.get('duration_minutes')) || null,
            description: formData.get('description') || null,
            notes: formData.get('notes') || null
        };

        const submitBtn = document.getElementById('submit-lesson-btn');
        ui.disableButton(submitBtn);

        try {
            await api.createLesson(lessonData);
            ui.showSuccess('Lesson created successfully');
            ui.closeModal();
            await this.loadLessons();
        } catch (error) {
            ui.showError(error.message || 'Failed to create lesson');
        } finally {
            ui.enableButton(submitBtn);
        }
    }

    async startLesson(lessonId) {
        ui.confirm('Start this lesson now?', async () => {
            try {
                await api.startLesson(lessonId);
                ui.showSuccess('Lesson started successfully');
                await this.loadLessons();
            } catch (error) {
                ui.showError(error.message || 'Failed to start lesson');
            }
        });
    }

    async endLesson(lessonId) {
        ui.confirm('End this lesson?', async () => {
            try {
                await api.endLesson(lessonId);
                ui.showSuccess('Lesson ended successfully');
                await this.loadLessons();
            } catch (error) {
                ui.showError(error.message || 'Failed to end lesson');
            }
        });
    }

    uploadMaterials(lessonId) {
        const content = `
            <p>Upload lesson materials or presentation files.</p>
            <div class="form-group">
                <label for="materials_file">Materials (PDF, PPTX, DOCX, TXT)</label>
                <input type="file" id="materials_file" accept=".pdf,.pptx,.docx,.txt">
            </div>
            <div class="form-group">
                <label for="presentation_file">Presentation (PPTX, PDF)</label>
                <input type="file" id="presentation_file" accept=".pptx,.pdf">
            </div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
            <button class="btn btn-primary" id="upload-files-btn">Upload Files</button>
        `;

        const modal = ui.showModal('<i class="fas fa-upload"></i> Upload Lesson Files', content, footer);

        modal.querySelector('#upload-files-btn').addEventListener('click', async () => {
            const materialsFile = document.getElementById('materials_file').files[0];
            const presentationFile = document.getElementById('presentation_file').files[0];

            if (!materialsFile && !presentationFile) {
                ui.showError('Please select at least one file');
                return;
            }

            const uploadBtn = document.getElementById('upload-files-btn');
            ui.disableButton(uploadBtn);

            try {
                if (materialsFile) {
                    await api.uploadLessonMaterials(lessonId, materialsFile);
                }
                if (presentationFile) {
                    await api.uploadLessonPresentation(lessonId, presentationFile);
                }
                ui.showSuccess('Files uploaded successfully');
                ui.closeModal();
                await this.loadLessons();
            } catch (error) {
                ui.showError(error.message || 'Failed to upload files');
            } finally {
                ui.enableButton(uploadBtn);
            }
        });
    }

    async editLesson(lessonId) {
        try {
            const lesson = await api.getLesson(lessonId);
            
            const content = `
                <form id="edit-lesson-form">
                    <div class="form-group">
                        <label for="edit_title">Lesson Title *</label>
                        <input type="text" id="edit_title" name="title" value="${lesson.title}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit_subject">Subject</label>
                        <input type="text" id="edit_subject" name="subject" value="${lesson.subject || ''}">
                    </div>
                    <div class="form-group">
                        <label for="edit_duration">Duration (minutes)</label>
                        <input type="number" id="edit_duration" name="duration_minutes" value="${lesson.duration_minutes || ''}" min="1">
                    </div>
                    <div class="form-group">
                        <label for="edit_description">Description</label>
                        <textarea id="edit_description" name="description" rows="3">${lesson.description || ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="edit_notes">Notes</label>
                        <textarea id="edit_notes" name="notes" rows="2">${lesson.notes || ''}</textarea>
                    </div>
                </form>
            `;

            const footer = `
                <button class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
                <button class="btn btn-primary" id="update-lesson-btn">Update Lesson</button>
            `;

            const modal = ui.showModal('<i class="fas fa-edit"></i> Edit Lesson', content, footer);

            modal.querySelector('#update-lesson-btn').addEventListener('click', async () => {
                const form = document.getElementById('edit-lesson-form');
                const formData = new FormData(form);
                
                const updateData = {
                    title: formData.get('title'),
                    subject: formData.get('subject') || null,
                    duration_minutes: parseInt(formData.get('duration_minutes')) || null,
                    description: formData.get('description') || null,
                    notes: formData.get('notes') || null
                };

                const updateBtn = document.getElementById('update-lesson-btn');
                ui.disableButton(updateBtn);

                try {
                    await api.updateLesson(lessonId, updateData);
                    ui.showSuccess('Lesson updated successfully');
                    ui.closeModal();
                    await this.loadLessons();
                } catch (error) {
                    ui.showError(error.message || 'Failed to update lesson');
                } finally {
                    ui.enableButton(updateBtn);
                }
            });
        } catch (error) {
            ui.showError('Failed to load lesson details');
        }
    }

    async deleteLesson(lessonId) {
        ui.confirm('Are you sure you want to delete this lesson?', async () => {
            try {
                await api.deleteLesson(lessonId);
                ui.showSuccess('Lesson deleted successfully');
                await this.loadLessons();
            } catch (error) {
                ui.showError(error.message || 'Failed to delete lesson');
            }
        });
    }
}

// Initialize lessons handler
const lessons = new LessonsHandler();
