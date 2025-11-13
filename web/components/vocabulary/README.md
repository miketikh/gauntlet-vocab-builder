# Vocabulary Analysis Components

This directory contains components for displaying vocabulary analysis status and progress indicators (Story 3.6).

## Components

### AnalysisProgress

**File:** `analysis-progress.tsx`

Displays the current step in the analysis pipeline with a progress bar.

**Features:**

- 5-step pipeline visualization (Downloading → Extracting → Processing → Analyzing → Complete)
- Progress bar with percentage
- Current step highlighted with spinner animation
- Completed steps shown with checkmarks
- Estimated time remaining message

**Usage:**

```tsx
import { AnalysisProgress } from "@/components/vocabulary/analysis-progress"

;<AnalysisProgress currentStep={3} />
```

**Props:**

- `currentStep?: number` - Current step (1-5), if not provided shows indeterminate progress
- `className?: string` - Additional CSS classes

---

### AnalysisTimeline

**File:** `analysis-timeline.tsx`

Shows the analysis history for a document with visual timeline.

**Features:**

- Timeline visualization with icons
- Shows upload, start, complete, and failure events
- Timestamps for each event
- Error messages for failed analyses
- Color-coded status indicators

**Usage:**

```tsx
import { AnalysisTimeline } from "@/components/vocabulary/analysis-timeline"

;<AnalysisTimeline document={document} />
```

**Props:**

- `document: DocumentPublic` - Document object with status and metadata
- `className?: string` - Additional CSS classes

---

## Hooks

### useDocumentPolling

**File:** `/hooks/use-document-polling.ts`

Custom hook for polling document status with real-time updates.

**Features:**

- Automatically polls when document status is 'processing'
- Stops polling when status is 'completed' or 'failed'
- Configurable polling interval (default 3 seconds)
- Status change callbacks
- Error handling

**Usage:**

```tsx
import { useDocumentPolling } from "@/hooks/use-document-polling"

const { document, isPolling, error, refetch } = useDocumentPolling({
  documentId: "123",
  token: "auth-token",
  enabled: true,
  interval: 3000,
  onStatusChange: (status, doc) => {
    console.log("Status changed to:", status)
  },
})
```

**Parameters:**

- `documentId: string | number` - Document ID to poll
- `token: string` - Authentication token
- `enabled?: boolean` - Enable/disable polling (default: true)
- `interval?: number` - Polling interval in milliseconds (default: 3000)
- `onStatusChange?: (status, document) => void` - Callback when status changes

**Returns:**

- `document: DocumentPublic | null` - Current document data
- `isPolling: boolean` - Whether actively polling
- `error: string | null` - Error message if any
- `refetch: () => Promise<void>` - Manual refetch function

---

## Integration Notes

### Story 3.6 Implementation

This story focuses on **status and progress indicators** for the analysis pipeline. It complements Story 3.5 which handles the vocabulary profile display (results).

### Backend Dependency

The analysis endpoint (`POST /api/documents/{document_id}/analyze`) will be implemented in Story 3.4. The frontend components are ready with placeholder implementations.

### Toast Notifications

Uses `sonner` for toast notifications:

- Success: When analysis completes
- Error: When analysis fails
- Info: For retry/bulk analysis actions

### Real-time Updates

Document cards automatically poll for status updates when a document is in 'processing' state. Polling stops when status changes to 'completed' or 'failed'.

---

## TODO for Story 3.4 Integration

When the backend analysis endpoint is ready:

1. **Uncomment API calls in:**
   - `/components/documents/document-card.tsx` (line ~113)
   - `/components/documents/bulk-analyze-button.tsx` (line ~79)

2. **Update OpenAPI schema:**
   - Run `npm run generate:api` to regenerate types with the new analyze endpoint

3. **Test end-to-end flow:**
   - Upload document → status 'pending'
   - Trigger analysis → status 'processing'
   - Real-time polling shows progress
   - Analysis completes → status 'completed'
   - View vocabulary profile (Story 3.5)

---

## Component Relationships

```
StudentDetailPage
└── StudentSections
    └── Documents Card
        ├── BulkAnalyzeButton (all pending docs)
        └── DocumentList (with status filters)
            └── DocumentCard (with polling)
                ├── DocumentStatusBadge
                ├── Status messages
                ├── Retry button (failed)
                └── useDocumentPolling hook
```
