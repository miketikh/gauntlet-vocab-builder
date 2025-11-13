"use client"

import { UserMenu } from "./user-menu"
import { Separator } from "@/components/ui/separator"
import { BookOpen } from "lucide-react"
import Link from "next/link"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 w-full border-b bg-white">
        <div className="container flex h-16 items-center justify-between px-4 mx-auto max-w-7xl">
          {/* Logo and App Name */}
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-primary p-2">
              <BookOpen className="h-5 w-5 text-primary-foreground" />
            </div>
            <div className="flex flex-col">
              <Link
                href="/dashboard"
                className="text-lg font-bold text-gray-900 hover:text-gray-700 transition-colors"
              >
                Vocabulary Builder
              </Link>
              <span className="text-xs text-muted-foreground hidden sm:block">
                Educator Dashboard
              </span>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-sm font-medium text-gray-900 hover:text-primary transition-colors"
            >
              Students
            </Link>
            <Link
              href="/dashboard/settings"
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors cursor-not-allowed opacity-50"
              onClick={(e) => e.preventDefault()}
            >
              Settings
            </Link>
          </nav>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <UserMenu />
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">{children}</main>

      {/* Footer (Optional) */}
      <footer className="border-t bg-white mt-auto">
        <div className="container mx-auto px-4 py-6 max-w-7xl">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <div>
              <p>Vocabulary Builder - Personalized Learning Platform</p>
            </div>
            <div className="flex gap-4">
              <a
                href="#"
                className="hover:text-primary transition-colors cursor-not-allowed opacity-50"
                onClick={(e) => e.preventDefault()}
              >
                Help
              </a>
              <Separator orientation="vertical" className="h-4" />
              <a
                href="#"
                className="hover:text-primary transition-colors cursor-not-allowed opacity-50"
                onClick={(e) => e.preventDefault()}
              >
                Privacy
              </a>
              <Separator orientation="vertical" className="h-4" />
              <a
                href="#"
                className="hover:text-primary transition-colors cursor-not-allowed opacity-50"
                onClick={(e) => e.preventDefault()}
              >
                Terms
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
