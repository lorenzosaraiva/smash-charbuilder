# Smash Character Builder

**Project version: 0.1.4 (experimental)** | **Last updated: 2026-10-03**

Pick a fighter's body, borrow moves from other characters, and see what happens.
A fun Smash 64 project for friends, with two experiments living in one repository.

| Edition | Where it lives | What to expect |
| --- | --- | --- |
| **Character Lab** | [ssb-decomp-re/](ssb-decomp-re/README.md) | Our current original-roster build: twelve bodies, editable normal attacks, grabs/throws, VS assignments and Training hitbox view. |
| **Character Lab on Remix** | [remix/](remix/README.md) | Original-roster donor paths/timing, grabs/throws, laser choice, saved recipes and Training return on Smash Remix +EXTRA. Expanded-roster fidelity remains pending. |

These produce separate ROMs. Combining the source folders does not combine their
game engines or make features automatically carry between them.

**[How to play Character Lab](ssb-decomp-re/docs/playing.md)** |
**[Done / not done](docs/status.md)** | **[Build guide](docs/building.md)** |
**[Changes](CHANGELOG.md)**

## Downloads

| Build | ROM last updated | ROM download | Play package | Source build |
| --- | --- | --- | --- | --- |
| **Character Lab** | 2026-10-03 | [character-lab.z64](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.z64) | [character-lab.zip](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.zip) | [Exact build metadata](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/build-info.json) |
| **Character Lab on Remix (preview)** | 2026-10-03 | [remix-character-lab.z64](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-character-lab.z64) | [remix-character-lab.zip](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-character-lab.zip) | [Exact build metadata](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-build-info.json) |

Dates use Sao Paulo time and refer to the published ROMs. The project version
above tracks this repository; each source build identifies the exact ROM.
[Browse all releases](https://github.com/lorenzosaraiva/smash-charbuilder/releases).

The ZIP includes a play guide, feature checklist, changelog and commit/checksum
information. The first release was built and checked locally. Automatic updates
after successful pushes to `main` still need the one-time
[original-ROM build-source setup](docs/releases.md).

Open **Settings -> CHARACTER LAB** and keep **Original 12 Only** on. See the
[Remix play guide](remix/character_creator_guide.md) and
[port checklist](remix/docs/character-lab-status.md). The preview is published
locally; automatic hosted Remix builds remain pending.

## Make your first Character Lab build

1. Set your N64 emulator to **8 MB RDRAM / Expansion Pak**, then open the Character Lab ROM.
2. Go to **Options -> Character Lab**, then select one of four builds with **A**.
3. Choose a **Body** and change moves with **left/right**.
4. Use **Test in Training**. Leaving the test returns to that build's editor.
5. For VS, assign builds to human/CPU player slots and select **Play VS**.

In Training, press **Start -> View -> HITBOX** to see attack and hurtbox outlines.
Grabs preserve the current combo count and damage through the hold and throw.
Presets in this version last for the running ROM session.

Character Lab's **Neutral B** row now offers **Body Move**, **Fox Laser**,
**Mario Fireball**, **Luigi Fireball**, **Thunder Jolt**, **PK Fire**, **Falcon Punch**,
**Pound**, **Giant Punch**, **Charge Shot**, **Boomerang** and **Egg Lay**.
These donors work across all twelve bodies with source timing and collision data,
charge storage, returning boomerangs and capture/egg handoff. Borrowed animations
still use body poses; the new choices are decomp only. See the
[neutral controls and limits](ssb-decomp-re/docs/neutral-specials.md).

Borrowed **Up B/Down B** use donor phase clocks with temporary idle/falling poses.
DK Down B's slap windows/repeats follow DK's timing, and the Ness Up B asset-loading
freeze on foreign bodies is fixed. These specials still need broader collision and
movement work; see the [special timing notes](ssb-decomp-re/docs/special-timing.md).

Training and VS now allocate their heaps in the Expansion Pak bank, fixing the
character-selection allocation overflow behind the Test in Training freeze.

Every normal donor attack now uses its original hitbox path, size, active timing,
damage and knockback on the other bodies, including angled variants and landing
hitboxes. Most visible animations still belong to the body; the three Mario
animation pilots remain available. See the
[collision guide](ssb-decomp-re/docs/collision-trajectories.md) and
[checklist](ssb-decomp-re/docs/status.md). Broader in-game acceptance is pending.

## Build from this folder

Clone the project with its build dependencies:

```bash
git clone --recurse-submodules https://github.com/lorenzosaraiva/smash-charbuilder.git
cd smash-charbuilder
```

Character Lab, on Linux or WSL/Ubuntu:

```bash
bash tools/build-character-lab.sh --setup --init --jobs 4
```

Or from Windows PowerShell with WSL/Ubuntu:

```powershell
.\tools\build-character-lab.ps1 -Setup -Init -Jobs 4
```

Put the original US ROM at `ssb-decomp-re/baserom.us.z64` first. The checked ROM
and shareable ZIP appear in **dist/**. For later builds, omit Setup/Init. The
[build guide](docs/building.md) also covers the separate Remix build, using
`tools/build-remix-character-lab.ps1`.

## Bugs and ideas

Try unusual combinations and tell us what breaks. Use **Issues -> New issue**
and include the version, build commit, emulator, body, donor and attack. A clip
helps with animation problems. Small fixes and gameplay reports are welcome;
see [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

Built on [VetriTheRetri's ssb-decomp-re](https://github.com/VetriTheRetri/ssb-decomp-re),
[Smash Remix +EXTRA](https://github.com/joaorb64/smashremix-plus-extra),
[Smash Remix](https://github.com/JSsixtyfour/smashremix), and their communities.
This is an unofficial fan project. Original authorship and available license
files remain with the imported sources and dependencies.

The [repository guide](docs/repository.md) explains the folder layout and preserved
histories. Build dependencies remain pinned submodules; both creator codebases
are ordinary folders owned by this repository.
