import datetime
import unittest
from typing import MutableMapping, cast

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


if __name__ == "__main__":
    unittest.main()