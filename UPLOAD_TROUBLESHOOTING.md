# Presentation Upload Troubleshooting Guide
## "Failed to Upload Presentation" Error

### ✅ FIXED ISSUES

1. **Fixed parameter name mismatch** in `/upload-presentation` endpoint
   - Was: `presentation_file` 
   - Now: `file` (consistent across all endpoints)

2. **Added case-insensitive file extension checking**
   - Now accepts: `.pptx`, `.PPTX`, `.pdf`, `.PDF`

3. **Added better error messages**
   - Empty file detection
   - File size validation (max 50MB)
   - Missing file validation
   - Better error descriptions

4. **Added request logging**
   - Server now logs all upload attempts
   - Shows username, lesson ID, and filename

### 📋 UPLOAD ENDPOINTS

The API has TWO endpoints (both work the same way now):

1. **Main endpoint:**
   ```
   POST /api/lessons/{lesson_id}/presentation
   ```

2. **Legacy endpoint:**
   ```
   POST /api/lessons/{lesson_id}/upload-presentation
   ```

### 🔧 REQUIREMENTS

For upload to succeed, ALL of these must be true:

1. ✅ **Authentication**: Must include Bearer token in Authorization header
2. ✅ **Lesson exists**: The `lesson_id` must exist in database
3. ✅ **Field name**: File field must be named `file` (not `presentation`, `upload`, etc.)
4. ✅ **File type**: Must be `.pptx` or `.pdf` (case insensitive)
5. ✅ **File size**: Must be less than 50MB
6. ✅ **Not empty**: File must contain data

### 🌐 CORRECT FRONTEND CODE

#### JavaScript/React Example:
```javascript
const uploadPresentation = async (lessonId, file) => {
  // Get auth token (from login response or localStorage)
  const token = localStorage.getItem('access_token');
  
  // Create form data with field name "file"
  const formData = new FormData();
  formData.append('file', file);  // MUST be named 'file'
  
  try {
    const response = await fetch(
      `http://localhost:8001/api/lessons/${lessonId}/presentation`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
          // DO NOT set Content-Type - browser sets it automatically for FormData
        },
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    
    const result = await response.json();
    console.log('Upload successful:', result);
    return result;
    
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};
```

#### Axios Example:
```javascript
const uploadPresentation = async (lessonId, file) => {
  const token = localStorage.getItem('access_token');
  
  const formData = new FormData();
  formData.append('file', file);  // MUST be named 'file'
  
  try {
    const response = await axios.post(
      `http://localhost:8001/api/lessons/${lessonId}/presentation`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          // DO NOT set Content-Type - axios handles it
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Upload error:', error.response?.data || error);
    throw error;
  }
};
```

### 🐛 COMMON MISTAKES

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong field name | 400 Bad Request | Use `file` not `presentation_file` |
| Missing token | 401 Unauthorized | Add `Authorization: Bearer {token}` header |
| Wrong lesson ID | 404 Not Found | Verify lesson exists |
| Wrong file type | 400 Bad Request | Use .pptx or .pdf |
| Manual Content-Type | Upload fails | Don't set Content-Type - let browser/axios set it |
| Empty file | 400 Bad Request | Verify file has content |
| File too large | 400 Bad Request | Keep under 50MB |

### 📊 CHECKING SERVER LOGS

When upload fails, check server terminal for:
```
📤 Presentation upload request for lesson X
   User: username
   File: filename.pptx
```

Then look for error messages like:
- ❌ `No file provided or filename is missing`
- ❌ `Unsupported file type: filename.doc`
- ❌ `Uploaded file is empty`
- ❌ `File too large. Maximum size: 50MB`
- ❌ `Lesson with ID X not found`

### 🔍 DEBUGGING STEPS

1. **Check authentication**:
   ```javascript
   const token = localStorage.getItem('access_token');
   console.log('Token:', token ? 'Present' : 'Missing');
   ```

2. **Check file**:
   ```javascript
   console.log('File name:', file.name);
   console.log('File type:', file.type);
   console.log('File size:', file.size, 'bytes');
   ```

3. **Check FormData**:
   ```javascript
   for (let pair of formData.entries()) {
     console.log(pair[0], pair[1]);
   }
   ```

4. **Check response**:
   ```javascript
   const response = await fetch(...);
   console.log('Status:', response.status);
   const text = await response.text();
   console.log('Response:', text);
   ```

### ✅ SUCCESS RESPONSE

When upload succeeds, you'll get:
```json
{
  "message": "Presentation uploaded successfully",
  "filename": "lesson_1_presentation.pptx",
  "lesson_id": 1,
  "file_path": "D:\\Projects\\AI_in_Education\\uploads\\presentations\\lesson_1_presentation.pptx",
  "file_size": 123456
}
```

### 🎯 NEXT STEPS AFTER UPLOAD

After successful upload, call the process endpoint to generate slides:
```javascript
const response = await fetch(
  `http://localhost:8001/api/lessons/${lessonId}/presentation/process`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);
```

### 📞 STILL NOT WORKING?

1. Check server is running on port 8001
2. Check browser console for errors
3. Check browser Network tab to see actual request
4. Check server terminal for detailed logs
5. Try using curl to isolate frontend vs backend issue:
   ```bash
   curl -X POST http://localhost:8001/api/lessons/1/presentation \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@/path/to/test.pptx"
   ```
