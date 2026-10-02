# Original donor collision paths

The first collision-only milestone follows the donor's original hitbox path
independently of the selected body's animated limbs. This is partial coverage,
with automated checks complete and rendered in-game acceptance still pending.

## Coverage

| Donor attack | Bodies | Visible animation |
| --- | --- | --- |
| Kirby up-tilt | All eleven foreign original-roster bodies | Selected body's pose. |
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

## Implementation

`tools/generateCustomCollisions.py` evaluates original Kirby animation/skeleton
data and emits 19 collision-only frames, totaling **988 bytes**. The runtime uses
these shared frames for every body; it allocates no donor animation heap or new
per-player buffer. The other three paths reuse existing pilot frames.

Each center includes the donor's original size. `ftCustomCollisionApply` attaches
the center to the selected body's TopN with inverse body-size compensation. The
normal engine transforms then apply actor position and facing. Target limb
positions and poses have no effect on these centers. The engine continues to own
radius, hit records, attack state and previous/current positions for swept hits.

The existing per-player attack clock supplies duration, nonzero restart samples
and hitlag freezes. Lookup never advances it. Owner/status/motion and preset/scene
guards stop unrelated or interrupted attacks from using stale trajectory data.

## Automated verification

- Original native playback/matrices match **35,289 scalar pose samples** and
  **86 active hitbox centers**, including the three animation pilots and Kirby.
- The compiled collision-only table matches all **16 active Kirby centers** and
  source active masks within 0.001 engine units per coordinate.
- Original engine matrices check **384 world positions** across all twelve body
  sizes and both facings at a translated actor position; maximum error is
  **0.0001221 engine units**.
- Runtime tests cover all foreign bodies/three up-tilt selections, donor recovery,
  moved body limbs, paused clocks, nonzero starts, four players/shared presets,
  CPU/demo/scene guards, interruptions and missing-root/invalid-size fallback.
- ROM verification checks the linked collision bytes, donor scripts/timing,
  integrated collision processing and N64 CRC.

The build adds **1,408 bytes** of ROM/resident overlay data and code: 416 bytes
of text and 992 bytes of aligned read-only data, with **no BSS growth**. The
Training arena before transient allocations remains **1,968,880 bytes**. The
new ROM is 16,917,696 bytes; its checksum is included in the download metadata.

## Pending acceptance and expansion

- [ ] In-game comparison of DK/Kirby, then small/large bodies and both facings.
- [ ] Miss, hit, shield, hitlag, repeated attacks and damage interruption.
- [ ] Aerial landing/cancellation and four-player/CPU matches for shared paths.
- [ ] Remaining normals, angled variants, weapon/tail paths, multihits and loops.
- [ ] Donor movement and state-specific behavior; full visible body animations.

For build/release commands see [building](../../docs/building.md). The main
[checklist](status.md) records the roadmap. A numeric pass is not a rendered
emulator or real-hardware acceptance pass.
