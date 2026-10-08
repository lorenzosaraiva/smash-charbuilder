# Decomp to Remix port

Updated **2026-10-08**. Remix preview **0.1.18**, project **0.1.35**.

Preview 0.1.18 adds Kirby Neutral B to every original body: original ground/air
catch geometry and phase timing, native held victims, star spit, copy release,
and copied Neutral B from native/custom victims. Copy ownership is separate
from body passive unions; L, death, scene reset and native heavy-hit copy loss
discard it. Native Kirby keeps Remix's own dispatcher. Native wind/discard stars and
animated face overlays are connected; full body/stretch poses and hats remain
pending. See [neutral controls and evidence](neutral-specials.md).

The current special-edge-case checks and remaining rendered stage acceptance
are tracked in [special edge cases](special-edge-cases.md). Mario taunt growth
uses a planted body pivot; body presets set Neutral B explicitly, and missing
donor ground/air entries reject input instead of selecting a body fallback.
Current CPU checks cover two Quick Attack zips, a native Hyrule wall and slope,
PK Thunder steering/self-launch, Thunder owner contact, reflection/absorption,
Sing/Rest contacts, repeated DK hit windows, aerial landing and Training reset.
These targeted fixtures do not establish rendered acceptance across all bodies/stages.

The local 0.1.16 build adds the native stored Giant Punch flash, explicit opaque
two-cycle prop rendering and body-colored Samus compression/round/recovery meshes.
Real-input CPU checks cover full charge through movement/release and the ball
following the source hop; rendered acceptance remains pending.

Remix 0.1.16 draws borrowed fighter parts in the native fighter pass and
restores its one-cycle state afterward, addressing noisy tether textures and
white stage layers. Beam materials advance once per frame. Native material
submission and exit state have regression checks. The user confirmed the
reported tether/stage corruption was fixed; broader rendered acceptance remains
pending.

Preview 0.1.16 prevents duplicate Samus bombs when borrowed phases land or
enter the air, and allows donor aerial Down B on DK's body. Each input creates
one bomb; fresh inputs retain source timing. Actual weapon counts are checked
on DK, Mario and native Samus, alongside all-foreign-body MIPS event checks.
It also retains both DK/Samus down-smash fixes, Samus Bomb's
Morph Ball and restores Samus's missing borrowed tether glow. Their production
MIPS and targeted real-input CPU checks are separate from rendered acceptance.
DK's two slap windows are one original cycle, verified on native DK and Mario;
another cycle requires another B tap.

The decomp ROM remains the most complete edition. The Remix preview is a
partial port for the **original twelve** bodies and donors; exposing Remix's
expanded roster does not give those fighters the shared donor data.
Implemented means compiled and automatically checked. Visible poses, actual
contact and stage interactions still require rendered playtesting.

## What works and what remains

