import datetime
import unittest

from soviet_industrialization.network import (
    InfrastructureType,
    MapNode,
    RoutePlanner,
    Terrain,
)
from soviet_industrialization.simulation import Simulation


class NetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = RoutePlanner(
            nodes=(
                MapNode("Moscow", 0, 0, network_connected=True),
                MapNode("Moscow steel works", 3, 4),
                MapNode("Urals site", 13, 4),
            )
        )

    def test_route_snaps_to_known_nodes_and_preserves_waypoints(self) -> None:
        route = self.planner.draw(
            InfrastructureType.RAIL,
            start=(0.2, 0.1),
            end=(3.1, 3.9),
            waypoints=((1, 1), (2, 3)),
        )

        self.assertEqual(route.start.name, "Moscow")
        self.assertEqual(route.end.name, "Moscow steel works")
        self.assertEqual(route.waypoints, ((1, 1), (2, 3)))
        self.assertTrue(route.snapped)
        self.assertGreater(route.distance, 0)

    def test_terrain_and_connection_change_cost_and_reliability(self) -> None:
        connected = self.planner.draw(
            InfrastructureType.POWER,
            start=(0, 0),
            end=(3, 4),
            terrain=Terrain(terrain_multiplier=1, crossings=0, climate_multiplier=1, supply_access=1),
            commissioned=True,
        )
        isolated = self.planner.draw(
            InfrastructureType.POWER,
            start=(10, 0),
            end=(13, 4),
            terrain=Terrain(terrain_multiplier=2, crossings=1, climate_multiplier=1.5, supply_access=0.5),
        )

        self.assertTrue(connected.connected_to_legacy)
        self.assertFalse(isolated.connected_to_legacy)
        self.assertLess(connected.construction_cost, isolated.construction_cost)
        self.assertGreater(connected.reliability, isolated.reliability)
        self.assertLess(connected.construction_days, isolated.construction_days)
        self.assertEqual(connected.start.name, "Moscow")

    def test_unfinished_route_does_not_provide_legacy_connection(self) -> None:
        route = self.planner.draw(
            InfrastructureType.RAIL,
            start=(3, 4),
            end=(13, 4),
            commissioned=False,
        )

        self.assertFalse(route.connected_to_legacy)
        self.assertGreater(route.isolated_premium, 0)

    def test_commissioned_route_extends_network_for_later_routes(self) -> None:
        first_route = self.planner.draw(
            InfrastructureType.RAIL,
            start=(0, 0),
            end=(13, 4),
            commissioned=False,
        )
        self.planner.commission(first_route)

        later_route = self.planner.draw(
            InfrastructureType.ROAD,
            start=(13, 4),
            end=(3, 4),
        )

        self.assertTrue(later_route.connected_to_legacy)

    def test_parallel_routes_have_distinct_identity(self) -> None:
        rail = self.planner.draw(InfrastructureType.RAIL, start=(0, 0), end=(3, 4))
        second_rail = self.planner.draw(InfrastructureType.RAIL, start=(0, 0), end=(3, 4))
        power = self.planner.draw(InfrastructureType.POWER, start=(0, 0), end=(3, 4))
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={},
            routes=(rail, second_rail, power),
        )

        self.assertEqual(len(simulation.state.routes), 3)

    def test_commissioned_unsnapped_site_becomes_a_network_node(self) -> None:
        route = self.planner.draw(
            InfrastructureType.RAIL,
            start=(20, 20),
            end=(25, 20),
            commissioned=False,
        )
        self.planner.commission(route)

        later_route = self.planner.draw(
            InfrastructureType.POWER,
            start=(20, 20),
            end=(3, 4),
        )

        self.assertTrue(later_route.connected_to_legacy)

    def test_commissioned_draw_registers_endpoints_for_later_routes(self) -> None:
        self.planner.draw(
            InfrastructureType.RAIL,
            start=(20, 20),
            end=(25, 20),
            commissioned=True,
        )

        later_route = self.planner.draw(
            InfrastructureType.POWER,
            start=(20, 20),
            end=(3, 4),
        )

        self.assertTrue(later_route.connected_to_legacy)

    def test_routes_from_separate_planners_can_share_simulation(self) -> None:
        first = RoutePlanner().draw(InfrastructureType.RAIL, (0, 0), (3, 4))
        second = RoutePlanner().draw(InfrastructureType.RAIL, (0, 0), (3, 4))
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={},
            routes=(first, second),
        )

        self.assertEqual(len(simulation.state.routes), 2)

    def test_daily_simulation_preserves_route_inspection_state(self) -> None:
        route = self.planner.draw(
            InfrastructureType.ROAD,
            start=(0, 0),
            end=(3, 4),
        )
        simulation = Simulation(
            start_date=datetime.date(1928, 1, 1), resources={}, routes=(route,)
        )

        state = simulation.tick()

        self.assertEqual(state.routes[route.route_id], route)


if __name__ == "__main__":
    unittest.main()