"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ApiClient, type GroceryCategory } from "@/lib/api"
import { ArrowLeft, Printer, RefreshCw, Share2 } from "lucide-react"

export default function GroceryPage() {
    const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({})
    const [groceryCategories, setGroceryCategories] = useState<GroceryCategory[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        ApiClient.getGroceryList()
            .then((data) => {
                setGroceryCategories(data)
                setError(null)
            })
            .catch(() => setError("Could not load the grocery list. Check that the backend is running."))
            .finally(() => setLoading(false))
    }, [])

    const toggleItem = (id: string) => {
        setCheckedItems((prev) => ({ ...prev, [id]: !prev[id] }))
    }

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-10 bg-muted/20">
                <div className="container mx-auto max-w-[800px]">
                    <div className="flex items-center gap-4 mb-6">
                        <Link href="/plan">
                            <Button variant="ghost" size="icon">
                                <ArrowLeft className="h-4 w-4" />
                            </Button>
                        </Link>
                        <div>
                            <h1 className="font-serif text-3xl font-bold">Grocery List</h1>
                            <p className="text-muted-foreground">Generated from your latest local plan.</p>
                        </div>
                    </div>

                    <div className="flex justify-end gap-2 mb-6">
                        <Button variant="outline" size="sm" className="gap-2">
                            <Printer className="h-4 w-4" /> Print
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2">
                            <Share2 className="h-4 w-4" /> Share
                        </Button>
                    </div>

                    <div className="space-y-6">
                        {loading ? (
                            <div className="flex items-center justify-center gap-2 py-10 text-muted-foreground">
                                <RefreshCw className="h-4 w-4 animate-spin" />
                                Loading grocery list...
                            </div>
                        ) : error ? (
                            <Card>
                                <CardContent className="pt-6 text-center text-muted-foreground">
                                    {error}
                                </CardContent>
                            </Card>
                        ) : groceryCategories.length === 0 ? (
                            <Card>
                                <CardContent className="pt-6 text-center text-muted-foreground">
                                    No grocery items yet. Generate a plan first.
                                </CardContent>
                            </Card>
                        ) : (
                            groceryCategories.map((category) => (
                                <Card key={category.name}>
                                    <CardContent className="pt-6">
                                        <h3 className="font-serif text-xl font-bold mb-4 text-primary">{category.name}</h3>
                                        <div className="space-y-3">
                                            {category.items.map((item) => (
                                                <div key={item.id} className="flex items-start space-x-3 group">
                                                    <Checkbox
                                                        id={item.id}
                                                        checked={checkedItems[item.id] || false}
                                                        onCheckedChange={() => toggleItem(item.id)}
                                                        className="mt-1"
                                                    />
                                                    <div className="flex-1">
                                                        <Label
                                                            htmlFor={item.id}
                                                            className={`text-base font-medium cursor-pointer transition-colors ${checkedItems[item.id] ? "text-muted-foreground line-through decoration-muted-foreground/50" : ""}`}
                                                        >
                                                            {item.name}
                                                        </Label>
                                                        <div className={`text-sm text-muted-foreground flex justify-between gap-4 ${checkedItems[item.id] ? "opacity-50" : ""}`}>
                                                            <span>{item.quantity}</span>
                                                            <span className="text-xs italic hidden group-hover:inline-block transition-opacity opacity-70">
                                                                Used in: {item.meals.join(", ")}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            ))
                        )}
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}
