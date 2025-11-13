# AWS S3 Integration Guide

This document describes the S3 integration for secure document storage in the Vocab Builder application.

## Overview

The application uses **AWS S3** for storing student documents (essays, transcripts, etc.) with **presigned URLs** for secure, direct browser-to-S3 uploads and downloads. This approach is more efficient and scalable than routing file uploads through the API server.

## Architecture

```
┌─────────────┐      1. Request presigned URL     ┌──────────────┐
│             │ ─────────────────────────────────> │              │
│   Browser   │                                    │  FastAPI     │
│  (Frontend) │ <───────────────────────────────── │   Backend    │
│             │    2. Return presigned URL + key   │              │
└─────────────┘                                    └──────────────┘
       │                                                    │
       │                                                    │
       │ 3. Upload file directly                           │
       │    via PUT request                                │
       │                                                    │
       ▼                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                         AWS S3                              │
│                                                             │
│  Bucket: mtikh-vocab-builder-documents-dev                 │
│  Region: us-east-2                                         │
│  Encryption: SSE-S3 (Server-Side Encryption)               │
│  Public Access: BLOCKED                                    │
└─────────────────────────────────────────────────────────────┘
```

## How Presigned URLs Work

### Upload Flow

1. **Frontend requests upload URL**
   ```typescript
   POST /api/s3/upload-url
   {
     "student_id": 5,
     "filename": "essay.pdf",
     "content_type": "application/pdf"
   }
   ```

2. **Backend generates presigned URL**
   - Verifies educator owns the student (authentication + authorization)
   - Generates unique S3 key: `educators/{educator_id}/students/{student_id}/documents/{uuid}-{filename}`
   - Creates presigned URL valid for 1 hour
   - Returns URL and S3 key

3. **Frontend uploads directly to S3**
   ```typescript
   PUT {presigned_url}
   Headers:
     Content-Type: application/pdf
   Body: [file binary data]
   ```

4. **Frontend creates document record**
   ```typescript
   POST /api/documents
   {
     "student_id": 5,
     "title": "Essay #1",
     "s3_key": "educators/1/students/5/documents/uuid-essay.pdf",
     "file_type": "pdf"
   }
   ```

### Download Flow

1. **Frontend requests download URL**
   ```typescript
   POST /api/s3/download-url
   {
     "s3_key": "educators/1/students/5/documents/uuid-essay.pdf"
   }
   ```

2. **Backend generates presigned URL**
   - Verifies educator owns the document (parses S3 key for ownership)
   - Creates presigned URL valid for 1 hour
   - Returns URL

3. **Frontend downloads directly from S3**
   ```typescript
   GET {presigned_url}
   ```

## S3 Key Naming Convention

Documents are organized hierarchically for security and efficient management:

```
educators/{educator_id}/students/{student_id}/documents/{uuid}-{filename}
```

**Example:**
```
educators/1/students/5/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890-essay.pdf
```

**Benefits:**
- **Organization:** All files for a student are grouped together
- **Uniqueness:** UUID prevents filename collisions
- **Security:** Easy to implement access control (educator only sees their files)
- **Cleanup:** Can delete all documents for a student using prefix
- **Lifecycle:** Can apply S3 lifecycle policies per educator/student

## Environment Configuration

### Required Environment Variables

Add these to `/api/.env`:

```bash
# AWS S3 Configuration
AWS_S3_BUCKET=mtikh-vocab-builder-documents-dev
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### Environment Variables by Environment

**Development:**
```
AWS_S3_BUCKET=mtikh-vocab-builder-documents-dev
AWS_REGION=us-east-2
```

**Production:**
```
AWS_S3_BUCKET=mtikh-vocab-builder-documents-prod
AWS_REGION=us-east-2
```

## Security Considerations

### 1. No Public Access

The S3 bucket has **"Block all public access"** enabled. Files cannot be accessed without a presigned URL.

### 2. Server-Side Encryption

All objects are encrypted at rest using **SSE-S3** (AES-256 encryption).

### 3. Presigned URL Expiration

Presigned URLs expire after **1 hour** (3600 seconds). This limits the time window for unauthorized access if a URL is leaked.

### 4. Authorization Checks

Before generating a presigned URL, the API:
- Verifies the user is authenticated (valid JWT)
- Verifies the educator owns the student (database query)
- Denies access if ownership check fails (403 Forbidden)

### 5. IAM Least Privilege

The IAM user/role used by FastAPI has only these permissions:
- `s3:PutObject` - Upload files
- `s3:GetObject` - Download files
- `s3:DeleteObject` - Delete files
- `s3:ListBucket` - List files (optional)

**No permissions for:**
- Bucket deletion
- Bucket policy changes
- Public ACL changes

### 6. Content-Type Validation

The API requires specifying `content_type` when generating upload URLs. This prevents:
- Uploading executable files disguised as PDFs
- XSS attacks via uploaded HTML files

**Supported MIME types:**
- `application/pdf` - PDF files
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document` - DOCX files
- `text/plain` - Plain text files

