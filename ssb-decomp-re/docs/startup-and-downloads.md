# Startup and download checks

Version 0.1.13, updated 2026-10-04. Enable **8 MB RDRAM / Expansion Pak**.

The public `character-lab.z64`, root `dist/character-lab.z64` and Desktop
`smash-character-lab-full-roster.z64` are copies of one checked build. The release
publisher verifies their metadata/checksums and downloads the public ROM and ZIP
again after publishing. The latest ROM SHA-256 is recorded in the release's
`build-info.json` and `SHA256SUMS.txt`.

## The 0.1.7 black-screen regression

A byte-for-byte comparison confirmed that the reported downloaded
`character-lab (2).z64` matched the working-path ROM. The original download was
not truncated or a different build. An uninterrupted boot reproduced a game
bug: the opening room exhausted its lower-bank allocation arena before the
first update/render frame. Its heap pointer reached `0x80393ad0`, past the
`0x803903e0` limit, and the allocator entered its overflow loop.

The normal animation expansion increased static overlay memory and reduced the
space left for intro models and graphics. Previous CPU smoke tests jumped from
startup to Options, so they missed this allocation path. Reaching the menus
through a skipped intro did not establish successful uninterrupted boot.

All nineteen opening scenes now move their allocation arena into
Expansion Pak memory when it is present, using the existing
Training/VS heap helper. The original framebuffers, lower-bank overlays, SDK
addresses and normal animation/collision tables are preserved.

## The 0.1.13 pose bank

The special animation expansion exposed another memory boundary: keeping the
larger compressed pose pool inside the fighter overlay moved dependent game
code past the fixed `0x80392a00` framebuffer start. The uninterrupted boot check
caught this before publication. Pose keys now occupy a separate ROM section
loaded into the Expansion Pak; scene heaps start after that reserved bank.
Original lower-bank overlays and video buffer addresses remain separate.
The linker and ROM verifier reject overlaps, and the cold-boot test checks the
new heap boundary through every intro scene. The existing 4 MB launch guard
still applies; gameplay requires 8 MB.

## Regression checks

The 0.1.13 build passed uninterrupted boot through all nineteen opening scenes,
title and Start into the main menu, with at least 1,090,624 bytes of opening heap
headroom. Its 4 MB Training launch guard passed. Live charge/store/full-release
and Luigi Up B checks passed on the final build, including same-editor returns
and four assigned builds in VS. The mixed twelve-normal-donor preload regression
retained at least 429,876 bytes of Training heap headroom. Special pose/phase,
Mario Up B, normal-animation and remaining-special regressions also passed on
the new memory layout. These are CPU execution checks with null rendering;
rendered acceptance remains pending.

The 0.1.13 ROM is 19,077,584 bytes, with SHA-256
`62c6277c1d5e844093fff60976e8957ac521906358deb35c355d5383cdbffb36`.

The 0.1.12 normal-mechanics build passed uninterrupted boot through all nineteen
opening scenes, title and Start into the main menu. Opening heap headroom
remains at least 2,309,952 bytes. Its normal-mechanics CPU sweep passed all 144
donor/body jab chains, twelve controlled Link bounces/Ness bat reflections,
editor returns and four assigned VS builds. Training retained at least
1,641,264 bytes of headroom with all twelve normal donor files selected.

The new donor attribute/model preloads exposed the old 100-entry Training/VS
asset-cache limit, which stopped loading before the first Training update.
Both caches now have 512 entries. With 4 MB, startup skips the resource-heavy
intro to keep menus and their existing 8 MB requirement reachable. The 4 MB
Test in Training guard passed without a heap overflow. With 8 MB, the full
intro still plays. The native allocator/SDK addresses remain
unchanged; selected donor files and Ness's bat motion file fit without cache
exhaustion. These are CPU execution checks with null rendering; rendered
acceptance remains pending.

The final build also passed four Mario donor animation catalogs, Mario Up B
ground/air paths and recovery, Ness steering/self-contact/recovery, editor
returns and assigned four-player VS. These regressions caught an interrupted
Egg Lay release reading a missing throw descriptor; its original donor
escape values are now generated and installed before capture. Customized
grabs retain the body script that provides native release setup.

The 0.1.12 ROM is 18,491,024 bytes, with SHA-256
`adc5910f7ae81bbf23b067170dc460a3b446fa925447225b7446aa47772036b7`.

The 0.1.11 mechanics build also moves stage selection into the Expansion Pak
arena. It passed uninterrupted boot through all nineteen opening scenes, title
and Start into the main menu, the 4 MB Training guard, Mario and Ness Up B
regressions, four Mario normal-animation catalogs, editor returns and four-slot
VS. Its opening heap retained at least 2,309,952 bytes of headroom. These are
CPU execution checks with null rendering; rendered acceptance remains pending.
The ROM is 18,473,952 bytes, with SHA-256
`e3746a295b5b33973ffd0ae5c24881813112b642471efdd0c042fc13fe40c56b`.

The 0.1.8 ROM passed uninterrupted boot through all nineteen opening scenes,
the title screen and Start into the main menu. The opening heap retained at
least 2,309,952 bytes of headroom. The checked ROM is 18,220,016 bytes; its
SHA-256 is `ea44caee841fa7e79303b3ab7c03a6059913f1fce0af44fc26dffd1cfab0c171`.
The post-fix gameplay check also passed Mario with all eleven foreign normal
donors (1,288 live poses), Training back into the same editor, and a four-build
VS match with three CPUs. Training retained 1,975,436 bytes of heap headroom.
The 4 MB Training launch guard also passed; gameplay still requires 8 MB.

After a checked build, run the optional isolated Mupen64Plus CPU test:

```bash
python3 tools/testTrainingScenes.py --boot
```

It lets startup and the whole intro run normally, checks all nineteen opening
scenes and allocation bounds, requires progress to the title, and presses Start
through the real input handler to reach the main menu. It rejects a stopped
intro even if there is no CPU exception. Null rendering checks game execution;
rendered acceptance remains a separate check.

To run the same check against a downloaded file:

```bash
python3 tools/testTrainingScenes.py --boot --rom /path/to/character-lab.z64
```

The `--rom` option requires an exact match with the current build/ELF before
checking emulator memory. Core/plugin paths can be supplied with `--core`,
`--rsp`, `--headers` and `--data`, as in the other scene smoke tests.

`verifyCustomMoveRom.py` also verifies all nineteen linked opening functions
contain the Expansion Pak helper call, along with the normal source tables,
shared animation data, gameplay code and N64 CRC.
