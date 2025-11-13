"use client"

import { useEffect, useState } from "react"
import { AlertCircle, Loader2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { getAuthenticatedClient } from "@/lib/api-client"
import { StatsCards } from "./stats-cards"
import { GradeDistributionChart } from "./grade-distribution-chart"
import { ChallengingWordsList } from "./challenging-words-list"
import { Button } from "@/components/ui/button"

interface VocabularyAnalysis {
  analysis_id: string
  document_id: number
  total_words: number
  unique_words: number
  grade_distribution: Record<string, number>
  average_grade_level: number
  unmapped_words: number
  unmapped_percentage: number
  challenging_words: Array<{
    word: string
    grade_level: number
    definition?: string | null
    frequency: number
  }>
  analyzed_at: string
}

interface VocabularyProfileProps {
  documentId: number
  studentGradeLevel: number
  token: string
  refreshTrigger?: number
}

export function VocabularyProfile({
  documentId,
  studentGradeLevel,
  token,
  refreshTrigger = 0,
}: VocabularyProfileProps) {
  const [analysis, setAnalysis] = useState<VocabularyAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchAnalysis() {
      try {
        setLoading(true)
        setError(null)

        const apiClient = getAuthenticatedClient(token)

        // GET /api/documents/{document_id}/analysis
        const { data, error: apiError } = await apiClient.GET(
          "/api/documents/{document_id}/analysis",
          {
            params: {
              path: {
                document_id: documentId,
              },
            },
          }
        )

        if (apiError) {
          // If 404, analysis doesn't exist yet
          if (JSON.stringify(apiError).includes("404")) {
            setAnalysis(null)
          } else {
            setError("Failed to load vocabulary analysis")
            console.error("Error fetching analysis:", apiError)
          }
          return
        }

        if (data) {
          setAnalysis(data as VocabularyAnalysis)
        }
      } catch (err) {
        console.error("Error fetching analysis:", err)
        setError("An unexpected error occurred")
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [documentId, token, refreshTrigger])

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Loading vocabulary analysis...
          </p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.location.reload()}
          className="mt-2"
        >
          Retry
        </Button>
      </Alert>
    )
  }

  // No analysis state
  if (!analysis) {
    return null
  }

  // Success state - display analysis
  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <StatsCards
        totalWords={analysis.total_words}
        uniqueWords={analysis.unique_words}
        averageGradeLevel={analysis.average_grade_level}
        unmappedPercentage={analysis.unmapped_percentage}
      />

      {/* Grade Distribution Chart */}
      <GradeDistributionChart
        gradeDistribution={analysis.grade_distribution}
        studentGradeLevel={studentGradeLevel}
      />

      {/* Challenging Words List */}
      <ChallengingWordsList
        words={analysis.challenging_words}
        studentGradeLevel={studentGradeLevel}
      />

      {/* Analysis Metadata */}
      <div className="text-xs text-muted-foreground text-center">
        Analysis completed{" "}
        {new Date(analysis.analyzed_at).toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "numeric",
          minute: "numeric",
        })}
      </div>
    </div>
  )
}
