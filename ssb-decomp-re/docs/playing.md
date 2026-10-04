# Playing Character Lab

## Start here

Download the latest play package, unzip it, and open `character-lab.z64` in an N64
emulator. RMG-K has been used for local playtesting. Other emulator and real-hardware
compatibility still need reports. If you already had an older ROM open, reopen it
to load the new build. Set **8 MB RDRAM / Expansion Pak** in emulator settings.
Training and VS use that extra bank for preview and match resources; the editor
shows a memory requirement and blocks Test/Play VS on a 4 MB configuration.

The ZIP's `build-info.json` identifies the source commit. Include that commit when
reporting a bug; two downloads named `character-lab.z64` can be different builds.

## The character editor

Open **Options -> Character Lab**. Pick Build One, Two, Three or Four with **A**.
Use **up/down** to move through the rows and **left/right** to change a value.
The body is the fighter whose model you play. Attack rows choose the donor whose
attack values and timing you want to use.

**Use Body For All** restores that body's moves. **Randomize Attacks** makes a
mix. **B** returns to the lab's main screen.

Neutral B cycles through **Body Move**, **Fox Laser**, **Mario Fireball**,
**Luigi Fireball**, **Thunder Jolt**, **PK Fire**, **Falcon Punch**, **Pound**,
**Giant Punch**, **Charge Shot**, **Boomerang** and **Egg Lay**. Donor choices work
on any original body; selecting its own donor keeps the native move. Borrowed
shots use original spawn positions, firing/recovery timing and native weapon
behavior, while visible poses remain the body's. Landing or leaving an edge
continues the action without a second shot.

| Projectile | Ground/air firing frame | Ground/air recovery duration |
| --- | --- | --- |
| Mario Fireball | 16 / 16 | 46 / 46 |
| Luigi Fireball | 16 / 16 | 46 / 46 |
| Thunder Jolt | 21 / 21 | 64 / 64 |
| PK Fire | 20 / 20 | 72 / 60 |

Charge/store/release, returning boomerangs, donor melee paths/movement and Egg Lay
capture/egg handoff now have dedicated adapters. See [neutral controls](neutral-specials.md)
for charge controls and visual limits. Kirby's copy system is excluded. Rendered
contact/reflection/absorption acceptance remains pending; report body/donor, ground
or air, and emulator when something breaks. Up B and Down B use donor phase clocks
with temporary idle/falling poses; broader fidelity remains experimental.

## Training

Choose **Test in Training** from the editor, then select your training opponent
and stage through the usual screens. The edited build is assigned to player one.

Press **Start**, find **View**, and change it to **HITBOX**. Red attack outlines
and hurtbox visualization help you see what is happening. NORMAL/CLOSE UP restore
ordinary rendering.

Grabbing the opponent keeps the current combo count and damage while they are
held, carried or waiting for the throw. Throw damage adds to that combo; the
counter resets after release and hitstun end. A grab by itself adds no hit or
damage. This applies to native fighters and creator builds in Training.

To check it in-game, land a hit and grab before the opponent recovers, wait in
the hold, then throw. Check that the count/damage survive the hold and increase
on the throw. Also check a grab escape and a recovered opponent reset the meter.
Automated counter tests pass; rendered gameplay acceptance remains pending.

Leaving the test through the pause menu, or using **Back** on its character-select
screen, reopens the same build's editor with **Test in Training** selected. Resetting
the training match keeps that return destination.

## VS and custom CPU opponents

On the lab's main screen, change **Player One/Two/Three/Four** to a build or
**Vanilla**, then choose **Play VS**. These are player/controller slots, not team
colors. Use the game's usual player-type control to make a slot CPU.

Keep the assigned build's body selected on character select. Choosing another
body plays that fighter normally. Two slots can use different builds with the
same body, or share a build.

## Expectations

Normal attacks now follow their donor collision paths on every body, including
angled variants, weapon/tail attacks, multihits and landing hitboxes. All twelve bodies now visibly follow all twelve donors'
normal poses; see the [animation coverage](full-roster-animations.md).

For an easy comparison, choose **DK Body -> Up Tilt: Kirby**, then
**Test in Training -> View: HITBOX**. The two hitboxes follow Kirby's original
up-tilt path and duration while DK performs the retargeted Kirby pose. The same donor path also
works on the other bodies. Compare with a vanilla Kirby up-tilt at the same
fighter position and facing; visual acceptance is still pending. See the
[coverage and comparison guide](collision-trajectories.md).

Also try **Kirby Body -> Up Air: Falcon -> Test in Training -> View: HITBOX**.
The hitboxes follow Falcon's original upward kick while Kirby performs the
retargeted Falcon pose. The same Falcon path works on every foreign body.

Builds and assignments last for the running ROM session and reset when the ROM
restarts. Specials still use body or temporary poses. Throws copy donor
damage/knockback but retain body choreography; DK skips cargo when another fighter's
forward throw is selected. The [checklist](status.md) explains the remaining gaps.

For donor animations, choose a Mario body and Fox, DK, Luigi or Falcon for any
normal attack row. Angled attacks and aerial landing poses are included. Try
Falcon Up Air, Fox Up Smash or DK Down Smash. Visual acceptance is still pending.

Borrowed Up/Down B currently use idle/falling poses while their donor phase clocks
control duration and events. DK Down B keeps both original slap windows; tap B
again during a cycle to queue another cycle. Ness Up B now loads its wave/trail
assets on other bodies. DK Up B, Mario/Luigi Tornado and Falcon Kick now keep donor
hitbox paths and numeric values independent of those poses. Falcon Kick uses its
original movement, and Ness uses its original projectile socket/self-launch
clock. Tap B during Tornado to rise. See [coverage and limits](special-timing.md).
