# Kalasetu API Documentation

## Overview
The Kalasetu REST API provides endpoints for user authentication, product management, artisan profiles, stories, and consultant verification workflows. Built with Django REST Framework and JWT authentication.

## Base URL
```
http://localhost:8000/api/
```

## Authentication

### 1. Register a New User
**POST** `/api/auth/register/`

Request:
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "password_confirm": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "role": "ARTISAN",
  "phone_number": "+1234567890",
  "region": "South India"
}
```

Response (201):
```json
{
  "email": "user@example.com",
  "role": "ARTISAN",
  "message": "User registered successfully. Please login."
}
```

Available roles: `ADMIN`, `ARTISAN`, `BUYER`, `CONSULTANT`

---

### 2. Login (Obtain JWT Token)
**POST** `/api/auth/login/`

Request:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response (200):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "ARTISAN",
  "email": "user@example.com"
}
```

**Note**: Use the `access` token in subsequent requests via the Authorization header:
```
Authorization: Bearer <access_token>
```

---

### 3. Refresh JWT Token
**POST** `/api/auth/refresh/`

Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response (200):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Get Current User Profile
**GET** `/api/auth/me/`

Headers:
```
Authorization: Bearer <access_token>
```

Response (200):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "ARTISAN",
  "phone_number": "+1234567890",
  "bio": "I am a traditional craftsman...",
  "region": "South India",
  "experience_years": 5,
  "profile_image": "http://localhost:8000/media/artisan_profiles/image.jpg"
}
```

---

### 5. Update Current User Profile
**PUT** `/api/auth/me/`

Headers:
```
Authorization: Bearer <access_token>
```

Request (partial update allowed):
```json
{
  "bio": "Updated bio",
  "experience_years": 10
}
```

Response (200): Updated user object

---

## Products

### 1. List All Products (Public)
**GET** `/api/products/`

Query Parameters:
- `page` (optional): Page number for pagination (default: 1)

Response (200):
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Traditional Silk Saree",
      "price": "250.00",
      "image": "http://localhost:8000/media/product_images/saree.jpg",
      "region": "Tamil Nadu",
      "artisan": {
        "id": 5,
        "email": "artisan@example.com",
        "first_name": "Ram",
        "last_name": "Kumar",
        "role": "ARTISAN",
        "bio": "Master weaver...",
        "region": "Tamil Nadu",
        "experience_years": 15
      },
      "verification_status": "VERIFIED",
      "is_verified": true,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

**Note**: Public users see only verified products. Authenticated users see their own products + verified products (if ARTISAN).

---

### 2. Get Product Details
**GET** `/api/products/<id>/`

Response (200):
```json
{
  "id": 1,
  "name": "Traditional Silk Saree",
  "description": "Handwoven premium silk saree...",
  "price": "250.00",
  "image": "http://localhost:8000/media/product_images/saree.jpg",
  "region": "Tamil Nadu",
  "cultural_story": "This saree represents the rich heritage...",
  "craft_process": "The weaving process takes 15 days...",
  "artisan": { ... },
  "is_approved": true,
  "verification_status": "VERIFIED",
  "is_verified": true,
  "verified_by": { ... },
  "verification_note": "Excellent cultural significance",
  "impact_score": 85,
  "created_at": "2026-01-15T10:30:00Z"
}
```

---

### 3. Create a New Product (Artisans Only)
**POST** `/api/products/`

Headers:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

Request:
```json
{
  "name": "Traditional Silk Saree",
  "description": "Handwoven premium silk saree",
  "price": "250.00",
  "image": <file>,
  "region": "Tamil Nadu",
  "cultural_story": "Rich heritage of Tamil Nadu weaving...",
  "craft_process": "Step-by-step process..."
}
```

Response (201): Product object

**Permissions**: ARTISAN role required

---

### 4. Update a Product (Owner Only)
**PUT/PATCH** `/api/products/<id>/`

Headers:
```
Authorization: Bearer <access_token>
```

Request (example):
```json
{
  "price": "275.00",
  "description": "Updated description"
}
```

Response (200): Updated product object

**Permissions**: Product owner (artisan) only

---

### 5. Get User's Products
**GET** `/api/products/my_products/`

Headers:
```
Authorization: Bearer <access_token>
```

Response (200): List of artisan's products

**Permissions**: ARTISAN role required

---

### 6. Get Pending Products (Consultant)
**GET** `/api/products/pending/`

Headers:
```
Authorization: Bearer <access_token>
```

Response (200): List of pending verification products

**Permissions**: CONSULTANT or ADMIN role required

---

### 7. Verify/Reject Product (Consultant)
**PATCH** `/api/products/<id>/verify/`

Headers:
```
Authorization: Bearer <access_token>
```

Request:
```json
{
  "verification_status": "VERIFIED",
  "verification_note": "Outstanding craftsmanship and cultural significance",
  "impact_score": 90
}
```

Response (200): Updated product object

**Permissions**: CONSULTANT or ADMIN role required
**Note**: verification_status must be either "VERIFIED" or "REJECTED"

---

## Artisans

### 1. List All Artisans
**GET** `/api/artisans/`

Response (200):
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "email": "artisan@example.com",
      "first_name": "Ram",
      "last_name": "Kumar",
      "role": "ARTISAN",
      "bio": "Master weaver with 15 years experience",
      "region": "Tamil Nadu",
      "experience_years": 15,
      "profile_image": "http://localhost:8000/media/artisan_profiles/ram.jpg"
    }
  ]
}
```

