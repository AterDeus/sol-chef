from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


class KitImportError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True, slots=True)
class ComponentDraft:
    code: str
    title: str
    canonical_ids: tuple
    qty: Decimal
    unit: str
    weekend_steps: list
    parcook: dict
    storage: dict


@dataclass(frozen=True, slots=True)
class ContainerDraft:
    code: str
    component_code: str
    label: str
    qty: Decimal
    unit: str
    place: str
    thaw_before_day: int | None


@dataclass(frozen=True, slots=True)
class SlotDraft:
    day: int
    meal: str
    slug: str
    mode: str
    flavor: str | None
    plate: dict
    source: dict
    container_ids: list[str]
    alternatives: list
    servings_cooked: int | None
    feeds_slots: int | None
    time_active_from_prep_min: int | None
    time_active_scratch_min: int | None
    steps: list
    no_leftover: dict


@dataclass(frozen=True, slots=True)
class KitDraft:
    slug: str
    title: str
    summary: str | None
    servings_base: int | None
    caution_text: str | None
    rhythm: str | None
    position: int
    metrics: dict
    weekend_timeline: list
    shopping: list[dict]
    allergens: dict
    components: tuple[ComponentDraft, ...]
    containers: tuple[ContainerDraft, ...]
    slots: tuple[SlotDraft, ...]
    recipe_slugs: frozenset[str]
