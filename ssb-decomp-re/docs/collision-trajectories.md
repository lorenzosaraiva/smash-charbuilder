# Original donor collision paths

All normal donor attacks now follow their original collision paths independently
of the selected body's animated limbs. Generation and automated checks cover the
full original roster. Rendered emulator and real-hardware acceptance remain pending.

## Coverage

- All twelve donors on all eleven foreign original-roster bodies.
- All thirteen normal families: jab, dash, three tilts, three smashes, five aerials.
- Available angled variants, weapon and tail geometry, phased hits and multihits.
- Donor landing collisions and third/rapid-jab phases on every original body.
- Original radius, damage, angle, knockback, collision masks, groups, refresh and
  create/change/clear operations remain in the donor scripts.
- Startup, active windows and recovery use the donor clock; hitlag pauses it.

The 396 donor/variant definitions resolve to 293 distinct timelines, including
aliases, landing fallbacks, empty setup/end definitions and repeated-jab fallbacks.
237 of these have active collision paths. Missing native variants use the same
fallback as the event compiler. Vanilla/unassigned fighters and donor-equals-body
choices keep native behavior.

All original donor normal poses are retargeted to all twelve bodies. The body
keeps its hurtbox geometry and movement outside attacks. Donor jab chains,
Link's bounce, Ness's bat field and normal travel/physics are now implemented;
see [normal mechanics](normal-mechanics.md). Special effects and tether/paired
grab choreography remain separate work.

## Try it

1. Options -> Character Lab -> edit a build.
2. Choose any body and change a normal attack donor.
3. Test in Training -> Start -> View -> HITBOX.
4. Compare with the vanilla donor at the same fighter position and facing.

Two easy comparisons:

| Build | Donor clock samples | Recovery |
| --- | --- | --- |
| DK Body + Kirby Up Tilt | Two hitboxes active 4 through 11, clear at 12 | Ends at 18 |
| Kirby Body + Falcon Up Air | Two hitboxes active 5 through 13, clear at 14 | Ends at 34 |

These are source animation/script sample numbers, not a new convention for
counting player input frames. Hitboxes can visibly separate from the body pose.
The Falcon up-air retains 16 damage, radii 110/130 engine units and the original
angle phases (80, 361, then 20). Aerial landing selects the donor landing timeline
and stops applying the aerial path. Usual damage staling and victim weight apply.

Also compare Samus angled forward smashes, Link sword attacks, Pikachu tail
attacks, Luigi dash attack, multi-hit aerials and donor landing hits. Jab3/rapid
phases remain limited to the body's existing chain capabilities.

## One general converter

`tools/customMoveCatalog.py` resolves original motion descriptors and fallbacks
for both event compilation and trajectory generation. There is no body/donor-pair
allowlist. `tools/generateCustomCollisions.py` evaluates each resolved donor once
and generates a direct 12-by-33 registry. All bodies share those trajectory bytes.

The converter follows native `setup_parts`, enabled hidden joints, insertion order
and figatree traversal. It handles extra rotation channels, detached TransN
movement channels, Luigi's translation scaling, raw track-length adjustments,
and looping figatree interpolation. TransN displacement is excluded from the
root-relative center because fighter movement already supplies it.

Collision scheduling preserves source command order. A backwards absolute wait
can make later commands execute immediately, as in Luigi's dash-attack cleanup;
it cannot move a clear into an earlier frame or leave a stale head hitbox active.
Some attacks rely on status/animation-end cleanup rather than a script clear;
non-loop paths end at donor recovery and normal status transitions clear attacks.

Rapid-jab paths retain their first animation cycle and then repeat a verified
steady cycle. Donors without a rapid animation use their existing jab fallback.
Loop periods match the generated collision scripts, independently of the body's
visible animation loop.

Only the relevant frame ranges are stored. The full sampled catalog occupies
**140,452 bytes**, plus **7,920 bytes** for the registry. Lookup uses the current
normal definition's index, without scanning the catalog or allocating per-player
animation/skeleton buffers. Empty/no-hit definitions have no trajectory allocation.

Each center includes the donor's original size. The runtime attaches it to the
body's TopN with inverse body-size compensation, then the engine applies actor
position and facing. Body limb transforms cannot stretch or relocate these
centers. Radius, hit records, attack state and previous/current swept positions
remain owned by the normal engine collision code.

The existing per-player clock supports frozen frames, nonzero restart samples,
independent human/CPU players and shared presets. Owner/status/motion and
preset/scene guards stop interrupted or unrelated moves from using old data.

## Automated verification

- All **293 timelines** and **2,519,424 scalar animation samples** match original
  `ftAnimParseDObjFigatree` and native playback, including translation scaling.
  Maximum channel error: **0.0000076**.
- **5,322 active centers** match original `gmCollision` matrix/point transforms and an independent C
  event scheduler with native sync/async wait semantics.
  Maximum coordinate error: **0.0001569 engine units**.
- All **396 registry entries** and **5,236 stored active centers** match compiled
  samples and source scheduling; each float matches the converter exactly.
- **125,664 world positions** checked across all twelve real body sizes, both
  facings and a translated root. Maximum error: **0.0002441 engine units**.
- Runtime tests run all definitions on all foreign bodies through complete
  timelines and repeated rapid cycles. They preserve radius/damage/groups/state
  and swept history, check moved limbs, inactive frames, recovery, interruptions,
  hitlag-style frozen reads, nonzero starts and independent/shared player presets.
- Existing source checks retain all **808 original hitbox definitions**, including
  **511 tilt/smash definitions**, with original values and creation/clear commands.
- ROM checks verify linked trajectory bytes, registry pointers/metadata, donor
  scripts/timing, integrated processing and N64 CRC. CI checks regeneration.

The complete catalog adds **145,328 bytes** to the ROM/resident overlay relative
to the five-move release, with **no BSS growth**. The Training arena retains about
**1.74 MiB** before the framebuffer region. The checked ROM size and checksum are
recorded in the download's build metadata.

These are numeric/code checks, not rendered collision-detection acceptance.

## Still to test or implement

- [ ] In-game donor comparisons across small/large bodies, variants and both facings.
- [ ] Miss, hit, shield, hitlag, repeat hits, damage interruption and four-player/CPU matches.
- [ ] Aerial landing/cancellation and actual jab-chain transitions.
- [ ] Visible donor animation retargeting across the roster.
- [ ] Donor-specific movement, callbacks/effects and hurtbox behavior.
- [x] Projectile neutral first batch: Mario/Luigi Fireball, Thunder Jolt, PK Fire with donor timing and spawn geometry.
- [ ] Remaining neutral charge/melee/movement/return/capture adapters, excluding Kirby copy.
- [ ] Tether/paired grab and throw mechanics and choreography.

See [building](../../docs/building.md) for ROM/release commands and the
[checklist](status.md) for the remaining roadmap.