| Feature | Remix status | Next work |
| --- | --- | --- |
| Normal attack damage, knockback, sizes and source hitbox paths | Shared donor data and independent clocks implemented | Rendered contact, slopes and interruption acceptance |
| Normal root movement | Donor TransN travel, flag selection, traction/air attributes and landing branches ported, including Fox dash and Kirby forward smash | Rendered momentum, slopes and interruption acceptance |
| Jab chains, Link down-air bounce, Ness bat reflection | Donor callbacks, native donor jab status arrays, source bounce/rehit and bat windows/geometry ported | Rendered contact and stage acceptance |
| Up/Down B timing | Donor phase clocks, frozen phases, gameplay duration overrides and eight donor helpless/landing clocks implemented | Rendered landing/interrupt and held-bomb contact acceptance |
| Up/Down B collision paths | All 96 shared phases connected; directional Fire Fox placement and donor Reflector/Magnet volumes added | Rendered contacts and paired Dive acceptance |
| Up/Down B movement | Source TransN travel, separate Mario/Luigi/Falcon angles, imported callbacks and donor recovery attributes | Rendered steering, slopes, wall/ledge and interruption acceptance |
| Mario + Falcon Kick / Pikachu Up B | Regression targets: original travel, retained recipe and body scale | Two-dash steering, aerial starts, walls/ledges and interruptions in rendered play |
| Neutral B | All twelve original donors, private weapons, charge/store/release, Egg Lay and Kirby inhale/copy; source poses for the other eleven donors | Full Kirby body/stretch poses and hats; full rendered projectile/contact/reflect/absorb, paired victim alignment and material acceptance |
| Animations | Shared normal/supported special/recovery curves on twelve bodies through independent ROM caches; Cutter sword/trails and Stone replacement added | Full rendered acceptance, remaining overlays/materials, victim alignment and taunt mesh acceptance |
| Grab/throw selections | Donor tether/tongue reach and props, pull clocks, paired positioning/facing/release, DK cargo and Kirby lift/fall/landing | Rendered alignment, slopes/edges and interruption acceptance |
| Custom taunts | Twelve-donor selector, source clocks/poses/effects, Mario growth/shrink and Luigi hitbox/cancel window | Rendered mesh/effects and broader interruption acceptance |
| Training/UI/presets | Four SRAM builds, human/CPU assignment, initialized Test launch, editor return and Character Lab menu label | Rendered acceptance and any new selector fields |
| Hitbox view / grab combo meter / unlocks | Remix built-in features retained | Rendered regression with custom mechanics |
| Yoshi Build One / 4-stock items-off defaults | Still decomp only | Update Remix initialization without overwriting saved user presets |
| Match ending | Decomp results fix is separate; Remix uses its own scenes | Exercise Remix results, victory poses and rematches with assigned builds |

## Special-by-special acceptance

Source paths and clocks are shared foundations. They do not establish complete
mechanical parity for each special below. Native donor callbacks still run
through Remix's compatibility context.

| Donor | Up B still needing acceptance or additional adapters | Down B still needing acceptance or additional adapters |
| --- | --- | --- |
| Mario / Luigi | Steering travel and donor helpless/landing ported; sweetspot/contact/map acceptance remains | Independent Tornado expenditure and source rise/transition callbacks ported; real-input acceptance remains |
| Fox | Fire Fox directional hitboxes and donor recovery ported; map/steering contact acceptance remains | Donor source volume connected; rendered turning/reflection acceptance remains |
| Donkey Kong | Spin ground/air limits, recovery and contact | Slap repeats, ground transitions and contact |
| Samus | Donor landing clock ported; Screw Attack intangibility/contact acceptance remains | Donor-relative bomb position and callbacks ported; rendered bomb contact acceptance remains |
| Link | Independent Spin Attack weapon, interruption cleanup and aerial recovery ported; rendered contacts remain | Held-bomb common ground/air throw clock, events, donor values and release socket ported; rendered contact/interrupt acceptance remains |
| Yoshi | Source held/release socket and independent egg ownership ported; rendered trajectory/contact acceptance remains | Bomb drop/landing and interruption acceptance |
| Kirby | Final Cutter movement/projectile placement/transitions and sword/trail attachments ported; rendered contacts remain | Armor, hold/timeout, body-safe callbacks and Stone replacement model ported; landing/interruption acceptance remains |
| Pikachu | Donor recovery ported; second-dash direction gate and wall/floor/ledge acceptance remain | Thunder source socket and independent weapon/passive ownership ported; rendered self-contact/interrupt acceptance remains |
| Jigglypuff | Sing source sleep volume and transitions | Rest invulnerability, one-frame contact and sleep recovery |
| Captain Falcon | Source Dive socket, frame-16 release and donor recovery ported; rendered paired contact/positioning acceptance remains | Kick slopes, aerial branches, hit/contact and interruption |
| Ness | Independent PK Thunder pointer/passives/trails, source socket and recovery ported; steering/self-launch/contact acceptance remains | Donor source volume connected; rendered absorption/healing and contact acceptance remain |

Link's held-bomb common throw actions retain borrowed ownership through all
parameter/command hooks and use source clocks/events, throw values and release
sockets. Falcon Dive adjusts the attacker socket while retaining Remix's
native victim-offset lookup. Their rendered contacts and interruptions remain
acceptance work.

Full inhale body/stretch poses, copy hats, rendered face alignment and Remix-exclusive donor fidelity remain pending.
Use body-native specials when testing a mechanic not yet verified.

## Port order

