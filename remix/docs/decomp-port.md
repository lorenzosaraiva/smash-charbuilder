# Decomp to Remix port

Updated **2026-10-06**. Remix preview **0.1.4**, project **0.1.21**.

The decomp ROM remains the most complete edition. The Remix preview is a
partial port for the **original twelve** bodies and donors; exposing Remix's
expanded roster does not give those fighters the shared donor data.
Implemented means compiled and automatically checked. Visible poses, actual
contact and stage interactions still require rendered playtesting.

## What works and what remains

| Feature | Remix status | Next work |
| --- | --- | --- |
| Normal attack damage, knockback, sizes and source hitbox paths | Shared donor data and independent clocks implemented | Rendered contact, slopes and interruption acceptance |
| Normal root movement | Donor TransN travel and flag selection ported, including Fox dash and Kirby forward smash | Donor traction/air attributes and movement callbacks |
| Jab chains, Link down-air bounce, Ness bat reflection | Body callbacks remain | Port donor availability, chain states, contact bounce and reflector geometry |
| Up/Down B timing | Donor phase clocks, frozen phases, gameplay duration overrides and eight donor helpless/landing clocks implemented | Rendered landing/interrupt and held-bomb contact acceptance |
| Up/Down B collision paths | All 96 shared phases connected; directional Fire Fox placement and donor Reflector/Magnet volumes added | Rendered contacts and paired Dive acceptance |
| Up/Down B movement | Source TransN travel, separate Mario/Luigi/Falcon angles, imported callbacks and donor recovery attributes | Rendered steering, slopes, wall/ledge and interruption acceptance |
| Mario + Falcon Kick / Pikachu Up B | Regression targets: original travel, retained recipe and body scale | Two-dash steering, aerial starts, walls/ledges and interruptions in rendered play |
| Neutral B | Body Move and finite Fox Laser adapter | Fireballs, Jolt, PK Fire, Punch/Pound, charge/store, Boomerang and Egg Lay |
| Animations | Three Mario normal pilots; borrowed Up/Down B uses safe body idle/fall poses | Stream shared donor animation curves from ROM, then retarget normals/specials |
| Grab/throw selections | Donor grab collision events/timing and numeric throw values | Tether reach/props, paired positioning/release, DK cargo and Kirby landing throws |
| Custom taunts | Native body taunts | Add donor selector, source clock/pose, Mario growth and Luigi hitbox |
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
| Kirby | Final Cutter movement/projectile placement/transitions ported; sword/effect attachments and rendered contacts remain | Armor, hold/timeout and body-safe callbacks ported; Stone prop and landing/interruption acceptance remain |
| Pikachu | Donor recovery ported; second-dash direction gate and wall/floor/ledge acceptance remain | Thunder source socket and independent weapon/passive ownership ported; rendered self-contact/interrupt acceptance remains |
| Jigglypuff | Sing source sleep volume and transitions | Rest invulnerability, one-frame contact and sleep recovery |
| Captain Falcon | Source Dive socket, frame-16 release and donor recovery ported; rendered paired contact/positioning acceptance remains | Kick slopes, aerial branches, hit/contact and interruption |
| Ness | Independent PK Thunder pointer/passives/trails, source socket and recovery ported; steering/self-launch/contact acceptance remains | Donor source volume connected; rendered absorption/healing and contact acceptance remain |

Link's held-bomb common throw actions retain borrowed ownership through all
parameter/command hooks and use source clocks/events, throw values and release
sockets. Falcon Dive adjusts the attacker socket while retaining Remix's
native victim-offset lookup. Their rendered contacts and interruptions remain
acceptance work.

Kirby copy and Remix-exclusive donor fidelity remain outside the original-roster
milestone. Use body-native specials when testing a mechanic not yet verified.

## Port order

1. Check rendered special contacts, steering, recovery and interruptions,
   including Link's held-bomb throws and Falcon Dive paired captures. The
   shared angles, sockets, volumes, independent passives and recovery layer is
   implemented; it does not establish acceptance for every body/stage.
2. Complete normal-specific callbacks and the ten remaining neutral adapters.
3. Stream the donor animation bank and retarget the full catalog. Embedding the
   entire decomp catalog in Remix's already occupied Expansion Pak RAM is too
   large; selected clips need a bounded per-player cache.
4. Port tether/paired throws and taunts, followed by starter defaults and results
   acceptance. Update the relevant checklist and build a checked ROM each batch.

## Checks

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

Preview 0.1.4 passes real-input Test/Back on all four editor slots with
stale Training selections, plus CSS Start/stage confirmation into a running
Training match. Kick/Quick Attack still passes 72 source-velocity samples and
the directional second zip. These CPU results use null rendering.
