"""FastAPI + HTMX application for the Soviet industrialization dashboard."""

from __future__ import annotations

import datetime
import json
import threading
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from soviet_industrialization.simulation import Facility, Simulation, SimulationSpeed

from .state import SimulationStateEndpoint, REGION_SCHEMATIC, URALS_EAST

# Absolute path to the static directory (module-level for endpoints)
_STATIC_DIR = Path(__file__).parent / "static"


# ---------------------------------------------------------------------------
# Demo simulation helpers
# ---------------------------------------------------------------------------

_EMPTY_COSTS: Mapping[str, float] = MappingProxyType({})


def _flat_terrain():
    from soviet_industrialization.network import Terrain
    return Terrain(
        terrain_multiplier=1.0,
        crossings=0,
        climate_multiplier=1.0,
        supply_access=1.0,
    )

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(simulation: Simulation) -> FastAPI:
    app = FastAPI(title="Soviet Industrialization Dashboard")
    endpoint = SimulationStateEndpoint(simulation)

    templates = Jinja2Templates(
        directory=str(Path(__file__).parent / "templates"),
    )

    # Mount static files
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Prototype: industry map modes
    @app.get("/prototype/map-modes")
    async def prototype_map_modes(request: Request):
        proto_path = Path(__file__).parents[2] / ".scratch" / "soviet-industrialization-game" / "prototype-industry-map.html"
        if proto_path.exists():
            return HTMLResponse(proto_path.read_text())
        raise HTTPException(404, "Prototype file not found")

    # -------------------------------------------------------------------------
    # JSON state endpoint
    # -------------------------------------------------------------------------

    @app.get("/api/state.json")
    def state_json() -> dict:
        """Small JSON endpoint exposing the full simulation state for the UI."""
        return endpoint.to_json()

    @app.get("/api/state.json/schema")
    def state_schema() -> dict:
        """Return the JSON schema for the state endpoint."""
        return {
            "date": "string (ISO date)",
            "paused": "boolean",
            "speed": "integer (1=NORMAL, 2=FAST, 4=VERY_FAST)",
            "resources": "object (resource name -> amount)",
            "facilities": "object (name -> {daily_output, operating})",
            "projects": "array of {name, region, stage, blocked_by, binding_constraint, priority, sector}",
            "alerts": "array of {id, severity, message, source, project_name, region}",
            "queue": "array of {id, system, target, action, severity, available_actions, recommended_action}",
            "map_regions": "array of {name, detailed, developable, cities, industrial_sites, schematic_x, schematic_y, surveyed}",
            "routes": "array of {id, start, end, infrastructure_type, distance}",
            "technical_knowledge": "object (name -> amount)",
            "supply_chains": "array of string",
            "global_automation": "boolean",
            "automation": "object (system -> boolean)",
            "critical_pause_latched": "boolean",
        }

    # -------------------------------------------------------------------------
    # Dashboard page
    # -------------------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "dashboard.html", {})

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard_page(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "dashboard.html", {})

    # -------------------------------------------------------------------------
    # HTMX partials
    # -------------------------------------------------------------------------

    @app.get("/partials/summary")
    def partial_summary(request: Request) -> HTMLResponse:
        """Top bar: date, speed, pause, resources summary."""
        state = endpoint.to_json()
        return templates.TemplateResponse(request, "partials/summary.html", {"state": state})

    @app.get("/partials/alerts")
    def partial_alerts(request: Request) -> HTMLResponse:
        """Alerts panel including autopause alerts."""
        state = endpoint.to_json()
        return templates.TemplateResponse(request, "partials/alerts.html", {"alerts": state["alerts"]})

    @app.get("/partials/projects")
    def partial_projects(request: Request) -> HTMLResponse:
        """Project queue with stage and blockers."""
        state = endpoint.to_json()
        return templates.TemplateResponse(
            request, "partials/projects.html",
            {"projects": state["projects"], "paused": state["paused"]},
        )

    @app.get("/partials/queue")
    def partial_queue(request: Request) -> HTMLResponse:
        """Decision queue."""
        state = endpoint.to_json()
        return templates.TemplateResponse(request, "partials/queue.html", {"queue": state["queue"]})

    @app.get("/partials/automation")
    def partial_automation(request: Request) -> HTMLResponse:
        """Automation controls."""
        state = endpoint.to_json()
        return templates.TemplateResponse(request, "partials/automation.html", {"state": state})

    # -------------------------------------------------------------------------
    # Map endpoints
    # -------------------------------------------------------------------------

    @app.get("/api/oblasts.json")
    def api_oblasts() -> JSONResponse:
        """Serve the USSR oblast GeoJSON (Russia + Ukraine + Belarus)."""
        geojson_path = _STATIC_DIR / "ussr_oblasts_simplified.geojson"
        with open(geojson_path) as f:
            data = json.load(f)
        return JSONResponse(data)

    @app.get("/partials/map")
    def partial_map(request: Request) -> HTMLResponse:
        """Map with current mode applied."""
        return templates.TemplateResponse(request, "partials/map.html", {})

    @app.post("/api/survey/{region}")
    def survey_region(region: str) -> dict:
        """Unlock a region east of the Urals by progressing its survey project.

        Returns 501 if the simulation does not yet support region surveying.
        """
        if region not in URALS_EAST:
            raise HTTPException(status_code=400, detail="Region does not need survey")
        sim = endpoint.simulation
        if not hasattr(sim, "survey_region"):
            raise HTTPException(
                status_code=501,
                detail="Simulation does not support region surveying yet",
            )
        sim.survey_region(region)
        return {"ok": True, "region": region}

    # -------------------------------------------------------------------------
    # Control actions (POST)
    # -------------------------------------------------------------------------

    @app.post("/api/control/pause")
    def control_pause() -> dict:
        endpoint.simulation.pause()
        return {"ok": True, "paused": True}

    @app.post("/api/control/resume")
    def control_resume() -> dict:
        endpoint.simulation.resume()
        return {"ok": True, "paused": False}

    @app.post("/api/control/speed")
    def control_speed(speed: int) -> dict:
        try:
            sim_speed = SimulationSpeed(speed)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid speed value")
        endpoint.simulation.set_speed(sim_speed)
        return {"ok": True, "speed": speed}

    @app.post("/api/control/tick")
    def control_tick() -> dict:
        state = endpoint.simulation.tick()
        return {"ok": True, "date": state.date.isoformat()}

    @app.post("/api/control/resolve/{decision_id}")
    def control_resolve(decision_id: str, action: Optional[str] = None) -> dict:
        endpoint.simulation.resolve_decision(decision_id, action)
        return {"ok": True}

    @app.post("/api/control/automation/{system}")
    def control_automation(system: str, enabled: bool = True) -> dict:
        """Enable or disable an automation system. System must be a valid AutomationSystem name."""
        from soviet_industrialization.automation import AutomationSystem
        try:
            sys = AutomationSystem(system)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown automation system: {system}")
        endpoint.simulation.set_automation(sys, enabled)
        return {"ok": True, "system": system, "enabled": enabled}

    @app.post("/api/control/global-automation")
    def control_global_automation(enabled: bool) -> dict:
        endpoint.simulation.set_global_automation(enabled)
        return {"ok": True, "global_automation": enabled}

    # -------------------------------------------------------------------------
    # Focus item (click on map element focuses dashboard item)
    # -------------------------------------------------------------------------

    # Registry map: focus_type → (state key, id field name, template name)
    _FOCUS_REGISTRY: dict[str, tuple[str, str, str]] = {
        "project": ("projects", "name", "partials/focused_project.html"),
        "region": ("map_regions", "name", "partials/focused_region.html"),
        "alert": ("alerts", "id", "partials/focused_alert.html"),
        "route": ("routes", "id", "partials/focused_route.html"),
        "facility": ("facilities", "name", "partials/focused_facility.html"),
    }

    @app.get("/partials/focused/{focus_type}/{focus_id}")
    def partial_focused(request: Request, focus_type: str, focus_id: str) -> HTMLResponse:
        """Return a focused view of a specific item (project, region, route, facility, alert)."""
        if focus_type not in _FOCUS_REGISTRY:
            raise HTTPException(status_code=404, detail="Item not found")
        state_key, id_field, template = _FOCUS_REGISTRY[focus_type]
        state = endpoint.to_json()
        items = [item for item in state[state_key] if item[id_field] == focus_id]
        if not items:
            raise HTTPException(status_code=404, detail="Item not found")
        return templates.TemplateResponse(request, template, {focus_type: items[0]})

    return app


