"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ArrowLeft, Share2, Printer } from "lucide-react"
import Link from "next/link"



export default function GroceryPage() {
    const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({})
    const [groceryCategories, setGroceryCategories] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch("http://localhost:8000/api/grocery-list")
            .then(res => res.json())
            .then(data => {
                setGroceryCategories(data)
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to fetch grocery list:", err)
                setLoading(false)
            })
    }, [])

    const toggleItem = (id: string) => {
        setCheckedItems(prev => ({ ...prev, [id]: !prev[id] }))
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
                            <p className="text-muted-foreground">For Feb 12 - Feb 18 Plan</p>
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
                            <div className="text-center py-10">Loading grocery list...</div>
                        ) : (
                            groceryCategories.map((category) => (
                                <Card key={category.name}>
                                    <CardContent className="pt-6">
                                        <h3 className="font-serif text-xl font-bold mb-4 text-primary">{category.name}</h3>
                                        <div className="space-y-3">
                                            {category.items.map((item: any) => (
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
                                                        <div className={`text-sm text-muted-foreground flex justify-between ${checkedItems[item.id] ? "opacity-50" : ""}`}>
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
