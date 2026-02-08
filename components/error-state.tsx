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
        <div className="flex flex-col items-center justify-center p-8 text-center space-y-4 bg-destructive/5 rounded-lg border border-destructive/20">
            <div className="p-3 bg-white rounded-full shadow-sm">
                <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
            <div className="space-y-1">
                <h3 className="font-serif text-xl font-bold text-foreground">{title}</h3>
                <p className="text-muted-foreground max-w-md">{message}</p>
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
