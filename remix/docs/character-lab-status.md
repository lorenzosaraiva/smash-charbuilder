# Character Lab on Remix checklist

Preview **0.1.12 (2026-10-07)** is a partial port into Smash Remix +EXTRA.
Checkboxes mean implemented and automatically checked, not playtested in every
matchup. Keep **Original 12 Only** enabled for the shared donor system.

See the [decomp-to-Remix matrix](decomp-port.md) for a full move/mechanics rundown.

- [x] Safe foreign normal effects and model commands; DK/Samus down smash recovers in both directions.
- [x] One Samus bomb per grounded/aerial Down B; phase resumes skip consumed spawn flags.
- [x] Donor aerial Down B availability, including Samus Bomb on DK's body; native DK's aerial move stays unavailable.
- [x] Weapon-count CPU checks on DK, Mario and native Samus, plus all-foreign-body event/timing regressions.
- [x] Samus Bomb's donor Morph Ball replacement, source window and interruption cleanup.
- [x] Samus tether's native glow at donor joint 23; paired visual resource preloads and cleanup.
- [x] Single-tap DK cycle checks; original two-slap cycle and explicitly requested repeats.
- [ ] Rendered Morph Ball and DK/Samus tether appearance, including four-player interruptions.

- [x] Mario taunt growth around the native body rest-height pivot.
- [x] All moves from body selects the explicit original Neutral B donor.
- [x] Reject unavailable donor aerial specials without executing body fallback.
- [x] Production MIPS preset, missing-entry and all-body taunt-pivot checks.
- [x] Real-input special contact, repeated-hitlag and transition/reset fixtures.
- [ ] Broader rendered special walls/slopes/ledges/interruptions acceptance; see [edge-case evidence](special-edge-cases.md).

- [x] Four named SRAM presets and per-human/CPU slot assignments.
- [x] Original twelve bodies and donors, all thirteen normal attack families.
- [x] Shared 396 normal definitions: damage, radius, element, angle and knockback.
- [x] Donor startup/active/clear/recovery timing independent of body animation.
- [x] Root-relative donor collision paths with body-size compensation.
- [x] Donor normal TransN movement/flag selection, including Fox dash and Kirby forward smash.
- [x] Angled variants, weapon/tail hitboxes, landing collision paths and supported jab phases.
- [x] Bounded rapid-jab loops, interruption cleanup and four independent player clocks.
- [x] Grab/forward-throw/back-throw donor selectors; donor numeric throw values.
- [x] Foreign DK forward throw enters donor cargo carry/toss phases.
- [x] Remix's extended throw-victim lookup retained.
- [x] Body-name/native and all eleven original neutral donors; Kirby copy excluded.
- [x] Borrowed original-roster specials use safe native status setup followed by shared donor poses.
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
- [x] Shared normal/supported special/recovery retargeting on twelve original bodies, with four bounded ROM caches.
- [x] Preserve the three Mario pose pilots: Falcon down-air, Fox straight forward tilt, DK straight forward smash.
- [x] Cutter sword/trails, Stone replacement, Falcon flames, blaster/tongue props and source-sized held charge orb.
- [x] Safe source visual/audio clocks; owned attachment, loop/voice and Stone visibility cleanup on interruptions/death/scene reset.
- [x] Independent source-prop/linked-MIPS checks, including four-port reset, plus real-input CPU allocation/recovery for Cutter/Stone, Punch/Kick, blaster, tongue and orb.
- [ ] Full rendered special attachment/pose acceptance and remaining actor-specific overlays/materials.
- [x] Editor Test initializes the chosen body, P1 and native Mario dummy with valid costumes.
- [x] Settings label uses **Character Lab** title case.
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
- [x] Shared normal/supported special/recovery pose retargeting on all twelve original bodies and donors.
- [x] Tether/grab/pull, paired throw/cargo/lift/fall/landing and taunt pose entry points.
- [x] Donor jab availability/buffering, third/rapid phases and source loop boundaries on original bodies.
- [x] Donor angle/landing availability, traction, gravity, terminal velocity and aerial drift during normals.
- [x] Link down-air contact bounce, fastfall cancellation, late-hit rewind and delayed rehit.
- [x] Ness bat source reflector flags/socket/size and native weapon/item reflection path.
- [x] Neutral selector shows fighter names; each build keeps its native body label and twelve choices.
- [ ] Rendered jab/bounce/bat contact, landing/Z-cancel, slopes and interruptions.
- [x] Fireballs/Jolt/PK Fire private weapon resources, source firing/recovery and ground/air continuation.
- [x] Punch/Pound source collision and momentum; Giant Punch/Charge Shot charge, storage and release.
- [x] Boomerang empty/return/catch lifecycle and Egg Lay source capture/release with native egg states.
- [x] Existing saved recipe bit layout preserved with four validated neutral choices in spare options bytes.
- [x] Null-rendering CPU scenes: all ten new neutrals plus Laser, charged storage/release, PK Fire flame contact and Egg Lay capture/egg damage on Mario/Kirby.
- [ ] Neutral rendered contact/reflect/absorb and broad stage/interrupt/attachment acceptance.
- [x] Donor tether/tongue reach and props, pull clocks, attacker/victim sockets/facing/release, DK cargo and Kirby landing throws.
- [ ] Rendered paired alignment/contact, slopes/edges, interruptions and native/expanded victim acceptance.
- [x] Twelve taunt donors, source poses/clocks/cancel flags/effects, Mario growth/shrink and Luigi damage.
- [x] Old preset fallback and all four full taunt choices saved without moving existing recipe bits.
- [ ] Rendered taunt mesh/effect acceptance and broader damage/KO interruption coverage.
- [ ] Yoshi starter build and four-stock/items-off VS defaults.
- [ ] Remix results/rematch regression with assigned builds.
- [ ] Donor trajectory/timing fidelity for Remix-exclusive fighters.
- [ ] Automatic hosted Remix builds/releases after each push.

