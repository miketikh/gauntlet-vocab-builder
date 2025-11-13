"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { AlertTriangle } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/layout"
import { StudentHeader } from "@/components/students/student-header"
import { StudentSections } from "@/components/students/student-sections"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { createClient } from "@/lib/supabase/client"
import { getAuthenticatedClient } from "@/lib/api-client"

interface Student {
  id: number
  name: string
  grade_level: number
  reading_level?: string | null
  notes?: string | null
  educator_id: number
  created_at: string
  updated_at?: string
}

function StudentDetailSkeleton() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="space-y-4">
          <Skeleton className="h-4 w-64" />
          <Skeleton className="h-8 w-32" />
          <div className="space-y-2">
            <Skeleton className="h-10 w-64" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-6 w-32" />
            </div>
          </div>
        </div>

        {/* Content Skeleton */}
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}

function StudentNotFoundError({ message }: { message: string }) {
  const router = useRouter()

  return (
    <DashboardLayout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="rounded-full bg-destructive/10 p-3">
                <AlertTriangle className="h-8 w-8 text-destructive" />
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-semibold">Student Not Found</h2>
                <p className="text-sm text-muted-foreground">{message}</p>
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  onClick={() => window.location.reload()}
                >
                  Try Again
                </Button>
                <Button onClick={() => router.push("/dashboard")}>
                  Back to Dashboard
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

export default function StudentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [student, setStudent] = useState<Student | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const supabase = createClient()

  useEffect(() => {
    async function fetchStudent() {
      try {
        setLoading(true)
        setError(null)

        // Get the student ID from params
        const studentId = params.id as string

        if (!studentId || isNaN(Number(studentId))) {
          setError("Invalid student ID")
          setLoading(false)
          return
        }

        // Get access token
        const {
          data: { session },
        } = await supabase.auth.getSession()

        if (!session) {
          router.push("/login")
          return
        }

        setAccessToken(session.access_token)

        // Create authenticated API client
        const apiClient = getAuthenticatedClient(session.access_token)

        // Fetch student details
        const { data, error: apiError } = await apiClient.GET(
          "/api/students/{student_id}",
          {
            params: {
              path: {
                student_id: Number(studentId),
              },
            },
          }
        )

        if (apiError) {
          // Handle specific error cases
          const errorMessage =
            typeof apiError === "object" && apiError !== null
              ? JSON.stringify(apiError)
              : String(apiError)

          if (
            errorMessage.includes("not found") ||
            errorMessage.includes("404")
          ) {
            setError(
              "This student does not exist or you do not have permission to view it."
            )
          } else {
            setError(errorMessage || "Failed to load student details")
          }
          setLoading(false)
          return
        }

        if (!data) {
          setError("No student data returned")
          setLoading(false)
          return
        }

        setStudent(data)
      } catch (err) {
        console.error("Error fetching student:", err)
        setError(
          err instanceof Error
            ? err.message
            : "An unexpected error occurred while loading the student"
        )
      } finally {
        setLoading(false)
      }
    }

    fetchStudent()
  }, [params.id, router, supabase.auth])

  const handleDocumentUploaded = () => {
    // Callback for when a document is uploaded
    // In Story 2.5, this will refresh the document list
    console.log("Document uploaded successfully!")
  }

  // Loading state
  if (loading) {
    return <StudentDetailSkeleton />
  }

  // Error state
  if (error || !student) {
    return (
      <StudentNotFoundError
        message={
          error ||
          "This student does not exist or you do not have permission to view it."
        }
      />
    )
  }

  // Success state
  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Student Header */}
        <StudentHeader
          studentName={student.name}
          gradeLevel={student.grade_level}
          readingLevel={student.reading_level}
        />

        {/* Student Sections */}
        {accessToken && (
          <StudentSections
            studentId={student.id}
            token={accessToken}
            onDocumentUploaded={handleDocumentUploaded}
          />
        )}
      </div>
    </DashboardLayout>
  )
}
