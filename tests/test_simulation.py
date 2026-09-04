import datetime
import unittest
from typing import MutableMapping, cast

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

    def test_state_mappings_are_read_only(self) -> None:
        simulation = self.make_simulation()

        with self.assertRaises(TypeError):
            cast(MutableMapping[str, float], simulation.state.resources)["coal"] = 0

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


if __name__ == "__main__":
    unittest.main()