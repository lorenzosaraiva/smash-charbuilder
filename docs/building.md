# Build the two versions

Start from the repository root and initialize the pinned dependencies:

```bash
git submodule update --init --recursive
```

## Character Lab

The finished decomp ROM requires **8 MB RDRAM / Expansion Pak** enabled in the
emulator. Opening movies, Training/VS selection and matches use the upper bank
for their heap. The optional [uninterrupted startup check](../ssb-decomp-re/docs/startup-and-downloads.md)
also tests an identical downloaded ROM through the full intro and title into
the main menu.

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

## Character Lab on Remix

Use Python 3.12+ on Windows with WSL/Ubuntu. In Ubuntu install `clang`,
`gcc-multilib` and `build-essential`. Put the original US ROM (the SHA-1 above)
at `remix/smashremix/roms/ssb.rom`. Initialize the pinned submodules first.

```powershell
.\tools\build-remix-character-lab.ps1 -Setup
```

Setup installs the locked Remix Python dependencies and the pinned Unicorn
execution-test dependency. Later omit Setup. `-Distribution` selects WSL;
`-RomDirectory` changes the Desktop copy destination. By default it is
`C:\Users\Lorenzo\Desktop\Smash 64\roms\smash-character-lab-remix.z64`.

The full build regenerates assets/catalog/menu, applies owned overrides, compiles
the shared MIPS runtime, assembles, updates CRC, runs shared host and production
MIPS tests, then packages the separate ROM/ZIP. Logs are `remix/charlab-*.log`.

| File | Purpose |
| --- | --- |
| `dist/remix-character-lab.z64` | Checked Remix preview ROM. |
| `dist/remix-character-lab.zip` | ROM, guide, checklist, changelog and metadata. |
| `dist/remix-build-info.json` | Commit, source/ROM checksums and pending acceptance. |
| `dist/remix-SHA256SUMS.txt` | Published-file checksums. |

Use `-Incremental` only for runtime/ASM edits when generated assets and menus are
current. After committing an unchanged build, `-PackageOnly` rechecks its source
receipt and ROM and refreshes clean commit metadata. Changing source after
assembly requires a rebuild. These flags do not replace full generation after
catalog, menu or appender changes.

Linux uses a Remix Python environment with `pipenv sync`,
`pipenv run python -m pip install -r scripts/requirements-test.txt`, then
`pipenv run python scripts/build_charlab.py` from `remix/`. Install Wine for the
pinned Windows assembler/CRC tool, plus Clang and gcc-multilib. Windows is the
locally exercised build path. The older `build.bat` / `patch_extra.bat` asset
pipeline remains available but does not perform the new checked packaging.

Original/generated ROMs, extraction assets and environments stay out of Git.
The two source folders share one root Git repository; do not initialize new
project repositories inside them.
