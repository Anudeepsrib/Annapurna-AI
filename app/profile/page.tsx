"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { ApiClient, ApiError, type FamilyProfile, type PantryItem, type TeluguAndhraConstraint } from "@/lib/api"
import { ArrowRight, Loader2, Plus, ShieldCheck, Users, Wheat } from "lucide-react"
import { toast } from "sonner"

const constraintOptions: { value: TeluguAndhraConstraint; label: string; helper: string }[] = [
    { value: "vegetarian", label: "Vegetarian", helper: "Blocks meat and seafood suggestions." },
    { value: "no_egg", label: "No egg", helper: "Keeps Andhra vegetarian plans egg-free." },
    { value: "andhra_telugu_style", label: "Andhra Telugu style", helper: "Prioritizes pappu, pulusu, rice, chutneys, and home cooking." },
    { value: "rice_based_lunch", label: "Rice-based lunch", helper: "Keeps lunch familiar for Telugu households." },
    { value: "pappu_or_dal_daily", label: "Daily pappu or dal", helper: "Adds a pulse anchor across most days." },
    { value: "fermented_breakfasts_ok", label: "Fermented breakfasts OK", helper: "Allows idli, dosa, uttapam, and pesarattu." },
    { value: "mild_for_children", label: "Mild for children", helper: "Keeps spice guidance family-friendly." },
    { value: "festival_no_onion_garlic", label: "Festival no onion/garlic", helper: "Removes onion and garlic from generated plans." },
]

function parsePantryInventory(input: string): PantryItem[] {
    return input
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
            const parts = line.split("-").map((part) => part.trim()).filter(Boolean)
            const name = parts[0] || line
            const quantity = parts[1] || ""
            const expiresMatch = line.match(/(?:use within|expires in|expires)\s+(\d+)/i)
            return {
                name,
                quantity,
                category: inferPantryCategory(name),
                expiresWithinDays: expiresMatch ? Number(expiresMatch[1]) : null,
            }
        })
        .slice(0, 80)
}

function inferPantryCategory(name: string): PantryItem["category"] {
    const normalized = name.toLowerCase()
    if (/(rice|millet|ragi|wheat|rava|atta)/.test(normalized)) return "grains"
    if (/(dal|pappu|chana|gram|lentil|pesara|moong|toor)/.test(normalized)) return "dals"
    if (/(spinach|tomato|okra|brinjal|cabbage|carrot|beans|mango|cucumber)/.test(normalized)) return "vegetables"
    if (/(mustard|cumin|chili|turmeric|pepper|tamarind|curry leaves|spice)/.test(normalized)) return "spices"
    if (/(curd|milk|yogurt|paneer|dairy)/.test(normalized)) return "dairy"
    return "other"
}

