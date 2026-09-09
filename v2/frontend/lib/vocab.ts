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
  return chapterIdForRecipe(code, 'main');
}

export function bookChapterById(id: string | undefined): BookChapter | undefined {
  return BOOK_CHAPTERS.find((chapter) => chapter.id === id);
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

export function labelOf(map: Record<string, string>, code: string): string {
  return map[code] ?? code;
}

/** Vessel, or method-only family code (`air_fryer`, `steam`) on the equipment axis. */
export function equipmentLabel(code: string): string {
  return EQUIPMENT[code] ?? COOK_METHOD[code] ?? code;
}
