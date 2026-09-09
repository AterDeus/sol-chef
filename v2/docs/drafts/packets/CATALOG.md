# Каталог волн — свёртка брифа 2026-09-06

PROPOSAL. Не квоты HUMAN §5. Правила осей: [README.md](README.md).

Исходник человека: ~30 «MVP» + ~50 «ещё» + семейства и матрицы ситуаций. Ниже — **уникальные slug**, без двойного борща и без второй «капусты с мясом».

Полный список slug: [CATALOG.md](CATALOG.md). Закрытые волны: [CLOSED-WAVES.md](CLOSED-WAVES.md).

## Что не плодить

| Было в брифе | Решение |
|--------------|---------|
| Крылышки 46 и 77 | один slug |
| Котлеты говядина 53 и 88 | один slug |
| Бефстроганов 54 и 90 | один slug, грибы = addon |
| Омлет 61 и 103 | один slug, овощи/сыр = addon |
| Сырники 62 и 105 | один slug, «ленивые» = addon |
| Запеканка 63 и 104 | один slug |
| Капуста 50 / 66 / 109 | один slug `tushenaya-kapusta`, мясо = addon |
| Свинина+картофель 49 и 83 | один slug, тушение/казан = equipment |
| Курица+картофель 44 / 47 / 76 | один slug бёдер; голень = `allowed_cuts`, не второй рецепт |
| Тефтели куриные 78 | addon/метод у `kurinye-kotlety`, не slug |
| Рыбные тефтели 97 | addon у `rybnye-kotlety` |
| Хек 57 / 93 / 98 | один slug |
| Скумбрия 58 и 95 | один slug |
| Рыба+картофель 60 и 94 | один slug, белок = addon/choice |
| Паста с курицей 72 и 119 | один slug |
| Шашлык новый vs духовка V1 | **не** второй id: оверлей `svinoj-shashlyk-v-duhovke-na-shpazhkah` |
| Курица с гречкой 80 | уже есть V1 `tushenaya-kuritsa-s-grechkoj-na-dni` — оверлей, не волна |
| Гречка с грибами 117 | уже есть V1 рассыпчатая гречка — оверлей |
| Яйца в томате 64 | оверлей шакшуки, не новый slug |
| Четыре целые курицы / три стейка | не трогать slug в волне; семейство — отдельный оверлей позже |
| Пять масел | техника, не калькулятор. Не развивать |

Морепродукты, белая рыба «просто на сковороде», винегрет, нут — **не в этом срезе**. Чип `seafood` останется пустым, пока не будет отдельной волны.

## Семейства (метка packet, не колонка БД)

```
shashlyk        → свинина (оверлей V1); курица и овощи — следующие волны
kotlety         → куриные / говяжьи / свиные / рыбные (разный protein_base)
gulyash         → говядина / свинина
one_pan_potato  → куриные бёдра / свинина / говядина / рыба с картофелем
kapusta         → тушёная капуста ± мясо
plov            → курица сейчас; говядина / без мяса — позже отдельные slug
pertsy          → фаршированные, белок addon
borshch         → говядина база; курица / постный — addon
```

Котлеты из разного фарша **не** сливать: температуры SAFETY разные, якорь разный, фильтр книги по `protein_base`.

## Новые slug

`eq` = обязательные equipment-варианты сверх базы. `add` = обязательные addon.

### Птица — 8

