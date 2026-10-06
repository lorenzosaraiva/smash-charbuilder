# Donor normal mechanics

Decomp implementation since version 0.1.17 (2026-10-05). Remix preview 0.1.6
also ports these normal mechanics; see its [guide and checks](../../remix/docs/normal-mechanics.md).

Customized grabs retain native release descriptors and choreography. The VS
regression also caught an Egg Lay interruption crash: the adapter now installs
Yoshi's original throw/escape descriptors before a capture can begin.

Normal attacks use the selected donor for gameplay as well as poses, hitbox
paths and event timing. The body keeps its hurtbox shapes, weight, jump inventory
and movement outside the attack. Matching donor/body and unassigned fighters
remain native.

## Jab chains

The Jab row selects the whole donor chain on every original body. It preserves
the original follow-up windows, input buffering, rapid-jab thresholds, hit groups,
refresh events, loop periods and ending. Body support no longer limits the chain.

| Donor | Native chain |
| --- | --- |
| Mario, Luigi, Ness | Three jabs |
| Donkey Kong, Samus, Yoshi, Jigglypuff | Two jabs |
| Pikachu | Repeated jab one |
| Fox, Kirby | Two jabs, then rapid-jab states |
| Link | Third slash or rapid-jab fork from jab two |
| Captain Falcon | Third jab, then rapid-jab states |

Tap A at the donor's follow-up window to chain; repeated presses/releases request
rapid jabs where the original donor supports them. Stop tapping to finish through
the donor's ending. Link's rapid threshold is five press/release events, Falcon's
is six, and Fox/Kirby use four. These preserve the original input
counter rules; they are not counts of complete button presses.

Jigglypuff's source table contains unused rapid-jab descriptors and a four-event
callback threshold, but its jab-two script never opens that transition gate.
Its playable donor chain therefore stays at two jabs, as in the original game.

Four private jab phase IDs select the donor's existing native status descriptors
without indexing a foreign body's special table. The visible body uses a safe
local clip underneath the shared donor pose. The independent donor clock supplies
rapid-loop boundaries, so a short body animation cannot cut off or repeat a phase.

## Bounce, reflection and movement

Version 0.1.17 corrects the native root-movement flag. The legacy descriptor
macro names for TransN and XRotN are reversed; the engine reads TransN from bit
30 (`0x40000000`). Checking bit 31 incorrectly removed Fox dash attack's travel
and chose friction for Kirby forward smash. The regenerated normal data and
physics selector now follow the actual native bitfield. Original descriptor
values and the body's movement outside attacks stay intact.
Repeated rapid-jab loops also retain the source end-to-start root velocity;
the first frame's zero velocity is only used when the action initially starts.

Fox dash attack's source root curve travels 1,050 engine units;
Kirby forward smash's travels 819, including Kirby's original size. These curves
apply on every borrowed body, with original timing and facing. Stage collision,
hitlag and interruption can shorten the distance in a real match.

- Link down-air performs the original contact bounce on any body: clear attacks,
  cancel fastfall, set upward velocity to 40, rewind a late hit to frame 35, and
  retain the 30-tick rehit timer with the original frame-65 cutoff. A Link body
  borrowing another down-air does not add the bounce.
- Ness forward-smash activates its native bat reflector at frame 16 and clears
  it at frame 22. The source field uses the original TopN offset `(0, 150, 0)`,
  radius `(300, 300, 300)` and 1000 damage resistance, including Ness's source
  size. Native reflection handles weapon/item ownership and outgoing behavior.
  A Ness body borrowing another forward-smash does not add reflection.
- Donor descriptors choose forward-tilt, up-tilt and forward-smash angle
  availability, and dedicated aerial landing versus the native null-landing
  fallback. A missing body clip does not remove a donor variant.
- Ground root travel, traction, air gravity, terminal speed and drift use source
  normal data while the attack or its dedicated landing clock is active. Body
  pose translations cannot alter donor travel. The usual map/landing callbacks,
  Z-cancel rules and hitlag behavior stay in the native engine.
- Source part-intangibility events map to the corresponding body head/limb,
  without changing its hurtbox sizes or layout. The body script cannot add its
  own collision, invulnerability, input flags or accessory effects to a borrowed
  normal. Status exits restore native hit status and clear reflection.

Source world paths also keep normal scripts valid when a body lacks a mapped
joint, such as Samus's right hand. An existing root joint provides the safe
engine reference; donor coordinates still determine hitbox position and reach.

Training and VS have 512-entry asset caches, enlarged from 100, to accommodate
builds referencing all twelve donor attribute/model files. Only selected donors
are preloaded; Ness's bat also preloads its source motion file. Gameplay still
requires 8 MB RDRAM / Expansion Pak. With 4 MB, startup skips the intro so
menus can show the memory requirement; Training/VS lab launches stay blocked.

## Checks and remaining acceptance

- [x] Target-compiled `FTAnimDesc` flag packing versus all 396 normal movement records.
- [x] Root velocities compared frame by frame with original C figatree playback.
- [x] Live ROM Fox dash attack and Kirby forward-smash velocity, world displacement,
  both facings, donor duration and native recovery checks across all twelve bodies (null rendering).
- [x] Production normal callback checks on all twelve donors/bodies/four slots:
  jab buffering, thresholds, loop/end clocks, Link bounce/rehit, Ness bat field,
  source travel/physics and generation guards.
- [x] Original normal collision/pose checks and linked-ROM validation, including
  all 396 movement records and the source bat sockets.
- [x] Live ROM CPU checks: all 144 donor/body jab chains, twelve controlled Link
  bounces and Ness bat reflections, twelve editor returns and four assigned VS
  builds. Training heap retained at least 1,641,264 bytes of headroom.
- [ ] Rendered contact/shield, slopes/edges, interruption and part-intangibility
  acceptance across stages and bodies.
- [ ] Mesh/accessory/effect/audio polish and the Remix port of this milestone.

`generateNormalMechanics.py` regenerates source root travel and bat sockets.
`testNormalMechanics.py` runs production C callbacks with real 32-bit layouts;
its resource/map setup is a fixture. The optional Linux
`testTrainingScenes.py --normal-mechanics --cases 12` uses real menu/input/CPU
execution with null rendering. Each jab trial starts at the native ground spawn
to isolate recovery from accumulated movement toward stage edges. Its contact
fixtures place the CPU in Link's live attack volume and a native CPU fireball in
Ness's field; natural contact and rendered playtesting remain separate acceptance
checks.

`testTrainingScenes.py --normal-movement --cases 12` starts Fox dash attack and
Kirby forward smash through actual controller inputs. Position fixtures keep
the attacker on the flat stage and an idle opponent away; the native physics
and recovery callbacks run normally. Rendered contact, slopes and interruptions
remain separate acceptance checks.

Specials, tether grabs and paired throw choreography are tracked in their own
guides. The [full-roster animation guide](full-roster-animations.md) explains
pose retargeting; the [feature checklist](status.md) tracks wider acceptance.
