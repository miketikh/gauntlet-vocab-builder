"use client"

import { useState, useEffect } from "react"
import { FileText, BarChart3, Lightbulb, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { UploadDocumentDialog } from "@/components/documents/upload-document-dialog"
import { DocumentList } from "@/components/documents/document-list"
import { BulkAnalyzeButton } from "@/components/documents/bulk-analyze-button"
import { VocabularyProfile } from "@/components/vocabulary/vocabulary-profile"
import { getAuthenticatedClient } from "@/lib/api-client"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]

interface StudentSectionsProps {
  studentId: number
  studentGradeLevel: number
  token: string
  onDocumentUploaded?: () => void
  refreshTrigger?: number
}

export function StudentSections({
  studentId,
  studentGradeLevel,
  token,
  onDocumentUploaded,
  refreshTrigger = 0,
}: StudentSectionsProps) {
  const [documentCount, setDocumentCount] = useState<number>(0)
  const [documents, setDocuments] = useState<DocumentPublic[]>([])
  const [isLoadingCount, setIsLoadingCount] = useState(true)
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(
    null
  )
  const [analysisRefreshTrigger, setAnalysisRefreshTrigger] = useState(0)

  // Fetch document count and list for display in header
  useEffect(() => {
    async function fetchDocumentCount() {
      try {
        setIsLoadingCount(true)
        const apiClient = getAuthenticatedClient(token)
        const { data } = await apiClient.GET(
          "/api/documents/students/{student_id}/documents",
          {
            params: {
              path: {
                student_id: studentId,
              },
            },
          }
        )
        if (data) {
          setDocumentCount(data.length)
          setDocuments(data)

          // Auto-select first completed document
          const completedDoc = data.find((doc) => doc.status === "completed")
          if (completedDoc && !selectedDocumentId) {
            setSelectedDocumentId(completedDoc.id)
          }
        }
      } catch (error) {
        console.error("Error fetching document count:", error)
      } finally {
        setIsLoadingCount(false)
      }
    }

    fetchDocumentCount()
  }, [studentId, token, refreshTrigger, selectedDocumentId])

  // Handle bulk analysis complete
  const handleBulkAnalyzeComplete = () => {
    // Refresh document list and analysis
    setAnalysisRefreshTrigger((prev) => prev + 1)
    onDocumentUploaded?.()
  }

  // Get completed documents for dropdown
  const completedDocuments = documents.filter(
    (doc) => doc.status === "completed"
  )

  return (
    <div className="space-y-6">
      {/* Documents Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Uploaded Documents
              {!isLoadingCount && documentCount > 0 && (
                <span className="text-sm font-normal text-muted-foreground">
                  ({documentCount})
                </span>
              )}
            </CardTitle>
            <div className="flex items-center gap-2">
              {!isLoadingCount && documents.length > 0 && (
                <BulkAnalyzeButton
                  documents={documents}
                  token={token}
                  onComplete={handleBulkAnalyzeComplete}
                />
              )}
              <UploadDocumentDialog
                studentId={studentId}
                token={token}
                onUploadComplete={onDocumentUploaded}
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <DocumentList
            studentId={studentId}
            token={token}
            refreshTrigger={refreshTrigger}
          />
        </CardContent>
      </Card>

      {/* Vocabulary Profile Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Vocabulary Analysis
            </CardTitle>
            {completedDocuments.length > 0 && (
              <Select
                value={selectedDocumentId?.toString() || ""}
                onValueChange={(value) => setSelectedDocumentId(Number(value))}
              >
                <SelectTrigger className="w-[250px]">
                  <SelectValue placeholder="Select a document" />
                </SelectTrigger>
                <SelectContent>
                  {completedDocuments.map((doc) => (
                    <SelectItem key={doc.id} value={doc.id.toString()}>
                      {doc.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {completedDocuments.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-3 mb-4">
                <BarChart3 className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                No analyzed documents yet
              </h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Upload and analyze a document to see vocabulary statistics, word
                frequency analysis, and reading level metrics.
              </p>
            </div>
          ) : selectedDocumentId ? (
            <VocabularyProfile
              documentId={selectedDocumentId}
              studentGradeLevel={studentGradeLevel}
              token={token}
              refreshTrigger={analysisRefreshTrigger}
            />
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-3 mb-4">
                <BarChart3 className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              </div>
              <p className="text-sm text-muted-foreground">
                Select a document to view its vocabulary analysis
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendations Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Personalized Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-amber-100 dark:bg-amber-900 p-3 mb-4">
              <Lightbulb className="h-8 w-8 text-amber-600 dark:text-amber-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              Recommendations will appear after document analysis
            </h3>
            <p className="text-sm text-muted-foreground max-w-md">
              After analyzing uploaded documents, the system will generate
              personalized vocabulary recommendations, learning resources, and
              practice activities tailored to this student&apos;s needs.
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <AlertCircle className="h-3 w-3" />
              <span>Recommendation engine coming in Story 4.4</span>
            </div>
          </div>

          {/* Placeholder for recommendation cards */}
          <div className="hidden grid-cols-1 md:grid-cols-2 gap-4">
            {/* Recommendation cards will be rendered here */}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
