// API Configuration and Client
const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }
    }

    getHeaders(isFormData = false) {
        const headers = {};
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        if (!isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.isFormData),
        };

        // Don't set Content-Type for FormData
        if (options.isFormData) {
            delete config.isFormData;
        }

        try {
            const response = await fetch(url, config);
            
            // Handle 204 No Content
            if (response.status === 204) {
                return { success: true };
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const data = await this.request('/api/auth/login', {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        this.setToken(data.access_token);
        return data;
    }

    async getCurrentUser() {
        return await this.request('/api/auth/me');
    }

    async registerUser(userData) {
        return await this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    logout() {
        this.setToken(null);
    }

    // Students
    async getStudents(skip = 0, limit = 100, isActive = null) {
        let url = `/api/students?skip=${skip}&limit=${limit}`;
        if (isActive !== null) {
            url += `&is_active=${isActive}`;
        }
        return await this.request(url);
    }

    async getStudent(id) {
        return await this.request(`/api/students/${id}`);
    }

    async createStudent(studentData) {
        return await this.request('/api/students', {
            method: 'POST',
            body: JSON.stringify(studentData),
        });
    }

    async updateStudent(id, studentData) {
        return await this.request(`/api/students/${id}`, {
            method: 'PUT',
            body: JSON.stringify(studentData),
        });
    }

    async deleteStudent(id) {
        return await this.request(`/api/students/${id}`, {
            method: 'DELETE',
        });
    }

    async enrollStudentFace(id, faceImage) {
        const formData = new FormData();
        formData.append('face_image', faceImage);

        return await this.request(`/api/students/${id}/enroll-face`, {
            method: 'POST',
            body: formData,
            isFormData: true,
        });
    }

    // Lessons
    async getLessons(skip = 0, limit = 100, statusFilter = null) {
        let url = `/api/lessons?skip=${skip}&limit=${limit}`;
        if (statusFilter) {
            url += `&status_filter=${statusFilter}`;
        }
        return await this.request(url);
    }

    async getLesson(id) {
        return await this.request(`/api/lessons/${id}`);
    }

    async createLesson(lessonData) {
        return await this.request('/api/lessons', {
            method: 'POST',
            body: JSON.stringify(lessonData),
        });
    }

    async updateLesson(id, lessonData) {
        return await this.request(`/api/lessons/${id}`, {
            method: 'PUT',
            body: JSON.stringify(lessonData),
        });
    }

    async deleteLesson(id) {
        return await this.request(`/api/lessons/${id}`, {
            method: 'DELETE',
        });
    }

    async startLesson(id) {
        return await this.request(`/api/lessons/${id}/start`, {
            method: 'POST',
        });
    }

    async endLesson(id) {
        return await this.request(`/api/lessons/${id}/end`, {
            method: 'POST',
        });
    }

    async uploadLessonMaterials(id, file) {
        const formData = new FormData();
        formData.append('materials_file', file);

        return await this.request(`/api/lessons/${id}/upload-materials`, {
            method: 'POST',
            body: formData,
            isFormData: true,
        });
    }

    async uploadLessonPresentation(id, file) {
        const formData = new FormData();
        formData.append('presentation_file', file);

        return await this.request(`/api/lessons/${id}/upload-presentation`, {
            method: 'POST',
            body: formData,
            isFormData: true,
        });
    }

    // Attendance
    async getAttendance(skip = 0, limit = 100, lessonId = null, studentId = null) {
        let url = `/api/attendance?skip=${skip}&limit=${limit}`;
        if (lessonId) url += `&lesson_id=${lessonId}`;
        if (studentId) url += `&student_id=${studentId}`;
        return await this.request(url);
    }

    async getLessonAttendance(lessonId) {
        return await this.request(`/api/attendance/lesson/${lessonId}`);
    }

    async getStudentAttendance(studentId) {
        return await this.request(`/api/attendance/student/${studentId}`);
    }

    async markAttendance(attendanceData) {
        return await this.request('/api/attendance', {
            method: 'POST',
            body: JSON.stringify(attendanceData),
        });
    }

    async deleteAttendance(id) {
        return await this.request(`/api/attendance/${id}`, {
            method: 'DELETE',
        });
    }

    // Q&A Sessions
    async getQASessions(skip = 0, limit = 100, lessonId = null, foundAnswer = null) {
        let url = `/api/qa?skip=${skip}&limit=${limit}`;
        if (lessonId) url += `&lesson_id=${lessonId}`;
        if (foundAnswer !== null) url += `&found_answer=${foundAnswer}`;
        return await this.request(url);
    }

    async getLessonQASessions(lessonId) {
        return await this.request(`/api/qa/lesson/${lessonId}`);
    }

    async getQASession(id) {
        return await this.request(`/api/qa/${id}`);
    }

    async createQASession(qaData) {
        return await this.request('/api/qa', {
            method: 'POST',
            body: JSON.stringify(qaData),
        });
    }

    async deleteQASession(id) {
        return await this.request(`/api/qa/${id}`, {
            method: 'DELETE',
        });
    }
}

// Initialize API client
const api = new APIClient(API_BASE_URL);
