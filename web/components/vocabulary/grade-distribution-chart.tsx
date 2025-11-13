"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface GradeDistributionChartProps {
  gradeDistribution: Record<string, number>
  studentGradeLevel: number
}

export function GradeDistributionChart({
  gradeDistribution,
  studentGradeLevel,
}: GradeDistributionChartProps) {
  // Convert grade distribution to array and sort by grade
  const distributionArray = Object.entries(gradeDistribution)
    .map(([grade, percentage]) => ({
      grade: parseInt(grade),
      percentage,
    }))
    .sort((a, b) => a.grade - b.grade)

  // Find max percentage for scaling
  const maxPercentage = Math.max(...distributionArray.map((d) => d.percentage))

  // Color coding based on student's grade level
  const getBarColor = (grade: number) => {
    if (grade < studentGradeLevel) {
      return "bg-green-500" // Below grade level - easier
    } else if (grade === studentGradeLevel) {
      return "bg-blue-500" // At grade level
    } else if (grade === studentGradeLevel + 1) {
      return "bg-amber-500" // One above - challenging
    } else {
      return "bg-red-500" // Well above - very challenging
    }
  }

  const getBarLightColor = (grade: number) => {
    if (grade < studentGradeLevel) {
      return "bg-green-100 dark:bg-green-900/20"
    } else if (grade === studentGradeLevel) {
      return "bg-blue-100 dark:bg-blue-900/20"
    } else if (grade === studentGradeLevel + 1) {
      return "bg-amber-100 dark:bg-amber-900/20"
    } else {
      return "bg-red-100 dark:bg-red-900/20"
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Grade Level Distribution</CardTitle>
          <Badge variant="outline">Student Grade: {studentGradeLevel}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Legend */}
          <div className="flex flex-wrap gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-green-500" />
              <span className="text-muted-foreground">Below grade</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-blue-500" />
              <span className="text-muted-foreground">At grade</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-amber-500" />
              <span className="text-muted-foreground">Challenging</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-red-500" />
              <span className="text-muted-foreground">Very challenging</span>
            </div>
          </div>

          {/* Bar chart */}
          <div className="space-y-3">
            {distributionArray.map(({ grade, percentage }) => {
              const heightPercentage = (percentage / maxPercentage) * 100

              return (
                <div key={grade} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-medium w-16">Grade {grade}</span>
                      {grade === studentGradeLevel && (
                        <Badge variant="secondary" className="text-xs">
                          Current
                        </Badge>
                      )}
                    </div>
                    <span className="text-muted-foreground">
                      {(percentage * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div
                    className={`w-full h-8 rounded-md ${getBarLightColor(
                      grade
                    )} relative overflow-hidden`}
                  >
                    <div
                      className={`h-full ${getBarColor(grade)} transition-all`}
                      style={{ width: `${heightPercentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>

          {/* Summary */}
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              {distributionArray.filter((d) => d.grade < studentGradeLevel)
                .length > 0 && (
                <>
                  {(
                    distributionArray
                      .filter((d) => d.grade < studentGradeLevel)
                      .reduce((sum, d) => sum + d.percentage, 0) * 100
                  ).toFixed(0)}
                  % below grade level,{" "}
                </>
              )}
              {(
                distributionArray
                  .filter((d) => d.grade > studentGradeLevel)
                  .reduce((sum, d) => sum + d.percentage, 0) * 100
              ).toFixed(0)}
              % above grade level
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
