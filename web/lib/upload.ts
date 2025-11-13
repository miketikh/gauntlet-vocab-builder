/**
 * File Upload Utilities
 * Handles direct S3 uploads and document metadata creation
 */

/**
 * Supported file types for document upload
 */
export const SUPPORTED_FILE_TYPES = {
  "application/pdf": ".pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    ".docx",
  "text/plain": ".txt",
} as const

export const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB in bytes

export type SupportedFileType = keyof typeof SUPPORTED_FILE_TYPES

/**
 * Validate file type and size
 */
export function validateFile(file: File): { valid: boolean; error?: string } {
  // Check file type
  if (!Object.keys(SUPPORTED_FILE_TYPES).includes(file.type)) {
    const acceptedExtensions = Object.values(SUPPORTED_FILE_TYPES).join(", ")
    return {
      valid: false,
      error: `Invalid file type. Please upload a ${acceptedExtensions} file.`,
    }
  }

  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    const maxSizeMB = MAX_FILE_SIZE / (1024 * 1024)
    return {
      valid: false,
      error: `File is too large. Maximum size is ${maxSizeMB}MB.`,
    }
  }

  return { valid: true }
}

/**
 * Get file type enum value from MIME type
 */
export function getFileTypeFromMime(mimeType: string): string {
  const extension = SUPPORTED_FILE_TYPES[mimeType as SupportedFileType]
  if (!extension) {
    throw new Error(`Unsupported file type: ${mimeType}`)
  }
  return extension.replace(".", "") // Return 'pdf', 'docx', or 'txt'
}

/**
 * Upload file directly to S3 using presigned URL
 *
 * @param file - File to upload
 * @param presignedUrl - Presigned URL from backend
 * @param onProgress - Optional progress callback (0-100)
 * @returns Promise that resolves when upload completes
 */
export async function uploadToS3(
  file: File,
  presignedUrl: string,
  onProgress?: (progress: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener("progress", (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100
          onProgress(Math.round(percentComplete))
        }
      })
    }

    // Handle completion
    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`))
      }
    })

    // Handle errors
    xhr.addEventListener("error", () => {
      reject(new Error("Network error during upload"))
    })

    xhr.addEventListener("abort", () => {
      reject(new Error("Upload aborted"))
    })

    // Send PUT request to S3
    xhr.open("PUT", presignedUrl)
    xhr.setRequestHeader("Content-Type", file.type)
    xhr.send(file)
  })
}

/**
 * Document creation data
 */
export interface CreateDocumentData {
  student_id: number
  title: string
  s3_key: string
  file_type: string
  subject?: string
}

/**
 * Document response from API
 */
export interface DocumentResponse {
  id: number
  student_id: number
  title: string
  upload_date: string
  file_type: string
  subject?: string
  status: string
  error_message?: string
}

/**
 * Create document metadata in database after S3 upload
 *
 * @param data - Document metadata
 * @param token - Authentication token
 * @returns Promise that resolves to created document
 */
export async function createDocument(
  data: CreateDocumentData,
  token: string
): Promise<DocumentResponse> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/documents`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }
  )

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(
      error.detail || `Failed to create document: ${response.statusText}`
    )
  }

  return response.json()
}

/**
 * Get presigned URL for S3 upload
 */
export interface PresignedUrlRequest {
  student_id: number
  filename: string
  content_type: string
}

export interface PresignedUrlResponse {
  presigned_url: string
  s3_key: string
  expires_in: number
}

/**
 * Get presigned URL from backend for direct S3 upload
 *
 * @param data - Upload request data
 * @param token - Authentication token
 * @returns Promise that resolves to presigned URL data
 */
export async function getPresignedUrl(
  data: PresignedUrlRequest,
  token: string
): Promise<PresignedUrlResponse> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/s3/upload-url`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }
  )

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(
      error.detail || `Failed to get upload URL: ${response.statusText}`
    )
  }

  return response.json()
}

/**
 * Complete upload workflow: get presigned URL, upload to S3, create document
 *
 * @param file - File to upload
 * @param studentId - Student ID
 * @param title - Document title
 * @param subject - Optional subject
 * @param token - Authentication token
 * @param onProgress - Optional progress callback (0-100)
 * @returns Promise that resolves to created document
 */
export async function completeUploadWorkflow(
  file: File,
  studentId: number,
  title: string,
  subject: string | undefined,
  token: string,
  onProgress?: (progress: number) => void
): Promise<DocumentResponse> {
  // Step 1: Validate file
  const validation = validateFile(file)
  if (!validation.valid) {
    throw new Error(validation.error)
  }

  // Step 2: Get presigned URL
  onProgress?.(10)
  const { presigned_url, s3_key } = await getPresignedUrl(
    {
      student_id: studentId,
      filename: file.name,
      content_type: file.type,
    },
    token
  )

  // Step 3: Upload to S3
  onProgress?.(20)
  await uploadToS3(file, presigned_url, (uploadProgress) => {
    // Map upload progress to 20-80% of total progress
    const totalProgress = 20 + (uploadProgress * 60) / 100
    onProgress?.(Math.round(totalProgress))
  })

  // Step 4: Create document metadata
  onProgress?.(90)
  const document = await createDocument(
    {
      student_id: studentId,
      title,
      s3_key,
      file_type: getFileTypeFromMime(file.type),
      subject,
    },
    token
  )

  onProgress?.(100)
  return document
}
