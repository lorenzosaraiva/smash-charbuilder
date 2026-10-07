# Remix special effects and attachments

Preview **0.1.11**, updated **2026-10-07**. Keep **Original 12 Only** enabled.

| Donor move | Borrowed presentation |
| --- | --- |
| Kirby Final Cutter | Native sword draw, rising/falling sword and trails on source effect-flag transitions |
| Kirby Stone | Source model replacement with sampled transforms; hide the native body only while the prop is active |
| Falcon Punch / Falcon Kick | Native flames attached to the retargeted hand/foot; original create/remove flags |
| Fox Laser | Source blaster model and sampled open/close transforms, firing sparkle and sound |
| Yoshi Egg Lay | Native tongue part and sampled extension/retraction through catch/release phases |
| Samus Bomb | Donor Morph Ball replaces the foreign body on frames 10-42; native body flags return at frame 43 or interruption |
| Samus tether grab | Six donor beam parts plus native glow tree/materials at sampled source joint 23, independent of body joints |
| Samus Charge Shot | Cosmetic orb at the donor socket, all eight source sizes and charging sound; retain through release startup until firing |

The same source prop samples work on all eleven foreign original bodies. Their
positions, sizes and lifetimes follow the donor clock, independently of body
proportions or hitboxes. Flame/sword attachment joints use semantic body roles.
Body hurtboxes stay native; props and the held orb are EF objects without
weapon collisions. Damaging Charge Shot remains the separate projectile.

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

The standard build compares source prop tables with an independent host ELF
and executes 1,122 prop placements and 88 Samus beam-glow placements across foreign bodies/facings, 66 private native
constructors, Cutter/Falcon effect flags, all eight orb sizes, release handoff,
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
