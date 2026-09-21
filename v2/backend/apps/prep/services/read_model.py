from __future__ import annotations

from dataclasses import dataclass

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot


@dataclass(frozen=True, slots=True)
class KitData:
    kit: PrepKit
    components: tuple[PrepComponent, ...]
    containers: tuple[PrepContainer, ...]
    slots: tuple[PrepSlot, ...]

    @property
    def containers_by_code(self) -> dict[str, PrepContainer]:
        return {container.code: container for container in self.containers}


def load_kit_data(kit: PrepKit) -> KitData:
    return KitData(
        kit=kit,
        components=tuple(kit.components.all()),
        containers=tuple(kit.containers.all()),
        slots=tuple(kit.slots.all()),
    )
