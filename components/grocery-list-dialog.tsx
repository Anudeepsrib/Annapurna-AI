"use client"

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useGetGroceryList } from "@/hooks/use-plan"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Loader2, ShoppingBasket } from "lucide-react"

interface GroceryListDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function GroceryListDialog({ open, onOpenChange }: GroceryListDialogProps) {
    const { data: groceryList, isLoading } = useGetGroceryList()

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] md:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-2xl font-serif text-primary">
                        <ShoppingBasket className="h-6 w-6" />
                        Grocery List
                    </DialogTitle>
                    <DialogDescription>
                        Your weekly shopping list based on the generated meal plan.
                    </DialogDescription>
                </DialogHeader>

                <ScrollArea className="h-[60vh] pr-4 mt-4">
                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center h-40 gap-4 text-muted-foreground">
                            <Loader2 className="h-8 w-8 animate-spin" />
                            <p>Curating your list...</p>
                        </div>
                    ) : groceryList && groceryList.length > 0 ? (
                        <div className="space-y-8">
                            {groceryList.map((category) => (
                                <div key={category.name} className="space-y-3">
                                    <h3 className="font-semibold text-lg text-foreground border-b pb-2">
                                        {category.name}
                                    </h3>
                                    <div className="grid gap-3">
                                        {category.items.map((item) => (
                                            <div
                                                key={item.id}
                                                className="flex items-start space-x-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
                                            >
                                                <Checkbox id={item.id} />
                                                <div className="grid gap-1.5 leading-none">
                                                    <Label
                                                        htmlFor={item.id}
                                                        className="text-base font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                                                    >
                                                        {item.name}
                                                    </Label>
                                                    <p className="text-sm text-muted-foreground">
                                                        {item.quantity} • Used in: {item.meals.join(", ")}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                            <p>No items found. Generate a plan first!</p>
                        </div>
                    )}
                </ScrollArea>
            </DialogContent>
        </Dialog>
    )
}
