"use client"

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { CheckCircle2, Clock3, Leaf, PackageCheck, Printer, RefreshCw, Share2 } from "lucide-react"
import { toast } from "sonner"

import { Footer } from "@/components/footer"
import { Header } from "@/components/header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { ApiClient, type GroceryCategory, type Ingredient } from "@/lib/api"

export default function GroceryPage() {
    const [checked, setChecked] = useState<Record<string, boolean>>({})
    const [categories, setCategories] = useState<GroceryCategory[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        ApiClient.getGroceryList()
            .then((data) => {
                setCategories(data)
                setError(null)
            })
            .catch(() => setError("Could not load the grocery list. Check that the backend is running."))
            .finally(() => setLoading(false))
    }, [])

    const items = useMemo(() => categories.flatMap((category) => category.items), [categories])
    const buyItems = items.filter((item) => item.status === "need_to_buy")
    const pantryItems = items.filter((item) => item.status === "pantry")
    const useSoonItems = items.filter((item) => item.priority === "use_soon")
    const completed = buyItems.filter((item) => checked[item.id]).length

    const share = async () => {
        const text = buyItems.map((item) => `• ${item.name} — ${item.quantity}`).join("\n")
        try {
            const shared = typeof navigator.share === "function"
            if (shared) await navigator.share({ title: "Annapurna shopping list", text })
            else await navigator.clipboard.writeText(text)
            toast.success(shared ? "Shopping list shared." : "Shopping list copied.")
        } catch {
            toast.error("Could not share the shopping list.")
        }
    }

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 bg-muted/20 py-10">
                <div className="container mx-auto max-w-[860px] space-y-6 px-4">
                    <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
                        <div>
                            <p className="text-sm font-medium uppercase tracking-wide text-secondary">Pantry-aware shopping</p>
                            <h1 className="font-serif text-4xl font-bold">Shop</h1>
                            <p className="mt-2 text-muted-foreground">Only missing ingredients belong on the buy checklist.</p>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" className="gap-2" onClick={() => window.print()}>
                                <Printer className="h-4 w-4" /> Print
                            </Button>
                            <Button variant="outline" size="sm" className="gap-2" onClick={share} disabled={!buyItems.length}>
                                <Share2 className="h-4 w-4" /> Share
                            </Button>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3">
                        <Summary icon={CheckCircle2} label="To buy" value={`${completed}/${buyItems.length}`} />
                        <Summary icon={PackageCheck} label="Already at home" value={String(pantryItems.length)} />
                        <Summary icon={Clock3} label="Use soon" value={String(useSoonItems.length)} />
                    </div>

                    <div className="rounded-lg border border-secondary/20 bg-secondary/5 p-4">
                        <div className="flex gap-3">
                            <Leaf className="mt-0.5 h-5 w-5 text-secondary" />
                            <div>
                                <p className="font-medium">How this list was calculated</p>
                                <p className="text-sm text-muted-foreground">
                                    Planned ingredients are normalized, matched against usable pantry stock, and grouped without
                                    inventing quantities that recipes did not provide. <Link className="underline" href="/pantry">Review pantry</Link>
                                </p>
                            </div>
                        </div>
                    </div>

                    {loading ? (
                        <div className="flex items-center justify-center gap-2 py-10 text-muted-foreground">
                            <RefreshCw className="h-4 w-4 animate-spin" /> Loading grocery list...
                        </div>
                    ) : error ? (
                        <Card><CardContent className="pt-6 text-center text-muted-foreground">{error}</CardContent></Card>
                    ) : categories.length === 0 ? (
                        <Card><CardContent className="pt-6 text-center text-muted-foreground">No grocery items yet. Generate a plan first.</CardContent></Card>
                    ) : (
                        <div className="space-y-6">
                            {categories.map((category) => (
                                <Card key={category.name}>
                                    <CardContent className="pt-6">
                                        <h2 className="font-serif text-xl font-bold text-primary">{category.name}</h2>
                                        <p className="mb-4 mt-1 text-sm text-muted-foreground">{categoryExplanation(category.name)}</p>
                                        <div className="space-y-3">
                                            {category.items.map((item) => (
                                                <GroceryRow
                                                    key={item.id}
                                                    item={item}
                                                    checked={Boolean(checked[item.id])}
                                                    onToggle={() => setChecked((current) => ({ ...current, [item.id]: !current[item.id] }))}
                                                />
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </main>
            <Footer />
        </div>
    )
}

function Summary({ icon: Icon, label, value }: { icon: typeof CheckCircle2; label: string; value: string }) {
    return (
        <Card><CardContent className="flex items-center gap-3 py-4">
            <Icon className="h-5 w-5 text-secondary" />
            <div><p className="text-xl font-bold">{value}</p><p className="text-xs text-muted-foreground">{label}</p></div>
        </CardContent></Card>
    )
}

function GroceryRow({ item, checked, onToggle }: { item: Ingredient; checked: boolean; onToggle: () => void }) {
    const canCheck = item.status === "need_to_buy"
    return (
        <div className="flex items-start gap-3 rounded-lg border bg-white p-3">
            {canCheck ? (
                <Checkbox id={`shop-${item.id}`} checked={checked} onCheckedChange={onToggle} className="mt-1" />
            ) : (
                <PackageCheck className="mt-0.5 h-5 w-5 text-secondary" aria-hidden="true" />
            )}
            <div className={checked ? "flex-1 opacity-50" : "flex-1"}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                    <Label htmlFor={canCheck ? `shop-${item.id}` : undefined} className={checked ? "line-through" : ""}>
                        {item.name}
                    </Label>
                    <Badge variant={canCheck ? "default" : "secondary"}>
                        {canCheck ? "Buy" : item.status === "pantry" ? "Have" : "Use soon"}
                    </Badge>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{item.quantity}</p>
                {item.optimization_note ? <p className="mt-1 text-xs text-muted-foreground">Why: {item.optimization_note}</p> : null}
                {item.storeAffinity ? <p className="mt-1 text-xs text-muted-foreground">Suggested store: {item.storeAffinity.replaceAll("_", " ")}</p> : null}
                {item.meals.length ? <p className="mt-1 text-xs italic text-muted-foreground">Used in: {item.meals.join(", ")}</p> : null}
            </div>
        </div>
    )
}

function categoryExplanation(name: string) {
    if (name === "Use From Pantry First") return "Matched to current usable pantry inventory; do not buy again."
    if (name === "Buy / Replenish") return "Needed by the weekly plan but not found in usable pantry stock."
    return "Already at home but nearing expiry and not currently used by the plan."
}
