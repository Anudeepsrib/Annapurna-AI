"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function LoginPage() {
    const router = useRouter()

    useEffect(() => {
        // Local mode - no auth needed, redirect to profile
        router.push("/profile")
    }, [router])

    return (
        <div className="flex min-h-screen items-center justify-center">
            <p className="text-muted-foreground">Redirecting...</p>
        </div>
    )
}
