import Link from "next/link"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"

export default function NotFound() {
    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 flex flex-col items-center justify-center py-20 bg-muted/20 text-center px-4">
                <div className="space-y-6 max-w-md mx-auto">
                    <div className="rounded-full bg-primary/10 w-24 h-24 flex items-center justify-center mx-auto mb-6">
                        <Search className="h-10 w-10 text-primary" />
                    </div>
                    <h1 className="font-serif text-5xl font-bold text-primary">404</h1>
                    <h2 className="text-2xl font-semibold">Page Not Found</h2>
                    <p className="text-muted-foreground">
                        We couldn't find the page you were looking for. It might have been moved or doesn't exist.
                    </p>
                    <div className="flex gap-4 justify-center pt-4">
                        <Link href="/">
                            <Button size="lg" className="min-w-[140px]">
                                Go Home
                            </Button>
                        </Link>
                        <Link href="/plan">
                            <Button variant="outline" size="lg" className="min-w-[140px]">
                                My Plan
                            </Button>
                        </Link>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}