export default function ProfilePage() {
    const router = useRouter()
    const [householdSize, setHouseholdSize] = useState("3")
    const [spiceLevel, setSpiceLevel] = useState("medium")
    const [dietary, setDietary] = useState("vegetarian Andhra home cooking; prefer rice lunch and pappu most days")
    const [allergies, setAllergies] = useState("")
    const [familyProfiles, setFamilyProfiles] = useState<FamilyProfile[]>([
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
    ])
    const [pantryText, setPantryText] = useState("rice - 5 kg\nmoong dal - 1 kg\nspinach - 1 bunch - use within 2 days\ntamarind - small box")
    const [teluguAndhraConstraints, setTeluguAndhraConstraints] = useState<TeluguAndhraConstraint[]>([
        "vegetarian",
        "no_egg",
        "andhra_telugu_style",
        "rice_based_lunch",
        "pappu_or_dal_daily",
        "fermented_breakfasts_ok",
        "mild_for_children",
    ])
    const [submitting, setSubmitting] = useState(false)

    const updateFamilyProfile = (index: number, patch: Partial<FamilyProfile>) => {
        setFamilyProfiles((profiles) =>
            profiles.map((profile, currentIndex) =>
                currentIndex === index ? { ...profile, ...patch } : profile,
            ),
        )
    }

    const addFamilyProfile = () => {
        setFamilyProfiles((profiles) => [
            ...profiles,
            {
                label: `Member ${profiles.length + 1}`,
                ageGroup: "adult",
                appetite: "regular",
                dietaryTags: [],
                privacyScope: "local_device_only",
            },
        ])
    }

    const toggleConstraint = (constraint: TeluguAndhraConstraint, checked: boolean) => {
        setTeluguAndhraConstraints((current) => {
            if (checked) return Array.from(new Set([...current, constraint]))
            return current.filter((item) => item !== constraint)
        })
    }

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
                familyProfiles,
                pantryInventory: parsePantryInventory(pantryText),
                teluguAndhraConstraints,
            })

            if (result.source_status === "safety_guardrail") {
                toast.warning("General wellness guidance created. Review the safety notes on your plan.")
            } else {
                toast.success("Meal plan generated with pantry-aware grocery optimization.")
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
            <main className="flex-1 bg-muted/20 py-10">
                <div className="container mx-auto max-w-[980px] px-4">
                    <div className="mb-8 grid gap-5 md:grid-cols-[1.2fr_0.8fr] md:items-end">
                        <div className="space-y-3">
                            <div className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-primary/5 px-3 py-1 text-sm font-medium text-primary">
                                <ShieldCheck className="h-4 w-4" />
                                Local-first family planning
                            </div>
                            <h1 className="font-serif text-3xl font-bold text-primary md:text-4xl">
                                Build a private Andhra Telugu meal plan
                            </h1>
                            <p className="max-w-2xl text-muted-foreground">
                                Use role labels, pantry stock, allergies, and cultural constraints. Annapurna stores the
                                planning context locally by default and treats this as wellness guidance, not medical advice.
                            </p>
                        </div>
                        <div className="rounded-lg border border-secondary/20 bg-secondary/5 p-4 text-sm text-foreground">
                            <p className="font-semibold text-primary">Family profile privacy model</p>
                            <p className="mt-1 text-muted-foreground">
                                Prefer &quot;Adult cook&quot; or &quot;Child&quot; over real names. Use age groups and appetite bands instead
                                of exact ages, weights, diagnoses, or medical history.
                            </p>
                        </div>
                    </div>

                    <Card>
                        <form onSubmit={handleSubmit}>
                            <CardHeader>
                                <CardTitle>Planning Inputs</CardTitle>
                                <CardDescription>
                                    The backend validates these rules before saving a plan or grocery list.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-8">
                                <section className="grid gap-5 md:grid-cols-3">
                                    <div className="space-y-2">
                                        <Label htmlFor="size">Household Size</Label>
                                        <select
                                            id="size"
                                            value={householdSize}
                                            onChange={(event) => setHouseholdSize(event.target.value)}
                                            className="h-10 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                        >
                                            {["1", "2", "3", "4", "5", "6"].map((size) => (
                                                <option key={size} value={size}>{size} people</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="space-y-2">
                                        <Label>Spice Tolerance</Label>
                                        <div className="grid grid-cols-3 gap-2">
                                            {(["mild", "medium", "spicy"] as const).map((level) => (
                                                <Button
                                                    key={level}
                                                    type="button"
                                                    variant={spiceLevel === level ? "default" : "outline"}
                                                    className="h-10 capitalize"
                                                    onClick={() => setSpiceLevel(level)}
                                                >
                                                    {level}
                                                </Button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="allergies">Allergies or Avoid List</Label>
                                        <Input
                                            id="allergies"
                                            value={allergies}
                                            onChange={(event) => setAllergies(event.target.value)}
                                            placeholder="peanut, sesame"
                                        />
                                    </div>
                                </section>

                                <section className="space-y-3">
                                    <div className="flex items-center gap-2">
                                        <Users className="h-5 w-5 text-primary" />
                                        <h2 className="font-serif text-xl font-bold">Family Profiles</h2>
                                    </div>
                                    <div className="grid gap-4 md:grid-cols-2">
                                        {familyProfiles.map((profile, index) => (
                                            <div key={`${profile.label}-${index}`} className="rounded-lg border bg-white p-4">
                                                <div className="grid gap-3">
                                                    <div className="space-y-2">
                                                        <Label htmlFor={`profile-label-${index}`}>Role Label</Label>
                                                        <Input
                                                            id={`profile-label-${index}`}
                                                            value={profile.label}
                                                            onChange={(event) => updateFamilyProfile(index, { label: event.target.value })}
                                                        />
                                                    </div>
                                                    <div className="grid grid-cols-2 gap-3">
                                                        <div className="space-y-2">
                                                            <Label>Age Group</Label>
                                                            <select
                                                                value={profile.ageGroup}
                                                                onChange={(event) =>
                                                                    updateFamilyProfile(index, { ageGroup: event.target.value as FamilyProfile["ageGroup"] })
                                                                }
                                                                className="h-10 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                            >
                                                                <option value="adult">Adult</option>
                                                                <option value="senior">Senior</option>
                                                                <option value="teen">Teen</option>
                                                                <option value="child">Child</option>
                                                            </select>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label>Appetite</Label>
                                                            <select
                                                                value={profile.appetite}
                                                                onChange={(event) =>
                                                                    updateFamilyProfile(index, { appetite: event.target.value as FamilyProfile["appetite"] })
                                                                }
                                                                className="h-10 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                            >
                                                                <option value="light">Light</option>
                                                                <option value="regular">Regular</option>
                                                                <option value="hearty">Hearty</option>
                                                            </select>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-2">
                                                        <Label htmlFor={`profile-tags-${index}`}>Dietary Tags</Label>
                                                        <Input
                                                            id={`profile-tags-${index}`}
                                                            value={profile.dietaryTags.join(", ")}
                                                            onChange={(event) =>
                                                                updateFamilyProfile(index, {
                                                                    dietaryTags: event.target.value
                                                                        .split(",")
                                                                        .map((item) => item.trim())
                                                                        .filter(Boolean),
                                                                })
                                                            }
                                                            placeholder="mild spice, prefers curd rice"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <Button type="button" variant="outline" onClick={addFamilyProfile} className="gap-2">
                                        <Plus className="h-4 w-4" />
                                        Add role
                                    </Button>
                                </section>

                                <section className="grid gap-6 md:grid-cols-[1fr_1fr]">
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2">
                                            <Wheat className="h-5 w-5 text-primary" />
                                            <Label htmlFor="pantry" className="text-base font-semibold">Pantry Inventory</Label>
                                        </div>
                                        <textarea
                                            id="pantry"
                                            value={pantryText}
                                            onChange={(event) => setPantryText(event.target.value)}
                                            className="min-h-40 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            One item per line. Add quantity and optional expiry note, for example:
                                            spinach - 1 bunch - use within 2 days.
                                        </p>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="dietary">Household Notes</Label>
                                        <textarea
                                            id="dietary"
                                            value={dietary}
                                            onChange={(event) => setDietary(event.target.value)}
                                            className="min-h-40 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            Keep this to cooking preferences, allergies, budget, and cultural context.
                                            Medical conditions should be reviewed with a clinician.
                                        </p>
                                    </div>
                                </section>

                                <section className="space-y-3">
                                    <h2 className="font-serif text-xl font-bold">Telugu / Andhra Dietary Constraints</h2>
                                    <div className="grid gap-3 md:grid-cols-2">
                                        {constraintOptions.map((option) => {
                                            const checked = teluguAndhraConstraints.includes(option.value)
                                            return (
                                                <label
                                                    key={option.value}
                                                    className="flex cursor-pointer gap-3 rounded-lg border bg-white p-3"
                                                >
                                                    <Checkbox
                                                        checked={checked}
                                                        onCheckedChange={(value) => toggleConstraint(option.value, value === true)}
                                                        className="mt-1"
                                                    />
                                                    <span>
                                                        <span className="block font-medium">{option.label}</span>
                                                        <span className="text-sm text-muted-foreground">{option.helper}</span>
                                                    </span>
                                                </label>
                                            )
                                        })}
                                    </div>
                                </section>
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
