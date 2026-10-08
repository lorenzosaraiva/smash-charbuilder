# Remix neutral donors

Preview **0.1.19**, updated **2026-10-08**. Keep **Original 12 Only** enabled.
Neutral Special now offers the body's name (native behavior) and Fox, Mario,
Luigi, Pikachu, Ness, Captain Falcon, Jigglypuff, Donkey Kong, Samus, Link and
Yoshi and Kirby. Choosing the same donor as the body keeps its native routines.

| Donor | Shared gameplay on foreign original bodies |
| --- | --- |
| Fox | Fire at 25 ground / 15 air; repeat windows; 55 / 45 recovery |
| Mario / Luigi | Fireball at 16; 46 recovery; separate source velocity/gravity/lifetime |
| Pikachu | Jolt at 21; 64 recovery; native airborne/surface-following lifecycle |
| Ness | PK Fire at 20; 72 ground / 60 air; spark and flame-pillar item |
| Captain Falcon | Punch contact at 42-46; 90 recovery; source ground travel and air boost |
| Jigglypuff | Pound contact at 12-27; 55 recovery; source ground travel and air boost |
| Donkey Kong | Startup, charge cycles, stored level with native full-charge flash, partial/full punch and source collisions |
| Samus | Charge ticks/storage, charge-dependent startup speed, shot scaling and recoil |
| Link | Tilt/smash launch, one outstanding Boomerang, empty/return/catch phases and reflection |
| Yoshi | Source grab path, capture anchor, swallow/release and native egg damage/escape |
| Kirby | Ground/air inhale, native capture/held victim, star spit, absorb/copy and use of the victim's selected Neutral B; native wind/discard star; no added mouth overlay |

With **Kirby** selected, hold **B** to inhale. Once holding a victim, press
**A or L** to spit or **B/down** to absorb and copy its Neutral B. The next B uses
the copied move; **L** discards it. Heavy hits retain the native chance to lose
the copy. Death, respawn and a new match clear it without changing your saved
recipe. Copying a custom fighter uses its selected Neutral B; copying native
Kirby uses his current ability. Native Kirby keeps Remix's own hats/copy rules.
The added held-L spit input applies to borrowed bodies; native Kirby retains
Remix's original A-spit controls.

Borrowed inhale uses the original donor catch sizes/reach and source event
timing with native body hurtboxes. Native wind follows the body's face and ends
when inhale stops. The added geometric mouth overlay has been removed.
L with a swallowed opponent uses the same donor spit, damage, release timing
and ownership path as A, on ground and in the air; it does not taunt or discard
an ability in that phase. L after copying emits the original discarded-copy star.
Full body/stretch poses and copied hats remain deferred. Native victim
shrink/hold/star-release states remain connected.

Start charging with **B**. **B or A** releases; **Z** stores. Ground rolls also
store charge. Fully charged Giant Punch blinks using the original color script,
including while walking or performing other moves. Releasing consumes the stored
charge and removes its flash; higher-priority native color effects remain in control.
Giant Punch applies queued input at the source cycle boundary.
Full charging stops and the next B releases. Charge Shot releases in the air,
including when leaving the floor during charging. Damage while charging clears
charge; a new fighter generation/match clears stored state.

Pressing B with a Boomerang already out plays the empty throw. Its native return
can enter the source catch phase in the interrupt window. Captures keep the
body's native victim rig; Egg Lay uses source anchors and native egg states.

Shared donor poses follow the source clock, including charge loops and release
transitions. Gameplay collision centers, reach and sizes stay independent of
the body rig. Body hurtboxes remain native. The held Charge Shot orb, blaster,
tongue, Falcon flames and safe source sound/voice/effect events are connected;
see [special effects](special-effects.md). Full rendered/material acceptance
and paired victim rotation remain separate work.

Private descriptors/resources keep these borrowed weapons independent of
Remix's native and expanded-fighter globals. Resources load before the match;
pressing B does not enter the file loader. Four existing presets remain intact:
the old neutral recipe bit stays fixed and validated full choices occupy unused
creator-options bytes. Pre-upgrade saves retain their native/Fox choices.

The standard build runs source/linked-data checks and MIPS adapter tests for
all original bodies, ground/air, four ports, charge cycles/storage/damage,
private weapon values and generation cleanup. SRAM packing checks translate
only two N64 DADDU register moves to equivalent ADDU in the MIPS32 fixture;
live editor checks retain the original N64 instructions and real save I/O. Optional
`scripts/test_charlab_scenes.py --neutral N --body B` checks real B input,
native callbacks and recovery with null rendering; choices 8/9 also exercise Z
storage and B release. `--egg-contact` checks controlled Egg Lay capture/egg
handoff/damage; `--projectile-contact` checks PK Fire spark/flame-pillar contact. These CPU checks do not establish rendered projectile,
contact, reflection/absorption, wall/ledge or full interruption acceptance.

The 0.1.19 inhale suite checks 88 foreign ground/air entries across four ports,
880 source catch placements, 176 A/L held-victim release selections, 528 copied-choice dispatches and 156 native/custom
victim choices. It executes source absorb flags at frame eight and copy loss,
taunt, death and generation cleanup without writing body passive memory.
`--neutral 12 --inhale-contact --inhale-held-l` checks actual capture/held ownership, A spit,
L held-victim spit, repeat capture/B copy, copied Fireball, L discard and aerial inhale/landing.
The held-L CPU fixture starts grounded and checks attacker survival/position and
victim ownership cleanup. Airborne A/L release selection is checked in linked
MIPS; broader native airborne contact and rendered acceptance remain pending.
Null-rendering scenes cover all eleven foreign original bodies, including
copied Mario Fireball and aerial inhale/landing; native Kirby also passes entry
and recovery. Broader rendered contact and interruption acceptance remain pending.

The 0.1.7 ROM passed real-input CPU scenes for all ten new choices and the
existing Fox Laser. Controlled PK Fire contact created its native flame pillar
and damage; controlled Egg Lay contact captured and egged the victim on Mario
and Kirby bodies. Giant Punch/Charge Shot scenes reused stored charge on release.
Editor-to-Training, Falcon Kick and two-dash Quick Attack regressions also passed.
These runs use null rendering; inspect the actual meshes and attached effects
in the emulator before marking visual acceptance complete.

See [port checklist](decomp-port.md) and [animation limits](animations.md).

The local 0.1.16 CPU regression `--body 0 --neutral 8 --full-charge` holds
Giant Punch through full charge, observes advancing native blink colors while
idle and moving, then confirms release consumes the charge and clears its flash.
This uses null rendering; rendered flash acceptance remains pending.
