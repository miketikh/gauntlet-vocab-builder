# JWT Authentication Testing Guide

This guide shows how to test the FastAPI JWT authentication endpoints.

## Prerequisites

1. FastAPI server running: `uvicorn main:app --reload --port 8000`
2. Next.js frontend running with Supabase auth (to get JWT tokens)

## Testing Workflow

### Step 1: Start the API Server

```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Step 2: Get a JWT Token from Frontend

The easiest way to get a JWT token is from your Next.js frontend:

1. Log in to the Next.js app (http://localhost:3000)
2. Open browser DevTools → Console
3. Run this JavaScript to get your token:

```javascript
// Get the Supabase session
const { data: { session } } = await window.supabase.auth.getSession();
console.log("JWT Token:", session.access_token);
```

Or check the Application/Storage tab for the `sb-<project-id>-auth-token` cookie.

### Step 3: Test Protected Endpoints

Once you have a JWT token, test the endpoints:

#### Test 1: Get Current Educator (`/api/auth/me`)

```bash
# Replace YOUR_JWT_TOKEN with actual token from Step 2
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "email": "educator@example.com",
  "name": "John Doe",
  "school": "Example School",
  "created_at": "2024-11-13T12:00:00"
}
```

**On First Login:** This will create a new educator record in the database.

#### Test 2: Verify Token (`/api/auth/verify`)

```bash
curl -X GET "http://localhost:8000/api/auth/verify" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "valid": true,
  "user_id": "uuid-here",
  "email": "educator@example.com"
}
```

#### Test 3: Logout (`/api/auth/logout`)

```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "message": "Logged out successfully",
  "user_id": "uuid-here"
}
```

### Step 4: Test Error Cases

#### Missing Token (401 Unauthorized)

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Content-Type: application/json"
```

**Expected Response (401):**
```json
{
  "detail": "Not authenticated"
}
```

#### Invalid Token (401 Unauthorized)

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer invalid.token.here" \
  -H "Content-Type: application/json"
```

**Expected Response (401):**
```json
{
  "detail": "Invalid token: ..."
}
```

#### Expired Token (401 Unauthorized)

Use an old token from a previous session:

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer EXPIRED_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (401):**
```json
{
  "detail": "Invalid token: Signature has expired"
}
```

## Testing from Frontend (Next.js)

### Example: Call Protected Endpoint from React

```typescript
// In your Next.js component or API route
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';

async function getEducatorInfo() {
  const supabase = createClientComponentClient();

  // Get the session to get the JWT token
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    console.error('Not authenticated');
    return;
  }

  // Call FastAPI protected endpoint
  const response = await fetch('http://localhost:8000/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    console.error('Failed to fetch educator info');
    return;
  }

  const educator = await response.json();
  console.log('Educator:', educator);
  return educator;
}
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

You can test the endpoints directly from the Swagger UI by:
1. Click the "Authorize" button
2. Enter: `Bearer YOUR_JWT_TOKEN`
3. Click "Authorize"
4. Test any protected endpoint

## Troubleshooting

### CORS Errors
If you get CORS errors from the frontend, verify:
- The frontend URL is in `allow_origins` in `main.py`
- `allow_credentials=True` is set
- The request includes credentials

### 401 Unauthorized
- Verify the token is valid (not expired)
- Check the token format: `Bearer <token>`
- Ensure Supabase URL is correctly set in `.env`
- Check that JWKS endpoint is accessible: `https://afpskpdxuubdsxxxuxar.supabase.co/auth/v1/.well-known/jwks.json`

### 503 Service Unavailable
- Check internet connection (JWKS fetch requires external request)
- Verify Supabase project is online
- Check SUPABASE_URL in `.env` is correct

## Security Notes

1. **Never commit JWT tokens to git**
2. **Tokens expire after 1 hour by default** (Supabase setting)
3. **Always use HTTPS in production**
4. **JWKS keys are cached for 1 hour** to reduce external requests
5. **Service role key is for server-side operations only** - never expose to frontend

## Next Steps

After verifying authentication works:
1. Add authorization middleware to check educator owns resources
2. Protect student and document endpoints
3. Add rate limiting for auth endpoints
4. Implement refresh token handling
