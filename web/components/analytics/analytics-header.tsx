"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, TrendingUp, BookOpen, Award } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface AnalyticsHeaderProps {
  totalStudents: number
  averageGradeLevel: number | null
  averageAdoptionRate: number
  totalDocuments: number
  loading?: boolean
}

export function AnalyticsHeader({
  totalStudents,
  averageGradeLevel,
  averageAdoptionRate,
  totalDocuments,
  loading = false,
}: AnalyticsHeaderProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-[100px]" />
              <Skeleton className="h-4 w-4 rounded" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-[60px] mb-1" />
              <Skeleton className="h-3 w-[120px]" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const stats = [
    {
      title: "Total Students",
      value: totalStudents,
      description: "in your roster",
      icon: Users,
      color: "text-blue-600",
    },
    {
      title: "Class Average",
      value: averageGradeLevel ? `${averageGradeLevel.toFixed(1)}` : "N/A",
      description: "vocabulary grade level",
      icon: TrendingUp,
      color: "text-green-600",
    },
    {
      title: "Adoption Rate",
      value: `${Math.round(averageAdoptionRate * 100)}%`,
      description: "recommendations adopted",
      icon: Award,
      color: "text-purple-600",
    },
    {
      title: "Documents Analyzed",
      value: totalDocuments,
      description: "across all students",
      icon: BookOpen,
      color: "text-orange-600",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
