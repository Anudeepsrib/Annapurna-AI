"use client"

import { useState } from "react"
import { MealCard } from "@/components/meal-card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight } from "lucide-react"

// Mock Data Type
interface DayPlan {
    day: string
    date: string
    meals: {
        breakfast: {
            title: string
            description: string
            ingredients: string[]
            time?: string
        }
        lunch: {
            title: string
            description: string
            ingredients: string[]
            time?: string
        }
        dinner: {
            title: string
            description: string
            ingredients: string[]
            time?: string
        }
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
        <div className="space-y-10">
            {/* HORIZONTAL CALENDAR STRIP - Clean Design */}
            <div className="relative">
                {/* Desktop Navigation Arrows */}
                <div className="hidden md:flex absolute -left-4 top-1/2 -translate-y-1/2 z-10">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={prevDay}
                        className="h-10 w-10 rounded-full bg-white shadow border border-border hover:bg-muted"
                    >
                        <ChevronLeft className="h-5 w-5" />
                    </Button>
                </div>
                <div className="hidden md:flex absolute -right-4 top-1/2 -translate-y-1/2 z-10">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={nextDay}
                        className="h-10 w-10 rounded-full bg-white shadow border border-border hover:bg-muted"
                    >
                        <ChevronRight className="h-5 w-5" />
                    </Button>
                </div>

                {/* Calendar Track */}
                <div className="flex overflow-x-auto scrollbar-hide py-4 px-2 -mx-2 snap-x snap-mandatory gap-2 md:justify-center">
                    {weekPlan.map((day, index) => {
                        const isSelected = selectedDayIndex === index
                        return (
                            <button
                                key={index}
                                onClick={() => setSelectedDayIndex(index)}
                                className={cn(
                                    "flex-shrink-0 snap-center flex flex-col items-center justify-center transition-all duration-300 rounded-xl relative overflow-hidden h-24 w-16 gap-1 border",
                                    isSelected
                                        ? "bg-primary text-primary-foreground border-primary shadow-md scale-105"
                                        : "bg-white text-muted-foreground border-border hover:bg-muted/50"
                                )}
                            >
                                <span className="text-xs font-semibold uppercase tracking-wider opacity-80">
                                    {day.day.substring(0, 3)}
                                </span>
                                <span className={cn(
                                    "text-2xl font-bold font-serif",
                                    isSelected ? "scale-110" : "scale-100"
                                )}>
                                    {day.date.split(' ')[1]}
                                </span>
                                {isSelected && (
                                    <div className="w-1.5 h-1.5 rounded-full bg-accent mt-1" />
                                )}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* DAILY FOCUSED VIEW - Clean & Minimal */}
            <div className="space-y-6">
                <div className="text-center space-y-2">
                    <h2 className="font-serif text-3xl md:text-4xl font-bold text-primary">
                        {selectedDay.day}, {selectedDay.date}
                    </h2>
                    <p className="text-muted-foreground text-sm uppercase tracking-wide font-medium">
                        Today's Menu
                    </p>
                </div>

                <div className="relative overflow-hidden bg-white/50 rounded-2xl p-2 md:p-6 border border-border/40">
                    <div className="flex overflow-x-auto scrollbar-hide snap-x snap-mandatory gap-4 md:gap-6 pb-6 pt-2 items-stretch px-2 md:justify-center">
                        {/* Breakfast */}
                        <div className="flex-shrink-0 w-[280px] md:w-[320px] snap-center">
                            <MealCard
                                type="Breakfast"
                                title={selectedDay.meals.breakfast.title}
                                description={selectedDay.meals.breakfast.description}
                                time={selectedDay.meals.breakfast.time || "8:00 AM"}
                                ingredients={selectedDay.meals.breakfast.ingredients}
                            />
                        </div>

                        {/* Lunch */}
                        <div className="flex-shrink-0 w-[280px] md:w-[320px] snap-center">
                            <MealCard
                                type="Lunch"
                                title={selectedDay.meals.lunch.title}
                                description={selectedDay.meals.lunch.description}
                                time={selectedDay.meals.lunch.time || "1:00 PM"}
                                ingredients={selectedDay.meals.lunch.ingredients}
                            />
                        </div>

                        {/* Dinner */}
                        <div className="flex-shrink-0 w-[280px] md:w-[320px] snap-center">
                            <MealCard
                                type="Dinner"
                                title={selectedDay.meals.dinner.title}
                                description={selectedDay.meals.dinner.description}
                                time={selectedDay.meals.dinner.time || "7:30 PM"}
                                ingredients={selectedDay.meals.dinner.ingredients}
                            />
                        </div>
                    </div>

                    {/* Simple Scroll Hint */}
                    <div className="hidden md:flex absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground/30 animate-pulse">
                        <ChevronRight className="h-8 w-8" />
                    </div>
                </div>
            </div>
        </div>
    )
}
