import { Plus, Users } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { FamilyProfile } from "@/lib/api"

interface FamilyMembersSectionProps {
    profiles: FamilyProfile[]
    onChange: (profiles: FamilyProfile[]) => void
}

export function FamilyMembersSection({ profiles, onChange }: FamilyMembersSectionProps) {
    const update = (index: number, patch: Partial<FamilyProfile>) => {
        onChange(profiles.map((profile, current) => current === index ? { ...profile, ...patch } : profile))
    }
    const add = () => onChange([
        ...profiles,
        {
            label: `Member ${profiles.length + 1}`,
            ageGroup: "adult",
            appetite: "regular",
            dietaryTags: [],
            privacyScope: "local_device_only",
        },
    ])

    return (
        <section className="space-y-3">
            <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                <h2 className="font-serif text-xl font-bold">Family Profiles</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
                {profiles.map((profile, index) => (
                    <div key={`${profile.label}-${index}`} className="grid gap-3 rounded-lg border bg-white p-4">
                        <div className="space-y-2">
                            <Label htmlFor={`profile-label-${index}`}>Role Label</Label>
                            <Input
                                id={`profile-label-${index}`}
                                value={profile.label}
                                onChange={(event) => update(index, { label: event.target.value })}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-2">
                                <Label>Age Group</Label>
                                <select
                                    value={profile.ageGroup}
                                    onChange={(event) => update(index, { ageGroup: event.target.value as FamilyProfile["ageGroup"] })}
                                    className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm"
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
                                    onChange={(event) => update(index, { appetite: event.target.value as FamilyProfile["appetite"] })}
                                    className="h-10 w-full rounded-md border border-input bg-white px-3 text-sm"
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
                                onChange={(event) => update(index, {
                                    dietaryTags: event.target.value.split(",").map((item) => item.trim()).filter(Boolean),
                                })}
                                placeholder="mild spice, prefers curd rice"
                            />
                        </div>
                    </div>
                ))}
            </div>
            <Button type="button" variant="outline" onClick={add} className="gap-2">
                <Plus className="h-4 w-4" /> Add role
            </Button>
        </section>
    )
}
