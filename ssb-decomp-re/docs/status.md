# What works, what is still a dream

This is a fun Smash 64 experiment for friends. Checkboxes mean implemented;
they do not mean every matchup has been playtested. Please share weird cases.

## Playable now

- [x] Four editable character builds with any of the twelve original fighter bodies.
- [x] Thirteen normal attack families: jab, dash attack, three tilts, three smashes and five aerials.
- [x] Donor damage, knockback, hitbox values and attack/recovery timing for normals.
- [x] Independent grab, forward-throw and back-throw selections.
- [x] Donor grab/throw timing, paths, numeric values, capture anchors and native victim queues.
- [x] Non-DK forward throws on DK release directly instead of entering cargo carry.
- [x] All eleven non-copy neutral donors plus Body Move, on every original body.
- [x] Four native projectile adapters with donor timing/spawn geometry and ground/air continuation.
- [x] Existing Up B/Down B adapters, still experimental and needing more playtesting.
- [x] Assign builds to any human or CPU slot in VS, including two builds with the same body.
- [x] Training HITBOX view for attack and hurtbox outlines.
- [x] Training combo count/damage survive capture, cargo carry and throw windup.
- [x] Return from a lab training test to the same build's editor.
- [x] Training/VS selection and match heaps use separate Expansion Pak memory (8 MB required).
- [x] Fix cold-boot opening-room overflow; all nineteen intro scenes use Expansion Pak memory.
- [x] Uninterrupted CPU boot through all nineteen intro scenes, title and Start into the main menu (null rendering).
- [x] Emulator CPU regression: twelve body/neutral choices, four preset returns, four-slot VS and the 4 MB launch guard (null rendering).
- [x] The four unlockable characters and Item Switch enabled.
- [x] Creator UI built with the game's existing font, colors and menu elements.
- [x] Local build command with ROM and play package under `dist/`.
- [x] GitHub build/release workflow prepared; needs the one-time setup in [releases.md](releases.md).

## Normal animations across the roster

- [x] Mario body + Captain Falcon down-air poses and donor hitbox trajectory.
- [x] Mario body + Fox straight forward-tilt poses and donor hitbox trajectory.
- [x] Mario body + DK straight forward-smash poses and donor hitbox trajectory.
- [ ] Rendered emulator acceptance of all three pilot combinations.
- [x] Fox/DK/Luigi/Falcon normal attack families and angled tilt/smash variants on Mario.
- [x] Aerial landing poses and Falcon/Luigi third jabs on Mario.
- [x] Shared compact clips, native-source orientation checks and guarded per-player playback.
- [x] ROM CPU pose checks for all four Mario donors, editor returns and four-Mario VS loading (null rendering).
- [x] All twelve donor normal catalogs on all twelve bodies through shared curves and semantic rig maps.
- [x] Native C donor playback versus actual runtime orientations for every clip/frame/body.
- [x] Live ROM CPU checks: 132 foreign donor/body pairs, 15,248 poses, twelve editor returns and four assigned VS builds.
- [ ] Rendered acceptance of the full catalog and mesh-specific polish.

See the [full-roster animation guide](full-roster-animations.md); the
[Mario expansion report](mario-animations.md) documents the preceding milestone.

## Still to do

