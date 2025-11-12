# 🚀 Quick Deployment Checklist

Use this checklist to ensure a smooth deployment of your AI Education Platform.

---

## 📋 Pre-Deployment Checklist

### Local Development
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] Database initialized (`python -m backend.init_db`)
- [ ] Server starts without errors
- [ ] API documentation accessible at `/docs`
- [ ] Can login with default credentials (admin/admin123)
- [ ] Test file uploads (materials, presentations, faces)
- [ ] Test face recognition enrollment
- [ ] Test Q&A system
- [ ] Test presentation delivery

### Production Server
- [ ] Server OS updated (`sudo apt update && sudo apt upgrade`)
- [ ] Python 3.11+ installed
- [ ] Nginx installed
- [ ] Domain name configured and pointing to server
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Application user created (`aiedu`)
- [ ] Application cloned to server
- [ ] Production `.env` configured with secure values
- [ ] Database initialized
- [ ] Systemd service created and enabled
- [ ] Nginx configuration created and enabled
- [ ] Static files accessible
- [ ] WebSocket connections working
- [ ] Logs directory created and writable

---

## 🔐 Security Checklist

### Environment Configuration
- [ ] `SECRET_KEY` generated and unique (32+ characters)
- [ ] `DEBUG=False` in production
- [ ] `CORS_ORIGINS` set to specific domains (not `*`)
- [ ] Database credentials strong and secure
- [ ] `.env` file not committed to git
- [ ] `.env` file has restricted permissions (600)

### Server Security
- [ ] SSH key authentication enabled
- [ ] Password authentication disabled (SSH)
- [ ] Firewall enabled and configured
- [ ] Fail2ban installed and configured
- [ ] Automatic security updates enabled
- [ ] Non-root user for application
- [ ] File permissions properly set (755 for dirs, 644 for files)
- [ ] SSL/TLS configured with strong ciphers
- [ ] HSTS header enabled
- [ ] Rate limiting configured (optional)

### Application Security
- [ ] Default admin password changed
- [ ] Additional admin users created with strong passwords
- [ ] File upload size limits configured
- [ ] File type validation working
- [ ] API endpoints require authentication
- [ ] Role-based access control working
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention (input validation)

---

## ⚙️ Configuration Checklist

### Application Settings
- [ ] App name and version set
- [ ] Database URL configured
- [ ] Upload directories created with proper permissions
- [ ] Vector store directory created
- [ ] Logs directory created
- [ ] Max upload size configured appropriately
- [ ] Token expiration time set
- [ ] CORS origins configured

### AI Models
- [ ] STT model accessible and downloading
- [ ] Embedding model accessible
- [ ] TTS voice configured
- [ ] GPU support configured (if available)
- [ ] Model cache directory configured

### Server Configuration
- [ ] Gunicorn workers set appropriately (2*CPU+1)
- [ ] Worker timeout set for long operations (300s+)
- [ ] Nginx worker processes set
- [ ] Nginx worker connections set
- [ ] Client max body size set (50MB+)
- [ ] Proxy timeouts configured for AI operations

---

## 🧪 Testing Checklist

### Basic Functionality
- [ ] Health check endpoint responds (`/health`)
- [ ] Root endpoint responds (`/`)
- [ ] API docs accessible (`/docs`)
- [ ] Login works with valid credentials
- [ ] Login fails with invalid credentials
- [ ] JWT token generated on login
- [ ] Protected endpoints require authentication

### Student Management
- [ ] List students
- [ ] Create new student
- [ ] Update student information
- [ ] View student details
- [ ] Face enrollment for student
- [ ] Student activation/deactivation

### Lesson Management
- [ ] Create new lesson
- [ ] List lessons
- [ ] Update lesson
- [ ] Delete lesson (admin only)
- [ ] Upload lesson materials
- [ ] Upload presentation
- [ ] Process presentation slides
- [ ] Start lesson
- [ ] End lesson
- [ ] Lesson status changes automatically

### Attendance
- [ ] Manual attendance marking
- [ ] Face recognition attendance
- [ ] View attendance records
- [ ] Attendance by lesson
- [ ] Attendance by student
- [ ] Attendance reports

### Q&A System
- [ ] Ask text question
- [ ] Ask audio question (with Uzbek audio)
- [ ] Receive AI-generated answer
- [ ] View Q&A history
- [ ] Q&A by lesson
- [ ] Delete Q&A session

### Presentation Delivery
- [ ] WebSocket connection establishes
- [ ] Slides display correctly
- [ ] TTS audio plays
- [ ] Navigation (next/previous) works
- [ ] Pause/resume works
- [ ] Progress tracking works

