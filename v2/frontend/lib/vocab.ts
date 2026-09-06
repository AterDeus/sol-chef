export const PROTEIN_BASE: Record<string, string> = {
  beef: 'Говядина и телятина',
  pork: 'Свинина',
  poultry: 'Птица',
  lamb: 'Баранина',
  fish_white_sea: 'Белая морская рыба',
  fish_red_sea: 'Красная рыба',
  fish_river: 'Речная рыба',
  seafood: 'Морепродукты',
  offal: 'Субпродукты',
  eggs_dairy: 'Яйца и молочные',
  vegetarian: 'Растительная / без мяса',
  vegetables: 'Овощи',
  mushrooms: 'Грибы',
  legumes: 'Бобовые',
};

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