- [x] Original donor hitbox trajectories on every body for all normal attacks.
- [x] Grounded/aerial/angled/weapon/tail and multihit trajectory coverage.
- [x] Landing collision paths and donor third/rapid-jab timelines on every body.
- [x] Shared descriptor/fallback catalog for scripts, trajectories and verification.
- [x] Native geometry checks for all 293 resolved timelines and all 396 registry entries.
- [x] Body-size/facing compensation, per-player lifecycle and repeated-loop tests.
- [ ] Rendered acceptance of collision paths, actual hits/shields and interruptions.
- [ ] Validate donor startup, active frames, recovery, landing lag and hitlag in-game.
- [x] Full donor jab-chain availability, input buffering, rapid thresholds and repeat-hit/refresh timelines on all original bodies.
- [x] Every donor normal attack animation on every body.
- [x] Shared phase animations for all implemented neutral/Up B/Down B adapters on every body, including charge loops and recovery.
- [x] Shared donor grab/throw attacker poses on every body; donor-selected native victim phases.
- [x] Paired positioning/release, DK cargo carry and Kirby lift/fall/landing throw mechanics.
- [x] Link/Samus/Yoshi donor tether reach/timing and native hook/beam/tongue props.
- [ ] Rendered tether/paired contact, victim alignment, slopes/edges and interruption acceptance.
- [x] Native projectile neutral first batch on all bodies/four player slots; eight donor pose/matrix checks.
- [ ] Rendered projectile contact, stage following, reflection/absorption and transition acceptance.
- [x] Falcon Punch/Pound hitbox and movement adapters.
- [x] DK/Samus charging, Link boomerang return/catch and Yoshi capture; Kirby copy excluded.
- [x] Donor neutral startup/charge/release/recovery poses across bodies.
- [x] Safe native Reflector/Sing/PSI Magnet/Final Cutter/Falcon effects and separate blaster/tongue/Stone props and charge orb.
- [ ] Rendered acceptance and complete voice/color/accessory polish for specials.
- [x] Donor normal movement/physics, angled/landing availability, Link down-air bounce and Ness bat reflection.
- [ ] Complete, consistent special-move compatibility across all bodies.
- [ ] Save creator presets across ROM restarts; currently they last for the running session.
- [ ] Wider emulator and real-hardware testing.
- [ ] In-game acceptance of hit -> grab -> throw combo continuity and escape/reset.
- [x] First public ROM/ZIP release published and downloaded/checksum verified.
- [ ] Configure the original-ROM source for automatic hosted ROM builds.

Priority: collision paths and timing first, then body animations, neutral specials,
and tether/paired capture mechanics. Keep the selected body's hurtboxes initially.

## Known rough edges

Normal attacks now show body-adapted donor poses. Compact bodies merge some
semantic joints; accessories keep native bind poses and no foreign weapon mesh
is added. Donor reach remains independent of limb length, so hitboxes may extend
beyond a small body's limbs. See the
[collision coverage and test guide](collision-trajectories.md). Grabs and throws use donor paths, clocks and capture anchors, with shared
attacker poses and native victim rigs. Bodies of different sizes can still intersect
visually while retaining original donor reach. Rendered tether materials, victim
alignment and stage/contact/interruption acceptance remain pending. See
[paired grabs and throws](paired-grabs-and-throws.md).

All twelve normal catalogs and bodies have automated numeric checks. Rendered
appearance, special adapters and transitions need more gameplay reports. You may
run into bugs.

For a useful report, include the build/commit, emulator, body, donor, attack and steps
to reproduce it. A short clip helps. Ideas and casual feedback are welcome too.

Training combo regression tests exercise the production counter update across all
twelve bodies, native/creator fighters and four player slots. They cover held and
throwing victims, release into hitstun, recovery, empty grabs, attacker/victim
distinction, independent player counters and vanilla resets outside Training.

## Decomp Up/Down B timing fixes

