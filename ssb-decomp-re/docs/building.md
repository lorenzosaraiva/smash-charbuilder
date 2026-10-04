# Build Character Lab

You need x86-64 Ubuntu 22.04, or Windows with WSL/Ubuntu, and the original US Smash 64
ROM. Native Windows and macOS are not supported by the complete current toolchain.
You do not need to build the project just to play a downloaded release.

Enable **8 MB RDRAM / Expansion Pak** when playing the ROM. Full-roster Training
and VS selection/match resources use the separate upper memory bank.

## First build

1. Clone the public project repository with its submodules:

   ```bash
   git clone --recurse-submodules YOUR-REPOSITORY-URL
   cd YOUR-REPOSITORY-FOLDER
   ```

2. Put the original ROM at `baserom.us.z64` in the repo root. The required SHA-1
   is `e2929e10fccc0aa84e5776227e798abc07cedabf`. A previously modified ROM, another
   region or different byte order will fail the check. Original ROMs stay local
   and are ignored by Git.

3. In Ubuntu, install the prerequisites for dependency setup:

   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-venv git
   bash tools/build-character-lab.sh --setup --init --jobs 4
   ```

   The setup creates `.venv/`, initializes submodules, installs dependencies and
   downloads the compiler/asset tools. The existing installer may ask for sudo
   to install missing system packages. The first extraction/build takes a while.
   The compiler emulator also downloads a checksum-verified compatibility runtime
   into its ignored tool directory on older hosts; it does not replace system libc.

## Windows shortcut

Install WSL with an Ubuntu distribution, complete its first-run setup, and install
`python3-venv` in Ubuntu as above. Then, from PowerShell in this repository:

```powershell
.\tools\build-character-lab.ps1 -Setup -Init -Jobs 4
```

For a distribution named something else, add `-Distribution Ubuntu-24.04` (or its
actual name). If your PowerShell execution policy blocks scripts, use the Bash
command from a WSL terminal instead.

## Later builds

```bash
bash tools/build-character-lab.sh --jobs 4
```

Or on Windows:

```powershell
.\tools\build-character-lab.ps1 -Jobs 4
```

After pulling changes to `smashbrothers.us.yaml` or `symbols/`, add `--init` (or
`-Init` in PowerShell) to re-extract the original data. This rebuilds generated
extraction files without deleting your source changes.

## Output

| File | What it is |
| --- | --- |
| `build/smashbrothers.us.z64` | The engine's usual ROM output. |
| `dist/character-lab.z64` | The checked ROM with its fixed download filename. |
| `dist/character-lab.zip` | ROM, play guide, checklist, changelog and build information. |
| `dist/build-info.json` | Commit, local-change status, size and ROM SHA-256. |
| `dist/SHA256SUMS.txt` | Checksums for the published files. |

`build/`, `dist/`, `.venv/` and ROM files are ignored by Git. No copy is made to
someone else's desktop by this portable build command.

## What the command checks

The build runs the actual custom-move host tests and verifies linked code, donor
tables, shared donor curves, all twelve rig maps, relocated registry pointers and N64 checksum
in the ROM before packaging it.
These automated checks do not replace in-emulator playtesting.

The Makefile may print `smashbrothers.us.z64: FAILURE` after compilation. That is
its original byte-for-byte vanilla comparison: this modified ROM is supposed to
differ. The dedicated verifier must print `PASS`; a failed build/test/verifier
stops packaging and the GitHub release workflow.

For source debugging and the original decompilation tools, see
[decompilation.md](decompilation.md) and [custom-move-roster.md](custom-move-roster.md).
