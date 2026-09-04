from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import IntEnum
from types import MappingProxyType
from typing import Mapping

from .map import NationalMap, default_national_map
from .network import InfrastructureRoute
from .project import Project, ProjectStage, ProjectState


class SimulationSpeed(IntEnum):
    NORMAL = 1
    FAST = 2
    VERY_FAST = 4


@dataclass(frozen=True)
class Facility:
    name: str
    input_resource: str
    input_per_day: float
    output_resource: str
    output_per_day: float

    def __post_init__(self) -> None:
        if self.input_per_day <= 0 or self.output_per_day <= 0:
            raise ValueError("facility flow rates must be positive")


@dataclass(frozen=True)
class FacilityState:
    facility: Facility
    daily_output: float = 0


@dataclass(frozen=True)
class SimulationState:
    date: datetime.date
    resources: Mapping[str, float]
    facilities: Mapping[str, FacilityState]
    projects: Mapping[str, ProjectState]
    routes: Mapping[str, InfrastructureRoute]
    national_map: NationalMap
    paused: bool = False
    speed: SimulationSpeed = SimulationSpeed.NORMAL


class Simulation:
    """A daily simulation transition with a small observable resource flow."""

    def __init__(
        self,
        start_date: datetime.date,
        resources: Mapping[str, float],
        facilities: tuple[Facility, ...] = (),
        projects: tuple[Project, ...] = (),
        routes: tuple[InfrastructureRoute, ...] = (),
        national_map: NationalMap | None = None,
    ) -> None:
        facility_states = {
            facility.name: FacilityState(facility=facility) for facility in facilities
        }
        if len(facility_states) != len(facilities):
            raise ValueError("facility names must be unique")
        project_states = {
            project.name: ProjectState.planned_for(project) for project in projects
        }
        if len(project_states) != len(projects):
            raise ValueError("project names must be unique")
        route_states = {route.route_id: route for route in routes}
        if len(route_states) != len(routes):
            raise ValueError("route endpoints must be unique")
        self._state = SimulationState(
            date=start_date,
            resources=MappingProxyType(dict(resources)),
            facilities=MappingProxyType(facility_states),
            projects=MappingProxyType(project_states),
            routes=MappingProxyType(route_states),
            national_map=national_map or default_national_map(),
        )

    @property
    def state(self) -> SimulationState:
        return self._state

    def pause(self) -> None:
        self._state = SimulationState(
            date=self._state.date,
            resources=self._state.resources,
            facilities=self._state.facilities,
            projects=self._state.projects,
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=True,
            speed=self._state.speed,
        )

    def resume(self) -> None:
        self._state = SimulationState(
            date=self._state.date,
            resources=self._state.resources,
            facilities=self._state.facilities,
            projects=self._state.projects,
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=False,
            speed=self._state.speed,
        )

    def set_speed(self, speed: SimulationSpeed) -> None:
        if self._state.paused:
            self._state = SimulationState(
                date=self._state.date,
                resources=self._state.resources,
                facilities=self._state.facilities,
                projects=self._state.projects,
                routes=self._state.routes,
                national_map=self._state.national_map,
                paused=True,
                speed=speed,
            )
            return
        self._state = SimulationState(
            date=self._state.date,
            resources=self._state.resources,
            facilities=self._state.facilities,
            projects=self._state.projects,
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=False,
            speed=speed,
        )

    def tick(self) -> SimulationState:
        if self._state.paused:
            return self._state

        resources = dict(self._state.resources)
        project_states = self._advance_projects(resources)
        facility_states: dict[str, FacilityState] = {}
        for name, facility_state in self._state.facilities.items():
            facility = facility_state.facility
            available_input = max(0, resources.get(facility.input_resource, 0))
            input_used = min(available_input, facility.input_per_day)
            output = facility.output_per_day * input_used / facility.input_per_day
            resources[facility.input_resource] = available_input - input_used
            resources[facility.output_resource] = (
                resources.get(facility.output_resource, 0) + output
            )
            facility_states[name] = FacilityState(facility=facility, daily_output=output)

        self._state = SimulationState(
            date=self._state.date + datetime.timedelta(days=1),
            resources=resources,
            facilities=facility_states,
            projects=MappingProxyType(project_states),
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=False,
            speed=self._state.speed,
        )
        return self._state

    def _advance_projects(self, resources: dict[str, float]) -> dict[str, ProjectState]:
        project_states: dict[str, ProjectState] = {}
        ordered_projects = sorted(
            self._state.projects.values(),
            key=lambda state: state.project.priority,
            reverse=True,
        )
        for project_state in ordered_projects:
            if project_state.stage == ProjectStage.COMMISSIONED:
                project_states[project_state.project.name] = project_state
                continue
            costs = project_state.project.stage_costs[project_state.stage]
            blocked_by = tuple(
                resource
                for resource, amount in costs.items()
                if resources.get(resource, 0) < amount
            )
            if blocked_by:
                project_states[project_state.project.name] = ProjectState(
                    project=project_state.project,
                    stage=project_state.stage,
                    blocked_by=blocked_by,
                )
                continue
            for resource, amount in costs.items():
                resources[resource] = resources.get(resource, 0) - amount
            stages = project_state.project.stages
            stage_index = stages.index(project_state.stage)
            next_stage = (
                ProjectStage.COMMISSIONED
                if stage_index == len(stages) - 1
                else stages[stage_index + 1]
            )
            project_states[project_state.project.name] = ProjectState(
                project=project_state.project,
                stage=next_stage,
            )
        return project_states