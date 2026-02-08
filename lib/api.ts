import axios from "axios";

// --- Types ---

export interface Ingredient {
    id: string;
    name: string;
    quantity: string;
    meals: string[];
}

export interface GroceryCategory {
    name: string;
    items: Ingredient[];
}

export interface Meal {
    title: string;
    description: string;
    ingredients: string[];
    time: string;
}

export interface DayPlan {
    day: string;
    date: string;
    meals: {
        breakfast: Meal;
        lunch: Meal;
        dinner: Meal;
    };
}

export interface EvidenceCitation {
    source: string;
    year: number;
    identifier: string;
}

export interface EvidenceClaim {
    id: string;
    topic: string;
    claim: string;
    evidence_type: "guideline" | "systematic-review" | "meta-analysis";
    population: string;
    limitations: string;
    citation: EvidenceCitation;
}

export interface EvidenceResponse {
    topic: string;
    claims: EvidenceClaim[];
    disclaimer: string;
}

// --- API Client ---

const api = axios.create({
    baseURL: "/api/python", // Proxied to Backend
    headers: {
        "Content-Type": "application/json",
    },
});

export const ApiClient = {
    getPlan: async (): Promise<DayPlan[]> => {
        const { data } = await api.get<DayPlan[]>("/plan");
        return data;
    },

    generatePlan: async (prefs: { householdSize: string; spiceLevel: string; dietary: string }) => {
        const { data } = await api.post("/generate-plan", prefs);
        return data;
    },

    getGroceryList: async (): Promise<GroceryCategory[]> => {
        const { data } = await api.get<GroceryCategory[]>("/grocery-list");
        return data;
    },

    getEvidence: async (topic: string): Promise<EvidenceResponse> => {
        const { data } = await api.get<EvidenceResponse>(`/evidence/${topic}`);
        return data;
    }
};
