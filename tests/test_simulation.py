import datetime
import unittest
from typing import MutableMapping, cast

from soviet_industrialization.automation import AutomationSystem, DecisionSeverity
from soviet_industrialization.network import (
    InfrastructureRoute,
    InfrastructureType,
    MapNode,
)
from soviet_industrialization.project import Project, ProjectStage
from soviet_industrialization.simulation import Facility, Simulation, SimulationSpeed


class SimulationTests(unittest.TestCase):
    def make_simulation(self) -> Simulation:
        return Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={"coal": 4, "steel": 0},
            facilities=(
                Facility(
                    name="Moscow steel works",
                    input_resource="coal",
                    input_per_day=2,
                    output_resource="steel",
                    output_per_day=1,
                ),
            ),
        )

    def test_running_tick_advances_one_day_and_produces_output(self) -> None:
        simulation = self.make_simulation()

        state = simulation.tick()

        self.assertEqual(state.date, datetime.date(1928, 1, 2))
        self.assertEqual(state.resources["coal"], 2)
        self.assertEqual(state.resources["steel"], 1)
        self.assertEqual(state.facilities["Moscow steel works"].daily_output, 1)

    def test_pause_holds_state_without_consumption_or_penalty(self) -> None:
        simulation = self.make_simulation()
        before_pause = simulation.state

        simulation.pause()
        paused_state = simulation.tick()

        self.assertTrue(paused_state.paused)
        self.assertEqual(paused_state.date, before_pause.date)
        self.assertEqual(paused_state.resources, before_pause.resources)
        self.assertEqual(paused_state.facilities, before_pause.facilities)

        simulation.resume()
        resumed_state = simulation.tick()

        self.assertEqual(resumed_state.date, datetime.date(1928, 1, 2))
        self.assertEqual(resumed_state.resources["coal"], 2)
        self.assertEqual(resumed_state.resources["steel"], 1)

    def test_speed_can_be_selected_without_changing_daily_resolution(self) -> None:
        simulation = self.make_simulation()

        simulation.set_speed(SimulationSpeed.FAST)
        state = simulation.tick()

        self.assertEqual(state.speed, SimulationSpeed.FAST)
        self.assertEqual(state.date, datetime.date(1928, 1, 2))
        self.assertEqual(state.resources["steel"], 1)

    def test_daily_state_exposes_full_map_and_detailed_launch_regions(self) -> None:
        simulation = self.make_simulation()

        initial_map = simulation.state.national_map
        state_after_tick = simulation.tick()

        self.assertEqual(
            {region.name for region in initial_map.regions},
            {
                "Belarus",
                "Central Asia",
                "Caucasus",
                "Donbas",
                "Far East",
                "Kazakhstan",
                "Leningrad",
                "Moscow",
                "Siberia",
                "Urals",
                "Volga",
            },
        )
        for region_name in ("Donbas", "Moscow", "Leningrad"):
            region = initial_map.region(region_name)
            self.assertTrue(region.detailed)
            self.assertTrue(region.cities)
            self.assertTrue(region.industrial_sites)
            self.assertTrue(region.legacy_networks)
        self.assertTrue(initial_map.region("Urals").developable)
        self.assertTrue(all(region.cities for region in initial_map.regions))
        self.assertEqual(state_after_tick.national_map, initial_map)

    def test_later_sector_waits_for_explicit_enablers(self) -> None:
        project = Project(
            name="Urals chemical works",
            region="Urals",
            sector="chemicals",
            nameplate_capacity=10,
            stage_costs=self.lifecycle_costs("equipment"),
            required_knowledge=("synthetic chemistry",),
            required_infrastructure=("Urals power grid",),
            required_supply_chains=("chemical feedstock",),
        )
        simulation = Simulation(
            start_date=datetime.date(1941, 1, 1),
            resources=self.lifecycle_resources("equipment"),
            projects=(project,),
        )

        simulation.tick()

        self.assertEqual(
            simulation.state.projects[project.name].blocked_by,
            ("synthetic chemistry", "Urals power grid", "chemical feedstock"),
        )
        simulation.add_technical_knowledge("synthetic chemistry")
        simulation.add_supply_chain("chemical feedstock")
        simulation.add_route(self.make_route("Urals power grid"))
        simulation.set_global_automation(False)
        simulation.set_global_automation(True)
        simulation.tick()

        self.assertEqual(
            simulation.state.projects[project.name].stage,
            ProjectStage.DESIGN,
        )
        self.assertEqual(
            simulation.request_report().regions[("Urals", "chemicals")].sector,
            "chemicals",
        )

    def test_late_project_can_be_added_and_play_continues_after_1940(self) -> None:
        simulation = Simulation(
            start_date=datetime.date(1940, 12, 31),
            resources=self.lifecycle_resources("equipment"),
        )
        simulation.tick()
        self.assertEqual(simulation.state.date, datetime.date(1941, 1, 1))

        project = Project(
            name="Urals machine works",
            region="Urals",
            nameplate_capacity=10,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        simulation.add_project(project)
        state = simulation.tick()

        self.assertEqual(state.date, datetime.date(1941, 1, 2))
        self.assertIn(project.name, state.projects)
        self.assertEqual(state.projects[project.name].stage, ProjectStage.DESIGN)

    @staticmethod
    def lifecycle_resources(equipment_resource: str) -> dict[str, float]:
        return {
            "survey": 1,
            "design": 1,
            "construction_materials": 2,
            equipment_resource: 1,
            "electricity": 1,
            "labor": 1,
            "freight": 1,
            "maintenance": 1,
            "trial_operation": 1,
        }

    @staticmethod
    def make_route(identifier: str) -> InfrastructureRoute:
        return InfrastructureRoute(
            identifier=identifier,
            infrastructure_type=InfrastructureType.POWER,
            start=MapNode("Urals", 0, 0, network_connected=True),
            end=MapNode(identifier, 1, 0),
            waypoints=(),
            snapped=True,
            commissioned=True,
            connected_to_legacy=True,
            distance=1,
            construction_cost=1,
            construction_days=1,
            reliability=1,
            isolated_premium=0,
        )

    def test_state_mappings_are_read_only(self) -> None:
        simulation = self.make_simulation()

        with self.assertRaises(TypeError):
            cast(MutableMapping[str, float], simulation.state.resources)["coal"] = 0

    def test_industry_automation_off_queues_idle_facility_work(self) -> None:
        simulation = self.make_simulation()
        simulation.set_automation(AutomationSystem.INDUSTRY, False)

        state = simulation.tick()

        self.assertEqual(state.resources["coal"], 4)
        self.assertEqual(state.facilities["Moscow steel works"].daily_output, 0)
        self.assertEqual(state.action_queue[0].system, AutomationSystem.INDUSTRY)
        self.assertEqual(state.action_queue[0].severity, DecisionSeverity.WARNING)
        self.assertTrue(state.paused)

    def test_resource_shortage_is_a_notice_without_autopause(self) -> None:
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={"coal": 0},
            facilities=(
                Facility(
                    name="Moscow steel works",
                    input_resource="coal",
                    input_per_day=2,
                    output_resource="steel",
                    output_per_day=1,
                ),
            ),
        )

        state = simulation.tick()

        self.assertEqual(state.date, datetime.date(1928, 1, 2))
        self.assertFalse(state.paused)
        self.assertEqual(state.action_queue[0].severity, DecisionSeverity.NOTICE)

    def test_decision_can_be_dismissed_or_delegated(self) -> None:
        simulation = self.make_simulation()
        simulation.set_automation(AutomationSystem.INDUSTRY, False)
        decision_id = simulation.tick().action_queue[0].order_id

        simulation.dismiss_decision(decision_id)
        self.assertFalse(simulation.state.action_queue)

        delegated_simulation = self.make_simulation()
        delegated_simulation.set_automation(AutomationSystem.INDUSTRY, False)
        decision_id = delegated_simulation.tick().action_queue[0].order_id
        delegated_simulation.set_global_automation(False)
        delegated_simulation.resolve_decision(decision_id, "delegate")
        self.assertTrue(
            delegated_simulation.state.automation[AutomationSystem.INDUSTRY]
        )
        self.assertFalse(delegated_simulation.state.action_queue)

    def test_manual_order_overrides_switch_until_revoked(self) -> None:
        simulation = self.make_simulation()
        simulation.set_automation(AutomationSystem.INDUSTRY, False)
        order = simulation.issue_manual_order(
            AutomationSystem.INDUSTRY, "Moscow steel works", "operate"
        )

        first = simulation.tick()
        second = simulation.tick()
        self.assertEqual(first.resources["steel"], 1)
        self.assertEqual(second.resources["steel"], 2)

        simulation.revoke_manual_order(order.order_id)
        stopped = simulation.tick()
        self.assertEqual(stopped.resources["steel"], 2)
        self.assertTrue(stopped.action_queue)

    def test_global_automation_switch_overrides_individual_switches(self) -> None:
        simulation = self.make_simulation()
        simulation.set_global_automation(False)

        state = simulation.tick()

        self.assertEqual(state.resources["coal"], 4)
        self.assertEqual(len(state.action_queue), 1)

    def test_all_automation_systems_have_independent_switches(self) -> None:
        simulation = self.make_simulation()

        self.assertEqual(set(simulation.state.automation), set(AutomationSystem))
        simulation.set_automation(AutomationSystem.IMPORTS, False)

        self.assertFalse(simulation.state.automation[AutomationSystem.IMPORTS])
        self.assertTrue(simulation.state.automation[AutomationSystem.INDUSTRY])

    def test_project_automation_off_queues_work_and_manual_order_resumes_it(self) -> None:
        project = Project(
            name="Moscow machine works",
            region="Moscow",
            nameplate_capacity=10,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={"survey": 1, "design": 1, "construction_materials": 2},
            projects=(project,),
        )
        simulation.set_automation(AutomationSystem.BUILDING, False)

        idle = simulation.tick()

        self.assertEqual(idle.projects[project.name].stage, ProjectStage.SURVEY)
        self.assertEqual(idle.action_queue[0].target, project.name)
        order = simulation.issue_manual_order(
            AutomationSystem.BUILDING, project.name, "advance"
        )
        resumed = simulation.tick()

        self.assertEqual(resumed.projects[project.name].stage, ProjectStage.DESIGN)
        self.assertIn(order.order_id, resumed.manual_orders)

    def test_project_progresses_through_gates_to_commissioning(self) -> None:
        project = Project(
            name="Moscow machine works",
            region="Moscow",
            nameplate_capacity=10,
            stage_costs={
                ProjectStage.SURVEY: {"survey": 1},
                ProjectStage.DESIGN: {"design": 1},
                ProjectStage.CIVIL_WORKS: {"construction_materials": 2},
                ProjectStage.EQUIPMENT: {"equipment": 1},
                ProjectStage.ELECTRICITY: {"electricity": 1},
                ProjectStage.LABOR: {"labor": 1},
                ProjectStage.FREIGHT_ACCESS: {"freight": 1},
                ProjectStage.MAINTENANCE: {"maintenance": 1},
                ProjectStage.TRIAL_OPERATION: {"trial_operation": 1},
            },
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 1,
                "design": 1,
                "construction_materials": 2,
                "equipment": 1,
                "electricity": 1,
                "labor": 1,
                "freight": 1,
                "maintenance": 1,
                "trial_operation": 1,
            },
            projects=(project,),
        )

        for _ in range(len(project.stage_costs)):
            simulation.tick()

        state = simulation.state.projects[project.name]
        self.assertEqual(state.stage, ProjectStage.COMMISSIONED)
        self.assertEqual(state.planned_capacity, 10)
        self.assertEqual(state.built_capacity, 10)
        self.assertTrue(state.physically_complete)
        self.assertEqual(state.commissioned_capacity, 10)
        self.assertEqual(state.operating_output, 0)
        self.assertEqual(state.utilization, 0)

    def test_missing_prerequisite_blocks_project_and_reports_blocker(self) -> None:
        project = Project(
            name="Donbas steel works",
            region="Donbas",
            nameplate_capacity=8,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 1,
                "design": 1,
                "construction_materials": 2,
            },
            projects=(project,),
        )

        for _ in range(3):
            simulation.tick()
        state = simulation.tick().projects[project.name]

        self.assertEqual(state.stage, ProjectStage.EQUIPMENT)
        self.assertEqual(state.blocked_by, ("equipment",))
        self.assertFalse(state.physically_complete)
        self.assertEqual(state.commissioned_capacity, 0)
        self.assertEqual(state.operating_output, 0)

        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 1,
                "design": 1,
                "construction_materials": 2,
                "equipment": 1,
            },
            projects=(project,),
        )
        for _ in range(4):
            simulation.tick()

        built_state = simulation.state.projects[project.name]
        self.assertEqual(built_state.stage, ProjectStage.ELECTRICITY)
        self.assertTrue(built_state.physically_complete)
        self.assertEqual(built_state.built_capacity, 8)
        self.assertEqual(built_state.commissioned_capacity, 0)

    def test_higher_priority_project_wins_scarce_stage_input(self) -> None:
        high_priority = Project(
            name="Priority works",
            region="Moscow",
            priority=10,
            nameplate_capacity=5,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        low_priority = Project(
            name="Deferred works",
            region="Moscow",
            priority=1,
            nameplate_capacity=5,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 2,
                "design": 2,
                "construction_materials": 4,
                "equipment": 1,
                "electricity": 2,
                "labor": 2,
                "freight": 2,
                "maintenance": 2,
                "trial_operation": 2,
            },
            projects=(low_priority, high_priority),
        )

        for _ in range(3):
            simulation.tick()
        state = simulation.tick()

        self.assertEqual(state.projects[high_priority.name].stage, ProjectStage.ELECTRICITY)
        self.assertEqual(state.projects[low_priority.name].blocked_by, ("equipment",))

    def test_freight_and_maintenance_gates_remain_independently_visible(self) -> None:
        freight_blocked = Project(
            name="Freight-blocked works",
            region="Moscow",
            nameplate_capacity=5,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 1,
                "design": 1,
                "construction_materials": 2,
                "equipment": 1,
                "electricity": 1,
                "labor": 1,
            },
            projects=(freight_blocked,),
        )
        for _ in range(7):
            simulation.tick()

        freight_state = simulation.state.projects[freight_blocked.name]
        self.assertEqual(freight_state.stage, ProjectStage.FREIGHT_ACCESS)
        self.assertEqual(freight_state.blocked_by, ("freight",))
        self.assertEqual(freight_state.built_capacity, 5)
        self.assertEqual(freight_state.commissioned_capacity, 0)

        maintenance_blocked = Project(
            name="Maintenance-blocked works",
            region="Moscow",
            nameplate_capacity=5,
            stage_costs=self.lifecycle_costs("equipment"),
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 1,
                "design": 1,
                "construction_materials": 2,
                "equipment": 1,
                "electricity": 1,
                "labor": 1,
                "freight": 1,
            },
            projects=(maintenance_blocked,),
        )
        for _ in range(8):
            simulation.tick()

        maintenance_state = simulation.state.projects[maintenance_blocked.name]
        self.assertEqual(maintenance_state.stage, ProjectStage.MAINTENANCE)
        self.assertEqual(maintenance_state.blocked_by, ("maintenance",))
        self.assertEqual(maintenance_state.built_capacity, 5)
        self.assertEqual(maintenance_state.commissioned_capacity, 0)

    @staticmethod
    def lifecycle_costs(resource: str) -> dict[ProjectStage, dict[str, float]]:
        return {
            ProjectStage.SURVEY: {"survey": 1},
            ProjectStage.DESIGN: {"design": 1},
            ProjectStage.CIVIL_WORKS: {"construction_materials": 2},
            ProjectStage.EQUIPMENT: {resource: 1},
            ProjectStage.ELECTRICITY: {"electricity": 1},
            ProjectStage.LABOR: {"labor": 1},
            ProjectStage.FREIGHT_ACCESS: {"freight": 1},
            ProjectStage.MAINTENANCE: {"maintenance": 1},
            ProjectStage.TRIAL_OPERATION: {"trial_operation": 1},
        }