- [x] Link Spin Attack source paths and full ground/air gameplay, grounded attack weapon and 40-frame ending.
- [x] Samus Screw Attack source paths, distinct ground/air physics and hit sequences, startup intangibility and recovery.
- [x] Jigglypuff Rest one-frame hit, original damage/knockback/radius, invulnerability and uninterrupted 250-frame sleep.
- [x] Donor friction/air limits, Link/Samus recovery attributes and source landing lengths.
- [x] Production native-versus-borrowed callback/physics/weapon lifecycle checks across twelve bodies, four slots and both facings.
- [x] Live ROM CPU checks for all three donors on all twelve bodies: 72 ground/air starts, reset/editor return and four-slot VS loading.
- [ ] Rendered contact, platform/ledge and damage-interruption acceptance for Spin Attack, Screw Attack and Rest.
- [x] Mario/Luigi Up B source collision paths, distinct hit phases, travel/steering, ground/air timing and donor helpless/landing recovery.
- [x] Native-versus-borrowed Mario/Luigi physics and recovery checks across all bodies/slots, with interruption and respawn guards.
- [x] Live ROM CPU checks for both Up B donors on all twelve bodies: ground/air hit fields, foreign source centers, recovery, reset/editor return and four-slot VS.
- [ ] Rendered Mario/Luigi Up B sweetspot/multihit contact, platforms, ledges and interruptions.
- [x] Donor phase durations/loop boundaries and independent event clocks; shared donor poses.
- [x] DK Down B startup/slap/recovery, four source hitboxes and queued repeat cycles.
- [x] Ness Up B weapon/wave/trail preloads and independent foreign-body passive state.
- [x] Host/native/linked-ROM checks and all-body ROM CPU regressions for DK slaps and Ness expiry.
- [x] DK Up B and Mario/Luigi Tornado: source collision positions/fields and donor aerial physics.
- [x] Falcon Kick: source collision paths and movement for all five phases.
- [x] Foreign Tornado state isolated from body passives; landing/respawn reset.
- [x] Ness source projectile socket and 28-tick self-launch gameplay clock.
- [x] Original C playback/matrix comparisons and packed-field/linked-pointer checks for all 96 collision/travel/socket phases.
- [x] ROM CPU regressions across all twelve bodies: grounded/aerial spin, Tornado B-tap rise, Kick travel, Ness steering/controlled self-contact/recovery, editor returns and four-slot VS.
- [x] Remaining special mechanics: bombs/eggs/Thunder, Fire Fox/Quick Attack, Reflector/PSI Magnet/Sing, Falcon Dive, Final Cutter and Stone on original bodies.
- [x] Link held-bomb Down B toss keeps source release timing, socket and throw values.
- [x] Donor reflection/absorption fields; native ownership and PSI healing rules.
- [x] Independent held egg/Thunder ownership and interruption/generation cleanup; required Thunder trail models preloaded.
- [x] Stone selection, native US armor/minimum hold/timeout; Cutter travel without body rescaling.
- [x] 99 donor clocks and 96 source collision/travel/socket phases, original-C geometry and linked-ROM checks.
- [x] Production callback checks across twelve bodies/four slots for movement, zip gate, ownership, healing, capture/release, armor and bomb throw values.
- [x] Live CPU checks for thirteen donor specials on all twelve bodies: 312 ground/air casts, native projectile creation, recovery, reset/editor return and four-slot VS; controlled Falcon Dive capture/throw and Thunder owner contact included (null rendering).
- [ ] Rendered projectile/contact, sleep/capture, slopes/ledges, interruption and visual acceptance across bodies and stages.
- [x] Retarget implemented special phases, charge loops and recovery; add semantic effects and native props.
- [ ] Port this special mechanics/animation batch to Remix.
- [ ] Rendered contact, steering, self-launch, reflection and interruption acceptance.

## Decomp normal-specific mechanics

- [x] Donor jab chains, third/rapid phases, source buffering and native loop endings on every original body.
- [x] Pikachu repeats jab one; Jigglypuff retains its native two-jab chain (unused rapid descriptors stay unreachable).
- [x] Link down-air contact bounce, fastfall cancellation, late-hit rewind and 30-tick rehit timer.
- [x] Ness bat source reflector window/socket/size and native projectile/item reflection.
- [x] Donor root travel, attack traction/air physics, angled variants and landing fallback selection.
- [x] Donor part-intangibility timing mapped onto native body hurtboxes; body script suppression and status cleanup.
- [x] Training/VS 512-entry asset caches for all twelve selected donor files.
- [x] Production callbacks on twelve donors/bodies/four slots and all 396 movement records verified in the ROM.
- [x] Live ROM CPU checks: all 144 donor/body jab chains, twelve controlled Link
  bounces and Ness bat reflections, editor returns and four assigned VS builds.
- [ ] Rendered contact/shield, slopes/edges, interruptions and part-intangibility acceptance.
- [ ] Normal mesh/effect/audio polish and port this mechanics batch to Remix.

See the [normal mechanics guide](normal-mechanics.md).

## Decomp tether grabs and paired throws

- [x] All twelve donor grab and forward/back throw choices retain independent source clocks.
- [x] Link hook/rope, Samus beam and Yoshi tongue use source reach, windows and native props.
- [x] Full donor capture matrices include animated scale and preserve each victim's own rig.
- [x] Donor release flags, throw descriptors, facing changes and native victim status pairs.
- [x] DK carry/walk/turn/jump/fall/landing/damage/toss and Kirby lift/fall/landing callbacks.
- [x] Per-player ownership/generation guards, original-C geometry and linked-ROM checks.
- [x] Paired ROM CPU checks: 24 foreign and 24 native forward/back releases, donor reach/ticks/damage, live victim positions and DK mash escape (null rendering).
- [ ] Rendered contact, materials, compact-body intersections, slopes/edges and damage/escape acceptance.
- [ ] Port this paired mechanics/animation batch to Remix.

See [controls and verification](paired-grabs-and-throws.md).
