"""JSON state endpoint for the visual dashboard."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Mapping

from soviet_industrialization.simulation import Simulation, SimulationState


@dataclass
class DashboardAlert:
    id: str
    severity: str  # "critical" | "warning" | "info"
    message: str
    source: str  # e.g. "project:<name>", "resource:<name>", "route:<id>"
    project_name: str | None = None
    region: str | None = None


@dataclass
class ProjectQueueItem:
    name: str
    region: str
    stage: str
    blocked_by: tuple[str, ...]
    binding_constraint: str | None
    priority: int
    sector: str


@dataclass
class MapRegionSummary:
    name: str
    detailed: bool
    developable: bool
    cities: tuple[str, ...]
    industrial_sites: tuple[str, ...]
    lat: float  # real centroid lat from oblast data
    lon: float  # real centroid lon from oblast data
    schematic_x: float  # normalized 0-1 for visualization
    schematic_y: float
    surveyed: bool = True  # east of Urals starts False


def _get_region_latlon(region_name: str) -> tuple[float, float]:
    """Return (lat, lon) for a region using real centroid from oblast data."""
    try:
        from .oblasts import get_region_centroid
        return get_region_centroid(region_name)
    except Exception:
        sx, sy = REGION_SCHEMATIC.get(region_name, (0.5, 0.5))
        # Fallback schematic conversion
        lon = sx * 140 - 20
        lat = 110 - (sy * 70 + 40)
        return (lat, lon)


# Static schematic positions for regions (for visualization)
REGION_SCHEMATIC: dict[str, tuple[float, float]] = {
    "Donbas": (0.62, 0.52),
    "Moscow": (0.56, 0.38),
    "Leningrad": (0.52, 0.28),
    "Belarus": (0.54, 0.45),
    "Central Asia": (0.70, 0.70),
    "Caucasus": (0.66, 0.60),
    "Far East": (0.90, 0.55),
    "Kazakhstan": (0.75, 0.65),
    "Siberia": (0.82, 0.40),
    "Urals": (0.75, 0.42),
    "Volga": (0.62, 0.45),
}

# Regions east of the Urals - require survey to unlock
URALS_EAST = {"Far East", "Siberia", "Kazakhstan", "Central Asia"}


def _sim_state_to_json(state: SimulationState) -> dict[str, Any]:
    resources = dict(state.resources)
    facilities = {
        name: {
            "daily_output": fs.daily_output,
            "operating": fs.daily_output > 0,
        }
        for name, fs in state.facilities.items()
    }
    projects: list[dict[str, Any]] = []
    alerts: list[DashboardAlert] = []
    for name, ps in state.projects.items():
        stage_str = ps.stage.value
        blocked = tuple(ps.blocked_by)
        binding = ps.binding_constraint
        projects.append({
            "name": name,
            "region": ps.project.region,
            "stage": stage_str,
            "blocked_by": blocked,
            "binding_constraint": binding,
            "priority": ps.project.priority,
            "sector": ps.project.sector,
        })
        if binding:
            alerts.append(DashboardAlert(
                id=f"constraint-{name}",
                severity="warning",
                message=f"{name} constrained by {binding}",
                source=f"project:{name}",
                project_name=name,
                region=ps.project.region,
            ))
        if ps.stage.value != "commissioned":
            for blocker in blocked:
                alerts.append(DashboardAlert(
                    id=f"blocker-{name}-{blocker}",
                    severity="info" if binding else "warning",
                    message=f"{name} blocked by {blocker}",
                    source=f"project:{name}",
                    project_name=name,
                    region=ps.project.region,
                ))
    # Critical pause alert
    if state.critical_pause_latched:
        alerts.insert(0, DashboardAlert(
            id="critical-pause",
            severity="critical",
            message="Critical decision requires attention — simulation paused",
            source="autopause",
        ))
    # Map regions
    map_regions: list[dict[str, Any]] = []
    for region in state.national_map.regions:
        # Use real centroid lat/lon from oblast data
        lat, lon = _get_region_latlon(region.name)
        # Keep schematic for any code that still references it
        sx, sy = REGION_SCHEMATIC.get(region.name, (0.5, 0.5))
        surveyed = region.name not in URALS_EAST
        map_regions.append({
            "name": region.name,
            "detailed": region.detailed,
            "developable": region.developable and surveyed,
            "cities": region.cities,
            "industrial_sites": region.industrial_sites,
            "lat": lat,
            "lon": lon,
            "schematic_x": sx,
            "schematic_y": sy,
            "surveyed": surveyed,
        })

    # Oblast GeoJSON URL for polygon rendering
    oblast_geojson_url = "/static/ussr_oblasts_simplified.geojson"
    # Routes
    routes: list[dict[str, Any]] = []
    for route_id, route in state.routes.items():
        routes.append({
            "id": route_id,
            "start": route.start.name if route.start else None,
            "end": route.end.name if route.end else None,
            "infrastructure_type": route.infrastructure_type.value if route.infrastructure_type else None,
            "distance": route.distance,
        })
    # Queue items from action_queue
    queue: list[dict[str, Any]] = []
    for item in state.action_queue:
        queue.append({
            "id": item.order_id,
            "system": item.system.value if item.system else None,
            "target": item.target,
            "action": item.action,
            "severity": item.severity.value if item.severity else None,
            "available_actions": item.available_actions,
            "recommended_action": item.recommended_action,
        })
    return {
        "date": state.date.isoformat(),
        "paused": state.paused,
        "speed": state.speed.value,
        "resources": resources,
        "facilities": facilities,
        "projects": projects,
        "alerts": [
            # Use __dict__ since DashboardAlert is a dataclass with exactly these fields
            a.__dict__
            for a in alerts
        ],
        "queue": queue,
        "map_regions": map_regions,
        "routes": routes,
        "technical_knowledge": dict(state.technical_knowledge),
        "supply_chains": list(state.supply_chains),
        "global_automation": state.global_automation,
        "automation": {k.value: v for k, v in state.automation.items()},
        "critical_pause_latched": state.critical_pause_latched,
        "oblast_geojson_url": oblast_geojson_url,
    }


class SimulationStateEndpoint:
    """Wraps a Simulation and exposes its state as a JSON-serializable dict."""

    def __init__(self, simulation: Simulation) -> None:
        self._simulation = simulation

    def to_json(self) -> dict[str, Any]:
        return _sim_state_to_json(self._simulation.state)

    @property
    def simulation(self) -> Simulation:
        return self._simulation
