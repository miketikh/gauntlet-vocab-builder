"use client"

import { useState } from "react"
import { UserPlus } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { AddStudentForm } from "./add-student-form"
import { toast } from "sonner"

interface Student {
  id: number
  name: string
  grade_level: number
  reading_level?: string | null
  notes?: string | null
}

interface AddStudentDialogProps {
  onSuccess?: (student: Student) => void
  trigger?: React.ReactNode
}

export function AddStudentDialog({
  onSuccess,
  trigger,
}: AddStudentDialogProps) {
  const [open, setOpen] = useState(false)

  const handleSuccess = (student: Student) => {
    // Close dialog
    setOpen(false)

    // Show success toast
    toast.success("Student created successfully!", {
      description: `${student.name} has been added to your roster.`,
    })

    // Call parent success handler
    onSuccess?.(student)
  }

  const handleCancel = () => {
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button size="lg">
            <UserPlus className="mr-2 h-5 w-5" />
            Add Your First Student
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Add New Student</DialogTitle>
          <DialogDescription>
            Create a new student profile to track their vocabulary development.
            All fields marked as optional can be filled in later.
          </DialogDescription>
        </DialogHeader>
        <AddStudentForm onSuccess={handleSuccess} onCancel={handleCancel} />
      </DialogContent>
    </Dialog>
  )
}
