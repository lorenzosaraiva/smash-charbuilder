# Character Lab on Remix checklist

Preview **0.1.2 (2026-10-05)** is a partial port into Smash Remix +EXTRA.
Checkboxes mean implemented and automatically checked, not playtested in every
matchup. Keep **Original 12 Only** enabled for the shared donor system.

See the [decomp-to-Remix matrix](decomp-port.md) for a full move/mechanics rundown.

- [x] Four named SRAM presets and per-human/CPU slot assignments.
- [x] Original twelve bodies and donors, all thirteen normal attack families.
- [x] Shared 396 normal definitions: damage, radius, element, angle and knockback.
- [x] Donor startup/active/clear/recovery timing independent of body animation.
- [x] Root-relative donor collision paths with body-size compensation.
- [x] Donor normal TransN movement/flag selection, including Fox dash and Kirby forward smash.
- [x] Angled variants, weapon/tail hitboxes, landing collision paths and supported jab phases.
- [x] Bounded rapid-jab loops, interruption cleanup and four independent player clocks.
- [x] Grab/forward-throw/back-throw donor selectors; donor numeric throw values.
- [x] DK foreign forward throw releases directly instead of entering cargo.
- [x] Remix's extended throw-victim lookup retained.
- [x] Body Move/Fox Laser neutral selection with finite ground/air laser recovery.
- [x] Borrowed original-roster specials use body idle/falling poses instead of growing/displacing taunts.
- [x] Original-roster special phase clocks retain donor recovery/events, speed and frozen phases.
- [x] Retain recipes by actual body identity during borrowed special phases.
- [x] Compile 96 special source collision/travel phases; connect borrowed Up/Down B status events and root placements.
- [x] Source TransN special travel and donor attributes around native phase physics.
- [x] Source gameplay-duration overrides and fighter-generation clock/callback guards.
- [x] Foreign-body guards for Pikachu stretch and Fox/Ness recovery pitch.
- [x] Three Mario pose pilots: Falcon down-air, Fox straight forward tilt, DK straight forward smash.
- [x] Training exit and Training CSS Back return to the tested preset editor.
- [x] Native Settings menu style and built-in HITBOX/HITBOX+ display.
- [x] Existing improved combo meter handles grabs (enabled by default).
- [x] Existing character/Item Switch unlock patch retained.
- [x] Checked root build command, separate ROM/ZIP and source/checksum metadata.
- [ ] Rendered emulator acceptance: normals/contact, grabs, throws, laser, Training return and reloads.
- [ ] Rendered borrowed-special acceptance: Mario/Pikachu two dashes, position, size, landing and interruptions.
- [ ] Directional special collision transforms, spawn sockets and independent weapon/passive state.
- [ ] Coupled/capture mechanics and complete donor helpless/landing recovery.
- [ ] Full animation retargeting on every body and donor.
- [ ] Normal donor traction/air physics, landing behavior, jab availability, Link bounce and Ness bat reflection.
- [ ] Neutral specials beyond Body Move/Fox Laser; Kirby copy excluded.
- [ ] Donor tether/capture/paired-throw choreography and visuals.
- [ ] Custom taunts, Yoshi starter build and four-stock/items-off VS defaults.
- [ ] Remix results/rematch regression with assigned builds.
- [ ] Donor trajectory/timing fidelity for Remix-exclusive fighters.
- [ ] Automatic hosted Remix builds/releases after each push.

**Verification:** shared production host tests; MIPS relocations and all
allocated runtime bytes; 657 shared data tables/poses; 3,978 foreign normal
variants and all 144 grab pairings; 14,113 native parser frames with 6,701 root
placements; 432 throw selections; laser frame 25/15 and recovery 55/45; all
sixteen player/preset assignments and all four Training return destinations.
Special regressions execute Idle/Fall selection and transform guards on twelve
bodies/four ports, frozen dash and 46-frame end clocks, 235 donor phase
speed/loop/continuation cases, the native second-dash
update and endpoint position preservation. The direction predicate and second
dash status/render setup are isolated; this does not verify rendered movement.
Additional checks compare normal travel/special geometry to the source host
binaries and execute production movement/root-placement hooks, donor attribute
restoration and generation cleanup. The optional real-input CPU fixture targets
Mario using Falcon Kick and Pikachu Up B with isolated saves and null rendering.
The checked 0.1.2 ROM passes that CPU fixture, including 72 source Kick velocity
samples and an actual directional second Quick Attack dash, landing/recovery,
stable body scale and restored body identity. Rendered steering/contact and
broader body/stage coverage remain pending.
The movement batch checks 211 source geometry arrays, 1,804 Fox/Kirby momentum
samples, all 96 paths across eleven foreign bodies per donor, 4,756 native
special parser frames, 3,119 placements and 7,574 air-travel samples, plus native
air fallback and generation/attribute cleanup.
The built ROM's N64 CRC is checked. Engine status setup, rendering, staling,
projectile/audio services are isolated in execution tests where documented.
Contact detection and visible in-game behavior still need playtesting.

The new SRAM revision resets older Remix recipes/settings once. Original-roster
donor tables use vanilla US values, matching Character Lab; Remix's gameplay
settings, modifiers, staling and collision engine still apply to the result.