| id | База | eq | add | Зачем |
|----|------|----|-----|--------|
| `kurinye-bedra-s-kartofelem` | `oven` + форма | `skillet`, `kazan`, `air_fryer` | — | one-pan, дешёвый якорь, калькулятор |
| `kurinye-kotlety` | `pan_fry` | `oven`, `air_fryer`, тефтели=`stew`+`pot` | — | фарш, `mince`, 74 °C |
| `kurinye-krylyshki` | `oven` | `air_fryer`, `grill` | сковорода **только** если дельта партий | не дублировать 77 |
| `kurinyy-sup-s-lapshoy` | `boil` | — | картофель / рис / вермишель | грудка и бедро = `allowed_cuts` |
| `kurinaya-grudka-s-ovoshchami` | `pan_fry` | `oven`, `air_fryer`, `stew` | — | не путать с целой курицей |
| `kurinye-bedra-v-smetannom-souse` | `pan_fry` | `oven`, `stew` | — | сметана → йогурт = adaptation |
| `kurinaya-grudka-v-slivochnom-souse` | `pan_fry` | `oven` | грибы, сыр; `light` | 72 °C |
| `kurinyy-plov` | `stew` + `kazan` | `pot`, `oven` | — | не второй белок в addon |

### Свинина — 7

| id | База | eq | add |
|----|------|----|-----|
| `svinina-s-kartofelem` | `oven` | `stew`+`pot`, `kazan`, `skillet` | — |
| `svinye-otbivnye` | `pan_fry` | `oven`, `grill`, `air_fryer` | — |
| `svinina-s-lukom` | `pan_fry` | `stew`, `kazan` | — |
| `svinye-rebra` | `oven` | `grill` | — |
| `svinoy-gulyash` | `stew` | `kazan`, `pot`, `oven` | — |
| `svinye-kotlety` | `pan_fry` | `oven`, `air_fryer` | — |
| `buzhenina` | `oven` | — | рукав / фольга / медленно — addon или equipment_note, не три slug |

Шашлык — оверлей существующего slug, не строка этой таблицы. Packet: `docs/archive/packets/WAVE-1.md`.

### Говядина — 5

| id | База | eq | add |
|----|------|----|-----|
| `kotlety-iz-govyadiny` | `pan_fry` | `oven`, `grill`, `air_fryer` | в соусе = `stew` |
| `befstroganov` | `pan_fry` | — | классика=база; сметана; `light`+йогурт; грибы |
| `gulyash-iz-govyadiny` | `stew` | `kazan`, `pot`, `oven` | — |
| `tefteli-iz-govyadiny` | `stew` | `oven` | — |
| `govyadina-s-kartofelem` | `oven` | `kazan`, `stew` | — |

Не стейк, не бастинг.

### Рыба — 7

Все якоря из магазина: минтай, хек, треска, скумбрия. `target` 63 °C.

| id | База | eq | add |
|----|------|----|-----|
| `mintay-v-duhovke` | `oven` | `skillet`, `steam`, `air_fryer` | — |
| `hek-s-ovoshchami` | `oven` | `stew`, `steam`, `skillet` | — |
| `skumbriya-v-duhovke` | `oven` | `grill`; фольга = addon или шаг | — |
| `rybnye-kotlety` | `pan_fry` | `oven`, `steam` | тефтели |
| `ryba-s-kartofelem` | `oven` | `stew` | минтай / хек / треска |
| `mintay-v-klyare` | `pan_fry` | `oven`, `air_fryer` | не `deep_fry` в волне 1 |
| `ryba-v-smetannom-souse` | `oven` | `stew` | хек / минтай / треска |

### Субпродукты — 3

| id | База | eq | add |
|----|------|----|-----|
| `kurinye-serdechki-v-smetane` | `stew` | `skillet` | — |
| `pechen-po-stroganovski` | `pan_fry` | `stew` | говяжья база; куриная = **отдельный slug** в той же family (другой белок и время) |
| `pechen-s-lukom` | `pan_fry` | `oven` | — |

Печень: `protein_base=offal`. Не `poultry`.

### Яйца и молочное — 4

| id | База | eq | add |
|----|------|----|-----|
| `omlet` | `pan_fry` | `oven` | овощи, сыр |
| `syrniki` | `pan_fry` | `oven`, `air_fryer` | ленивые |
| `tvorozhnaya-zapekanka` | `oven` | `air_fryer` | — |
| `yaichnitsa-s-pomidorami` | `pan_fry` | `oven` | — |

### Овощи и картофель — 8

