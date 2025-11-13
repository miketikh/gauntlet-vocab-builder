"use client"

import { useState } from "react"
import { FileText, Download, Eye } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { DocumentStatusBadge } from "./document-status-badge"
import { downloadDocument } from "@/lib/download"
import { formatDistanceToNow } from "@/lib/date-utils"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]
type FileType = components["schemas"]["FileType"]

interface DocumentCardProps {
  document: DocumentPublic
  token: string
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

export function DocumentCard({ document, token }: DocumentCardProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  const FileIcon = fileTypeIcons[document.file_type] || FileText

  // Format upload date
  const uploadDate = new Date(document.upload_date)
  const formattedDate = formatDistanceToNow(uploadDate)

  // Get subject color
  const subjectColor =
    subjectColors[document.subject || ""] ||
    "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"

  // Determine if we can view analysis
  const canViewAnalysis = document.status === "completed"

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
          {document.status === "pending" && (
            <p className="text-xs text-muted-foreground">
              Processing will begin soon
            </p>
          )}
          {document.status === "processing" && (
            <p className="text-xs text-muted-foreground">
              Analyzing document...
            </p>
          )}
          {document.status === "failed" && document.error_message && (
            <p className="text-xs text-destructive">{document.error_message}</p>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              disabled={isDownloading}
              className="flex-1"
            >
              <Download className="h-4 w-4 mr-2" />
              {isDownloading ? "Downloading..." : "Download"}
            </Button>

            {canViewAnalysis && (
              <Button variant="default" size="sm" className="flex-1">
                <Eye className="h-4 w-4 mr-2" />
                View Analysis
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
