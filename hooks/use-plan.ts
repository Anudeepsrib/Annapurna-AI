import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiClient, DayPlan } from "@/lib/api";
import { toast } from "sonner";

export function useGetPlan() {
    return useQuery({
        queryKey: ["weekPlan"],
        queryFn: ApiClient.getPlan,
        retry: 1,
    });
}

export function useGeneratePlan() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ApiClient.generatePlan,
        onSuccess: () => {
            toast.success("Meal plan generated successfully!");
            queryClient.invalidateQueries({ queryKey: ["weekPlan"] });
            queryClient.invalidateQueries({ queryKey: ["groceryList"] });
        },
        onError: (error) => {
            console.error(error);
            toast.error("Failed to generate plan. Please try again.");
        },
    });
}

export function useGetGroceryList() {
    return useQuery({
        queryKey: ["groceryList"],
        queryFn: ApiClient.getGroceryList,
    });
}

export function useGetEvidence(topic: string) {
    return useQuery({
        queryKey: ["evidence", topic],
        queryFn: () => ApiClient.getEvidence(topic),
        enabled: !!topic,
    });
}
