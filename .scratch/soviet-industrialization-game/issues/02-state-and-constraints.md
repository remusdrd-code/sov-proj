# 02: National Map and Legacy Infrastructure

**What to build:** A full-USSR map with historically concentrated cities, industries, and legacy networks. Donbas, Moscow, and Leningrad receive detailed launch data.

**Blocked by:** 01: Daily Simulation Slice

**Status:** resolved

- [x] The player can view the full Soviet Union with cities, industrial sites, and legacy infrastructure concentrated west of the Urals.
- [x] Donbas, Moscow, and Leningrad have detailed launch locations and legacy industrial context.
- [x] The Urals and other regions are present as identifiable, developable national-map regions.
- [x] Map state can be inspected through the daily simulation without introducing excluded agricultural or coercive systems.

## Answer

Implemented the `NationalMap` and `Region` domain model with the full launch-region dataset. The daily simulation state exposes and preserves the map, while tests verify the three detailed launch regions, developable national regions, and absence of excluded systems.
