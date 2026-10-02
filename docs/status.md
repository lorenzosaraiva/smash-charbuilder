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
the animation pilots and remaining work.

The [Remix creator guide](../remix/character_creator_guide.md) describes that
version's SRAM recipes, compiled roster and experimental adapters. Its moves
and animations do not have Character Lab's full donor timing/trajectory system.

## Gameplay order

- [x] Shared collision trajectories independent of visible body animations.
- [x] Kirby up-tilt, Falcon down-air, Fox straight forward tilt and DK straight
  forward smash trajectories on all other original-roster bodies.
- [ ] In-game comparison with vanilla donors, including contact and interruptions.
- [ ] Expand original trajectories to every normal attack and variant.

1. **Original normal-attack collisions and timing.** Reproduce donor hitbox paths
   and sizes relative to fighter position/facing, independent of body proportions.
   Start with DK using Kirby's up-tilt, then expand across bodies and attacks.
2. **Donor animations on each body.** Use the collision clock for visible poses.
3. **Neutral specials, excluding Kirby's copy system.** Include projectiles,
   charging, movement, ground/air transitions and recovery.
4. **Tether grabs and paired throws.** Include reach, capture/release timing and
   attacker/victim positioning, followed by matching visuals.

Also track multihits/refresh rules, jab chains, aerial landing lag, hitlag and
interruption cleanup, donor movement and move-specific behavior such as Link's
down-air bounce. Body hurtboxes remain the initial policy.

Full trajectory and animation coverage remains unfinished. See the detailed
checklist for implementation coverage and pending in-game acceptance.
