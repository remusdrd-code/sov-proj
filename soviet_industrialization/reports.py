from __future__ import annotations

from datetime import date
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from .simulation import SimulationState


@dataclass(frozen=True)
class SectorReport:
    region: str
    sector: str
    nameplate_capacity: float
    commissioned_capacity: float
    operating_output: float
    utilization: float
    connectivity: float
    bottlenecks: tuple[str, ...]
    disorganization: tuple[str, ...]


@dataclass(frozen=True)
class ControlFigureComparison:
    milestone_year: int
    actual: Mapping[str, float]
    control: Mapping[str, float]
    variance: Mapping[str, float]


@dataclass(frozen=True)
class AnalyticalReport:
    date: date
    regions: Mapping[tuple[str, str], SectorReport]
    connected_routes: int
    total_routes: int
    bottlenecks: tuple[str, ...]
    disorganization: tuple[str, ...]
    milestone_year: int | None = None
    control_figure_comparison: ControlFigureComparison | None = None

    @property
    def connectivity(self) -> float:
        if not self.total_routes:
            return 1.0
        return self.connected_routes / self.total_routes

    @property
    def nameplate_capacity(self) -> float:
        return sum(row.nameplate_capacity for row in self.regions.values())

    @property
    def commissioned_capacity(self) -> float:
        return sum(row.commissioned_capacity for row in self.regions.values())

    @property
    def operating_output(self) -> float:
        return sum(row.operating_output for row in self.regions.values())

    @property
    def utilization(self) -> float:
        if not self.commissioned_capacity:
            return 0
        return self.operating_output / self.commissioned_capacity


def historical_milestones(through_year: int) -> tuple[int, ...]:
    required = {1928, 1932, 1937, 1942}
    required.update(range(1947, through_year + 1, 5))
    return tuple(year for year in sorted(required) if year <= through_year)


def build_report(state: SimulationState) -> AnalyticalReport:
    rows: dict[tuple[str, str], SectorReport] = {}
    bottlenecks: set[str] = set()
    disorganization: list[str] = []
    sector_disorganization: dict[tuple[str, str], list[str]] = {}

    project_groups: dict[tuple[str, str], list[object]] = {}
    for project_state in state.projects.values():
        key = (project_state.project.region, project_state.project.sector)
        project_groups.setdefault(key, []).append(project_state)
        sector_messages = sector_disorganization.setdefault(key, [])
        bottlenecks.update(project_state.blocked_by)
        if project_state.binding_constraint:
            bottlenecks.add(project_state.binding_constraint)
        if project_state.stage.value != "commissioned":
            message = f"unfinished project: {project_state.project.name}"
            disorganization.append(message)
            sector_messages.append(message)
        for resource in project_state.blocked_by:
            message = f"project {project_state.project.name} blocked by {resource}"
            disorganization.append(message)
            sector_messages.append(message)
        if project_state.binding_constraint:
            message = (
                f"project {project_state.project.name} constrained by "
                f"{project_state.binding_constraint}"
            )
            disorganization.append(message)
            sector_messages.append(message)
        if project_state.maintenance_deficit_days:
            message = (
                f"project {project_state.project.name} has insufficient maintenance "
                f"for {project_state.maintenance_deficit_days} days"
            )
            disorganization.append(message)
            sector_messages.append(message)

    for key, project_states in project_groups.items():
        nameplate = sum(item.nameplate_capacity for item in project_states)
        commissioned = sum(item.commissioned_capacity for item in project_states)
        output = sum(item.operating_output for item in project_states)
        rows[key] = SectorReport(
            region=key[0],
            sector=key[1],
            nameplate_capacity=nameplate,
            commissioned_capacity=commissioned,
            operating_output=output,
            utilization=output / commissioned if commissioned else 0,
            connectivity=_region_connectivity(state, key[0]),
            bottlenecks=tuple(
                sorted(
                    {
                        constraint
                        for item in project_states
                        for constraint in (
                            *item.blocked_by,
                            *(() if item.binding_constraint is None else (item.binding_constraint,)),
                        )
                    }
                )
            ),
            disorganization=tuple(
                sector_disorganization.get(key, ())
            ),
        )

    connected_routes = sum(
        route.connected_to_legacy for route in state.routes.values()
    )
    for route in state.routes.values():
        if not route.connected_to_legacy:
            disorganization.append(f"disconnected route: {route.route_id}")

    milestone_year = state.date.year if state.date.year in historical_milestones(state.date.year) else None
    return AnalyticalReport(
        date=state.date,
        regions=MappingProxyType(rows),
        connected_routes=connected_routes,
        total_routes=len(state.routes),
        bottlenecks=tuple(sorted(bottlenecks)),
        disorganization=tuple(disorganization),
        milestone_year=milestone_year,
    )


def compare_control_figures(
    report: AnalyticalReport, control_figures: Mapping[str, float]
) -> ControlFigureComparison:
    actual = {
        name: float(getattr(report, name)) for name in control_figures
    }
    control = dict(control_figures)
    variance = {
        name: actual[name] - expected for name, expected in control.items()
    }
    return ControlFigureComparison(
        milestone_year=1932,
        actual=MappingProxyType(actual),
        control=MappingProxyType(control),
        variance=MappingProxyType(variance),
    )


def _region_connectivity(state: SimulationState, region: str) -> float:
    relevant = [
        route
        for route in state.routes.values()
        if route.start.name == region or route.end.name == region
    ]
    if not relevant:
        return 1.0
    return sum(route.connected_to_legacy for route in relevant) / len(relevant)
