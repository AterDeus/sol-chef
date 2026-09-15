# Спринт — сентябрьские наборы + 5 новых карточек

Человек (чат 2026-09-09): финал брифа; пять slug; вечером — редакционный проход по карточкам (жир, companion, `fish_canned`, рис).

Не делать: импорт эксперимента №0 (`kit-1` / `kit-2`); оверлей осей N; архивный V1 без просьбы; `editorial_tested`.

Чат 2026-09-10: **два новых slug** на «Без вчерашнего», не каталог недели (`chechevitsa` / `kartofel-s-gribami` не подставлять). Packet: [PREP-NO-LEFTOVER.md](docs/drafts/packets/PREP-NO-LEFTOVER.md). Сверх пяти сентября только эти два.

## Цель

1. Сетки: [BRIEFS-SEPTEMBER.md](docs/drafts/weekly-prep/BRIEFS-SEPTEMBER.md).
2. Packet’ы: [PREP-SEPTEMBER.md](docs/drafts/packets/PREP-SEPTEMBER.md).
3. Черновики: `export_draft` / WIP JSON → валидатор → Terra.
4. Собрать kit из конструкций, не из новой пачки рецептов.

## Чек-лист

- [x] Бриф сеток под ловушки хранения и яиц.
- [x] Вердикт A–J (5 new / 5 overlay слота).
- [x] Пять JSON авторов.
- [x] `import_draft --check` (когда контейнер и скрипт доступны).
- [x] Terra Medium по каждому accept/revise.
- [x] Редакционный проход: жир тыквы, лобио+салат слота, говядина=чип обязателен, `fish_canned`, рис без 60–90 в карточке.
- [x] Два slug leftover: JSON + Terra `accept` (`tushenye-kabachki-s-risom`, `baklazhany-s-kartofelem-na-skovorode`).
- [x] Правила наборов как системы недели: [WEEKLY-PREP-DESIGN.md](docs/weekly/WEEKLY-PREP-DESIGN.md) §28–40, сроки и охлаждение в [SAFETY.md](docs/SAFETY.md).
- [x] Проход по текстам и JSON обоих сентябрьских наборов против §28–40 (охлаждение, сроки, банки, разморозка в сетке, посуда, минуты, жаргон, цена «Без вчерашнего»).
- [x] Внутренняя непротиворечивость: счёт контейнеров без банок; срок противня по смеси; охлаждение без «пара»; разморозка по типу заготовки; рис; «Осторожно» полосок.
- [x] `import_draft` двух slug и `import_prep_kit` обоих наборов, когда Docker жив.

## Готово, когда

Пять карточек в БД, бриф не противоречит контракту тарелки. На «На неделю» — два сентябрьских набора.