**Permissions**: Public access

---

### 2. Get Artisan Profile
**GET** `/api/artisans/<id>/`

Response (200): Full artisan profile with all fields

**Permissions**: Public access

---

## Artisan Stories

### 1. List All Stories
**GET** `/api/stories/`

Response (200):
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "artisan": {
        "id": 5,
        "email": "artisan@example.com",
        "first_name": "Ram",
        ...
      },
      "title": "My Journey as a Weaver",
      "content": "It all started when my grandfather taught me...",
      "image": "http://localhost:8000/media/artisan_stories/story1.jpg",
      "created_at": "2026-01-10T08:45:00Z"
    }
  ]
}
```

**Permissions**: Public access

---

### 2. Get Story Details
**GET** `/api/stories/<id>/`

Response (200): Full story object

**Permissions**: Public access

---

### 3. Create a Story (Artisans Only)
**POST** `/api/stories/`

Headers:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

Request:
```json
{
  "title": "My Journey as a Weaver",
  "content": "Detailed story content...",
  "image": <file>
}
```

Response (201): Story object

**Permissions**: ARTISAN role required

---

### 4. Update a Story (Owner Only)
**PUT/PATCH** `/api/stories/<id>/`

Headers:
```
Authorization: Bearer <access_token>
```

Response (200): Updated story object

**Permissions**: Story owner (artisan) only

---

### 5. Get Your Stories
**GET** `/api/stories/my_stories/`

Headers:
```
Authorization: Bearer <access_token>
```

Response (200): List of your stories

**Permissions**: ARTISAN role required

---

## Consultant Operations

### 1. Get Pending Products for Review
**GET** `/api/consultant/pending/`

Headers:
```
Authorization: Bearer <access_token>
```

Response (200): List of pending products

**Permissions**: CONSULTANT or ADMIN role required

---

### 2. Verify Product (Consultant)
**PATCH** `/api/consultant/verify/<id>/`

Headers:
```
Authorization: Bearer <access_token>
```

Request:
```json
{
  "verification_status": "VERIFIED",
  "verification_note": "Excellent work!",
  "impact_score": 85
}
```

Response (200): Updated product object

**Permissions**: CONSULTANT or ADMIN role required

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"],
  "another_field": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Server Error
```json
{
  "detail": "Internal server error."
}
```

---

## Token Expiration & Refresh

Access tokens expire after **1 hour**. Use the refresh token to obtain a new access token without re-authenticating.

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

Refresh tokens are valid for **30 days**.

---

## Rate Limiting

Currently no rate limiting is implemented. This should be added for production.

---

## Testing with cURL

### Register:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "ARTISAN"
  }'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Get Products:
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Role-Based Access Control

| Endpoint | Anonymous | Buyer | Artisan | Consultant | Admin |
|----------|-----------|-------|---------|------------|-------|
| GET /products | ✓ (verified only) | ✓ (verified only) | ✓ (own + verified) | ✓ (all) | ✓ (all) |
| POST /products | ✗ | ✗ | ✓ | ✗ | ✓ |
| GET /artisans | ✓ | ✓ | ✓ | ✓ | ✓ |
| POST /stories | ✗ | ✗ | ✓ | ✗ | ✓ |
| GET /stories | ✓ | ✓ | ✓ | ✓ | ✓ |
| PATCH /products/<id>/verify | ✗ | ✗ | ✗ | ✓ | ✓ |
| GET /consultant/pending | ✗ | ✗ | ✗ | ✓ | ✓ |

---

## Frontend Integration (React + Vite)

### Example: Register User
```javascript
const response = await fetch('http://localhost:8000/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password',
    password_confirm: 'secure_password',
    first_name: 'John',
    last_name: 'Doe',
    role: 'ARTISAN',
  }),
});
const data = await response.json();
```

### Example: Login
```javascript
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password',
  }),
});
const data = await response.json();
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
```

### Example: Protected Request
```javascript
const response = await fetch('http://localhost:8000/api/auth/me/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  },
});
const userData = await response.json();
```

---

## Future Enhancements

1. Add rate limiting (django-ratelimit)
2. Add API versioning
3. Add filtering and search capabilities
4. Add order/payment API endpoints (when Order model is populated)
5. Add review/rating API endpoints (when Review model is populated)
6. Add pagination defaults
7. Add API documentation (Swagger/OpenAPI)

---

**API Version**: 1.0
**Last Updated**: March 3, 2026
