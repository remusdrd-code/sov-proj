# 09: Decision Queue and Critical Autopause

**What to build:** A visible decision queue that surfaces unresolved player and automation decisions and pauses the simulation when continuing would risk irreversible loss or major capacity damage.

**Blocked by:** 01: Daily Simulation Slice; 03: Project Lifecycle and Construction Gating

**Status:** done

- [x] Queue items identify affected systems and projects, cost of waiting, available actions, and a recommended action.
- [x] Notice items do not pause; warning items pause when the affected system is not automated; critical items always pause.
- [x] The player can resolve an item manually, dismiss it, or delegate it permanently to automation.
- [x] Resolving a critical item leaves the simulation paused until the player explicitly resumes.
- [x] Routine shortages and recoverable low utilization do not create false critical pauses.

## Answer

Accepted design: severity-based autopause protects against irreversible or materially costly decisions while preserving uninterrupted play for routine shortages. The queue is the authoritative surface for unresolved decisions, and explicit resume prevents a second problem from being hidden by automatic continuation.
