"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { createClient } from "@/lib/supabase/client"
import { getAuthenticatedClient } from "@/lib/api-client"

// Form validation schema
const formSchema = z.object({
  name: z
    .string()
    .min(1, "Student name is required")
    .max(255, "Name is too long"),
  grade_level: z
    .number()
    .int()
    .min(6, "Grade must be 6-12")
    .max(12, "Grade must be 6-12"),
  reading_level: z.string().optional(),
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface Student {
  id: number
  name: string
  grade_level: number
  reading_level?: string | null
  notes?: string | null
}

interface AddStudentFormProps {
  onSuccess?: (student: Student) => void
  onCancel?: () => void
}

export function AddStudentForm({ onSuccess, onCancel }: AddStudentFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const supabase = createClient()

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      grade_level: 6,
      reading_level: "",
      notes: "",
    },
  })

  async function onSubmit(values: FormValues) {
    setIsSubmitting(true)
    setError(null)

    try {
      // Get access token
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        throw new Error("Not authenticated")
      }

      // Create authenticated API client
      const apiClient = getAuthenticatedClient(session.access_token)

      // Create student
      const { data, error: apiError } = await apiClient.POST("/api/students", {
        body: {
          name: values.name,
          grade_level: values.grade_level,
          reading_level: values.reading_level || null,
          notes: values.notes || null,
        },
      })

      if (apiError) {
        const errorMessage =
          typeof apiError === "object" && apiError !== null
            ? JSON.stringify(apiError)
            : String(apiError)
        throw new Error(errorMessage || "Failed to create student")
      }

      if (!data) {
        throw new Error("No data returned from API")
      }

      // Success - call callback
      onSuccess?.(data)

      // Reset form
      form.reset()
    } catch (err) {
      console.error("Error creating student:", err)
      setError(err instanceof Error ? err.message : "Failed to create student")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="bg-destructive/15 text-destructive px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}

        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Student Name</FormLabel>
              <FormControl>
                <Input placeholder="Enter student name" {...field} />
              </FormControl>
              <FormDescription>
                The display name for this student profile
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="grade_level"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Grade Level</FormLabel>
              <Select
                onValueChange={(value) => field.onChange(parseInt(value))}
                defaultValue={field.value?.toString()}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select grade level" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="6">Grade 6</SelectItem>
                  <SelectItem value="7">Grade 7</SelectItem>
                  <SelectItem value="8">Grade 8</SelectItem>
                  <SelectItem value="9">Grade 9</SelectItem>
                  <SelectItem value="10">Grade 10</SelectItem>
                  <SelectItem value="11">Grade 11</SelectItem>
                  <SelectItem value="12">Grade 12</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>Current grade level (6-12)</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="reading_level"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Reading Level (Optional)</FormLabel>
              <FormControl>
                <Input
                  placeholder="e.g., Grade Level, Above Grade Level"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Student&apos;s current reading level if known
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes (Optional)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Any additional notes about this student..."
                  className="resize-none"
                  rows={4}
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Additional information or context
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-3 justify-end">
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isSubmitting ? "Creating..." : "Create Student"}
          </Button>
        </div>
      </form>
    </Form>
  )
}
