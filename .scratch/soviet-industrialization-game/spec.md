# Soviet Industrialization Sandbox

Status: ready-for-agent

## Problem Statement

The project needs a coherent specification for an open-ended, historically grounded industrial sandbox set in the Soviet Union from 1928 onward. The player should be able to plan and build a national industrial system at city-builder scale while daily resource, infrastructure, labor, construction, and commissioning constraints make ambitious industrial development consequential.

The design must retain a clear distinction between planned projects, construction progress, commissioned capacity, and actual production. It also needs to support both automated administration and detailed player control without turning the simulation into either a spreadsheet or a hidden black box.

## Solution

Build a country-scale industrial city builder with a historically grounded 1930s USSR map and continuous time resolved through daily simulation ticks. The player is the central planning authority and may delegate each major system to automation or control it manually. The player can pause freely, queue construction, draw infrastructure across terrain, set priorities, inspect flows, and override automated decisions. Manual overrides persist until revoked.

The launch model focuses detailed content on the historically concentrated western industrial core: Donbas, Moscow, and Leningrad. The full national map remains visible and represented historically, with the territory east of the Urals shown for context but locked to non-interactive status until a survey project unlocks the region. Legacy rail, power, port, water, road, industrial, and city systems make connected development cheaper and more reliable without preventing isolated expansion.

Industrial construction uses explicit gates and transparent competition for scarce inputs. Once a facility has its equipment, electricity, and labor force, it can operate. Its output is fractional and recalculated daily, so a facility can operate at a fraction of capacity because fuel, freight, maintenance, labor, or local services are deficient. This under-utilization is recoverable when the player fixes the binding constraint. Historical Five-Year Plan dates provide analytical reports rather than victory conditions or a hard ending.

The game also includes a visible decision queue, severity-based autopause, and a fundable R&D system. Critical unresolved decisions pause the simulation before they cause irreversible losses; routine warnings do not. R&D funding creates a stockpile that enables named, sector-specific productivity improvements. Improvements require explicit adoption, can affect new projects or require retrofit work on existing facilities, and create measurable output or maintenance tradeoffs.

The visual interface is a local browser layer backed by a Python simulation core. The first view is a project-and-constraints dashboard plus a map with toggleable Political, Industry, Network, Constraints, and R&D modes. The map is an inspection and navigation surface; the queue and dashboard remain the primary decision surfaces.

## User Stories

