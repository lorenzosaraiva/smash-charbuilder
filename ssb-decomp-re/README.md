# Smash 64 Character Lab

Pick a fighter's body, mix in moves from the other Smash 64 characters, and try
your creation against friends or a CPU. A little experiment that got out of hand.

This is a fun project, and it is still rough around the edges. Most combinations
use the selected body's animations with the donor's attack values and timing.
Full donor animations on other bodies are the dream; three Mario moves have an
initial animation pilot so far.

**[How to play](docs/playing.md)** · **[Done / not done](docs/status.md)** ·
**[Build it yourself](docs/building.md)** · **[What's changed](CHANGELOG.md)**

## Download

This codebase is part of [Smash Character Builder](../README.md). Downloads use
the combined project's [releases](https://github.com/lorenzosaraiva/smash-charbuilder/releases)
and the root workflow described in the [download setup](../docs/releases.md). Once enabled, every
successful push to `main` publishes a new build with the same download filenames.

Grab **character-lab.zip** for the ROM, a quick play guide, the feature checklist
and build information. If you only need the ROM, use **character-lab.z64**.
The permanent links are shown in each successful release workflow's summary.

The existing Google Drive copy can stay available while GitHub downloads are
being set up.

## Make your first character

1. Open the ROM in your N64 emulator.
2. Go to **Options -> Character Lab** and choose one of the four builds with **A**.
3. Choose a **Body**, then change moves with **left/right**.
4. Choose **Test in Training** to try it. Leaving the training test brings you
   back to that build's editor.
5. For VS, return to the lab's main screen, assign builds to player slots, then
   choose **Play VS**. A slot can be human or CPU.

In Training, press **Start -> View -> HITBOX** to see attack and hurtbox outlines.
Creator builds currently last for the running ROM session.

## What's in it?

- Twelve original fighter bodies and all thirteen normal attack families.
- Custom grab and forward/back throw selections.
- Four builds, assigned independently to human or CPU slots.
- Training hitbox view, quick return to the editor, unlockable fighters and Item Switch.
- Neutral B choice between **Body Move** and **Fox Laser**; experimental Up B/Down B adapters.
- Three Mario animation pilots: Falcon down air, Fox straight forward tilt,
  DK straight forward smash.
- Original hitbox paths across bodies for Kirby up-tilt and those three straight
  pilot attacks, independently of visible animations. See the
  [collision guide](docs/collision-trajectories.md) for coverage and how to compare.

The [checkbox list](docs/status.md) covers what is implemented, what still needs
playtesting and what is missing. In particular, throws currently copy donor
damage/knockback with body choreography, and most donor animations are unfinished.

## Build a ROM inside this repo

With the original US ROM and the toolchain set up:

```bash
bash tools/build-character-lab.sh
```

On Windows with WSL/Ubuntu:

```powershell
.\tools\build-character-lab.ps1
```

The checked ROM and shareable ZIP appear in **dist/**. Generated ROMs, original
ROMs and build files stay out of Git history. Root build entry points also copy
these files into the combined project's `dist/`. See the [build guide](docs/building.md)
for the first-time setup and the [release guide](docs/releases.md) for automation.

## Bugs, ideas and helping out

Try silly combinations. Tell us what breaks. A useful report includes the body,
donor, attack, emulator and download/build commit; a clip is great too. In GitHub
**Issues -> New issue**, choose **Something broke** or **An idea**.

Code changes and gameplay feedback are welcome. Please include how you checked a
change; see [CONTRIBUTING.md](CONTRIBUTING.md) for a small guide.

## Thanks

Built on [VetriTheRetri's ssb-decomp-re](https://github.com/VetriTheRetri/ssb-decomp-re)
and the Smash 64 decompilation community's work. The original
[decompilation README](docs/decompilation.md) and detailed
[gameplay](docs/custom-move-roster.md) / [animation](docs/animation-retargeting-pilot.md)
notes are kept for people who want to dig into the implementation.
