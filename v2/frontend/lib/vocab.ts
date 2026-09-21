export const PROTEIN_BASE: Record<string, string> = {
  beef: 'Говядина и телятина',
  pork: 'Свинина',
  poultry: 'Птица',
  lamb: 'Баранина',
  fish_white_sea: 'Белая морская рыба',
  fish_red_sea: 'Красная рыба',
  fish_river: 'Речная рыба',
  fish_canned: 'Консервированная рыба',
  seafood: 'Морепродукты',
  offal: 'Субпродукты',
  eggs_dairy: 'Яйца и молочные',
  vegetarian: 'Растительная / без мяса',
  vegetables: 'Овощи',
  mushrooms: 'Грибы',
  legumes: 'Бобовые',
  fruits: 'Фрукты и ягоды',
};

/**
 * First-level book TOC. Role on the table (breakfast / side / dessert) wins over
 * protein_base, so яичница is in Завтраки, not «другое».
 */
export const BOOK_CHAPTERS = [
  { id: 'meat', label: 'Мясо', bases: ['beef', 'pork', 'lamb', 'offal'], dishTypes: [] },
  { id: 'poultry', label: 'Птица', bases: ['poultry'], dishTypes: [] },
  {
    id: 'vegetables',
    label: 'Овощи',
    bases: ['vegetables', 'mushrooms', 'legumes', 'vegetarian'],
    dishTypes: [],
  },
  {
    id: 'fish',
    label: 'Рыба и морепродукты',
    bases: ['fish_white_sea', 'fish_red_sea', 'fish_river', 'fish_canned', 'seafood'],
    dishTypes: [],
  },
  { id: 'sides', label: 'Гарниры', bases: [], dishTypes: ['side'] },
  { id: 'breakfasts', label: 'Завтраки', bases: [], dishTypes: ['breakfast'] },
  { id: 'desserts', label: 'Десерты', bases: [], dishTypes: ['dessert'] },
  { id: 'other', label: 'Другое', bases: [], dishTypes: ['sauce', 'preserve', 'drink'] },
] as const;

export type BookChapterId = (typeof BOOK_CHAPTERS)[number]['id'];
export type BookChapter = (typeof BOOK_CHAPTERS)[number];

const ROLE_CHAPTER_IDS: readonly BookChapterId[] = ['breakfasts', 'desserts', 'sides'];
const PROTEIN_CHAPTER_IDS: readonly BookChapterId[] = ['meat', 'poultry', 'vegetables', 'fish'];

export function chapterIdForRecipe(proteinBase: string, dishType: string): BookChapterId {
  for (const chapter of BOOK_CHAPTERS) {
    if ((chapter.dishTypes as readonly string[]).includes(dishType)) return chapter.id;
  }
  for (const chapter of BOOK_CHAPTERS) {
    if (ROLE_CHAPTER_IDS.includes(chapter.id) || chapter.id === 'other') continue;
    if ((chapter.bases as readonly string[]).includes(proteinBase)) return chapter.id;
  }
  return 'other';
}

/** Infer a protein chapter from `?protein_base=` when `chapter` is absent. */
export function chapterIdForBase(code: string): BookChapterId {
  if (code === 'eggs_dairy') return 'breakfasts';
  if (code === 'fruits') return 'desserts';
  return chapterIdForRecipe(code, 'main');
}

export function bookChapterById(id: string | undefined): BookChapter | undefined {
  return BOOK_CHAPTERS.find((chapter) => chapter.id === id);
}

export type ProteinVariantLink = { code: string; title: string; protein_base: string };

export function recipeCookMethods(recipe: {
  cook_method: string;
  cook_methods?: string[];
}): string[] {
  if (recipe.cook_methods?.length) return [...recipe.cook_methods];
  return recipe.cook_method ? [recipe.cook_method] : [];
}

export function recipeProteinCodes(recipe: {
  protein_base: string;
  protein_bases?: string[];
}): string[] {
  if (recipe.protein_bases?.length) return [...recipe.protein_bases];
  return recipe.protein_base ? [recipe.protein_base] : [];
}

