"use client"

import { useAuth } from "@/contexts/auth-context"
import { DashboardLayout } from "@/components/dashboard/layout"
import { StudentList } from "@/components/students/student-list"
import { AddStudentDialog } from "@/components/students/add-student-dialog"
import { AnalyticsHeader } from "@/components/analytics/analytics-header"
import { StudentComparisonTable } from "@/components/analytics/student-comparison-table"
import { Loader2, UserPlus, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { getAuthenticatedClient } from "@/lib/api-client"

interface StudentSummary {
  student_id: number
  name: string
  current_grade_level: number | null
  actual_grade: number
  progress_trend: "improving" | "stable" | "declining"
  grade_level_change: number
  adoption_rate: number
  total_recommendations: number
  adopted_recommendations: number
  last_activity: string | null
  needs_support: boolean
  is_top_performer: boolean
}

interface AnalyticsData {
  total_students: number
  average_grade_level: number | null
  grade_distribution: {
    below_grade: number
    at_grade: number
    above_grade: number
  }
  average_adoption_rate: number
  total_documents_analyzed: number
  students: StudentSummary[]
  top_performers: StudentSummary[]
  needs_support: StudentSummary[]
}

export default function DashboardPage() {
  const { educator, loading } = useAuth()
  const [refreshKey, setRefreshKey] = useState(0)
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(true)
  const [analyticsError, setAnalyticsError] = useState<string | null>(null)
  const supabase = createClient()

  const handleStudentCreated = () => {
    // Trigger refresh by updating key
    setRefreshKey((prev) => prev + 1)
    // Also refresh analytics
    fetchAnalytics()
  }

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true)
    setAnalyticsError(null)

    try {
      // Get access token
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        throw new Error("Not authenticated")
      }

      // Create authenticated API client
      const apiClient = getAuthenticatedClient(session.access_token)

      // Fetch analytics
      const { data, error: apiError } = await apiClient.GET(
        "/api/educators/analytics"
      )

      if (apiError) {
        const errorMessage =
          typeof apiError === "object" && apiError !== null
            ? JSON.stringify(apiError)
            : String(apiError)
        throw new Error(errorMessage || "Failed to fetch analytics")
      }

      if (!data) {
        throw new Error("No data returned from API")
      }

      setAnalytics(data as AnalyticsData)
    } catch (err) {
      console.error("Error fetching analytics:", err)
      setAnalyticsError(
        err instanceof Error ? err.message : "Failed to load analytics"
      )
    } finally {
      setAnalyticsLoading(false)
    }
  }

  useEffect(() => {
    if (!loading && educator) {
      fetchAnalytics()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, educator])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">
            Loading your dashboard...
          </p>
        </div>
      </div>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Track class progress and manage your student roster
            </p>
          </div>
          <AddStudentDialog
            onSuccess={handleStudentCreated}
            trigger={
              <Button size="lg">
                <UserPlus className="mr-2 h-5 w-5" />
                Add Student
              </Button>
            }
          />
        </div>

        {/* Analytics Header */}
        <AnalyticsHeader
          totalStudents={analytics?.total_students || 0}
          averageGradeLevel={analytics?.average_grade_level || null}
          averageAdoptionRate={analytics?.average_adoption_rate || 0}
          totalDocuments={analytics?.total_documents_analyzed || 0}
          loading={analyticsLoading}
        />

        {/* Error State */}
        {analyticsError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error Loading Analytics</AlertTitle>
            <AlertDescription className="flex items-center justify-between">
              <span>{analyticsError}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchAnalytics}
                className="ml-4"
              >
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Student Comparison Table */}
        {analytics && analytics.students.length > 0 && (
          <StudentComparisonTable
            students={analytics.students}
            gradeDistribution={analytics.grade_distribution}
            loading={analyticsLoading}
          />
        )}

        {/* Student Grid View */}
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-4">
            All Students
          </h2>
          <StudentList
            key={refreshKey}
            educatorName={educator?.name || "Educator"}
          />
        </div>
      </div>
    </DashboardLayout>
  )
}
