import Link from "next/link"
import { Wheat } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface PantrySectionProps {
    value: string
    onChange: (value: string) => void
}

export function PantrySection({ value, onChange }: PantrySectionProps) {
    return (
        <section className="space-y-2">
            <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    <Wheat className="h-5 w-5 text-primary" />
                    <Label htmlFor="pantry" className="text-base font-semibold">Pantry Inventory</Label>
                </div>
                <Button asChild type="button" variant="ghost" size="sm">
                    <Link href="/pantry">Open pantry</Link>
                </Button>
            </div>
            <textarea
                id="pantry"
                value={value}
                onChange={(event) => onChange(event.target.value)}
                className="min-h-32 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <p className="text-xs text-muted-foreground">
                One item per line, for example: spinach - 1 bunch - use within 2 days.
            </p>
        </section>
    )
}
