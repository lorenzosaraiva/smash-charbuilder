# Original donor collision paths

The first collision-only milestone follows the donor's original hitbox path
independently of the selected body's animated limbs. This is partial coverage,
with automated checks complete and rendered in-game acceptance still pending.

## Coverage

| Donor attack | Bodies | Visible animation |
| --- | --- | --- |
| Kirby up-tilt | All eleven foreign original-roster bodies | Selected body's pose. |
| Falcon up-air | All eleven foreign bodies, including Kirby | Selected body's pose. |
| Falcon down-air | All eleven foreign bodies | Donor pose on Mario; body pose elsewhere. |
| Fox straight forward tilt | All eleven foreign bodies | Donor pose on Mario; body pose elsewhere. |
| DK straight forward smash | All eleven foreign bodies | Donor pose on Mario; body pose elsewhere. |

Kirby has one up-tilt. Bodies with forward/back up-tilt variants use that same
Kirby trajectory for all three variants. Angled Fox forward tilts and DK forward
smashes still use mapped joints. Other donor attacks retain mapped joints too.
Vanilla/unassigned fighters and donor-equals-body choices keep native behavior.

## Try DK + Kirby up-tilt

1. Options -> Character Lab -> edit a build.
2. Body: DK. Up Tilt: Kirby.
3. Test in Training. Start -> View -> HITBOX.
4. Compare with vanilla Kirby at the same fighter position and facing.

Kirby's two hitboxes are active at donor clock samples **4 through 11** and clear
at **12**. Recovery ends at **18**. These are the source script/animation frame
numbers, not a new convention for counting player input frames. DK's foot pose
may visibly separate from these hitboxes; body animations are the next milestone.

The radius, damage, angle, knockback, hit groups and create/clear/refresh operations
come from the donor scripts. Body proportions do not stretch this collision path.
The selected body keeps its hurtboxes and locomotion; donor-specific movement or
special state behavior is separate work. Damage staling and victim weight still
use the game's usual rules.

## Try Kirby + Falcon up-air

Choose **Kirby Body -> Up Air: Falcon -> Test in Training -> View: HITBOX**.
Jump and perform an up-air. The two hitboxes follow Falcon's original trajectory
while Kirby uses his own visible pose. The path also works on every other body.

Donor samples **5 through 13** are active; hitboxes clear at **14**, and recovery
ends at **34**. The original 16 damage, radii 110/130 engine units and angle
phases (80, 361, then 20) remain in the source collision script. The landing
transition selects the donor landing timeline and stops applying the aerial path.

## Implementation

`tools/generateCustomCollisions.py` evaluates donor animation/skeleton data once
per move. Kirby up-tilt uses 19 samples (**988 bytes**); Falcon up-air uses 35
(**1,820 bytes**). The runtime shares these samples across bodies and allocates
no donor animation heap or new per-player buffer. The other three paths reuse
existing pilot frames.

The generated donor-move registry selects the path using the current move
definition, then the common runtime applies body-size compensation and facing.
There is no body/donor-pair branch. Missing native up-tilt variants are registered
using the same donor fallback rules as the collision-script compiler. Existing
Mario pilot trajectories retain their sampled stride and straight-variant coverage.

To expand this catalog, add one supported donor move to `COLLISION_PILOTS`, run
the generator and native checks, then build the ROM. Registration, native-oracle
calls, body-size/facing comparisons and ROM verification derive from that catalog.
Unsupported animation flags/translation scaling still require converter support;
full normal-attack coverage is not enabled yet. Visible animation retargeting is
a separate pass using reusable body rig maps and special handling where needed.

Each center includes the donor's original size. `ftCustomCollisionApply` attaches
the center to the selected body's TopN with inverse body-size compensation. The
normal engine transforms then apply actor position and facing. Target limb
positions and poses have no effect on these centers. The engine continues to own
radius, hit records, attack state and previous/current positions for swept hits.

The existing per-player attack clock supplies duration, nonzero restart samples
and hitlag freezes. Lookup never advances it. Owner/status/motion and preset/scene
guards stop unrelated or interrupted attacks from using stale trajectory data.

## Automated verification

- Original native playback/matrices match **43,479 scalar pose samples** and
  **104 active hitbox centers**, including the three animation pilots, Kirby
  up-tilt and Falcon up-air.
- The compiled collision-only tables match all **34 active centers** and
  source active masks within 0.001 engine units per coordinate.
- Original engine matrices check **816 world positions** across all twelve body
  sizes and both facings at a translated actor position; maximum error is
  **0.0001221 engine units**.
- Runtime tests cover all foreign bodies/three up-tilt selections, donor recovery,
  moved body limbs, paused clocks, nonzero starts, four players/shared presets,
  CPU/demo/scene guards, interruptions and missing-root/invalid-size fallback.
  Falcon up-air adds complete frame coverage on all foreign bodies, original
  hitbox radii/damage preservation and landing transitions without stale paths.
- ROM verification checks the linked collision bytes, donor scripts/timing,
  integrated collision processing and N64 CRC.

The first collision milestone added 1,408 bytes of ROM/resident overlay code and
data, with no BSS growth. Falcon up-air and the generated registry add another
**2,096 bytes**, again with no BSS growth. The ROM is **16,919,792 bytes**;
its checksum is included in download metadata.

## Pending acceptance and expansion

- [ ] In-game comparison of DK/Kirby and Kirby/Falcon up-air, then small/large bodies and both facings.
- [ ] Miss, hit, shield, hitlag, repeated attacks and damage interruption.
- [ ] Aerial landing/cancellation and four-player/CPU matches for shared paths.
- [ ] Remaining normals, angled variants, weapon/tail paths, multihits and loops.
- [ ] Donor movement and state-specific behavior; full visible body animations.

For build/release commands see [building](../../docs/building.md). The main
[checklist](status.md) records the roadmap. A numeric pass is not a rendered
emulator or real-hardware acceptance pass.
