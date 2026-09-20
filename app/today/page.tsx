"use client"

import Link from "next/link"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Clock3, Loader2, PackageOpen, Send, ShoppingBasket } from "lucide-react"
import { toast } from "sonner"

import { Footer } from "@/components/footer"
import { Header } from "@/components/header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ApiClient, ApiError, type FeedbackSignal, type MealStatus, type TodayMeal } from "@/lib/api"

const statuses: [MealStatus, string][] = [
    ["COOKED", "Cooked"],
    ["SKIPPED", "Skipped"],
    ["LEFTOVER", "Saved leftovers"],
    ["ATE_OUT", "Ate outside"],
    ["REPLACED", "Replaced"],
]

const signals: [FeedbackSignal, string][] = [
    ["LIKED", "Liked"],
    ["DISLIKED", "Disliked"],
    ["TOO_SPICY", "Too spicy"],
    ["TOO_MUCH_WORK", "Too much work"],
    ["WOULD_REPEAT", "Would repeat"],
    ["WOULD_NOT_REPEAT", "Would not repeat"],
]

export default function TodayPage() {
    const queryClient = useQueryClient()
    const [command, setCommand] = useState("")
    const today = useQuery({ queryKey: ["today"], queryFn: ApiClient.getToday })
    const statusMutation = useMutation({
        mutationFn: ({ meal, status, details }: {
            meal: TodayMeal
            status: MealStatus
            details?: { servingsRemaining?: number; usableUntil?: string }
        }) => ApiClient.setMealStatus(today.data!.day, meal.mealType, status, details),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["today"] }),
        onError: showError,
    })
    const feedbackMutation = useMutation({
        mutationFn: ({ meal, signal }: { meal: TodayMeal; signal: FeedbackSignal }) =>
            ApiClient.recordMealFeedback(today.data!.day, meal.mealType, signal),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["today"] }),
        onError: showError,
    })
    const commandMutation = useMutation({
        mutationFn: ApiClient.sendCommand,
        onSuccess: (result) => {
            setCommand("")
            toast.success(`Applied ${result.command.type.replaceAll("_", " ").toLowerCase()}.`)
            queryClient.invalidateQueries({ queryKey: ["today"] })
            queryClient.invalidateQueries({ queryKey: ["weekPlan"] })
            queryClient.invalidateQueries({ queryKey: ["groceryList"] })
        },
        onError: showError,
    })
    const leftoverMutation = useMutation({
        mutationFn: (leftoverId: number) => ApiClient.updateLeftover(leftoverId, { consumed: true }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["today"] }),
        onError: showError,
    })
    const useLeftoverMutation = useMutation({
        mutationFn: (leftoverId: number) => ApiClient.assignLeftover(leftoverId, today.data!.day, "dinner"),
        onSuccess: () => {
            toast.success("Leftovers scheduled for dinner.")
            queryClient.invalidateQueries({ queryKey: ["today"] })
            queryClient.invalidateQueries({ queryKey: ["weekPlan"] })
            queryClient.invalidateQueries({ queryKey: ["groceryList"] })
        },
        onError: showError,
    })

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 bg-muted/20 py-10">
                <div className="container mx-auto max-w-6xl space-y-8 px-4">
                    <div>
                        <p className="text-sm font-medium uppercase tracking-wide text-secondary">Daily cooking</p>
                        <h1 className="font-serif text-4xl font-bold">Today</h1>
                        <p className="mt-2 text-muted-foreground">
                            {today.data ? `${today.data.day} · ${today.data.date}` : "Meals, prep, and household follow-through."}
                        </p>
                    </div>

                    <Card>
                        <CardContent className="flex flex-col gap-3 pt-6 sm:flex-row">
                            <Input
                                value={command}
                                onChange={(event) => setCommand(event.target.value)}
                                placeholder="Try: Use the spinach tomorrow"
                                aria-label="Household command"
                                onKeyDown={(event) => {
                                    if (event.key === "Enter" && command.trim()) commandMutation.mutate(command)
                                }}
                            />
                            <Button
                                className="gap-2"
                                disabled={!command.trim() || commandMutation.isPending}
                                onClick={() => commandMutation.mutate(command)}
                            >
                                <Send className="h-4 w-4" /> Apply
                            </Button>
                        </CardContent>
                    </Card>

                    {today.isLoading ? (
                        <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin" /></div>
                    ) : today.isError ? (
                        <Card><CardContent className="py-10 text-center">Could not load today&apos;s plan.</CardContent></Card>
                    ) : !today.data?.planAvailable ? (
                        <Card><CardContent className="space-y-3 py-10 text-center">
                            <p>No weekly plan is available yet.</p><Button asChild><Link href="/profile">Generate a plan</Link></Button>
                        </CardContent></Card>
                    ) : (
                        <>
                            <div className="grid gap-5 lg:grid-cols-3">
                                {today.data.meals.map((meal) => (
                                    <TodayMealCard
                                        key={meal.mealType}
                                        meal={meal}
                                        busy={statusMutation.isPending || feedbackMutation.isPending}
                                        onStatus={(status, details) => statusMutation.mutate({ meal, status, details })}
                                        onFeedback={(signal) => feedbackMutation.mutate({ meal, signal })}
                                    />
                                ))}
                            </div>
                            <div className="grid gap-5 md:grid-cols-2">
                                <Card>
                                    <CardHeader><CardTitle className="flex gap-2"><Clock3 className="h-5 w-5" /> Use soon</CardTitle></CardHeader>
                                    <CardContent className="space-y-2">
                                        {today.data.expiringPantry.length ? today.data.expiringPantry.map((item) => (
                                            <div key={item.id} className="flex justify-between rounded-lg border p-3">
                                                <span>{item.displayName}</span><Badge variant="outline">{item.quantityText || "Available"}</Badge>
                                            </div>
                                        )) : <p className="text-sm text-muted-foreground">Nothing expires in the next five days.</p>}
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardHeader><CardTitle className="flex gap-2"><PackageOpen className="h-5 w-5" /> Leftovers</CardTitle></CardHeader>
                                    <CardContent className="space-y-2">
                                        {today.data.leftovers.length ? today.data.leftovers.map((item) => (
                                            <div key={item.id} className="flex items-center justify-between gap-3 rounded-lg border p-3">
                                                <div><p className="font-medium">{item.title}</p>
                                                <p className="text-sm text-muted-foreground">{item.servingsRemaining} serving(s), use by {new Date(item.usableUntil).toLocaleDateString()}</p></div>
                                                <div className="flex gap-2">
                                                    <Button size="sm" variant="outline" disabled={useLeftoverMutation.isPending} onClick={() => useLeftoverMutation.mutate(item.id)}>Dinner</Button>
                                                    <Button size="sm" variant="outline" disabled={leftoverMutation.isPending} onClick={() => leftoverMutation.mutate(item.id)}>Used up</Button>
                                                </div>
                                            </div>
                                        )) : <p className="text-sm text-muted-foreground">No active leftovers.</p>}
                                    </CardContent>
                                </Card>
                            </div>
                        </>
                    )}
                </div>
            </main>
            <Footer />
        </div>
    )
}

