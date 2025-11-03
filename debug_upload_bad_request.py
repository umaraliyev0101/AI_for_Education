#!/usr/bin/env python3
"""
Debug Script for Presentation Upload Bad Request Errors
========================================================
This script helps diagnose why presentation uploads are failing
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

print("="*70)
print("PRESENTATION UPLOAD DEBUGGING TOOL")
print("="*70)

# Test 1: Check if server is running
print("\n[1] Testing server connectivity...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("    ✅ Server is running")
    else:
        print(f"    ⚠️  Server responded with status {response.status_code}")
except Exception as e:
    print(f"    ❌ Cannot connect to server: {e}")
    print(f"    Make sure server is running on {BASE_URL}")
    exit(1)

# Test 2: Check CORS headers
print("\n[2] Checking CORS configuration...")
try:
    response = requests.options(f"{API_URL}/lessons/1/presentation/upload")
    cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
    if cors_headers:
        print("    ✅ CORS headers present:")
        for k, v in cors_headers.items():
            print(f"       {k}: {v}")
    else:
        print("    ⚠️  No CORS headers found (might cause issues from browser)")
except Exception as e:
    print(f"    ⚠️  Could not check CORS: {e}")

# Test 3: Test file upload validation
print("\n[3] Common Bad Request Causes:")
print("    ❌ Missing authentication token")
print("    ❌ Wrong lesson_id (lesson doesn't exist)")
print("    ❌ Wrong file format (not .pptx or .pdf)")
print("    ❌ File field name is not 'file'")
print("    ❌ Empty file")
print("    ❌ File too large (>50MB)")
print("    ❌ Uppercase extension (.PPTX instead of .pptx)")

# Test 4: Show proper request format
print("\n[4] Correct Upload Format (using curl):")
print("-" * 70)
print("""
# Get authentication token first
curl -X POST {base}/api/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=YOUR_USERNAME&password=YOUR_PASSWORD"

# Upload presentation (field name MUST be "file")
curl -X POST {base}/api/lessons/{{lesson_id}}/presentation/upload \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -F "file=@/path/to/presentation.pptx"

# IMPORTANT:
# - Field name must be "file" (not "presentation_file" or anything else)
# - File extension must be .pptx or .pdf (case insensitive now)
# - Authorization header is required
# - lesson_id must exist in database
""".format(base=BASE_URL))

# Test 5: Show Python requests format
print("\n[5] Correct Upload Format (using Python requests):")
print("-" * 70)
print("""
import requests

# Login
login_response = requests.post(
    "{base}/api/auth/login",
    data={{"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}}
)
token = login_response.json()["access_token"]

# Upload file
files = {{"file": open("presentation.pptx", "rb")}}
headers = {{"Authorization": f"Bearer {{token}}"}}

response = requests.post(
    "{base}/api/lessons/1/presentation/upload",
    files=files,
    headers=headers
)

print(response.status_code)
print(response.json())
""".format(base=BASE_URL))

# Test 6: Show JavaScript/Fetch format
print("\n[6] Correct Upload Format (using JavaScript/Fetch):")
print("-" * 70)
print("""
// Login first
const loginResponse = await fetch('{base}/api/auth/login', {{
  method: 'POST',
  headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
  body: 'username=YOUR_USERNAME&password=YOUR_PASSWORD'
}});
const {{ access_token }} = await loginResponse.json();

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);  // MUST be named 'file'

const response = await fetch('{base}/api/lessons/1/presentation/upload', {{
  method: 'POST',
  headers: {{ 'Authorization': `Bearer ${{access_token}}` }},
  body: formData
}});

const result = await response.json();
console.log(result);
""".format(base=BASE_URL))

# Test 7: API endpoint info
print("\n[7] Endpoint Details:")
print("-" * 70)
print(f"    URL: POST {API_URL}/lessons/{{lesson_id}}/presentation/upload")
print(f"    Auth: Required (Bearer token)")
print(f"    Content-Type: multipart/form-data")
print(f"    Field name: 'file'")
print(f"    Supported formats: .pptx, .pdf (case insensitive)")
print(f"    Max file size: 50 MB")

print("\n[8] Troubleshooting Steps:")
print("-" * 70)
print("    1. Check if you're authenticated (include Bearer token)")
print("    2. Verify lesson_id exists in database")
print("    3. Ensure file field name is 'file' (not 'presentation' or 'upload')")
print("    4. Check file extension is .pptx or .pdf")
print("    5. Make sure file is not empty")
print("    6. Check file size is under 50MB")
print("    7. Look at server logs for detailed error message")

print("\n[9] Check Server Logs:")
print("-" * 70)
print("    Look for detailed error messages in your server terminal")
print("    The updated endpoint now provides specific error messages:")
print("    - 'No file provided or filename is missing'")
print("    - 'Unsupported file type: [filename]'")
print("    - 'Uploaded file is empty'")
print("    - 'File too large. Maximum size: 50MB'")

print("\n" + "="*70)
print("For more help, check the API documentation at:")
print(f"{BASE_URL}/docs")
print("="*70)
