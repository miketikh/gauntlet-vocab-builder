import { createClient } from "@/lib/supabase/server"
import { NextResponse } from "next/server"

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get("code")
  const origin = requestUrl.origin

  if (code) {
    const supabase = await createClient()
    const { error, data } = await supabase.auth.exchangeCodeForSession(code)

    if (error) {
      console.error("Error exchanging code for session:", error)
      return NextResponse.redirect(`${origin}/login?error=auth_failed`)
    }

    // If this is a new user (OAuth signup), create educator record
    if (data.user) {
      const { error: educatorError } = await supabase.from("educators").upsert(
        {
          id: data.user.id,
          email: data.user.email!,
          name:
            data.user.user_metadata.name ||
            data.user.user_metadata.full_name ||
            data.user.email?.split("@")[0] ||
            "Educator",
          school: null,
        },
        {
          onConflict: "id",
          ignoreDuplicates: true,
        }
      )

      if (educatorError) {
        console.error("Error creating educator record:", educatorError)
        // Don't block login if educator record fails
      }
    }
  }

  // URL to redirect to after sign in process completes
  return NextResponse.redirect(`${origin}/dashboard`)
}
