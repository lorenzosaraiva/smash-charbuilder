# Smash 64 Character Lab

Pick a fighter's body, mix in moves from the other Smash 64 characters, and try
your creation against friends or a CPU. A little experiment that got out of hand.

Version **0.1.9**, updated **2026-10-04**. All twelve bodies now perform all twelve
donors' normal attacks through shared motion curves and body skeleton maps.
Hitboxes and timing follow the donor independently of body proportions. This is
still experimental; special, tether and paired throw animations need more work.

Mario/Luigi Up B now borrow source hitbox paths, movement, steering, hit phases
and helpless/landing recovery. See [coverage and testing](docs/super-jump-punch.md).

**[How to play](docs/playing.md)** | **[Done / not done](docs/status.md)** |
**[Build it yourself](docs/building.md)** | **[What's changed](CHANGELOG.md)**

## Download

This codebase is part of [Smash Character Builder](../README.md). Downloads use
the combined project's [releases](https://github.com/lorenzosaraiva/smash-charbuilder/releases)
and the root workflow described in the [download setup](../docs/releases.md).
The checked local release is available now. Automatic releases after pushes
still require the original-ROM build-source setup.

Grab [character-lab.zip](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.zip)
for the ROM, a quick play guide, checklist and build information, or download
[character-lab.z64](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.z64)
directly. These permanent links follow the latest checked release.

## Make your first character

1. Open the ROM in your N64 emulator.
2. Go to **Options -> Character Lab** and choose one of the four builds with **A**.
3. Choose a **Body**, then change moves with **left/right**.
4. Choose **Test in Training** to try it. Leaving the training test brings you
   back to that build's editor.
5. For VS, return to the lab's main screen, assign builds to player slots, then
   choose **Play VS**. A slot can be human or CPU.

In Training, press **Start -> View -> HITBOX** to see attack and hurtbox outlines.
Grabs preserve the current combo count and damage through the hold and throw.
Creator builds currently last for the running ROM session.

## What's in it?

- Twelve original fighter bodies and all thirteen normal attack families.
- Custom grab and forward/back throw selections.
- Four builds, assigned independently to human or CPU slots.
- Training hitbox view, quick return to the editor, unlockable fighters and Item Switch.
- Neutral B: **Body Move** and every non-copy original neutral donor, including charging, returning boomerangs and Egg Lay. See [controls and limits](docs/neutral-specials.md); Up B/Down B remain experimental.
- Up/Down B: donor timing, DK slaps/spin, Mario/Luigi Tornado and Falcon Kick collision paths/movement, and Ness projectile socket/self-launch timing. See [coverage and limits](docs/special-timing.md).
- **8 MB RDRAM / Expansion Pak required**: Training/VS selection and match resources use the upper memory bank.
- All twelve donor normal animations on all twelve bodies, angled variants,
  aerial landings and body-supported jab phases. See the
  [animation guide](docs/full-roster-animations.md).
- Original donor hitbox paths for the complete normal roster on every foreign
  body, including angled variants, weapon/tail attacks, multihits and landing
  hitboxes. See the [collision guide](docs/collision-trajectories.md).

The [checkbox list](docs/status.md) covers what is implemented, what still needs
playtesting and what is missing. In particular, throws currently copy donor
damage/knockback with body choreography; donor special animations remain unfinished.

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

Borrowed Up/Down B now use donor phase clocks and temporary idle/falling poses.
See [special timing and remaining limits](docs/special-timing.md).
