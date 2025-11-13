"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { Upload, FileText, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  completeUploadWorkflow,
  validateFile,
  SUPPORTED_FILE_TYPES,
  type DocumentResponse,
} from "@/lib/upload"

interface UploadDocumentFormProps {
  studentId: number
  token: string
  onSuccess?: (document: DocumentResponse) => void
  onError?: (error: string) => void
}

interface FormData {
  file: FileList | null
  title: string
  subject: string
}

const SUBJECTS = [
  { value: "ela", label: "ELA (English Language Arts)" },
  { value: "math", label: "Math" },
  { value: "science", label: "Science" },
  { value: "social_studies", label: "Social Studies" },
  { value: "other", label: "Other" },
]

export function UploadDocumentForm({
  studentId,
  token,
  onSuccess,
  onError,
}: UploadDocumentFormProps) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset,
  } = useForm<FormData>({
    defaultValues: {
      title: "",
      subject: "",
    },
  })

  const watchedSubject = watch("subject")

  // Handle file selection
  const handleFileChange = (files: FileList | null) => {
    if (!files || files.length === 0) {
      setSelectedFile(null)
      return
    }

    const file = files[0]
    const validation = validateFile(file)

    if (!validation.valid) {
      setError(validation.error || "Invalid file")
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
    setError(null)

    // Auto-fill title with filename if empty
    if (!watch("title")) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "")
      setValue("title", nameWithoutExt)
    }
  }

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files)
    }
  }

  // Handle form submission
  const onSubmit = async (data: FormData) => {
    if (!selectedFile) {
      setError("Please select a file to upload")
      return
    }

    if (!data.subject) {
      setError("Please select a subject")
      return
    }

    setUploading(true)
    setProgress(0)
    setError(null)

    try {
      const document = await completeUploadWorkflow(
        selectedFile,
        studentId,
        data.title,
        data.subject,
        token,
        (p) => setProgress(p)
      )

      // Success!
      onSuccess?.(document)
      reset()
      setSelectedFile(null)
      setProgress(0)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to upload document"
      setError(errorMessage)
      onError?.(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* File Upload Area */}
      <div className="space-y-2">
        <Label htmlFor="file-upload">Document File</Label>
        <div
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"}
            ${selectedFile ? "bg-muted/50" : ""}
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept={Object.values(SUPPORTED_FILE_TYPES).join(",")}
            onChange={(e) => handleFileChange(e.target.files)}
            disabled={uploading}
          />

          {!selectedFile ? (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-muted p-3">
                  <Upload className="h-6 w-6 text-muted-foreground" />
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">
                  Drag and drop your file here, or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports PDF, DOCX, and TXT files up to 50MB
                </p>
              </div>
              <Button
                type="button"
                variant="outline"
                onClick={() => document.getElementById("file-upload")?.click()}
                disabled={uploading}
              >
                Choose File
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-primary/10 p-3">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedFile(null)
                  setError(null)
                }}
                disabled={uploading}
              >
                Change File
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Title Input */}
      <div className="space-y-2">
        <Label htmlFor="title">
          Document Title <span className="text-destructive">*</span>
        </Label>
        <Input
          id="title"
          {...register("title", {
            required: "Title is required",
            minLength: {
              value: 1,
              message: "Title must be at least 1 character",
            },
          })}
          placeholder="e.g., Essay on Climate Change"
          disabled={uploading}
        />
        {errors.title && (
          <p className="text-xs text-destructive">{errors.title.message}</p>
        )}
      </div>

      {/* Subject Selector */}
      <div className="space-y-2">
        <Label htmlFor="subject">
          Subject <span className="text-destructive">*</span>
        </Label>
        <Select
          value={watchedSubject}
          onValueChange={(value) => setValue("subject", value)}
          disabled={uploading}
        >
          <SelectTrigger id="subject">
            <SelectValue placeholder="Select a subject" />
          </SelectTrigger>
          <SelectContent>
            {SUBJECTS.map((subject) => (
              <SelectItem key={subject.value} value={subject.value}>
                {subject.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {!watchedSubject && errors.subject && (
          <p className="text-xs text-destructive">Subject is required</p>
        )}
      </div>

      {/* Progress Bar */}
      {uploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Uploading...</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Submit Button */}
      <div className="flex justify-end gap-3 pt-4">
        <Button
          type="submit"
          disabled={uploading || !selectedFile}
          className="min-w-32"
        >
          {uploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Upload
            </>
          )}
        </Button>
      </div>
    </form>
  )
}
