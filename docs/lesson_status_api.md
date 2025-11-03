# Lesson Status Update API

## Overview
The lesson status can be updated using the general lesson update endpoint. This provides flexible status management for lessons along with other lesson properties.

## Endpoint

### Update Lesson (Including Status)
**PUT** `/api/v1/lessons/{lesson_id}`

Updates lesson information including status. Requires teacher or admin authentication.

#### Request (Update Status Only)
```json
{
  "status": "in_progress"
}
```

#### Request (Update Status and Date for Rescheduling)
```json
{
  "status": "scheduled",
  "date": "2025-11-10T08:00:00Z"
}
```

#### Valid Status Values
- `scheduled` - Lesson is scheduled but not started
- `in_progress` - Lesson is currently ongoing
- `completed` - Lesson has been completed
- `cancelled` - Lesson has been cancelled

#### Response
```json
{
  "id": 1,
  "title": "Algebra Basics",
  "description": "Introduction to algebra",
  "date": "2025-11-05T10:00:00Z",
  "duration_minutes": 60,
  "subject": "Mathematics",
  "notes": null,
  "start_time": "2025-11-05T10:00:00Z",
  "end_time": null,
  "presentation_path": "/path/to/presentation.pptx",
  "materials_path": "/path/to/materials.pdf",
  "vector_store_path": null,
  "status": "in_progress",
  "created_at": "2025-11-01T08:00:00Z",
  "updated_at": "2025-11-05T10:00:00Z"
}
```

## Automatic Timestamp Management

The endpoint automatically manages timestamps based on the status:

1. **Setting to `in_progress`**: 
   - Automatically sets `start_time` to current time (if not already set)

2. **Setting to `completed`**: 
   - Automatically sets `end_time` to current time (if not already set)

3. **Setting to `scheduled`**: 
   - Resets both `start_time` and `end_time` to null (for rescheduling)

4. **Setting to `cancelled`**: 
   - No timestamp changes

## Recommended Status Transitions

```
SCHEDULED → IN_PROGRESS → COMPLETED
           ↓               ↓
        CANCELLED ← ──────┘
           ↓
        SCHEDULED (reschedule)
```

## Usage Examples

### Python Example
```python
import requests

# Configuration
API_URL = "http://localhost:8001/api/v1"
token = "your_access_token"

# Update lesson status only
response = requests.put(
    f"{API_URL}/lessons/1",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={"status": "in_progress"}
)

if response.status_code == 200:
    lesson = response.json()
    print(f"Lesson status updated to: {lesson['status']}")
else:
    print(f"Error: {response.text}")

# Reschedule a completed lesson (update status + date)
response = requests.put(
    f"{API_URL}/lessons/1",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "status": "scheduled",
        "date": "2025-11-10T08:00:00Z"
    }
)
```

### cURL Example
```bash
# Update status only
curl -X PUT http://localhost:8001/api/v1/lessons/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# Reschedule lesson
curl -X PUT http://localhost:8001/api/v1/lessons/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "scheduled", "date": "2025-11-10T08:00:00Z"}'
```

### JavaScript/Fetch Example
```javascript
const updateLessonStatus = async (lessonId, newStatus) => {
  const response = await fetch(
    `http://localhost:8001/api/v1/lessons/${lessonId}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: newStatus })
    }
  );
  
  if (response.ok) {
    const lesson = await response.json();
    console.log('Updated lesson:', lesson);
  } else {
    console.error('Failed to update status');
  }
};

// Usage
await updateLessonStatus(1, 'in_progress');

// Reschedule a lesson
const rescheduleLesson = async (lessonId, newDate) => {
  const response = await fetch(
    `http://localhost:8001/api/v1/lessons/${lessonId}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        status: 'scheduled',
        date: newDate 
      })
    }
  );
  
  return response.json();
};
```

## Alternative Endpoints

For standard workflow, you can also use these specialized endpoints:

- **POST** `/api/v1/lessons/{lesson_id}/start` - Start a lesson (SCHEDULED → IN_PROGRESS)
- **POST** `/api/v1/lessons/{lesson_id}/end` - End a lesson (IN_PROGRESS → COMPLETED)

These endpoints have validation to ensure proper status transitions.

## Error Responses

### 404 Not Found
```json
{
  "detail": "Lesson with ID 123 not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Only teachers and administrators can update lesson status"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "status"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

## Testing

A test script is provided in `test_lesson_status.py` to verify the functionality:

```bash
# Make sure the backend is running on port 8001
python test_lesson_status.py
```

## Schema Definition

### LessonUpdate Schema
```python
class LessonUpdate(BaseModel):
    """Schema for updating lesson information"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    subject: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[LessonStatus] = None
```

### LessonStatus Enum
```python
class LessonStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

## Notes

- This endpoint requires teacher or admin authentication
- The general `PUT /api/v1/lessons/{lesson_id}` endpoint can also update status along with other fields
- Use this PATCH endpoint when you only need to update the status
- Status changes are logged through the `updated_at` timestamp
