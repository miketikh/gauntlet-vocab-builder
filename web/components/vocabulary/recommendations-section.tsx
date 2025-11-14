"use client"

import { useEffect, useState } from "react"
import {
  AlertCircle,
  Lightbulb,
  Loader2,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent } from "@/components/ui/card"
import { toast } from "sonner"

// Type definitions based on backend API
type RecommendationStatus = "pending" | "adopted" | "not_used"

interface Recommendation {
  id: number
  student_id: number
  document_id: number | null
  word: string
  recommended_grade_level: number
  subject: string | null
  current_usage: string | null
  context: string | null
  example_sentence: string | null
  rationale: string | null
  status: RecommendationStatus
  recommended_at: string
}

interface RecommendationsSectionProps {
  studentId: number
  studentGradeLevel: number
  token: string
  refreshTrigger?: number
}

// Subject color mapping
const subjectColors: Record<string, string> = {
  ELA: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  Math: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  Science:
    "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
  "Social Studies":
    "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
}

const statusColors: Record<RecommendationStatus, string> = {
  pending:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  adopted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  not_used: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300",
}

const statusLabels: Record<RecommendationStatus, string> = {
  pending: "Pending",
  adopted: "Adopted",
  not_used: "Not Used",
}

export function RecommendationsSection({
  studentId,
  token,
  refreshTrigger = 0,
}: RecommendationsSectionProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

  // Filters
  const [subjectFilter, setSubjectFilter] = useState<string>("all")
  const [countLimit, setCountLimit] = useState<number>(10)

  // Fetch recommendations
  useEffect(() => {
    async function fetchRecommendations() {
      try {
        setLoading(true)
        setError(null)

        // Build query params
        const queryParams: Record<string, string> = {
          limit: countLimit.toString(),
        }

        if (subjectFilter !== "all") {
          queryParams.subject = subjectFilter
        }

        // GET /api/students/{student_id}/recommendations
        const response = await fetch(
          `/api/students/${studentId}/recommendations?${new URLSearchParams(
            queryParams
          ).toString()}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        )

        if (!response.ok) {
          if (response.status === 404) {
            setRecommendations([])
            return
          }
          throw new Error("Failed to fetch recommendations")
        }

        const data = await response.json()
        setRecommendations(data)
      } catch (err) {
        console.error("Error fetching recommendations:", err)
        setError("Failed to load recommendations")
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [studentId, token, subjectFilter, countLimit, refreshTrigger])

  // Generate recommendations
  const handleGenerateRecommendations = async () => {
    try {
      setGenerating(true)
      setError(null)

      const response = await fetch(
        `/api/students/${studentId}/recommendations/generate`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            count: 10,
            subject: subjectFilter !== "all" ? subjectFilter : null,
          }),
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.detail || "Failed to generate recommendations"
        )
      }

      const data = await response.json()

      toast.success(
        `Generated ${data.count} recommendation${data.count !== 1 ? "s" : ""}`
      )

      // Refresh recommendations list
      setRecommendations([...data.recommendations, ...recommendations])
    } catch (err) {
      console.error("Error generating recommendations:", err)
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Failed to generate recommendations"
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setGenerating(false)
    }
  }

  const toggleRowExpansion = (id: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedRows(newExpanded)
  }

  // Get unique subjects from recommendations
  const availableSubjects = Array.from(
    new Set(
      recommendations
        .map((r) => r.subject)
        .filter((s): s is string => s !== null)
    )
  )

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Loading recommendations...
          </p>
        </div>
      </div>
    )
  }

  // Error state
  if (error && recommendations.length === 0) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  // Empty state
  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="rounded-full bg-amber-100 dark:bg-amber-900 p-3 mb-4">
          <Lightbulb className="h-8 w-8 text-amber-600 dark:text-amber-400" />
        </div>
        <h3 className="text-lg font-semibold mb-2">No recommendations yet</h3>
        <p className="text-sm text-muted-foreground max-w-md mb-6">
          Generate personalized vocabulary recommendations based on document
          analysis. The AI will suggest words that are appropriate for this
          student&apos;s level.
        </p>
        <Button
          onClick={handleGenerateRecommendations}
          disabled={generating}
          className="gap-2"
        >
          {generating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Generate Recommendations
            </>
          )}
        </Button>
      </div>
    )
  }

  // Recommendations exist - show table/cards with filters
  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Subject filter tabs */}
          {availableSubjects.length > 0 && (
            <Tabs value={subjectFilter} onValueChange={setSubjectFilter}>
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                {availableSubjects.map((subject) => (
                  <TabsTrigger key={subject} value={subject}>
                    {subject}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          )}

          {/* Count selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Show:</span>
            <Select
              value={countLimit.toString()}
              onValueChange={(value) => setCountLimit(Number(value))}
            >
              <SelectTrigger className="w-[100px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="15">15</SelectItem>
                <SelectItem value="20">20</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Generate more button */}
        <Button
          onClick={handleGenerateRecommendations}
          disabled={generating}
          variant="outline"
          className="gap-2"
        >
          {generating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Generate More
            </>
          )}
        </Button>
      </div>

      {/* Desktop table view */}
      <div className="hidden md:block border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Word</TableHead>
              <TableHead>Grade</TableHead>
              <TableHead>Subject</TableHead>
              <TableHead>Current Usage</TableHead>
              <TableHead>Example</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {recommendations.map((rec) => {
              const isExpanded = expandedRows.has(rec.id)
              return (
                <>
                  <TableRow key={rec.id}>
                    <TableCell className="font-semibold text-base">
                      {rec.word}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        Grade {rec.recommended_grade_level}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {rec.subject && (
                        <Badge
                          className={subjectColors[rec.subject] || ""}
                          variant="secondary"
                        >
                          {rec.subject}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {rec.current_usage || "—"}
                    </TableCell>
                    <TableCell className="text-sm max-w-[300px] truncate">
                      {rec.example_sentence || "—"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={statusColors[rec.status]}
                        variant="secondary"
                      >
                        {statusLabels[rec.status]}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {rec.rationale && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleRowExpansion(rec.id)}
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                  {isExpanded && rec.rationale && (
                    <TableRow>
                      <TableCell colSpan={7} className="bg-muted/50">
                        <div className="py-2 px-4">
                          <p className="text-sm font-medium mb-1">Rationale:</p>
                          <p className="text-sm text-muted-foreground">
                            {rec.rationale}
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </>
              )
            })}
          </TableBody>
        </Table>
      </div>

      {/* Mobile card view */}
      <div className="md:hidden space-y-4">
        {recommendations.map((rec) => {
          const isExpanded = expandedRows.has(rec.id)
          return (
            <Card key={rec.id}>
              <CardContent className="pt-6">
                <div className="space-y-3">
                  {/* Word and grade */}
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">{rec.word}</h3>
                      <Badge variant="outline" className="mt-1">
                        Grade {rec.recommended_grade_level}
                      </Badge>
                    </div>
                    <div className="flex flex-col gap-2 items-end">
                      {rec.subject && (
                        <Badge
                          className={subjectColors[rec.subject] || ""}
                          variant="secondary"
                        >
                          {rec.subject}
                        </Badge>
                      )}
                      <Badge
                        className={statusColors[rec.status]}
                        variant="secondary"
                      >
                        {statusLabels[rec.status]}
                      </Badge>
                    </div>
                  </div>

                  {/* Current usage */}
                  {rec.current_usage && (
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Current Usage
                      </p>
                      <p className="text-sm">{rec.current_usage}</p>
                    </div>
                  )}

                  {/* Example sentence */}
                  {rec.example_sentence && (
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Example
                      </p>
                      <p className="text-sm italic">{rec.example_sentence}</p>
                    </div>
                  )}

                  {/* Rationale (expandable) */}
                  {rec.rationale && (
                    <div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleRowExpansion(rec.id)}
                        className="w-full justify-between px-0"
                      >
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">
                          Rationale
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </Button>
                      {isExpanded && (
                        <p className="text-sm text-muted-foreground mt-2">
                          {rec.rationale}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
