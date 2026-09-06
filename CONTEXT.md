# Project Context

## Purpose

This project analyzes a counterfactual Soviet industrialization plan beginning in 1928/29. Its objective is to explore how much reliable industrial capacity can be commissioned over an open-ended simulation without economic disorganization, using historical Five-Year Plan dates as comparison milestones.

## Canonical terms

- **Industry**: productive industrial capacity and its direct enabling systems: metallurgy, coal, oil and refining, chemicals, machine-building, construction materials, electricity generation and transmission, and fuel systems.
- **Building**: civil works required to make industrial capacity operational: factories, mines, power-plant structures, transport civil works, worker housing, and essential water, sewer, heat, and local-transit systems.
- **Transport**: freight-supporting rail infrastructure, rolling stock and repair, waterways and shipping, ports, and industrial feeder roads.
- **Capital construction**: the complete path from survey and design through civil works, equipment installation, trial operation, and full commissioning. Expenditure or construction starts do not equal productive capacity.
- **Commissioned capacity**: capacity that has completed its construction and equipment gates, operated through a test period, has trained labor and maintenance support, and can deliver output through reliable freight routes.
- **Disorganization**: measurable failure of coordination or welfare boundaries, including unfinished projects, delivery arrears, freight unreliability, power shortages, labor loss, inadequate housing and services, excessive price escalation, and insufficient maintenance.
- **Urbanization boundary**: the limit on industrial labor concentration imposed by the exogenous food, housing, heat, sanitation, transport, and service capacity assumed by the model. Agriculture is outside the model; requisitioning is not an industrial financing input.
- **Trade envelope**: the separate modeled external purchasing-power ceiling equal to 5% of 1928 GDP, reserved for verified imported bottlenecks. It is not foreign direct investment or domestic capital expenditure.
- **Control figure**: an officially stated quantitative target or limit in the original First Five-Year Plan. It is distinct from an appropriation, realized output, reported fulfillment, or counterfactual assumption.
- **Nameplate capacity**: the maximum output a completed industrial facility is designed to produce under stated operating conditions. It is not the same as commissioned capacity or current output.
- **Utilization**: current operating output expressed as a share of a facility's commissioned capacity. Utilization can be fractional and can recover when its limiting conditions improve.
- **Operating output**: the actual production delivered by commissioned capacity under current daily constraints.
- **Legacy infrastructure**: infrastructure present in the 1928 starting state, or infrastructure later commissioned and maintained well enough to provide network connection benefits.
- **Construction gating**: the rule that a capital-construction stage cannot create its downstream capability until required prerequisites, such as equipment, electricity, labor, freight access, and trial operation, are available.
- **Automation**: delegated execution of decisions in a modeled system. The player may enable or disable automation independently by system; manual overrides remain active until revoked.
- **Decision queue**: the visible set of unresolved player or automation decisions, including their affected systems, consequences, cost of waiting, and available resolutions.
- **Autopause**: an automatic pause triggered by a critical decision whose unresolved continuation risks irreversible loss or major capacity damage.
- **R&D funding**: a recurring allocation that generates a stockpile for developing named, sector-specific productivity improvements.
- **Productivity improvement**: a developed technical change that modifies a sector's output or operating requirements. Adoption is explicit and may require cost, downtime, or retrofit work.
- **Map mode**: a visual inspection layer that changes the map's colors, labels, and overlays without changing simulation state. The initial modes are Political, Industry, Network, Constraints, and R&D.
- **Survey boundary**: the rule that visible territory is not necessarily actionable territory. Regions east of the Urals are shown on the historical map but remain non-interactive until a survey project unlocks their sites and networks.
- **Schematic position**: a normalized map coordinate used to preserve relative geography for visualization without claiming survey-grade geographic accuracy.
- **Analytical milestone**: a dated report used to compare the sandbox state with historical plans or earlier states. It does not end play or impose a victory condition.

## Scope boundary

Detailed optimization covers Industry, Building, and Transport only. Agriculture, grain production, rural extraction, forced labor, famine, and coercive displacement are excluded as sectors or feasible policy inputs.
