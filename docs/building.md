# Build the two versions

Start from the repository root and initialize the pinned dependencies:

```bash
git submodule update --init --recursive
```

## Character Lab

Use x86-64 Ubuntu 22.04, or Windows with WSL/Ubuntu. Put the original US ROM at
`ssb-decomp-re/baserom.us.z64`; its SHA-1 must be
`e2929e10fccc0aa84e5776227e798abc07cedabf`.

Install setup prerequisites in Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv git
bash tools/build-character-lab.sh --setup --init --jobs 4
```

Windows entry point (after installing WSL/Ubuntu and those prerequisites):

```powershell
.\tools\build-character-lab.ps1 -Setup -Init -Jobs 4
```

Later, omit `--setup --init` / `-Setup -Init`. Add Init after changes to extraction
YAML or symbols. Both entry points run the existing host and ROM checks, package
the result and copy the checked files into root **dist/**:

| File | Purpose |
| --- | --- |
| `dist/character-lab.z64` | Checked ROM. |
| `dist/character-lab.zip` | ROM, play guide, checklist, changelog and metadata. |
| `dist/build-info.json` | Root repository commit and ROM checksum. |
| `dist/SHA256SUMS.txt` | Published-file checksums. |

The component's original `build/` and `dist/` outputs remain available too.
The Makefile's vanilla comparison prints `FAILURE` for an intentionally modified
ROM; the dedicated verifier must pass. See the
[detailed toolchain guide](../ssb-decomp-re/docs/building.md).

## Remix creator

This produces a separate ROM using the existing +EXTRA build system. Put the
original ROM at `remix/smashremix/roms/ssb.rom`. On Windows with Python 3.12+:

```powershell
Set-Location remix
.\build.bat
```

The build applies the versioned source overrides, including the Sonic creator
hook, during source generation. Its Python environment is recreated locally.
The ROM output is `remix/ssb64asm_extra.z64`.

`patch_extra.bat` also copies the result to `remix/dist/char_builder.z64`. To
add your own emulator folder, set `SMASH_EXTRA_ROM_DIR` before building.
See the [original Remix build guide](../remix/README.md) for Linux/Wine and the
[creator guide](../remix/character_creator_guide.md) for that version's menu.

Original/generated ROMs, tools, extraction assets and environments stay out of
Git. The two source folders share one root Git repository; do not initialize
new project repositories inside them.