/** Home chapter plus extra protein chapters from chips / extra bases. Role chapters do not leak. */
export function chapterIdsForRecipe(recipe: {
  protein_base: string;
  dish_type: string;
  protein_bases?: string[];
}): BookChapterId[] {
  const home = chapterIdForRecipe(recipe.protein_base, recipe.dish_type);
  const ids: BookChapterId[] = [home];
  if (ROLE_CHAPTER_IDS.includes(home)) return ids;
  for (const code of recipeProteinCodes(recipe)) {
    if (code === recipe.protein_base) continue;
    const extra = chapterIdForRecipe(code, 'main');
    if (extra !== home && PROTEIN_CHAPTER_IDS.includes(extra) && !ids.includes(extra)) {
      ids.push(extra);
    }
  }
  return ids;
}

export function pickGuestProteinVariant(
  recipe: {
    protein_base: string;
    dish_type: string;
    protein_variants?: ProteinVariantLink[];
  },
  opts: { chapterId?: string; proteinFilter?: string[] },
): ProteinVariantLink | null {
  const variants = recipe.protein_variants ?? [];
  if (!variants.length) return null;
  const filter = opts.proteinFilter ?? [];
  if (filter.length === 1 && filter[0] !== recipe.protein_base) {
    return variants.find((item) => item.protein_base === filter[0]) ?? null;
  }
  if (opts.chapterId) {
    const home = chapterIdForRecipe(recipe.protein_base, recipe.dish_type);
    if (home === opts.chapterId) return null;
    const chapter = bookChapterById(opts.chapterId);
    if (!chapter?.bases.length) return null;
    return (
      variants.find((item) => (chapter.bases as readonly string[]).includes(item.protein_base)) ??
      null
    );
  }
  return null;
}

export const COOK_METHOD: Record<string, string> = {
  oven: 'В духовке',
  pan_fry: 'На сковороде',
  stew: 'Тушение',
  boil: 'Варка',
  grill: 'Гриль',
  steam: 'На пару',
  no_cook: 'Без термообработки',
  air_fryer: 'Аэрогриль',
  deep_fry: 'Во фритюре',
};

export const DISH_TYPE: Record<string, string> = {
  main: 'Основное блюдо',
  soup: 'Суп',
  salad: 'Салат',
  appetizer: 'Закуска',
  breakfast: 'Завтрак',
  side: 'Гарнир',
  pasta_grains: 'Паста и крупы',
  bakery: 'Выпечка',
  dessert: 'Десерт',
  sauce: 'Соус',
  drink: 'Напиток',
  preserve: 'Заготовка',
};

export const EQUIPMENT: Record<string, string> = {
  pot: 'Кастрюля',
  oven: 'Духовка',
  kazan: 'Казан',
  skillet: 'Сковорода',
  saucepan: 'Сотейник',
  baking_dish: 'Форма',
  grill: 'Гриль',
};

/** cook_method codes that appear on the equipment axis (no vessel field). */
export const METHOD_ONLY_EQUIPMENT = new Set(['air_fryer', 'steam']);

/** Extra-conditions cookware row: vessels plus аэрогриль. */
export const EQUIPMENT_FILTER: Record<string, string> = {
  ...EQUIPMENT,
  air_fryer: 'Аэрогриль',
};

export const CUT: Record<string, string> = {
  shank: 'голяшка',
  shoulder: 'лопатка',
  neck: 'шея',
  rump: 'огузок',
  brisket: 'грудинка',
  thick_rib: 'толстый край',
  tenderloin: 'вырезка',
  loin: 'корейка',
  belly: 'брюшина',
  ribs: 'рёбра',
  mince: 'фарш',
  breast: 'грудка',
  thigh: 'бедро',
  drumstick: 'голень',
  wing: 'крыло',
  whole_bird: 'целиком',
};

export const ALLERGEN: Record<string, string> = {
  gluten: 'глютен',
  milk: 'молоко',
  egg: 'яйцо',
  fish: 'рыба',
  crustacean: 'ракообразные',
  mollusc: 'моллюски',
  peanut: 'арахис',
  tree_nut: 'орехи',
  soy: 'соя',
  sesame: 'кунжут',
  mustard: 'горчица',
  celery: 'сельдерей',
  sulfite: 'сульфиты',
  lupin: 'люпин',
};

export const HIGH_RISK: Record<string, string> = {
  raw_egg: 'Сырое яйцо',
  raw_meat: 'Сырое мясо',
  raw_fish: 'Сырая рыба',
  raw_milk: 'Сырое молоко',
  wild_mushrooms: 'Дикие грибы',
  ground_meat: 'Фарш',
  preservation: 'Консервация',
  fermentation: 'Ферментация',
  child_food: 'Детское питание',
  fire_hazard: 'Пожарная опасность',
  poultry_temp: 'Температура птицы',
};

