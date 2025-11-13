"use client"

import { BookOpen, ListChecks, TrendingUp, HelpCircle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface StatsCardsProps {
  totalWords: number
  uniqueWords: number
  averageGradeLevel: number
  unmappedPercentage: number
}

export function StatsCards({
  totalWords,
  uniqueWords,
  averageGradeLevel,
  unmappedPercentage,
}: StatsCardsProps) {
  const stats = [
    {
      title: "Total Words",
      value: totalWords.toLocaleString(),
      icon: BookOpen,
      description: "Words in document",
      color: "text-blue-600 dark:text-blue-400",
      bgColor: "bg-blue-100 dark:bg-blue-900",
    },
    {
      title: "Unique Words",
      value: uniqueWords.toLocaleString(),
      icon: ListChecks,
      description: "Distinct vocabulary",
      color: "text-green-600 dark:text-green-400",
      bgColor: "bg-green-100 dark:bg-green-900",
    },
    {
      title: "Grade Level",
      value: averageGradeLevel.toFixed(1),
      icon: TrendingUp,
      description: "Average difficulty",
      color: "text-purple-600 dark:text-purple-400",
      bgColor: "bg-purple-100 dark:bg-purple-900",
    },
    {
      title: "Unknown Words",
      value: `${(unmappedPercentage * 100).toFixed(1)}%`,
      icon: HelpCircle,
      description: "Not in grade lists",
      color: "text-amber-600 dark:text-amber-400",
      bgColor: "bg-amber-100 dark:bg-amber-900",
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title}>
            <CardContent className="pt-6">
              <div className="flex flex-col space-y-3">
                <div className="flex items-center justify-between">
                  <div className={`rounded-full ${stat.bgColor} p-2`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {stat.description}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
