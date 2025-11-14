"use client"

import { useEffect, useState } from "react"
import { TrendingUp, TrendingDown, Minus, Loader2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"

// Types for the API response
interface VocabularyHistoryDataPoint {
  date: string
  average_grade_level: number | null
  document_id: number
  document_title: string
  unique_words: number
  total_words: number
}

interface VocabularyHistoryResponse {
  student_id: number
  data_points: VocabularyHistoryDataPoint[]
  overall_trend: "improving" | "stable" | "declining"
  grade_level_change: number
}

interface VocabularyProgressChartProps {
  studentId: number
  studentGradeLevel: number
  token: string
  refreshTrigger?: number
}

export function VocabularyProgressChart({
  studentId,
  studentGradeLevel,
  token,
  refreshTrigger = 0,
}: VocabularyProgressChartProps) {
  const [historyData, setHistoryData] =
    useState<VocabularyHistoryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchVocabularyHistory() {
      try {
        setLoading(true)
        setError(null)

        // Call the vocabulary history endpoint
        const response = await fetch(
          `http://localhost:8000/api/students/${studentId}/vocabulary/history`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        )

        if (!response.ok) {
          if (response.status === 404) {
            // Not enough data to show progress
            const data = await response.json()
            setError(
              data.detail ||
                "Not enough data. Upload at least 2 documents to see progress over time."
            )
            setLoading(false)
            return
          }
          throw new Error("Failed to fetch vocabulary history")
        }

        const data: VocabularyHistoryResponse = await response.json()
        setHistoryData(data)
      } catch (err) {
        console.error("Error fetching vocabulary history:", err)
        setError("An unexpected error occurred while loading progress data")
      } finally {
        setLoading(false)
      }
    }

    fetchVocabularyHistory()
  }, [studentId, token, refreshTrigger])

  // Get trend color
  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "improving":
        return "text-green-600 dark:text-green-400"
      case "declining":
        return "text-red-600 dark:text-red-400"
      case "stable":
        return "text-blue-600 dark:text-blue-400"
      default:
        return "text-muted-foreground"
    }
  }

  // Get trend icon
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "improving":
        return <TrendingUp className="h-4 w-4" />
      case "declining":
        return <TrendingDown className="h-4 w-4" />
      case "stable":
        return <Minus className="h-4 w-4" />
      default:
        return null
    }
  }

  // Get line color based on trend
  const getLineColor = (trend: string) => {
    switch (trend) {
      case "improving":
        return "#22c55e" // green-500
      case "declining":
        return "#ef4444" // red-500
      case "stable":
        return "#3b82f6" // blue-500
      default:
        return "#3b82f6"
    }
  }

  // Custom tooltip component
  const CustomTooltip = ({
    active,
    payload,
  }: {
    active?: boolean
    payload?: Array<{
      payload: VocabularyHistoryDataPoint & { dateDisplay: string }
    }>
  }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border border-border rounded-lg shadow-lg p-3">
          <p className="font-semibold text-sm mb-1">{data.document_title}</p>
          <p className="text-xs text-muted-foreground mb-2">
            {new Date(data.date).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </p>
          <p className="text-sm">
            <span className="font-medium">Grade Level:</span>{" "}
            {data.average_grade_level?.toFixed(1) || "N/A"}
          </p>
          <p className="text-sm">
            <span className="font-medium">Unique Words:</span>{" "}
            {data.unique_words}
          </p>
        </div>
      )
    }
    return null
  }

  // Loading state
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Vocabulary Progress Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Loading progress data...
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Error state (not enough data)
  if (error || !historyData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Vocabulary Progress Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-3 mb-4">
              <TrendingUp className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Progress Data Yet</h3>
            <p className="text-sm text-muted-foreground max-w-md">
              {error || "Upload at least 2 documents to see progress over time"}
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Format data for Recharts
  const chartData = historyData.data_points.map((point) => ({
    ...point,
    // Format date for display
    dateDisplay: new Date(point.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }))

  // Calculate Y-axis domain (6.0 to 12.0 with some padding)
  const minGrade = Math.min(
    6.0,
    ...historyData.data_points
      .map((p) => p.average_grade_level)
      .filter((g): g is number => g !== null)
  )
  const maxGrade = Math.max(
    12.0,
    ...historyData.data_points
      .map((p) => p.average_grade_level)
      .filter((g): g is number => g !== null)
  )
  const yAxisDomain = [
    Math.max(6.0, Math.floor(minGrade - 0.5)),
    Math.min(12.0, Math.ceil(maxGrade + 0.5)),
  ]

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Vocabulary Progress Over Time
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className={getTrendColor(historyData.overall_trend)}
              >
                <span className="flex items-center gap-1">
                  {getTrendIcon(historyData.overall_trend)}
                  {historyData.overall_trend.charAt(0).toUpperCase() +
                    historyData.overall_trend.slice(1)}
                  {historyData.grade_level_change !== 0 && (
                    <span className="ml-1">
                      ({historyData.grade_level_change > 0 ? "+" : ""}
                      {historyData.grade_level_change.toFixed(1)} grade levels)
                    </span>
                  )}
                </span>
              </Badge>
            </div>
          </div>

          {/* Subject filter - placeholder for future implementation */}
          {/* <Select value={selectedSubject} onValueChange={setSelectedSubject}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by subject" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Subjects</SelectItem>
              <SelectItem value="ela">ELA</SelectItem>
              <SelectItem value="math">Math</SelectItem>
              <SelectItem value="science">Science</SelectItem>
            </SelectContent>
          </Select> */}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Chart */}
          <div className="w-full h-[300px] sm:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="dateDisplay"
                  className="text-xs"
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  domain={yAxisDomain}
                  className="text-xs"
                  tick={{ fontSize: 12 }}
                  label={{
                    value: "Grade Level",
                    angle: -90,
                    position: "insideLeft",
                    style: { fontSize: 12 },
                  }}
                />
                <Tooltip content={<CustomTooltip />} />
                {/* Reference line for student's target grade */}
                <ReferenceLine
                  y={studentGradeLevel}
                  stroke="#94a3b8"
                  strokeDasharray="5 5"
                  label={{
                    value: `Target (Grade ${studentGradeLevel})`,
                    position: "right",
                    style: { fontSize: 11, fill: "#64748b" },
                  }}
                />
                {/* Main line showing progress */}
                <Line
                  type="monotone"
                  dataKey="average_grade_level"
                  stroke={getLineColor(historyData.overall_trend)}
                  strokeWidth={2}
                  dot={{ r: 4, fill: getLineColor(historyData.overall_trend) }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Summary */}
          <div className="pt-4 border-t">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Documents Analyzed</p>
                <p className="font-semibold text-lg">
                  {historyData.data_points.length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Starting Level</p>
                <p className="font-semibold text-lg">
                  {historyData.data_points[0].average_grade_level?.toFixed(1) ||
                    "N/A"}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Current Level</p>
                <p className="font-semibold text-lg">
                  {historyData.data_points[
                    historyData.data_points.length - 1
                  ].average_grade_level?.toFixed(1) || "N/A"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