1. As the central planning authority, I want to view the entire Soviet Union, so that I can reason about national industrial geography.
2. As the central planning authority, I want a historically grounded 1930s USSR map, so that the industrial system reflects the region's real spatial and political geography.
3. As the player, I want the full map to be visible for context, so that I can understand national scale and the placement of industrial cores.
4. As the player, I want territory east of the Urals to remain non-interactive until surveyed, so that undeveloped regions do not create accidental, unsupported builds.
5. As the player, I want Donbas, Moscow, and Leningrad to have detailed sites and legacy networks, so that the launch experience begins with historically important industrial choices.
6. As the player, I want the Urals and other regions to remain visible on the map, so that I can see future expansion options and national bottlenecks.
7. As the player, I want to place industrial projects at viable surveyed sites, so that geography affects planning rather than acting as decoration.
8. As the player, I want surveys to unlock non-interactive territory, so that uncharted regions can become industrial options after a deliberate investment.
9. As the player, I want to draw railways, roads, power lines, pipelines, canals, and similar routes continuously across terrain, so that infrastructure placement feels like a country-scale builder.
10. As the player, I want routes to snap automatically to cities, sites, and existing networks, so that planning is efficient.
11. As the player, I want to shape major routes with manual waypoints, so that I can make deliberate geographic trade-offs.
12. As the player, I want distance, terrain, crossings, climate, and supply access to affect route cost, so that infrastructure placement has strategic consequences.
13. As the player, I want connections to commissioned legacy infrastructure to reduce construction and operating costs, so that established industrial regions have a real advantage.
14. As the player, I want isolated infrastructure to remain possible at higher cost and lower reliability, so that I am not locked out of developing new regions.
15. As the player, I want to see daily flows of coal, oil, refined fuel, ore, metals, construction materials, machinery, equipment, electricity, freight, labor, housing, services, and maintenance, so that I can understand the industrial system.
16. As the player, I want imported equipment to consume a bounded trade envelope, so that foreign bottlenecks cannot be purchased without limit.
17. As the player, I want to pause time without penalty, so that I can plan complex construction and logistics orders.
18. As the player, I want selectable simulation speeds, so that I can alternate between close management and long-term observation.
19. As the player, I want continuous daily simulation ticks, so that resource shortages and operational changes have understandable timing.
20. As the player, I want an automation switch for industry, so that routine production decisions can be delegated.
21. As the player, I want independent automation switches for building, transport, logistics, imports, staffing, maintenance, and project sequencing, so that I can delegate only the systems I do not want to manage.
22. As the player, I want a global automation switch, so that I can change the overall control mode quickly.
23. As the player, I want automation-off systems to leave unassigned work idle, so that the game never silently makes a decision I intended to control.
24. As the player, I want an action queue for blocked and unassigned work, so that manual administration has a clear workload.
25. As the player, I want manual orders to override automation, so that I can intervene in a specific project, route, allocation, or priority.
26. As the player, I want manual overrides to remain active until revoked, so that important instructions are not silently lost.
27. As the player, I want a visible decision queue, so that unresolved decisions and system conflicts are surfaced directly.
28. As the player, I want a critical decision to trigger autopause, so that I can prevent irreversible or financially costly errors from continuing under the clock.
29. As the player, I want routine notices to remain visible without pausing the simulation, so that small shortages do not interrupt my flow.
30. As the player, I want warning-level issues to pause only when the affected system is not automated, so that automation can absorb low-level coordination without stopping play.
31. As the player, I want the simulation to remain paused after a critical issue until I explicitly resume, so that I make the decision rather than losing control to a hidden continuation.
32. As the player, I want to set project and resource priorities, so that scarce construction throughput is directed toward my national plan.
33. As the player, I want automation to execute routine decisions, so that detailed control is available without requiring constant micromanagement.
34. As the player, I want each project to pass survey and design gates, so that construction starts from a credible plan.
35. As the player, I want civil works and equipment installation represented separately, so that spending and physical completion do not equal productive capacity.
36. As the player, I want equipment availability to gate operation, so that an empty factory cannot produce.
37. As the player, I want electricity availability to gate operation, so that connected power is part of industrial capacity.
38. As the player, I want labor availability to gate operation, so that a finished facility without workers cannot produce.
39. As the player, I want freight access and trial operation represented as commissioning requirements, so that a facility must be connected to a usable supply chain.
40. As the player, I want maintenance support to matter, so that unreliable capacity can degrade or lose commissioned status over time.
41. As the player, I want unsupported projects to queue, delay, or become stranded rather than succeeding for free, so that overbuilding has visible consequences.
42. As the player, I want a facility with equipment, electricity, and labor to operate even when other inputs are deficient, so that partial production is possible.
43. As the player, I want facility operation to be fractional and recalculated daily, so that a plant can run at a fraction of capacity rather than being reduced to a binary on/off state.
44. As the player, I want the binding constraint identified, such as deficient fuel or freight access, so that I know how to restore utilization.
45. As the player, I want low utilization to be recoverable, so that solving a supply problem restores value to an already commissioned facility.
46. As the player, I want nameplate capacity, commissioned capacity, operating output, and utilization shown separately, so that planned potential is not confused with delivered production.
47. As the player, I want commissioned status lost only through technical failure, prolonged maintenance failure, or abandonment, so that temporary shortages do not erase completed work.
48. As the player, I want to inspect regional and sector-level bottlenecks, so that national aggregates do not hide local failures.
49. As the player, I want analytical reports on demand, so that I can investigate the system whenever a decision requires it.
50. As the player, I want at least quarterly reports, so that I can review progress without waiting for historical milestones.
51. As the player, I want reports at the 1928 baseline and 1932, 1937, 1942, and subsequent Five-Year Plan dates, so that I can compare the sandbox with the historical timeline without a war interruption.
52. As the player, I want the 1932/33 control-figure comparison preserved as a special view, so that the original planning target remains available for analysis.
53. As the player, I want historical milestones to be reports rather than victory screens, so that I can continue experimenting.
54. As the player, I want to continue beyond 1940 indefinitely, so that durable consequences of early infrastructure and commissioning choices can emerge.
55. As the player, I want transparent analytical reporting rather than intentionally biased institutional reports, so that I can learn the actual modeled causes of outcomes.
56. As the player, I want forecasts to express uncertainty without hiding the modeled state, so that imperfect prediction does not become artificial deception.
57. As the player, I want technical knowledge and enabling infrastructure to unlock new sectors later, so that the model expands without free capacity.
58. As the player, I want agriculture, grain production, forced labor, famine, and coercive displacement excluded from playable inputs, so that the industrial sandbox respects its defined scope.
59. As the player, I want housing and essential services represented as industrial constraints, so that urban growth and labor concentration have consequences without modeling agriculture.
60. As the player, I want disorganization to reflect unfinished projects, delivery arrears, unreliable freight, power shortages, labor loss, inadequate services, price escalation, and insufficient maintenance, so that systemic overload is measurable.
61. As the player, I want to compare capacity, output, utilization, connectivity, bottlenecks, and disorganization by region and sector, so that different industrial strategies can be evaluated.
62. As the player, I want a fundable R&D budget, so that investment in technical knowledge produces measurable improvements rather than invisible abstract progress.
63. As the player, I want R&D improvements to be named and sector-specific, so that I can see exactly what changed in the industrial system.
64. As the player, I want future projects to adopt improvements during design or equipment stages, so that new capacity reflects technical developments.
65. As the player, I want existing facilities to adopt improvements through retrofit projects, so that historical plants can also be modernized.
66. As the player, I want the quantity and cost of R&D improvements to be explicit, so that I understand the tradeoff between output gains and maintenance or energy demand.
67. As the player, I want a map mode toggle with Political, Industry, Network, Constraints, and R&D views, so that I can focus the map on different kinds of information.
68. As the player, I want the map to present a historical 1930s USSR outline, so that the world map feels grounded in the period rather than abstracted into a generic board.
69. As the player, I want the browser view to highlight queue items and blockers, so that critical issues are visible before they become ambiguous.
70. As a future implementer, I want a single daily simulation transition seam, so that resource allocation, construction gates, operating output, and analytical reporting can be tested through external behavior.

