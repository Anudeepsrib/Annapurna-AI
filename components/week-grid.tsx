"use client"

import { useState } from "react"
import { MealCard } from "@/components/meal-card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight, Sun, Sunrise, Moon } from "lucide-react"

// Mock Data Type
interface DayPlan {
    day: string
    date: string
    meals: {
        breakfast: any
        lunch: any
        dinner: any
    }
}

interface WeekGridProps {
    weekPlan: DayPlan[]
}

export function WeekGrid({ weekPlan }: WeekGridProps) {
    const [selectedDayIndex, setSelectedDayIndex] = useState(0)

    const nextDay = () => setSelectedDayIndex((prev) => (prev + 1) % 7)
    const prevDay = () => setSelectedDayIndex((prev) => (prev - 1 + 7) % 7)

    const selectedDay = weekPlan[selectedDayIndex]

    if (!selectedDay) return null

    return (
        <div className="space-y-8">
            {/* Weekly Navigation Rail */}
            <div className="flex flex-col space-y-4">
                <div className="flex items-center justify-between md:justify-center gap-4">
                    <Button variant="ghost" size="icon" onClick={prevDay} className="md:hidden">
                        <ChevronLeft className="h-4 w-4" />
                    </Button>

                    <div className="flex overflow-x-auto pb-2 gap-2 md:gap-4 no-scrollbar max-w-full snap-x">
                        {weekPlan.map((day, i) => (
                            <button
                                key={i}
                                onClick={() => setSelectedDayIndex(i)}
                                className={cn(
                                    "flex flex-col items-center justify-center min-w-[4.5rem] py-3 px-2 rounded-2xl transition-all duration-300 snap-center border-2",
                                    selectedDayIndex === i
                                        ? "bg-primary text-primary-foreground border-primary shadow-lg scale-105"
                                        : "bg-muted/30 hover:bg-muted/50 text-muted-foreground border-transparent"
                                )}
                            >
                                <span className="text-xs font-medium uppercase tracking-wider opacity-90">{day.day.substring(0, 3)}</span>
                                <span className={cn(
                                    "text-lg font-bold font-serif",
                                    selectedDayIndex === i ? "text-white" : "text-foreground"
                                )}>
                                    {day.date.split(' ')[1]}
                                </span>
                            </button>
                        ))}
                    </div>

                    <Button variant="ghost" size="icon" onClick={nextDay} className="md:hidden">
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            {/* Daily Focused View */}
            <div className="bg-card rounded-3xl p-6 md:p-10 shadow-lg border border-border animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="text-center mb-10">
                    <h2 className="font-serif text-3xl md:text-4xl font-bold text-primary mb-2">
                        {selectedDay.day}
                    </h2>
                    <p className="text-muted-foreground uppercase tracking-widest text-sm font-medium">
                        {selectedDay.date} • Menu
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {/* Breakfast */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-accent pb-2 border-b border-muted">
                            <Sunrise className="h-6 w-6" />
                            <h3 className="font-serif text-xl font-bold">Breakfast</h3>
                        </div>
                        <MealCard type="Breakfast" {...selectedDay.meals.breakfast} />
                    </div>

                    {/* Lunch */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-primary pb-2 border-b border-muted">
                            <Sun className="h-6 w-6" />
                            <h3 className="font-serif text-xl font-bold">Lunch</h3>
                        </div>
                        <MealCard type="Lunch" {...selectedDay.meals.lunch} />
                    </div>

                    {/* Dinner */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-secondary pb-2 border-b border-muted">
                            <Moon className="h-6 w-6" />
                            <h3 className="font-serif text-xl font-bold">Dinner</h3>
                        </div>
                        <MealCard type="Dinner" {...selectedDay.meals.dinner} />
                    </div>
                </div>
            </div>
        </div>
    )
}
