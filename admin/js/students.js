// Students Handler
class StudentsHandler {
    async init() {
        await this.loadStudents();
        this.initEventListeners();
    }

    initEventListeners() {
        document.getElementById('add-student-btn').addEventListener('click', () => {
            this.showAddStudentModal();
        });
    }

    async loadStudents() {
        const tbody = document.querySelector('#students-table tbody');
        ui.showLoading(tbody, 'Loading students...');

        try {
            const students = await api.getStudents();
            
            if (students.length === 0) {
                ui.showEmptyState(tbody, 'No students found', 8);
                return;
            }

            tbody.innerHTML = students.map(student => `
                <tr>
                    <td>${student.id}</td>
                    <td><strong>${student.student_id}</strong></td>
                    <td>${student.name}</td>
                    <td>${student.email || 'N/A'}</td>
                    <td>${student.phone || 'N/A'}</td>
                    <td>${student.face_image_path ? ui.getBooleanBadge(true, 'Yes', 'No') : ui.getBooleanBadge(false, 'Yes', 'No')}</td>
                    <td>${ui.getActiveBadge(student.is_active)}</td>
                    <td class="action-buttons">
                        <button class="btn btn-sm btn-icon" onclick="students.enrollFace(${student.id})" title="Enroll Face">
                            <i class="fas fa-camera"></i>
                        </button>
                        <button class="btn btn-sm btn-icon" onclick="students.editStudent(${student.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-icon" onclick="students.deleteStudent(${student.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            ui.showError('Failed to load students');
            console.error('Error loading students:', error);
        }
    }

    showAddStudentModal() {
        const content = `
            <form id="add-student-form">
                <div class="form-group">
                    <label for="student_id">Student ID *</label>
                    <input type="text" id="student_id" name="student_id" required>
                </div>
                <div class="form-group">
                    <label for="name">Full Name *</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email">
                </div>
                <div class="form-group">
                    <label for="phone">Phone</label>
                    <input type="tel" id="phone" name="phone">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="is_active" name="is_active" checked> Active
                    </label>
                </div>
            </form>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
            <button class="btn btn-primary" id="submit-student-btn">Add Student</button>
        `;

        const modal = ui.showModal('<i class="fas fa-user-plus"></i> Add New Student', content, footer);

        modal.querySelector('#submit-student-btn').addEventListener('click', async () => {
            await this.submitAddStudent();
        });
    }

    async submitAddStudent() {
        const form = document.getElementById('add-student-form');
        const formData = new FormData(form);
        
        const studentData = {
            student_id: formData.get('student_id'),
            name: formData.get('name'),
            email: formData.get('email') || null,
            phone: formData.get('phone') || null,
            is_active: formData.get('is_active') === 'on'
        };

        const submitBtn = document.getElementById('submit-student-btn');
        ui.disableButton(submitBtn);

        try {
            await api.createStudent(studentData);
            ui.showSuccess('Student created successfully');
            ui.closeModal();
            await this.loadStudents();
        } catch (error) {
            ui.showError(error.message || 'Failed to create student');
        } finally {
            ui.enableButton(submitBtn);
        }
    }

    async enrollFace(studentId) {
        const content = `
            <p>Upload a clear photo of the student's face for facial recognition.</p>
            <div class="form-group">
                <label for="face_image">Face Image *</label>
                <input type="file" id="face_image" accept="image/*" required>
            </div>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
            <button class="btn btn-primary" id="upload-face-btn">Upload Face</button>
        `;

        const modal = ui.showModal('<i class="fas fa-camera"></i> Enroll Student Face', content, footer);

        modal.querySelector('#upload-face-btn').addEventListener('click', async () => {
            const fileInput = document.getElementById('face_image');
            const file = fileInput.files[0];

            if (!file) {
                ui.showError('Please select an image');
                return;
            }

            const uploadBtn = document.getElementById('upload-face-btn');
            ui.disableButton(uploadBtn);

            try {
                await api.enrollStudentFace(studentId, file);
                ui.showSuccess('Face enrolled successfully');
                ui.closeModal();
                await this.loadStudents();
            } catch (error) {
                ui.showError(error.message || 'Failed to enroll face');
            } finally {
                ui.enableButton(uploadBtn);
            }
        });
    }

    async editStudent(studentId) {
        try {
            const student = await api.getStudent(studentId);
            
            const content = `
                <form id="edit-student-form">
                    <div class="form-group">
                        <label for="edit_name">Full Name *</label>
                        <input type="text" id="edit_name" name="name" value="${student.name}" required>
                    </div>
                    <div class="form-group">
                        <label for="edit_email">Email</label>
                        <input type="email" id="edit_email" name="email" value="${student.email || ''}">
                    </div>
                    <div class="form-group">
                        <label for="edit_phone">Phone</label>
                        <input type="tel" id="edit_phone" name="phone" value="${student.phone || ''}">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="edit_is_active" name="is_active" ${student.is_active ? 'checked' : ''}> Active
                        </label>
                    </div>
                </form>
            `;

            const footer = `
                <button class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
                <button class="btn btn-primary" id="update-student-btn">Update Student</button>
            `;

            const modal = ui.showModal('<i class="fas fa-edit"></i> Edit Student', content, footer);

            modal.querySelector('#update-student-btn').addEventListener('click', async () => {
                const form = document.getElementById('edit-student-form');
                const formData = new FormData(form);
                
                const updateData = {
                    name: formData.get('name'),
                    email: formData.get('email') || null,
                    phone: formData.get('phone') || null,
                    is_active: formData.get('is_active') === 'on'
                };

                const updateBtn = document.getElementById('update-student-btn');
                ui.disableButton(updateBtn);

                try {
                    await api.updateStudent(studentId, updateData);
                    ui.showSuccess('Student updated successfully');
                    ui.closeModal();
                    await this.loadStudents();
                } catch (error) {
                    ui.showError(error.message || 'Failed to update student');
                } finally {
                    ui.enableButton(updateBtn);
                }
            });
        } catch (error) {
            ui.showError('Failed to load student details');
        }
    }

    async deleteStudent(studentId) {
        ui.confirm('Are you sure you want to delete this student?', async () => {
            try {
                await api.deleteStudent(studentId);
                ui.showSuccess('Student deleted successfully');
                await this.loadStudents();
            } catch (error) {
                ui.showError(error.message || 'Failed to delete student');
            }
        });
    }
}

// Initialize students handler
const students = new StudentsHandler();
