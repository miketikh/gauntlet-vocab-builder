"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { GraduationCap } from "lucide-react"
import { AddStudentDialog } from "@/components/students/add-student-dialog"

interface EmptyStateProps {
  educatorName: string
}

export function EmptyState({ educatorName }: EmptyStateProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Welcome, {educatorName}!</CardTitle>
          <CardDescription>
            Your personalized vocabulary recommendation dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <div className="rounded-full bg-primary/10 p-6 mb-6">
              <GraduationCap className="h-12 w-12 text-primary" />
            </div>

            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No students yet
            </h3>

            <p className="text-gray-600 mb-2 max-w-md">
              Add your first student to get started with personalized vocabulary
              recommendations.
            </p>

            <p className="text-sm text-gray-500 mb-8 max-w-lg">
              Once you add a student, you&apos;ll be able to upload their
              writing samples, analyze their current vocabulary level, and
              receive AI-powered recommendations to help them improve their
              academic language skills.
            </p>

            <AddStudentDialog />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              How it works
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-1">1. Add Students</div>
            <p className="text-sm text-muted-foreground">
              Create student profiles with their grade level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Next step
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-1">2. Upload Work</div>
            <p className="text-sm text-muted-foreground">
              Upload student essays and writing samples
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Get results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-1">3. Get Insights</div>
            <p className="text-sm text-muted-foreground">
              Receive AI-powered vocabulary recommendations
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
