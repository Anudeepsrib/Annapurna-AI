"use client"

import { useState } from "react"
import { MealCard } from "@/components/meal-card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChevronLeft, ChevronRight } from "lucide-react"

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
    const [currentDayIndex, setCurrentDayIndex] = useState(0)

    // For mobile view (Day by Day)
    const currentDay = weekPlan[currentDayIndex]

    const nextDay = () => setCurrentDayIndex((prev) => (prev + 1) % 7)
    const prevDay = () => setCurrentDayIndex((prev) => (prev - 1 + 7) % 7)

    return (
        <div className="space-y-6">
            {/* Mobile/Tablet View (Tabs/Carousel) - Visible only on smaller screens usually, but for MVP we can use Tabs for all */}

            <div className="flex items-center justify-between md:hidden pb-4">
                <Button variant="ghost" size="icon" onClick={prevDay}>
                    <ChevronLeft className="h-4 w-4" />
                </Button>
                <div className="text-center">
                    <h3 className="font-serif text-xl font-bold">{currentDay.day}</h3>
                    <p className="text-xs text-muted-foreground">{currentDay.date}</p>
                </div>
                <Button variant="ghost" size="icon" onClick={nextDay}>
                    <ChevronRight className="h-4 w-4" />
                </Button>
            </div>

            <div className="md:hidden space-y-4">
                <MealCard type="Breakfast" {...currentDay.meals.breakfast} />
                <MealCard type="Lunch" {...currentDay.meals.lunch} />
                <MealCard type="Dinner" {...currentDay.meals.dinner} />
            </div>

            {/* Desktop Grid View */}
            <div className="hidden md:grid grid-cols-7 gap-4 min-w-[1000px] overflow-x-auto pb-4">
                {weekPlan.map((day, i) => (
                    <div key={i} className="space-y-4 min-w-[200px]">
                        <div className="text-center pb-2 border-b border-muted">
                            <h3 className="font-serif font-bold text-primary">{day.day}</h3>
                            <p className="text-xs text-muted-foreground">{day.date}</p>
                        </div>
                        <MealCard type="Breakfast" {...day.meals.breakfast} />
                        <MealCard type="Lunch" {...day.meals.lunch} />
                        <MealCard type="Dinner" {...day.meals.dinner} />
                    </div>
                ))}
            </div>
        </div>
    )
}
