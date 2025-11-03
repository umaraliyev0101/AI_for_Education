# "Error Parsing File" Troubleshooting Guide

## Possible Causes

### 1. **Frontend Receiving HTML Instead of JSON**
**Symptom:** Frontend tries to parse response as JSON but gets HTML error page

**Causes:**
- Server returning error page (500 error)
- CORS pre-flight failing
- Authentication redirect to login page
- Wrong Content-Type header

**Check:**
```javascript
const response = await fetch(...);
console.log('Content-Type:', response.headers.get('content-type'));
console.log('Status:', response.status);
const text = await response.text();
console.log('Raw response:', text);
// Then try to parse
try {
  const json = JSON.parse(text);
} catch (e) {
  console.error('JSON parse error:', e);
}
```

### 2. **Response Format Mismatch**
**Symptom:** Response is JSON but frontend expects different structure

**Our Response:**
```json
{
  "message": "Presentation uploaded successfully",
  "filename": "lesson_1_presentation.pptx",
  "lesson_id": 1,
  "file_path": "D:\\...\\lesson_1_presentation.pptx",
  "file_size": 123456
}
```

**Check frontend code expects these fields**

### 3. **Network Error Before Response**
**Symptom:** Request fails before getting response

**Causes:**
- Network timeout
- CORS blocked
- Server crashed
- File too large (network timeout)

**Check:**
```javascript
try {
  const response = await fetch(...);
} catch (error) {
  console.error('Network error:', error);
  // This is NOT a response parse error - it's a network failure
}
```

### 4. **Wrong Endpoint Called**
**Symptom:** 404 Not Found or 405 Method Not Allowed

**Correct endpoints:**
- `POST /api/lessons/{lesson_id}/presentation`
- `POST /api/lessons/{lesson_id}/upload-presentation`

**Wrong endpoints that won't work:**
- `/api/presentation` (missing lesson_id)
- `GET /api/lessons/{lesson_id}/presentation` (wrong method)
- `/api/lessons/presentation/{lesson_id}` (wrong order)

### 5. **Server-Side Exception**
**Symptom:** 500 Internal Server Error

**Check server logs for:**
```
❌ Error saving file: ...
❌ Database commit failed: ...
❌ Unexpected error in upload: ...
```

## Debugging Steps

### Step 1: Check What Frontend is Sending
```javascript
console.log('=== UPLOAD REQUEST ===');
console.log('URL:', url);
console.log('Method:', 'POST');
console.log('Headers:', headers);
console.log('File:', file.name, file.size, file.type);
console.log('FormData fields:');
for (let pair of formData.entries()) {
  console.log(pair[0], pair[1]);
}
```

### Step 2: Check What Frontend is Receiving
```javascript
console.log('=== UPLOAD RESPONSE ===');
console.log('Status:', response.status);
console.log('OK:', response.ok);
console.log('Headers:', Object.fromEntries(response.headers));

// Get raw text first
const text = await response.text();
console.log('Raw response:', text);

// Try to parse
try {
  const json = JSON.parse(text);
  console.log('Parsed JSON:', json);
} catch (e) {
  console.error('JSON parse failed:', e);
  console.log('This is what caused "error parsing file"');
}
```

### Step 3: Use Browser DevTools Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Try upload
4. Click on the request
5. Check:
   - **Request Headers**: Authorization present?
   - **Request Payload**: File present?
   - **Response Headers**: Content-Type is application/json?
   - **Response**: Is it JSON or HTML?
   - **Status Code**: 200 OK or error?

### Step 4: Test with curl
```bash
# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Upload (replace TOKEN and adjust paths)
curl -X POST http://localhost:8001/api/lessons/1/presentation \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test.pptx" \
  -v

# The -v flag shows full request/response
```

## Common Frontend Mistakes

### ❌ WRONG: Manually parsing before checking status
```javascript
const response = await fetch(...);
const data = await response.json(); // Fails if status is 400, 500, etc.
```

### ✅ CORRECT: Check status first
```javascript
const response = await fetch(...);
if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail || 'Upload failed');
}
const data = await response.json();
```

### ❌ WRONG: Setting Content-Type for FormData
```javascript
const formData = new FormData();
formData.append('file', file);
fetch(url, {
  headers: {
    'Content-Type': 'multipart/form-data' // DON'T DO THIS
  },
  body: formData
});
```

### ✅ CORRECT: Let browser set Content-Type
```javascript
const formData = new FormData();
formData.append('file', file);
fetch(url, {
  // No Content-Type header - browser adds it with boundary
  body: formData
});
```

### ❌ WRONG: Not handling errors
```javascript
const response = await fetch(...);
const data = await response.json(); // Crashes if response is HTML
setData(data);
```

### ✅ CORRECT: Proper error handling
```javascript
try {
  const response = await fetch(...);
  
  // Check if response is JSON
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    const text = await response.text();
    throw new Error(`Expected JSON, got ${contentType}: ${text.substring(0, 100)}`);
  }
  
  // Check status
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Upload failed: ${response.status}`);
  }
  
  const data = await response.json();
  setData(data);
  
} catch (error) {
  console.error('Upload error:', error);
  setError(error.message);
}
```

## What to Check in Server Logs

When upload happens, you should see:
```
📤 Presentation upload request for lesson 1
   User: username
   File: test.pptx
   Reading file content...
   File size: 123456 bytes
   Saving to: D:\...\lesson_1_presentation.pptx
   ✅ File saved successfully
   Updating database with path: D:\...\lesson_1_presentation.pptx
   ✅ Database updated
✅ Upload complete: lesson_1_presentation.pptx (123456 bytes)
```

If you see errors:
```
❌ Lesson 1 not found
❌ File is empty  
❌ File too large: ...
❌ Error saving file: ...
❌ Database commit failed: ...
```

## Solution Checklist

- [ ] Server running on correct port (8001)?
- [ ] Frontend using correct URL?
- [ ] Authorization header included?
- [ ] Token is valid (not expired)?
- [ ] Field name is 'file' not something else?
- [ ] File is .pptx or .pdf?
- [ ] File is not empty?
- [ ] File is under 50MB?
- [ ] Lesson ID exists in database?
- [ ] Not setting Content-Type manually?
- [ ] Checking response.ok before parsing?
- [ ] Error handling in place?

## Still Not Working?

Run the test script:
```bash
python test_upload_debug.py
```

This will show exactly what's being sent and received, helping identify where the problem is.