export const MEAT_CUTS = ['beef', 'pork', 'poultry'] as const;
export type MeatCut = (typeof MEAT_CUTS)[number];

export const MEAT_CUT_LABEL: Record<MeatCut, string> = {
  beef: 'Говядина',
  pork: 'Свинина',
  poultry: 'Птица',
};

export const INTENT: Record<string, string> = {
  fast: 'Быстро',
  pantry: 'Из того, что есть',
  easy: 'Проще',
  batch: 'На несколько дней',
  light: 'Полегче',
  oven: 'В духовке',
};

export const USE_CASE: Record<string, string> = {
  fast: 'Быстро',
  easy: 'Просто',
  pantry: 'Из запасов',
  one_pan: 'Одна посуда',
  batch: 'Заготовка',
  budget: 'Дешевле',
  light: 'Полегче',
};

export const HAVE_GROUP: Record<string, string> = {
  chicken: 'Курица',
  meat: 'Мясо',
  fish: 'Рыба',
  veg: 'Овощи',
  grains: 'Крупы',
  eggs: 'Яйца',
  dairy: 'Молочное',
  other: 'Другое',
};

/** Calculator pantry group → book chapter. Catalog does not accept have=. */
export const HAVE_GROUP_TO_BOOK: Record<
  string,
  { chapter: BookChapterId; protein_base?: string }
> = {
  chicken: { chapter: 'poultry', protein_base: 'poultry' },
  pork: { chapter: 'meat', protein_base: 'pork' },
  beef: { chapter: 'meat', protein_base: 'beef' },
  lamb: { chapter: 'meat', protein_base: 'lamb' },
  offal: { chapter: 'meat', protein_base: 'offal' },
  fish: { chapter: 'fish' },
  veg: { chapter: 'vegetables' },
  eggs: { chapter: 'breakfasts', protein_base: 'eggs_dairy' },
  legumes: { chapter: 'vegetables', protein_base: 'legumes' },
};

export const HAVE_GROUP_BOOK_PRIORITY = [
  'chicken',
  'pork',
  'beef',
  'lamb',
  'offal',
  'fish',
  'eggs',
  'legumes',
  'veg',
] as const;

export const TIP_KIND: Record<string, string> = {
  technique: 'Приём',
  mistake: 'Ошибка',
  timing: 'Время',
  accuracy: 'Точность',
  heat: 'Температура',
  storage: 'Хранение',
};

export const TIP_TAG: Record<string, string> = {
  prep: 'Подготовка',
  knives: 'Ножи',
  skillet: 'Сковорода',
  oven: 'Духовка',
  dough: 'Тесто',
  ingredients: 'Ингредиенты',
  spices: 'Специи',
  taste: 'Вкус',
  meat: 'Мясо',
  fish: 'Рыба',
  veg: 'Овощи',
  grains: 'Крупы',
  sauce: 'Соусы',
  storage: 'Хранение',
  safety: 'Безопасность',
};

export function labelOf(map: Record<string, string>, code: string): string {
  return map[code] ?? code;
}

/** Short chip for the home protein when addon chips swap meat/fish. */
export const PROTEIN_CHIP_LABEL: Record<string, string> = {
  beef: 'Говядина',
  pork: 'Свинина',
  poultry: 'Курица',
  lamb: 'Баранина',
  offal: 'Субпродукты',
  seafood: 'Морепродукты',
  fish_white_sea: 'Белая рыба',
  fish_red_sea: 'Красная рыба',
  fish_river: 'Речная рыба',
  fish_canned: 'Консервы',
};

const ANIMAL_PROTEIN = new Set(Object.keys(PROTEIN_CHIP_LABEL));

export function baseAddonChipLabel(
  homeProtein: string,
  variants: Array<{ has_delta?: boolean; protein_base?: string | null }>,
): string {
  const hasOverride = variants.some((item) => item.has_delta && item.protein_base);
  if (!hasOverride || !ANIMAL_PROTEIN.has(homeProtein)) return 'Как в рецепте';
  return PROTEIN_CHIP_LABEL[homeProtein] ?? labelOf(PROTEIN_BASE, homeProtein);
}

/** Vessel, or method-only family code (`air_fryer`, `steam`) on the equipment axis. */
export function equipmentLabel(code: string): string {
  return EQUIPMENT[code] ?? COOK_METHOD[code] ?? code;
}
