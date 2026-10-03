# What works, what is still a dream

This is a fun Smash 64 experiment for friends. Checkboxes mean implemented;
they do not mean every matchup has been playtested. Please share weird cases.

## Playable now

- [x] Four editable character builds with any of the twelve original fighter bodies.
- [x] Thirteen normal attack families: jab, dash attack, three tilts, three smashes and five aerials.
- [x] Donor damage, knockback, hitbox values and attack/recovery timing for normals.
- [x] Independent grab, forward-throw and back-throw selections.
- [x] Throw damage and knockback from the donor, with body capture/release animations.
- [x] Non-DK forward throws on DK release directly instead of entering cargo carry.
- [x] All eleven non-copy neutral donors plus Body Move, on every original body.
- [x] Four native projectile adapters with donor timing/spawn geometry and ground/air continuation.
- [x] Existing Up B/Down B adapters, still experimental and needing more playtesting.
- [x] Assign builds to any human or CPU slot in VS, including two builds with the same body.
- [x] Training HITBOX view for attack and hurtbox outlines.
- [x] Training combo count/damage survive capture, cargo carry and throw windup.
- [x] Return from a lab training test to the same build's editor.
- [x] Training/VS selection and match heaps use separate Expansion Pak memory (8 MB required).
- [x] Emulator CPU regression: twelve body/neutral choices, four preset returns, four-slot VS and the 4 MB launch guard (null rendering).
- [x] The four unlockable characters and Item Switch enabled.
- [x] Creator UI built with the game's existing font, colors and menu elements.
- [x] Local build command with ROM and play package under `dist/`.
- [x] GitHub build/release workflow prepared; needs the one-time setup in [releases.md](releases.md).

## Animation pilot

- [x] Mario body + Captain Falcon down-air poses and donor hitbox trajectory.
- [x] Mario body + Fox straight forward-tilt poses and donor hitbox trajectory.
- [x] Mario body + DK straight forward-smash poses and donor hitbox trajectory.
- [ ] Rendered emulator acceptance of all three pilot combinations.
- [ ] Angled tilt/smash animation variants.

## Still to do

- [x] Original donor hitbox trajectories on every body for all normal attacks.
- [x] Grounded/aerial/angled/weapon/tail and multihit trajectory coverage.
- [x] Landing collision paths and body-supported third/rapid-jab timelines.
- [x] Shared descriptor/fallback catalog for scripts, trajectories and verification.
- [x] Native geometry checks for all 293 resolved timelines and all 396 registry entries.
- [x] Body-size/facing compensation, per-player lifecycle and repeated-loop tests.
- [ ] Rendered acceptance of collision paths, actual hits/shields and interruptions.
- [ ] Validate donor startup, active frames, recovery, landing lag and hitlag in-game.
- [ ] Full donor jab-chain capabilities and repeat-hit/refresh behavior.
- [ ] Every donor attack animation on every body.
- [ ] Paired donor throw/victim choreography, including special capture mechanics.
- [ ] Tether grab reach, capture timing and visuals on other bodies.
- [x] Native projectile neutral first batch on all bodies/four player slots; eight donor pose/matrix checks.
- [ ] Rendered projectile contact, stage following, reflection/absorption and transition acceptance.
- [x] Falcon Punch/Pound hitbox and movement adapters.
- [x] DK/Samus charging, Link boomerang return/catch and Yoshi capture; Kirby copy excluded.
- [ ] Donor neutral animations across bodies.
- [ ] Donor movement/physics and move-specific behavior such as Link's down-air bounce.
- [ ] Complete, consistent special-move compatibility across all bodies.
- [ ] Save creator presets across ROM restarts; currently they last for the running session.
- [ ] Wider emulator and real-hardware testing.
- [ ] In-game acceptance of hit -> grab -> throw combo continuity and escape/reset.
- [x] First public ROM/ZIP release published and downloaded/checksum verified.
- [ ] Configure the original-ROM source for automatic hosted ROM builds.

Priority: collision paths and timing first, then body animations, neutral specials,
and tether/paired capture mechanics. Keep the selected body's hurtboxes initially.

## Known rough edges

Most attacks still show the body's animation. That can look odd even when the donor's
numbers and timing are in use. All normal donor choices now use original collision
paths across bodies, independently of those visible poses. See the
[collision coverage and test guide](collision-trajectories.md). Throws keep body poses and release timing; changing
the donor does not yet reproduce its full choreography. Tether-grab animation/reach
and fighter-specific effects, movement or capture behavior are not universally copied.

The three animation pilots have automated numeric checks. The rest of the roster,
special adapters and transitions need more gameplay reports. You may run into bugs.

For a useful report, include the build/commit, emulator, body, donor, attack and steps
to reproduce it. A short clip helps. Ideas and casual feedback are welcome too.

Training combo regression tests exercise the production counter update across all
twelve bodies, native/creator fighters and four player slots. They cover held and
throwing victims, release into hitstun, recovery, empty grabs, attacker/victim
distinction, independent player counters and vanilla resets outside Training.

## Decomp Up/Down B timing fixes

- [x] Donor phase durations/loop boundaries and independent event clocks; safe idle/falling poses.
- [x] DK Down B startup/slap/recovery, four source hitboxes and queued repeat cycles.
- [x] Ness Up B weapon/wave/trail preloads and independent foreign-body passive state.
- [x] Host/native/linked-ROM checks and all-body ROM CPU regressions for these two donors.
- [ ] Complete donor paths/sockets, movement and effects for every Up/Down B.
- [ ] Rendered contact, steering, self-launch, reflection and interruption acceptance.