**Verification:** shared production host tests; MIPS relocations and all
allocated runtime bytes; 657 shared data tables/poses; 4,048 foreign normal
variants and all 144 grab pairings; 14,226 native parser frames with 6,776 root
placements; 432 throw selections; laser frame 25/15 and recovery 55/45; all
sixteen player/preset assignments and all four Training return destinations.
Preview 0.1.7 adds forty normal entry guards, 528 jab-chain and 528 rapid-jab
cases, 132 donor-physics cases, 132 bounce/rehit cases, 132 bat-flag cases,
60 landing branches and 48 dynamic body-name labels. Bat placement/size on both
facings and both aerial-fastfall toggle routes are checked. Real-input CPU
scenes pass Fox/Link chains on Mario, Mario jab three on Kirby, Pikachu's repeat
on Yoshi, normal clip streaming/recovery and controlled Link down-air bounce.
These scenes use null rendering; rendered acceptance remains pending.
Special regressions execute Idle/Fall selection and transform guards on twelve
bodies/four ports, frozen dash and 46-frame end clocks, 235 donor phase
speed/loop/continuation cases, the native second-dash
update and endpoint position preservation. The direction predicate and second
dash status/render setup are isolated; this does not verify rendered movement.
Additional checks compare normal travel/special geometry to the source host
binaries and execute production movement/root-placement hooks, donor attribute
restoration and generation cleanup. Optional real-input CPU checks use isolated saves and null rendering. The
checked 0.1.3 ROM passed 24 primary Up/Down B casts across all twelve donors:
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

The Mario Kick/Quick Attack CPU regression also passes on preview 0.1.3: 72
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

The editor launch regression executes 48 production handlers across four
slots and twelve original bodies, checking scene initialization and the
Character Lab label; SRAM I/O and costume lookup are isolated there.
The optional `--editor-test --editor-slot 1` CPU fixture opens the real
Settings editor, poisons old Training selections, presses A on Test, waits
for a running CSS and returns with B (after recalling the selected puck).
`--editor-play` continues through real CSS Start and stage confirmation into
Training. These checks use null rendering; visible UI acceptance remains pending.

Preview 0.1.4 passes real-input Test/Back on all four editor slots with
stale Training selections, plus CSS Start/stage confirmation into a running
Training match. Kick/Quick Attack still passes 72 source-velocity samples and
the directional second zip. These CPU results use null rendering.

The 0.1.5 pose check passes 501 packed clips / 583,853 keys, 164,829 linked-MIPS
joint orientations on twelve rigs, 1,848 special selections, twelve callback-alias
world-root guards and four independent caches. Real-input CPU checks pass
Falcon normals on Mario/Kirby, Kirby normals on Yoshi, Falcon Kick source travel
and both Quick Attack zips/recovery. These checks use null rendering; visible
meshes, special props/effects and rendered contacts remain acceptance work.
