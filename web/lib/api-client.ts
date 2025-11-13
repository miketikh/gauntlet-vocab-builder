/**
 * API Client for Vocab Builder
 *
 * This file provides a type-safe API client using openapi-fetch.
 * Types are automatically generated from the FastAPI OpenAPI schema.
 *
 * Usage:
 * 1. Start the FastAPI server: cd api && uvicorn main:app --reload
 * 2. Generate types: cd web && npm run generate:api-types
 * 3. Import and use: import { apiClient } from '@/lib/api-client'
 */

import createClient from "openapi-fetch"
import type { paths } from "@/types/api"

// API base URL - configure based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

/**
 * Type-safe API client
 * All endpoints and request/response types are inferred from OpenAPI schema
 */
export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

/**
 * Helper to set authentication token
 * Call this after user logs in to add Bearer token to all requests
 *
 * @param token - JWT token from Supabase auth
 */
export function setAuthToken(token: string | null) {
  if (token) {
    apiClient.headers.set("Authorization", `Bearer ${token}`)
  } else {
    apiClient.headers.delete("Authorization")
  }
}

/**
 * Example usage:
 *
 * // GET request
 * const { data, error } = await apiClient.GET("/api/students", {
 *   params: {
 *     query: { educator_id: 123 }
 *   }
 * });
 *
 * // POST request
 * const { data, error } = await apiClient.POST("/api/students", {
 *   body: {
 *     name: "John Doe",
 *     grade_level: 8
 *   }
 * });
 *
 * // With authentication
 * setAuthToken(session.access_token);
 * const { data, error } = await apiClient.GET("/api/me");
 */

// Type exports for convenience
export type ApiPaths = paths
export type ApiResponse<T> = {
  data?: T
  error?: {
    message: string
    status: number
  }
}
