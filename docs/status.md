# Done / not done

Checkboxes mean implemented, not tested in every matchup.

## Repository

- [x] Both creator codebases in one project repository.
- [x] Preserve both source histories and existing creator edits.
- [x] Root play/build documentation, changelog and issue forms.
- [x] Pinned build dependencies available through recursive clone.
- [x] Character Lab build command with checked ROM and ZIP in root `dist/`.
- [x] GitHub release workflow with fixed download filenames.
- [ ] Configure the original-ROM source for automatic hosted builds.
- [x] Publish and verify the first public download.
- [ ] Automatic Remix ROM builds/releases.

## Gameplay

Character Lab's [detailed feature checklist](../ssb-decomp-re/docs/status.md)
covers normal attacks, grabs/throws, human/CPU assignments, Training HITBOX view,
grab-preserving combo counters, full-roster normal animations and remaining work.

- [x] All twelve decomp donor normal animations on all twelve bodies, angled variants, aerial landings and supported jab phases.
- [x] Shared compact donor curves and body maps with native-source and linked-ROM checks.
- [x] Live ROM CPU checks: 132 foreign donor/body pairs, 15,248 poses, twelve editor returns and four assigned VS builds.
- [ ] Rendered animation/contact acceptance across the full roster.
- [ ] Borrowed special, tether and paired throw animations.

The [Remix guide](../remix/character_creator_guide.md) and
[port checklist](../remix/docs/character-lab-status.md) cover the separate preview.

## Character Lab neutral specials

- [x] Body Move and Fox Laser.
- [x] Mario/Luigi Fireball, Pikachu Thunder Jolt and Ness PK Fire on all original bodies.
- [x] Donor firing/recovery timing, native projectile collision values and donor spawn geometry.
- [x] Ground/air continuation, independent player state and duplicate/interruption guards.
- [x] Host adapter tests, native spawn geometry checks and linked-ROM verification.
- [ ] Rendered projectile/contact/reflect/absorb acceptance in Training and VS.
- [x] Falcon Punch and Jigglypuff Pound: dedicated hitbox and movement timelines.
- [x] DK Giant Punch and Samus Charge Shot: charge/store/release state.
- [x] Link Boomerang: return/catch lifecycle; Yoshi Egg Lay: paired capture state.
- [ ] Borrowed neutral animations, charge orb, donor effects/voices and victim rotation. Kirby copy remains outside this milestone.
- [ ] Port the ten new neutral adapters to Remix.
- [x] Fix Training/VS heap overflow using separate Expansion Pak memory (8 MB required).
- [x] Emulator CPU regression: twelve body/neutral choices, four preset returns, four-slot VS and the 4 MB launch guard (null rendering).

## Character Lab on Remix

- [x] Original-roster donor normal timing, collision paths and numeric values.
- [x] Grab/throw selectors, donor throw values and DK foreign forward release.
- [x] Body Move/Fox Laser and the three Mario animation pilots.
- [x] Borrowed-special idle/falling poses, original-roster phase clocks and recovery transform guards.
- [ ] Full special hitbox/projectile/capture fidelity and rendered two-dash acceptance.
- [x] Existing SRAM recipes and human/CPU assignments integrated with the port.
- [x] Training exit/CSS Back return to the tested editor.
- [x] Native hitbox display, improved grab-aware combo meter and unlocks retained.
- [x] Compiled MIPS execution, linked-data/CRC checks and separate ROM/ZIP packaging.
- [ ] Rendered emulator acceptance and contact/interrupt comparison.
- [ ] Full animation retargeting, broader neutral specials and tether choreography.
- [ ] Shared donor fidelity for Remix-exclusive fighters.

The port uses the same generated vanilla US donor data as Character Lab and
hooks Remix's native animation clock, motion parser and swept collision engine.
Original bodies keep native fighter data and hurtboxes. Expanded-roster creator
adapters remain legacy; their fidelity is a separate future effort.

## Gameplay order

- [x] Shared collision trajectories independent of visible body animations.
- [x] Complete normal-attack path catalog for all twelve donors and bodies,
  including angled variants, landing collisions and body-supported jab phases.
- [x] Direct donor/variant registry with shared trajectory data and loop handling.
- [x] Original animation/matrix checks for every resolved donor timeline.
- [ ] In-game comparison with vanilla donors, including contact and interruptions.

1. **Original normal-attack collisions and timing.** Reproduce donor hitbox paths
   and sizes relative to fighter position/facing, independent of body proportions.
   Full source coverage is implemented; finish rendered/gameplay acceptance.
2. **Donor animations on each body.** Use the collision clock for visible poses.
3. **Neutral specials, excluding Kirby's copy system.** Include projectiles,
   charging, movement, ground/air transitions and recovery.
4. **Tether grabs and paired throws.** Include reach, capture/release timing and
   attacker/victim positioning, followed by matching visuals.

Also track multihits/refresh rules, jab chains, aerial landing lag, hitlag and
interruption cleanup, donor movement and move-specific behavior such as Link's
down-air bounce. Body hurtboxes remain the initial policy.

Normal trajectory generation is complete. Visible animations, donor-specific
mechanics and in-game acceptance remain on the detailed checklist.

## Decomp Up/Down B timing fixes

- [x] Donor phase durations/loop boundaries and independent event clocks; safe idle/falling poses.
- [x] DK Down B startup/slap/recovery, four source hitboxes and queued repeat cycles.
- [x] Ness Up B weapon/wave/trail preloads and independent foreign-body passive state.
- [x] Host/native/linked-ROM checks and all-body ROM CPU regressions for DK slaps and Ness expiry.
- [x] DK Up B and Mario/Luigi Tornado: source collision positions/fields and donor aerial physics.
- [x] Falcon Kick: source collision paths and movement for all five phases.
- [x] Foreign Tornado state isolated from body passives; landing/respawn reset.
- [x] Ness source projectile socket and 28-tick self-launch gameplay clock.
- [x] Original C playback/matrix comparisons and packed-field/linked-pointer checks for all 20 new phases.
- [x] ROM CPU regressions across all twelve bodies: grounded/aerial spin, Tornado B-tap rise, Kick travel, Ness steering/controlled self-contact/recovery, editor returns and four-slot VS.
- [ ] Complete donor paths/sockets, movement and effects for every Up/Down B.
- [ ] Rendered contact, steering, self-launch, reflection and interruption acceptance.
