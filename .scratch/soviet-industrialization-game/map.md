# Soviet Industrialization Sandbox

## Destination

A handoff-ready design for a historically grounded, country-scale industrial city builder set in the Soviet Union. The player acts as the central planning authority and can build whatever the available materials, equipment, electricity, labor, freight, services, and trade envelope permit.

Time flows continuously and resolves through daily simulation ticks. The player can pause, change priorities, draw infrastructure, plan projects, and inspect the modeled state. Play begins in 1928 and has no hard ending: the historical Five-Year Plan dates are analytical milestones, not victory screens.

The central experience is turning a map of legacy industrial assets into a connected national production system. The player can build new capacity anywhere, but terrain, distance, supply access, and network connection determine cost, schedule, reliability, and eventual utilization.

## Map and starting scope

- The map uses a historically grounded 1930s USSR outline and covers the full Soviet Union visually.
- Cities, industrial assets, ports, waterways, railways, power systems, roads, and other legacy infrastructure are historically concentrated west of the Urals.
- Donbas, Moscow, and Leningrad are the fully detailed launch regions, with their existing industries and networks providing a meaningful starting advantage.
- The Urals and western regions remain present and developable at launch. Territory east of the Urals remains visible for national context but is non-interactive until a survey project unlocks its sites and networks.
- Industrial sites are placed at candidate locations or newly surveyed locations. Rail, roads, power lines, pipelines, canals, and similar infrastructure can be drawn continuously across terrain with freeform routes, automatic network snapping, and optional manual waypoints.
- Routes account for distance, terrain, crossings, climate, and access to construction supply. Connections to commissioned legacy infrastructure reduce construction and operating costs and improve reliability. Isolated construction remains possible at a premium.

## Simulation and control

- The simulation runs continuously at selectable speeds and resolves daily flows of materials, fuel, electricity, equipment, labor, housing and services, freight, and maintenance.
- Pause is unrestricted planning time. Decisions take effect when the simulation resumes; pausing itself has no penalty.
- Every major system has an independent automation switch: industry, building, transport, logistics, imports, staffing, maintenance, and project sequencing. A global switch changes all systems for convenience.
- With automation enabled, the system executes routine decisions. With automation disabled, unassigned work remains idle and appears in an action queue; no decision is silently made for the player.
- Manual orders override automation and remain active until the player revokes them. Overrides can target a project, route, resource allocation, or standing priority.
- Critical unresolved decisions can trigger autopause before continued simulation causes irreversible loss or major capacity damage. Routine notices do not pause; warnings pause when the affected system is not automated. After resolution, the player must explicitly resume the simulation.
- The decision queue shows affected systems and projects, the estimated cost of waiting, available actions, and a recommended action. The player can resolve an item manually, dismiss it, or delegate it permanently to automation.
- The player sees analytical modeled reality directly: flows, queues, forecasts, constraints, utilization, and projected commissioning dates. Reports may be uncertain because forecasts are imperfect, but they are not intentionally biased or deceptive.

## Construction, gating, and operation

Capital construction is a gated path rather than a single build action. Projects compete transparently for resources and throughput. Priority controls determine which projects receive scarce inputs first, while gates prevent downstream work from creating unsupported capacity.

The launch model should support gates for survey and design, civil works, equipment, electricity, labor, freight access, trial operation, maintenance, and commissioning. A facility can be physically complete yet remain unable to operate when a required gate is absent. The player can attempt ambitious plans, but unsupported projects queue, delay one another, or become stranded rather than succeeding for free.

Once a facility has its equipment, electricity, and labor force, it can operate. Operation is fractional and recalculated daily: a plant may run at 34% because fuel or freight access is deficient while still producing useful output. Fuel, power, inbound materials, outbound freight, labor, maintenance, and local services can each become the binding constraint.

Reports distinguish:

- **Nameplate capacity**: the designed maximum.
- **Commissioned capacity**: technically validated capacity available for production.
- **Operating output**: actual daily production.
- **Utilization**: operating output as a percentage of commissioned capacity.

Low utilization is recoverable. Fixing the binding constraint can restore output. Commissioned status is lost only through conditions such as technical failure, prolonged maintenance failure, or abandonment, not merely because current supply is inadequate.

## Resources and sectors

The initial sandbox models coal, oil and refined fuel, ore and metals, construction materials, electricity, machinery and equipment, freight capacity, labor, housing and essential services, and imported equipment. These flows support Industry, Building, and Transport without making agriculture a playable financing or extraction system.

