# Remaining special mechanics

Version 0.1.11, updated 2026-10-04. Decomp only; the Remix preview is unchanged.

The gameplay adapters cover the twelve original bodies. They use native US
status, weapon, item and capture code together with generated donor event clocks,
collision paths and sockets. Body proportions do not change donor attack reach.
The chosen body keeps its hurtboxes, jump inventory and movement outside specials.
Version 0.1.13 adds shared retargeted phase poses and safe effects/props. See
[special animations](special-animations.md); rendered acceptance is pending.

## Controls and behavior

Select a donor in the editor's **Up B** or **Down B** row, then choose
**Test in Training**. Use **Start -> View -> HITBOX** to see collisions.

| Move | Implemented gameplay |
| --- | --- |
| Link Down B | Native held bomb, fuse/explosion and pickup behavior; 45-frame ground/air creation action. Down B with a held bomb uses Link's common toss: release on frame 8, 24-frame grounded / 35-frame aerial action, source hand socket and Link's throw velocity/damage scales. Other ordinary item-throw inputs remain body actions. |
| Samus Down B | Native bomb factory, collision/explosion and bomb jump; source spawn event, 57-frame ground/air clocks, donor position and native movement flags. |
| Yoshi Up B | Native held egg, B-hold charge, stick direction, release, gravity, explosion and cleanup. The source 72-frame action and joint-3 socket drive events; the held egg has independent ownership on foreign bodies. |
| Pikachu Down B | Native Thunder head/trails and owner contact; source horizontal socket, stage-ceiling spawn offset, falling speed, contact box and recovery. Pikachu Model is preloaded for native trail effects. Foreign ownership/destruction state survives common status-union overwrites safely. |
| Fox Up B | Original 8-frame startup, 35-tick charge counter, directional launch, 30-tick travel, deceleration, stage callbacks and donor recovery. Source hitbox positions rotate around Fox's pitch pivot with launch direction. Hold the desired stick direction through launch. |
| Pikachu Up B | Native 20-tick startup, 5-tick zip, directional movement, second-zip gate, speed reduction, wall/platform/ledge callbacks and donor recovery. Change direction during the zip window for a second zip; the native minimum direction change is 42 degrees. No third zip. |
| Fox Down B | Native startup hit, held reflection, ownership handoff, turning, release and 18-tick minimum hold. The field follows the donor socket and radius rather than the body joint. Hold B to keep it active. |
| Ness Down B | Native absorbability rules, held field, hit/recovery state and healing: twice absorbed projectile damage, clamped at zero percent. The donor field bypasses body hurtbox broad-phase culling, then uses the original special collision test. Hold B to keep it active. |
| Jigglypuff Up B | Original 180-frame Sing action, sleep collision element, changing radii and native ground/air victim rules. Native singing effects are enabled on foreign bodies. |
| Falcon Up B | Native flight, catch/release callbacks, captured-victim state and donor catch socket; source throw descriptors preserve capture/release damage and knockback. Successful release restores the native reusable recovery behavior. Victims retain native body capture poses. |
| Kirby Up B | Source ascent/descent hit paths, native movement and stage transitions, landing beam and recovery. Its native 0.8 aerial travel multiplier is applied without resizing the foreign body's root. Native Cutter draw/up/down/trail effects use safe visual attachments. |
| Kirby Down B | Stone is selectable on all bodies. Native fall/landing/slide/release, 38% US armor with spill damage, 18-tick minimum hold and 160-tick timeout. Tap B after the minimum to release early. The native Stone mesh is drawn separately on foreign bodies; armor-color polish is pending. |
| Yoshi Down B | Source startup/landing paths and travel, native falling state and landing-star weapon behavior. Included in this batch's regression coverage. |

## Timing and lifecycle

The generated registry contains **99 donor phase clocks** and **96 collision,
travel or socket phases**, including Link's two common bomb-toss actions.
DK's dedicated hand-slap trajectory remains separate. The generator merges
parallel event streams and stops at native pause instructions; it does not let
an animation loop replay a one-shot gameplay event.

Thunder's short looping pose must not restart its gameplay script before its
frame-60 timeout. Its foreign loop/hit clocks span 61/31 frames. PSI Magnet's
four-frame hit pose similarly carries a 16-frame gameplay script. Fire Fox and
Stone keep their native action counters independently of pose length.

Held egg and Thunder pointers live outside the fighter's common status union.
Damage, capture and Training reset can overwrite that union before changing
status. Cleanup uses owner/player-generation guards and native destruction
callbacks; a respawn cannot inherit another fighter's weapon state. A consumed
Thunder head drops its owned reference before its GObj can be recycled.

Stage selection now uses the Expansion Pak arena too. This prevents the enlarged
shared gameplay overlay from overrunning its previous stage-menu heap.

## Verification and remaining acceptance

- `testSpecialTiming.py`: production clocks/accessors across twelve bodies,
  four slots and both facings, with loop, transition and generation checks.
- `testRemainingSpecials.py`: production callback checks for Fire Fox/Quick Attack,
  second-zip gating, reflection ownership, PSI healing, egg lifecycle, Thunder
  contact/cleanup, Stone armor/release, Falcon Dive capture/release, Cutter scale
  preservation and Link bomb throw values. Resource factories/maps are host
  fixtures; this does not replace live projectile tests.
- `testNativeAnimation.py`: original C animation playback/matrices versus every
  generated path, active mask, travel delta and socket.
- `verifyCustomMoveRom.py`: original packed event fields, throw descriptors,
  linked pointers, runtime code and N64 CRC in the built ROM.
- Optional Linux `testTrainingScenes.py --mechanic ID --mechanic-kind hi|lw`:
  actual menu/input/CPU execution with ground/air casts, source hit fields/centers,
  native projectile creation, recovery, reset, editor return and four-slot VS.
  It uses null rendering. `--falcon-contact` places the CPU in the live catch volume;
  `--thunder-contact` places the live head in the owner-contact box. These
  controlled fixtures check native contact/release branches, rather than natural
  approach/steering. IDs: Fox 1, Samus 3, Link 5, Yoshi 6, Falcon 7,
  Kirby 8, Pikachu 9, Jigglypuff 10, Ness 11. See [emulator setup](neutral-specials.md).

- [x] Native mechanics, donor clocks/paths/sockets and interruption-safe ownership.
- [x] Host/source geometry and linked-ROM verification.
- [x] Live CPU coverage: thirteen specials on twelve bodies, 312 ground/air
  casts, reset/editor return and four-slot VS. Controlled Falcon Dive capture/throw
  and Thunder head placement exercise contact branches; natural contact and
  rendered acceptance remain separate checks.
- [x] Final ROM startup regression: all nineteen opening scenes, title/main menu,
  4 MB Training guard, Mario/Ness Up B and four Mario normal-animation catalogs.
- [ ] Rendered contact/shield comparisons, reflected/absorbed projectile scenarios,
  Sing victim transitions, Falcon Dive contacts, bomb jumps, slopes, platforms,
  ledges and damage interruptions across bodies/stages.
- [x] Shared special phase poses, native Stone prop and safe charge/field/Cutter effects.
- [ ] Complete voice/color and rendered accessory polish.
- [ ] Port this mechanics batch to Remix.

Kirby's Neutral B copy system and tether-grab/ordinary paired-throw choreography
remain separate milestones. Gameplay coverage is implemented; full visual and
stage/contact acceptance is still open. Report the build, emulator, body, donor
and steps when a combination behaves differently from vanilla.
