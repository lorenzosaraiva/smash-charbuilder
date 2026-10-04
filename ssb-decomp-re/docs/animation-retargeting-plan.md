# Animation work: current milestone and next steps

Version 0.1.7 implements normal donor poses for all twelve bodies and donors.
The shared curve format, skeleton maps, preserved body proportions and native
verification are documented in [full-roster animations](full-roster-animations.md).
The [Mario report](mario-animations.md) and [three-move pilot](animation-retargeting-pilot.md)
record earlier milestones.

## What is complete

- Independent original donor normal collision paths, numeric attack values and
  donor clocks for all 396 resolved entries.
- Shared normal pose curves, angled variants, aerial landings and body-supported
  third/rapid jab phases across all twelve skeletons.
- Native C playback/matrix comparisons, actual C retargeter checks for every
  clip/frame/body, per-player/lifecycle guards and linked ROM data verification.
- Body meshes, bone lengths, bind scales, TopN/facing and detached TransN physics
  remain native. Collision reach is independent of retargeted limb positions.

## Next work

1. **Rendered normal acceptance and rig polish.** Compare the custom body and
   vanilla donor on a flat stage with the same facing and world position. Check
   start, active frames, recovery, landing, hitlag and interrupts. Focus on compact
   Kirby/Jigglypuff/Pikachu skeletons, shoulders, feet and accessories. Record
   body/donor/move combinations; adjust rig maps only when the geometry supports
   it. Gameplay timing and hitbox reach take priority over visual convenience.
2. **Neutral animations, excluding Kirby copy.** Reuse shared curves and body
   maps for ground/air startup, charging/holding, release and recovery. Keep the
   existing projectile/socket/capture/charge adapters and their phase clocks.
   Begin with simple Punch/Pound/projectile poses; handle charge loops and paired
   Egg Lay captures separately. Validate native playback before enabling clips.
3. **Remaining Up/Down B and special motion.** Add phase poses to the existing
   safe adapters without importing foreign fighter callbacks or passive unions.
   Preserve donor travel/timing and keep root displacement from being applied
   both cosmetically and physically. Add missing gameplay paths/effects separately.
4. **Tethers and paired throws.** Model reach, capture/release timing and both
   attacker/victim positions before adding animation choreography. Keep native
   identity and valid joint references; never attach raw foreign figatrees.

Every milestone updates the checklist/docs and produces a checked ROM/package.
Mesh-specific fixes must not restart or stretch the donor clock. Missing required
joints reject a pose before any partial write; optional attachments are skipped.
Keep all player state isolated and test two builds sharing the same body, stock
loss, scene changes, Training return and four assigned VS slots.
