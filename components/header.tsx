import Link from "next/link"
import Image from "next/image"
import { Settings } from "lucide-react"

const primaryLinks = [
    ["Today", "/today"],
    ["Week", "/plan"],
    ["Pantry", "/pantry"],
    ["Shop", "/list"],
    ["Family", "/profile"],
] as const

export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-primary/10 bg-background/80 backdrop-blur-md shadow-sm">
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
                        <span className="text-2xl font-serif font-bold tracking-tight text-primary">
                            Annapurna
                        </span>
                    </Link>
                </div>
                <nav aria-label="Primary navigation" className="flex items-center gap-3 overflow-x-auto md:gap-5">
                    {primaryLinks.map(([label, href]) => (
                        <Link key={href} href={href} className="whitespace-nowrap text-sm font-medium text-foreground/80 transition-colors hover:text-primary">
                            {label}
                        </Link>
                    ))}
                    <Link href="/settings" className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors">
                        <span className="sr-only">Settings</span>
                        <Settings className="h-5 w-5" />
                    </Link>
                    <span className="hidden rounded-md border border-primary/10 bg-primary/5 px-2 py-1 text-xs font-medium tracking-wide text-primary/80 shadow-sm sm:inline">
                        Local Mode
                    </span>
                </nav>
            </div>
        </header>
    )
}
