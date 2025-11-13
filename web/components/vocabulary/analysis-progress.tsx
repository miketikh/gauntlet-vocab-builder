"use client"

import { CheckCircle2, Circle, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

interface AnalysisStep {
  id: number
  label: string
  description: string
}

const ANALYSIS_STEPS: AnalysisStep[] = [
  {
    id: 1,
    label: "Downloading",
    description: "Retrieving document from storage",
  },
  {
    id: 2,
    label: "Extracting",
    description: "Extracting text from document",
  },
  {
    id: 3,
    label: "Processing",
    description: "Tokenizing and lemmatizing words",
  },
  {
    id: 4,
    label: "Analyzing",
    description: "Mapping vocabulary to grade levels",
  },
  {
    id: 5,
    label: "Complete",
    description: "Analysis finished successfully",
  },
]

interface AnalysisProgressProps {
  currentStep?: number // 1-5, if not provided shows indeterminate progress
  className?: string
}

export function AnalysisProgress({
  currentStep,
  className,
}: AnalysisProgressProps) {
  // Calculate progress percentage
  const progressPercentage = currentStep
    ? ((currentStep - 1) / (ANALYSIS_STEPS.length - 1)) * 100
    : 0

  return (
    <div className={cn("space-y-6", className)}>
      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Analysis Progress</span>
          {currentStep && (
            <span className="font-medium">
              {Math.round(progressPercentage)}%
            </span>
          )}
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {ANALYSIS_STEPS.map((step) => {
          const isComplete = currentStep ? step.id < currentStep : false
          const isCurrent = step.id === currentStep
          const isPending = currentStep ? step.id > currentStep : true

          return (
            <div
              key={step.id}
              className={cn(
                "flex items-start gap-3 transition-opacity",
                isPending && !isCurrent && "opacity-40"
              )}
            >
              {/* Icon */}
              <div className="shrink-0 mt-0.5">
                {isComplete && (
                  <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                )}
                {isCurrent && (
                  <Loader2 className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin" />
                )}
                {isPending && !isCurrent && (
                  <Circle className="h-5 w-5 text-muted-foreground" />
                )}
              </div>

              {/* Text */}
              <div className="flex-1 min-w-0">
                <p
                  className={cn(
                    "text-sm font-medium",
                    isCurrent && "text-blue-600 dark:text-blue-400",
                    isComplete && "text-green-600 dark:text-green-400"
                  )}
                >
                  {step.label}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {step.description}
                </p>
              </div>

              {/* Step number */}
              <div
                className={cn(
                  "shrink-0 text-xs font-medium text-muted-foreground",
                  isCurrent && "text-blue-600 dark:text-blue-400"
                )}
              >
                {step.id}/{ANALYSIS_STEPS.length}
              </div>
            </div>
          )
        })}
      </div>

      {/* Estimated time (optional - could be enhanced with actual estimates) */}
      {currentStep && currentStep < ANALYSIS_STEPS.length && (
        <div className="text-xs text-muted-foreground text-center pt-2 border-t">
          Analysis in progress... This usually takes 10-30 seconds
        </div>
      )}
    </div>
  )
}
