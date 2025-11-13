# User Interface Design Goals

## Overall UX Vision

The interface should prioritize **clarity and efficiency** for time-constrained educators. The design should feel professional and trustworthy (appropriate for educational context) while remaining approachable and easy to navigate. Key principles:

- **Progressive disclosure:** Show summary views by default, allow drill-down into details
- **Data-driven insights front and center:** Visualizations and key metrics should be immediately visible, not buried in tabs
- **Minimal friction for core workflows:** Document upload and student creation should be fast (<3 clicks from dashboard)
- **Trust through transparency:** Show how recommendations were generated, don't black-box the AI
- **Educator empowerment:** Provide controls (filters, customization) without overwhelming with options

## Key Interaction Paradigms

**Card-based browsing:** Student dashboard uses cards for scannable overview with key stats visible at a glance

**Drag-and-drop uploads:** Document upload supports drag-and-drop for quick batch additions

**Inline filtering:** Recommendations and progress views have inline subject filters (tabs or dropdowns) to avoid context switching

**Contextual actions:** Primary actions (upload document, view details) appear on hover/focus for cleaner interface

**Real-time feedback:** Show progress indicators during document analysis, use optimistic UI updates where possible

**Data visualization as primary interface:** Charts and graphs are interactive (hover for details, click to filter), not just static displays

## Core Screens and Views

**Login Screen**
- Supabase Auth UI integration with:
  - Email/password sign-in
  - Google OAuth option ("Sign in with Google" button)
  - Password reset flow (Supabase magic link)
- Clean, professional branding
- Future: Additional OAuth providers (Microsoft, Apple) if needed

**Main Dashboard** (Educator Home)
- Student grid/list with cards showing:
  - Student display name
  - Current grade level
  - Current vocabulary grade level
  - Recent progress indicator (↑↓→)
  - Document count
- "Add New Student" CTA button prominently placed
- Quick stats header (total students, avg improvement, etc.)
- User menu with sign-out option

**Create Student Page**
- Simple form: display name, grade level (6-8 dropdown)
- Immediate redirect to student detail page after creation

**Student Detail Page** (Most complex view)
- **Header:** Student name, grade level, overall vocabulary stats
- **Section 1: Upload Documents**
  - Drag-drop zone or file picker
  - Subject selector (ELA, Math, Science, Social Studies)
  - Title input
  - Upload button (triggers FastAPI analysis)
  - List of previously uploaded documents (date, title, subject)
- **Section 2: Current Vocabulary Profile**
  - Pie chart or bar chart showing grade-level distribution
  - Average grade level prominently displayed
  - Based on most recent analysis
- **Section 3: Recommendations**
  - Subject filter tabs/dropdown
  - Count selector (5, 10, 15, 20)
  - Table/list view with columns:
    - Word
    - Grade level
    - Current usage (what student says now)
    - Example sentence
    - Subject tag
  - Expandable rows for full rationale/context
- **Section 4: Progress Over Time**
  - Line graph showing vocabulary grade level progression
  - Toggle for subject-specific views
  - Display recommendation adoption rate
  - AI-generated insights box (narrative text)

**Settings Page** (Phase 2+)
- Educator profile settings (name, email - managed by Supabase)
- Account management (password change via Supabase)

## Accessibility: WCAG AA

**Target compliance level:** WCAG 2.1 Level AA

**Key requirements:**
- Sufficient color contrast ratios (4.5:1 for text)
- Keyboard navigation for all interactive elements
- Screen reader compatibility with semantic HTML and ARIA labels
- Focus indicators visible on all interactive elements
- Form labels and error messages clearly associated
- Charts have text alternatives and data tables

## Branding

**Style:** Clean, modern, professional educational tool aesthetic

**Tone:** Trustworthy, empowering, approachable (not playful/gamified for educator interface)

**Visual approach:**
- Simple, uncluttered layouts with generous whitespace
- Professional typography (clear, readable sans-serif)
- Data visualization as primary visual interest (no decorative graphics)
- Muted, professional color palette suitable for educational context
- Use shadcn/ui component library for consistent, accessible components

## Target Device and Platforms: Web Responsive

**Primary target:** Desktop/laptop browsers (educators typically work on computers for planning)

**Secondary target:** Tablet (iPads common in schools for educator use)

**Responsive breakpoints:**
- Desktop (1280px+): Full multi-column layouts
- Tablet (768px-1279px): Adjusted layouts, some sections stack
- Mobile (320px-767px): Fully stacked layout, optimized for viewing (not primary use case)

**Browser support:**
- Modern evergreen browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)

**Technical approach:**
- Tailwind CSS for responsive utilities
- shadcn/ui component library (already integrated in existing Next.js setup)
- Mobile-first CSS with progressive enhancement for larger screens
- Touch-friendly targets (44px minimum) for tablet support

---
