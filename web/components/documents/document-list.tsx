"use client"

import { useEffect, useState, useCallback } from "react"
import { FileText, AlertCircle, RefreshCw } from "lucide-react"
import { getAuthenticatedClient } from "@/lib/api-client"
import { DocumentCard } from "./document-card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]

interface DocumentListProps {
  studentId: number
  token: string
  refreshTrigger?: number
}

export function DocumentList({
  studentId,
  token,
  refreshTrigger = 0,
}: DocumentListProps) {
  const [documents, setDocuments] = useState<DocumentPublic[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const apiClient = getAuthenticatedClient(token)

      const { data, error: apiError } = await apiClient.GET(
        "/api/documents/students/{student_id}/documents",
        {
          params: {
            path: {
              student_id: studentId,
            },
          },
        }
      )

      if (apiError) {
        const errorMessage =
          typeof apiError === "object" && apiError !== null
            ? JSON.stringify(apiError)
            : String(apiError)
        setError(errorMessage || "Failed to load documents")
        return
      }

      if (data) {
        setDocuments(data)
      }
    } catch (err) {
      console.error("Error fetching documents:", err)
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      )
    } finally {
      setLoading(false)
    }
  }, [studentId, token])

  // Fetch documents on mount and when refreshTrigger changes
  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments, refreshTrigger])

  // Loading state
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-4 p-6 border rounded-lg">
              <div className="flex items-start gap-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-6 w-16" />
                <Skeleton className="h-6 w-20" />
              </div>
              <Skeleton className="h-9 w-full" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="rounded-full bg-destructive/10 p-3 mb-4">
          <AlertCircle className="h-8 w-8 text-destructive" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Failed to load documents</h3>
        <p className="text-sm text-muted-foreground mb-6 max-w-md">{error}</p>
        <Button onClick={fetchDocuments} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </Button>
      </div>
    )
  }

  // Empty state
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="rounded-full bg-muted p-3 mb-4">
          <FileText className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-2">
          No documents uploaded yet
        </h3>
        <p className="text-sm text-muted-foreground max-w-md">
          Upload student essays, transcripts, or other writing samples to begin
          vocabulary analysis and get personalized recommendations.
        </p>
      </div>
    )
  }

  // Handle document deletion
  const handleDocumentDelete = () => {
    // Refresh the document list after deletion
    fetchDocuments()
  }

  // Document grid
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          token={token}
          onDelete={handleDocumentDelete}
        />
      ))}
    </div>
  )
}
