# Epic 2: Student Management & Document Upload

**Expanded Goal:**
Enable educators to create and manage student profiles with pseudonymized identifiers, upload student documents (essays, transcripts) to secure cloud storage with subject metadata, and view their complete document library organized by student. This epic delivers the core data collection workflow, allowing educators to build their student portfolio before analysis features are available.

## Story 2.1: Create Student Profile Form

As an **educator**,
I want **to create new student profiles with basic information**,
so that **I can organize and track vocabulary development for each of my students**.

### Acceptance Criteria:

1. "Add New Student" page (`/students/new`) implemented with form:
   - Display name input (text field, required)
   - Grade level selector (dropdown: 6, 7, 8, required)
   - Form validation (display name not empty, grade level selected)
   - "Create Student" button
   - "Cancel" button (returns to dashboard)
   - Uses shadcn/ui form components

2. Form submission:
   - Creates record in `students` table via Supabase client
   - Associates student with logged-in educator (educator_id)
   - Generates unique UUID for student
   - Sets created_at timestamp

3. Success handling:
   - Redirects to student detail page after creation
   - Shows success toast notification

4. Error handling:
   - Displays error message if creation fails
   - Validation errors shown inline
   - Network errors handled gracefully

5. Testing:
   - Can create student with valid data
   - Cannot submit with empty display name
   - Cannot submit without selecting grade level
   - Student appears in database with correct educator_id
   - RLS prevents creating students for other educators

## Story 2.2: Display Student List on Dashboard

As an **educator**,
I want **to see all my students in a grid/list on the dashboard**,
so that **I can quickly access individual student details and track my roster**.

### Acceptance Criteria:

1. Dashboard (`/dashboard`) updated to fetch and display students:
   - Queries `students` table filtered by educator_id
   - Displays student cards in responsive grid (3-4 columns on desktop, 1-2 on tablet/mobile)
   - Each card shows:
     - Student display name
     - Grade level
     - Placeholder for vocabulary stats (show "No data yet")
     - Document count (initially 0)
     - "View Details" button/link

2. Empty state handling:
   - Shows "No students yet" message if no students
   - "Add New Student" button prominently displayed

3. Card interactions:
   - Click anywhere on card navigates to student detail page
   - Hover effect for visual feedback
   - Uses shadcn/ui Card component

4. Loading state:
   - Shows skeleton loaders while fetching students
   - Handles slow network gracefully

5. Real-time updates (optional enhancement):
   - Dashboard refreshes when returning from student creation
   - Or use Supabase real-time subscriptions

6. Testing:
   - Dashboard shows all students for logged-in educator
   - Dashboard does not show students from other educators (RLS)
   - Empty state displays when no students exist
   - Can navigate to student detail page from card
   - Newly created student appears in list

## Story 2.3: Create Student Detail Page Structure

As an **educator**,
I want **a dedicated page for each student showing their information and document library**,
so that **I can manage all student-specific data in one place**.

### Acceptance Criteria:

1. Student detail page (`/students/[id]`) created with:
   - Dynamic route using student ID
   - Fetches student data from Supabase
   - 404 page if student not found or belongs to different educator

2. Page layout includes sections:
   - **Header:** Student display name, grade level, back button to dashboard
   - **Upload Documents section:** Placeholder for upload form (Epic 2.4)
   - **Documents Library section:** List of uploaded documents (initially empty)
   - **Vocabulary Profile section:** Placeholder showing "Upload documents to see vocabulary analysis"
   - **Recommendations section:** Placeholder showing "Analysis coming soon"

3. Documents Library (empty state):
   - Message: "No documents yet. Upload an essay or transcript to get started."
   - Styled table/list ready for document rows

4. Navigation:
   - Back button returns to dashboard
   - Breadcrumbs: Dashboard > [Student Name]

5. Responsive layout:
   - Desktop: Multi-column layout
   - Mobile: Stacked sections

6. Testing:
   - Can navigate to student detail page from dashboard
   - Page displays correct student information
   - Cannot access other educators' students (RLS + route protection)
   - Shows appropriate empty states

## Story 2.4: Implement Document Upload with S3 Integration

As an **educator**,
I want **to upload student documents (essays, transcripts) with subject classification**,
so that **the system can analyze their vocabulary and generate recommendations**.

### Acceptance Criteria:

