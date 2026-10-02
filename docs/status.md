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

The [Remix creator guide](../remix/character_creator_guide.md) describes that
version's SRAM recipes, compiled roster and experimental adapters. Its moves
and animations do not have Character Lab's full donor timing/trajectory system.

## Future Remix port

- [ ] Port Character Lab's donor timing and collision paths to Remix.

This is feasible, but a substantial integration rather than a source-folder copy.
The original twelve fighters can reuse the generated donor data and conversion
tools. Remix needs assembly hooks for the independent move clock, safe attack
events and root-relative collision placement, integrated with its existing
creator adapters and gameplay patches. Its current normal adapter borrows raw
donor scripts while retaining body animation timing and bone placement.

Start with the original twelve behind Remix's existing Original 12 Only option,
then add animation pilots, grab/throw selections and special adapters. Extending
the same fidelity to Remix-exclusive fighters needs their own move, rig and
collision data, plus compatibility checks for their mechanics. The existing
Remix UI and saved recipes provide a useful starting point. No port is implemented
by the Training counter fix; Remix already has its own improved combo meter.

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
