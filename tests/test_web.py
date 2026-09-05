"""Tests for the soviet_industrialization_web state endpoint."""

import asyncio
import datetime
import unittest

from soviet_industrialization.simulation import Facility, Simulation
from soviet_industrialization_web.state import (
    SimulationStateEndpoint,
    URALS_EAST,
    REGION_SCHEMATIC,
    _sim_state_to_json,
)


class StateEndpointTests(unittest.TestCase):
    def make_sim(self) -> Simulation:
        return Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={"coal": 100, "steel": 50, "electricity": 80},
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

    def test_state_json_contains_date_and_resources(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        self.assertEqual(data["date"], "1928-01-01")
        self.assertIn("coal", data["resources"])
        self.assertIn("steel", data["resources"])
        self.assertIn("facilities", data)
        self.assertIn("projects", data)
        self.assertIn("alerts", data)
        self.assertIn("queue", data)
        self.assertIn("map_regions", data)
        self.assertIn("routes", data)

    def test_state_json_contains_map_regions(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        region_names = {r["name"] for r in data["map_regions"]}
        self.assertIn("Moscow", region_names)
        self.assertIn("Donbas", region_names)
        self.assertIn("Leningrad", region_names)
        self.assertIn("Urals", region_names)
        self.assertIn("Far East", region_names)

    def test_state_json_survey_east_of_urals_false(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        surveyed = {r["name"]: r["surveyed"] for r in data["map_regions"]}
        for name in URALS_EAST:
            self.assertFalse(surveyed[name], f"{name} should not be surveyed initially")

    def test_state_json_west_of_urals_surveyed(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        surveyed = {r["name"]: r["surveyed"] for r in data["map_regions"]}
        self.assertTrue(surveyed["Moscow"])
        self.assertTrue(surveyed["Donbas"])
        self.assertTrue(surveyed["Leningrad"])
        self.assertTrue(surveyed["Urals"])

    def test_state_json_facilities(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        facs = data["facilities"]
        self.assertIn("Moscow steel works", facs)
        self.assertEqual(facs["Moscow steel works"]["daily_output"], 0)
        self.assertFalse(facs["Moscow steel works"]["operating"])

    def test_tick_updates_state(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)

        sim.tick()
        data = endpoint.to_json()
        self.assertEqual(data["date"], "1928-01-02")
        # After one tick, facility should have produced
        self.assertEqual(data["facilities"]["Moscow steel works"]["daily_output"], 1)
        self.assertTrue(data["facilities"]["Moscow steel works"]["operating"])

    def test_region_schematic_positions_in_bounds(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        for region in data["map_regions"]:
            x = region["schematic_x"]
            y = region["schematic_y"]
            self.assertGreaterEqual(x, 0.0, f"{region['name']} x out of bounds")
            self.assertLessEqual(x, 1.0, f"{region['name']} x out of bounds")
            self.assertGreaterEqual(y, 0.0, f"{region['name']} y out of bounds")
            self.assertLessEqual(y, 1.0, f"{region['name']} y out of bounds")

    def test_paused_state_reported(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()
        self.assertFalse(data["paused"])

        sim.pause()
        data = endpoint.to_json()
        self.assertTrue(data["paused"])

    def test_critical_pause_alert(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()
        self.assertFalse(data["critical_pause_latched"])

        sim.pause()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()
        # latched state requires the critical flag; set it directly
        from soviet_industrialization.simulation import SimulationState
        from types import MappingProxyType
        sim._state = SimulationState(
            date=sim._state.date,
            resources=sim._state.resources,
            facilities=sim._state.facilities,
            projects=sim._state.projects,
            routes=sim._state.routes,
            national_map=sim._state.national_map,
            paused=True,
            speed=sim._state.speed,
            automation=sim._state.automation,
            global_automation=sim._state.global_automation,
            manual_orders=sim._state.manual_orders,
            action_queue=sim._state.action_queue,
            suppressed_decisions=sim._state.suppressed_decisions,
            delegated_automation=sim._state.delegated_automation,
            critical_pause_latched=True,
            reports=sim._state.reports,
            technical_knowledge=sim._state.technical_knowledge,
            supply_chains=sim._state.supply_chains,
        )
        data = endpoint.to_json()
        self.assertTrue(data["critical_pause_latched"])
        # Should have a critical alert
        severities = {a["severity"] for a in data["alerts"]}
        self.assertIn("critical", severities)

    def test_map_regions_have_required_fields(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        required = {"name", "detailed", "developable", "cities",
                    "industrial_sites", "schematic_x", "schematic_y", "surveyed"}
        for region in data["map_regions"]:
            self.assertEqual(required, set(region.keys()), f"{region['name']} missing fields")

    def test_urals_east_regions_locked(self) -> None:
        sim = self.make_sim()
        endpoint = SimulationStateEndpoint(sim)
        data = endpoint.to_json()

        surveyed = {r["name"]: r["surveyed"] for r in data["map_regions"]}
        for name in URALS_EAST:
            self.assertFalse(surveyed[name], f"{name} should start locked")
            self.assertFalse(
                any(r["name"] == name and r["developable"] for r in data["map_regions"]),
                f"{name} should not be developable when not surveyed"
            )


class FastAPIAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sim = Simulation(
            start_date=datetime.date(1928, 1, 1),
            resources={"coal": 100, "steel": 50},
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
        from soviet_industrialization_web.app import create_app
        self.app = create_app(self.sim)

    def _async_test(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro())

    def test_state_endpoint_returns_200(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/state.json")
                self.assertEqual(resp.status_code, 200)
        self._async_test(_)

    def test_state_endpoint_returns_valid_json(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/state.json")
                data = resp.json()
                self.assertIn("date", data)
                self.assertIn("resources", data)
        self._async_test(_)

    def test_state_schema_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/state.json/schema")
                self.assertEqual(resp.status_code, 200)
                schema = resp.json()
                self.assertIn("date", schema)
        self._async_test(_)

    def test_pause_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/control/pause")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.json()["paused"])
        self._async_test(_)

    def test_resume_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                await client.post("/api/control/pause")
                resp = await client.post("/api/control/resume")
                self.assertEqual(resp.status_code, 200)
                self.assertFalse(resp.json()["paused"])
        self._async_test(_)

    def test_speed_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/control/speed?speed=2")
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.json()["speed"], 2)
        self._async_test(_)

    def test_speed_invalid(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/control/speed?speed=99")
                self.assertEqual(resp.status_code, 400)
        self._async_test(_)

    def test_tick_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/control/tick")
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.json()["date"], "1928-01-02")
        self._async_test(_)

    def test_dashboard_returns_200(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/dashboard")
                self.assertEqual(resp.status_code, 200)
        self._async_test(_)

    def test_partial_summary(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/partials/summary")
                self.assertEqual(resp.status_code, 200)
                self.assertIn("coal", resp.text)
        self._async_test(_)

    def test_partial_alerts(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/partials/alerts")
                self.assertEqual(resp.status_code, 200)
        self._async_test(_)

    def test_partial_projects(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/partials/projects")
                self.assertEqual(resp.status_code, 200)
        self._async_test(_)

    def test_survey_east_region_returns_message(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/survey?region=Far+East")
                self.assertEqual(resp.status_code, 200)
        self._async_test(_)

    def test_focused_project_not_found(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/partials/focused/project/NonexistentProject")
                self.assertEqual(resp.status_code, 404)
        self._async_test(_)

    def test_focused_alert_not_found(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/partials/focused/alert/nonexistent-alert")
                self.assertEqual(resp.status_code, 404)
        self._async_test(_)

    def test_focused_region_found(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/partials/focused/region/Moscow")
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Moscow", resp.text)
        self._async_test(_)

    def test_automation_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/control/automation/industry",
                    json={"enabled": True},
                )
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.json()["enabled"])
        self._async_test(_)

    def test_automation_unknown_system_rejected(self) -> None:
        from httpx import ASGITransport, AsyncClient
        async def _():
            transport = ASGITransport(app=self.app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/control/automation/nonexistent",
                    json={"enabled": True},
                )
                self.assertEqual(resp.status_code, 400)
        self._async_test(_)
