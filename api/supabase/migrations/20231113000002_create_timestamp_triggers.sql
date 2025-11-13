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
