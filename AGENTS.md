# Smash Character Builder

This folder is the Git root for both `ssb-decomp-re` (current Character Lab) and
`remix` (earlier Remix creator). Origin is `lorenzosaraiva/smash-charbuilder`.
Dependencies remain pinned submodules. Keep creator changes in owned source or
versioned overrides so recursive clones reproduce them.

For gameplay work:

- Keep README, feature checklists, relevant guides and changelogs current.
  Separate implemented/automatically checked features from pending in-game tests.
- Build and verify a new ROM whenever gameplay changes. From the root use
  `tools/build-character-lab.ps1 -Jobs 4` on Windows/WSL or
  `bash tools/build-character-lab.sh --jobs 4` on Linux.
- Checked Character Lab packages belong in root `dist/`. Also copy the new ROM to
  `C:\Users\Lorenzo\Desktop\Smash 64\roms\smash-character-lab-full-roster.z64`.
  Provide the user a clickable ROM link.
- Preserve original-ROM files locally; never commit them. Automatic hosted builds
  require the documented `BASEROM_URL` repository secret.
- Current priority is donor collision paths and timing, then retargeted animations,
  neutral specials excluding Kirby copy, and tether/paired grab and throw mechanics.
- Preserve donor sizes/reach independently of body proportions. Body hurtboxes
  remain native for the first collision milestones.

The Makefile's vanilla comparison prints `FAILURE` for a modified ROM. Compilation,
host checks and `tools/verifyCustomMoveRom.py` must succeed; do not interpret the
vanilla checksum comparison as gameplay verification.
