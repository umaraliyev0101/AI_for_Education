"""
Common Bad Request Issues for Presentation Upload
==================================================

ISSUE 1: File Extension Check
------------------------------
Current code: file.filename.endswith(('.pptx', '.pdf'))

Problems:
- Case sensitive! Will reject "file.PPTX" or "file.Pdf"
- Doesn't handle None filename
- Doesn't handle uppercase extensions

ISSUE 2: Missing Lesson
-----------------------
If lesson_id doesn't exist in database -> 404 NOT FOUND
But your friend might be getting "Bad Request" (400) not "Not Found" (404)

ISSUE 3: File Upload Format
---------------------------
The endpoint expects multipart/form-data with field name "file"
If using wrong field name or content type -> Bad Request

ISSUE 4: Authentication
-----------------------
If not authenticated properly -> Usually 401 Unauthorized
But might show as Bad Request in some cases

ISSUE 5: CORS
-------------
If uploading from browser and CORS not configured -> might appear as Bad Request

Let me create a better upload endpoint with detailed error messages...
"""

print(__doc__)
