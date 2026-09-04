# 04: Terrain Infrastructure Construction

**What to build:** Players draw rail, roads, power lines, pipelines, and canals across terrain with snapping, waypoints, terrain-sensitive costs, network benefits, and isolated-construction penalties.

**Blocked by:** 02: National Map and Legacy Infrastructure; 03: Project Lifecycle and Construction Gating

**Status:** resolved

- [x] The player can draw continuous infrastructure routes across terrain and connect them to sites, cities, and existing networks.
- [x] Routes support automatic snapping and optional manual waypoints.
- [x] Distance, terrain, crossings, climate, and construction-supply access affect route cost and schedule.
- [x] Commissioned legacy connections improve construction and operating reliability, while isolated routes remain possible at a premium.

## Answer

Implemented immutable route planning with rail, road, power, pipeline, and canal types. Routes snap to known map nodes, preserve manual waypoints, calculate terrain-sensitive cost, schedule, and reliability, apply commissioned legacy-network benefits, and expose isolated-construction premiums. Stable route identities allow parallel infrastructure, and commissioning a route extends the planner's connected network. Routes are available through the daily simulation state for inspection.
