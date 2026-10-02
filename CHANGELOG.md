# Character Lab changes

## Next release — repository setup

- Newcomer README, feature checklist, play/build guides and release instructions.
- One build command that verifies the ROM and creates a play package under `dist/`.
- Automatic build/release workflow for pushes to `main`, manual runs and `v*` tags.
- Fixed download filenames, source commit information and SHA-256 checksums.
- Compiler emulator setup keeps verified compatibility libraries locally on Ubuntu 22.04.

## Current gameplay build

- Training tests return to the same build's character editor (`62f65219e`).
- Neutral B can select Body Move or Fox Laser. Foreign-body lasers use a finite
  firing action; DK no longer runs his charge loop underneath a laser.
- DK skips cargo carry when another fighter's forward throw is selected (`8cb8b29bf`).
- Three Mario animation pilots: Falcon down air, Fox straight forward tilt,
  DK straight forward smash (`ad41465b1`). Numeric verification passed; visual review pending.
- Original donor normal-attack timing, hitbox values and knockback, plus mapped
  grab timing and numeric forward/back throw customization.
- Four presets, human/CPU assignments in VS, Training HITBOX view, native menu
  styling, unlockable fighters and Item Switch.

For remaining work and limitations, see [the checklist](docs/status.md).