| id | База | eq | add |
|----|------|----|-----|
| `kartofel-po-derevenski` | `oven` | `air_fryer`, `skillet` | — |
| `tushenaya-kapusta` | `stew` + `pot` | `kazan`, `oven` | `with_pork`, `with_chicken` (база без мяса) |
| `ovoshchnoe-ragu` | `stew` | `oven`, `kazan`, `skillet` | картофель / кабачок / баклажан / грибы — **не все сразу**; 2–3 лучших addon |
| `zapechennye-ovoshchi` | `oven` | `air_fryer`, `grill` | — |
| `kartofel-s-gribami` | `pan_fry` | `oven`, `air_fryer` | whitelist грибы |
| `zharenaya-kartoshka-s-lukom` | `pan_fry` | — | грибы, бекон |
| `tsvetnaya-kapusta-v-duhovke` | `oven` | `air_fryer` | сыр, сметана |
| `farshirovannye-pertsy` | `stew` + `pot` | `oven`, `kazan` | `beef`, `pork`, `chicken`, `rice_vegetable` |

Кабачки 111 → addon рагу, не slug. Картофель тушёный с мясом 107 → семейство `one_pan_potato`, не третий картофель.

### Бобовые — 3

| id | База | eq |
|----|------|----|
| `chechevitsa-s-ovoshchami` | `boil` | `stew` |
| `fasol-tushenaya-s-ovoshchami` | `stew` | `kazan` |
| `gorohovoe-pyure` | `boil` | копчёности = addon |

Мультиварку не обещать.

### Крупы и паста — 7

| id | База | eq | add |
|----|------|----|-----|
| `ris-na-garnir` | `boil` | — | овощи; рассыпчатый = база; «под жареный рис» = notes |
| `kartofelnoe-pyure` | `boil` | — | молоко / без молока / масло / печёный чеснок |
| `pshennaya-kasha` | `boil` | — | гарнир=база; молочная; тыква |
| `perlovka-s-gribami` | `boil` | `oven`, `kazan` | — |
| `pasta-s-kuritsey-v-slivkah` | `pan_fry` | запеканка=`oven` | грибы; томатный соус |
| `makarony-s-myasnym-sousom` | `stew`/`boil` | — | говядина=база; свинина; микс; без мяса |
| `makarony-po-flotski` | `pan_fry` | `pot` | говядина / свинина / микс |

Рис «рисоварка» не писать.

### Супы и салат — 3

| id | База | add |
|----|------|-----|
| `borshch` | `boil`, `beef` | курица; постный |
| `shchi-iz-svezhey-kapusty` | `boil` | мясные; без мяса |
| `ovoshchnoy-salat` | `no_cook` | сыр; яйцо; сметана vs масло |

Постный борщ: база говядина, addon убирает мясо (`omission` + addon). Чип `vegetables` этот slug не поймает — это ок для волны 1; отдельный постный slug не плодить.

## Оверлей существующих (не волна)

Когда оверлей дойдёт до slug:

| V1 id | Сделать |
|-------|---------|
| `svinoj-shashlyk-v-duhovke-na-shpazhkah` | база `grill`; духовка и сковорода — equipment с дельтой; тот же `id` |
| `shakshuka-s-tomatami-i-bazilikom` | addon сыр / перец / фасоль; не переименовывать в «яйца с помидорами» |
| `tushenaya-kuritsa-s-grechkoj-na-dni` | казань/духовка если честно готовятся; не новый 80 |
| `rassypchataya-grechka-…` | ось посуды, если отличается; не новый 117 |
| масла, бастинг | профиль + якорь; **без** новых способов «чтобы было» |
| четыре целые курицы, стейки | не сливать в этой сессии |

## Приоритет плотности для калькулятора

Сначала (волна 1): [CLOSED-WAVES.md](CLOSED-WAVES.md). Уже в БД.

`light` писать там, где жир реально убирается (котлеты, бефстроганов, паста со сливками, сырники). Не на шашлыке «для галочки».
