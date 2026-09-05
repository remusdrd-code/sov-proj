import datetime
import unittest

from soviet_industrialization.project import Project, ProjectStage
from soviet_industrialization.reports import historical_milestones
from soviet_industrialization.simulation import Simulation


class ReportTests(unittest.TestCase):
    def make_simulation(self) -> Simulation:
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
            operating_inputs={"fuel": 10, "freight": 5},
        )
        return Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={
                "survey": 1,
                "design": 1,
                "construction_materials": 2,
                "equipment": 1,
                "electricity": 1,
                "labor": 1,
                "logistics": 1,
                "maintenance_support": 1,
                "trial_operation": 1,
                "fuel": 10,
                "freight": 5,
            },
            projects=(project,),
        )

    def test_on_demand_report_exposes_capacity_output_and_constraints(self) -> None:
        simulation = self.make_simulation()
        for _ in range(9):
            simulation.tick()

        report = simulation.request_report()
        sector = report.regions[("Donbas", "industry")]

        self.assertEqual(sector.nameplate_capacity, 100)
        self.assertEqual(sector.commissioned_capacity, 100)
        self.assertEqual(sector.operating_output, 100)
        self.assertEqual(sector.utilization, 1)
        self.assertEqual(sector.bottlenecks, ())
        self.assertEqual(simulation.state.reports[-1], report)

    def test_quarterly_reports_are_recorded_during_play(self) -> None:
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1), resources={}
        )

        for _ in range(182):
            simulation.tick()

        self.assertGreaterEqual(len(simulation.state.reports), 2)
        self.assertEqual(
            [report.date for report in simulation.state.reports[:2]],
            [datetime.date(1928, 4, 1), datetime.date(1928, 7, 1)],
        )

    def test_historical_milestones_include_required_and_later_five_year_dates(self) -> None:
        self.assertEqual(
            historical_milestones(1952),
            (1928, 1932, 1937, 1942, 1947, 1952),
        )

    def test_1932_control_figure_comparison_does_not_score_or_end_play(self) -> None:
        simulation = self.make_simulation()
        comparison = simulation.compare_to_1932_control_figures(
            {"commissioned_capacity": 120}
        )

        self.assertEqual(comparison.milestone_year, 1932)
        self.assertEqual(comparison.actual["commissioned_capacity"], 0)
        self.assertEqual(comparison.control["commissioned_capacity"], 120)
        self.assertEqual(comparison.variance["commissioned_capacity"], -120)
        self.assertFalse(simulation.state.paused)


if __name__ == "__main__":
    unittest.main()
