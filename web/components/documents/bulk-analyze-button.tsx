"use client"

import { useState } from "react"
import { PlayCircle, Loader2, CheckCircle2, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import { getAuthenticatedClient } from "@/lib/api-client"
import { toast } from "sonner"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]

interface BulkAnalyzeButtonProps {
  documents: DocumentPublic[]
  token: string
  onComplete?: () => void
}

export function BulkAnalyzeButton({
  documents,
  token,
  onComplete,
}: BulkAnalyzeButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<{
    total: number
    completed: number
    failed: number
    errors: string[]
  }>({
    total: 0,
    completed: 0,
    failed: 0,
    errors: [],
  })

  // Filter to only pending documents
  const pendingDocuments = documents.filter((doc) => doc.status === "pending")

  // Handle bulk analysis
  const handleBulkAnalyze = async () => {
    if (pendingDocuments.length === 0) {
      toast.error("No Pending Documents", {
        description: "There are no pending documents to analyze.",
      })
      return
    }

    setIsAnalyzing(true)
    setResults({
      total: pendingDocuments.length,
      completed: 0,
      failed: 0,
      errors: [],
    })

    const apiClient = getAuthenticatedClient(token)
    let completed = 0
    let failed = 0
    const errors: string[] = []

    // Process documents sequentially to avoid overwhelming the server
    for (let i = 0; i < pendingDocuments.length; i++) {
      const doc = pendingDocuments[i]
      if (!doc) continue

      try {
        // TODO: Uncomment when backend analyze endpoint is available (Story 3.4)
        // const { error: apiError } = await apiClient.POST(
        //   "/api/documents/{document_id}/analyze",
        //   {
        //     params: {
        //       path: {
        //         document_id: doc.id,
        //       },
        //     },
        //   }
        // )

        // if (apiError) {
        //   failed++
        //   errors.push(`${doc.title}: Analysis request failed`)
        // } else {
        //   completed++
        // }

        // Temporary: Simulate success for UI testing
        completed++
      } catch (error) {
        failed++
        errors.push(
          `${doc.title}: ${error instanceof Error ? error.message : "Unknown error"}`
        )
      }

      // Update progress
      const currentProgress = ((i + 1) / pendingDocuments.length) * 100
      setProgress(currentProgress)
      setResults({
        total: pendingDocuments.length,
        completed,
        failed,
        errors,
      })
    }

    setIsAnalyzing(false)

    // Show completion toast
    if (failed === 0) {
      toast.success("Bulk Analysis Started", {
        description: `Successfully started analysis for ${completed} document${completed > 1 ? "s" : ""}.`,
      })
    } else {
      toast.error("Bulk Analysis Completed with Errors", {
        description: `Started ${completed} analysis, ${failed} failed.`,
      })
    }

    // Notify parent to refresh
    onComplete?.()

    // Close dialog after a short delay
    setTimeout(() => {
      setIsOpen(false)
      setProgress(0)
    }, 2000)
  }

  if (pendingDocuments.length === 0) {
    return null
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="default" size="sm">
          <PlayCircle className="h-4 w-4 mr-2" />
          Analyze All Pending ({pendingDocuments.length})
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Bulk Document Analysis</DialogTitle>
          <DialogDescription>
            Start analysis for all pending documents. This will process{" "}
            {pendingDocuments.length} document
            {pendingDocuments.length > 1 ? "s" : ""}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {!isAnalyzing && results.total === 0 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                The following documents will be analyzed:
              </p>
              <ul className="text-sm space-y-1 max-h-48 overflow-y-auto">
                {pendingDocuments.slice(0, 10).map((doc) => (
                  <li key={doc.id} className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-400" />
                    {doc.title}
                  </li>
                ))}
                {pendingDocuments.length > 10 && (
                  <li className="text-muted-foreground italic">
                    ...and {pendingDocuments.length - 10} more
                  </li>
                )}
              </ul>
            </div>
          )}

          {(isAnalyzing || results.total > 0) && (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">
                    {isAnalyzing ? "Processing..." : "Complete"}
                  </span>
                  <span className="font-medium">{Math.round(progress)}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="space-y-1">
                  <div className="text-2xl font-bold">{results.total}</div>
                  <div className="text-xs text-muted-foreground">Total</div>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-green-600">
                    {results.completed}
                  </div>
                  <div className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    Started
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-red-600">
                    {results.failed}
                  </div>
                  <div className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                    <XCircle className="h-3 w-3" />
                    Failed
                  </div>
                </div>
              </div>

              {results.errors.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-destructive">
                    Errors:
                  </p>
                  <ul className="text-xs space-y-1 max-h-32 overflow-y-auto">
                    {results.errors.map((error, i) => (
                      <li key={i} className="text-destructive">
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2">
          {!isAnalyzing && results.total === 0 && (
            <>
              <Button
                variant="outline"
                onClick={() => setIsOpen(false)}
                disabled={isAnalyzing}
              >
                Cancel
              </Button>
              <Button onClick={handleBulkAnalyze} disabled={isAnalyzing}>
                <PlayCircle className="h-4 w-4 mr-2" />
                Start Analysis
              </Button>
            </>
          )}
          {isAnalyzing && (
            <Button disabled>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Analyzing...
            </Button>
          )}
          {!isAnalyzing && results.total > 0 && (
            <Button onClick={() => setIsOpen(false)}>Close</Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
