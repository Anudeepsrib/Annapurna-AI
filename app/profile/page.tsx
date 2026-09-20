"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowRight, Loader2, ShieldCheck } from "lucide-react"
import { toast } from "sonner"

import { Footer } from "@/components/footer"
import { Header } from "@/components/header"
import { ConstraintsSection } from "@/components/profile/constraints-section"
import { FamilyMembersSection } from "@/components/profile/family-members-section"
import { HouseholdSection } from "@/components/profile/household-section"
import { PantrySection } from "@/components/profile/pantry-section"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ApiClient, ApiError, type FamilyProfile, type TeluguAndhraConstraint } from "@/lib/api"

const initialProfiles: FamilyProfile[] = [
    {
        label: "Adult cook",
        ageGroup: "adult",
        appetite: "regular",
        dietaryTags: ["prefers rice lunch"],
        privacyScope: "local_device_only",
    },
    {
        label: "Child",
        ageGroup: "child",
        appetite: "light",
        dietaryTags: ["mild spice"],
        privacyScope: "meal_planning_only",
    },
]

const initialConstraints: TeluguAndhraConstraint[] = [
    "vegetarian",
    "no_egg",
    "andhra_telugu_style",
    "rice_based_lunch",
    "pappu_or_dal_daily",
    "fermented_breakfasts_ok",
    "mild_for_children",
]

export default function ProfilePage() {
    const router = useRouter()
    const [householdSize, setHouseholdSize] = useState("3")
    const [spiceLevel, setSpiceLevel] = useState("medium")
    const [dietary, setDietary] = useState("vegetarian Andhra home cooking; prefer rice lunch and pappu most days")
    const [allergies, setAllergies] = useState("")
    const [familyProfiles, setFamilyProfiles] = useState(initialProfiles)
    const [pantryText, setPantryText] = useState(
        "rice - 5 kg\nmoong dal - 1 kg\nspinach - 1 bunch - use within 2 days\ntamarind - small box",
    )
    const [constraints, setConstraints] = useState(initialConstraints)
    const [submitting, setSubmitting] = useState(false)

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault()
        setSubmitting(true)
        try {
            const result = await ApiClient.generatePlan({
                householdSize,
                spiceLevel,
                dietary,
                allergies: allergies.split(",").map((item) => item.trim()).filter(Boolean),
                familyProfiles,
                pantryText,
                teluguAndhraConstraints: constraints,
            })
            toast[result.source_status === "safety_guardrail" ? "warning" : "success"](
                result.source_status === "safety_guardrail"
                    ? "General wellness guidance created. Review the safety notes on your plan."
                    : "Meal plan generated with pantry-aware grocery optimization.",
            )
            router.push("/plan")
        } catch (error) {
            toast.error(error instanceof ApiError ? error.message : "Failed to generate plan. Is the backend running?")
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 bg-muted/20 py-10">
                <div className="container mx-auto max-w-[980px] px-4">
                    <div className="mb-8 grid gap-5 md:grid-cols-[1.2fr_0.8fr] md:items-end">
                        <div className="space-y-3">
                            <div className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-primary/5 px-3 py-1 text-sm font-medium text-primary">
                                <ShieldCheck className="h-4 w-4" /> Local-first family planning
                            </div>
                            <h1 className="font-serif text-3xl font-bold text-primary md:text-4xl">
                                Build a private Andhra Telugu meal plan
                            </h1>
                            <p className="max-w-2xl text-muted-foreground">
                                Set household preferences and hard constraints. The backend validates every generated plan.
                            </p>
                        </div>
                        <div className="rounded-lg border border-secondary/20 bg-secondary/5 p-4 text-sm">
                            <p className="font-semibold text-primary">Family profile privacy</p>
                            <p className="mt-1 text-muted-foreground">
                                Use role labels and age groups instead of real names, exact ages, weights, or diagnoses.
                            </p>
                        </div>
                    </div>

                    <Card>
                        <form onSubmit={handleSubmit}>
                            <CardHeader>
                                <CardTitle>Planning Inputs</CardTitle>
                                <CardDescription>Hard rules are validated; preferences guide candidate ranking.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-8">
                                <HouseholdSection
                                    householdSize={householdSize}
                                    spiceLevel={spiceLevel}
                                    allergies={allergies}
                                    dietary={dietary}
                                    onHouseholdSizeChange={setHouseholdSize}
                                    onSpiceLevelChange={setSpiceLevel}
                                    onAllergiesChange={setAllergies}
                                    onDietaryChange={setDietary}
                                />
                                <FamilyMembersSection profiles={familyProfiles} onChange={setFamilyProfiles} />
                                <PantrySection value={pantryText} onChange={setPantryText} />
                                <ConstraintsSection value={constraints} onChange={setConstraints} />
                            </CardContent>
                            <CardFooter>
                                <Button className="h-12 w-full text-lg" type="submit" disabled={submitting}>
                                    {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    Generate Private Weekly Plan
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
