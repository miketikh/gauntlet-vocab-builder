-- 20231113000001_create_core_tables.sql
-- Migration: Create core tables for vocab-builder
-- Created: 2023-11-13
-- Description: Creates educators, students, documents, and grade_words tables with proper relationships

-- Create educators table
CREATE TABLE IF NOT EXISTS educators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    school TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create index on educator email for faster lookups
CREATE INDEX IF NOT EXISTS idx_educators_email ON educators(email);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    educator_id UUID NOT NULL REFERENCES educators(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    grade_level INTEGER NOT NULL CHECK (grade_level >= 6 AND grade_level <= 12),
    reading_level TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for students table
CREATE INDEX IF NOT EXISTS idx_students_educator_id ON students(educator_id);
CREATE INDEX IF NOT EXISTS idx_students_grade_level ON students(grade_level);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    file_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for documents table
CREATE INDEX IF NOT EXISTS idx_documents_student_id ON documents(student_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date DESC);

-- Create grade_words table
CREATE TABLE IF NOT EXISTS grade_words (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grade_level INTEGER NOT NULL CHECK (grade_level >= 6 AND grade_level <= 12),
    word TEXT NOT NULL,
    definition TEXT NOT NULL,
    example TEXT,
    frequency_rank INTEGER,
    subject TEXT DEFAULT 'ELA',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for grade_words table
CREATE INDEX IF NOT EXISTS idx_grade_words_grade_level ON grade_words(grade_level);
CREATE INDEX IF NOT EXISTS idx_grade_words_word ON grade_words(word);
CREATE INDEX IF NOT EXISTS idx_grade_words_frequency_rank ON grade_words(frequency_rank);

-- Add unique constraint to prevent duplicate words per grade level
CREATE UNIQUE INDEX IF NOT EXISTS idx_grade_words_unique ON grade_words(grade_level, word, subject);

-- Add comments for documentation
COMMENT ON TABLE educators IS 'Stores educator account information';
COMMENT ON TABLE students IS 'Stores student profiles managed by educators';
COMMENT ON TABLE documents IS 'Stores metadata for uploaded student documents (actual files in S3)';
COMMENT ON TABLE grade_words IS 'Reference table for grade-level appropriate vocabulary words';

COMMENT ON COLUMN documents.s3_key IS 'S3 object key for retrieving the document file';
COMMENT ON COLUMN documents.status IS 'Processing status: pending, processing, completed, failed';
COMMENT ON COLUMN grade_words.frequency_rank IS 'Word frequency ranking (lower = more common)';


-- 20231113000002_create_timestamp_triggers.sql
-- Migration: Create automatic timestamp triggers
-- Created: 2023-11-13
-- Description: Creates function and triggers to automatically update updated_at timestamps

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for educators table
DROP TRIGGER IF EXISTS update_educators_updated_at ON educators;
CREATE TRIGGER update_educators_updated_at
    BEFORE UPDATE ON educators
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for students table
DROP TRIGGER IF EXISTS update_students_updated_at ON students;
CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for documents table
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for grade_words table
DROP TRIGGER IF EXISTS update_grade_words_updated_at ON grade_words;
CREATE TRIGGER update_grade_words_updated_at
    BEFORE UPDATE ON grade_words
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comment for documentation
COMMENT ON FUNCTION update_updated_at_column() IS 'Automatically updates the updated_at timestamp on row updates';


-- 20231113000003_create_rls_policies.sql
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
