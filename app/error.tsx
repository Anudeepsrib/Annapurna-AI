"use client" // Error components must be Client Components

import { useEffect } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { AlertCircle, RefreshCw } from "lucide-react"

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error("Application Error:", error)
    }, [error])

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 flex flex-col items-center justify-center py-20 bg-destructive/5 text-center px-4">
                <div className="space-y-6 max-w-md mx-auto">
                    <div className="rounded-full bg-destructive/10 w-24 h-24 flex items-center justify-center mx-auto mb-6">
                        <AlertCircle className="h-10 w-10 text-destructive" />
                    </div>
                    <h1 className="font-serif text-3xl font-bold text-destructive">Something went wrong!</h1>
                    <p className="text-muted-foreground">
                        We encountered an unexpected error. Our chefs are looking into it.
                    </p>
                    {error.digest && (
                        <div className="bg-white p-2 rounded border text-xs text-muted-foreground font-mono">
                            Reference: {error.digest}
                        </div>
                    )}
                    <div className="pt-4">
                        <Button
                            onClick={() => reset()}
                            size="lg"
                            className="gap-2"
                        >
                            <RefreshCw className="h-4 w-4" />
                            Try Again
                        </Button>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}
