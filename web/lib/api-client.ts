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

function resolveApiUrl(path: string) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path
  }
  if (path.startsWith("/")) {
    return `${API_BASE_URL}${path}`
  }
  return `${API_BASE_URL}/${path}`
}

function buildHeaders(
  headers?: HeadersInit,
  token?: string,
  includeJsonContentType = true
) {
  const merged = new Headers(headers)

  if (includeJsonContentType && !merged.has("Content-Type")) {
    merged.set("Content-Type", "application/json")
  }

  if (token) {
    merged.set("Authorization", `Bearer ${token}`)
  }

  return merged
}

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
 * Helper to get API client with authentication token
 * Call this when making authenticated requests
 *
 * @param token - JWT token from Supabase auth
 */
export function getAuthenticatedClient(token: string) {
  return createClient<paths>({
    baseUrl: API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  })
}

/**
 * Thin wrapper around fetch that automatically prefixes the API base URL.
 * Useful for endpoints that aren't yet represented in the generated OpenAPI types.
 */
export async function apiFetch(path: string, init: RequestInit = {}) {
  return fetch(resolveApiUrl(path), {
    ...init,
    headers: buildHeaders(init.headers),
  })
}

/**
 * Authenticated fetch helper that adds the bearer token and base URL prefix.
 */
export async function authenticatedFetch(
  path: string,
  token: string,
  init: RequestInit = {}
) {
  return fetch(resolveApiUrl(path), {
    ...init,
    headers: buildHeaders(init.headers, token),
  })
}

/**
 * Example usage:
 *
 * // GET request (public)
 * const { data, error } = await apiClient.GET("/api/health");
 *
 * // POST request (authenticated)
 * const token = session.access_token;
 * const client = getAuthenticatedClient(token);
 * const { data, error } = await client.POST("/api/students", {
 *   body: {
 *     name: "John Doe",
 *     grade_level: 8
 *   }
 * });
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
