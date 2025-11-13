"use client"

import { useAuth } from "@/contexts/auth-context"
import { DashboardLayout } from "@/components/dashboard/layout"
import { EmptyState } from "@/components/dashboard/empty-state"
import { Loader2 } from "lucide-react"

export default function DashboardPage() {
  const { educator, loading } = useAuth()

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
      <EmptyState educatorName={educator?.name || "Educator"} />
    </DashboardLayout>
  )
}
