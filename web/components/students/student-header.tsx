"use client"

import { ArrowLeft, Edit } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

interface StudentHeaderProps {
  studentName: string
  gradeLevel: number
  readingLevel?: string | null
}

export function StudentHeader({
  studentName,
  gradeLevel,
  readingLevel,
}: StudentHeaderProps) {
  return (
    <div className="space-y-4">
      {/* Breadcrumb Navigation */}
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Students</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{studentName}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Back Button */}
      <div>
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Student Info Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">{studentName}</h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="text-sm">
              Grade {gradeLevel}
            </Badge>
            {readingLevel && (
              <Badge variant="secondary" className="text-sm">
                {readingLevel}
              </Badge>
            )}
          </div>
        </div>

        {/* Edit Button - Placeholder for future functionality */}
        <Button
          variant="outline"
          size="sm"
          className="gap-2 cursor-not-allowed opacity-50"
          disabled
        >
          <Edit className="h-4 w-4" />
          Edit Student
        </Button>
      </div>
    </div>
  )
}
