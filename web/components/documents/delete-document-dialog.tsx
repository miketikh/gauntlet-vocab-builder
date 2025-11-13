"use client"

import { useState } from "react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { toast } from "sonner"
import { getAuthenticatedClient } from "@/lib/api-client"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]

interface DeleteDocumentDialogProps {
  document: DocumentPublic
  token: string
  open: boolean
  onOpenChange: (open: boolean) => void
  onDeleteSuccess: () => void
}

export function DeleteDocumentDialog({
  document,
  token,
  open,
  onOpenChange,
  onDeleteSuccess,
}: DeleteDocumentDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    setIsDeleting(true)

    try {
      const client = getAuthenticatedClient(token)
      const { data, error } = await client.DELETE(
        "/api/documents/{document_id}",
        {
          params: {
            path: { document_id: document.id },
          },
        }
      )

      if (error) {
        console.error("Delete error:", error)
        const errorMessage =
          error.detail?.[0]?.msg ||
          "An error occurred while deleting the document"
        toast.error("Failed to delete document", {
          description: errorMessage,
        })
        return
      }

      // Success
      toast.success("Document deleted", {
        description: data?.message || `"${document.title}" has been deleted`,
      })

      // Close dialog and notify parent
      onOpenChange(false)
      onDeleteSuccess()
    } catch (err) {
      console.error("Unexpected error:", err)
      toast.error("Failed to delete document", {
        description: "An unexpected error occurred",
      })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete document?</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete{" "}
            <strong>&quot;{document.title}&quot;</strong>? This action cannot be
            undone. The document will be permanently removed from storage.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault()
              handleDelete()
            }}
            disabled={isDeleting}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
