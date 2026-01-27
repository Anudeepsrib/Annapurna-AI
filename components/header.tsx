import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60 shadow-sm">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <div className="flex items-center gap-2">
                    <Link href="/" className="flex items-center gap-3">
                        <Image
                            src="/annapurna_logo.png"
                            alt="Annapurna Logo"
                            width={40}
                            height={40}
                            priority
                            unoptimized
                            className="object-contain"
                        />
                        <span className="text-2xl font-serif font-bold text-primary tracking-tight">
                            Annapurna
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
