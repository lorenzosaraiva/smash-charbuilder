# Playing Character Lab

## Start here

Download the latest play package, unzip it, and open `character-lab.z64` in an N64
emulator. RMG-K has been used for local playtesting. Other emulator and real-hardware
compatibility still need reports. If you already had an older ROM open, reopen it
to load the new build.

The ZIP's `build-info.json` identifies the source commit. Include that commit when
reporting a bug; two downloads named `character-lab.z64` can be different builds.

## The character editor

Open **Options -> Character Lab**. Pick Build One, Two, Three or Four with **A**.
Use **up/down** to move through the rows and **left/right** to change a value.
The body is the fighter whose model you play. Attack rows choose the donor whose
attack values and timing you want to use.

**Use Body For All** restores that body's moves. **Randomize Attacks** makes a
mix. **B** returns to the lab's main screen.

Neutral B currently switches between **Body Move** and **Fox Laser**. The full
neutral-special donor roster is unfinished. Up B and Down B use earlier adapters
and may have rough combinations.

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
angled variants, weapon/tail attacks, multihits and landing hitboxes. The body
keeps its visible pose outside the three Mario animation pilots.

For an easy comparison, choose **DK Body -> Up Tilt: Kirby**, then
**Test in Training -> View: HITBOX**. The two hitboxes follow Kirby's original
up-tilt path and duration while DK keeps his own pose. The same donor path also
works on the other bodies. Compare with a vanilla Kirby up-tilt at the same
fighter position and facing; visual acceptance is still pending. See the
[coverage and comparison guide](collision-trajectories.md).

Also try **Kirby Body -> Up Air: Falcon -> Test in Training -> View: HITBOX**.
The hitboxes follow Falcon's original upward kick while Kirby keeps his own
up-air pose. The same Falcon path works on every foreign body.

Builds and assignments last for the running ROM session and reset when the ROM
restarts. Most attack animations still come from the body. Throws copy donor
damage/knockback but retain body choreography; DK skips cargo when another fighter's
forward throw is selected. The [checklist](status.md) explains the remaining gaps.

For the animation pilot, choose a Mario body with Falcon Down Air, Fox Forward
Tilt or DK Forward Smash. The tilt/smash pilots cover the straight variants only;
angled poses stay native. Visual acceptance is still pending.
