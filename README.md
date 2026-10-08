# Smash Character Builder

**Project version: 0.1.31 (experimental)** | **Last updated: 2026-10-08**

Pick a fighter's body, borrow moves from other characters, and see what happens.
A fun Smash 64 project for friends, with two experiments living in one repository.

| Edition | Where it lives | What to expect |
| --- | --- | --- |
| **Character Lab** | [ssb-decomp-re/](ssb-decomp-re/README.md) | Our current original-roster build: twelve bodies, editable normal attacks, grabs/throws, VS assignments and Training hitbox view. |
| **Character Lab on Remix** | [remix/](remix/README.md) | Original-roster donor paths/timing, grabs/throws, eleven neutral donors, saved recipes and Training return on Smash Remix +EXTRA. Expanded-roster fidelity remains pending. |

These produce separate ROMs. Combining the source folders does not combine their
game engines or make features automatically carry between them.

Character Lab includes donor tether reach, grab/pull timing and paired
forward/back throws on every original body. DK cargo carry and Kirby's landing
throw retain their own mechanics. Attacker poses share the animation catalog;
victims keep their native rigs and donor-selected capture/throw states.
See [tether grabs and paired throws](ssb-decomp-re/docs/paired-grabs-and-throws.md).
Rendered contact and visual polish remain on the checklist.

**[How to play Character Lab](ssb-decomp-re/docs/playing.md)** |
**[Done / not done](docs/status.md)** | **[Build guide](docs/building.md)** |
**[Changes](CHANGELOG.md)**

Taunts are now customizable too: choose **TAUNT**, then press **L** in-game.
Donor poses, duration/cancel windows and Luigi's 1-damage hitbox follow the selection.
See [taunt controls](ssb-decomp-re/docs/custom-taunts.md).
Mario's borrowed taunt now grows and shrinks the selected body on the original
timeline. VS starts with **4 stocks, items off**; the results-screen memory fix
restores match endings and rematches.

## Downloads

