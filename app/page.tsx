import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import Link from "next/link"
import { ArrowRight, Leaf, ChefHat, BookOpen } from "lucide-react"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative space-y-8 pb-12 pt-12 md:pb-24 md:pt-20 lg:py-32 bg-gradient-to-b from-background to-muted/20 overflow-hidden">
          <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
            <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-primary to-secondary opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" style={{ clipPath: "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)" }}></div>
          </div>
          <div className="container mx-auto flex max-w-[64rem] flex-col items-center gap-6 text-center">
            <div className="rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary shadow-sm border border-primary/20">
              South Indian Vegetarian • Andhra Style
            </div>
            <h1 className="font-serif text-4xl font-bold tracking-tight text-primary sm:text-5xl md:text-6xl lg:text-7xl">
              Plan your week. <br className="hidden sm:inline" />
              <span>Cook like home.</span>
            </h1>
            <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8 font-sans">
              Authentic meal planning for Andhra Telugu households.
              Balanced nutrition, zero waste, and culturally respectful recipes
              that feel like your grandmother's kitchen.
            </p>
            <div className="space-x-4 pt-4">
              <Link href="/profile">
                <Button size="lg" className="h-12 px-8 text-lg gap-2 shadow-md">
                  Generate Weekly Plan
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/about">
                <Button variant="outline" size="lg" className="h-12 px-8 text-lg bg-white hover:bg-muted">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="container space-y-6 py-8 dark:bg-transparent md:py-12 lg:py-24">
          <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center">
            <h2 className="font-serif text-3xl font-bold leading-[1.1] sm:text-3xl md:text-5xl text-secondary">
              Why Annapurna?
            </h2>
            <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
              Designed specifically for the nuances of South Indian vegetarian cooking.
            </p>
          </div>
          <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-3">
            <Card className="flex flex-col items-center justify-between p-2">
              <CardContent className="pt-6 flex flex-col items-center text-center gap-3">
                <div className="p-3 bg-accent/10 rounded-full">
                  <ChefHat className="h-8 w-8 text-accent" />
                </div>
                <h3 className="font-serif text-xl font-bold">Authentic Recipes</h3>
                <p className="text-sm text-muted-foreground">
                  Pappu, Pulusu, Vepudu — tailored to your spice levels and family traditions.
                </p>
              </CardContent>
            </Card>
            <Card className="flex flex-col items-center justify-between p-2">
              <CardContent className="pt-6 flex flex-col items-center text-center gap-3">
                <div className="p-3 bg-secondary/10 rounded-full">
                  <Leaf className="h-8 w-8 text-secondary" />
                </div>
                <h3 className="font-serif text-xl font-bold">Zero Waste</h3>
                <p className="text-sm text-muted-foreground">
                  Smart grocery lists that use up ingredients across multiple meals.
                </p>
              </CardContent>
            </Card>
            <Card className="flex flex-col items-center justify-between p-2">
              <CardContent className="pt-6 flex flex-col items-center text-center gap-3">
                <div className="p-3 bg-primary/10 rounded-full">
                  <BookOpen className="h-8 w-8 text-primary" />
                </div>
                <h3 className="font-serif text-xl font-bold">Evidence Based</h3>
                <p className="text-sm text-muted-foreground">
                  Nutrition advice grounded in science, not pseudo-science.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
