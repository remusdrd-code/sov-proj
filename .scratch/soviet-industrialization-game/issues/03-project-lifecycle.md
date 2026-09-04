# 03: Project Lifecycle and Construction Gating

**What to build:** Projects progress through survey, design, civil works, equipment, electricity, labor, trial operation, and commissioning, with missing prerequisites visibly blocking work.

**Blocked by:** 01: Daily Simulation Slice; 02: National Map and Legacy Infrastructure

**Status:** resolved

- [x] An industrial project can progress through explicit construction and commissioning stages.
- [x] Missing equipment, electricity, labor, freight access, trial operation, or maintenance prerequisites visibly block the relevant stage.
- [x] Project priorities compete transparently for scarce inputs and throughput.
- [x] The player can distinguish planned, built, commissioned, and operating capacity.

## Answer

Implemented gated `Project` and `ProjectState` domain objects and integrated them into the daily simulation transition. Projects progress one gate per day through survey, design, civil works, equipment, electricity, labor, freight access, maintenance, trial operation, and commissioning; consume scarce resources by priority; expose blocking resource names; and distinguish planned, physically complete, commissioned, and currently operating capacity. Operating output remains zero until the later resource-flow slice connects commissioned projects to daily facility operation.