## API Endpoints

### POST /api/s3/upload-url

Generate a presigned URL for uploading a document.

**Request:**
```json
{
  "student_id": 5,
  "filename": "essay.pdf",
  "content_type": "application/pdf"
}
```

**Response:**
```json
{
  "presigned_url": "https://mtikh-vocab-builder-documents-dev.s3.us-east-2.amazonaws.com/educators/1/students/5/documents/a1b2c3d4-essay.pdf?X-Amz-Algorithm=...",
  "s3_key": "educators/1/students/5/documents/a1b2c3d4-essay.pdf",
  "expires_in": 3600
}
```

**Authentication:** Required (JWT token in `Authorization: Bearer <token>` header)

**Authorization:** Educator must own the student

**Error Responses:**
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Educator doesn't own the student
- `404 Not Found` - Student not found
- `500 Internal Server Error` - S3 bucket not configured or doesn't exist

### POST /api/s3/download-url

Generate a presigned URL for downloading a document.

**Request:**
```json
{
  "s3_key": "educators/1/students/5/documents/a1b2c3d4-essay.pdf"
}
```

**Response:**
```json
{
  "presigned_url": "https://mtikh-vocab-builder-documents-dev.s3.us-east-2.amazonaws.com/educators/1/students/5/documents/a1b2c3d4-essay.pdf?X-Amz-Algorithm=...",
  "expires_in": 3600
}
```

**Authentication:** Required

**Authorization:** Educator must own the document (verified by parsing S3 key)

**Error Responses:**
- `400 Bad Request` - Invalid S3 key format
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Educator doesn't own the document
- `404 Not Found` - File not found in S3
- `500 Internal Server Error` - S3 error

### GET /api/s3/health

Check S3 service health.

**Response:**
```json
{
  "status": "healthy",
  "service": "s3",
  "bucket_accessible": true
}
```

**Authentication:** Not required

## Testing Instructions

### 1. Test Presigned URL Generation

```bash
# Set environment variables
export SUPABASE_URL="..."
export SUPABASE_SERVICE_ROLE_KEY="..."
export DATABASE_URL="..."
export AWS_S3_BUCKET="mtikh-vocab-builder-documents-dev"
export AWS_REGION="us-east-2"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Start the API
cd api
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Test with curl

**Get a JWT token first:**
```bash
# Login via frontend or use existing token
JWT_TOKEN="your_jwt_token_here"
```

**Generate upload URL:**
```bash
curl -X POST http://localhost:8000/api/s3/upload-url \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "filename": "test.txt",
    "content_type": "text/plain"
  }'
```

**Upload a file to S3:**
```bash
# Use the presigned_url from the previous response
curl -X PUT "$PRESIGNED_URL" \
  -H "Content-Type: text/plain" \
  --data-binary "@test.txt"
```

**Generate download URL:**
```bash
# Use the s3_key from the upload response
curl -X POST http://localhost:8000/api/s3/download-url \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_key": "educators/1/students/1/documents/uuid-test.txt"
  }'
```

**Download the file:**
```bash
curl "$PRESIGNED_DOWNLOAD_URL" -o downloaded.txt
```

### 3. Test Health Check

```bash
curl http://localhost:8000/api/s3/health
```

### 4. Test Error Handling

**Invalid student (not owned by educator):**
```bash
curl -X POST http://localhost:8000/api/s3/upload-url \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 999,
    "filename": "test.txt",
    "content_type": "text/plain"
  }'
# Should return 404 Not Found
```

**Missing authentication:**
```bash
curl -X POST http://localhost:8000/api/s3/upload-url \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "filename": "test.txt",
    "content_type": "text/plain"
  }'
# Should return 401 Unauthorized
```

## S3 Bucket Setup (Manual)

If the S3 bucket doesn't exist yet, follow these steps:

### 1. Create Bucket

```bash
aws s3api create-bucket \
  --bucket mtikh-vocab-builder-documents-dev \
  --region us-east-2 \
  --create-bucket-configuration LocationConstraint=us-east-2
