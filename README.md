# Smash Character Builder

Pick a fighter's body, borrow moves from other characters, and see what happens.
A fun Smash 64 project for friends, with two experiments living in one repository.

| Version | Where it lives | What to expect |
| --- | --- | --- |
| **Character Lab** | [ssb-decomp-re/](ssb-decomp-re/README.md) | Our current original-roster build: twelve bodies, editable normal attacks, grabs/throws, VS assignments and Training hitbox view. |
| **Remix creator** | [remix/](remix/README.md) | The earlier Smash Remix +EXTRA experiment, with its larger compiled roster and saved creator recipes. Its compatibility rules differ from Character Lab. |

These produce separate ROMs. Combining the source folders does not combine their
game engines or make features automatically carry between them.

**[How to play Character Lab](ssb-decomp-re/docs/playing.md)** |
**[Done / not done](docs/status.md)** | **[Build guide](docs/building.md)** |
**[Changes](CHANGELOG.md)**

## Downloads

The permanent Character Lab links are:

- [Play package: character-lab.zip](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.zip)
- [ROM only: character-lab.z64](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.z64)
- [All releases](https://github.com/lorenzosaraiva/smash-charbuilder/releases)

The ZIP includes a play guide, feature checklist, changelog and commit/checksum
information. The first release was built and checked locally. Automatic updates
after successful pushes to `main` still need the one-time
[original-ROM build-source setup](docs/releases.md).

## Make your first Character Lab build

1. Open the Character Lab ROM in your N64 emulator.
2. Go to **Options -> Character Lab**, then select one of four builds with **A**.
3. Choose a **Body** and change moves with **left/right**.
4. Use **Test in Training**. Leaving the test returns to that build's editor.
5. For VS, assign builds to human/CPU player slots and select **Play VS**.

In Training, press **Start -> View -> HITBOX** to see attack and hurtbox outlines.
Presets in this version last for the running ROM session.

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
[build guide](docs/building.md) also covers the separate Remix build.

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
