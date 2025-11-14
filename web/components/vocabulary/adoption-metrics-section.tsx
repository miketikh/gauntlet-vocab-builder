"use client"

import { useEffect, useState } from "react"
import { TrendingUp, Loader2, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { authenticatedFetch } from "@/lib/api-client"

interface AdoptionMetrics {
  student_id: number
  total_recommendations: number
  adopted: number
  pending: number
  not_used: number
  adoption_rate: number
}

interface AdoptionMetricsSectionProps {
  studentId: number
  token: string
  refreshTrigger?: number
}

export function AdoptionMetricsSection({
  studentId,
  token,
  refreshTrigger = 0,
}: AdoptionMetricsSectionProps) {
  const [metrics, setMetrics] = useState<AdoptionMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchMetrics() {
      try {
        setLoading(true)
        setError(null)

        const response = await authenticatedFetch(
          `/api/students/${studentId}/recommendations/metrics`,
          token
        )

        if (!response.ok) {
          if (response.status === 404) {
            // No recommendations yet
            setMetrics(null)
            return
          }
          throw new Error("Failed to fetch adoption metrics")
        }

        const data = await response.json()
        setMetrics(data)
      } catch (err) {
        console.error("Error fetching adoption metrics:", err)
        setError("Failed to load adoption metrics")
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [studentId, token, refreshTrigger])

  // Loading state
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Adoption Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  // Error state
  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Adoption Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  // No data state
  if (!metrics || metrics.total_recommendations === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Adoption Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="rounded-full bg-slate-100 dark:bg-slate-800 p-3 mb-4">
              <TrendingUp className="h-8 w-8 text-slate-400" />
            </div>
            <p className="text-sm text-muted-foreground">
              No recommendations yet. Generate vocabulary recommendations to
              track adoption metrics.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Calculate percentages
  const adoptedPercentage =
    metrics.total_recommendations > 0
      ? Math.round((metrics.adopted / metrics.total_recommendations) * 100)
      : 0
  const pendingPercentage =
    metrics.total_recommendations > 0
      ? Math.round((metrics.pending / metrics.total_recommendations) * 100)
      : 0
  const notUsedPercentage =
    metrics.total_recommendations > 0
      ? Math.round((metrics.not_used / metrics.total_recommendations) * 100)
      : 0

  // Display adoption rate as percentage (from the backend it's already 0-1 scale)
  const adoptionRatePercentage = Math.round(metrics.adoption_rate * 100)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Adoption Metrics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Overall Adoption Rate */}
          <div className="rounded-lg border bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950 p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-muted-foreground">
                Overall Adoption Rate
              </p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {adoptionRatePercentage}%
              </p>
            </div>
            <p className="text-xs text-muted-foreground">
              {metrics.adopted} of {metrics.adopted + metrics.not_used}{" "}
              completed recommendations
            </p>
          </div>

          {/* Total Recommendations */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium">Total Recommendations</p>
              <p className="text-lg font-semibold">
                {metrics.total_recommendations}
              </p>
            </div>
          </div>

          {/* Words Adopted */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Words Adopted</p>
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold text-green-600 dark:text-green-400">
                  {metrics.adopted}
                </p>
                <p className="text-xs text-muted-foreground">
                  ({adoptedPercentage}%)
                </p>
              </div>
            </div>
            <Progress
              value={adoptedPercentage}
              className="h-2 bg-green-100 dark:bg-green-950"
            />
          </div>

          {/* Still Learning (Pending) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Still Learning</p>
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                  {metrics.pending}
                </p>
                <p className="text-xs text-muted-foreground">
                  ({pendingPercentage}%)
                </p>
              </div>
            </div>
            <Progress
              value={pendingPercentage}
              className="h-2 bg-gray-100 dark:bg-gray-900"
            />
          </div>

          {/* Not Yet Used */}
          {metrics.not_used > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">Not Yet Used</p>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold text-yellow-600 dark:text-yellow-400">
                    {metrics.not_used}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    ({notUsedPercentage}%)
                  </p>
                </div>
              </div>
              <Progress
                value={notUsedPercentage}
                className="h-2 bg-yellow-100 dark:bg-yellow-950"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