### File Operations
- [ ] File upload works (materials, presentations, faces)
- [ ] File size limits enforced
- [ ] File type validation works
- [ ] Static files accessible via `/uploads/`
- [ ] Face images stored correctly
- [ ] Audio files stored correctly
- [ ] Presentation slides generated

### Performance
- [ ] Page load times acceptable (<2s)
- [ ] API response times acceptable (<1s for simple queries)
- [ ] File upload works for large files (up to limit)
- [ ] STT processing completes in reasonable time
- [ ] Q&A response generation acceptable (<10s)
- [ ] Face recognition processing fast (<2s)
- [ ] Multiple concurrent users supported

---

## 📊 Monitoring Checklist

### Application Monitoring
- [ ] Application logs accessible and readable
- [ ] Error logs being written
- [ ] Access logs being written
- [ ] Log rotation configured
- [ ] Disk space monitoring
- [ ] Memory usage monitoring
- [ ] CPU usage monitoring

### Service Health
- [ ] Systemd service status green
- [ ] Nginx status green
- [ ] Database accessible
- [ ] No error spikes in logs
- [ ] Response times normal
- [ ] WebSocket connections stable

### Backup & Recovery
- [ ] Backup script created
- [ ] Backup schedule configured (daily recommended)
- [ ] Backup location configured
- [ ] Backup retention policy set (7-30 days)
- [ ] Database backup tested
- [ ] Upload files backup tested
- [ ] Recovery procedure documented
- [ ] Recovery tested on staging environment

---

## 📱 Post-Deployment Checklist

### Immediate Actions (Day 1)
- [ ] Change default admin password
- [ ] Create initial teacher accounts
- [ ] Test all critical features
- [ ] Monitor logs for errors
- [ ] Verify SSL certificate
- [ ] Test from external network
- [ ] Test on different devices
- [ ] Document any issues

### First Week
- [ ] Create user documentation
- [ ] Train staff on system usage
- [ ] Enroll first batch of students
- [ ] Conduct pilot lesson
- [ ] Gather user feedback
- [ ] Monitor system performance
- [ ] Check backup execution
- [ ] Review security logs

### First Month
- [ ] Review system usage metrics
- [ ] Optimize performance if needed
- [ ] Address user feedback
- [ ] Update documentation
- [ ] Plan feature enhancements
- [ ] Review security posture
- [ ] Test disaster recovery
- [ ] Update system dependencies

---

## 🐛 Common Issues Checklist

If something goes wrong, check:

### Application Won't Start
- [ ] Virtual environment activated
- [ ] Dependencies installed correctly
- [ ] `.env` file exists and readable
- [ ] Database file exists and writable
- [ ] Upload directories exist
- [ ] Port 8001 not already in use
- [ ] Python version is 3.11+

### Database Issues
- [ ] Database file permissions correct (644)
- [ ] Database directory writable
- [ ] Database initialized (`init_db.py` run)
- [ ] No database locks active
- [ ] SQLite version compatible

### Authentication Issues
- [ ] `SECRET_KEY` configured
- [ ] Token not expired
- [ ] User exists in database
- [ ] Password correct
- [ ] User is active

### File Upload Issues
- [ ] Upload directories exist
- [ ] Directory permissions correct (755)
- [ ] Disk space available
- [ ] File size within limit
- [ ] File type allowed

### Face Recognition Issues
- [ ] Camera accessible
- [ ] OpenCV installed correctly
- [ ] Face images in correct directory
- [ ] Face database initialized
- [ ] Sufficient lighting for recognition

### STT/TTS Issues
- [ ] Models downloaded
- [ ] Hugging Face accessible
- [ ] Audio format supported
- [ ] Audio file not corrupted
- [ ] Sufficient memory for model

### Performance Issues
- [ ] Sufficient RAM available (8GB+)
- [ ] CPU not maxed out
- [ ] Disk not full
- [ ] Number of workers appropriate
- [ ] Database not locked
- [ ] No memory leaks

---

## ✅ Deployment Complete!

Once all items are checked:

1. Document your deployment configuration
2. Save your `.env` file securely
3. Create admin account backups
4. Share API documentation with developers
5. Train users on the system
6. Monitor logs regularly
7. Keep dependencies updated
8. Review security monthly

---

## 📞 Support

If you encounter issues:
- Check logs: `sudo journalctl -u aiedu -f`
- Check application logs: `tail -f logs/error.log`
- Review DEPLOYMENT.md for detailed instructions
- Check GitHub issues
- Contact support

**Good luck with your deployment! 🚀**
