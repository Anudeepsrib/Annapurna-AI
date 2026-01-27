"use client"

import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { WeekGrid } from "@/components/week-grid"
import { Button } from "@/components/ui/button"
import { Download, ShoppingCart } from "lucide-react"
import { useEffect, useState } from "react"

const defaultWeekPlan = [] // Empty initially, fetched from backend

export default function PlanPage() {
    const [weekPlan, setWeekPlan] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch("http://localhost:8000/api/plan")
            .then(res => res.json())
            .then(data => {
                setWeekPlan(data)
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to fetch plan:", err)
                setLoading(false)
            })
    }, [])

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-10 bg-muted/20">
                <div className="container mx-auto px-4 max-w-[1400px]">
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
                        <div>
                            <h1 className="font-serif text-3xl font-bold">Your Weekly Plan</h1>
                            <p className="text-muted-foreground mt-1">Feb 12 - Feb 18 • Vegetarian • Andhra Style</p>
                        </div>
                        <div className="flex gap-3 flex-wrap">
                            {/* Link to Grocery List would go here */}
                            <Button variant="outline" className="gap-2">
                                <Download className="h-4 w-4" /> Export
                            </Button>
                            <Button className="gap-2">
                                <ShoppingCart className="h-4 w-4" /> View Grocery List
                            </Button>
                        </div>
                    </div>

                    {loading ? (
                        <div className="text-center py-20">Loading plan...</div>
                    ) : (
                        <WeekGrid weekPlan={weekPlan} />
                    )}
                </div>
            </main>
            <Footer />
        </div>
    )
}
