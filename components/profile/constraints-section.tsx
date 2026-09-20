import { Checkbox } from "@/components/ui/checkbox"
import type { TeluguAndhraConstraint } from "@/lib/api"

const options: { value: TeluguAndhraConstraint; label: string; helper: string }[] = [
    { value: "vegetarian", label: "Vegetarian", helper: "Blocks meat and seafood suggestions." },
    { value: "no_egg", label: "No egg", helper: "Keeps plans egg-free." },
    { value: "andhra_telugu_style", label: "Andhra Telugu style", helper: "Prioritizes familiar home cooking." },
    { value: "rice_based_lunch", label: "Rice-based lunch", helper: "Prefers familiar Telugu lunches." },
    { value: "pappu_or_dal_daily", label: "Daily pappu or dal", helper: "Raises pulse frequency in ranking." },
    { value: "fermented_breakfasts_ok", label: "Fermented breakfasts OK", helper: "Allows idli, dosa, and uttapam." },
    { value: "mild_for_children", label: "Mild for children", helper: "Prefers child-friendly spice." },
    { value: "festival_no_onion_garlic", label: "Festival no onion/garlic", helper: "Strictly blocks onion and garlic." },
]

interface ConstraintsSectionProps {
    value: TeluguAndhraConstraint[]
    onChange: (value: TeluguAndhraConstraint[]) => void
}

export function ConstraintsSection({ value, onChange }: ConstraintsSectionProps) {
    const toggle = (constraint: TeluguAndhraConstraint, checked: boolean) => {
        onChange(checked ? Array.from(new Set([...value, constraint])) : value.filter((item) => item !== constraint))
    }
    return (
        <section className="space-y-3">
            <h2 className="font-serif text-xl font-bold">Telugu / Andhra Dietary Constraints</h2>
            <div className="grid gap-3 md:grid-cols-2">
                {options.map((option) => (
                    <label key={option.value} className="flex cursor-pointer gap-3 rounded-lg border bg-white p-3">
                        <Checkbox
                            checked={value.includes(option.value)}
                            onCheckedChange={(checked) => toggle(option.value, checked === true)}
                            className="mt-1"
                        />
                        <span>
                            <span className="block font-medium">{option.label}</span>
                            <span className="text-sm text-muted-foreground">{option.helper}</span>
                        </span>
                    </label>
                ))}
            </div>
        </section>
    )
}