```

### 2. Block Public Access

```bash
aws s3api put-public-access-block \
  --bucket mtikh-vocab-builder-documents-dev \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 3. Enable Encryption

```bash
aws s3api put-bucket-encryption \
  --bucket mtikh-vocab-builder-documents-dev \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

### 4. Create IAM User

```bash
aws iam create-user --user-name vocab-builder-s3-user
```

### 5. Attach Policy

Create policy file `s3-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::mtikh-vocab-builder-documents-dev",
        "arn:aws:s3:::mtikh-vocab-builder-documents-dev/*"
      ]
    }
  ]
}
```

Apply policy:
```bash
aws iam put-user-policy \
  --user-name vocab-builder-s3-user \
  --policy-name S3DocumentAccess \
  --policy-document file://s3-policy.json
```

### 6. Create Access Keys

```bash
aws iam create-access-key --user-name vocab-builder-s3-user
```

Save the `AccessKeyId` and `SecretAccessKey` to `.env`.

## Common Issues & Troubleshooting

### Issue: "S3 bucket does not exist"

**Cause:** Bucket name in `.env` doesn't match actual bucket name, or bucket hasn't been created.

**Solution:**
1. Check bucket name: `aws s3 ls | grep vocab-builder`
2. Create bucket if missing (see Bucket Setup above)
3. Update `AWS_S3_BUCKET` in `.env`

### Issue: "Access denied to S3 bucket"

**Cause:** IAM user doesn't have permissions, or wrong access key.

**Solution:**
1. Verify IAM policy is attached: `aws iam list-user-policies --user-name vocab-builder-s3-user`
2. Check access key is correct in `.env`
3. Test manually: `aws s3 ls s3://mtikh-vocab-builder-documents-dev --profile your-profile`

### Issue: "No credentials found"

**Cause:** `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` not set in `.env`.

**Solution:**
1. Check `.env` file has both variables
2. Restart FastAPI server to reload environment variables
3. Verify with: `echo $AWS_ACCESS_KEY_ID` (should not be empty)

### Issue: "Presigned URL expired"

**Cause:** Presigned URLs expire after 1 hour.

**Solution:**
- Generate a new presigned URL
- For long-running uploads, consider increasing `expires_in` parameter (max 7 days)

### Issue: "Upload fails with 403 Forbidden"

**Cause:** Content-Type mismatch between presigned URL generation and actual upload.

**Solution:**
- Ensure Content-Type header in PUT request matches the `content_type` used when generating the presigned URL
- Example: If you generate URL with `application/pdf`, you must upload with `Content-Type: application/pdf`

## Performance Considerations

### Benefits of Presigned URLs

1. **Reduced API Server Load**
   - Files don't pass through FastAPI server
   - API only handles metadata and authentication
   - Can handle many concurrent uploads

2. **Lower Latency**
   - Direct browser-to-S3 connection
   - No intermediate proxy
   - Faster for large files

3. **Cost Efficiency**
   - No API server bandwidth costs for file transfers
   - S3 bandwidth costs are lower than EC2/Lambda

### File Size Limits

- **Maximum file size:** 5 GB (S3 single PUT limit)
- **For files > 5 GB:** Use multipart upload (not implemented in MVP)

### Expiration Times

- **Upload URLs:** 1 hour (3600 seconds)
- **Download URLs:** 1 hour (3600 seconds)

**Rationale:** Short expiration reduces security risk. URLs can be regenerated if needed.

## Future Enhancements

### 1. Multipart Upload Support

For files larger than 5 GB, implement multipart upload:
- Frontend splits file into chunks
- API generates presigned URL for each chunk
- Frontend uploads chunks in parallel
- API completes multipart upload

### 2. Virus Scanning

Integrate AWS Lambda to scan uploaded files:
- S3 triggers Lambda on object creation
- Lambda runs ClamAV or similar
- Quarantine infected files
- Update document status in database

### 3. S3 Lifecycle Policies

Automatically manage old documents:
- Move to Glacier after 1 year (for archival)
- Delete after 3 years (compliance with data retention policies)

### 4. CloudFront CDN

For frequently accessed documents:
- Add CloudFront distribution in front of S3
- Faster downloads for students worldwide
- Reduced S3 GET request costs

### 5. Direct Upload from Mobile

For React Native mobile app:
- Use same presigned URL approach
- Works with `fetch()` API or `react-native-fs`

## References

- [AWS S3 Presigned URLs Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
