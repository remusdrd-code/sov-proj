# Open-source resource-management game code reference

**Research date:** 2026-09-05  
**Question:** Which open-source resource-management game is the closest code reference for this project's industrial simulation?

## Executive answer

**Widelands** is the best primary reference for this project. Its source models production sites, input queues, workers, construction sites, and data-driven production programs as separate concepts. That maps closely to this project's Industry, Building, Transport, construction gating, and automation requirements.

**OpenTTD** is a useful secondary reference for cargo provenance, periodic industry production, and reason-coded pause behavior. It is a stronger reference for networked freight movement than for construction gating or multi-input production chains.

The recommendation is to study the designs and, where legally appropriate, reuse small pieces only after checking the applicable license and dependencies. Neither project should be treated as a drop-in implementation for this Python codebase.

## Selection criteria

The candidate should be an actual open-source game with primary-source code showing most of these behaviors:

- resource inputs becoming outputs through production chains;
- buildings or projects whose construction state gates operation;
- transport or economy queues connecting producers and consumers;
- a discrete simulation update or production program;
- player or system pause/event handling that can inform the decision queue and autopause design.

## Candidate comparison

| Project | Best match | Important limitation | Primary sources |
|---|---|---|---|
| **Widelands** | Production chains, building construction, input queues, workers, and data-driven recipes | Its real-time strategy economy and tribe-specific rules are much narrower than the project's historical industrial model | [Widelands repository](https://github.com/widelands/widelands), [GPL license](https://github.com/widelands/widelands/blob/master/COPYING) |
| **OpenTTD** | Cargo movement, industry production cycles, cargo packets, and explicit pause reasons | Industry production is intentionally simpler; it does not provide the same construction lifecycle or worker/input production-site model | [OpenTTD repository](https://github.com/OpenTTD/OpenTTD), [GPL license](https://github.com/OpenTTD/OpenTTD/blob/master/COPYING.md) |

## Recommended source map: Widelands

### Production sites and programs

Widelands represents a production site as a map object with production behavior rather than embedding every recipe in a global simulation loop. The declarations are separated into headers for the production site and production program, while implementation behavior is in the corresponding source file.

- [`productionsite.h`](https://github.com/widelands/widelands/blob/master/src/logic/map_objects/tribes/productionsite.h) defines the production-site object and its stateful interface.
- [`production_program.h`](https://github.com/widelands/widelands/blob/master/src/logic/map_objects/tribes/production_program.h) defines the production-program representation.
- [`productionsite.cc`](https://github.com/widelands/widelands/blob/master/src/logic/map_objects/tribes/productionsite.cc) implements production-site behavior, including the interaction between inputs, workers, and production execution.

**Useful design to adapt:** represent a project or facility as a stateful domain object, and represent its recipe or operating program as data that can be inspected, validated, and scheduled. For this project, that can support explicit gates such as survey, civil works, equipment, labor, trial operation, and reliable freight access without putting all rules into `simulation.py`.

### Construction lifecycle

- [`constructionsite.h`](https://github.com/widelands/widelands/blob/master/src/logic/map_objects/tribes/constructionsite.h) defines the construction-site object.

**Useful design to adapt:** keep “being built” distinct from “operating.” That supports this project's rule that expenditure or construction starts do not create commissioned capacity. A project can remain in construction, wait for missing inputs, complete construction, and only then pass trial-operation and commissioning gates.

### Inputs and economy queues

- [`input_queue.h`](https://github.com/widelands/widelands/blob/master/src/economy/input_queue.h) defines an input queue used to request and receive materials for economic objects.
- The production-site implementation in [`productionsite.cc`](https://github.com/widelands/widelands/blob/master/src/logic/map_objects/tribes/productionsite.cc) shows how production objects coordinate their input and worker requirements.

**Useful design to adapt:** make shortage and delivery state explicit at the consuming facility. That is a good fit for this project's freight reliability and construction gating: a plant can have an input shortfall without being destroyed, while a critical unresolved choice can still enter the decision queue.

### Data-driven recipes

- [Empire mill definition](https://github.com/widelands/widelands/blob/master/data/tribes/buildings/productionsites/empire/mill/init.lua) is a concrete data definition for a production building and its production programs.

**Useful design to adapt:** keep ordinary recipes and balancing values outside the core execution code. In this project, sector definitions can hold inputs, outputs, labor, energy, construction requirements, and operating constraints while Python code handles generic lifecycle and scheduling rules.

## Secondary source map: OpenTTD

### Industry production

- [`industry_cmd.cpp`](https://github.com/OpenTTD/OpenTTD/blob/master/src/industry_cmd.cpp) contains industry behavior and production-related logic.

**Useful design to adapt:** a periodic production step can be isolated from map rendering and player commands. This is relevant to the daily simulation slice and to distinguishing nameplate capacity from current operating output.

### Cargo identity and transport

- [`cargopacket.h`](https://github.com/OpenTTD/OpenTTD/blob/master/src/cargopacket.h) defines cargo packets and their state.

**Useful design to adapt:** preserve cargo identity and quantities as they move through the network rather than representing transport as a single undifferentiated number. For this project, provenance and delivery state can help explain why a plant is underutilized or why construction is waiting.

### Pause reasons and simulation control

- [`misc_cmd.cpp`](https://github.com/OpenTTD/OpenTTD/blob/master/src/misc_cmd.cpp) contains command-level miscellaneous controls, including pause-related behavior.
- [`openttd.cpp`](https://github.com/OpenTTD/OpenTTD/blob/master/src/openttd.cpp) contains core application and game-loop control.

**Useful design to adapt:** keep “the simulation is paused” separate from “why it is paused.” This supports a decision queue in which a critical item pauses the simulation, resolving the item does not automatically resume it, and the player must explicitly resume.

## Fit to this project

| Project need | Closest reference | Adaptation boundary |
|---|---|---|
| Production chains | Widelands production sites/programs | Use historical sector and facility concepts, not tribe/building rules. |
| Construction gating | Widelands construction sites | Add this project's survey, equipment, trial-operation, and commissioning gates. |
| Freight and input constraints | Widelands input queues plus OpenTTD cargo packets | Preserve the existing network model and use queue state as an explanation of shortages. |
| Daily operating output | OpenTTD industry production logic | Keep utilization, maintenance, labor, and power constraints explicit. |
| Automation and decisions | Neither is a direct match | Keep the project's decision queue authoritative and add severity/recommendation data around domain events. |
| Autopause | OpenTTD pause-control code as a conceptual reference | Implement criticality in the project's own event model; do not copy UI or command assumptions. |

## License and reuse caveat

The primary license files show GPL version 2 text for both projects: [Widelands `COPYING`](https://github.com/widelands/widelands/blob/master/COPYING) and [OpenTTD `COPYING.md`](https://github.com/OpenTTD/OpenTTD/blob/master/COPYING.md). OpenTTD also states that third-party modules are exceptions to its main license in that file, so dependencies must be checked separately.

This repository should therefore treat these projects as architectural references unless a deliberate compatibility review approves code reuse. Before copying any code, check the exact source file's current license, repository contribution terms, third-party dependencies, and whether distributing a derivative would impose source-distribution or other GPL obligations. A clean-room reimplementation of the relevant domain behavior may be simpler and better suited to this Python project.

## Practical recommendation

Start by reading Widelands' `ProductionSite`, `ProductionProgram`, `ConstructionSite`, and `InputQueue` together. The most valuable pattern is the separation between a stateful facility, a data-defined operating program, construction state, and delivered inputs. Then consult OpenTTD's cargo packet and pause-control code when implementing freight explanations and the decision queue's explicit paused/resume state.

Do not copy code directly into the project as part of this investigation. Use the source map to guide a small, project-native design that preserves the repository's canonical distinctions between construction, commissioned capacity, utilization, operating output, and network reliability.
