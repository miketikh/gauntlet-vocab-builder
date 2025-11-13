"use client"

import {
  Upload,
  PlayCircle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Clock,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]

interface TimelineEvent {
  id: string
  type: "upload" | "start" | "complete" | "failed" | "retry"
  timestamp: Date
  title: string
  description?: string
  icon: typeof Upload
  iconColor: string
}

interface AnalysisTimelineProps {
  document: DocumentPublic
  className?: string
}

export function AnalysisTimeline({
  document,
  className,
}: AnalysisTimelineProps) {
  // Build timeline events from document data
  const events: TimelineEvent[] = []

  // Upload event
  events.push({
    id: "upload",
    type: "upload",
    timestamp: new Date(document.upload_date),
    title: "Document Uploaded",
    description: `${document.title} uploaded`,
    icon: Upload,
    iconColor: "text-blue-600 dark:text-blue-400",
  })

  // Analysis start (if processing or completed)
  if (document.status === "processing" || document.status === "completed") {
    events.push({
      id: "start",
      type: "start",
      timestamp: new Date(document.upload_date), // In reality would be analysis_started_at
      title: "Analysis Started",
      description: "Processing document content",
      icon: PlayCircle,
      iconColor: "text-purple-600 dark:text-purple-400",
    })
  }

  // Analysis complete
  if (document.status === "completed") {
    events.push({
      id: "complete",
      type: "complete",
      timestamp: new Date(), // In reality would be analysis_completed_at
      title: "Analysis Completed",
      description: "Vocabulary profile generated",
      icon: CheckCircle2,
      iconColor: "text-green-600 dark:text-green-400",
    })
  }

  // Analysis failed
  if (document.status === "failed") {
    events.push({
      id: "failed",
      type: "failed",
      timestamp: new Date(), // In reality would be analysis_failed_at
      title: "Analysis Failed",
      description:
        document.error_message || "An error occurred during analysis",
      icon: XCircle,
      iconColor: "text-red-600 dark:text-red-400",
    })
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[19px] top-2 bottom-2 w-px bg-border" />

        {/* Events */}
        <div className="space-y-6">
          {events.map((event, index) => {
            const Icon = event.icon
            const isLast = index === events.length - 1

            return (
              <div key={event.id} className="relative flex gap-4">
                {/* Icon */}
                <div
                  className={cn(
                    "relative z-10 rounded-full bg-background p-2 border-2",
                    event.iconColor.includes("blue") && "border-blue-600",
                    event.iconColor.includes("purple") && "border-purple-600",
                    event.iconColor.includes("green") && "border-green-600",
                    event.iconColor.includes("red") && "border-red-600"
                  )}
                >
                  <Icon className={cn("h-4 w-4", event.iconColor)} />
                </div>

                {/* Content */}
                <div className="flex-1 pb-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium">{event.title}</h4>
                      {event.description && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {event.description}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
                      <Clock className="h-3 w-3" />
                      {format(event.timestamp, "MMM d, h:mm a")}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Pending state */}
      {document.status === "pending" && (
        <div className="text-xs text-muted-foreground text-center pt-2 border-t">
          Analysis has not started yet
        </div>
      )}

      {/* Processing state */}
      {document.status === "processing" && (
        <div className="text-xs text-muted-foreground text-center pt-2 border-t">
          Analysis in progress...
        </div>
      )}
    </div>
  )
}
