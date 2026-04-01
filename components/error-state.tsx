import { AlertCircle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
    title?: string;
    message?: string;
    onRetry?: () => void;
}

export function ErrorState({
    title = "Something went wrong",
    message = "We couldn't load the data. Please check your connection and try again.",
    onRetry
}: ErrorStateProps) {
    return (
        <div className="flex flex-col items-center justify-center p-8 text-center space-y-5 bg-destructive/5 rounded-2xl border border-destructive/10 shadow-sm">
            <div className="p-4 bg-white/50 backdrop-blur-sm rounded-full shadow-sm border border-destructive/5">
                <AlertCircle className="h-8 w-8 text-destructive/80" />
            </div>
            <div className="space-y-2">
                <h3 className="font-serif text-2xl font-bold text-destructive/90">{title}</h3>
                <p className="text-muted-foreground max-w-md text-base leading-relaxed">{message}</p>
            </div>
            {onRetry && (
                <Button onClick={onRetry} variant="outline" className="gap-2">
                    <RefreshCcw className="h-4 w-4" />
                    Try Again
                </Button>
            )}
        </div>
    );
}
