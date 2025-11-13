"use client"

import { useEffect, useState, useCallback } from "react"
import { FileText, AlertCircle, RefreshCw, Filter } from "lucide-react"
import { getAuthenticatedClient } from "@/lib/api-client"
import { DocumentCard } from "./document-card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]
type DocumentStatus = components["schemas"]["DocumentStatus"]

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
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | "all">(
    "all"
  )

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

  // Handle status change (for real-time updates)
  const handleStatusChange = (updatedDocument: DocumentPublic) => {
    setDocuments((prev) =>
      prev.map((doc) => (doc.id === updatedDocument.id ? updatedDocument : doc))
    )
  }

  // Filter documents by status
  const filteredDocuments = documents.filter((doc) =>
    statusFilter === "all" ? true : doc.status === statusFilter
  )

  // Calculate counts by status
  const statusCounts = {
    all: documents.length,
    pending: documents.filter((d) => d.status === "pending").length,
    processing: documents.filter((d) => d.status === "processing").length,
    completed: documents.filter((d) => d.status === "completed").length,
    failed: documents.filter((d) => d.status === "failed").length,
  }

  // Document grid
  return (
    <div className="space-y-4">
      {/* Status filter tabs */}
      <Tabs
        value={statusFilter}
        onValueChange={(value) =>
          setStatusFilter(value as DocumentStatus | "all")
        }
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all" className="gap-2">
            All
            {statusCounts.all > 0 && (
              <Badge variant="secondary" className="ml-1 px-1.5 py-0 text-xs">
                {statusCounts.all}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="completed" className="gap-2">
            Analyzed
            {statusCounts.completed > 0 && (
              <Badge variant="secondary" className="ml-1 px-1.5 py-0 text-xs">
                {statusCounts.completed}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="pending" className="gap-2">
            Pending
            {statusCounts.pending > 0 && (
              <Badge variant="secondary" className="ml-1 px-1.5 py-0 text-xs">
                {statusCounts.pending}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="processing" className="gap-2">
            Processing
            {statusCounts.processing > 0 && (
              <Badge variant="secondary" className="ml-1 px-1.5 py-0 text-xs">
                {statusCounts.processing}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="failed" className="gap-2">
            Failed
            {statusCounts.failed > 0 && (
              <Badge variant="secondary" className="ml-1 px-1.5 py-0 text-xs">
                {statusCounts.failed}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Filtered documents grid */}
      {filteredDocuments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-3 mb-4">
            <Filter className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold mb-2">
            No {statusFilter !== "all" ? statusFilter : ""} documents
          </h3>
          <p className="text-sm text-muted-foreground max-w-md">
            {statusFilter === "all"
              ? "Upload student essays, transcripts, or other writing samples to begin vocabulary analysis."
              : `There are no ${statusFilter} documents. Try selecting a different filter.`}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((document) => (
            <DocumentCard
              key={document.id}
              document={document}
              token={token}
              onDelete={handleDocumentDelete}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}
    </div>
  )
}
