"use client"

import { useEffect, useRef, useState } from "react"
import { getAuthenticatedClient } from "@/lib/api-client"
import type { components } from "@/types/api"

type DocumentPublic = components["schemas"]["DocumentPublic"]
type DocumentStatus = components["schemas"]["DocumentStatus"]

interface UseDocumentPollingOptions {
  documentId: string | number
  token: string
  enabled?: boolean
  interval?: number // milliseconds, default 3000
  onStatusChange?: (status: DocumentStatus, document: DocumentPublic) => void
}

/**
 * Custom hook for polling document status
 * Automatically polls when status is 'processing'
 * Stops polling when status is 'completed' or 'failed'
 */
export function useDocumentPolling({
  documentId,
  token,
  enabled = true,
  interval = 3000,
  onStatusChange,
}: UseDocumentPollingOptions) {
  const [document, setDocument] = useState<DocumentPublic | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const previousStatusRef = useRef<DocumentStatus | null>(null)

  const fetchDocument = async () => {
    try {
      const apiClient = getAuthenticatedClient(token)
      const { data, error: apiError } = await apiClient.GET(
        "/api/documents/{document_id}",
        {
          params: {
            path: {
              document_id: Number(documentId),
            },
          },
        }
      )

      if (apiError) {
        setError("Failed to fetch document status")
        return
      }

      if (data) {
        setDocument(data)
        setError(null)

        // Check if status changed
        if (
          previousStatusRef.current !== null &&
          previousStatusRef.current !== data.status
        ) {
          onStatusChange?.(data.status, data)
        }
        previousStatusRef.current = data.status
      }
    } catch (err) {
      console.error("Error polling document:", err)
      setError(err instanceof Error ? err.message : "An error occurred")
    }
  }

  useEffect(() => {
    if (!enabled || !documentId || !token) {
      return
    }

    // Initial fetch
    fetchDocument()

    // Cleanup function
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [documentId, token, enabled])

  // Set up polling based on document status
  useEffect(() => {
    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // Only poll if enabled and status is processing
    if (enabled && document?.status === "processing") {
      setIsPolling(true)
      intervalRef.current = setInterval(fetchDocument, interval)
    } else {
      setIsPolling(false)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [enabled, document?.status, interval])

  return {
    document,
    isPolling,
    error,
    refetch: fetchDocument,
  }
}
