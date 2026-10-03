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
grab-preserving combo counters, the animation pilots and remaining work.

The [Remix guide](../remix/character_creator_guide.md) and
[port checklist](../remix/docs/character-lab-status.md) cover the separate preview.

## Character Lab on Remix

- [x] Original-roster donor normal timing, collision paths and numeric values.
- [x] Grab/throw selectors, donor throw values and DK foreign forward release.
- [x] Body Move/Fox Laser and the three Mario animation pilots.
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
