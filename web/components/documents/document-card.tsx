"use client"

import { useState, useEffect } from "react"
import {
  FileText,
  Download,
  Eye,
  Trash2,
  RefreshCw,
  AlertCircle,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { DocumentStatusBadge } from "./document-status-badge"
import { DeleteDocumentDialog } from "./delete-document-dialog"
import { AnalyzeDocumentButton } from "@/components/vocabulary/analyze-document-button"
import { downloadDocument } from "@/lib/download"
import { formatDistanceToNow } from "@/lib/date-utils"
import { useDocumentPolling } from "@/hooks/use-document-polling"
import { getAuthenticatedClient } from "@/lib/api-client"
import { toast } from "sonner"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]
type FileType = components["schemas"]["FileType"]
type DocumentStatus = components["schemas"]["DocumentStatus"]

interface DocumentCardProps {
  document: DocumentPublic
  token: string
  onDelete?: () => void
  onStatusChange?: (document: DocumentPublic) => void
}

// Subject color mapping
const subjectColors: Record<string, string> = {
  ELA: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300",
  Math: "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300",
  Science:
    "bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300",
  "Social Studies":
    "bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300",
}

// File type icon mapping
const fileTypeIcons: Record<FileType, typeof FileText> = {
  pdf: FileText,
  docx: FileText,
  txt: FileText,
}

export function DocumentCard({
  document: initialDocument,
  token,
  onDelete,
  onStatusChange,
}: DocumentCardProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  // Use polling for real-time status updates
  const { document: polledDocument, isPolling } = useDocumentPolling({
    documentId: initialDocument.id,
    token,
    enabled: true,
    onStatusChange: (status, doc) => {
      // Notify parent component of status change
      onStatusChange?.(doc)

      // Show toast notification for status changes
      if (status === "completed") {
        toast.success("Analysis Complete", {
          description: `${doc.title} has been analyzed successfully.`,
        })
      } else if (status === "failed") {
        toast.error("Analysis Failed", {
          description:
            doc.error_message || "An error occurred during analysis.",
        })
      }
    },
  })

  // Use polled document if available, otherwise use initial document
  const document = polledDocument || initialDocument

  const FileIcon = fileTypeIcons[document.file_type] || FileText

  // Format upload date
  const uploadDate = new Date(document.upload_date)
  const formattedDate = formatDistanceToNow(uploadDate)

  // Get subject color
  const subjectColor =
    subjectColors[document.subject || ""] ||
    "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"

  // Determine if we can view analysis or analyze
  const canViewAnalysis = document.status === "completed"
  const canAnalyze = document.status === "pending"

  // Handle download
  const handleDownload = async () => {
    setIsDownloading(true)
    try {
      // Extract filename from title or use a default
      const filename = `${document.title}.${document.file_type}`
      await downloadDocument(document.id, document.s3_key, filename, token)
    } finally {
      setIsDownloading(false)
    }
  }

  // Handle delete success
  const handleDeleteSuccess = () => {
    if (onDelete) {
      onDelete()
    }
  }

  // Handle analysis complete
  const handleAnalysisComplete = () => {
    // Status will be updated by polling hook
    // Notify parent component if needed
    onStatusChange?.(document)
  }

  // Get status-specific message
  const getStatusMessage = () => {
    switch (document.status) {
      case "pending":
        return "Ready to analyze"
      case "processing":
        return "Analyzing document..."
      case "completed":
        return "Analysis complete"
      case "failed":
        return document.error_message || "Analysis failed"
      default:
        return null
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Header: Icon and Title */}
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-muted p-2 shrink-0">
              <FileIcon className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm truncate">
                {document.title}
              </h3>
              <p className="text-xs text-muted-foreground mt-1">
                {document.file_type.toUpperCase()} • {formattedDate}
              </p>
            </div>
          </div>

          {/* Badges: Subject and Status */}
          <div className="flex flex-wrap gap-2">
            {document.subject && (
              <Badge
                variant="outline"
                className={`border-transparent ${subjectColor}`}
              >
                {document.subject}
              </Badge>
            )}
            <DocumentStatusBadge status={document.status} />
          </div>

          {/* Status Messages */}
          <div className="flex items-start gap-2">
            {document.status === "pending" && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <AlertCircle className="h-3 w-3" />
                <span>{getStatusMessage()}</span>
              </div>
            )}
            {document.status === "processing" && (
              <div className="flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400">
                <RefreshCw className="h-3 w-3 animate-spin" />
                <span>{getStatusMessage()}</span>
              </div>
            )}
            {document.status === "completed" && (
              <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400">
                <Eye className="h-3 w-3" />
                <span>{getStatusMessage()}</span>
              </div>
            )}
            {document.status === "failed" && (
              <div className="flex flex-col gap-2 w-full">
                <div className="flex items-center gap-2 text-xs text-destructive">
                  <AlertCircle className="h-3 w-3" />
                  <span>{getStatusMessage()}</span>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              disabled={isDownloading}
              className="flex-1 min-w-[120px]"
            >
              <Download className="h-4 w-4 mr-2" />
              {isDownloading ? "Downloading..." : "Download"}
            </Button>

            {canAnalyze && (
              <AnalyzeDocumentButton
                documentId={document.id}
                token={token}
                onAnalysisComplete={handleAnalysisComplete}
              />
            )}

            {canViewAnalysis && (
              <Button
                variant="default"
                size="sm"
                className="flex-1 min-w-[120px]"
              >
                <Eye className="h-4 w-4 mr-2" />
                View Analysis
              </Button>
            )}

            {document.status === "failed" && (
              <AnalyzeDocumentButton
                documentId={document.id}
                token={token}
                onAnalysisComplete={handleAnalysisComplete}
              />
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDeleteDialog(true)}
              className="text-muted-foreground hover:text-destructive"
              title="Delete document"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>

      {/* Delete confirmation dialog */}
      <DeleteDocumentDialog
        document={document}
        token={token}
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        onDeleteSuccess={handleDeleteSuccess}
      />
    </Card>
  )
}
