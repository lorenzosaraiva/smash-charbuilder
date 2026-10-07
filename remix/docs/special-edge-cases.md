# Special edge cases

Updated **2026-10-07**, Remix preview **0.1.11**, project **0.1.28**.
This milestone covers the original twelve bodies and donors. Body hurtboxes
remain native; donor attack values, paths and clocks stay independent of poses.

## Fixes

- DK/Samus borrowed down smashes no longer send donor effect bone IDs to
  absent body joints. Cosmetic effects map to valid body roles or TopN;
  donor mesh and part-hurtbox commands leave the foreign body intact.
- Samus Bomb uses a separate donor Morph Ball on frames 10-42, restoring
  native body visibility at frame 43 or interruption. Native body hurtboxes
  stay unchanged; bomb creation, movement and recovery retain source timing.
- Samus tether's glow tree/materials are preloaded for paired actions and
  follow source joint 23 rather than the selected body's joint 23. The six
  original beam-part samples remain unchanged.
- A single DK Down B cycle deliberately has two slap windows at 16-17 and
  26-27. Single-tap CPU checks on native DK and Mario's borrowed DK both
  produce exactly one cycle. Another B tap requests a second cycle.

- Mario's borrowed taunt grows around the selected body's planted pivot.
  Shared poses retain body bind translations, so applying Mario's root drop
  directly buried the foreign body's feet. The hip now follows the scaled body
  rest height; the world/collision root stays unchanged. Natural exit and
  interruptions restore the native scale.
- **USE BODY FOR ALL MOVES** selects the body's explicit Neutral B donor.
  Kirby keeps native copy; expanded bodies keep their native entry. Other move
  selectors and existing recipes retain their behavior.
- A selected donor with no ground/air special entry rejects the input before
  creating borrowed context or resources. For example, airborne DK Down B
  does nothing; landing lets the same selection use DK's grounded slaps. It
  no longer executes the body's unrelated Down B.

## Automated evidence

The standard build executes the actual linked MIPS preset/dispatch/pose code:
twelve bodies and four slots for body presets, eleven foreign bodies and four
ports for airborne DK rejection, and all eleven foreign Mario taunt pivots
through eight source growth/shrink samples. These are production-code checks,
with menu helpers isolated where appropriate.

Optional CPU fixtures boot the built ROM with a native Mupen64Plus core and
real controller input. Positioning fixtures make contacts repeatable; native
weapon/collision/status code determines the outcome. Absorption starts from an
explicit 80-percent fixture. No successful contact, launch, sleep, damage or
release result is injected.

| Check | Evidence | Rendered acceptance still needed |
| --- | --- | --- |
| DK/Samus down smash | Both donor/body directions execute real down-smash input and recover without CPU fault; 396 absent-effect-joint cases pass linked MIPS | Visible effects and contacts across the wider roster |
| Samus Bomb | DK allocates a Morph Ball, hides its body on the source clock and restores visibility/owned handles on recovery; both ground/air prop tables checked on all foreign bodies | Visible ball size/position, grounded and airborne interruptions |
| Samus tether | DK's missed tether allocates six beam parts plus native glow; full extension/retraction and seven-object cleanup; donor glow placements checked on all foreign bodies/facings | Visible alignment with DK's hand, hitbox and victim |
| Missing aerial DK Down B | Mario rejects aerial input and performs grounded donor slaps after landing | Other bodies, ledges and buffered inputs |
| Repeated DK slaps | Mario repeats frames 16–17 / 26–27, including native hitlag and opponent damage | Slopes, stage edges and interruption chains |
| Quick Attack | Two real-input zips, direction change and recovery; native position/velocity/scale checked | Walls, ceilings, ledge snaps and all directional gates |
| Quick Attack wall contact | Mario's borrowed aerial zip contacts a stage-derived Hyrule wall and enters the native end phase | Other walls, ceilings, second-zip contacts and visible alignment |
| Quick Attack ledge recovery | Mario catches a stage-derived Dream Land ledge, uses real ledge-attack input and returns to Idle without KO | Other ledges, facing, second-zip approaches and visible snapping |
| Slope movement | Mario's Falcon Kick enters on a stage-derived Hyrule slope, reads a nonvertical floor normal and recovers without KO | Other slopes, reversals and moving surfaces |
| PK Thunder | Real steering, native self-contact/launch and recovery fixture | Wall bounces, shields/reflectors, ledges and multiple owners |
| Thunder | Falcon enters the native owner-contact hit/end phases and recovers | Misses, moving platforms and interrupted owner contact |
| Reflector / PSI Magnet | Yoshi reflects a real opponent Fireball; Magnet heals from contact; volumes clear on release | Facing changes, simultaneous projectiles and other projectile families |
| Sing | Mario's borrowed Sing places the opponent in native FuraSleep and recovers | Wake timing across percentages, air targets and interruptions |
| Rest | Real opponent damage, frame-1 hitbox, intangibility through frame 29 / normal at 30, and full 250-frame recovery | Exact visible overlap and broader body/contact acceptance |
| Air-to-ground transition | Falcon's aerial Mario Tornado reaches the grounded donor phase on Dream Land and Planet Zebes | Slopes, ceilings and moving platform continuity |
| Interruption | Training reset during PK Thunder removes the weapon and recreates a running fighter | Hitstun, grab, KO and scene-change combinations across all specials |

The CPU reports in checked build metadata identify the exact ROM hash, body,
stage and checks. Null-renderer fixtures establish native mechanics and recovery,
not visible alignment. They supplement the existing linked-MIPS timing,
ownership, source geometry and cleanup tests.

## Remaining acceptance checklist

- [x] Correct planted Mario taunt pivot and body Neutral B preset selection.
- [x] Reject unavailable aerial donor specials without body fallback.
- [x] Add reproducible native special contact/transition/interruption fixtures.
- [ ] Render every special on foreign bodies with HITBOX view and compare
  startup, contact, active windows and recovery with the source fighter.
- [ ] Quick Attack second-zip angle gates, walls/ceilings, slopes and ledges.
- [ ] PK Thunder wall bounds, interrupted trails, reflection and multiple owners.
- [ ] Thunder self-contact on moving platforms and during owner interruption.
- [ ] Reflector/Magnet facing and every supported projectile contact family.
- [ ] Sing wake/re-hit behavior and Rest invulnerability/contact across bodies.
- [ ] Repeated DK slaps on slopes/edges and interruptions during each hit window.
- [ ] VS stock KOs, rematches and scene changes with four assigned builds.

Run the fixture from `remix/` with a compatible core/API header pair:

```sh
python scripts/test_charlab_scenes.py --core /path/libmupen64plus.so.2 \
  --headers /path/core/src/api --edge dk-repeat --body 0 --run-id dk-repeat
```

Other `--edge` choices are `grounded-only`, `ness-launch`, `thunder-contact`,
`reflect`, `absorb`, `sing`, `rest`, `air-land`, `interrupt`, `quick-wall`,
`quick-ledge` and `slope`. Wall/slope fixtures read the live stage geometry;
use Hyrule (`--stage 4`) for those checks. `--stage` selects
an original stage. Isolated `--run-id` folders prevent save/config collisions.
`--taunt-donor 0 --body 1` checks Fox with Mario's taunt through real L input.
These fixtures use null rendering; visual acceptance requires an emulator with
a working graphics plugin.

See [the complete port matrix](decomp-port.md) for all remaining milestones.
