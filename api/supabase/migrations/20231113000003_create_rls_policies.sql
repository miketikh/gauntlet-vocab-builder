-- Migration: Create Row-Level Security (RLS) policies
-- Created: 2023-11-13
-- Description: Implements RLS policies to ensure educators can only access their own data

-- Enable RLS on all tables
ALTER TABLE educators ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE grade_words ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- EDUCATORS TABLE POLICIES
-- ============================================================================

-- Policy: Educators can view their own profile
CREATE POLICY "Educators can view own profile" ON educators
    FOR SELECT
    USING (auth.uid()::text = id::text);

-- Policy: Educators can update their own profile
CREATE POLICY "Educators can update own profile" ON educators
    FOR UPDATE
    USING (auth.uid()::text = id::text)
    WITH CHECK (auth.uid()::text = id::text);

-- Policy: Anyone can insert their profile during signup (will be their own user ID)
CREATE POLICY "Users can insert own profile" ON educators
    FOR INSERT
    WITH CHECK (auth.uid()::text = id::text);

-- ============================================================================
-- STUDENTS TABLE POLICIES
-- ============================================================================

-- Policy: Educators can view their own students
CREATE POLICY "Educators can view own students" ON students
    FOR SELECT
    USING (auth.uid()::text = educator_id::text);

-- Policy: Educators can insert students for themselves
CREATE POLICY "Educators can insert own students" ON students
    FOR INSERT
    WITH CHECK (auth.uid()::text = educator_id::text);

-- Policy: Educators can update their own students
CREATE POLICY "Educators can update own students" ON students
    FOR UPDATE
    USING (auth.uid()::text = educator_id::text)
    WITH CHECK (auth.uid()::text = educator_id::text);

-- Policy: Educators can delete their own students
CREATE POLICY "Educators can delete own students" ON students
    FOR DELETE
    USING (auth.uid()::text = educator_id::text);

-- ============================================================================
-- DOCUMENTS TABLE POLICIES
-- ============================================================================

-- Policy: Educators can view documents for their students
CREATE POLICY "Educators can view documents for own students" ON documents
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM students
            WHERE students.id = documents.student_id
            AND students.educator_id::text = auth.uid()::text
        )
    );

-- Policy: Educators can insert documents for their students
CREATE POLICY "Educators can insert documents for own students" ON documents
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM students
            WHERE students.id = documents.student_id
            AND students.educator_id::text = auth.uid()::text
        )
    );

-- Policy: Educators can update documents for their students
CREATE POLICY "Educators can update documents for own students" ON documents
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM students
            WHERE students.id = documents.student_id
            AND students.educator_id::text = auth.uid()::text
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM students
            WHERE students.id = documents.student_id
            AND students.educator_id::text = auth.uid()::text
        )
    );

-- Policy: Educators can delete documents for their students
CREATE POLICY "Educators can delete documents for own students" ON documents
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM students
            WHERE students.id = documents.student_id
            AND students.educator_id::text = auth.uid()::text
        )
    );

-- ============================================================================
-- GRADE_WORDS TABLE POLICIES
-- ============================================================================

-- Policy: All authenticated users can read grade_words (reference data)
CREATE POLICY "Authenticated users can read grade words" ON grade_words
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Policy: Only service role can insert/update/delete grade_words
-- (This is handled by service role key, no explicit policy needed for regular users)

-- Add comments for documentation
COMMENT ON POLICY "Educators can view own profile" ON educators IS
    'Allows educators to view only their own profile data';
COMMENT ON POLICY "Educators can view own students" ON students IS
    'Ensures educators can only see students they have created';
COMMENT ON POLICY "Educators can view documents for own students" ON documents IS
    'Restricts document access to only those belonging to the educator''s students';
COMMENT ON POLICY "Authenticated users can read grade words" ON grade_words IS
    'Grade-level vocabulary is reference data accessible to all authenticated users';
