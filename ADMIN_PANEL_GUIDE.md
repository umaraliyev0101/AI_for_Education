# Admin Panel - Frontend Development (External)

## 🎉 Admin Panel Frontend Development

The admin panel frontend has been removed from this repository as it will be developed by a separate team member.

## 📋 Quick Start

### 1. Login
Use the default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

### 2. Navigate the Dashboard
After login, you'll see:
- **Dashboard**: Overview statistics and recent activity
- **Students**: Manage student records and face enrollment
- **Lessons**: Create and manage lessons with materials
- **Attendance**: Track and review attendance records
- **Q&A**: Monitor question-answer sessions
- **Users**: Manage system users (Admin only)

## 🎯 Key Features

### Students Management
1. Click **"Add Student"** to register new students
2. Fill in student details (name, email, grade, etc.)
3. **Enroll Face**: Upload face image for recognition
4. **Edit/Delete**: Use action buttons on each row

### Lessons Management
1. Click **"Add Lesson"** to create new lessons
2. Set lesson title, description, and date/time
3. **Upload Materials**: PDF, DOCX, TXT files (for Q&A)
4. **Upload Presentations**: PPT, PPTX, PDF files
5. **Start Lesson**: Begin attendance tracking
6. **End Lesson**: Finalize the lesson

### Attendance Tracking
- View all attendance records
- Filter by lesson or student
- See recognition method and confidence
- Delete incorrect records

### Q&A Sessions
- Monitor questions asked during lessons
- Check if answers were found
- View relevance scores
- Delete sessions

## 🔧 Admin Panel Components

### Frontend Files
```
admin/
├── index.html          # Main page structure
├── css/style.css       # Complete styling
└── js/
    ├── app.js          # Main application controller
    ├── api.js          # API client
    ├── auth.js         # Authentication
    ├── ui.js           # UI utilities
    ├── dashboard.js    # Dashboard
    ├── students.js     # Students management
    ├── lessons.js      # Lessons management
    ├── attendance.js   # Attendance tracking
    ├── qa.js           # Q&A sessions
    └── users.js        # User management
```

### Backend Integration
The admin panel is served by FastAPI:
```python
# In backend/main.py
app.mount("/admin", StaticFiles(directory=admin_path, html=True))
```

All API calls go through `/api/*` endpoints:
- `/api/auth/login` - Authentication
- `/api/students` - Students CRUD
- `/api/lessons` - Lessons CRUD
- `/api/attendance` - Attendance tracking
- `/api/qa` - Q&A sessions

## 🎨 UI Features

- **Responsive Design**: Works on desktop and tablets
- **Toast Notifications**: Success/error messages
- **Modal Dialogs**: Forms and confirmations
- **Status Badges**: Visual status indicators
- **Icons**: Font Awesome icons throughout
- **Loading States**: Spinner animations

## 🚀 Next Steps

### 1. Test Each Feature
- [ ] Login with admin credentials
- [ ] Add a test student
- [ ] Create a test lesson
- [ ] Upload materials to a lesson
- [ ] Start and end a lesson
- [ ] View attendance records
- [ ] Check Q&A sessions

### 2. Customize (Optional)
- Update colors in `admin/css/style.css` (CSS variables at top)
- Modify layout in `admin/index.html`
- Add new features by extending handler classes

### 3. Production Setup
When deploying to production:
1. Change default admin password
2. Use environment variables for secrets
3. Enable HTTPS
4. Update CORS settings
5. Set `DEBUG=False`

## 🔐 Security Notes

- JWT tokens stored in localStorage
- Tokens expire after 30 days (configurable)
- Role-based access control (Admin, Teacher, Viewer)
- Admin-only features restricted

## 📞 Troubleshooting

### Cannot Access Admin Panel
```bash
# Check if server is running
curl http://localhost:8000/health

# Restart server
uvicorn backend.main:app --reload
```

### Login Issues
- Verify database is initialized: `python backend/init_db.py`
- Check browser console (F12) for errors
- Clear localStorage and try again

### Static Files Not Loading
- Check `admin/` folder exists in project root
- Verify file permissions
- Check browser DevTools > Network tab

## 📚 API Documentation

Full API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ✅ Testing Checklist

- [x] Backend server running on port 8000
- [x] Admin panel accessible at /admin
- [x] Login page loads
- [ ] Can login with admin credentials
- [ ] Dashboard loads statistics
- [ ] Can navigate between pages
- [ ] Can add/edit/delete students
- [ ] Can create lessons
- [ ] Can upload materials
- [ ] Toast notifications work
- [ ] Modals open/close correctly

## 🎊 Success!

Your admin panel is fully set up and ready to use. The interface provides complete control over:
- Student enrollment and management
- Lesson creation and materials
- Attendance tracking and reporting
- Q&A session monitoring
- User administration

**Enjoy your AI Education System! 🚀**