# ---------------------------------------------------------------------------
# Default app with a demo simulation
# ---------------------------------------------------------------------------

def make_demo_simulation() -> Simulation:
    """Create a brownfield demo simulation showcasing a 1928 USSR with
    commissioned legacy facilities, active construction projects,
    and connected infrastructure — the player starts with a running
    national production system and a visible project queue.
    """
    from soviet_industrialization.network import (
        InfrastructureType,
        InfrastructureRoute,
        MapNode,
        RoutePlanner,
    )
    from soviet_industrialization.project import Project, ProjectStage

    # -------------------------------------------------------------------------
    # Infrastructure: commissioned legacy rail connections
    # -------------------------------------------------------------------------
    # Schematic node positions for the three detailed regions.
    # These use the same normalized (x, y) space as REGION_SCHEMATIC in state.py.
    donbas_node = MapNode(name="Donbas hub", x=0.62, y=0.52, network_connected=True)
    moscow_node = MapNode(name="Moscow hub", x=0.56, y=0.38, network_connected=True)
    leningrad_node = MapNode(name="Leningrad hub", x=0.52, y=0.28, network_connected=True)

    planner = RoutePlanner(
        nodes=(donbas_node, moscow_node, leningrad_node),
        snap_distance=0.05,
    )

    # Donbas → Moscow: commissioned legacy rail (existing at game start)
    donbas_moscow_route = planner.draw(
        InfrastructureType.RAIL,
        start=(0.62, 0.52),
        end=(0.56, 0.38),
        waypoints=((0.60, 0.46),),
        terrain=_flat_terrain(),
        commissioned=True,
    )

    # Moscow → Leningrad: commissioned legacy rail
    moscow_leningrad_route = planner.draw(
        InfrastructureType.RAIL,
        start=(0.56, 0.38),
        end=(0.52, 0.28),
        waypoints=((0.54, 0.34),),
        terrain=_flat_terrain(),
        commissioned=True,
    )

    # -------------------------------------------------------------------------
    # Commissioned legacy facilities (running at game start)
    # -------------------------------------------------------------------------
    commissioned_facilities = (
        # Donbas: large coal mine producing 8 coal/day, consuming 2 labor/day
        Facility(
            name="Yuzovka deep mine",
            input_resource="labor",
            input_per_day=2,
            output_resource="coal",
            output_per_day=8,
        ),
        # Moscow: steel works converting 4 coal + 2 ore → 2 steel
        # (Modelled as a steel output with coal as proxy for ore+coal bundle)
        Facility(
            name="Moscow steel works",
            input_resource="coal",
            input_per_day=4,
            output_resource="steel",
            output_per_day=2,
        ),
        # Leningrad: machinery plant consuming 3 steel → 1 machinery
        Facility(
            name="Leningrad machine works",
            input_resource="steel",
            input_per_day=3,
            output_resource="machinery",
            output_per_day=1,
        ),
    )

    # -------------------------------------------------------------------------
    # Active construction projects (in various stages)
    # -------------------------------------------------------------------------
    # Project 1: New coal mine in Donbas — DESIGN stage, well-supplied
    _STAGE_COSTS_COAL_MINE = {
        ProjectStage.SURVEY: {"labor": 3},
        ProjectStage.DESIGN: {"design_work": 5, "survey_kits": 2},
        ProjectStage.CIVIL_WORKS: {"steel": 6, "labor": 8},
        ProjectStage.EQUIPMENT: {"machinery": 4},
        ProjectStage.ELECTRICITY: {"steel": 2},
        ProjectStage.LABOR: {"labor": 5},
        ProjectStage.FREIGHT_ACCESS: {"coal": 2},
        ProjectStage.MAINTENANCE: {"maintenance": 1},
        ProjectStage.TRIAL_OPERATION: {"coal": 4},
    }
    coal_mine_project = Project(
        name="Makeyevka coal mine",
        region="Donbas",
        nameplate_capacity=12,
        stage_costs=_STAGE_COSTS_COAL_MINE,
        operating_inputs={"labor": 3, "maintenance": 1},
        sector="industry",
        priority=10,
    )

    # Project 2: Second Moscow steel plant — CIVIL_WORKS, blocked on steel
    moscow_steel_project = Project(
        name="Tula steel complex",
        region="Moscow",
        nameplate_capacity=5,
        stage_costs={
            ProjectStage.SURVEY: {"labor": 2},
            ProjectStage.DESIGN: {"design_work": 4},
            ProjectStage.CIVIL_WORKS: {"steel": 10, "labor": 12},
            ProjectStage.EQUIPMENT: {"machinery": 6},
            ProjectStage.ELECTRICITY: {"steel": 3},
            ProjectStage.LABOR: {"labor": 8},
            ProjectStage.FREIGHT_ACCESS: {"coal": 4},
            ProjectStage.MAINTENANCE: {"maintenance": 2},
            ProjectStage.TRIAL_OPERATION: {"coal": 6},
        },
        operating_inputs={"coal": 6, "electricity": 3, "maintenance": 2},
        sector="industry",
        priority=8,
    )

    # Project 3: Leningrad expansion — EQUIPMENT stage, waiting on machinery
    leningrad_expansion = Project(
        name="Leningrad shipyard extension",
        region="Leningrad",
        nameplate_capacity=3,
        stage_costs={
            ProjectStage.SURVEY: {"labor": 2},
            ProjectStage.DESIGN: {"design_work": 3},
            ProjectStage.CIVIL_WORKS: {"steel": 8, "labor": 10},
            ProjectStage.EQUIPMENT: {"machinery": 8},
            ProjectStage.ELECTRICITY: {"steel": 2},
            ProjectStage.LABOR: {"labor": 6},
            ProjectStage.FREIGHT_ACCESS: {"coal": 3},
            ProjectStage.MAINTENANCE: {"maintenance": 1},
            ProjectStage.TRIAL_OPERATION: {"steel": 4},
        },
        operating_inputs={"steel": 5, "electricity": 2, "maintenance": 1},
        sector="industry",
        priority=6,
    )

    # -------------------------------------------------------------------------
    # Build simulation with all pieces
    # -------------------------------------------------------------------------
    sim = Simulation(
        start_date=datetime.date(1928, 1, 1),
        resources={
            "coal": 80,
            "steel": 30,
            "machinery": 5,
            "electricity": 60,
            "labor": 50,
            "maintenance": 10,
            "design_work": 8,
            "survey_kits": 3,
        },
        facilities=commissioned_facilities,
        projects=(coal_mine_project, moscow_steel_project, leningrad_expansion),
        routes=(donbas_moscow_route, moscow_leningrad_route),
        supply_chains=("donbas_coal_flow", "moscow_steel_flow"),
    )

    # Advance coal mine to DESIGN so it's past survey
    ps = sim.state.projects["Makeyevka coal mine"]
    sim._state = replace(
        sim._state,
        projects=MappingProxyType({
            **dict(sim._state.projects),
            "Makeyevka coal mine": replace(ps, stage=ProjectStage.DESIGN),
        }),
    )

    # Advance Tula steel to CIVIL_WORKS
    ps2 = sim.state.projects["Tula steel complex"]
    sim._state = replace(
        sim._state,
        projects=MappingProxyType({
            **dict(sim._state.projects),
            "Tula steel complex": replace(ps2, stage=ProjectStage.CIVIL_WORKS),
        }),
    )

    # Advance Leningrad extension to EQUIPMENT
    ps3 = sim.state.projects["Leningrad shipyard extension"]
    sim._state = replace(
        sim._state,
        projects=MappingProxyType({
            **dict(sim._state.projects),
            "Leningrad shipyard extension": replace(ps3, stage=ProjectStage.EQUIPMENT),
        }),
    )

    return sim


# Lazy-init demo app
_demo_app: FastAPI | None = None
_demo_lock = threading.Lock()


def get_demo_app() -> FastAPI:
    global _demo_app
    with _demo_lock:
        if _demo_app is None:
            sim = make_demo_simulation()
            _demo_app = create_app(sim)
        return _demo_app
