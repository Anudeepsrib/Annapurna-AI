import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Clock, Users, Info } from "lucide-react"

interface MealCardProps {
    type: "Breakfast" | "Lunch" | "Dinner"
    title: string
    description: string
    time: string
    ingredients: string[]
}

export function MealCard({ type, title, description, time, ingredients }: MealCardProps) {
    return (
        <Card className="h-full flex flex-col hover:shadow-md transition-shadow border-muted/60">
            <div className="px-4 py-2 bg-muted/30 border-b border-muted flex justify-between items-center bg-[var(--background)]">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{type}</span>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {time}
                </div>
            </div>
            <CardContent className="flex-1 p-4 space-y-2">
                <h3 className="font-serif text-lg font-bold leading-tight text-primary">{title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
                <div className="pt-2 flex flex-wrap gap-1">
                    {ingredients.slice(0, 3).map((ing, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-secondary/10 text-secondary-foreground rounded-full border border-secondary/20">
                            {ing}
                        </span>
                    ))}
                    {ingredients.length > 3 && (
                        <span className="text-[10px] px-1.5 py-0.5 text-muted-foreground">+{ingredients.length - 3} more</span>
                    )}
                </div>
            </CardContent>
            <CardFooter className="p-4 pt-0">
                <Button variant="ghost" size="sm" className="w-full text-xs h-8">
                    View Recipe <Info className="ml-2 h-3 w-3" />
                </Button>
            </CardFooter>
        </Card>
    )
}