| Build | ROM last updated | ROM download | Play package | Source build |
| --- | --- | --- | --- | --- |
| **Character Lab** | 2026-10-05 | [character-lab.z64](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.z64) | [character-lab.zip](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/character-lab.zip) | [Exact build metadata](https://github.com/lorenzosaraiva/smash-charbuilder/releases/latest/download/build-info.json) |
| **Character Lab on Remix (preview 0.1.14)** | 2026-10-08 | [remix-character-lab.z64](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-character-lab.z64) | [remix-character-lab.zip](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-character-lab.zip) | [Exact build metadata](https://github.com/lorenzosaraiva/smash-charbuilder/releases/download/remix-preview/remix-build-info.json) |

Dates use Sao Paulo time and refer to the published ROMs. The project version
above tracks this repository; each source build identifies the exact ROM.
[Browse all releases](https://github.com/lorenzosaraiva/smash-charbuilder/releases).

The ZIP includes a play guide, feature checklist, changelog and commit/checksum
information. The first release was built and checked locally. Automatic updates
after successful pushes to `main` still need the one-time
[original-ROM build-source setup](docs/releases.md).

Open **Settings -> Character Lab** and keep **Original 12 Only** on. See the
[Remix play guide](remix/character_creator_guide.md) and
[port checklist](remix/docs/character-lab-status.md). The preview is published
locally; automatic hosted Remix builds remain pending.

Remix 0.1.14 draws borrowed fighter parts in the native fighter pass and
restores its one-cycle state afterward, addressing noisy tether textures and
white stage layers. Beam materials advance once per frame. Native material
submission and exit state have regression checks; rendered acceptance of this
fix remains pending.

Remix **0.1.14** fixes duplicate Samus bombs on DK and other foreign bodies:
one Down B creates one bomb, and ground/air transitions cannot replay the spawn.
Fresh inputs still create new bombs on Samus's source timeline.
It retains both DK/Samus borrowed down-smash fixes and adds Samus
Bomb's Morph Ball and the missing tether glow on foreign bodies. DK Down B
keeps its original two slaps in one cycle; another cycle requires another B tap.
Automated checks pass; rendered visual acceptance remains pending.
It also retains fixes for borrowed Mario taunt growth around planted feet, updates
Neutral B when choosing **All moves from body**, and rejects unavailable aerial
donor specials without falling back to the body's move. See
[special edge-case checks and remaining acceptance](remix/docs/special-edge-cases.md).
The preview includes donor tether pulls, paired throws, DK cargo, Kirby lift/fall/landing
and customizable taunts, including Mario growth/shrink and Luigi damage. See
[grab, throw and taunt controls](remix/docs/paired-grabs-and-taunts.md). It retains Cutter sword/trails, Stone replacement, Falcon flames,
Fox blaster, Yoshi tongue and Samus's charging orb, with source clocks and
owned cleanup. See [effects and attachments](remix/docs/special-effects.md).
It includes every original Neutral B donor except Kirby copy, with source
projectiles, Punch/Pound, charge storage/release, Boomerang and Egg Lay.
See [neutral controls and limits](remix/docs/neutral-specials.md). It also ports donor jab chains, Link bounce, Ness bat reflection,
normal physics and landing behavior. It retargets the decomp's shared normal and supported special/recovery
poses onto all twelve original bodies. Selected clips stream from ROM into
separate 15 KB player caches; timing, donor collision paths and world movement
remain independent of the visual pose. The three Mario pilots are preserved.
See [Remix animations](remix/docs/animations.md) for coverage and rendered acceptance.
This is a partial port: the [decomp-to-Remix feature matrix](remix/docs/decomp-port.md)
lists every remaining special, animation, neutral, normal acceptance and paired
grab/throw milestone. The decomp download remains **0.1.18**.

## Make your first Character Lab build

1. Set your N64 emulator to **8 MB RDRAM / Expansion Pak**, then open the Character Lab ROM.
2. Go to **Options -> Character Lab**, then select one of four builds with **A**.
3. Choose a **Body** and change moves with **left/right**.
4. Use **Test in Training**. Leaving the test returns to that build's editor.
5. For VS, assign builds to human/CPU player slots and select **Play VS**.

In Training, press **Start -> View -> HITBOX** to see attack and hurtbox outlines.
Grabs preserve the current combo count and damage through the hold and throw.
Presets in this version last for the running ROM session.

**Build One** now starts with a **Yoshi** body and the requested mixed moveset,
including **Fox Laser**, **Pikachu Up B**, **Fox Down B** and **Mario Taunt**.
See the [complete starter recipe](ssb-decomp-re/docs/playing.md#default-build-one).

Borrowed normal attacks now read the native root-movement flag correctly,
restoring Fox dash attack and Kirby forward-smash travel on Yoshi and other bodies.
See the [movement checks](ssb-decomp-re/docs/normal-mechanics.md).

Character Lab's **Neutral B** row now offers **Body Move**, **Fox Laser**,
**Mario Fireball**, **Luigi Fireball**, **Thunder Jolt**, **PK Fire**, **Falcon Punch**,
**Pound**, **Giant Punch**, **Charge Shot**, **Boomerang** and **Egg Lay**.
These donors work across all twelve bodies with source timing and collision data,
charge storage, returning boomerangs and capture/egg handoff. Borrowed animations
now adapt donor poses to the body; the new choices are decomp only. See the
[neutral controls and limits](ssb-decomp-re/docs/neutral-specials.md).

Borrowed **Up B/Down B** use donor phase clocks and shared donor poses.
DK Down B, DK Up B, Mario/Luigi Tornado and Falcon Kick now have source collision
paths and numeric attack values independent of the body pose. Falcon Kick uses
source movement; spin/Tornado physics use donor values. Ness Up B uses its donor
spawn socket and 28-tick self-launch timeline, with independent weapon state.
The remaining specials now use native mechanics and source paths/sockets too;
rendered animation/contact acceptance remains pending. See the
[special timing notes](ssb-decomp-re/docs/special-timing.md).

Mario/Luigi **Up B** now use their original ground/air collision paths, distinct
hit phases, donor movement and steering, helpless recovery physics and 25-tick
landing recovery on other bodies, with shared rise/fall/landing animations.
See the [Super Jump Punch guide](ssb-decomp-re/docs/super-jump-punch.md).

Training and VS now allocate their heaps in the Expansion Pak bank, fixing the
character-selection allocation overflow behind the Test in Training freeze.
Version 0.1.8 also moves all opening movie heaps into that bank to fix a
black-screen intro overflow. Public downloads and the local ROM use the same
checked binary; see the [startup checks](ssb-decomp-re/docs/startup-and-downloads.md).

Every normal donor attack now uses its original hitbox path, size, active timing,
damage and knockback on the other bodies, including angled variants and landing
hitboxes. **All twelve bodies now perform all twelve donors' normal attacks**,
including angled variants, aerial landings and body-supported jab phases. Shared
donor curves adapt to each body's skeleton and proportions. Implemented specials
share that catalog. Grabs/throws retain donor paths, paired positioning and
release mechanics, with shared attacker poses and native victim rigs. See the
[full animation guide](ssb-decomp-re/docs/full-roster-animations.md), the
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
