import { Skeleton } from "@/components/ui/skeleton"

export function PlanSkeleton() {
    return (
        <div className="space-y-8">
            {/* Navigation Rail Skeleton */}
            <div className="flex items-center justify-between gap-4">
                <div className="flex gap-4 overflow-x-auto pb-2">
                    {[...Array(7)].map((_, i) => (
                        <Skeleton key={i} className="h-20 w-[4.5rem] rounded-2xl" />
                    ))}
                </div>
            </div>

            {/* Daily View Skeleton */}
            <div className="bg-card rounded-3xl p-6 md:p-10 shadow-lg border border-border">
                <div className="text-center mb-10 space-y-3 flex flex-col items-center">
                    <Skeleton className="h-10 w-48" />
                    <Skeleton className="h-4 w-32" />
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="space-y-4">
                            <div className="flex items-center gap-3 pb-2 border-b border-muted">
                                <Skeleton className="h-6 w-6 rounded-full" />
                                <Skeleton className="h-6 w-24" />
                            </div>
                            <Skeleton className="h-[200px] w-full rounded-xl" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
