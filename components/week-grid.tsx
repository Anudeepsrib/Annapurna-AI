"use client"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { AlertCircle, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react"
import { useMemo, useState } from "react"
import { toast } from "sonner"

import { MealCard } from "@/components/meal-card"
import { Button } from "@/components/ui/button"
import { ApiClient, ApiError, type DayPlan, type TodayMeal } from "@/lib/api"
import { cn } from "@/lib/utils"

interface WeekGridProps {
    weekPlan: DayPlan[]
}

export function WeekGrid({ weekPlan }: WeekGridProps) {
    const queryClient = useQueryClient()
    const [selectedDayIndex, setSelectedDayIndex] = useState(0)
    const dayCount = weekPlan.length
    const selectedDay = weekPlan[selectedDayIndex]
    const safetyNotes = useMemo(
        () => Array.from(new Set(weekPlan.flatMap((day) => day.safety_notes || []))),
        [weekPlan],
    )
    const mealMutation = useMutation({
        mutationFn: async (action: {
            kind: "lock" | "replace"
            day: string
            mealType: TodayMeal["mealType"]
            locked?: boolean
        }) => action.kind === "lock"
            ? ApiClient.setMealLock(action.day, action.mealType, Boolean(action.locked))
            : ApiClient.replaceMeal(action.day, action.mealType),
        onSuccess: async () => {
            await Promise.all([
                queryClient.invalidateQueries({ queryKey: ["weekPlan"] }),
                queryClient.invalidateQueries({ queryKey: ["groceryList"] }),
                queryClient.invalidateQueries({ queryKey: ["today"] }),
            ])
        },
        onError: (error) => toast.error(error instanceof ApiError ? error.message : "Could not update the meal."),
    })
    const dayMutation = useMutation({
        mutationFn: () => ApiClient.regenerateDay(selectedDay.day),
        onSuccess: async () => {
            toast.success("Regenerated unlocked meals for this day.")
            await Promise.all([
                queryClient.invalidateQueries({ queryKey: ["weekPlan"] }),
                queryClient.invalidateQueries({ queryKey: ["groceryList"] }),
                queryClient.invalidateQueries({ queryKey: ["today"] }),
            ])
        },
        onError: (error) => toast.error(error instanceof ApiError ? error.message : "Could not regenerate the day."),
    })

    const mealActions = (mealType: TodayMeal["mealType"], locked?: boolean) => ({
        locked,
        busy: mealMutation.isPending,
        onLockChange: (next: boolean) => mealMutation.mutate({
            kind: "lock", day: selectedDay.day, mealType, locked: next,
        }),
        onReplace: () => mealMutation.mutate({ kind: "replace", day: selectedDay.day, mealType }),
    })

    if (!dayCount || !selectedDay) {
        return (
            <div className="rounded-lg border border-border bg-white p-8 text-center text-muted-foreground">
                No plan has been generated yet.
            </div>
        )
    }

    const nextDay = () => setSelectedDayIndex((prev) => (prev + 1) % dayCount)
    const prevDay = () => setSelectedDayIndex((prev) => (prev - 1 + dayCount) % dayCount)

    return (
        <div className="space-y-10">
            {safetyNotes.length > 0 && (
                <div className="flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                    <AlertCircle className="h-5 w-5 shrink-0" />
                    <div className="space-y-1">
                        {safetyNotes.slice(0, 3).map((note) => (
                            <p key={note}>{note}</p>
                        ))}
                    </div>
                </div>
            )}

            <div className="relative">
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

                <div className="flex overflow-x-auto scrollbar-hide py-4 px-2 -mx-2 snap-x snap-mandatory gap-2 md:justify-center">
                    {weekPlan.map((day, index) => {
                        const isSelected = selectedDayIndex === index
                        return (
                            <button
                                key={`${day.day}-${day.date}`}
                                onClick={() => setSelectedDayIndex(index)}
                                className={cn(
                                    "flex-shrink-0 snap-center flex flex-col items-center justify-center transition-all duration-300 rounded-xl relative overflow-hidden h-24 w-16 gap-1 border",
                                    isSelected
                                        ? "bg-primary text-primary-foreground border-primary shadow-md scale-105"
                                        : "bg-white text-muted-foreground border-border hover:bg-muted/50",
                                )}
                            >
                                <span className="text-xs font-semibold uppercase tracking-wider opacity-80">
                                    {day.day.substring(0, 3)}
                                </span>
                                <span
                                    className={cn(
                                        "text-2xl font-bold font-serif",
                                        isSelected ? "scale-110" : "scale-100",
                                    )}
                                >
                                    {day.date.split(" ")[1] || index + 1}
                                </span>
                                {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-accent mt-1" />}
                            </button>
                        )
                    })}
                </div>
            </div>

            <div className="space-y-6">
                <div className="text-center space-y-2">
                    <h2 className="font-serif text-3xl md:text-4xl font-bold text-primary">
                        {selectedDay.day}, {selectedDay.date}
                    </h2>
                    <p className="text-muted-foreground text-sm uppercase tracking-wide font-medium">
                        Today&apos;s Menu
                    </p>
                    {selectedDay.guestCount ? (
                        <p className="text-sm font-medium text-secondary">Planning for {selectedDay.guestCount} guest(s)</p>
                    ) : null}
                    <Button
                        variant="outline"
                        size="sm"
                        disabled={dayMutation.isPending || mealMutation.isPending}
                        onClick={() => dayMutation.mutate()}
                    >
                        <RefreshCw className="mr-2 h-3.5 w-3.5" /> Refresh unlocked meals
                    </Button>
                </div>

                <div className="relative overflow-hidden bg-white/50 rounded-2xl p-2 md:p-6 border border-border/40">
                    <div className="flex overflow-x-auto scrollbar-hide snap-x snap-mandatory gap-4 md:gap-6 pb-6 pt-2 items-stretch px-2 md:justify-center">
                        <div className="flex-shrink-0 w-[280px] md:w-[320px] snap-center">
                            <MealCard
                                type="Breakfast"
                                title={selectedDay.meals.breakfast.title}
                                description={selectedDay.meals.breakfast.description}
                                time={selectedDay.meals.breakfast.time || "8:00 AM"}
                                ingredients={selectedDay.meals.breakfast.ingredients}
                                nutrition={selectedDay.meals.breakfast.nutrition}
                                confidence={selectedDay.meals.breakfast.confidence}
                                disclaimer={selectedDay.meals.breakfast.disclaimer}
                                {...mealActions("breakfast", selectedDay.meals.breakfast.locked)}
                            />
                        </div>

                        <div className="flex-shrink-0 w-[280px] md:w-[320px] snap-center">
                            <MealCard
                                type="Lunch"
                                title={selectedDay.meals.lunch.title}
                                description={selectedDay.meals.lunch.description}
                                time={selectedDay.meals.lunch.time || "1:00 PM"}
                                ingredients={selectedDay.meals.lunch.ingredients}
                                nutrition={selectedDay.meals.lunch.nutrition}
                                confidence={selectedDay.meals.lunch.confidence}
                                disclaimer={selectedDay.meals.lunch.disclaimer}
                                {...mealActions("lunch", selectedDay.meals.lunch.locked)}
                            />
                        </div>

                        <div className="flex-shrink-0 w-[280px] md:w-[320px] snap-center">
                            <MealCard
                                type="Dinner"
                                title={selectedDay.meals.dinner.title}
                                description={selectedDay.meals.dinner.description}
                                time={selectedDay.meals.dinner.time || "7:30 PM"}
                                ingredients={selectedDay.meals.dinner.ingredients}
                                nutrition={selectedDay.meals.dinner.nutrition}
                                confidence={selectedDay.meals.dinner.confidence}
                                disclaimer={selectedDay.meals.dinner.disclaimer}
                                {...mealActions("dinner", selectedDay.meals.dinner.locked)}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
