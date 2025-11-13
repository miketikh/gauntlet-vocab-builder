"use client"

import {
  FileText,
  Upload,
  BarChart3,
  Lightbulb,
  AlertCircle,
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export function StudentSections() {
  return (
    <div className="space-y-6">
      {/* Documents Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Uploaded Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-muted p-3 mb-4">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              No documents uploaded yet
            </h3>
            <p className="text-sm text-muted-foreground mb-6 max-w-md">
              Upload student essays, transcripts, or other writing samples to
              begin vocabulary analysis and get personalized recommendations.
            </p>
            <Button disabled className="gap-2 cursor-not-allowed opacity-50">
              <Upload className="h-4 w-4" />
              Upload Document
            </Button>
            <p className="text-xs text-muted-foreground mt-3">
              Document upload coming in Story 2.4
            </p>
          </div>

          {/* Grid ready for document cards - hidden when empty */}
          <div className="hidden grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Document cards will be rendered here */}
          </div>
        </CardContent>
      </Card>

      {/* Vocabulary Profile Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Vocabulary Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-3 mb-4">
              <BarChart3 className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              Upload a document to see vocabulary analysis
            </h3>
            <p className="text-sm text-muted-foreground max-w-md">
              Once documents are uploaded, you&apos;ll see detailed vocabulary
              statistics, word frequency analysis, and reading level metrics
              here.
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <AlertCircle className="h-3 w-3" />
              <span>Analysis features coming in Story 3.5</span>
            </div>
          </div>

          {/* Placeholder for future charts and stats */}
          <div className="hidden">
            {/* Vocabulary charts and metrics will be rendered here */}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Personalized Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-amber-100 dark:bg-amber-900 p-3 mb-4">
              <Lightbulb className="h-8 w-8 text-amber-600 dark:text-amber-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              Recommendations will appear after document analysis
            </h3>
            <p className="text-sm text-muted-foreground max-w-md">
              After analyzing uploaded documents, the system will generate
              personalized vocabulary recommendations, learning resources, and
              practice activities tailored to this student&apos;s needs.
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <AlertCircle className="h-3 w-3" />
              <span>Recommendation engine coming in Story 4.4</span>
            </div>
          </div>

          {/* Placeholder for recommendation cards */}
          <div className="hidden grid-cols-1 md:grid-cols-2 gap-4">
            {/* Recommendation cards will be rendered here */}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
