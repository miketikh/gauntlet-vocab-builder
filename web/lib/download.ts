/**
 * Download utilities for document files
 */

import { getAuthenticatedClient } from "@/lib/api-client"
import { toast } from "sonner"

/**
 * Download a document by requesting a presigned URL and opening it
 *
 * @param documentId - ID of the document (not used in current implementation, kept for future)
 * @param s3Key - S3 key of the document file
 * @param filename - Suggested filename for download
 * @param token - JWT authentication token
 */
export async function downloadDocument(
  documentId: number,
  s3Key: string,
  filename: string,
  token: string
): Promise<void> {
  try {
    // Create authenticated API client
    const apiClient = getAuthenticatedClient(token)

    // Request presigned download URL from backend
    const { data, error } = await apiClient.POST("/api/s3/download-url", {
      body: {
        s3_key: s3Key,
      },
    })

    if (error) {
      console.error("Error getting download URL:", error)
      toast.error("Failed to download document", {
        description:
          typeof error === "object" && error !== null && "detail" in error
            ? String(error.detail)
            : "Unable to generate download link",
      })
      return
    }

    if (!data || !data.presigned_url) {
      toast.error("Failed to download document", {
        description: "No download URL returned",
      })
      return
    }

    // Open the presigned URL in a new tab to trigger download
    // The browser will handle the download based on Content-Disposition header
    const link = document.createElement("a")
    link.href = data.presigned_url
    link.download = filename // Suggested filename
    link.target = "_blank"
    link.rel = "noopener noreferrer"

    // Trigger the download
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    toast.success("Download started", {
      description: `Downloading ${filename}`,
    })
  } catch (err) {
    console.error("Unexpected error downloading document:", err)
    toast.error("Failed to download document", {
      description:
        err instanceof Error ? err.message : "An unexpected error occurred",
    })
  }
}

/**
 * Get file extension from filename
 */
export function getFileExtension(filename: string): string {
  const parts = filename.split(".")
  const lastPart = parts[parts.length - 1]
  return parts.length > 1 && lastPart ? lastPart.toLowerCase() : ""
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes?: number): string {
  if (!bytes || bytes === 0) return "Unknown size"

  const units = ["B", "KB", "MB", "GB"]
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex] || "B"}`
}
