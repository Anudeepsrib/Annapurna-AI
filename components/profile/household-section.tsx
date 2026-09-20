import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface HouseholdSectionProps {
    householdSize: string
    spiceLevel: string
    allergies: string
    dietary: string
    onHouseholdSizeChange: (value: string) => void
    onSpiceLevelChange: (value: string) => void
    onAllergiesChange: (value: string) => void
    onDietaryChange: (value: string) => void
}

export function HouseholdSection(props: HouseholdSectionProps) {
    return (
        <section className="space-y-5">
            <div className="grid gap-5 md:grid-cols-3">
                <div className="space-y-2">
                    <Label htmlFor="size">Household Size</Label>
                    <select
                        id="size"
                        value={props.householdSize}
                        onChange={(event) => props.onHouseholdSizeChange(event.target.value)}
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
                                variant={props.spiceLevel === level ? "default" : "outline"}
                                className="h-10 capitalize"
                                onClick={() => props.onSpiceLevelChange(level)}
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
                        value={props.allergies}
                        onChange={(event) => props.onAllergiesChange(event.target.value)}
                        placeholder="peanut, sesame"
                    />
                </div>
            </div>
            <div className="space-y-2">
                <Label htmlFor="dietary">Household Notes</Label>
                <textarea
                    id="dietary"
                    value={props.dietary}
                    onChange={(event) => props.onDietaryChange(event.target.value)}
                    className="min-h-28 w-full rounded-md border border-input bg-white px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
                <p className="text-xs text-muted-foreground">
                    Keep this to cooking preferences, allergies, budget, and cultural context.
                </p>
            </div>
        </section>
    )
}
