"use client"

import { CheckCircle2, Clock, Loader2, XCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { components } from "@/types/api"

type DocumentStatus = components["schemas"]["DocumentStatus"]

interface DocumentStatusBadgeProps {
  status: DocumentStatus
  className?: string
}

export function DocumentStatusBadge({
  status,
  className,
}: DocumentStatusBadgeProps) {
  const statusConfig = {
    pending: {
      label: "Pending",
      icon: Clock,
      className:
        "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
      animated: false,
    },
    processing: {
      label: "Processing",
      icon: Loader2,
      className:
        "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300",
      animated: true,
    },
    completed: {
      label: "Completed",
      icon: CheckCircle2,
      className:
        "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300",
      animated: false,
    },
    failed: {
      label: "Failed",
      icon: XCircle,
      className: "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300",
      animated: false,
    },
  }

  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <Badge
      variant="outline"
      className={cn("border-transparent gap-1", config.className, className)}
    >
      <Icon
        className={cn("h-3 w-3", config.animated && "animate-spin")}
        aria-hidden="true"
      />
      {config.label}
    </Badge>
  )
}
