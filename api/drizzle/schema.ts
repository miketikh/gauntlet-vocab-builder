/**
 * Drizzle ORM Schema for Vocab Builder
 *
 * This schema defines all database tables with TypeScript types for type-safe database operations.
 * Tables are designed to support the vocabulary recommendation engine for educators and students.
 */

import { pgTable, uuid, text, timestamp, integer, index, uniqueIndex, check } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// ============================================================================
// Educators Table
// ============================================================================

export const educators = pgTable('educators', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  school: text('school'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  emailIdx: index('idx_educators_email').on(table.email),
}));

// ============================================================================
// Students Table
// ============================================================================

export const students = pgTable('students', {
  id: uuid('id').primaryKey().defaultRandom(),
  educatorId: uuid('educator_id').notNull().references(() => educators.id, { onDelete: 'cascade' }),
  name: text('name').notNull(),
  gradeLevel: integer('grade_level').notNull(),
  readingLevel: text('reading_level'),
  notes: text('notes'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  educatorIdx: index('idx_students_educator_id').on(table.educatorId),
  gradeLevelIdx: index('idx_students_grade_level').on(table.gradeLevel),
  gradeLevelCheck: check('grade_level_check', sql`${table.gradeLevel} >= 6 AND ${table.gradeLevel} <= 12`),
}));

// ============================================================================
// Documents Table
// ============================================================================

export const documents = pgTable('documents', {
  id: uuid('id').primaryKey().defaultRandom(),
  studentId: uuid('student_id').notNull().references(() => students.id, { onDelete: 'cascade' }),
  title: text('title').notNull(),
  s3Key: text('s3_key').notNull(),
  uploadDate: timestamp('upload_date', { withTimezone: true }).notNull().defaultNow(),
  fileType: text('file_type').notNull(),
  status: text('status').notNull().default('pending'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  studentIdx: index('idx_documents_student_id').on(table.studentId),
  statusIdx: index('idx_documents_status').on(table.status),
  uploadDateIdx: index('idx_documents_upload_date').on(table.uploadDate),
  statusCheck: check('status_check', sql`${table.status} IN ('pending', 'processing', 'completed', 'failed')`),
}));

// ============================================================================
// Grade Words Table
// ============================================================================

export const gradeWords = pgTable('grade_words', {
  id: uuid('id').primaryKey().defaultRandom(),
  gradeLevel: integer('grade_level').notNull(),
  word: text('word').notNull(),
  definition: text('definition').notNull(),
  example: text('example'),
  frequencyRank: integer('frequency_rank'),
  subject: text('subject').notNull().default('ELA'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  gradeLevelIdx: index('idx_grade_words_grade_level').on(table.gradeLevel),
  wordIdx: index('idx_grade_words_word').on(table.word),
  frequencyRankIdx: index('idx_grade_words_frequency_rank').on(table.frequencyRank),
  uniqueWordPerGrade: uniqueIndex('idx_grade_words_unique').on(table.gradeLevel, table.word, table.subject),
  gradeLevelCheck: check('grade_level_check', sql`${table.gradeLevel} >= 6 AND ${table.gradeLevel} <= 12`),
}));

// ============================================================================
// TypeScript Types (inferred from schema)
// ============================================================================

export type Educator = typeof educators.$inferSelect;
export type NewEducator = typeof educators.$inferInsert;

export type Student = typeof students.$inferSelect;
export type NewStudent = typeof students.$inferInsert;

export type Document = typeof documents.$inferSelect;
export type NewDocument = typeof documents.$inferInsert;

export type GradeWord = typeof gradeWords.$inferSelect;
export type NewGradeWord = typeof gradeWords.$inferInsert;

// ============================================================================
// Status Enums
// ============================================================================

export const DocumentStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;

export type DocumentStatusType = typeof DocumentStatus[keyof typeof DocumentStatus];

// ============================================================================
// Grade Level Constants
// ============================================================================

export const VALID_GRADE_LEVELS = [6, 7, 8, 9, 10, 11, 12] as const;
export type GradeLevelType = typeof VALID_GRADE_LEVELS[number];
