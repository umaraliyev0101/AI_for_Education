#!/usr/bin/env python3
"""
Test presentation upload and processing via API
"""
import requests
import json

BASE_URL = "http://localhost:8001/api"

# First, you need to:
# 1. Get a valid auth token by logging in
# 2. Create a lesson
# 3. Upload a presentation to that lesson

print("="*60)
print("PRESENTATION UPLOAD & PROCESSING TEST")
print("="*60)

# Example: Check if server is running
try:
    response = requests.get(f"{BASE_URL.replace('/api', '')}/docs", timeout=2)
    if response.status_code == 200:
        print("✅ Server is running at http://localhost:8001")
        print(f"📖 API docs: http://localhost:8001/docs")
    else:
        print(f"⚠️  Server responded with status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Server is not running!")
    print("   Start it with: uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload")
    exit(1)

print("\n" + "="*60)
print("TO UPLOAD A PRESENTATION:")
print("="*60)
print("1. Go to http://localhost:8001/docs")
print("2. Authorize with your credentials")
print("3. Create a lesson (POST /api/lessons/)")
print("4. Upload presentation (POST /api/lessons/{lesson_id}/presentation/upload)")
print("   - Use a .pptx or .pdf file")
print("5. Process presentation (POST /api/lessons/{lesson_id}/presentation/process)")
print("   - This will generate slide images and audio")
print("6. Check uploads/slides/lesson_{id}/ for generated PNG files")

print("\n" + "="*60)
print("OR USE CURL:")
print("="*60)
print("""
# Step 1: Login to get token
curl -X POST http://localhost:8001/api/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=your_username&password=your_password"

# Step 2: Create a lesson
curl -X POST http://localhost:8001/api/lessons/ \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Test Lesson", "subject": "Math", "scheduled_at": "2025-11-01T10:00:00"}'

# Step 3: Upload presentation
curl -X POST http://localhost:8001/api/lessons/1/presentation/upload \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -F "file=@path/to/your/presentation.pptx"

# Step 4: Process presentation
curl -X POST http://localhost:8001/api/lessons/1/presentation/process \\
  -H "Authorization: Bearer YOUR_TOKEN"
""")

print("\n" + "="*60)
print("TROUBLESHOOTING:")
print("="*60)
print("If slides still don't generate after processing:")
print("1. Check server logs for PowerPoint COM errors")
print("2. Make sure PowerPoint is installed")
print("3. Check uploads/slides/lesson_{id}/ directory")
print("4. Look for error messages in the API response")
