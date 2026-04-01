import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"

export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-primary/10 bg-primary text-primary-foreground shadow-md">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <div className="flex items-center gap-2">
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className="relative">
                            <Image
                                src="/annapurna_logo.png"
                                alt="Annapurna Logo"
                                width={40}
                                height={40}
                                priority
                                unoptimized
                                className="object-contain"
                            />
                        </div>
                        <span className="text-2xl font-serif font-bold tracking-tight text-primary-foreground">
                            Annapurna
                        </span>
                    </Link>
                </div>
                <nav className="flex items-center gap-6">
                    <Link href="/about" className="text-sm font-medium text-primary-foreground/90 hover:text-accent transition-colors">
                        About
                    </Link>
                    <Link href="/settings" className="text-sm font-medium text-primary-foreground/90 hover:text-accent transition-colors">
                        <Settings className="h-5 w-5" />
                    </Link>
                    <span className="text-xs bg-white/20 px-2 py-1 rounded text-primary-foreground/80">
                        Local Mode
                    </span>
                </nav>
            </div>
        </header>
    )
}
