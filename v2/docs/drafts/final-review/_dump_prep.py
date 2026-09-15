# Temporary dump helper for editorial review. Not a product command.
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

BASE = "http://localhost:8080"
OUT_DIR = Path(__file__).resolve().parent / "prep"
OUT_FILE = OUT_DIR / "all.md"
README = OUT_DIR / "README.md"

CATALOG_LEDE = (
    "Один выходной: закупка и полуфабрикаты. Будни — собрать тарелку за 10–20 минут."
)

PREP_MODE_RU = {
    "assemble": "Собрать",
    "finish": "Доготовить",
    "reheat": "Разогреть",
}
PREP_MEAL_RU = {"lunch": "Обед", "dinner": "Ужин"}
PREP_DAY_FULL = [
    "",
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]
PREP_DAY_RU = ["", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
PREP_PLACE_RU = {"fridge": "Холодильник", "freezer": "Морозилка", "pantry": "Шкаф"}
PREP_DAY_GENITIVE = [
    "",
    "понедельника",
    "вторника",
    "среды",
    "четверга",
    "пятницы",
    "субботы",
    "воскресенья",
]
DICED_COMPONENT_CODES = {
    "roasted_vegetables",
    "roasted_pumpkin",
    "roasted_veg_near",
    "roasted_veg_pumpkin",
    "braised_cabbage",
}
ALLERGEN = {
    "gluten": "глютен",
    "milk": "молоко",
    "egg": "яйцо",
    "fish": "рыба",
    "crustacean": "ракообразные",
    "mollusc": "моллюски",
    "peanut": "арахис",
    "tree_nut": "орехи",
    "soy": "соя",
    "sesame": "кунжут",
    "mustard": "горчица",
    "celery": "сельдерей",
    "sulfite": "сульфиты",
    "lupin": "люпин",
}


def get_json(url: str):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ru_count(n: int, one: str, few: str, many: str) -> str:
    n10 = abs(n) % 10
    n100 = abs(n) % 100
    if n10 == 1 and n100 != 11:
        return one
    if 2 <= n10 <= 4 and (n100 < 12 or n100 > 14):
        return few
    return many


def leftover_cost_caption(cost: dict | None) -> str | None:
    if not cost or (cost.get("dishes", 0) <= 0 and cost.get("shopping_add", 0) <= 0):
        return None
    dishes_n = int(cost.get("dishes") or 0)
    shop_n = int(cost.get("shopping_add") or 0)
    dishes = f"{dishes_n} {ru_count(dishes_n, 'быстрое блюдо', 'быстрых блюда', 'быстрых блюд')}"
    shop = f"{shop_n} {ru_count(shop_n, 'позиция', 'позиции', 'позиций')} к закупке"
    return f"+{dishes}, +{shop}."


def cold_container_caption(containers: list[dict]) -> str | None:
    cold = sum(1 for box in containers if box.get("place") in {"fridge", "freezer"})
    pantry = sum(1 for box in containers if box.get("place") == "pantry")
    if cold <= 0:
        return None
    n = f"{cold} {ru_count(cold, 'контейнер', 'контейнера', 'контейнеров')}"
    if pantry > 0:
        return f"{n} плюс банки в шкафу"
    return n


def thaw_prev_day_genitive(day: int) -> str:
    if day <= 1:
        return "воскресенья"
    return PREP_DAY_GENITIVE[day - 1] or "воскресенья"


def thaw_pull_mode(box: dict) -> str | None:
    if box.get("place") != "freezer" or box.get("thaw_before_day") is None:
        return None
    pull = box.get("thaw_pull")
    if pull in {"morning", "evening_before"}:
        return pull
    if box.get("unit") == "ml":
        return "evening_before"
    if box.get("component_code") in DICED_COMPONENT_CODES:
        return "morning"
    return "evening_before"


def format_thaw_column(box: dict) -> str:
    pull = thaw_pull_mode(box)
    day = box.get("thaw_before_day")
    if not pull or day is None:
        return "—"
    name = PREP_DAY_GENITIVE[int(day)] or PREP_DAY_RU[int(day)]
    if pull == "morning":
        return f"утром {name}"
    return f"вечером накануне {name}"


def container_number(label: str | None) -> str | None:
    if not label:
        return None
    match = re.search(r"№\s*(\d+)", label)
    return f"№{match.group(1)}" if match else None


def format_container_list(labels: list[str]) -> str:
    nums = [container_number(label) for label in labels]
    if labels and all(nums):
        word = "контейнер" if len(nums) == 1 else "контейнеры"
        if len(nums) == 1:
            joined = nums[0]
        elif len(nums) == 2:
            joined = f"{nums[0]} и {nums[1]}"
        else:
            joined = ", ".join(nums[:-1]) + f" и {nums[-1]}"
        return f"{word} {joined}"
    return ", ".join(label for label in labels if label)


def thaw_reminders_for_day(day: int, containers: list[dict]) -> list[str]:
    due = [
        box
        for box in containers
        if box.get("place") == "freezer" and box.get("thaw_before_day") == day
    ]
    evening = [box for box in due if thaw_pull_mode(box) == "evening_before"]
    morning = [box for box in due if thaw_pull_mode(box) == "morning"]
    names = lambda boxes: format_container_list([box.get("label") or "" for box in boxes])
    lines: list[str] = []
    if evening:
        lines.append(
            f"С вечера {thaw_prev_day_genitive(day)} достаньте из морозилки "
            f"{names(evening)} и переложите в холодильник."
        )
    if morning:
        lines.append(
            f"Утром достаньте из морозилки {names(morning)} и переложите в холодильник."
        )
    return lines


def format_clock(row: dict) -> str | None:
    raw = row.get("t_min")
    if raw is None or raw == "":
        return None
    minutes = raw if isinstance(raw, int) else int(raw)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def format_timer(step: dict) -> str | None:
    seconds = step.get("timer_seconds")
    label = step.get("timer_label")
    note = step.get("timer_note")
    pull = step.get("pull_internal_temperature_c")
    target = step.get("target_internal_temperature_c")
    hold = step.get("hold_seconds")
    if seconds is None and not label and not note and pull is None and target is None and hold is None:
        return None
    parts: list[str] = []
    if seconds is not None:
        if seconds >= 120 and seconds % 60 == 0:
            head = f"таймер {seconds // 60} мин"
        else:
            head = f"таймер {seconds} с"
        if label:
            head = f"{head} ({label})"
        parts.append(head)
    elif label:
        parts.append(label)
    if note:
        parts.append(note)
    if pull is not None:
        parts.append(f"снятие {pull} °C")
    if target is not None:
        parts.append(f"цель {target} °C")
    if hold is not None:
        parts.append(f"выдержка {hold} с")
    if not parts:
        return None
    return "_" + "; ".join(parts) + "_"


def allergen_line(allergens: dict | None) -> str | None:
    if not allergens:
        return None
    contains = [ALLERGEN.get(code, code) for code in (allergens.get("contains") or [])]
    may_contain = [ALLERGEN.get(code, code) for code in (allergens.get("may_contain") or [])]
    unknown = [ALLERGEN.get(code, code) for code in (allergens.get("unknown") or [])]
    bits: list[str] = []
    if contains:
        bits.append(", ".join(contains))
    if may_contain:
        bits.append("следы: " + ", ".join(may_contain))
    if unknown:
        bits.append("неизвестно: " + ", ".join(unknown))
    if not bits:
        return None
    return "Аллергены набора: " + "; ".join(bits) + "."


def slot_title(slot: dict) -> str:
    return (slot.get("plate_title") or slot.get("flavor") or slot.get("title") or "").strip()


def fetch_kit(slug: str, *, no_leftover: bool = False) -> dict:
    qs = urlencode({"no_leftover": "1"}) if no_leftover else ""
    suffix = f"?{qs}" if qs else ""
    return get_json(f"{BASE}/api/prep-kits/{slug}/{suffix}")


def fetch_slot_recipe(kit_slug: str, slot: dict, *, no_leftover: bool = False, slug: str | None = None) -> dict:
    params = {
        "prep": kit_slug,
        "day": slot["day"],
        "meal": slot["meal"],
    }
    if no_leftover:
        params["no_leftover"] = "1"
    url = f"{BASE}/api/recipes/{slug or slot['slug']}/?{urlencode(params)}"
    return get_json(url)


def render_steps(steps: list[dict]) -> list[str]:
    lines: list[str] = []
    for i, step in enumerate(steps, start=1):
        lines.append(f"{i}. {(step.get('text') or '').strip()}")
        timer = format_timer(step)
        if timer:
            lines.append(f"   {timer}")
    return lines


def render_shopping(rows: list[dict]) -> list[str]:
    if not rows:
        return ["Список закупки пуст.", ""]
    lines = ["### Что купить", ""]
    for row in rows:
        amount = (row.get("display_amount") or "").strip()
        title = (row.get("title_ru") or row.get("canonical_id") or "").strip()
        if amount and title:
            lines.append(f"- {amount} {title}")
        elif title:
            lines.append(f"- {title}")
        else:
            lines.append(f"- {amount}")
    lines.append("")
    return lines


def render_sunday(kit: dict) -> list[str]:
    lines = ["### Рецепт воскресенья", ""]
    timeline = kit.get("weekend_timeline") or []
    intro = [row for row in timeline if row.get("kind") == "intro"]
    recipe_steps = [row for row in timeline if row.get("kind") != "intro"]
    for row in intro:
        hands = row.get("hands") if isinstance(row.get("hands"), str) else ""
        if hands.strip():
            lines.append(hands.strip())
            lines.append("")
    for i, row in enumerate(recipe_steps, start=1):
        hands = row.get("hands") if isinstance(row.get("hands"), str) else ""
        clock = format_clock(row)
        head = f"{i}. "
        if clock:
            head += f"**{clock}.** "
        lines.append(head + hands.strip())
    if recipe_steps:
        lines.append("")
    return lines


def render_containers(kit: dict) -> list[str]:
    lines = ["### Куда разложить", ""]
    caption = cold_container_caption(kit.get("containers") or [])
    if caption:
        lines.append(caption)
        lines.append("")
    for box in kit.get("containers") or []:
        label = (box.get("label") or "").strip()
        amount = (box.get("display_amount") or "").strip()
        what = (box.get("component_title") or "").strip()
        place = PREP_PLACE_RU.get(box.get("place") or "", box.get("place") or "")
        thaw = format_thaw_column(box)
        head = f"- **{label}**"
        if amount:
            head += f" · {amount}"
        tail = [part for part in (what, place) if part]
        text = f"{head} — {' · '.join(tail)}" if tail else head
        if thaw != "—":
            text += f" · достать {thaw}"
        lines.append(text)
    lines.append("")
    return lines


def render_components(kit: dict) -> list[str]:
    components = kit.get("components") or []
    if not components:
        return []
    lines = ["### Подробнее по каждой заготовке", ""]
    for item in components:
        title = (item.get("title") or "").strip()
        amount = (item.get("display_amount") or "").strip()
        head = f"**{title}**"
        if amount:
            head += f" · {amount}"
        lines.append(head)
        lines.append("")
        steps = item.get("weekend_steps") or []
        for i, step in enumerate(steps, start=1):
            text = step if isinstance(step, str) else str(step)
            lines.append(f"{i}. {text.strip()}")
        if steps:
            lines.append("")
    return lines


def render_slot_body(kit_slug: str, slot: dict, *, no_leftover: bool) -> list[str]:
    mode = PREP_MODE_RU.get(slot.get("mode") or "", slot.get("mode") or "")
    meal = PREP_MEAL_RU.get(slot.get("meal") or "", slot.get("meal") or "")
    lines = [f"**{meal} · {mode}**", "", slot_title(slot), ""]
    composition = (slot.get("plate_composition") or "").strip()
    if composition:
        lines.append(composition)
        lines.append("")
    boxes = slot.get("containers") or []
    if boxes:
        for box in boxes:
            label = (box.get("label") or "").strip()
            what = (box.get("component_title") or "").strip()
            amount = (box.get("display_amount") or "").strip()
            place = PREP_PLACE_RU.get(box.get("place") or "", "")
            bits = [part for part in (label and f"**{label}**", what, amount) if part]
            extra = f" · {place}" if place == "Морозилка" else ""
            lines.append(f"- {' · '.join(bits)}{extra}".rstrip())
        lines.append("")
    recipe = fetch_slot_recipe(kit_slug, slot, no_leftover=no_leftover)
    prep_items = recipe.get("prep") or []
    if prep_items:
        lines.append("Заранее")
        lines.append("")
        for item in prep_items:
            text = (item.get("text") or "").strip()
            if text:
                lines.append(f"- {text}")
        lines.append("")
    steps = recipe.get("steps") or []
    if steps:
        lines.extend(render_steps(steps))
        lines.append("")
    for alt in slot.get("alternatives") or []:
        if not isinstance(alt, dict) or not alt.get("slug"):
            continue
        label = (alt.get("label") or alt.get("slug") or "").strip()
        lines.append(f"Замена: {label}")
        lines.append("")
        alt_recipe = fetch_slot_recipe(
            kit_slug, slot, no_leftover=no_leftover, slug=alt["slug"]
        )
        alt_steps = alt_recipe.get("steps") or []
        if alt_steps:
            lines.extend(render_steps(alt_steps))
            lines.append("")
    return lines


def render_meals(kit: dict, *, no_leftover: bool, heading: str = "### Блюда на неделю") -> list[str]:
    lines = [heading, ""]
    slots = kit.get("slots") or []
    containers = kit.get("containers") or []
    for day in range(1, 8):
        day_slots = [slot for slot in slots if slot.get("day") == day]
        day_slots.sort(key=lambda slot: 0 if slot.get("meal") == "lunch" else 1)
        if not day_slots:
            continue
        lines.append(f"#### {PREP_DAY_FULL[day]}")
        lines.append("")
        for reminder in thaw_reminders_for_day(day, containers):
            lines.append(reminder)
            lines.append("")
        for slot in day_slots:
            lines.extend(render_slot_body(kit["slug"], slot, no_leftover=no_leftover))
    return lines


def slot_signature(slot: dict, recipe: dict) -> tuple:
    steps = tuple((step.get("text") or "").strip() for step in (recipe.get("steps") or []))
    prep = tuple((item.get("text") or "").strip() for item in (recipe.get("prep") or []))
    boxes = tuple(
        (
            box.get("code"),
            box.get("display_amount"),
            box.get("label"),
        )
        for box in (slot.get("containers") or [])
    )
    alts = tuple((item.get("slug"), item.get("label")) for item in (slot.get("alternatives") or []))
    return (
        slot.get("slug"),
        slot.get("mode"),
        slot_title(slot),
        (slot.get("plate_composition") or "").strip(),
        boxes,
        alts,
        prep,
        steps,
    )


def shopping_signature(rows: list[dict]) -> tuple:
    return tuple(
        (
            row.get("canonical_id"),
            row.get("title_ru"),
            row.get("display_amount"),
        )
        for row in rows
    )


def render_no_leftover(base: dict, variant: dict) -> list[str]:
    if not base.get("has_leftovers"):
        return []
    lines = ["### Без вчерашнего", ""]
    caption = (
        "Блюдо на один приём; вместо разогрева — другое из набора. Меняет закупку и воскресенье."
    )
    extra = leftover_cost_caption(base.get("leftover_cost"))
    if extra:
        caption = f"{caption} {extra}"
    lines.append(caption)
    lines.append("")
    if shopping_signature(base.get("shopping") or []) != shopping_signature(variant.get("shopping") or []):
        lines.append("#### Что купить с галочкой")
        lines.append("")
        # reuse shopping renderer but it adds ### — strip that
        shop = render_shopping(variant.get("shopping") or [])
        lines.extend(shop[2:] if shop and shop[0].startswith("###") else shop)

    changed: list[dict] = []
    base_by_key = {(slot["day"], slot["meal"]): slot for slot in base.get("slots") or []}
    for slot in variant.get("slots") or []:
        key = (slot["day"], slot["meal"])
        old = base_by_key.get(key)
        new_recipe = fetch_slot_recipe(variant["slug"], slot, no_leftover=True)
        if old is None:
            changed.append(slot)
            continue
        old_recipe = fetch_slot_recipe(base["slug"], old, no_leftover=False)
        if slot_signature(old, old_recipe) != slot_signature(slot, new_recipe):
            changed.append(slot)

    if changed:
        lines.append("Что меняется:")
        lines.append("")
        current_day = None
        for slot in changed:
            day = slot["day"]
            if day != current_day:
                current_day = day
                lines.append(f"#### {PREP_DAY_FULL[day]}")
                lines.append("")
            lines.extend(render_slot_body(variant["slug"], slot, no_leftover=True))
    return lines


def render_kit(base: dict, variant: dict) -> str:
    parts: list[str] = [f"## {base['title']}", ""]
    summary = (base.get("summary") or "").strip()
    if summary:
        parts.append(summary)
        parts.append("")
    caution = (base.get("caution_text") or "").strip()
    if caution:
        parts.append(f"**Осторожно.** {caution}")
        parts.append("")
    allergens = allergen_line(base.get("allergens"))
    if allergens:
        parts.append(allergens)
        parts.append("")
    parts.extend(render_shopping(base.get("shopping") or []))
    parts.extend(render_sunday(base))
    parts.extend(render_containers(base))
    parts.extend(render_components(base))
    parts.extend(render_meals(base, no_leftover=False))
    leftover = render_no_leftover(base, variant)
    if leftover:
        parts.extend(leftover)
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    catalog = get_json(f"{BASE}/api/prep-kits/")
    cards = catalog.get("results") or []
    cards.sort(key=lambda item: item.get("position") or 0)
    kits = []
    for card in cards:
        slug = card["slug"]
        base = fetch_kit(slug, no_leftover=False)
        variant = fetch_kit(slug, no_leftover=True)
        kits.append((base, variant))

    toc = "\n".join(f"- {base['title']}" for base, _ in kits)
    blocks = "\n---\n\n".join(render_kit(base, variant) for base, variant in kits)
    text = (
        f"# На неделю\n\n{CATALOG_LEDE}\n\n{toc}\n\n---\n\n{blocks}"
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(text, encoding="utf-8")

    titles = " — ".join(base["title"] for base, _ in kits)
    readme = (
        "# Выгрузка «На неделю»\n\n"
        "Тексты с живой страницы `/prep`: лид каталога, шапка набора, закупка, "
        "рецепт воскресенья, боксы, слоты будней и шаги тарелки.\n"
        "Без ккал, минут экономии и книжного тела рецепта (оно в "
        "[recipes/all.md](../recipes/all.md)).\n\n"
        f"Наборов: **{len(kits)}**. Один файл.\n\n"
        f"## [all.md](all.md) — {len(kits)} шт.\n\n"
        f"{titles}\n\n"
        + "\n".join(f"- {base['title']}" for base, _ in kits)
        + "\n"
    )
    README.write_text(readme, encoding="utf-8")
    print("wrote", OUT_FILE, "kits", len(kits), "chars", len(text))


if __name__ == "__main__":
    main()
