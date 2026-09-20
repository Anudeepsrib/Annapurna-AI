// --- Types ---

export interface Ingredient {
  id: string;
  name: string;
  quantity: string;
  meals: string[];
  priority?: "high" | "normal" | "pantry" | "use_soon";
  status?: "need_to_buy" | "pantry" | "pantry_unused";
  optimization_note?: string;
}

export interface GroceryCategory {
  name: string;
  items: Ingredient[];
}

export interface NutritionEstimate {
  calories_kcal?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  fiber_g?: number | null;
}

export interface Meal {
  title: string;
  description: string;
  ingredients: string[];
  time: string;
  nutrition?: NutritionEstimate;
  confidence?: "low" | "medium" | "high";
  source_status?: string;
  disclaimer?: string;
}

export interface DayPlan {
  day: string;
  date: string;
  meals: {
    breakfast: Meal;
    lunch: Meal;
    dinner: Meal;
  };
  confidence?: "low" | "medium" | "high";
  source_status?: string;
  disclaimer?: string;
  safety_notes?: string[];
}

export interface PlanPreferences {
  householdSize: string;
  spiceLevel: string;
  dietary: string;
  allergies?: string[];
  familyProfiles?: FamilyProfile[];
  pantryInventory?: PantryItem[];
  pantryText?: string;
  preferences?: SoftPlanningPreferences;
  teluguAndhraConstraints?: TeluguAndhraConstraint[];
}

export interface SoftPlanningPreferences {
  preferredCuisines?: string[];
  spiceLevel?: "mild" | "medium" | "spicy";
  riceLunchPreference?: boolean;
  dalMealsPerWeek?: number;
  fermentedBreakfasts?: "avoid" | "okay" | "prefer";
  preparationEffort?: "low" | "medium" | "any";
  weekdayCookingMinutes?: number;
  leftoversPreference?: "avoid" | "neutral" | "prefer";
  repetitionTolerance?: "low" | "medium" | "high";
  pantryUtilizationPreference?: "low" | "medium" | "high";
  ingredientReusePreference?: "low" | "medium" | "high";
}

export type TeluguAndhraConstraint =
  | "vegetarian"
  | "no_egg"
  | "andhra_telugu_style"
  | "rice_based_lunch"
  | "pappu_or_dal_daily"
  | "fermented_breakfasts_ok"
  | "mild_for_children"
  | "festival_no_onion_garlic";

export interface FamilyProfile {
  label: string;
  ageGroup: "adult" | "senior" | "teen" | "child";
  appetite: "light" | "regular" | "hearty";
  dietaryTags: string[];
  privacyScope: "local_device_only" | "meal_planning_only";
}

export interface PantryItem {
  name: string;
  quantity?: string;
  category?: "grains" | "dals" | "vegetables" | "spices" | "dairy" | "other";
  expiresWithinDays?: number | null;
}

export type PantryUnit =
  | "g" | "kg" | "oz" | "lb"
  | "ml" | "l" | "tsp" | "tbsp" | "cup"
  | "piece" | "bunch" | "packet" | "can" | "bottle";

export interface PantryInventoryItem {
  id: number;
  ingredientId: string | null;
  displayName: string;
  quantity: string | null;
  unit: PantryUnit | null;
  quantityText: string;
  category: string;
  storageLocation: "pantry" | "refrigerator" | "freezer";
  opened: boolean;
  expiresAt: string | null;
  expired: boolean;
  minimumStockQuantity: string | null;
  minimumStockUnit: PantryUnit | null;
  preferredBrand: string;
  notes: string;
  version: number;
}

export type MealStatus = "COOKED" | "SKIPPED" | "LEFTOVER" | "ATE_OUT" | "REPLACED";
export type FeedbackSignal =
  | "LIKED" | "DISLIKED" | "TOO_SPICY" | "TOO_MUCH_WORK" | "WOULD_REPEAT" | "WOULD_NOT_REPEAT";

export interface TodayMeal {
  mealType: "breakfast" | "lunch" | "dinner";
  meal: Meal;
  status: MealStatus | null;
  feedback: FeedbackSignal[];
  missingIngredients: string[];
}

