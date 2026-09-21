from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q

from apps.prep.constants import PrepStatus
from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot
from apps.prep.services.importer.contracts import (
    ComponentDraft,
    ContainerDraft,
    KitDraft,
    KitImportError,
    SlotDraft,
)
from apps.recipes.models import Recipe


def unpublished_recipe_errors(slugs: set[str]) -> list[str]:
    if not slugs:
        return []
    published = set(
        Recipe.objects.filter(slug__in=slugs, status="published").values_list(
            "slug", flat=True
        )
    )
    missing = sorted(slugs - published)
    if missing:
        return [f"unpublished/нет recipe: {', '.join(missing)}."]
    return []


def recipe_map(slugs: set[str]) -> dict[str, Recipe]:
    return {row.slug: row for row in Recipe.objects.filter(slug__in=slugs)}


def resolve_kit_status(existing: PrepKit | None, publish: bool | None) -> str:
    if publish is True:
        return PrepStatus.PUBLISHED
    if publish is False:
        return PrepStatus.DRAFT
    if existing is not None and existing.status == PrepStatus.PUBLISHED:
        return PrepStatus.PUBLISHED
    return PrepStatus.DRAFT


def _clean_save(instance, *, update_fields: list[str] | None = None) -> None:
    try:
        instance.full_clean()
    except DjangoValidationError as exc:
        raise KitImportError(_flatten_validation(exc)) from exc
    instance.save(update_fields=update_fields)


def _flatten_validation(exc: DjangoValidationError) -> list[str]:
    if hasattr(exc, "message_dict"):
        rows: list[str] = []
        for field, messages in exc.message_dict.items():
            for message in messages:
                rows.append(message if field == "__all__" else f"{field}: {message}")
        return rows
    return [str(item) for item in exc.messages]


def sync_components(kit: PrepKit, drafts: tuple[ComponentDraft, ...]) -> dict[str, PrepComponent]:
    existing = {item.code: item for item in kit.components.all()}
    expected = {draft.code for draft in drafts}
    kit.components.exclude(code__in=expected).delete()

    result: dict[str, PrepComponent] = {}
    for draft in drafts:
        values = {
            "title": draft.title,
            "canonical_ids": list(draft.canonical_ids),
            "qty": draft.qty,
            "unit": draft.unit,
            "weekend_steps": list(draft.weekend_steps),
            "parcook": dict(draft.parcook),
            "storage": dict(draft.storage),
        }
        component = existing.get(draft.code)
        if component is None:
            component = PrepComponent(kit=kit, code=draft.code, **values)
            _clean_save(component)
        else:
            for name, value in values.items():
                setattr(component, name, value)
            _clean_save(component, update_fields=list(values))
        result[draft.code] = component
    return result


def sync_containers(
    kit: PrepKit,
    drafts: tuple[ContainerDraft, ...],
    components: dict[str, PrepComponent],
) -> None:
    existing = {item.code: item for item in kit.containers.all()}
    expected = {draft.code for draft in drafts}
    kit.containers.exclude(code__in=expected).delete()

    for draft in drafts:
        values = {
            "label": draft.label,
            "component": components[draft.component_code],
            "qty": draft.qty,
            "unit": draft.unit,
            "place": draft.place,
            "thaw_before_day": draft.thaw_before_day,
        }
        container = existing.get(draft.code)
        if container is None:
            container = PrepContainer(kit=kit, code=draft.code, **values)
            _clean_save(container)
        else:
            for name, value in values.items():
                setattr(container, name, value)
            _clean_save(container, update_fields=list(values))


def sync_slots(
    kit: PrepKit,
    drafts: tuple[SlotDraft, ...],
    recipes: dict[str, Recipe],
) -> None:
    existing = {(item.day, item.meal): item for item in kit.slots.all()}
    keep = Q()
    for draft in drafts:
        keep |= Q(day=draft.day, meal=draft.meal)
    if drafts:
        kit.slots.exclude(keep).delete()
    else:
        kit.slots.all().delete()

    for draft in drafts:
        values = {
            "recipe": recipes[draft.slug],
            "mode": draft.mode,
            "flavor": draft.flavor,
            "plate": dict(draft.plate),
            "source": dict(draft.source),
            "container_ids": list(draft.container_ids),
            "alternatives": list(draft.alternatives),
            "servings_cooked": draft.servings_cooked,
            "feeds_slots": draft.feeds_slots,
            "time_active_from_prep_min": draft.time_active_from_prep_min,
            "time_active_scratch_min": draft.time_active_scratch_min,
            "steps": list(draft.steps),
            "no_leftover": dict(draft.no_leftover),
        }
        slot = existing.get((draft.day, draft.meal))
        if slot is None:
            slot = PrepSlot(kit=kit, day=draft.day, meal=draft.meal, **values)
            _clean_save(slot)
        else:
            for name, value in values.items():
                setattr(slot, name, value)
            _clean_save(slot, update_fields=list(values))


def persist_kit(draft: KitDraft, *, publish: bool | None) -> PrepKit:
    with transaction.atomic():
        kit = PrepKit.objects.filter(slug=draft.slug).first()
        status = resolve_kit_status(kit, publish)
        values = {
            "title": draft.title,
            "summary": draft.summary,
            "servings_base": draft.servings_base,
            "caution_text": draft.caution_text,
            "rhythm": draft.rhythm,
            "status": status,
            "position": draft.position,
            "metrics": dict(draft.metrics),
            "weekend_timeline": list(draft.weekend_timeline),
            "shopping": list(draft.shopping),
            "allergens": dict(draft.allergens),
        }
        if kit is None:
            kit = PrepKit(slug=draft.slug, **values)
            _clean_save(kit)
        else:
            for name, value in values.items():
                setattr(kit, name, value)
            _clean_save(kit, update_fields=list(values))

        components = sync_components(kit, draft.components)
        sync_containers(kit, draft.containers, components)
        recipes = recipe_map(set(draft.recipe_slugs))
        sync_slots(kit, draft.slots, recipes)
        return kit