class FractionalOperationTests(unittest.TestCase):
    """Issue 05: commissioned facilities operate at fractional utilization."""

    def make_commissioned_simulation(self, resources: dict[str, float]) -> Simulation:
        project = Project(
            name="Donbas coke works",
            region="Donbas",
            nameplate_capacity=100,
            stage_costs={
                ProjectStage.SURVEY: {"survey": 1},
                ProjectStage.DESIGN: {"design": 1},
                ProjectStage.CIVIL_WORKS: {"construction_materials": 2},
                ProjectStage.EQUIPMENT: {"equipment": 1},
                ProjectStage.ELECTRICITY: {"electricity": 1},
                ProjectStage.LABOR: {"labor": 1},
                ProjectStage.FREIGHT_ACCESS: {"logistics": 1},
                ProjectStage.MAINTENANCE: {"maintenance_support": 1},
                ProjectStage.TRIAL_OPERATION: {"trial_operation": 1},
            },
            operating_inputs={
                "fuel": 10,
                "freight": 5,
                "materials": 5,
                "maintenance": 2,
                "services": 1,
                "power": 4,
                "labor": 3,
            },
        )
        return Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources=resources,
            projects=(project,),
        )

    def commission(self, simulation: Simulation) -> None:
        for _ in range(len(ProjectStage) - 1):
            simulation.tick()

    @staticmethod
    def operating_resources(
        fuel: float,
        freight: float = 5,
        logistics: float = 1,
        maintenance_support: float = 1,
    ) -> dict[str, float]:
        return {
            "survey": 1,
            "design": 1,
            "construction_materials": 2,
            "equipment": 1,
            "electricity": 1,
            "labor": 1,
            "logistics": logistics,
            "maintenance_support": maintenance_support,
            "trial_operation": 1,
            "fuel": fuel,
            "freight": freight,
            "materials": 5,
            "maintenance": 2,
            "services": 1,
            "power": 4,
            "labor": 3,
        }

    def test_commissioned_facility_operates_fractionally_when_fuel_deficient(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(3.4))
        self.commission(simulation)

        state = simulation.state.projects["Donbas coke works"]

        self.assertEqual(state.stage, ProjectStage.COMMISSIONED)
        self.assertEqual(state.commissioned_capacity, 100)
        self.assertAlmostEqual(state.operating_output, 34)
        self.assertAlmostEqual(state.utilization, 0.34)
        self.assertEqual(state.binding_constraint, "fuel")

    def test_binding_constraint_recovers_when_corrected(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(3.4))
        self.commission(simulation)
        self.assertAlmostEqual(
            simulation.state.projects["Donbas coke works"].utilization, 0.34
        )

        simulation.add_resources(
            {
                "fuel": 10.0,
                "freight": 2.7,
                "materials": 1.7,
                "maintenance": 1.68,
                "services": 0.34,
                "power": 1.36,
                "labor": 2.02,
            }
        )
        simulation.tick()

        state = simulation.state.projects["Donbas coke works"]
        self.assertAlmostEqual(state.operating_output, 100)
        self.assertAlmostEqual(state.utilization, 1.0)
        self.assertIsNone(state.binding_constraint)

    def test_freight_deficiency_is_identified_as_binding_constraint(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(10, 1))
        self.commission(simulation)

        state = simulation.state.projects["Donbas coke works"]

        self.assertEqual(state.binding_constraint, "freight")
        self.assertAlmostEqual(state.utilization, 0.2)

    def test_nameplate_commissioned_output_and_utilization_remain_distinct(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(5))
        self.commission(simulation)

        state = simulation.state.projects["Donbas coke works"]

        self.assertEqual(state.planned_capacity, 100)
        self.assertEqual(state.nameplate_capacity, 100)
        self.assertEqual(state.commissioned_capacity, 100)
        self.assertAlmostEqual(state.operating_output, 50)
        self.assertAlmostEqual(state.utilization, 0.5)
        self.assertEqual(state.binding_constraint, "fuel")

    def test_prolonged_maintenance_shortage_degrades_capacity_and_recovers(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(10))
        self.commission(simulation)
        simulation.add_resources({"maintenance": -2})

        for _ in range(5):
            simulation.tick()
            simulation.add_resources(
                {
                    "fuel": 10,
                    "freight": 5,
                    "materials": 5,
                    "services": 1,
                    "power": 4,
                    "labor": 3,
                }
            )

        degraded = simulation.state.projects["Donbas coke works"]
        self.assertEqual(degraded.stage, ProjectStage.COMMISSIONED)
        self.assertEqual(degraded.maintenance_deficit_days, 5)
        self.assertEqual(degraded.commissioned_capacity, 80)
        self.assertEqual(degraded.operating_output, 0)
        report = simulation.request_report()
        self.assertIn(
            "project Donbas coke works has insufficient maintenance for 5 days",
            report.disorganization,
        )

        simulation.add_resources(
            {
                "maintenance": 10,
                "fuel": 10,
                "freight": 5,
                "materials": 5,
                "services": 1,
                "power": 4,
                "labor": 3,
            }
        )
        simulation.tick()

        recovered = simulation.state.projects["Donbas coke works"]
        self.assertEqual(recovered.maintenance_deficit_days, 4)
        self.assertEqual(recovered.commissioned_capacity, 90)

    def test_critical_maintenance_risk_pauses_until_explicit_resume(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(10))
        self.commission(simulation)
        simulation.add_resources({"maintenance": -2})

        for _ in range(6):
            simulation.tick()
            simulation.add_resources(
                {
                    "fuel": 10,
                    "freight": 5,
                    "materials": 5,
                    "services": 1,
                    "power": 4,
                    "labor": 3,
                }
            )

        decision = next(
            item
            for item in simulation.state.action_queue
            if item.severity == DecisionSeverity.CRITICAL
        )
        paused_date = simulation.state.date
        self.assertTrue(simulation.state.paused)
        self.assertEqual(decision.affected_projects, ("Donbas coke works",))
        self.assertIn("commissioned capacity degradation", decision.cost_of_waiting)

        simulation.resolve_decision(decision.order_id, "supply_maintenance")
        self.assertTrue(simulation.state.paused)
        self.assertEqual(simulation.state.date, paused_date)
        self.assertEqual(
            simulation.state.manual_orders[decision.order_id].action,
            "supply_maintenance",
        )
        simulation.issue_manual_order(
            AutomationSystem.MAINTENANCE,
            "Donbas coke works",
            "supply_maintenance",
        )
        self.assertTrue(simulation.state.paused)

        simulation.add_resources({"maintenance": 10})
        simulation.resume()
        self.assertGreater(simulation.tick().date, paused_date)

    def test_uncommissioned_project_has_no_operating_output(self) -> None:
        simulation = self.make_commissioned_simulation(self.operating_resources(10))

        state = simulation.tick().projects["Donbas coke works"]

        self.assertNotEqual(state.stage, ProjectStage.COMMISSIONED)
        self.assertEqual(state.operating_output, 0)
        self.assertEqual(state.utilization, 0)
        self.assertIsNone(state.binding_constraint)


if __name__ == "__main__":
    unittest.main()