export interface Leftover {
  id: number;
  title: string;
  sourceDay: string;
  sourceMealType: "breakfast" | "lunch" | "dinner";
  servingsRemaining: number;
  createdAt: string;
  usableUntil: string;
}

export interface TodayResponse {
  planAvailable: boolean;
  day: string;
  date: string;
  meals: TodayMeal[];
  expiringPantry: PantryInventoryItem[];
  leftovers: Leftover[];
}

export interface GeneratePlanResponse {
  status: string;
  message: string;
  plan: DayPlan[];
  source_status: string;
  disclaimer: string;
  safety_notes: string[];
  grocery_optimization: GroceryCategory[];
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
  evidence_type: "guideline" | "systematic-review" | "meta-analysis" | "research-abstract";
  population: string;
  limitations: string;
  citation: EvidenceCitation;
}

export interface EvidenceResponse {
  topic: string;
  claims: EvidenceClaim[];
  disclaimer: string;
}

export interface SettingsResponse {
  app_env: string;
  debug: boolean;
  llm_provider: string;
  llm_base_url: string;
  llm_model: string;
  llm_network_mode: "local" | "external";
  llm_privacy_note: string;
  database_url: string;
  enable_external_network: boolean;
  enable_usda: boolean;
  enable_pubmed: boolean;
}

export interface ModelsResponse {
  provider: string;
  models: string[];
  error?: string;
  note?: string;
}

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

// This value is safe to expose: it is only a browser-visible route prefix.
const API_BASE_PATH = process.env.NEXT_PUBLIC_API_BASE_PATH || "/api/python";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_PATH}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const message =
      payload?.error?.message ||
      payload?.detail?.error ||
      payload?.detail?.message ||
      payload?.detail ||
      "Backend request failed";
    const code = payload?.error?.code;
    throw new ApiError(String(message), response.status, code);
  }

  return payload as T;
}

export const ApiClient = {
  getPlan: async (): Promise<DayPlan[]> => request<DayPlan[]>("/plan"),

  generatePlan: async (prefs: PlanPreferences): Promise<GeneratePlanResponse> =>
    request<GeneratePlanResponse>("/generate-plan", {
      method: "POST",
      body: JSON.stringify(prefs),
    }),

  getGroceryList: async (): Promise<GroceryCategory[]> => request<GroceryCategory[]>("/grocery-list"),

  getPantry: async (): Promise<PantryInventoryItem[]> => request<PantryInventoryItem[]>("/pantry"),

  importPantry: async (pantryText: string): Promise<PantryInventoryItem[]> =>
    request<PantryInventoryItem[]>("/pantry/import", {
      method: "POST",
      body: JSON.stringify({ pantryText }),
    }),

  getToday: async (): Promise<TodayResponse> => request<TodayResponse>("/today"),

  setMealStatus: async (
    day: string,
    mealType: TodayMeal["mealType"],
    status: MealStatus,
  ): Promise<{ status: MealStatus }> =>
    request<{ status: MealStatus }>(`/today/${encodeURIComponent(day)}/${mealType}/status`, {
      method: "POST",
      body: JSON.stringify({ status }),
    }),

  recordMealFeedback: async (
    day: string,
    mealType: TodayMeal["mealType"],
    signal: FeedbackSignal,
  ): Promise<{ signal: FeedbackSignal }> =>
    request<{ signal: FeedbackSignal }>(`/today/${encodeURIComponent(day)}/${mealType}/feedback`, {
      method: "POST",
      body: JSON.stringify({ signal }),
    }),

  getEvidence: async (topic: string): Promise<EvidenceResponse> =>
    request<EvidenceResponse>(`/evidence/${encodeURIComponent(topic)}`),

  getSettings: async (): Promise<SettingsResponse> => request<SettingsResponse>("/settings/"),

  testLLM: async (): Promise<Record<string, unknown>> =>
    request<Record<string, unknown>>("/settings/test-llm", { method: "POST" }),

  listModels: async (): Promise<ModelsResponse> => request<ModelsResponse>("/settings/models"),

  health: async (): Promise<{ status: string; mode: string; external_network_enabled: boolean }> =>
    request<{ status: string; mode: string; external_network_enabled: boolean }>("/health"),
};
