# Animation work: current milestone and next steps

Version 0.1.13 extends the shared catalog to special startup, charge loops,
transitions, release and recovery. See [special animations](special-animations.md)
for phase coverage, safe effects and native props.
Normal donor poses and gameplay mechanics cover all twelve bodies and donors.
See [normal mechanics](normal-mechanics.md) for jab chains,
bounce, reflection and source attack movement.
The shared curve format, skeleton maps, preserved body proportions and native
verification are documented in [full-roster animations](full-roster-animations.md).
The [Mario report](mario-animations.md) and [three-move pilot](animation-retargeting-pilot.md)
record earlier milestones.

## What is complete

- Independent original donor normal collision paths, numeric attack values and
  donor clocks for all 396 resolved entries.
- Shared normal pose curves, angled variants, aerial landings and donor
  third/rapid jab phases on every body across all twelve skeletons.
- Native C playback/matrix comparisons, actual C retargeter checks for every
  clip/frame/body, per-player/lifecycle guards and linked ROM data verification.
- Body meshes, bone lengths, bind scales and TopN/facing remain native. Attack
  root travel uses the donor; collision reach stays independent of retargeted
  limb positions.
- Shared special phase poses, safe source effects/sounds, native field/Cutter/Falcon
  effects, separate blaster/tongue/Stone props and a collision-free held charge orb.

## Next work

1. **Rendered normal acceptance and rig polish.** Compare the custom body and
   vanilla donor on a flat stage with the same facing and world position. Check
   start, active frames, recovery, landing, hitlag and interrupts. Focus on compact
   Kirby/Jigglypuff/Pikachu skeletons, shoulders, feet and accessories. Record
   body/donor/move combinations; adjust rig maps only when the geometry supports
   it. Gameplay timing and hitbox reach take priority over visual convenience.
2. **Rendered special acceptance and polish.** Check native props/materials,
   charge/store/release, ground/air continuation, directional recovery and cleanup
   after damage/KO. Compare the donor alongside the custom body. Resolve compact
   skeleton issues, then add remaining voice/color/mesh polish without changing
   collision paths or phase clocks. Kirby copy remains outside this milestone.
3. **Tethers and paired throws.** Model reach, capture/release timing and both
   attacker/victim positions before adding animation choreography. Keep native
   identity and valid joint references; never attach raw foreign figatrees.

Every milestone updates the checklist/docs and produces a checked ROM/package.
Mesh-specific fixes must not restart or stretch the donor clock. Missing required
joints reject a pose before any partial write; optional attachments are skipped.
Keep all player state isolated and test two builds sharing the same body, stock
loss, scene changes, Training return and four assigned VS slots.
