import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
  BookOpen,
  TrendingUp,
  Users,
  BarChart3,
  Sparkles,
  MessageSquare,
  Target,
} from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-blue-600" />
            </div>
            <span className="text-xl font-semibold text-white">
              Talk Ladder
            </span>
          </div>
          <Button
            asChild
            variant="secondary"
            size="default"
            className="bg-white text-blue-600 hover:bg-blue-50"
          >
            <Link href="/login">Login</Link>
          </Button>
        </div>
      </header>

      <section className="container mx-auto px-4 py-12 md:py-16">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground text-balance leading-tight">
            Climb the ladder of vocabulary excellence
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto text-pretty leading-relaxed">
            An AI-powered platform that helps middle school students
            progressively advance their vocabulary while giving educators
            powerful insights into student growth.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-2">
            <Button
              asChild
              size="lg"
              className="text-lg px-8 py-6 h-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              <Link href="/login">Get Started Now</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-4 py-12 bg-gradient-to-b from-blue-50 to-indigo-50">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="bg-white rounded-xl p-6 border border-blue-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Progressive Word Advancement
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Students receive personalized vocabulary recommendations that
                are challenging yet attainable, matched to their current
                proficiency level.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-xl p-6 border border-blue-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Real-Time Progress Tracking
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Monitor vocabulary growth with detailed analytics that track
                which words students are learning and using effectively.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-xl p-6 border border-blue-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Teacher Dashboard
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Educators gain powerful insights into class-wide vocabulary
                trends and individual student progress with automated gap
                analysis.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center space-y-12">
          <div className="space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground text-balance">
              Built for educators and students
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty leading-relaxed">
              Talk Ladder uses AI to analyze student writing and conversations,
              automatically identifying vocabulary gaps and suggesting the
              perfect next words to learn.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 text-left">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 text-white flex items-center justify-center font-bold text-lg shadow-lg">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-semibold text-foreground">
                Analyze Student Language
              </h4>
              <p className="text-muted-foreground leading-relaxed">
                Our AI builds profiles of each student&apos;s vocabulary from
                their writing and conversation transcripts.
              </p>
            </div>

            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 text-white flex items-center justify-center font-bold text-lg shadow-lg">
                <Target className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-semibold text-foreground">
                Identify Gaps
              </h4>
              <p className="text-muted-foreground leading-relaxed">
                Advanced algorithms detect vocabulary gaps and generate
                personalized word recommendations.
              </p>
            </div>

            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center font-bold text-lg shadow-lg">
                <Sparkles className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-semibold text-foreground">
                Track Growth
              </h4>
              <p className="text-muted-foreground leading-relaxed">
                Monitor progress as students incorporate new words, with
                detailed analytics for teachers.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-10 md:p-12 text-center shadow-xl">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 text-balance">
            Ready to elevate vocabulary learning?
          </h2>
          <p className="text-lg text-white/90 mb-6 max-w-2xl mx-auto text-pretty leading-relaxed">
            Join educators who are transforming vocabulary instruction with
            AI-powered insights.
          </p>
          <Button
            asChild
            size="lg"
            variant="secondary"
            className="text-lg px-8 py-6 h-auto bg-white text-blue-600 hover:bg-blue-50"
          >
            <Link href="/login">Get Started Now</Link>
          </Button>
        </div>
      </section>

      <footer className="border-t border-border bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700">
                Talk Ladder
              </span>
            </div>
            <p className="text-sm text-gray-600">
              © 2025 Flourish Schools. Empowering vocabulary growth.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
