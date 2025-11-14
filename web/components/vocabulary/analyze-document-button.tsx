"use client"

import { useState } from "react"
import { Loader2, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { authenticatedFetch } from "@/lib/api-client"

interface AnalyzeDocumentButtonProps {
  documentId: number
  token: string
  onAnalysisComplete?: () => void
  disabled?: boolean
}

export function AnalyzeDocumentButton({
  documentId,
  token,
  onAnalysisComplete,
  disabled = false,
}: AnalyzeDocumentButtonProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyze = async () => {
    try {
      setIsAnalyzing(true)
      const response = await authenticatedFetch(
        `/api/documents/${documentId}/analyze`,
        token,
        {
          method: "POST",
        }
      )

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}))
        const detail =
          errorPayload?.detail || response.statusText || "Unknown error"
        console.error("Analysis failed:", detail)
        toast.error("Analysis failed", {
          description:
            detail || "Failed to analyze document. Please try again.",
        })
        return
      }

      toast.success("Analysis complete", {
        description: "Vocabulary profile has been generated.",
      })
      onAnalysisComplete?.()
    } catch (error) {
      console.error("Error analyzing document:", error)
      toast.error("Analysis failed", {
        description: "An unexpected error occurred.",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <Button
      onClick={handleAnalyze}
      disabled={disabled || isAnalyzing}
      size="sm"
      variant="default"
    >
      {isAnalyzing ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Analyzing...
        </>
      ) : (
        <>
          <Play className="mr-2 h-4 w-4" />
          Analyze Document
        </>
      )}
    </Button>
  )
}
