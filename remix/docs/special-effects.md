# Remix special effects and attachments

Preview **0.1.18**, updated **2026-10-08**. Keep **Original 12 Only** enabled.

| Donor move | Borrowed presentation |
| --- | --- |
| Kirby Final Cutter | Native sword draw, rising/falling sword and trails on source effect-flag transitions |
| Kirby Stone | Source model replacement with sampled transforms; hide the native body only while the prop is active |
| Kirby Inhale | Gameplay connected; native wind and discard-star effects, animated face-attached mouth overlays; full body/stretch poses and copied hats deferred; native victim shrink/hold/star states retained |
| Falcon Punch / Falcon Kick | Native flames attached to the retargeted hand/foot; original create/remove flags |
| Fox Laser | Source blaster model and sampled open/close transforms, firing sparkle and sound |
| Yoshi Egg Lay | Native tongue part and sampled extension/retraction through catch/release phases |
| Samus Bomb | Body-colored donor Morph Ball replaces the foreign body on frames 3-48, with the source compressed/round/recovery meshes; native body flags return at frame 49 or interruption; one damaging bomb per input, independent of the visual prop |
| Samus tether grab | Six donor beam parts plus native glow tree/materials at sampled source joint 23, independent of body joints |
| DK Giant Punch | Native full-charge blinking color script persists while stored; consumed charge removes it without restarting the blink every tick |
| Samus Charge Shot | Cosmetic orb at the donor socket, all eight source sizes and charging sound; retain through release startup until firing |

Independent fighter meshes now draw on head 0, matching native Samus's fighter
pass; the native beam glow stays on effects head 1. Props initialize native
stage environment color, two-cycle shading, explicit opaque two-cycle render mode
and zero fog alpha. Install the native one-light count and stage direction.
Stone also initializes complete white diffuse and brown ambient light records:
the native light helper supplies direction without initializing colors, and the
previous build still appeared black. A poisoned-heap regression checks both
records before the source mesh; rendered Stone colour acceptance remains pending.
Then restore
one-cycle shading, palette/alpha/render settings and stage lighting. Previously,
leaving two-cycle state on effects head 1 corrupted later translucent stage layers.
The runtime uses the game's F3DEX2 graphics commands. Six linked-MIPS cases execute
the actual callback, native material image branches and deliberately dirty mesh
state, checking both submission and the final state seen by subsequent draws.
Paired materials now advance only through the native EF update, once per frame;
the imported fighter-owned tick incorrectly doubled Samus texture animation speed.
The user confirmed a visible tether in 0.1.13 but reported noisy textures and
white Dream Land layers. The user confirmed the subsequent fix worked. Broader
rendered tether acceptance across bodies and stages remains pending.

The real-input Dream Land regression adds
`--body 2 --paired-donor 3 --paired-miss --visuals --tether-materials`
to `scripts/test_charlab_scenes.py`. It checks 99 native material samples for
one update per frame, the original 50-frame image hold and blink sequence.
Separate contact/release and missed-extension/recovery scenes pass without a
CPU fault. These scenes use null rendering.

The same source prop samples work on all eleven foreign original bodies. Their
positions, sizes and lifetimes follow the donor clock, independently of body
proportions or hitboxes. Flame/sword attachment joints use semantic body roles.
Body hurtboxes stay native; props and the held orb are EF objects without
weapon collisions. Damaging Charge Shot remains the separate projectile.

Samus Bomb keeps the original grounded hop: the native frame-3 air handoff and
40-unit upward velocity with Samus gravity are preserved. The ball uses the
source-sized joint-6 pose and a private CI4 palette tinted for the selected body;
shared donor textures are untouched. Part 1 covers compression/recovery and part
2 covers the round ball from frame 10 through 42. Earlier checks only covered
allocation/placement of part 2 and missed the incomplete render-state setup.

Borrowed Inhale retains preloaded Kirby script/texture pointers across native
particle bank reinitialization and binds the spare eighth slot after scene setup.
If all eight native slots are occupied, wind is suppressed safely; rendered
four-player/native-copy bank pressure remains acceptance work. No files load on B.
The CPU regression compares the live wind script bytes with the source ROM. Its
funnel follows the receiving body's head during the source loop. An owned
geometric mouth overlay opens/closes on source phases and follows head rotations;
it does not deform the native jaw or retarget the full inhale/stretch pose. L or
native heavy-hit copy loss emits one native discard star per held copy. Wind and
mouth handles clear on recovery, capture, interruptions, death and scene resets.
Per-body face offsets and rendered alignment still require in-game acceptance.

The 0.1.18 null-rendering CPU sequence passes on every foreign original body:
capture, spit, repeat capture, copy, copied Mario Fireball, actual L-discard taunt
and aerial inhale/landing/release. Each run observes the mouth and wind, compares
the live wind script with Kirby's source bytes, counts exactly one discard star
and checks finite transforms and cleared handles after recovery.

The safe common visual stream includes original absolute waits, common effects,
FGM, voices and tracked loop sounds. Donor part/texture/hurtbox commands remain
blocked from modifying foreign body parts. Actor-specific effect constructors
outside this table, facial materials and other special overlays are separate work.

Private asset pointers load during the pre-match donor walk. Pressing B performs
no file loads. Attached effects validate fighter/generation ownership and native
effect-list membership. Interruptions, damage/capture, death and scene resets
remove owned objects and restore Stone-hidden flags. Same-family transitions
can retain attachments; donor/attack-family changes clean them up. Short-lived
common particles finish their native lifetimes; the scene arena clears them on exit.

The 0.1.16 real-input CPU checks charge Mario's borrowed Giant Punch to full,
observe the native color script advancing while idle/moving and confirm its
removal after release. DK's borrowed Bomb passes two grounded and two aerial
casts, with meshes/private palettes at source frames 3/10/43/48 and the original
grounded rise, while retaining exactly one weapon birth per input. These checks
use null rendering; visible colors/blink/ball acceptance remains pending.

The standard build compares source prop tables with an independent host ELF
and executes 1,122 prop placements and 88 Samus beam-glow placements across foreign bodies/facings, 66 private native
constructors, 44 stored-charge color/priority/cleanup cases, twelve private
ball palettes and all Morph Ball mesh switches, Cutter/Falcon effect flags, all eight orb sizes, release handoff,
audio waits/idempotence and interruption/death/four-port reset/stale-owner cleanup.
Allocation and audio services are fixtures in these linked-MIPS checks.

`scripts/test_charlab_scenes.py --visuals` additionally checks native allocation,
finite transforms and cleanup after real input in the emulator. Default rendering
is null, so these checks alone do not establish visible quality. The attempted
Rice graphics smoke harness did not produce valid frames and crashed on shutdown;
it is not counted as rendered acceptance. Full rendered acceptance across bodies, stages,
interruptions and four-player matches remains pending.

Try Cutter/Stone, Punch/Kick, Laser, Egg Lay and charged storage/release on a
foreign body with HITBOX/HITBOX+ enabled. Report the body, donor, phase, emulator
and version, with a clip showing any misplaced or lingering attachment.

The checked 0.1.9 ROM passes real-input CPU scenes on Mario for Cutter/Stone,
Punch, Laser, Egg Lay and charge storage/release, plus the Kick/two-zip Quick
Attack regression. Native props/FX are allocated, their transforms remain finite,
Stone hides the body while active, and owned handles are cleared on recovery.
Editor Test -> CSS Start -> stage -> Training also passes. These scenes use
null rendering; source audio dispatch is checked, audible output is not.
