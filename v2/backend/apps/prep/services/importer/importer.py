from __future__ import annotations

from apps.prep.models import PrepKit
from apps.prep.services.importer.contracts import KitDraft, KitImportError
from apps.prep.services.importer.repository import persist_kit, unpublished_recipe_errors
from apps.prep.services.importer.validators import collect_payload_errors, draft_from_payload


def validate_kit_payload(payload: dict) -> list[str]:
    errors, slugs = collect_payload_errors(payload)
    errors.extend(unpublished_recipe_errors(slugs))
    return errors


def parse_kit_draft(payload: dict) -> tuple[KitDraft | None, list[str]]:
    errors, slugs = collect_payload_errors(payload)
    errors.extend(unpublished_recipe_errors(slugs))
    if errors:
        return None, errors
    return draft_from_payload(payload, slugs), []


def upsert_kit(
    payload: dict,
    *,
    dry_run: bool = False,
    publish: bool | None = None,
) -> PrepKit | None:
    draft, errors = parse_kit_draft(payload)
    if errors:
        raise KitImportError(errors)
    if dry_run:
        return None
    assert draft is not None
    return persist_kit(draft, publish=publish)
