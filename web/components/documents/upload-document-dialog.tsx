"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Upload } from "lucide-react"
import { UploadDocumentForm } from "./upload-document-form"
import { toast } from "sonner"
import type { DocumentResponse } from "@/lib/upload"

interface UploadDocumentDialogProps {
  studentId: number
  token: string
  onUploadComplete?: () => void
  trigger?: React.ReactNode
}

export function UploadDocumentDialog({
  studentId,
  token,
  onUploadComplete,
  trigger,
}: UploadDocumentDialogProps) {
  const [open, setOpen] = useState(false)

  const handleSuccess = (document: DocumentResponse) => {
    toast.success("Document uploaded successfully", {
      description: `"${document.title}" has been uploaded and is ready for analysis.`,
    })
    setOpen(false)
    onUploadComplete?.()
  }

  const handleError = (error: string) => {
    toast.error("Upload failed", {
      description: error,
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="gap-2">
            <Upload className="h-4 w-4" />
            Upload Document
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Upload Student Document</DialogTitle>
          <DialogDescription>
            Upload essays, transcripts, or other writing samples for vocabulary
            analysis. Supported formats: PDF, DOCX, TXT (max 50MB).
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <UploadDocumentForm
            studentId={studentId}
            token={token}
            onSuccess={handleSuccess}
            onError={handleError}
          />
        </div>
      </DialogContent>
    </Dialog>
  )
}
