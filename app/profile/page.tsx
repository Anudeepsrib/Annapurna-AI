"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowRight, Utensils, Flame, Leaf } from "lucide-react"
import { toast } from "sonner"

export default function ProfilePage() {
    const [householdSize, setHouseholdSize] = useState("2")
    const [spiceLevel, setSpiceLevel] = useState("medium")
    const [dietary] = useState("vegetarian")

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        const promise = fetch("/api/python/generate-plan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ householdSize, spiceLevel, dietary }),
        })

        toast.promise(promise, {
            loading: 'Generating your authentic meal plan...',
            success: (data) => {
                // For MVP, navigate to plan directly
                window.location.href = "/plan"
                return `Plan generated successfully!`
            },
            error: 'Failed to generate plan. Is the backend running?',
        });
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
                                <Label htmlFor="expertise">Cooking Expertise</Label>
                                <Select defaultValue="intermediate">
                                    <SelectTrigger id="expertise">
                                        <SelectValue placeholder="Select level" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="beginner">Beginner (Quick & Easy)</SelectItem>
                                        <SelectItem value="intermediate">Home Cook (Standard)</SelectItem>
                                        <SelectItem value="expert">Expert (Traditional)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label>Spice Tolerance</Label>
                                <div className="grid grid-cols-3 gap-4">
                                    <Button
                                        type="button"
                                        variant={spiceLevel === "mild" ? "default" : "outline"}
                                        className="flex flex-col h-20 gap-1"
                                        onClick={() => setSpiceLevel("mild")}
                                    >
                                        <span className="text-lg">🌶️</span>
                                        <span>Mild</span>
                                    </Button>
                                    <Button
                                        type="button"
                                        variant={spiceLevel === "medium" ? "default" : "outline"}
                                        className="flex flex-col h-20 gap-1"
                                        onClick={() => setSpiceLevel("medium")}
                                    >
                                        <span className="text-lg">🌶️🌶️</span>
                                        <span>Medium</span>
                                    </Button>
                                    <Button
                                        type="button"
                                        variant={spiceLevel === "spicy" ? "default" : "outline"}
                                        className="flex flex-col h-20 gap-1"
                                        onClick={() => setSpiceLevel("spicy")}
                                    >
                                        <span className="text-lg">🌶️🌶️🌶️</span>
                                        <span>Spicy</span>
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button className="w-full h-12 text-lg" onClick={handleSubmit}>
                                Generate Weekly Plan
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            </main>
            <Footer />
        </div>
    )
}
