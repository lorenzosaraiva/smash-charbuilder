# Character Lab on Remix checklist

This preview ports our current original-roster features into Smash Remix +EXTRA.
Checkboxes mean implemented and automatically checked, not playtested in every
matchup. Keep **Original 12 Only** enabled for the shared donor system.

- [x] Four named SRAM presets and per-human/CPU slot assignments.
- [x] Original twelve bodies and donors, all thirteen normal attack families.
- [x] Shared 396 normal definitions: damage, radius, element, angle and knockback.
- [x] Donor startup/active/clear/recovery timing independent of body animation.
- [x] Root-relative donor collision paths with body-size compensation.
- [x] Angled variants, weapon/tail hitboxes, landing collision paths and supported jab phases.
- [x] Bounded rapid-jab loops, interruption cleanup and four independent player clocks.
- [x] Grab/forward-throw/back-throw donor selectors; donor numeric throw values.
- [x] DK foreign forward throw releases directly instead of entering cargo.
- [x] Remix's extended throw-victim lookup retained.
- [x] Body Move/Fox Laser neutral selection with finite ground/air laser recovery.
- [x] Borrowed original-roster specials use body idle/falling poses instead of growing/displacing taunts.
- [x] Original-roster special phase clocks retain donor recovery/events, speed and frozen phases.
- [x] Foreign-body guards for Pikachu stretch and Fox/Ness recovery pitch.
- [x] Three Mario pose pilots: Falcon down-air, Fox straight forward tilt, DK straight forward smash.
- [x] Training exit and Training CSS Back return to the tested preset editor.
- [x] Native Settings menu style and built-in HITBOX/HITBOX+ display.
- [x] Existing improved combo meter handles grabs (enabled by default).
- [x] Existing character/Item Switch unlock patch retained.
- [x] Checked root build command, separate ROM/ZIP and source/checksum metadata.
- [ ] Rendered emulator acceptance: normals/contact, grabs, throws, laser, Training return and reloads.
- [ ] Rendered borrowed-special acceptance: Mario/Pikachu two dashes, position, size, landing and interruptions.
- [ ] Donor special collision paths, projectile placement and coupled/capture mechanics.
- [ ] Full animation retargeting on every body and donor.
- [ ] Donor-specific movement/physics, landing behavior, jab availability and other mechanics.
- [ ] Neutral specials beyond Body Move/Fox Laser; Kirby copy excluded.
- [ ] Donor tether/capture/paired-throw choreography and visuals.
- [ ] Donor trajectory/timing fidelity for Remix-exclusive fighters.
- [ ] Automatic hosted Remix builds/releases after each push.

**Verification:** shared production host tests; MIPS relocations and all
allocated runtime bytes; 657 shared data tables/poses; 3,978 foreign normal
variants and all 144 grab pairings; 14,113 native parser frames with 6,701 root
placements; 432 throw selections; laser frame 25/15 and recovery 55/45; all
sixteen player/preset assignments and all four Training return destinations.
Special regressions execute Idle/Fall selection and transform guards on twelve
bodies/four ports, frozen dash and 46-frame end clocks, 234 donor phase
speed/loop/continuation cases, the native second-dash
update and endpoint position preservation. The direction predicate and second
dash status/render setup are isolated; this does not verify rendered movement.
The built ROM's N64 CRC is checked. Engine status setup, rendering, staling,
projectile/audio services are isolated in execution tests where documented.
Contact detection and visible in-game behavior still need playtesting.

The new SRAM revision resets older Remix recipes/settings once. Original-roster
donor tables use vanilla US values, matching Character Lab; Remix's gameplay
settings, modifiers, staling and collision engine still apply to the result.
