"use client"

import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, BookOpen } from "lucide-react"

interface StudentCardProps {
  id: number
  name: string
  grade_level: number
  reading_level?: string | null
  document_count?: number
}

export function StudentCard({
  id,
  name,
  grade_level,
  reading_level,
  document_count = 0,
}: StudentCardProps) {
  return (
    <Link href={`/students/${id}`}>
      <Card className="hover:shadow-lg transition-all duration-200 hover:scale-[1.02] cursor-pointer h-full">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-xl font-semibold leading-tight">
              {name}
            </CardTitle>
            <Badge variant="secondary" className="shrink-0">
              Grade {grade_level}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {reading_level && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <BookOpen className="h-4 w-4" />
                <span>{reading_level}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-sm text-muted-foreground pt-2 border-t">
              <FileText className="h-4 w-4" />
              <span>
                {document_count === 0
                  ? "No documents yet"
                  : `${document_count} document${document_count === 1 ? "" : "s"}`}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