## Implementation Decisions

- The core simulation is a continuous-time presentation over daily state transitions. Pause changes whether transitions are applied; it does not create a separate turn-based ruleset.
- The highest testing seam is the daily simulation transition: given a state and active orders, it resolves flows, project progress, gates, facility utilization, maintenance, and disorganization. UI controls should dispatch intent into this seam and render its observable state.
- The domain state must distinguish planned projects, construction progress, physically complete projects, commissioned capacity, operating output, and utilization.
- Facility utilization is fractional. A facility can operate when it has equipment, electricity, and labor; fuel, inbound materials, outbound freight, maintenance, and local services can reduce output after operation is enabled. The binding constraint must be exposed.
- Construction gating and priority are separate concerns. Gates define prerequisites; priorities decide which eligible work receives scarce inputs. Automation proposes or executes eligible work, while disabled automation leaves unassigned work idle.
- Automation is independently configurable for industry, building, transport, logistics, imports, staffing, maintenance, and project sequencing, with a global convenience switch. Persistent manual overrides take precedence until revoked.
- The decision queue is the authoritative way to surface unresolved player or automation decisions, including affected systems, consequences, cost of waiting, available actions, and recommended action.
- Critical decisions use severity-based autopause. Routine shortages and recoverable low utilization remain visible without a pause; warning-level pauses occur when the affected system is not automated; critical-level pauses are unconditional.
- Infrastructure is represented as continuous terrain routes connected to sites, cities, and networks. Route cost and reliability depend on geographic conditions and supply access. Commissioned legacy infrastructure supplies connection benefits; unfinished routes do not.
- The launch map covers the full Soviet Union visually. Data and interaction detail are highest in Donbas, Moscow, and Leningrad; the Urals and other regions are present and developable with lower initial detail. Territory east of the Urals is visible for context but remains non-interactive until a survey project unlocks the region.
- The 1930s map uses schematic normalized coordinates rather than survey-grade geographic precision. It preserves an historical visual outline and relative geography without promising a GIS-grade source model.
- The initial resource model includes coal, oil and refined fuel, ore and metals, construction materials, electricity, machinery and equipment, freight capacity, labor, housing and essential services, maintenance, and imported equipment within the trade envelope.
- Demand is modeled as physical requirements rather than market pricing. The trade envelope is a cumulative import budget with lead times; price escalation is diagnostic and should not be the primary allocator.
- New sectors are not launch requirements. Later sectors must support Industry, Building, or Transport and enter through explicit enabling conditions.
- R&D funding is a recurring allocation that creates a stockpile for named, sector-specific productivity improvements. New projects can adopt improvements during design or equipment stages; existing facilities require explicit retrofit projects with downtime, equipment, labor, and freight costs.
- The first launch R&D set includes continuous casting, heavy press forging, longwall mining, cracking, high-pressure boilers, and welded rail. They represent the first generation of sector-specific productivity improvements rather than a universal technology system.
- The visual interface is a local browser layer backed by a Python simulation core. The first view is a project-and-constraints dashboard with a map toggle between Political, Industry, Network, Constraints, and R&D modes. The map is an inspection and navigation surface; decisions remain explicit in the queue and dashboard.
- The browser layer uses a small JSON state boundary, a local FastAPI service, and server-rendered HTMX controls. The map uses Leaflet for the first build, with the renderer adapter kept replaceable.
- Reports are analytical and available on demand and at least quarterly. Historical milestones occur at the 1928 baseline, 1932, 1937, 1942, and every five years afterward. Play has no hard end date.
- The project continues to use the domain boundaries in the project glossary: agriculture, grain production, rural extraction, forced labor, famine, and coercive displacement are not modeled sectors or feasible policy inputs.

