"use client"

import { useAuth } from "@/contexts/auth-context"
import { DashboardLayout } from "@/components/dashboard/layout"
import { StudentList } from "@/components/students/student-list"
import { AddStudentDialog } from "@/components/students/add-student-dialog"
import { Loader2, UserPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function DashboardPage() {
  const { educator, loading } = useAuth()
  const [refreshKey, setRefreshKey] = useState(0)

  const handleStudentCreated = () => {
    // Trigger refresh by updating key
    setRefreshKey((prev) => prev + 1)
  }

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
            <h1 className="text-3xl font-bold tracking-tight">My Students</h1>
            <p className="text-muted-foreground">
              Manage your student roster and track their vocabulary development
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
        <StudentList
          key={refreshKey}
          educatorName={educator?.name || "Educator"}
        />
      </div>
    </DashboardLayout>
  )
}
