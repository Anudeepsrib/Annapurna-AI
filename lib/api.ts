
// Types matching Backend Pydantic Models
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

export interface FoodItem {
    id: string;
    name: string;
    source: "IFCT" | "USDA";
    nutrients: any; // Simplified for MVP
}

const BASE_URL = '/api/python';

export const ApiClient = {
    /**
     * Fetch evidence for a specific topic (e.g., 'protein', 'diabetes')
     */
    getEvidence: async (topic: string): Promise<EvidenceResponse | null> => {
        try {
            const res = await fetch(`${BASE_URL}/evidence/${topic}`);
            if (!res.ok) throw new Error('Failed to fetch evidence');
            return await res.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    },

    /**
     * Search for food nutrients (IFCT prioritized)
     */
    searchFood: async (query: string): Promise<FoodItem[]> => {
        try {
            // Try IFCT first (local)
            const res = await fetch(`${BASE_URL}/mcp/ifct/search?query=${query}`);
            if (res.ok) {
                const data = await res.json();
                if (data.results && data.results.length > 0) return data.results;
            }

            // Fallback to USDA (if implemented in UI flow, for now just IFCT)
            return [];
        } catch (error) {
            console.error('Food Search Error:', error);
            return [];
        }
    }
};
