# Admin Panel

Web-based administration interface for the AI Education System.

## Features

- **Dashboard**: View statistics and recent activity
- **Students Management**: Add, edit, delete students and enroll faces
- **Lessons Management**: Create lessons, upload materials, start/end lessons
- **Attendance Tracking**: View and manage attendance records
- **Q&A Sessions**: Monitor questions and answers
- **User Management**: Admin-only user administration

## Setup

The admin panel is automatically served by the FastAPI backend.

### Start the Server

```bash
# From project root
uvicorn backend.main:app --reload
```

### Access the Admin Panel

Open your browser and navigate to:
```
http://localhost:8000/admin
```

## Default Login

Use the default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

## File Structure

```
admin/
├── index.html          # Main HTML structure
├── css/
│   └── style.css      # Complete styling
└── js/
    ├── api.js         # API client
    ├── auth.js        # Authentication handler
    ├── ui.js          # UI utilities
    ├── app.js         # Main application controller
    ├── dashboard.js   # Dashboard handler
    ├── students.js    # Students management
    ├── lessons.js     # Lessons management
    ├── attendance.js  # Attendance tracking
    ├── qa.js          # Q&A sessions
    └── users.js       # User management
```

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Custom styling with CSS variables
- **Vanilla JavaScript** - No frameworks
- **Font Awesome 6.4.0** - Icons
- **Fetch API** - HTTP requests
- **JWT** - Authentication

## Features by Page

### Dashboard
- Total counts for students, lessons, attendance, Q&A
- Upcoming lessons
- Recent activity feed

### Students
- List all students with pagination
- Add new students with face enrollment
- Edit student information
- Delete students with confirmation
- Upload face images for recognition

### Lessons
- Create lessons with date/time
- Upload materials (PDF, DOCX, TXT)
- Upload presentations (PPT, PPTX, PDF)
- Start and end lessons
- Edit lesson details
- Delete lessons

### Attendance
- View all attendance records
- Filter by lesson or student
- Delete records
- Shows recognition confidence

### Q&A Sessions
- View all questions and answers
- Check answer status and confidence
- View detailed Q&A information
- Delete sessions

### Users
- Admin-only access
- View system users
- Manage user roles

## API Integration

All API calls use the `/api` prefix:
- `/api/auth` - Authentication
- `/api/students` - Students CRUD
- `/api/lessons` - Lessons CRUD
- `/api/attendance` - Attendance tracking
- `/api/qa` - Q&A sessions

## Security

- JWT token authentication
- Role-based access control (Admin, Teacher, Viewer)
- Token stored in localStorage
- Auto-logout on token expiration
- CORS enabled for development

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Modern browsers with ES6+ support

## Development

The admin panel uses a Single Page Application (SPA) pattern with vanilla JavaScript for minimal dependencies and fast performance.

### Key Design Patterns

1. **Modular JS**: Each page has its own handler class
2. **Shared UI**: Common utilities in `ui.js`
3. **Centralized API**: All endpoints in `api.js`
4. **Auth Guard**: Token validation on each request
5. **Toast Notifications**: User feedback for all actions
6. **Modal Dialogs**: Forms and confirmations

## Troubleshooting

### Cannot Login
- Check backend server is running on port 8000
- Verify database is initialized (`python backend/init_db.py`)
- Check browser console for errors

### API Errors
- Open DevTools > Network tab
- Check request/response details
- Verify CORS settings

### Static Files Not Loading
- Ensure `admin/` folder exists in project root
- Check FastAPI StaticFiles mount in `backend/main.py`
- Verify file paths are correct

## Future Enhancements

- Real-time updates with WebSockets
- Export data to CSV/Excel
- Advanced filtering and search
- Charts and visualizations
- Mobile-responsive design improvements
- Dark mode toggle
