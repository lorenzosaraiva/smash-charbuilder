# Helping out

This is a casual project. Gameplay reports, ideas and small fixes are welcome.
Say whether you are using Character Lab or the Remix creator: their menus,
compatibility rules and ROMs differ.

For a bug, include the commit from `build-info.json` if available, emulator,
body, donor, attack and steps to reproduce it. A short clip helps.

For code changes:

1. Make a branch from `main` in this root repository.
2. Change the relevant source folder. Both folders use the same Git history now.
3. Follow [the build guide](docs/building.md) and try the affected combination.
4. Explain the behavior and how you checked it in your pull request.

Keep ROMs, generated output, virtual environments and tool binaries out of Git.
Preserve upstream credits/license files. Update the relevant feature checklist
and changelog when behavior or limitations change.

Dependency edits belong in a reproducible patch or source override, rather than
an unpublished submodule commit. The Remix Sonic creator hook is preserved in
`remix/smashremix_overwrite/Sonic/SonicSpecial.asm`.
