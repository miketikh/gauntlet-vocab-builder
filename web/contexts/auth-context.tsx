"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { User } from "@supabase/supabase-js"
import { createClient } from "@/lib/supabase/client"
import { useRouter } from "next/navigation"

type Educator = {
  id: string
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
    async function loadEducator(userId: string) {
      try {
        const { data, error } = await supabase
          .from("educators")
          .select("*")
          .eq("id", userId)
          .single()

        if (error) {
          console.error("Error loading educator:", error)
        } else {
          setEducator(data)
        }
      } catch (error) {
        console.error("Error loading educator:", error)
      } finally {
        setLoading(false)
      }
    }

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      if (session?.user) {
        loadEducator(session.user.id)
      } else {
        setLoading(false)
      }
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      if (session?.user) {
        loadEducator(session.user.id)
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
