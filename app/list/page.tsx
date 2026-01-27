"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ArrowLeft, Share2, Printer } from "lucide-react"
import Link from "next/link"

// Mock Grocery Data
const groceryCategories = [
    {
        name: "Produce",
        items: [
            { id: "p1", name: "Tomatoes", quantity: "1 kg", meals: ["Tomato Pappu", "Rasam"] },
            { id: "p2", name: "Onions", quantity: "1 kg", meals: ["Upma", "Sambar", "Pesarattu"] },
            { id: "p3", name: "Green Chillies", quantity: "200g", meals: ["All"] },
            { id: "p4", name: "Curry Leaves", quantity: "2 bunches", meals: ["Tempering"] },
            { id: "p5", name: "Bottle Gourd", quantity: "1 medium", meals: ["Stew"] },
            { id: "p6", name: "Brinjal", quantity: "500g", meals: ["Vankaya Vepudu", "Curry"] },
        ]
    },
    {
        name: "Grains & Dals",
        items: [
            { id: "g1", name: "Toor Dal", quantity: "500g", meals: ["Pappu", "Sambar"] },
            { id: "g2", name: "Moong Dal", quantity: "250g", meals: ["Pesarattu", "Pongal"] },
            { id: "g3", name: "Sona Masoori Rice", quantity: "5 kg", meals: ["Staple"] },
        ]
    },
    {
        name: "Dairy",
        items: [
            { id: "d1", name: "Curd / Yogurt", quantity: "1 kg", meals: ["Majjiga Pulusu", "Rice side"] },
            { id: "d2", name: "Ghee", quantity: "200g", meals: ["Pongal", "Seasoning"] },
        ]
    },
    {
        name: "Spices & Pantry",
        items: [
            { id: "s1", name: "Tamarind", quantity: "200g", meals: ["Pulihora", "Rasam"] },
            { id: "s2", name: "Mustard Seeds", quantity: "100g", meals: ["Tempering"] },
        ]
    },
]

export default function GroceryPage() {
    const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({})

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
                        {groceryCategories.map((category) => (
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
                        ))}
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}
