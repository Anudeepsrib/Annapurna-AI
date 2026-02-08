"use client"

import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { WeekGrid } from "@/components/week-grid"
import { Button } from "@/components/ui/button"
import { Download, ShoppingCart } from "lucide-react"
import { PlanSkeleton } from "@/components/skeletons"
import { EvidencePanel } from "@/components/evidence-panel"
import { useGetPlan } from "@/hooks/use-plan"
import { ErrorState } from "@/components/error-state"
import { GroceryListDialog } from "@/components/grocery-list-dialog"
import { useState } from "react"

export default function PlanPage() {
    const { data: weekPlan, isLoading, isError, refetch } = useGetPlan();
    const [showGroceryList, setShowGroceryList] = useState(false);

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-10 bg-muted/20">
                <div className="container mx-auto px-4 max-w-[1400px]">
                    <div className="bg-white rounded-xl p-8 mb-8 border shadow-sm">
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                            <div className="space-y-2">
                                <h1 className="font-serif text-3xl md:text-4xl font-bold text-primary">
                                    Your Weekly Plan
                                </h1>
                                <div className="flex items-center gap-3 text-muted-foreground">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-accent" />
                                        <span className="text-sm md:text-base font-medium text-foreground">Feb 12 - Feb 18</span>
                                    </div>
                                    <span className="text-muted-foreground/50">•</span>
                                    <span className="text-sm md:text-base font-medium">Vegetarian</span>
                                    <span className="text-sm md:text-base font-medium">Andhra Style</span>
                                </div>
                            </div>
                            <div className="flex gap-3 flex-wrap">
                                <Button
                                    variant="outline"
                                    className="gap-2 bg-white hover:bg-muted font-sans"
                                >
                                    <Download className="h-4 w-4" />
                                    <span className="font-semibold">Export</span>
                                </Button>
                                <Button
                                    onClick={() => setShowGroceryList(true)}
                                    className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90 shadow-md font-sans"
                                >
                                    <ShoppingCart className="h-4 w-4" />
                                    <span className="font-semibold">Grocery List</span>
                                </Button>
                            </div>
                        </div>
                    </div>

                    {isLoading ? (
                        <PlanSkeleton />
                    ) : isError ? (
                        <ErrorState onRetry={() => refetch()} />
                    ) : (
                        <WeekGrid weekPlan={weekPlan || []} />
                    )}

                    <div className="mt-12">
                        <EvidencePanel topic="protein" />
                    </div>
                </div>
            </main>
            <Footer />
            <GroceryListDialog open={showGroceryList} onOpenChange={setShowGroceryList} />
        </div>
    )
}