function TodayMealCard({ meal, busy, onStatus, onFeedback }: {
    meal: TodayMeal
    busy: boolean
    onStatus: (status: MealStatus, details?: { servingsRemaining?: number; usableUntil?: string }) => void
    onFeedback: (signal: FeedbackSignal) => void
}) {
    return (
        <Card className="flex h-full flex-col">
            <CardHeader>
                <div className="flex items-center justify-between gap-2">
                    <CardDescription className="capitalize">{meal.mealType}</CardDescription>
                    {meal.status ? <Badge>{meal.status.replaceAll("_", " ").toLowerCase()}</Badge> : null}
                </div>
                <CardTitle>{meal.meal.title}</CardTitle>
                <CardDescription>{meal.meal.description}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col gap-4">
                <div>
                    <p className="text-xs font-semibold uppercase tracking-wide">Prep</p>
                    <p className="mt-1 text-sm text-muted-foreground">Gather {meal.meal.ingredients.join(", ")}.</p>
                </div>
                {meal.missingIngredients.length ? (
                    <div className="rounded-lg border border-accent/30 bg-accent/10 p-3 text-sm">
                        <ShoppingBasket className="mr-2 inline h-4 w-4" /> Missing: {meal.missingIngredients.join(", ")}
                    </div>
                ) : <p className="text-sm text-secondary">Pantry covers the listed ingredients.</p>}
                <div className="mt-auto space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-wide">What happened?</p>
                    <div className="flex flex-wrap gap-2">
                        {statuses.map(([status, label]) => (
                            <Button key={status} size="sm" variant={meal.status === status ? "default" : "outline"} disabled={busy} onClick={() => {
                                if (status !== "LEFTOVER") return onStatus(status)
                                const servings = Number(window.prompt("Servings remaining", "1"))
                                if (!Number.isInteger(servings) || servings < 1 || servings > 24) return
                                const date = new Date(Date.now() + 2 * 86400000).toISOString().slice(0, 10)
                                const usableUntil = window.prompt("Use by (YYYY-MM-DD)", date)
                                if (!usableUntil) return
                                const parsed = new Date(`${usableUntil}T23:59:59Z`)
                                if (Number.isNaN(parsed.getTime())) return toast.error("Enter a valid date as YYYY-MM-DD.")
                                onStatus(status, { servingsRemaining: servings, usableUntil: parsed.toISOString() })
                            }}>{label}</Button>
                        ))}
                    </div>
                    <p className="pt-2 text-xs font-semibold uppercase tracking-wide">Quick feedback</p>
                    <div className="flex flex-wrap gap-2">
                        {signals.map(([signal, label]) => (
                            <Button key={signal} size="sm" variant={meal.feedback.includes(signal) ? "secondary" : "ghost"} disabled={busy} onClick={() => onFeedback(signal)}>{label}</Button>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}

function showError(error: Error) {
    toast.error(error instanceof ApiError ? error.message : "Could not update meal activity.")
}