## Testing Decisions

- Tests should assert external behavior at the daily simulation transition seam, using known state, active orders, available resources, and resulting state or report data. They should not assert internal queue algorithms or rendering implementation details.
- The daily transition must be tested for pause behavior, speed-independent daily resolution, resource flow, construction priority, gate blocking, commissioning, fractional operation, binding-constraint reporting, maintenance degradation, and disorganization changes.
- Automation tests must cover each system switch, the global switch, idle unassigned work when automation is disabled, and persistent manual overrides that remain active until revoked.
- Infrastructure tests must cover terrain-sensitive cost, snapping and network connection, legacy-infrastructure benefits, isolated-construction premiums, and the fact that unfinished routes do not provide connection benefits.
- Facility lifecycle tests must distinguish nameplate capacity, commissioned capacity, operating output, and utilization, including a facility operating at a fraction of capacity because fuel or freight access is deficient and recovering after the constraint is fixed.
- Decision-queue tests must cover notice, warning, and critical autopause events, and confirm that critical events remain paused until explicit player resume.
- R&D tests must cover recurring funding, explicit adoption, new-project adoption, retrofit adoption, and measurable output or maintenance tradeoffs.
- Reporting tests must cover on-demand reports, quarterly reports, the historical milestone dates, the 1932/33 control-figure view, regional and sector breakdowns, and continued simulation after 1940.
- Map tests should verify that the full national map is visible, detailed launch data exists for Donbas, Moscow, and Leningrad, and east-of-Ural territory remains locked until survey unlocks it.
- No repository test framework or comparable prior art is currently present. The first implementation should establish domain-level tests around the daily transition seam before adding UI or visual regression coverage.

## Out of Scope

- Agriculture, grain production, rural extraction, forced labor, famine, and coercive displacement as modeled sectors or playable policy inputs.
- A fixed victory condition, score-only campaign, or mandatory ending in 1932/33, 1937, 1940, or any other milestone.
- Deliberately deceptive factional reporting or hidden institutional bias as a primary mechanic.
- Additional sectors that do not directly support Industry, Building, or Transport.
- A requirement to model every Soviet region at the same site and network detail as Donbas, Moscow, and Leningrad in the first release.
- Treating expenditure, construction starts, or nameplate capacity as equivalent to commissioned capacity.
- The full historical map projection, asset-level dataset, and trade-price system beyond the initial launch assumptions described above.

## Further Notes

The existing child tickets cover the major follow-on slices: daily turn loop, state and constraints, project lifecycle, network and regional model, historical content, evaluation, player interface, queue and autopause, R&D, and the visual dashboard. They should be refined against this parent contract before implementation. Exact numerical values for flow equations, project costs, technology effects, maintenance thresholds, and map styling remain design work that should be assigned to later implementation tickets after the core simulation is proven.