1. Upload form added to student detail page with:
   - Document title input (text field, required)
   - Subject selector (dropdown: ELA, Math, Science, Social Studies, required)
   - File picker (accepts .txt, .pdf, .docx)
   - Drag-and-drop zone for file upload
   - "Upload" button
   - File size limit (5MB)
   - Uses shadcn/ui form components

2. Upload workflow (frontend):
   - Validates file type and size
   - Shows upload progress indicator
   - Calls FastAPI endpoint to get pre-signed S3 URL
   - Uploads file directly to S3 using pre-signed URL
   - Calls FastAPI to create document record

3. FastAPI endpoints created:
   - `POST /api/students/{student_id}/documents/upload-url`
     - Generates pre-signed S3 upload URL
     - Returns URL and S3 key
     - Verifies educator owns student (JWT + database check)
   - `POST /api/students/{student_id}/documents`
     - Creates document record in Supabase
     - Stores: student_id, title, subject, content_s3_key, uploaded_at
     - Returns document metadata

4. File storage:
   - Files uploaded to S3 with key format: `{educator_id}/{student_id}/{uuid}.{ext}`
   - S3 server-side encryption enabled
   - Metadata tags: student_id, educator_id, subject

5. Success/error handling:
   - Success: Document appears in library immediately, shows success toast
   - Error: Clear error messages (file too large, unsupported type, network error)
   - Failed uploads don't create orphaned S3 files or database records

6. Testing:
   - Can upload .txt file with valid metadata
   - File appears in S3 bucket with correct key
   - Document record created in database
   - Cannot upload file >5MB
   - Cannot upload unsupported file type
   - Upload progress indicator works
   - Cannot upload document for other educator's students

## Story 2.5: Display Uploaded Documents Library

As an **educator**,
I want **to see a list of all documents I've uploaded for each student**,
so that **I can track what has been analyzed and manage document history**.

### Acceptance Criteria:

1. Documents Library section on student detail page updated to display:
   - Table/list of documents fetched from `documents` table
   - Columns: Title, Subject, Upload Date, Actions
   - Sorted by upload date (newest first)
   - Empty state if no documents

2. Each document row shows:
   - Document title
   - Subject badge/tag (color-coded: ELA=blue, Math=green, Science=purple, Social Studies=orange)
   - Upload date (formatted as "MMM DD, YYYY" or relative like "2 days ago")
   - Download button (generates pre-signed URL)
   - Delete button (optional for MVP)

3. Download functionality:
   - Click download button calls FastAPI endpoint
   - `GET /api/documents/{document_id}/download`
     - Verifies educator owns document
     - Generates pre-signed S3 URL (15-minute expiration)
     - Returns URL or redirects to URL
   - Browser downloads file

4. Document count displayed:
   - Student card on dashboard shows accurate document count
   - Updates when new documents uploaded

5. Responsive design:
   - Desktop: Full table with all columns
   - Mobile: Stacked cards with key info

6. Testing:
   - Uploaded documents appear in library
   - Can download uploaded document
   - Downloaded file matches uploaded file (content verification)
   - Cannot download documents for other educators' students
   - Document count accurate on dashboard

## Story 2.6: Add Document Deletion (Optional Cleanup)

As an **educator**,
I want **to delete uploaded documents that are no longer needed**,
so that **I can manage my document library and remove mistakes or duplicates**.

### Acceptance Criteria:

1. Delete button added to each document in library:
   - Trash icon or "Delete" text button
   - Positioned in Actions column

2. Confirmation dialog:
   - Click delete shows confirmation modal
   - Message: "Are you sure you want to delete '[Document Title]'? This action cannot be undone."
   - "Cancel" and "Confirm Delete" buttons
   - Uses shadcn/ui Dialog component

3. Delete workflow:
   - Calls FastAPI endpoint: `DELETE /api/documents/{document_id}`
   - Verifies educator owns document
   - Deletes document record from database
   - Deletes file from S3
   - Returns success response

4. UI updates:
   - Document removed from library immediately (optimistic update)
   - Success toast notification
   - Document count decrements

5. Error handling:
   - If delete fails, restore document in UI
   - Show error message

6. Cascade considerations:
   - If document has associated vocab_analyses or recommendations, delete those too (cascade delete)
   - Or prevent deletion if analyses exist (business decision)

7. Testing:
   - Can delete document
   - Document removed from database
   - File removed from S3
   - Cannot delete other educators' documents
   - Document count updates correctly
   - Deleting last document shows empty state

---
