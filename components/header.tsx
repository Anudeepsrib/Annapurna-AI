import Link from "next/link"
import { Button } from "@/components/ui/button"

export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-muted bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <div className="flex items-center gap-2">
                    <Link href="/" className="flex items-center gap-2">
                        <span className="text-2xl font-serif font-bold text-primary tracking-tight">
                            Annapurna-AI
                        </span>
                    </Link>
                </div>
                <nav className="flex items-center gap-4">
                    <Link href="/about" className="text-sm font-medium hover:text-primary transition-colors">
                        About
                    </Link>
                    <Button size="sm" variant="outline">Sign In</Button>
                </nav>
            </div>
        </header>
    )
}
