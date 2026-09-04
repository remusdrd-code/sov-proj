from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, replace
from enum import Enum


class InfrastructureType(str, Enum):
    RAIL = "rail"
    ROAD = "road"
    POWER = "power"
    PIPELINE = "pipeline"
    CANAL = "canal"


@dataclass(frozen=True)
class MapNode:
    name: str
    x: float
    y: float
    network_connected: bool = False


@dataclass(frozen=True)
class Terrain:
    terrain_multiplier: float = 1
    crossings: int = 0
    climate_multiplier: float = 1
    supply_access: float = 1

    def __post_init__(self) -> None:
        if self.terrain_multiplier <= 0 or self.climate_multiplier <= 0:
            raise ValueError("terrain and climate multipliers must be positive")
        if self.crossings < 0 or not 0 < self.supply_access <= 1:
            raise ValueError("crossings must be non-negative and supply access must be in (0, 1]")


@dataclass(frozen=True)
class InfrastructureRoute:
    identifier: str
    infrastructure_type: InfrastructureType
    start: MapNode
    end: MapNode
    waypoints: tuple[tuple[float, float], ...]
    snapped: bool
    commissioned: bool
    connected_to_legacy: bool
    distance: float
    construction_cost: float
    construction_days: int
    reliability: float
    isolated_premium: float

    @property
    def route_id(self) -> str:
        return self.identifier


class RoutePlanner:
    """Draw continuous infrastructure routes over a simple coordinate surface."""

    _BASE_COSTS = {
        InfrastructureType.RAIL: 10,
        InfrastructureType.ROAD: 6,
        InfrastructureType.POWER: 8,
        InfrastructureType.PIPELINE: 7,
        InfrastructureType.CANAL: 12,
    }

    def __init__(self, nodes: tuple[MapNode, ...] = (), snap_distance: float = 1.5) -> None:
        if snap_distance <= 0:
            raise ValueError("snap distance must be positive")
        self._nodes = nodes
        self._snap_distance = snap_distance

    def draw(
        self,
        infrastructure_type: InfrastructureType,
        start: tuple[float, float],
        end: tuple[float, float],
        waypoints: tuple[tuple[float, float], ...] = (),
        terrain: Terrain | None = None,
        commissioned: bool = False,
    ) -> InfrastructureRoute:
        terrain = terrain or Terrain()
        resolved_start, start_snapped = self._resolve_node(
            start, f"route start ({start[0]}, {start[1]})"
        )
        resolved_end, end_snapped = self._resolve_node(
            end, f"route end ({end[0]}, {end[1]})"
        )
        points = ((resolved_start.x, resolved_start.y),) + waypoints + (
            (resolved_end.x, resolved_end.y),
        )
        distance = sum(
            math.dist(first, second) for first, second in zip(points, points[1:])
        )
        connected_to_legacy = (
            resolved_start.network_connected or resolved_end.network_connected
        )
        base_cost = (
            distance
            * self._BASE_COSTS[infrastructure_type]
            * terrain.terrain_multiplier
            * terrain.climate_multiplier
            * (1 + terrain.crossings * 0.1)
            * (1 + (1 - terrain.supply_access) * 0.5)
        )
        isolation_factor = 0.75 if connected_to_legacy else 1.5
        construction_cost = base_cost * isolation_factor
        isolated_premium = 0 if connected_to_legacy else base_cost * 0.75
        construction_days = max(
            1,
            math.ceil(
                distance
                * terrain.terrain_multiplier
                * terrain.climate_multiplier
                * (1 + terrain.crossings * 0.1)
                * (1 + (1 - terrain.supply_access) * 0.5)
                * (0.9 if connected_to_legacy else 1.2)
            ),
        )
        reliability = max(
            0,
            min(
                1,
                0.9
                * terrain.supply_access
                / terrain.terrain_multiplier
                / terrain.climate_multiplier
                / (1 + terrain.crossings * 0.05)
                + (0.1 if connected_to_legacy else 0),
            ),
        )
        route_id = f"route-{uuid.uuid4()}"
        route = InfrastructureRoute(
            identifier=route_id,
            infrastructure_type=infrastructure_type,
            start=resolved_start,
            end=resolved_end,
            waypoints=waypoints,
            snapped=start_snapped or end_snapped,
            commissioned=commissioned,
            connected_to_legacy=connected_to_legacy,
            distance=distance,
            construction_cost=construction_cost,
            construction_days=construction_days,
            reliability=reliability,
            isolated_premium=isolated_premium,
        )
        if commissioned:
            return self.commission(route)
        return route

    def _resolve_node(
        self, point: tuple[float, float], fallback_name: str
    ) -> tuple[MapNode, bool]:
        nearest = min(
            self._nodes,
            key=lambda node: math.dist(point, (node.x, node.y)),
            default=None,
        )
        if nearest is not None and math.dist(point, (nearest.x, nearest.y)) <= self._snap_distance:
            return nearest, True
        return MapNode(fallback_name, point[0], point[1]), False

    def commission(self, route: InfrastructureRoute) -> InfrastructureRoute:
        """Make a completed route available as a legacy network connection."""
        nodes = list(self._nodes)
        for endpoint in (route.start, route.end):
            matching_index = next(
                (index for index, node in enumerate(nodes) if node.name == endpoint.name),
                None,
            )
            connected_node = MapNode(
                endpoint.name,
                endpoint.x,
                endpoint.y,
                network_connected=True,
            )
            if matching_index is None:
                nodes.append(connected_node)
            else:
                nodes[matching_index] = connected_node
        self._nodes = tuple(nodes)
        return replace(
            route,
            commissioned=True,
            connected_to_legacy=True,
            isolated_premium=0,
        )