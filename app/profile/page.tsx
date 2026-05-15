"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ApiClient, ApiError } from "@/lib/api"
import { ArrowRight, Loader2 } from "lucide-react"
import { toast } from "sonner"

export default function ProfilePage() {
    const router = useRouter()
    const [householdSize, setHouseholdSize] = useState("2")
    const [spiceLevel, setSpiceLevel] = useState("medium")
    const [dietary, setDietary] = useState("vegetarian")
    const [allergies, setAllergies] = useState("")
    const [submitting, setSubmitting] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            const result = await ApiClient.generatePlan({
                householdSize,
                spiceLevel,
                dietary,
                allergies: allergies
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean),
            })

            if (result.source_status === "safety_guardrail") {
                toast.warning("General wellness guidance created. Review the safety notes on your plan.")
            } else {
                toast.success("Meal plan generated successfully.")
            }
            router.push("/plan")
        } catch (error) {
            const message = error instanceof ApiError
                ? error.message
                : "Failed to generate plan. Is the backend running?"
            toast.error(message)
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-10 bg-muted/20">
                <div className="container mx-auto max-w-[600px]">
                    <div className="mb-8 text-center space-y-2">
                        <h1 className="font-serif text-3xl font-bold">Your Kitchen Preferences</h1>
                        <p className="text-muted-foreground">
                            Tell us a bit about your cooking style to get a personalized Andhra-style meal plan.
                        </p>
                    </div>

                    <Card>
                        <form onSubmit={handleSubmit}>
                            <CardHeader>
                                <CardTitle>Household & Diet</CardTitle>
                                <CardDescription>
                                    Customize portion sizes and restrictions.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-2">
                                    <Label htmlFor="size">Household Size (People)</Label>
                                    <Select value={householdSize} onValueChange={setHouseholdSize}>
                                        <SelectTrigger id="size">
                                            <SelectValue placeholder="Select size" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="1">1 Person</SelectItem>
                                            <SelectItem value="2">2 People</SelectItem>
                                            <SelectItem value="3">3 People</SelectItem>
                                            <SelectItem value="4">4 People</SelectItem>
                                            <SelectItem value="5">5+ People</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="dietary">Dietary Notes</Label>
                                    <textarea
                                        id="dietary"
                                        value={dietary}
                                        onChange={(event) => setDietary(event.target.value)}
                                        className="min-h-24 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="allergies">Allergies or Avoid List</Label>
                                    <input
                                        id="allergies"
                                        value={allergies}
                                        onChange={(event) => setAllergies(event.target.value)}
                                        className="h-10 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                        placeholder="peanut, sesame"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label>Spice Tolerance</Label>
                                    <div className="grid grid-cols-3 gap-4">
                                        {(["mild", "medium", "spicy"] as const).map((level) => (
                                            <Button
                                                key={level}
                                                type="button"
                                                variant={spiceLevel === level ? "default" : "outline"}
                                                className="flex flex-col h-20 gap-1 capitalize"
                                                onClick={() => setSpiceLevel(level)}
                                            >
                                                <span>{level}</span>
                                            </Button>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                            <CardFooter>
                                <Button className="w-full h-12 text-lg" type="submit" disabled={submitting}>
                                    {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    Generate Weekly Plan
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </CardFooter>
                        </form>
                    </Card>
                </div>
            </main>
            <Footer />
        </div>
    )
}
