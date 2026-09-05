"""FastAPI + HTMX application for the Soviet industrialization dashboard."""

from __future__ import annotations

import datetime
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from soviet_industrialization.simulation import Facility, Simulation, SimulationSpeed

from .state import SimulationStateEndpoint, REGION_SCHEMATIC, URALS_EAST

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
    """Create a minimal demo simulation for the web UI."""
    return Simulation(
        start_date=datetime.date(1928, 1, 1),
        resources={"coal": 100, "steel": 50, "electricity": 80, "labor": 60},
        facilities=(
            Facility(
                name="Moscow steel works",
                input_resource="coal",
                input_per_day=2,
                output_resource="steel",
                output_per_day=1,
            ),
            Facility(
                name="Donbas coal mine",
                input_resource="labor",
                input_per_day=1,
                output_resource="coal",
                output_per_day=3,
            ),
        ),
    )


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
