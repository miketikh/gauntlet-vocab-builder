"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { User, Session } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/client"
import { getAuthenticatedClient } from "@/lib/api-client"
import { useRouter } from "next/navigation"

type Educator = {
  id: number
  email: string
  name: string
  school: string | null
  created_at: string
}

type AuthContextType = {
  user: User | null
  educator: Educator | null
  loading: boolean
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [educator, setEducator] = useState<Educator | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    async function loadEducator(session: Session) {
      try {
        // Use backend API to get or create educator
        const apiClient = getAuthenticatedClient(session.access_token)
        const { data, error } = await apiClient.GET("/api/auth/me")

        if (error) {
          console.error("Error loading educator from API:", error)
          setEducator(null)
        } else if (data) {
          setEducator(data as Educator)
        }
      } catch (error) {
        console.error("Error loading educator:", error)
        setEducator(null)
      } finally {
        setLoading(false)
      }
    }

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      if (session) {
        loadEducator(session)
      } else {
        setLoading(false)
      }
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      if (session) {
        loadEducator(session)
      } else {
        setEducator(null)
        setLoading(false)
      }
    })

    return () => subscription.unsubscribe()
  }, [supabase])

  async function signOut() {
    await supabase.auth.signOut()
    setUser(null)
    setEducator(null)
    router.push("/login")
    router.refresh()
  }

  return (
    <AuthContext.Provider value={{ user, educator, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
