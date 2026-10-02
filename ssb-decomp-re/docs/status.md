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
- [x] Neutral B choice: the body's move or Fox laser, with finite laser recovery on other bodies.
- [x] Existing Up B/Down B adapters, still experimental and needing more playtesting.
- [x] Assign builds to any human or CPU slot in VS, including two builds with the same body.
- [x] Training HITBOX view for attack and hurtbox outlines.
- [x] Return from a lab training test to the same build's editor.
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

- [ ] Original donor hitbox trajectories on every body for all normal attacks.
- [x] First collision-only milestone: Kirby up-tilt on DK and all other bodies.
- [x] Falcon down-air, Fox straight forward tilt and DK straight forward smash
  collision trajectories on all foreign bodies; animations remain Mario-only.
- [x] Native geometry checks, body-size/facing compensation and per-player lifecycle tests.
- [ ] Rendered acceptance of collision-only paths, actual hits/shields and interruptions.
- [ ] Grounded/aerial/angled/weapon/tail and multihit trajectory coverage.
- [ ] Validate donor startup, active frames, recovery, landing lag and hitlag in-game.
- [ ] Full donor jab-chain capabilities and repeat-hit/refresh behavior.
- [ ] Every donor attack animation on every body.
- [ ] Paired donor throw/victim choreography, including special capture mechanics.
- [ ] Tether grab reach, capture timing and visuals on other bodies.
- [ ] Neutral-special donor roster beyond Body Move/Fox Laser, excluding Kirby copy.
- [ ] Donor movement/physics and move-specific behavior such as Link's down-air bounce.
- [ ] Complete, consistent special-move compatibility across all bodies.
- [ ] Save creator presets across ROM restarts; currently they last for the running session.
- [ ] Wider emulator and real-hardware testing.
- [x] First public ROM/ZIP release published and downloaded/checksum verified.
- [ ] Configure the original-ROM source for automatic hosted ROM builds.

Priority: collision paths and timing first, then body animations, neutral specials,
and tether/paired capture mechanics. Keep the selected body's hurtboxes initially.

## Known rough edges

Most attacks still show the body's animation. That can look odd even when the donor's
numbers and timing are in use. Four donor attacks now use original collision paths
across bodies; other attacks still use mapped body joints. See the
[collision coverage and test guide](collision-trajectories.md). Throws keep body poses and release timing; changing
the donor does not yet reproduce its full choreography. Tether-grab animation/reach
and fighter-specific effects, movement or capture behavior are not universally copied.

The three animation pilots have automated numeric checks. The rest of the roster,
special adapters and transitions need more gameplay reports. You may run into bugs.

For a useful report, include the build/commit, emulator, body, donor, attack and steps
to reproduce it. A short clip helps. Ideas and casual feedback are welcome too.
