"use client"

import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function DashboardPage() {
  const { educator, signOut, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Vocabulary Builder
            </h1>
            <p className="text-sm text-gray-600">Educator Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {educator?.name}
              </p>
              <p className="text-xs text-gray-600">{educator?.email}</p>
            </div>
            <Button variant="outline" onClick={signOut}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Welcome, {educator?.name}!</CardTitle>
            <CardDescription>
              Your personalized vocabulary recommendation dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No students yet
              </h3>
              <p className="text-gray-600 mb-6">
                Add your first student to get started with personalized
                vocabulary recommendations.
              </p>
              <Button>Add New Student</Button>
            </div>

            {educator?.school && (
              <div className="mt-6 pt-6 border-t">
                <p className="text-sm text-gray-600">
                  School: <span className="font-medium">{educator.school}</span>
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
