# 11: Visual Dashboard and Toggleable Map Modes

**What to build:** A local browser interface backed by the Python simulation core, centered on a project-and-constraints dashboard with a map that can switch inspection modes.

**Blocked by:** 01: Daily Simulation Slice; 02: National Map and Legacy Infrastructure; 03: Project Lifecycle and Construction Gating

**Status:** resolved

- [x] The browser view exposes date, speed, pause state, resources, project queue, blockers, and autopause alerts.
- [x] The map can toggle between Political, Industry, Network, Constraints, and R&D modes.
- [x] Each map mode changes visible colors, labels, and overlays without changing simulation state.
- [x] The map uses a historically grounded 1930s USSR outline with schematic normalized positions.
- [x] Territory east of the Urals is visible but non-interactive until a survey project unlocks its sites and networks.
- [x] Clicking a region, facility, route, or alert focuses the related dashboard item.
- [x] Decisions remain explicit in the queue and dashboard rather than being hidden in map interactions.
- [x] The visual layer reads state through a small JSON endpoint while daily transitions remain in the Python simulation package.

## Answer

Accepted design: begin with a lightweight local FastAPI application using server-rendered HTMX controls and a small Leaflet or MapLibre map over a replaceable JSON state boundary. The project-and-constraints dashboard is the primary decision surface; the map is an inspection and navigation surface with five clear modes. A historical 1930s USSR map is visible from the start, while territory east of the Urals remains locked until surveyed.
