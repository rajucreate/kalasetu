# Quick API Reference

## Setup & Running

```bash
# Install SimpleJWT if not already installed
pip install djangorestframework-simplejwt

# Run migrations (if any)
python manage.py migrate

# Start server
python manage.py runserver
```

## API Base URL
```
http://localhost:8000/api/
```

## Authentication

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Use Token in Requests
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/products/
```

## Core Endpoints

### User Management
| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | /auth/register/ | Register user | No |
| POST | /auth/login/ | Get JWT token | No |
| POST | /auth/refresh/ | Refresh token | No |
| GET | /auth/me/ | Get profile | Yes |
| PUT | /auth/me/ | Update profile | Yes |

### Products
| Method | Endpoint | Purpose | Role |
|--------|----------|---------|------|
| GET | /products/ | List verified products | Public |
| GET | /products/<id>/ | Product detail | Public |
| POST | /products/ | Create product | ARTISAN |
| PATCH | /products/<id>/ | Update product | ARTISAN (owner) |
| GET | /products/my_products/ | Your products | ARTISAN |
| GET | /products/pending/ | Reviews needed | CONSULTANT |
| PATCH | /products/<id>/verify/ | Verify product | CONSULTANT |

### Artisans
| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | /artisans/ | List artisans | Public |
| GET | /artisans/<id>/ | Artisan profile | Public |

### Stories
| Method | Endpoint | Purpose | Role |
|--------|----------|---------|------|
| GET | /stories/ | All stories | Public |
| GET | /stories/<id>/ | Story detail | Public |
| POST | /stories/ | Create story | ARTISAN |
| PATCH | /stories/<id>/ | Update story | ARTISAN (owner) |
| GET | /stories/my_stories/ | Your stories | ARTISAN |

### Consultant
| Method | Endpoint | Purpose | Role |
|--------|----------|---------|------|
| GET | /consultant/pending/ | Reviews needed | CONSULTANT |
| PATCH | /consultant/verify/<id>/ | Verify product | CONSULTANT |

## Common Request Examples

### Register User
```javascript
fetch('http://localhost:8000/api/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password',
    password_confirm: 'secure_password',
    first_name: 'John',
    last_name: 'Doe',
    role: 'ARTISAN'  // ADMIN, ARTISAN, BUYER, CONSULTANT
  })
})
```

### Login & Store Token
```javascript
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password'
  })
});
const data = await response.json();
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
```

### Use Token in API Call
```javascript
const response = await fetch('http://localhost:8000/api/auth/me/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

### Create Product (Form Data)
```javascript
const formData = new FormData();
formData.append('name', 'Product Name');
formData.append('description', 'Description...');
formData.append('price', '100.00');
formData.append('image', fileInput.files[0]);
formData.append('region', 'Karnataka');
formData.append('cultural_story', 'Story...');
formData.append('craft_process', 'Process...');

fetch('http://localhost:8000/api/products/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
```

## Response Format

### Success (200, 201)
```json
{
  "id": 1,
  "field": "value",
  ...
}
```

### Error (400)
```json
{
  "field_name": ["Error message"]
}
```

### Unauthorized (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Forbidden (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## User Roles

- **ADMIN**: Full access
- **ARTISAN**: Create/manage products & stories
- **BUYER**: Purchase products (future)
- **CONSULTANT**: Verify product authenticity

## Token Expiry

- **Access Token**: 1 hour
- **Refresh Token**: 30 days

Refresh token to get new access token:
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

## Important Notes

1. **Product Visibility**:
   - Public: Only verified products
   - Artisans: Own + verified products
   - Consultants: All products

2. **Ownership Rules**:
   - Can only edit own products/stories
   - Ownership verified via request.user

3. **Verification Status**:
   - PENDING: Awaiting consultant review
   - VERIFIED: Approved
   - REJECTED: Not approved

4. **CORS**:
   - Enabled for localhost:5173 (Vite default)
   - Credentials enabled for cookies

## File Locations

- Serializers: `/api/serializers.py`
- Views: `/api/views.py`
- Permissions: `/api/permissions.py`
- URLs: `/api/urls.py`
- Full Docs: `/API_DOCUMENTATION.md`
- Summary: `/IMPLEMENTATION_SUMMARY.md`

## Debugging

Enable JWT debugging in development:
```python
# In settings.py
DEBUG = True
SIMPLE_JWT = {
    # ... existing config
    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,  # For HS256
}
```

## TODO for Production

- [ ] Add rate limiting (django-ratelimit)
- [ ] Add API versioning
- [ ] Add Swagger/OpenAPI documentation
- [ ] Add filtering & search
- [ ] Generate Secret Key (currently uses DEBUG key)
- [ ] Update CORS origins
- [ ] Add HTTPS
- [ ] Add CSRF token handling
- [ ] Monitor token rotation
