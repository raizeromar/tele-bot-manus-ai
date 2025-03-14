# Telegram AI Agent - API Documentation

## Project Structure

```
backend/telegram_ai_agent/
├── api/                    # Core API functionality
├── telegram_integration/   # Telegram-related features
├── ai_summarization/      # AI summarization features
└── telegram_ai_agent/     # Main project folder
```

## Authentication

**App**: `api`
**File**: `api/views.py`
Base URL: `/api/users/`

### Endpoints

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/register/` | POST | Register a new user | No |
| `/login/` | POST | Authenticate user and get session | No |
| `/logout/` | POST | End user session | Yes |

## Telegram Integration

**App**: `telegram_integration`
**File**: `telegram_integration/views.py`
Base URL: `/api/telegram/`

### Account Management
**File**: `telegram_integration/views/TelegramAccountViewSet`
Base URL: `/api/telegram/accounts/`

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/` | GET | List all user's Telegram accounts | Yes |
| `/` | POST | Create a new Telegram account | Yes |
| `/{id}/` | GET | Get specific account details | Yes |
| `/{id}/` | PUT/PATCH | Update account details | Yes |
| `/{id}/` | DELETE | Delete an account | Yes |
| `/{id}/authenticate/` | POST | Start Telegram authentication process | Yes |
| `/{id}/verify_code/` | POST | Verify Telegram authentication code | Yes |
| `/{id}/sync/` | POST | Sync groups and channels from Telegram account | Yes |

### Group Management
**File**: `telegram_integration/views/TelegramGroupViewSet`
Base URL: `/api/telegram/groups/`

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/` | GET | List all accessible Telegram groups | Yes |
| `/` | POST | Create/Join a new Telegram group | Yes |
| `/{id}/` | GET | Get specific group details | Yes |
| `/{id}/` | PUT/PATCH | Update group details | Yes |
| `/{id}/` | DELETE | Leave/Delete a group | Yes |
| `/join/` | POST | Join a new Telegram group | Yes |
| `/{id}/collect_messages/` | POST | Manually trigger message collection | Yes |

### Message Management
**File**: `telegram_integration/views/TelegramMessageViewSet`
Base URL: `/api/telegram/messages/`

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/` | GET | List all collected messages | Yes |
| `/{id}/` | GET | Get specific message details | Yes |

### Account-Group Associations
**File**: `telegram_integration/views/AccountGroupAssociationViewSet`
Base URL: `/api/telegram/associations/`

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/` | GET | List all account-group associations | Yes |
| `/` | POST | Create new association | Yes |
| `/{id}/` | GET | Get specific association details | Yes |
| `/{id}/` | DELETE | Remove association | Yes |

## AI Summarization

**App**: `ai_summarization`
**File**: `ai_summarization/views.py`
Base URL: `/api/ai/`

### Summaries
**File**: `ai_summarization/views/SummaryViewSet`
Base URL: `/api/ai/summaries/`

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/` | GET | List all summaries for user's groups | Yes |
| `/{id}/` | GET | Get specific summary details | Yes |
| `/generate/` | POST | Generate new summary | Yes |

### Summary Feedback
**File**: `ai_summarization/views/SummaryFeedbackViewSet`
Base URL: `/api/ai/feedback/`

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/` | GET | List all feedback provided by user | Yes |
| `/` | POST | Submit new feedback | Yes |
| `/{id}/` | GET | Get specific feedback details | Yes |
| `/{id}/` | PUT/PATCH | Update feedback | Yes |
| `/{id}/` | DELETE | Delete feedback | Yes |

## URL Configuration Files

### Main URLs
**File**: `telegram_ai_agent/urls.py`
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/telegram/', include('telegram_integration.urls')),
    path('api/ai/', include('ai_summarization.urls')),
]
```

### API URLs
**File**: `api/urls.py`
```python
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
```

### Telegram Integration URLs
**File**: `telegram_integration/urls.py`
```python
router = DefaultRouter()
router.register(r'accounts', TelegramAccountViewSet)
router.register(r'groups', TelegramGroupViewSet)
router.register(r'messages', TelegramMessageViewSet)
router.register(r'associations', AccountGroupAssociationViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
```

### AI Summarization URLs
**File**: `ai_summarization/urls.py`
```python
router = DefaultRouter()
router.register(r'summaries', SummaryViewSet)
router.register(r'feedback', SummaryFeedbackViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
```

## Request/Response Examples

### User Registration

```json
// POST /api/users/register/
Request:
{
    "username": "example_user",
    "email": "user@example.com",
    "password": "secure_password"
}

Response:
{
    "message": "Registration successful",
    "user": {
        "id": 1,
        "username": "example_user",
        "email": "user@example.com"
    }
}
```

### Telegram Account Authentication

```json
// POST /api/telegram/accounts/{id}/authenticate/
Request:
{
    "phone_number": "+1234567890"
}

Response:
{
    "message": "Authentication code sent",
    "phone_code_hash": "hash_value"
}

// POST /api/telegram/accounts/{id}/verify_code/
Request:
{
    "code": "12345",
    "phone_code_hash": "hash_value"
}

Response:
{
    "message": "Authentication successful",
    "account": {
        "id": 1,
        "phone_number": "+1234567890",
        "is_active": true
    }
}
```

### Summary Generation

```json
// POST /api/ai/summaries/generate/
Request:
{
    "group_id": 1,
    "days": 7
}

Response:
{
    "message": "Summary generated successfully",
    "summary": {
        "id": 1,
        "group": 1,
        "content": "Generated summary text...",
        "start_date": "2024-02-01T00:00:00Z",
        "end_date": "2024-02-07T23:59:59Z"
    }
}
```

### Account Sync

```json
// POST /api/telegram/accounts/{id}/sync/
Request:
{
    "phone_number": "+963937459456",
    "api_id": "29277175"
}

Response:
{
    "status": "success",
    "message": "Successfully synced account.",
    "details": {
        "groups_added": 5,
        "total_chats": 10
    }
}

// Error Response (Invalid Account)
{
    "error": "Account not found with provided phone number and API ID"
}

// Error Response (Not Authenticated)
{
    "error": "Account not authenticated"
}
```

The sync endpoint allows you to:
- Fetch all groups and channels from a Telegram account
- Automatically create or update groups in the database
- Create associations between the account and groups
- Track the number of new groups added

Note: The account must be authenticated before syncing can occur.

## Error Responses

All endpoints return appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error response format:
```json
{
    "error": "Error message description"
}
```

## Authentication

All authenticated endpoints require a valid session cookie or token. Include the authentication token in the request header:

```
Authorization: Bearer <token>
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Limits are:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Notes

- All timestamps are in UTC
- Pagination is implemented for list endpoints using limit/offset parameters
- Request bodies should be in JSON format
- Response data is always in JSON format