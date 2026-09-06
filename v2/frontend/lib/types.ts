export type Allergens = {
  contains: string[];
  may_contain: string[];
  unknown: string[];
};

export type Scaling = {
  enabled: boolean;
  mode?: 'anchor' | 'servings' | 'off';
  ratio?: number;
  base_anchor?: {
    amount: number;
    unit: string;
    name: string;
  };
  applied?: {
    anchor_weight?: number;
    servings?: number;
  };
};

export type RecipeCardData = {
  slug: string;
  title: string;
  protein_base: string;
  cook_method: string;
  dish_type: string;
  equipment?: string | null;
  allowed_cuts?: string[];
  summary?: string | null;
  editorial_tested?: boolean;
  high_risk_flags: string[];
  allergens: Allergens;
  scaling?: { enabled: boolean };
  has_delta_variants?: boolean;
  time_profile?: { total_minutes: number | null; active_minutes: number | null };
  effort_level?: number | null;
  washing_level?: number | null;
  use_cases?: string[];
  why?: string[];
  score?: number;
  applied_axes?: { variant: string | null; equipment: string | null };
  bucket?: 'now' | 'almost' | 'best' | 'match' | 'rest';
  shopping_delta?: Array<{ canonical_id: string; title: string }>;
  substitutions?: Array<{
    from_id: string;
    from_title: string;
    to_id: string;
    to_title: string;
  }>;
  step_count?: number;
};

export type PantryItem = { canonical_id: string; title: string };

export type PantryGroup = {
  id: string;
  title: string;
  items?: PantryItem[];
  children?: PantryGroup[];
};

export type PantryOptionsResponse = {
  groups: PantryGroup[];
};

export type PantryResolveResponse = {
  items: Array<{ canonical_id: string; title: string }>;
  unknown: string[];
};

export type CatalogResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: RecipeCardData[];
};

export type AlternativeSolution = RecipeCardData & { label: string };

export type RecommendationsResponse = {
  filters: Record<string, string[]>;
  results: RecipeCardData[];
  featured?: RecipeCardData | null;
  alternatives?: AlternativeSolution[];
  buckets?: {
    now: RecipeCardData[];
    almost: RecipeCardData[];
    best: RecipeCardData[];
  };
};

export type RecipeIngredient = {
  name: string;
  amount: number | null;
  amount_max: number | null;
  unit: string;
  detail: string | null;
  scalable: boolean;
  scale_mode: 'linear' | 'gentle' | 'whole' | 'manual';
  is_anchor: boolean;
  optional?: boolean;
  display_amount: string;
};

export type RecipeStep = {
  text: string;
  timer_seconds: number | null;
  timer_label: string | null;
  timer_note: string | null;
  pull_internal_temperature_c: number | null;
  target_internal_temperature_c: number | null;
  hold_seconds: number | null;
};

export type RecipeVariation = {
  title: string;
  text: string;
};

export type RecipeNote = {
  title: string | null;
  text: string;
};

export type RecipePrep = {
  type?: string;
  text: string;
  before_min?: number;
  before_hours?: number;
};

export type RecipeVariantOption = {
  code: string;
  title: string;
  axis: 'addon' | 'equipment' | 'energy';
  has_delta: boolean;
};

export type RecipeAdaptation = {
  type: 'substitution' | 'omission' | 'equipment' | 'method';
  from?: string;
  to?: string;
  ingredient?: string;
  quality?: number;
};

export type RecipeDetail = {
  slug: string;
  title: string;
  protein_base: string;
  cook_method: string;
  dish_type: string;
  equipment?: string | null;
  allowed_cuts?: string[];
  applied_axes?: { variant: string | null; equipment: string | null };
  available_variants?: RecipeVariantOption[];
  available_equipment?: string[];
  summary: string | null;
  source_name: string | null;
  source_url: string | null;
  editorial_tested: boolean;
  high_risk_flags: string[];
  caution_text: string | null;
  allergens: Allergens;
  scaling: Scaling;
  servings?: number | null;
  ingredients: RecipeIngredient[];
  steps: RecipeStep[];
  variations: RecipeVariation[];
  notes: RecipeNote[] | string | null;
  prep?: RecipePrep[];
  time_profile?: { total_minutes: number | null; active_minutes: number | null };
  effort_level?: number | null;
  washing_level?: number | null;
  use_cases?: string[];
  adaptations?: RecipeAdaptation[];
};

export type GuideDocument = {
  type: 'guide' | 'meat';
  slug: string;
  title: string;
  payload: unknown;
};

export type GrainRow = {
  name: string;
  wash: string;
  ratio: string;
  time: string;
  note: string;
};

export type GrainsPayload = {
  intro_lead?: string;
  intro?: string;
  rows?: GrainRow[];
};

export type MeatCard = {
  title: string;
  readout_label: string;
  readout_value: string;
  text: string;
  pitfall: string;
};

export type MeatMethod = {
  name: string;
  sub: string;
  cards: MeatCard[];
};

export type MeatPayload = {
  intro_lead?: string;
  intro?: string;
  methods?: MeatMethod[];
};

export type TipItem =
  | string
  | {
      hint: string;
      explanation?: string;
    };

export type TipsPayload = {
  intro?: string;
  sections?: Array<{
    id: string;
    title: string;
    items: TipItem[];
  }>;
};

export type SearchParamsRecord = Record<string, string | string[] | undefined>;
