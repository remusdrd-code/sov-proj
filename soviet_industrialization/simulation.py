from __future__ import annotations

import datetime
from dataclasses import dataclass, replace
from enum import IntEnum
from types import MappingProxyType
from typing import Mapping

from .automation import (
    ActionQueueItem,
    AutomationSystem,
    DecisionSeverity,
    ManualOrder,
    default_automation_switches,
)
from .map import NationalMap, default_national_map
from .network import InfrastructureRoute
from .project import Project, ProjectStage, ProjectState
from .reports import (
    AnalyticalReport,
    ControlFigureComparison,
    build_report,
    compare_control_figures,
)


class SimulationSpeed(IntEnum):
    NORMAL = 1
    FAST = 2
    VERY_FAST = 4


def _is_quarter_start(date: datetime.date) -> bool:
    return date.day == 1 and date.month in (1, 4, 7, 10)


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
    automation: Mapping[AutomationSystem, bool] = default_automation_switches()
    global_automation: bool = True
    manual_orders: Mapping[str, ManualOrder] = MappingProxyType({})
    action_queue: tuple[ActionQueueItem, ...] = ()
    suppressed_decisions: frozenset[str] = frozenset()
    delegated_automation: frozenset[AutomationSystem] = frozenset()
    critical_pause_latched: bool = False
    reports: tuple[AnalyticalReport, ...] = ()
    technical_knowledge: Mapping[str, float] = MappingProxyType({})
    supply_chains: tuple[str, ...] = ()


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
        technical_knowledge: Mapping[str, float] | None = None,
        supply_chains: tuple[str, ...] = (),
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
            technical_knowledge=MappingProxyType(dict(technical_knowledge or {})),
            supply_chains=tuple(supply_chains),
        )

    @property
    def state(self) -> SimulationState:
        return self._state

    def add_resources(self, amounts: Mapping[str, float]) -> None:
        resources = dict(self._state.resources)
        for resource, amount in amounts.items():
            resources[resource] = resources.get(resource, 0) + amount
        self._state = SimulationState(
            date=self._state.date,
            resources=MappingProxyType(resources),
            facilities=self._state.facilities,
            projects=self._state.projects,
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=self._state.paused,
            speed=self._state.speed,
            automation=self._state.automation,
            global_automation=self._state.global_automation,
            manual_orders=self._state.manual_orders,
            action_queue=self._state.action_queue,
            suppressed_decisions=self._state.suppressed_decisions,
            delegated_automation=self._state.delegated_automation,
            critical_pause_latched=self._state.critical_pause_latched,
            reports=self._state.reports,
            technical_knowledge=self._state.technical_knowledge,
            supply_chains=self._state.supply_chains,
        )

    def add_project(self, project: Project) -> None:
        if project.name in self._state.projects:
            raise ValueError("project names must be unique")
        projects = dict(self._state.projects)
        projects[project.name] = ProjectState.planned_for(project)
        self._state = replace(
            self._state,
            projects=MappingProxyType(projects),
            action_queue=self._build_action_queue(projects),
        )

    def add_route(self, route: InfrastructureRoute) -> None:
        if route.route_id in self._state.routes:
            raise ValueError("route identifiers must be unique")
        routes = dict(self._state.routes)
        routes[route.route_id] = route
        self._state = replace(self._state, routes=MappingProxyType(routes))

    def add_technical_knowledge(self, name: str, amount: float = 1) -> None:
        if not name or amount <= 0:
            raise ValueError("technical knowledge additions must be positive and named")
        knowledge = dict(self._state.technical_knowledge)
        knowledge[name] = knowledge.get(name, 0) + amount
        self._state = replace(
            self._state,
            technical_knowledge=MappingProxyType(knowledge),
        )

    def add_supply_chain(self, name: str) -> None:
        if not name:
            raise ValueError("supply chain name must not be empty")
        if name in self._state.supply_chains:
            return
        self._state = replace(
            self._state,
            supply_chains=(*self._state.supply_chains, name),
        )

    def commission_supply_chain(self, name: str) -> None:
        self.add_supply_chain(name)

    def request_report(self) -> AnalyticalReport:
        report = build_report(self._state)
        self._state = replace(
            self._state,
            reports=self._state.reports + (report,),
        )
        return report

    def compare_to_1932_control_figures(
        self, control_figures: Mapping[str, float]
    ) -> ControlFigureComparison:
        return compare_control_figures(build_report(self._state), control_figures)

    def set_automation(self, system: AutomationSystem, enabled: bool) -> None:
        automation = dict(self._state.automation)
        automation[system] = enabled
        self._replace_automation_state(automation=automation)

    def set_global_automation(self, enabled: bool) -> None:
        self._replace_automation_state(global_automation=enabled)

    def issue_manual_order(
        self,
        system: AutomationSystem,
        target: str,
        action: str,
        order_id: str | None = None,
    ) -> ManualOrder:
        resolved_id = order_id or f"{system.value}:{target}:{action}"
        order = ManualOrder(
            order_id=resolved_id,
            system=system,
            target=target,
            action=action,
        )
        orders = dict(self._state.manual_orders)
        orders[resolved_id] = order
        self._replace_automation_state(manual_orders=orders)
        if not self._state.critical_pause_latched:
            self._state = replace(self._state, paused=False)
        return order

    def revoke_manual_order(self, order_id: str) -> None:
        orders = dict(self._state.manual_orders)
        orders.pop(order_id, None)
        self._replace_automation_state(manual_orders=orders)

    def resolve_decision(self, decision_id: str, action: str | None = None) -> None:
        decision = self._find_decision(decision_id)
        chosen_action = action or decision.recommended_action or decision.action
        if chosen_action not in decision.available_actions and chosen_action != decision.action:
            raise ValueError(f"action {chosen_action!r} is unavailable for {decision_id}")
        if chosen_action == "delegate":
            self.delegate_decision(decision_id)
            return
        manual_orders = dict(self._state.manual_orders)
        if chosen_action not in ("dismiss", "delegate"):
            manual_orders[decision.order_id] = ManualOrder(
                order_id=decision.order_id,
                system=decision.system,
                target=decision.target,
                action=chosen_action,
            )
        self._state = replace(self._state, manual_orders=MappingProxyType(manual_orders))
        self._finish_decision(decision)

    def dismiss_decision(self, decision_id: str) -> None:
        decision = self._find_decision(decision_id)
        self._finish_decision(decision)

    def delegate_decision(self, decision_id: str) -> None:
        decision = self._find_decision(decision_id)
        automation = dict(self._state.automation)
        delegated = set(self._state.delegated_automation)
        for system in decision.affected_systems or (decision.system,):
            automation[system] = True
            delegated.add(system)
        self._state = replace(
            self._state,
            automation=MappingProxyType(automation),
            delegated_automation=frozenset(delegated),
        )
        self._finish_decision(decision)

    def _finish_decision(self, decision: ActionQueueItem) -> None:
        self._state = replace(
            self._state,
            suppressed_decisions=self._state.suppressed_decisions | {decision.order_id},
            paused=(
                self._state.paused
                if decision.severity == DecisionSeverity.CRITICAL
                else False
            ),
        )
        self._refresh_action_queue()

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
            automation=self._state.automation,
            global_automation=self._state.global_automation,
            manual_orders=self._state.manual_orders,
            action_queue=self._state.action_queue,
            suppressed_decisions=self._state.suppressed_decisions,
            delegated_automation=self._state.delegated_automation,
            critical_pause_latched=self._state.critical_pause_latched,
            reports=self._state.reports,
            technical_knowledge=self._state.technical_knowledge,
            supply_chains=self._state.supply_chains,
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
            automation=self._state.automation,
            global_automation=self._state.global_automation,
            manual_orders=self._state.manual_orders,
            action_queue=self._state.action_queue,
            suppressed_decisions=self._state.suppressed_decisions,
            delegated_automation=self._state.delegated_automation,
            critical_pause_latched=False,
            reports=self._state.reports,
            technical_knowledge=self._state.technical_knowledge,
            supply_chains=self._state.supply_chains,
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
                automation=self._state.automation,
                global_automation=self._state.global_automation,
                manual_orders=self._state.manual_orders,
                action_queue=self._state.action_queue,
                suppressed_decisions=self._state.suppressed_decisions,
                delegated_automation=self._state.delegated_automation,
                critical_pause_latched=self._state.critical_pause_latched,
                reports=self._state.reports,
                technical_knowledge=self._state.technical_knowledge,
                supply_chains=self._state.supply_chains,
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
            automation=self._state.automation,
            global_automation=self._state.global_automation,
            manual_orders=self._state.manual_orders,
            action_queue=self._state.action_queue,
            suppressed_decisions=self._state.suppressed_decisions,
            delegated_automation=self._state.delegated_automation,
            critical_pause_latched=self._state.critical_pause_latched,
            reports=self._state.reports,
            technical_knowledge=self._state.technical_knowledge,
            supply_chains=self._state.supply_chains,
        )

    def tick(self) -> SimulationState:
        if self._state.paused:
            return self._state

        resources = dict(self._state.resources)
        project_states = self._advance_projects(resources)
        project_states = self._operate_commissioned_projects(project_states, resources)
        facility_states: dict[str, FacilityState] = {}
        for name, facility_state in self._state.facilities.items():
            facility = facility_state.facility
            if not self._automated(AutomationSystem.INDUSTRY, name):
                facility_states[name] = FacilityState(facility=facility)
                continue
            available_input = max(0, resources.get(facility.input_resource, 0))
            input_used = min(available_input, facility.input_per_day)
            output = facility.output_per_day * input_used / facility.input_per_day
            resources[facility.input_resource] = available_input - input_used
            resources[facility.output_resource] = (
                resources.get(facility.output_resource, 0) + output
            )
            facility_states[name] = FacilityState(facility=facility, daily_output=output)

        action_queue = self._build_action_queue(project_states, facility_states)
        next_state = SimulationState(
            date=self._state.date + datetime.timedelta(days=1),
            resources=resources,
            facilities=facility_states,
            projects=MappingProxyType(project_states),
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=self._should_autopause(action_queue),
            speed=self._state.speed,
            automation=self._state.automation,
            global_automation=self._state.global_automation,
            manual_orders=self._state.manual_orders,
            action_queue=action_queue,
            suppressed_decisions=self._state.suppressed_decisions,
            delegated_automation=self._state.delegated_automation,
            critical_pause_latched=(
                self._state.critical_pause_latched
                or any(item.severity == DecisionSeverity.CRITICAL for item in action_queue)
            ),
            reports=self._state.reports,
            technical_knowledge=self._state.technical_knowledge,
            supply_chains=self._state.supply_chains,
        )
        if _is_quarter_start(next_state.date):
            next_state = replace(
                next_state,
                reports=next_state.reports + (build_report(next_state),),
            )
        self._state = next_state
        return self._state

    def _replace_automation_state(
        self,
        *,
        automation: Mapping[AutomationSystem, bool] | None = None,
        global_automation: bool | None = None,
        manual_orders: Mapping[str, ManualOrder] | None = None,
    ) -> None:
        self._state = SimulationState(
            date=self._state.date,
            resources=self._state.resources,
            facilities=self._state.facilities,
            projects=self._state.projects,
            routes=self._state.routes,
            national_map=self._state.national_map,
            paused=self._state.paused,
            speed=self._state.speed,
            automation=MappingProxyType(
                dict(
                    self._state.automation
                    if automation is None
                    else automation
                )
            ),
            global_automation=(
                self._state.global_automation
                if global_automation is None
                else global_automation
            ),
            manual_orders=MappingProxyType(
                dict(
                    self._state.manual_orders
                    if manual_orders is None
                    else manual_orders
                )
            ),
            action_queue=(),
            suppressed_decisions=self._state.suppressed_decisions,
            delegated_automation=self._state.delegated_automation,
            critical_pause_latched=self._state.critical_pause_latched,
            reports=self._state.reports,
            technical_knowledge=self._state.technical_knowledge,
            supply_chains=self._state.supply_chains,
        )
        self._state = replace(
            self._state,
            action_queue=self._build_action_queue(self._state.projects),
        )

    def _refresh_action_queue(self) -> None:
        self._state = replace(
            self._state,
            action_queue=self._build_action_queue(self._state.projects),
        )

    def _find_decision(self, decision_id: str) -> ActionQueueItem:
        try:
            return next(
                item for item in self._state.action_queue if item.order_id == decision_id
            )
        except StopIteration as error:
            raise ValueError(f"unknown decision: {decision_id}") from error

    def _should_autopause(self, action_queue: tuple[ActionQueueItem, ...]) -> bool:
        return any(
            item.severity == DecisionSeverity.CRITICAL
            or (
                item.severity == DecisionSeverity.WARNING
                and not self._automated(item.system, item.target)
            )
            for item in action_queue
        )

    def _automated(
        self, system: AutomationSystem, target: str | None = None
    ) -> bool:
        if target is not None and any(
            order.system == system and order.target == target
            for order in self._state.manual_orders.values()
        ):
            return True
        if system in self._state.delegated_automation:
            return True
        return self._state.global_automation and self._state.automation[system]

    def _build_action_queue(
        self,
        project_states: Mapping[str, ProjectState],
        facility_states: Mapping[str, FacilityState] | None = None,
    ) -> tuple[ActionQueueItem, ...]:
        queue: list[ActionQueueItem] = []
        for name in self._state.facilities:
            if not self._automated(AutomationSystem.INDUSTRY, name):
                queue.append(
                    ActionQueueItem(
                        order_id=f"industry:{name}:operate",
                        system=AutomationSystem.INDUSTRY,
                        target=name,
                        action="operate",
                        severity=DecisionSeverity.WARNING,
                        affected_systems=(AutomationSystem.INDUSTRY,),
                        affected_projects=(name,),
                        cost_of_waiting="one day of unattended industrial output",
                        available_actions=("operate", "dismiss", "delegate"),
                        recommended_action="operate",
                    )
                )
            elif facility_states is not None:
                facility_state = facility_states[name]
                if facility_state.daily_output < facility_state.facility.output_per_day:
                    queue.append(
                        ActionQueueItem(
                            order_id=f"industry:{name}:shortage",
                            system=AutomationSystem.INDUSTRY,
                            target=name,
                            action="review_inputs",
                            severity=DecisionSeverity.NOTICE,
                            affected_systems=(AutomationSystem.INDUSTRY,),
                            affected_projects=(name,),
                            cost_of_waiting="recoverable low utilization",
                            available_actions=(
                                "review_inputs",
                                "dismiss",
                                "delegate",
                            ),
                            recommended_action="review_inputs",
                        )
                    )
        for name, project_state in project_states.items():
            if project_state.stage == ProjectStage.COMMISSIONED:
                if project_state.maintenance_deficit_days >= 6:
                    queue.append(
                        ActionQueueItem(
                            order_id=f"maintenance:{name}:critical",
                            system=AutomationSystem.MAINTENANCE,
                            target=name,
                            action="supply_maintenance",
                            severity=DecisionSeverity.CRITICAL,
                            affected_systems=(
                                AutomationSystem.MAINTENANCE,
                                AutomationSystem.INDUSTRY,
                            ),
                            affected_projects=(name,),
                            cost_of_waiting="commissioned capacity degradation",
                            available_actions=(
                                "supply_maintenance",
                                "reduce_operations",
                                "dismiss",
                                "delegate",
                            ),
                            recommended_action="supply_maintenance",
                        )
                    )
                continue
            for system, action in (
                (AutomationSystem.BUILDING, "advance"),
                (AutomationSystem.PROJECT_SEQUENCING, "sequence"),
            ):
                if not self._automated(system, name):
                    queue.append(
                        ActionQueueItem(
                            order_id=f"{system.value}:{name}:{action}",
                            system=system,
                            target=name,
                            action=action,
                            severity=DecisionSeverity.WARNING,
                            affected_systems=(system,),
                            affected_projects=(name,),
                            cost_of_waiting="one day of project delay",
                            available_actions=(action, "dismiss", "delegate"),
                            recommended_action=action,
                        )
                    )
            if project_state.blocked_by:
                queue.append(
                    ActionQueueItem(
                        order_id=f"project:{name}:blocked",
                        system=AutomationSystem.PROJECT_SEQUENCING,
                        target=name,
                        action="review_blockers",
                        severity=DecisionSeverity.NOTICE,
                        affected_systems=(AutomationSystem.PROJECT_SEQUENCING,),
                        affected_projects=(name,),
                        cost_of_waiting="project delay",
                        available_actions=(
                            "resolve_blockers",
                            "dismiss",
                            "delegate",
                        ),
                        recommended_action="resolve_blockers",
                    )
                )
        return tuple(
            item for item in queue if item.order_id not in self._state.suppressed_decisions
        )

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
            missing_enablers = tuple(
                requirement
                for requirement in (
                    *project_state.project.required_knowledge,
                    *project_state.project.required_infrastructure,
                    *project_state.project.required_supply_chains,
                )
                if (
                    requirement in project_state.project.required_knowledge
                    and self._state.technical_knowledge.get(requirement, 0) <= 0
                )
                or (
                    requirement in project_state.project.required_infrastructure
                    and not self._infrastructure_available(requirement)
                )
                or (
                    requirement in project_state.project.required_supply_chains
                    and requirement not in self._state.supply_chains
                )
            )
            if missing_enablers:
                project_states[project_state.project.name] = ProjectState(
                    project=project_state.project,
                    stage=project_state.stage,
                    blocked_by=missing_enablers,
                )
                continue
            if not (
                self._automated(AutomationSystem.BUILDING, project_state.project.name)
                and self._automated(
                    AutomationSystem.PROJECT_SEQUENCING, project_state.project.name
                )
            ):
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
                maintenance_deficit_days=project_state.maintenance_deficit_days,
            )
        return project_states

    def _operate_commissioned_projects(
        self,
        project_states: Mapping[str, ProjectState],
        resources: dict[str, float],
    ) -> dict[str, ProjectState]:
        operated: dict[str, ProjectState] = {}
        for name, project_state in project_states.items():
            if project_state.stage != ProjectStage.COMMISSIONED:
                operated[name] = project_state
                continue
            if not self._automated(AutomationSystem.INDUSTRY, name):
                operated[name] = project_state
                continue
            operating_inputs = project_state.project.operating_inputs
            if not operating_inputs:
                operated[name] = project_state
                continue
            shares: list[float] = []
            binding: str | None = None
            min_share = 1.0
            for resource, required in operating_inputs.items():
                available = max(0, resources.get(resource, 0))
                share = min(1.0, available / required)
                shares.append(share)
                if share < 1.0 and (binding is None or share < min_share):
                    binding = resource
                    min_share = share
            utilization = min(shares)
            output = project_state.commissioned_capacity * utilization
            maintenance_required = operating_inputs.get("maintenance")
            maintenance_deficit_days = project_state.maintenance_deficit_days
            if maintenance_required is not None:
                if resources.get("maintenance", 0) < maintenance_required:
                    maintenance_deficit_days += 1
                else:
                    maintenance_deficit_days = max(0, maintenance_deficit_days - 1)
            for resource, required in operating_inputs.items():
                resources[resource] = max(
                    0, resources.get(resource, 0) - required * utilization
                )
            operated[name] = ProjectState(
                project=project_state.project,
                stage=project_state.stage,
                blocked_by=project_state.blocked_by,
                operating_output=output,
                binding_constraint=binding,
                maintenance_deficit_days=maintenance_deficit_days,
            )
        return operated

    def _infrastructure_available(self, identifier: str) -> bool:
        return any(
            route.route_id == identifier and route.commissioned
            for route in self._state.routes.values()
        )