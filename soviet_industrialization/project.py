from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ProjectStage(str, Enum):
    SURVEY = "survey"
    DESIGN = "design"
    CIVIL_WORKS = "civil_works"
    EQUIPMENT = "equipment"
    ELECTRICITY = "electricity"
    LABOR = "labor"
    FREIGHT_ACCESS = "freight_access"
    MAINTENANCE = "maintenance"
    TRIAL_OPERATION = "trial_operation"
    COMMISSIONED = "commissioned"


CONSTRUCTION_STAGES = (
    ProjectStage.SURVEY,
    ProjectStage.DESIGN,
    ProjectStage.CIVIL_WORKS,
    ProjectStage.EQUIPMENT,
    ProjectStage.ELECTRICITY,
    ProjectStage.LABOR,
    ProjectStage.FREIGHT_ACCESS,
    ProjectStage.MAINTENANCE,
    ProjectStage.TRIAL_OPERATION,
)


@dataclass(frozen=True)
class Project:
    name: str
    region: str
    nameplate_capacity: float
    stage_costs: Mapping[ProjectStage, Mapping[str, float]]
    priority: int = 0

    def __post_init__(self) -> None:
        if self.nameplate_capacity <= 0:
            raise ValueError("project capacity must be positive")
        missing_stages = set(CONSTRUCTION_STAGES) - set(self.stage_costs)
        if missing_stages:
            raise ValueError(f"project is missing stages: {missing_stages}")
        unknown_stages = set(self.stage_costs) - set(CONSTRUCTION_STAGES)
        if unknown_stages:
            raise ValueError(f"unknown project stages: {unknown_stages}")
        for stage in CONSTRUCTION_STAGES:
            costs = self.stage_costs[stage]
            if not costs or any(amount <= 0 for amount in costs.values()):
                raise ValueError(f"{stage.value} must have positive resource costs")

    @property
    def stages(self) -> tuple[ProjectStage, ...]:
        return tuple(stage for stage in CONSTRUCTION_STAGES if stage in self.stage_costs)


@dataclass(frozen=True)
class ProjectState:
    project: Project
    stage: ProjectStage
    blocked_by: tuple[str, ...] = ()

    @property
    def planned_capacity(self) -> float:
        return self.project.nameplate_capacity

    @property
    def physically_complete(self) -> bool:
        return self.stage in (
            ProjectStage.ELECTRICITY,
            ProjectStage.LABOR,
            ProjectStage.FREIGHT_ACCESS,
            ProjectStage.MAINTENANCE,
            ProjectStage.TRIAL_OPERATION,
            ProjectStage.COMMISSIONED,
        )

    @property
    def built_capacity(self) -> float:
        if self.physically_complete:
            return self.project.nameplate_capacity
        return 0

    @property
    def commissioned_capacity(self) -> float:
        if self.stage == ProjectStage.COMMISSIONED:
            return self.project.nameplate_capacity
        return 0

    @property
    def operating_output(self) -> float:
        return 0

    @property
    def utilization(self) -> float:
        if self.commissioned_capacity == 0:
            return 0
        return self.operating_output / self.commissioned_capacity

    @classmethod
    def planned_for(cls, project: Project) -> ProjectState:
        return cls(project=project, stage=project.stages[0])