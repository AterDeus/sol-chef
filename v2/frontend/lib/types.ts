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
  protein_bases?: string[];
  protein_variants?: Array<{ code: string; title: string; protein_base: string }>;
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

export type NutritionMacros = {
  kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
};

export type NutritionLine = {
  kcal_per_100g: number;
  protein_g_per_100g: number;
  fat_g_per_100g: number;
  carbs_g_per_100g: number;
  grams_per_unit: number;
  nutrition_factor?: number;
};

export type RecipeNutrition = {
  basis: 'raw_input';
  incomplete: boolean;
  omitted?: string[];
  total: NutritionMacros | null;
  per_100g_input: NutritionMacros | null;
  per_100g_cooked: NutritionMacros | null;
  per_serving: NutritionMacros | null;
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
  nutrition_exclude?: boolean;
  nutrition_skip_hint?: boolean;
  nutrition_line?: NutritionLine | null;
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
  protein_base?: string | null;
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
  home_protein_base?: string;
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
  yield_weight_g?: number | null;
  yield_kind?: 'estimated' | 'exact' | null;
  nutrition?: RecipeNutrition | null;
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
  prep_context?: PrepContext | null;
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

export type TipKind =
  | 'technique'
  | 'mistake'
  | 'timing'
  | 'accuracy'
  | 'heat'
  | 'storage';

export type TipTag =
  | 'prep'
  | 'knives'
  | 'skillet'
  | 'oven'
  | 'dough'
  | 'ingredients'
  | 'spices'
  | 'taste'
  | 'meat'
  | 'fish'
  | 'veg'
  | 'grains'
  | 'sauce'
  | 'storage'
  | 'safety';

export type TipRecord = {
  id?: string;
  hint: string;
  explanation?: string;
  kind?: TipKind;
  tags?: TipTag[];
};

/** Guide payload may omit id/kind/tags until JSON is tagged; strings are hint-only. */
export type TipItem = string | TipRecord;

export type TipsPayload = {
  intro?: string;
  sections?: Array<{
    id: string;
    title: string;
    items: TipItem[];
  }>;
};

export type SearchParamsRecord = Record<string, string | string[] | undefined>;

export type PrepMetrics = {
  slots_assemble?: number;
  slots_finish?: number;
  slots_reheat?: number;
  unique_slugs?: number;
  shopping_skus?: number;
  components_count?: number;
  t_sunday_active_min?: number | null;
  t_sunday_wall_min?: number | null;
  t_weekdays_active_min?: number | null;
  t_scratch_active_min?: number | null;
  kcal_avg_per_serving?: number | null;
};

export type PrepQty = {
  qty: number;
  unit: string;
  display_amount: string;
};

export type PrepContainer = PrepQty & {
  code: string;
  label: string;
  component_code?: string;
  component_title?: string;
  place: 'fridge' | 'freezer' | 'pantry';
  thaw_before_day: number | null;
  thaw_pull?: 'evening_before' | 'morning' | null;
};

export type PrepAlternative = {
  slug: string;
  label: string;
  mode: 'assemble' | 'finish' | 'reheat';
  container_ids?: string[];
};

export type PrepSource = { kind: 'weekend' } | { kind: 'slot'; day: number; meal: 'lunch' | 'dinner' };

export type PrepSlot = {
  day: number;
  meal: 'lunch' | 'dinner';
  slug: string;
  title: string;
  plate_title?: string | null;
  plate_composition?: string | null;
  mode: 'assemble' | 'finish' | 'reheat';
  flavor?: string | null;
  source: PrepSource;
  container_ids: string[];
  containers: PrepContainer[];
  alternatives: PrepAlternative[];
  servings_cooked?: number | null;
  feeds_slots?: number | null;
  time_active_from_prep_min?: number | null;
  time_active_scratch_min?: number | null;
};

export type PrepComponent = PrepQty & {
  code: string;
  title: string;
  canonical_ids: string[];
  weekend_steps: string[];
  parcook: Record<string, unknown>;
  storage: Record<string, unknown>;
};

export type PrepShopping = PrepQty & {
  canonical_id: string;
  title_ru?: string | null;
};

export type PrepGraphNode = {
  code: string;
  title: string;
  slots: Array<{
    day: number;
    meal: 'lunch' | 'dinner';
    slug: string;
    title: string;
    mode: string;
  }>;
};

export type PrepKitCard = {
  slug: string;
  title: string;
  summary?: string | null;
  rhythm?: string | null;
  position: number;
  metrics: PrepMetrics;
};

export type PrepKitListResponse = {
  results: PrepKitCard[];
};

export type PrepKitDetail = {
  slug: string;
  title: string;
  summary?: string | null;
  servings_base: number | null;
  no_leftover?: boolean;
  has_leftovers?: boolean;
  leftover_cost?: { dishes: number; shopping_add: number };
  scaling: Scaling;
  caution_text?: string | null;
  rhythm?: string | null;
  metrics: PrepMetrics;
  allergens: Allergens;
  shopping: PrepShopping[];
  components: PrepComponent[];
  containers: PrepContainer[];
  weekend_timeline: Array<Record<string, unknown>>;
  slots: PrepSlot[];
  graph: PrepGraphNode[];
};

export type PrepContext = {
  kit: { slug: string; title: string };
  day: number;
  meal: 'lunch' | 'dinner';
  mode: 'assemble' | 'finish' | 'reheat';
  source: PrepSource;
  containers: PrepContainer[];
  alternatives: PrepAlternative[];
  no_leftover?: boolean;
};

