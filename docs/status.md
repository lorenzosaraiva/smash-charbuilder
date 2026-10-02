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
- [ ] Publish and verify the first public download.
- [ ] Automatic Remix ROM builds/releases.

## Gameplay

Character Lab's [detailed feature checklist](../ssb-decomp-re/docs/status.md)
covers normal attacks, grabs/throws, human/CPU assignments, Training HITBOX view,
the animation pilots and remaining work.

The [Remix creator guide](../remix/character_creator_guide.md) describes that
version's SRAM recipes, compiled roster and experimental adapters. Its moves
and animations do not have Character Lab's full donor timing/trajectory system.

Full donor hitbox trajectories and donor animations across all bodies are still
unfinished. The proposed DK + Kirby up-tilt work has not been implemented yet.
