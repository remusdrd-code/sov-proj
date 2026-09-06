# 01: Daily Simulation Slice

**What to build:** A running and paused sandbox with selectable speeds, daily state transitions, basic resource flows, and one facility producing observable output.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] The player can pause, resume, and select simulation speeds while the simulation resolves daily ticks.
- [x] A minimal facility consumes available inputs and produces observable daily output through the central simulation transition.
- [x] Pausing prevents state transitions without penalizing the player, and resuming continues from the same state.
- [x] Domain tests cover the externally observable daily transition behavior.
