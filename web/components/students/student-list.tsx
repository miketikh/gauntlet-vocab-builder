"use client"

import { useEffect, useState } from "react"
import { StudentCard } from "./student-card"
import { EmptyState } from "@/components/dashboard/empty-state"
import { Skeleton } from "@/components/ui/skeleton"
import { createClient } from "@/lib/supabase/client"
import { getAuthenticatedClient } from "@/lib/api-client"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

interface Student {
  id: number
  name: string
  grade_level: number
  reading_level?: string | null
  notes?: string | null
}

interface StudentListProps {
  educatorName?: string
}

export function StudentList({ educatorName = "Educator" }: StudentListProps) {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const supabase = createClient()

  const fetchStudents = async () => {
    setLoading(true)
    setError(null)

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

      // Fetch students
      const { data, error: apiError } = await apiClient.GET("/api/students")

      if (apiError) {
        const errorMessage =
          typeof apiError === "object" && apiError !== null
            ? JSON.stringify(apiError)
            : String(apiError)
        throw new Error(errorMessage || "Failed to fetch students")
      }

      if (!data) {
        throw new Error("No data returned from API")
      }

      setStudents(data)
    } catch (err) {
      console.error("Error fetching students:", err)
      setError(err instanceof Error ? err.message : "Failed to load students")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStudents()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="h-[180px] w-full rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStudents}
            className="ml-4"
          >
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  if (students.length === 0) {
    return <EmptyState educatorName={educatorName} />
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {students.map((student) => (
        <StudentCard
          key={student.id}
          id={student.id}
          name={student.name}
          grade_level={student.grade_level}
          reading_level={student.reading_level}
          document_count={0}
        />
      ))}
    </div>
  )
}
