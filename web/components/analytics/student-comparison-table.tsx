"use client"

import { useState, useMemo } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  StarIcon,
  AlertTriangleIcon,
  TrendingUpIcon,
  TrendingDownIcon,
} from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { useRouter } from "next/navigation"

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

interface GradeDistribution {
  below_grade: number
  at_grade: number
  above_grade: number
}

interface StudentComparisonTableProps {
  students: StudentSummary[]
  gradeDistribution: GradeDistribution
  loading?: boolean
}

type SortField = "name" | "grade_level" | "progress" | "adoption_rate"
type FilterType =
  | "all"
  | "above_grade"
  | "at_grade"
  | "below_grade"
  | "needs_support"
  | "top_performers"

export function StudentComparisonTable({
  students,
  gradeDistribution,
  loading = false,
}: StudentComparisonTableProps) {
  const router = useRouter()
  const [sortField, setSortField] = useState<SortField>("name")
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc")
  const [filter, setFilter] = useState<FilterType>("all")

  const filteredAndSortedStudents = useMemo(() => {
    let filtered = [...students]

    // Apply filter
    switch (filter) {
      case "above_grade":
        filtered = filtered.filter(
          (s) =>
            s.current_grade_level &&
            s.current_grade_level - s.actual_grade > 0.5
        )
        break
      case "at_grade":
        filtered = filtered.filter(
          (s) =>
            s.current_grade_level &&
            Math.abs(s.current_grade_level - s.actual_grade) <= 0.5
        )
        break
      case "below_grade":
        filtered = filtered.filter(
          (s) =>
            s.current_grade_level &&
            s.current_grade_level - s.actual_grade < -0.5
        )
        break
      case "needs_support":
        filtered = filtered.filter((s) => s.needs_support)
        break
      case "top_performers":
        filtered = filtered.filter((s) => s.is_top_performer)
        break
    }

    // Apply sort
    filtered.sort((a, b) => {
      let comparison = 0

      switch (sortField) {
        case "name":
          comparison = a.name.localeCompare(b.name)
          break
        case "grade_level":
          comparison =
            (a.current_grade_level || 0) - (b.current_grade_level || 0)
          break
        case "progress":
          comparison = a.grade_level_change - b.grade_level_change
          break
        case "adoption_rate":
          comparison = a.adoption_rate - b.adoption_rate
          break
      }

      return sortDirection === "asc" ? comparison : -comparison
    })

    return filtered
  }, [students, sortField, sortDirection, filter])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const getTrendIcon = (trend: string) => {
    if (trend === "improving") {
      return <TrendingUpIcon className="h-4 w-4 text-green-600" />
    } else if (trend === "declining") {
      return <TrendingDownIcon className="h-4 w-4 text-red-600" />
    }
    return <MinusIcon className="h-4 w-4 text-gray-400" />
  }

  const getGradeBadgeColor = (
    currentGrade: number | null,
    actualGrade: number
  ): "default" | "secondary" | "destructive" => {
    if (!currentGrade) return "secondary"
    const diff = currentGrade - actualGrade
    if (diff > 0.5) return "default" // green for above grade
    if (diff < -0.5) return "destructive" // red for below grade
    return "secondary" // gray for at grade
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "No activity"
    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    )

    if (diffDays === 0) return "Today"
    if (diffDays === 1) return "Yesterday"
    if (diffDays < 7) return `${diffDays} days ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Student Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (students.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Student Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No students to display. Add students to see comparison data.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Student Comparison</CardTitle>
          <Select
            value={filter}
            onValueChange={(value) => setFilter(value as FilterType)}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filter students" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">
                All Students ({students.length})
              </SelectItem>
              <SelectItem value="above_grade">
                Above Grade ({gradeDistribution.above_grade})
              </SelectItem>
              <SelectItem value="at_grade">
                At Grade ({gradeDistribution.at_grade})
              </SelectItem>
              <SelectItem value="below_grade">
                Below Grade ({gradeDistribution.below_grade})
              </SelectItem>
              <SelectItem value="top_performers">
                Top Performers (
                {students.filter((s) => s.is_top_performer).length})
              </SelectItem>
              <SelectItem value="needs_support">
                Needs Support ({students.filter((s) => s.needs_support).length})
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[200px]">
                  <button
                    className="flex items-center gap-1 hover:text-foreground"
                    onClick={() => handleSort("name")}
                  >
                    Student
                    {sortField === "name" &&
                      (sortDirection === "asc" ? (
                        <ArrowUpIcon className="h-4 w-4" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4" />
                      ))}
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    className="flex items-center gap-1 hover:text-foreground"
                    onClick={() => handleSort("grade_level")}
                  >
                    Grade Level
                    {sortField === "grade_level" &&
                      (sortDirection === "asc" ? (
                        <ArrowUpIcon className="h-4 w-4" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4" />
                      ))}
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    className="flex items-center gap-1 hover:text-foreground"
                    onClick={() => handleSort("progress")}
                  >
                    Progress
                    {sortField === "progress" &&
                      (sortDirection === "asc" ? (
                        <ArrowUpIcon className="h-4 w-4" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4" />
                      ))}
                  </button>
                </TableHead>
                <TableHead>
                  <button
                    className="flex items-center gap-1 hover:text-foreground"
                    onClick={() => handleSort("adoption_rate")}
                  >
                    Adoption Rate
                    {sortField === "adoption_rate" &&
                      (sortDirection === "asc" ? (
                        <ArrowUpIcon className="h-4 w-4" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4" />
                      ))}
                  </button>
                </TableHead>
                <TableHead>Last Activity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedStudents.map((student) => (
                <TableRow
                  key={student.student_id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => router.push(`/students/${student.student_id}`)}
                >
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      {student.is_top_performer && (
                        <StarIcon className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                      )}
                      {student.needs_support && (
                        <AlertTriangleIcon className="h-4 w-4 text-red-500" />
                      )}
                      {student.name}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={getGradeBadgeColor(
                          student.current_grade_level,
                          student.actual_grade
                        )}
                      >
                        {student.current_grade_level
                          ? student.current_grade_level.toFixed(1)
                          : "N/A"}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        (Grade {student.actual_grade})
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getTrendIcon(student.progress_trend)}
                      <span
                        className={`text-sm ${
                          student.grade_level_change > 0
                            ? "text-green-600"
                            : student.grade_level_change < 0
                              ? "text-red-600"
                              : "text-gray-600"
                        }`}
                      >
                        {student.grade_level_change > 0 ? "+" : ""}
                        {student.grade_level_change.toFixed(1)}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-medium">
                        {Math.round(student.adoption_rate * 100)}%
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ({student.adopted_recommendations}/
                        {student.total_recommendations})
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(student.last_activity)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        {filteredAndSortedStudents.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8">
            No students match the selected filter.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
