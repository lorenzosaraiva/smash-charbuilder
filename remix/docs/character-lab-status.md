# Character Lab on Remix checklist

Preview **0.1.3 (2026-10-05)** is a partial port into Smash Remix +EXTRA.
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
- [x] Borrowed-only imported special callbacks with native/expanded-fighter fallback and preserved Dark Samus initialization.
- [x] Independent Mario/Luigi steering and Falcon Kick slope angles; directional Fire Fox collision placement.
- [x] Donor air attributes through helpless fall and source landing clocks for eight recovery donors.
- [x] Donor-sized Reflector/PSI Magnet weapon and item collision volumes.
- [x] Source egg/Thunder/PK Thunder/Final Cutter positions and donor-relative Samus bomb placement.
- [x] Independent Tornado expenditure, held-egg/Spin Attack/Thunder ownership and Ness passive/trail state.
- [x] Held-weapon interruption cleanup and generation guards; released eggs relinquish ownership.
- [x] Final Cutter gameplay callbacks and Stone armor/hold/timeout without donor-only body mutations.
- [x] Suppress donor mesh/texture/hurtbox-part commands and attached motion effects on foreign bodies; retain whole-fighter hit status and native body hurtboxes.
- [x] Suspend missing-joint fallbacks during native status setup, preserving world-root position; restore safe callback fallbacks afterward.
- [x] Three Mario pose pilots: Falcon down-air, Fox straight forward tilt, DK straight forward smash.
- [x] Training exit and Training CSS Back return to the tested preset editor.
- [x] Native Settings menu style and built-in HITBOX/HITBOX+ display.
- [x] Existing improved combo meter handles grabs (enabled by default).
- [x] Existing character/Item Switch unlock patch retained.
- [x] Checked root build command, separate ROM/ZIP and source/checksum metadata.
- [ ] Rendered emulator acceptance: normals/contact, grabs, throws, laser, Training return and reloads.
- [ ] Rendered borrowed-special acceptance: Mario/Pikachu two dashes, position, size, landing and interruptions.
- [x] Link held-bomb common throw ownership, source clock/events, donor throw values and release socket.
- [x] Falcon Dive source attacker socket and frame-16 release, retaining the native extended-victim lookup.
- [ ] Rendered special steering, weapon contacts, reflection/absorption, self-launch, stage transitions and interruptions.
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
restoration and generation cleanup. Optional real-input CPU checks use isolated saves and null rendering. The
checked 0.1.3 ROM passes 24 primary Up/Down B casts across all twelve donors:
ten donors on Mario, and Mario/Luigi on Kirby, plus Link's common held-bomb
throw through a second Down B. Entry-position continuity, return to Idle
without KO, body scale and restored identity are checked. Rendered
steering/contact and broader body/stage coverage remain pending.
The movement batch checks 211 source geometry arrays, 1,804 Fox/Kirby momentum
samples, all 96 paths across eleven foreign bodies per donor, 4,756 native
special parser frames, 3,119 placements and 7,574 air-travel samples, plus native
air fallback and generation/attribute cleanup.
Special adapter checks add 22 Mario/Luigi steering/travel cases, 88 donor
helpless/landing/interruption/generation cases, 66 source socket/facing cases,
22 Reflector/Magnet volumes and 55 Fire Fox directional placements. They also
exercise held-egg interruption, Stone armor/timeout, four-port passive isolation
and native PC-relative branch fallback. Ninety-nine body-part/effect command
skips preserve native parts/hurtboxes and multiword script alignment. Paired special checks add 22 Link
ground/air throw contexts/clocks/sockets, 44 Dive socket adjustments through
the native-offset delegate and 11 frame-16 releases. Native item/effect/contact
setup is isolated in these checks. Every installed hook is checked in the ROM.

The Mario Kick/Quick Attack CPU regression also passes on this ROM: 72
source-velocity samples and two real-input zips, with the second aimed back
toward the platform, followed by native recovery without KO or scale leaks.
Controlled live Dive hitbox contact also passes native capture, paired release
and throw damage. CPU fixtures use null rendering and do not establish visible
pose or full contact fidelity.

The built ROM's N64 CRC is checked. Engine status setup, rendering, staling,
projectile/audio services are isolated in execution tests where documented.
Contact detection and visible in-game behavior still need playtesting.

The new SRAM revision resets older Remix recipes/settings once. Original-roster
donor tables use vanilla US values, matching Character Lab; Remix's gameplay
settings, modifiers, staling and collision engine still apply to the result.
