# Decomp to Remix port

Updated **2026-10-05**. Remix preview **0.1.2**, project **0.1.19**.

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
| Up/Down B timing | Donor phase clocks, frozen phases and gameplay duration overrides implemented | Donor helpless/landing recovery across body transitions |
| Up/Down B collision paths | All 96 shared source phases compiled; source events and body-size-compensated root placement connected | Directional collision transforms, weapons and special volumes |
| Up/Down B movement | Source TransN travel and donor attributes around native phase physics connected | Separate steering angles, recovery attributes and move-specific callbacks |
| Mario + Falcon Kick / Pikachu Up B | Regression targets: original travel, retained recipe and body scale | Two-dash steering, aerial starts, walls/ledges and interruptions in rendered play |
| Neutral B | Body Move and finite Fox Laser adapter | Fireballs, Jolt, PK Fire, Punch/Pound, charge/store, Boomerang and Egg Lay |
| Animations | Three Mario normal pilots; borrowed Up/Down B uses safe body idle/fall poses | Stream shared donor animation curves from ROM, then retarget normals/specials |
| Grab/throw selections | Donor grab collision events/timing and numeric throw values | Tether reach/props, paired positioning/release, DK cargo and Kirby landing throws |
| Custom taunts | Native body taunts | Add donor selector, source clock/pose, Mario growth and Luigi hitbox |
| Training/UI/presets | Four SRAM builds, human/CPU assignment, editor return, native menu style | Rendered acceptance and any new selector fields |
| Hitbox view / grab combo meter / unlocks | Remix built-in features retained | Rendered regression with custom mechanics |
| Yoshi Build One / 4-stock items-off defaults | Still decomp only | Update Remix initialization without overwriting saved user presets |
| Match ending | Decomp results fix is separate; Remix uses its own scenes | Exercise Remix results, victory poses and rematches with assigned builds |

## Special-by-special acceptance

Source paths and clocks are shared foundations. They do not establish complete
mechanical parity for each special below. Native donor callbacks still run
through Remix's compatibility context.

| Donor | Up B still needing acceptance or additional adapters | Down B still needing acceptance or additional adapters |
| --- | --- | --- |
| Mario / Luigi | Steering-relative path rotation, sweetspots, helpless/landing recovery | Tornado independent state, B-tap rise and transitions |
| Fox | Fire Fox direction, map collisions and directional hitboxes | Reflector source volume, turning and reflection |
| Donkey Kong | Spin ground/air limits, recovery and contact | Slap repeats, ground transitions and contact |
| Samus | Screw Attack recovery/landing, intangibility and contact | Bomb spawn socket and ownership |
| Link | Ground Spin Attack weapon and source socket; aerial recovery | Bomb creation/held-bomb toss and source release socket |
| Yoshi | Egg launch/release socket and ownership | Bomb drop/landing and interruption |
| Kirby | Final Cutter sword/projectile socket, movement and transitions | Stone model/armor, hold/timeout, landing and interrupts |
| Pikachu | Second-dash direction gate, wall/floor/ledge transitions and landing | Thunder socket, independent weapon/passive ownership and self-contact |
| Jigglypuff | Sing source sleep volume and transitions | Rest invulnerability, one-frame contact and sleep recovery |
| Captain Falcon | Dive catch volume, paired capture/release and recovery | Kick slopes, aerial branches, hit/contact and interruption |
| Ness | PK Thunder independent ownership/socket, steering and self-launch | PSI Magnet source volume, absorption/healing and ownership |

The shared 96-phase dataset includes Link's held-bomb common throw actions;
those still need a dedicated adapter. Compilation of their source data does
not connect those common item states to borrowed-special ownership.

Kirby copy and Remix-exclusive donor fidelity remain outside the original-roster
milestone. Use body-native specials when testing a mechanic not yet verified.

## Port order

1. Finish the reported Kick/Quick Attack regressions, then directional geometry,
   special sockets, independent passives and donor recovery.
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
through real B input. It records native status/position/velocity/scale traces.
This checks CPU gameplay, not visible animations or contact fidelity. An old
core that cannot boot the unchanged preview cannot serve as a port regression.
Use matching API headers with `--core` / `--headers` for a locally built core.
Preview 0.1.2 passes the Mario CPU fixture: 72 live Kick source-velocity samples,
two Quick Attack dashes entered by real directional input, native landing/
recovery, stable scale and restored Mario identity. Its rendering is null;
visible animation/contact and broader body/stage acceptance remain pending.
