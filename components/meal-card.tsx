import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Clock, Info, ChefHat, Flame } from "lucide-react"

interface MealCardProps {
    type: "Breakfast" | "Lunch" | "Dinner"
    title: string
    description: string
    time: string
    ingredients: string[]
}

export function MealCard({ type, title, description, time, ingredients }: MealCardProps) {
    return (
        <Card className="h-full flex flex-col hover:shadow-lg transition-all duration-300 border bg-white overflow-hidden">
            {/* Card Header */}
            <div className="px-4 py-3 bg-muted/30 border-b border-border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="bg-primary/10 p-2 rounded-lg">
                            <ChefHat className="h-4 w-4 text-primary" />
                        </div>
                        <span className="text-xs font-bold text-primary uppercase tracking-widest">{type}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-white px-3 py-1.5 rounded-full border border-border">
                        <Clock className="h-3.5 w-3.5" />
                        <span className="font-semibold">{time}</span>
                    </div>
                </div>
            </div>

            {/* Card Content */}
            <CardContent className="flex-1 p-4 space-y-3">
                {/* Title */}
                <div className="space-y-1.5">
                    <h3 className="font-serif text-lg font-bold leading-tight text-foreground break-words">
                        {title}
                    </h3>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
                    {description}
                </p>

                {/* Ingredients Section */}
                <div className="pt-2 space-y-2">
                    <div className="flex items-center gap-2">
                        <Flame className="h-3 w-3 text-primary" />
                        <span className="text-[10px] text-foreground/70 uppercase tracking-wider font-bold">Key Ingredients</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                        {ingredients.slice(0, 5).map((ing, i) => (
                            <span
                                key={i}
                                className="text-[11px] px-2.5 py-1 bg-secondary/20 text-foreground font-semibold rounded-full border border-secondary/40 hover:border-secondary/60 hover:shadow-md transition-all duration-300"
                            >
                                {ing}
                            </span>
                        ))}
                        {ingredients.length > 5 && (
                            <span className="text-[11px] px-2.5 py-1 text-foreground/60 font-semibold flex items-center gap-1">
                                <span className="inline-block w-1 h-1 rounded-full bg-primary" />
                                {ingredients.length - 5} more
                            </span>
                        )}
                    </div>
                </div>
            </CardContent>

            {/* Card Footer */}
            <CardFooter className="p-4 pt-0 mt-auto">
                <Button
                    variant="ghost"
                    size="sm"
                    className="w-full h-11 group/btn hover:bg-gradient-to-r hover:from-primary/10 hover:to-secondary/10 border border-border/50 hover:border-primary/50 transition-all duration-300"
                >
                    <span className="font-semibold">View Recipe</span>
                    <Info className="ml-2 h-3.5 w-3.5 group-hover/btn:translate-x-1 group-hover/btn:scale-110 transition-all duration-300" />
                </Button>
            </CardFooter>
        </Card>
    )
}