Additional sectors may be introduced later when they directly support the established industrial model. They should enter through discoverable resources, technical knowledge, enabling infrastructure, and commissioned supply chains rather than appearing as free starting capacity.

R&D is a fundable enabling resource. Recurring funding creates an R&D stockpile; named, sector-specific productivity improvements spend that stockpile during development. Improvements require explicit adoption. New projects can adopt them during design or equipment stages, while existing facilities require retrofit projects with downtime, equipment, labor, and freight costs. Improvements may add operating or maintenance requirements alongside their productivity gains.

The visual interface includes a toggleable map inspection mode. The initial modes are Political, Industry, Network, Constraints, and R&D. Clicking a region, facility, route, or alert focuses the corresponding dashboard item; the map provides inspection and navigation, while decisions remain explicit in the queue and dashboard.

## Reporting and time horizon

The game provides reports on demand and at least quarterly. Historical comparison milestones follow the non-war-interrupted Five-Year Plan timeline: 1928 baseline, 1932, 1937, 1942, and every five years thereafter. The reports compare nameplate additions, commissioned capacity, output, utilization, infrastructure connectivity, resource bottlenecks, and disorganization by region and sector.

The 1932/33 control-figure comparison remains a special historical view. None of these dates ends the sandbox; the player can continue indefinitely and observe whether early infrastructure and commissioning choices create durable industrial systems.

## Decisions so far

- The destination is an open-ended sandbox, not a score-chasing campaign.
- The player has detailed authority over the modeled systems, with per-system automation and persistent manual overrides.
- Fractional operation is a first-class state. Construction gating protects the distinction between planned, built, commissioned, and actually operating capacity.
- The full national map is in scope, while detailed launch content focuses on Donbas, Moscow, and Leningrad.
- New sectors are a later expansion path.
- Configurable project templates are the canonical construction unit; scale, location, gates, and adopted improvements are configurable.
- Critical decisions use severity-based autopause, and resolution never resumes the simulation automatically.
- R&D funding produces a spendable stockpile for named productivity improvements with explicit adoption and retrofit paths.
- The first visual build is a local browser interface backed by the Python simulation core, centered on a project-and-constraints dashboard and a toggleable map.
- Daily utilization uses the minimum normalized availability across binding inputs and enabling systems, keeping the active bottleneck explicit.
- The 1928 dataset uses facility-level assets in Donbas, Moscow, and Leningrad, with regional aggregates elsewhere.
- The geographic presentation uses a 1930s USSR map with real oblast polygons (Natural Earth 10m admin-1 as 1939 Soviet census proxy) overlaid with the existing schematic normalized positions; east of the Urals is visible but locked behind survey projects.
- Launch construction uses configurable templates across extraction, processing, manufacturing, power, transport, and social infrastructure.
- Demand is represented as physical requirements rather than market prices; the trade envelope is a cumulative import budget with delivery lead times, and price escalation is diagnostic.
- Maintenance shortfalls accumulate degradation that caps utilization before sustained failure can remove commissioned status. Post-1940 structural changes are explicit expansion modules rather than automatic rules.
- Launch R&D includes named sector improvements: continuous casting, heavy press forging, longwall mining, cracking, high-pressure boilers, and welded rail.
- The visual layer uses a local FastAPI server, server-rendered HTMX controls, and a small Leaflet or MapLibre map over a JSON state boundary.
- Schematic map positions use normalized `(x, y)` coordinates and routes use polylines in the same space.
- The decision queue and autopause design is captured in [09-decision-queue-and-autopause.md](issues/09-decision-queue-and-autopause.md).
- The R&D and productivity design is captured in [10-r-and-d-productivity.md](issues/10-r-and-d-productivity.md).
- The dashboard and map-mode design is captured in [11-visual-dashboard-and-map-modes.md](issues/11-visual-dashboard-and-map-modes.md).

## Not yet specified

- Exact daily flow equations and the formula for combining binding constraints into utilization.
- Exact numerical values for flow equations, project costs, technology effects, survey costs, and maintenance thresholds.
- The initial facility list, regional aggregates, historical legacy-network data.
- The detailed visual language, interaction styling, and whether the first map renderer uses Leaflet or MapLibre.

## Out of scope

- Agriculture, grain production, rural extraction, forced labor, famine, and coercive displacement as modeled sectors or playable policy inputs.