1. Check rendered special contacts, steering, recovery and interruptions,
   including Link's held-bomb throws and Falcon Dive paired captures. The
   shared angles, sockets, volumes, independent passives and recovery layer is
   implemented; it does not establish acceptance for every body/stage.
2. Normal-specific callbacks and all twelve neutral donors
   are ported; finish rendered normal/neutral contact and interruption acceptance.
3. Safe source effects/attachments are ported; check broader rendered acceptance.
   Shared curves now stream from ROM through bounded per-player caches;
   neutral, tether/paired and taunt phase entry points are connected.
   See [effects and attachments](special-effects.md) for source clocks and cleanup.
4. Check rendered tether/paired throws and taunts; then port starter defaults
   and finish results/rematch acceptance. Update the relevant checklist and build a checked ROM each batch.

## Checks

For preview 0.1.9 normal callback coverage and real-input jab/bounce results,
see [normal mechanics](normal-mechanics.md). Kick/Quick Attack and the editor
Test -> CSS Start -> stage -> Training regression also pass on this preview;
these CPU checks use null rendering.

The standard build executes source host checks and production MIPS movement,
collision/parser, ownership and clock tests. It also independently verifies ELF
relocations, source geometry bytes, ROM CRC and Expansion RAM headroom.

Optional `scripts/test_charlab_scenes.py` boots Remix in a compatible
Mupen64Plus core with isolated saves and null rendering, reaches the main menu
with real Start input, loads a Training fixture and enters Kick/Quick Attack
through real B input. Optional donor selections exercise other Up/Down B
callbacks; Link includes a second Down B to throw its held bomb. It records
native status/position/velocity/scale traces and checks entry-position continuity,
return to Idle without KO, and body identity. `--falcon-contact` places the CPU
in the live Dive hitbox to exercise native capture/release and throw damage.
This checks CPU gameplay, not visible animations or contact fidelity. An old
core that cannot boot the unchanged preview cannot serve as a port regression.
Use matching API headers with `--core` / `--headers` for a locally built core.
Preview 0.1.3 passed 24 primary Up/Down B casts across all twelve donors: ten
donors on Mario, and Mario/Luigi on Kirby. Link also passes a second Down B
through the common held-bomb throw. These are controlled CPU fixtures with
null rendering; visible animation/contact and broader body/stage acceptance
remain pending.

The Mario Kick/Quick Attack CPU regression also passes on preview 0.1.3: 72
source-velocity samples and two real-input zips, with the second aimed back
toward the platform, followed by native recovery without KO or scale leaks.
Controlled live Dive hitbox contact also passes native capture, paired release
and throw damage. CPU fixtures use null rendering and do not establish visible
pose or full contact fidelity.

The editor launch regression executes 48 production handlers across four
slots and twelve original bodies, checking scene initialization and the
Character Lab label; SRAM I/O and costume lookup are isolated there.
The optional `--editor-test --editor-slot 1` CPU fixture opens the real
Settings editor, poisons old Training selections, presses A on Test, waits
for a running CSS and returns with B (after recalling the selected puck).
`--editor-play` continues through real CSS Start and stage confirmation into
Training. These checks use null rendering; visible UI acceptance remains pending.

Preview 0.1.5 passes real-input Test/Back on all four editor slots with
stale Training selections, plus CSS Start/stage confirmation into a running
Training match. Kick/Quick Attack still passes 72 source-velocity samples and
the directional second zip. These CPU results use null rendering.

Preview 0.1.5 uses the decomp retargeter and compressed curves in a ROM bank,
with independent 15,200-byte caches for four players. See [animation coverage](animations.md).
The standard verifier compares every packed clip with the original decomp ELF
and executes joint poses on all twelve rigs. Rendered acceptance remains pending.

The 0.1.5 pose check passes 501 packed clips / 583,853 keys, 164,829 linked-MIPS
joint orientations on twelve rigs, 1,848 special selections, twelve callback-alias
world-root guards and four independent caches. Real-input CPU checks pass
Falcon normals on Mario/Kirby, Kirby normals on Yoshi, Falcon Kick source travel
and both Quick Attack zips/recovery. These checks use null rendering; visible
meshes, special props/effects and rendered contacts remain acceptance work.
