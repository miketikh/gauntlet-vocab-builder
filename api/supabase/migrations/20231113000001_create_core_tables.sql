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
