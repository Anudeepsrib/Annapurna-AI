"use client"

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Archive, Loader2, RefreshCw, Snowflake } from "lucide-react"
import { toast } from "sonner"

import { Footer } from "@/components/footer"
import { Header } from "@/components/header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { ApiClient, ApiError, type PantryInventoryItem } from "@/lib/api"

const locations = ["pantry", "refrigerator", "freezer"] as const

export default function PantryPage() {
    const queryClient = useQueryClient()
    const [pantryText, setPantryText] = useState("")
    const pantry = useQuery({ queryKey: ["pantry"], queryFn: ApiClient.getPantry })
    const importer = useMutation({
        mutationFn: ApiClient.importPantry,
        onSuccess: (items) => {
            queryClient.setQueryData(["pantry"], items)
            setPantryText("")
            toast.success("Pantry inventory updated.")
        },
        onError: (error) => toast.error(error instanceof ApiError ? error.message : "Could not update the pantry."),
    })
    const items = pantry.data ?? []
    const expiring = items.filter(isUseSoon).length

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 bg-muted/20 py-10">
                <div className="container mx-auto max-w-5xl space-y-8 px-4">
                    <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
                        <div>
                            <p className="text-sm font-medium uppercase tracking-wide text-secondary">Household inventory</p>
                            <h1 className="font-serif text-4xl font-bold">Pantry</h1>
                            <p className="mt-2 text-muted-foreground">
                                Structured locally from your text entries and used for planning and shopping deductions.
                            </p>
                        </div>
                        <div className="flex gap-3 text-sm">
                            <Summary label="Items" value={items.length} />
                            <Summary label="Use soon" value={expiring} />
                        </div>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>Add or update stock</CardTitle>
                            <CardDescription>
                                One item per line. Existing canonical ingredients are updated instead of duplicated.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form
                                className="space-y-3"
                                onSubmit={(event) => {
                                    event.preventDefault()
                                    if (pantryText.trim()) importer.mutate(pantryText)
                                }}
                            >
                                <Label htmlFor="pantry-import">Pantry text</Label>
                                <textarea
                                    id="pantry-import"
                                    value={pantryText}
                                    onChange={(event) => setPantryText(event.target.value)}
                                    placeholder={"rice - 5 kg\nspinach - 1 bunch - use within 2 days"}
                                    className="min-h-28 w-full rounded-md border border-input bg-white px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                />
                                <Button disabled={importer.isPending || !pantryText.trim()}>
                                    {importer.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    Update pantry
                                </Button>
                            </form>
                        </CardContent>
                    </Card>

                    {pantry.isLoading ? (
                        <div className="flex items-center justify-center gap-2 py-16 text-muted-foreground">
                            <RefreshCw className="h-4 w-4 animate-spin" /> Loading pantry...
                        </div>
                    ) : pantry.isError ? (
                        <Card><CardContent className="py-10 text-center text-muted-foreground">Could not load the pantry.</CardContent></Card>
                    ) : items.length === 0 ? (
                        <Card><CardContent className="py-10 text-center text-muted-foreground">Your pantry is empty.</CardContent></Card>
                    ) : (
                        <div className="grid gap-6 lg:grid-cols-3">
                            {locations.map((location) => (
                                <InventoryGroup
                                    key={location}
                                    location={location}
                                    items={items.filter((item) => item.storageLocation === location)}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </main>
            <Footer />
        </div>
    )
}

function Summary({ label, value }: { label: string; value: number }) {
    return <div className="rounded-lg border bg-white px-4 py-2"><strong>{value}</strong> {label}</div>
}

function InventoryGroup({ location, items }: { location: typeof locations[number]; items: PantryInventoryItem[] }) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2 capitalize">
                    {location === "freezer" ? <Snowflake className="h-5 w-5" /> : <Archive className="h-5 w-5" />}
                    {location}
                </CardTitle>
                <CardDescription>{items.length} item{items.length === 1 ? "" : "s"}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
                {items.length === 0 ? <p className="text-sm text-muted-foreground">Nothing stored here.</p> : null}
                {items.map((item) => (
                    <div key={item.id} className="rounded-lg border bg-white p-3">
                        <div className="flex items-start justify-between gap-2">
                            <div>
                                <p className="font-medium">{item.displayName}</p>
                                <p className="text-sm text-muted-foreground">
                                    {item.quantity && item.unit ? `${item.quantity} ${item.unit}` : item.quantityText || "Quantity unknown"}
                                </p>
                            </div>
                            {item.expired ? <Badge variant="destructive">Expired</Badge> : null}
                            {!item.expired && isUseSoon(item) ? <Badge variant="outline">Use soon</Badge> : null}
                        </div>
                        <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                            <span className="rounded bg-muted px-2 py-1">{item.category.replaceAll("_", " ")}</span>
                            {item.opened ? <span className="rounded bg-muted px-2 py-1">Opened</span> : null}
                            {item.ingredientId ? null : <span className="rounded bg-muted px-2 py-1">Unresolved name</span>}
                        </div>
                    </div>
                ))}
            </CardContent>
        </Card>
    )
}

function isUseSoon(item: PantryInventoryItem) {
    if (!item.expiresAt || item.expired) return false
    const remaining = new Date(item.expiresAt).getTime() - Date.now()
    return remaining <= 5 * 24 * 60 * 60 * 1000
}
