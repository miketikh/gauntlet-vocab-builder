"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface ChallengingWord {
  word: string
  grade_level: number
  definition?: string | null
  frequency: number
}

interface ChallengingWordsListProps {
  words: ChallengingWord[]
  studentGradeLevel: number
}

export function ChallengingWordsList({
  words,
  studentGradeLevel,
}: ChallengingWordsListProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  // Sort by grade level descending, then by frequency
  const sortedWords = [...words]
    .sort((a, b) => {
      if (b.grade_level !== a.grade_level) {
        return b.grade_level - a.grade_level
      }
      return b.frequency - a.frequency
    })
    .slice(0, 20) // Limit to top 20

  if (sortedWords.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Challenging Words</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No challenging words found above grade level.
          </p>
        </CardContent>
      </Card>
    )
  }

  const getDifficultyBadge = (gradeLevel: number) => {
    const diff = gradeLevel - studentGradeLevel
    if (diff === 1) {
      return (
        <Badge
          variant="outline"
          className="bg-amber-100 text-amber-900 dark:bg-amber-900 dark:text-amber-100"
        >
          +1 Grade
        </Badge>
      )
    } else if (diff === 2) {
      return (
        <Badge
          variant="outline"
          className="bg-orange-100 text-orange-900 dark:bg-orange-900 dark:text-orange-100"
        >
          +2 Grades
        </Badge>
      )
    } else {
      return (
        <Badge
          variant="outline"
          className="bg-red-100 text-red-900 dark:bg-red-900 dark:text-red-100"
        >
          +{diff} Grades
        </Badge>
      )
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">Challenging Words</CardTitle>
            <Badge variant="secondary">{sortedWords.length}</Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <>
                <ChevronDown className="h-4 w-4 mr-1" />
                Collapse
              </>
            ) : (
              <>
                <ChevronRight className="h-4 w-4 mr-1" />
                Expand
              </>
            )}
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          Words above the student&apos;s grade level (showing top 20)
        </p>
      </CardHeader>
      {isExpanded && (
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Word</TableHead>
                  <TableHead className="w-[120px]">Grade Level</TableHead>
                  <TableHead className="w-[100px]">Frequency</TableHead>
                  <TableHead>Definition</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedWords.map((word, index) => (
                  <TableRow key={`${word.word}-${index}`}>
                    <TableCell className="font-medium">{word.word}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{word.grade_level}</span>
                        {getDifficultyBadge(word.grade_level)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{word.frequency}x</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {word.definition || "No definition available"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      )}
    </Card>
  )
}
