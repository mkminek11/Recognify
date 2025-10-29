# 🔌 Recognify API Documentation

This document provides comprehensive documentation for the Recognify REST API.

## Base URL
```
https://recognify.onrender.com
```

*For local development: `http://localhost:5000`*

## Authentication

The API uses session-based authentication with Flask-Login. Users must be logged in to access most endpoints.

### Auth Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass
```

#### Sign Up
```http
POST /auth/signup
Content-Type: application/x-www-form-urlencoded

username=user&email=user@example.com&password=pass
```

---

## Draft Management

Drafts are work-in-progress sets that can be edited before submission.

### Get Draft Gallery
```http
GET /api/draft/{draft_hash}/gallery
```

**Response:**
```json
{
  "images": [
    {
      "id": 1,
      "filename": "img_000001.jpg",
      "label": "Example Label",
      "slide": "encoded_slide_id"
    }
  ],
  "labels": [
    {
      "text": "Label Text",
      "slide": "encoded_slide_id"
    }
  ]
}
```

### Upload Images to Draft
```http
POST /api/draft/{draft_hash}/gallery
Content-Type: multipart/form-data

images: [file1, file2, ...]
```

### Add Image from URL
```http
POST /api/draft/{draft_hash}/gallery/url
Content-Type: application/json

{
  "url": "https://example.com/image.jpg"
}
```

### Update Image Label
```http
POST /api/draft/{draft_hash}/image/{image_id}
Content-Type: application/json

{
  "label": "New Label"
}
```

### Delete Draft Image
```http
DELETE /api/draft/{draft_hash}/image/{image_id}
```

### Get Draft Image
```http
GET /api/draft/{draft_hash}/image/{image_id}
```
Returns the actual image file.

### Submit Draft (Convert to Set)
```http
POST /api/draft/{draft_hash}/submit
Content-Type: application/json

{
  "images": [
    {
      "img": {"id": "image_id"},
      "label": "Final Label"
    }
  ]
}
```

### Update Draft Title
```http
POST /api/draft/{draft_hash}/rename
Content-Type: application/json

{
  "title": "New Draft Title"
}
```

### Update Draft Description
```http
POST /api/draft/{draft_hash}/description
Content-Type: application/json

{
  "description": "New description"
}
```

### Change Image from File
```http
POST /api/draft/{draft_hash}/change/image
Content-Type: multipart/form-data

image: file
change_id: image_id
```

### Change Image from URL
```http
POST /api/draft/{draft_hash}/change/url
Content-Type: multipart/form-data

url: https://example.com/new-image.jpg
change_id: image_id
```

### Delete Draft
```http
DELETE /api/draft/{draft_hash}/
```

---

## Set Operations

Sets are finalized collections ready for learning.

### View Set (Web Interface)
```http
GET /set/{set_hash}
```
Returns HTML page for viewing set details.

### Play Set (Web Interface)
```http
GET /set/{set_hash}/play
```
Returns HTML page for interactive learning.

### Get Set Image
```http
GET /api/set/{set_hash}/image/{image_id}
```
Returns the actual image file.

### Skip Image
```http
POST /api/set/{set_hash}/skip
Content-Type: application/json

{
  "image_id": 123
}
```
Marks an image as "known" so it won't appear in future learning sessions.

### Delete Set
```http
DELETE /api/set/{set_hash}
```
**Requires admin permissions (permission >= 1)**

---

## Presentation Processing

Extract images and labels from PowerPoint files.

### Process Presentation
```http
POST /api/presentation
Content-Type: multipart/form-data

presentation: file.pptx
draft: draft_hash
```

**Response:**
```json
{
  "images": [
    {
      "id": 1,
      "filename": "img_000001.jpg",
      "label": "",
      "slide": "encoded_slide_id"
    }
  ],
  "labels": [
    {
      "text": "Extracted Label",
      "slide": "encoded_slide_id"
    }
  ]
}
```

---

## Admin Operations

These endpoints require elevated permissions.

### Delete All Drafts
```http
DELETE /api/draft
```
**Requires admin permissions (permission >= 1)**

### Delete All Sets
```http
DELETE /api/set
```
**Requires admin permissions (permission >= 1)**

---

## Error Responses

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": "Error message description"
}
```

**Success Response Format:**
```json
{
  "message": "Success message",
  "data": {
    // Additional response data
  }
}
```

---

## Hash IDs

Recognify uses hash-based IDs for security. These are generated using the Hashids library and prevent enumeration of resources. Example: `L72ODlGx`

---

## File Upload Constraints

- **Image Extensions**: `png`, `jpg`, `jpeg`
- **Max File Size**: No explicit limit (be reasonable)
- **Presentation Types**: PowerPoint (`.pptx`)

---

## Rate Limiting

Currently no rate limiting is implemented, but be respectful of server resources.

---

## WebHook Support

Not currently supported.

---

## SDK/Libraries

No official SDKs available. Use standard HTTP libraries for your platform:
- JavaScript: `axios`, `fetch`
- Python: `requests`
- curl: For testing

**Example with curl:**
```bash
# Login
curl -X POST https://recognify.onrender.com/auth/login \
  -d "username=test&password=test" \
  -c cookies.txt

# Get draft gallery
curl -X GET https://recognify.onrender.com/api/draft/ABC123/gallery \
  -b cookies.txt
```