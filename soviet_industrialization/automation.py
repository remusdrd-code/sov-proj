from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class AutomationSystem(StrEnum):
    INDUSTRY = "industry"
    BUILDING = "building"
    TRANSPORT = "transport"
    LOGISTICS = "logistics"
    IMPORTS = "imports"
    STAFFING = "staffing"
    MAINTENANCE = "maintenance"
    PROJECT_SEQUENCING = "project_sequencing"


@dataclass(frozen=True)
class ManualOrder:
    order_id: str
    system: AutomationSystem
    target: str
    action: str


@dataclass(frozen=True)
class ActionQueueItem:
    order_id: str
    system: AutomationSystem
    target: str
    action: str


def default_automation_switches() -> Mapping[AutomationSystem, bool]:
    return MappingProxyType({system: True for system in AutomationSystem})
