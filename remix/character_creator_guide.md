# In-game Character Creator

Character Creator builds a playable recipe from fighters already compiled into
the ROM. It does not add a new CSS slot or duplicate character assets. Instead,
the selected body remains the real fighter and the runtime redirects selected
normal-action command streams and special-action ownership to donor fighters.

## Build and open the menu

Build the ROM normally:

```text
patch_extra.bat
```

A successful build is also copied automatically to `dist/char_builder.z64`
inside the Remix folder. Set `SMASH_EXTRA_ROM_DIR` to copy it to your emulator's
ROM folder instead. See the [shared build guide](../docs/building.md).

In game, open `Settings -> CHAR CREATOR`. There are four SRAM-backed build
slots. Each slot contains:

- an editable 20-character name;
- an Enabled switch and Body selector;
- Jab, Dash Attack, tilts, smashes, and all five aerials;
- Fox's locked Neutral Special, plus editable Up and Down Special;
- `USE BODY FOR ALL MOVES`, which creates a safe baseline;
- `TEST IN TRAINING`, which saves the recipe, selects it for player 1, and
  opens the Training character-select screen.

All four slots start enabled with mixed normal attacks already selected. Their
default bodies are Mario, Fox, Link, and Kirby. Each preset uses a bounded
group of original-roster donors, while Up and Down Special initially stay on
the body. `USE BODY FOR ALL MOVES` preserves Fox's Neutral Special lock.

The creator hub also has an `Original 12 Only` switch. Turn it on to limit
every Body and move selector to the original US roster (Mario through Ness).
Selections outside that roster are safely changed to the current body. The
switch is saved with the other creator data.

The selectors contain the normal playable roster that was actually compiled
by `character_appender.py`, including +EXTRA characters. Debug polygons,
boss-only forms, and other unsafe/non-playable forms are intentionally omitted.

## Recommended first recipe

1. Open a build slot and edit its name with the same keyboard used by Player
   Tags.
2. Select a Body.
3. Adjust any preselected moves you want to change.
4. Choose `TEST IN TRAINING`.
5. On the Training CSS, select the same fighter as the recipe's Body.
6. Open `Player Settings` on the CSS if you later want to choose another saved
   build for that port; use the `Custom Build` option.

The body check is deliberate: a recipe only activates when the selected CSS
fighter matches its Body. This makes stale per-port settings fall back to stock
behavior instead of unexpectedly changing another fighter.

## What is saved

Names and recipes are stored in four dedicated 0x30-byte SRAM blocks through
the native Settings serializer. `TEST IN TRAINING` explicitly saves before it
changes screens. The per-port `Custom Build` selection is a match setting, not
part of the recipe itself.

Changing the compiled roster can change catalog indexes. Recreate or verify
saved recipes after adding, removing, or reordering characters in the ROM.

## Compatibility model

Normal attacks retain the body's animation and action callbacks while borrowing
the donor's complete motion-command stream. That stream supplies startup and
active timing, hitbox clears, damage, angle, knockback growth, fixed/base
knockback, shield damage, hitbox size and offsets, sound, and element. Hitstun
is then calculated normally by the engine from the borrowed knockback data.
The body's animation still determines the move's total recovery in this first
pass, so a donor command that extends past a shorter body animation is cut off.

Hitbox bone IDs are interpreted on the body's skeleton. Very different rigs
can therefore place hitboxes incorrectly. If a borrowed script names a joint
the body does not have, the hitbox is attached to the body's top joint instead
of dereferencing a null joint and crashing.

Neutral Special is locked to Fox so every custom build creates his laser
directly from the body's native Neutral-B action. This avoids applying Fox's
fighter state, skeleton assumptions, and accessory callback to another body.
Up and Down Special remain selectable and are broader bundles: they include
character-specific executable code,
state fields, physics, projectiles, model parts, and follow-up actions. The
special adapter keeps the selected body model and attributes, but temporarily
activates the donor's character ID, FTData, unique-action table, motion-command
base, and special-file globals for the whole special chain. Donor animation
data uses a separately sized pre-match buffer so it cannot overflow the body's
animation heap. Direct accesses to a joint absent from the body resolve to its
top joint for the duration of the special. The complete body context is
restored before a shared action begins.

Special mixing is experimental and each body/donor pairing needs an emulator
runtime test. A successful ROM build proves that the assembly and resource
layout are valid; it does not prove that a donor callback never touches an
incompatible body joint, model part, state field, or follow-up action. The
animation is also being applied to a different skeleton, so proportions and
attachment positions can look unusual. Highly coupled mechanics such as
captures and body-part swaps are especially likely to need a move-specific
visual or state adapter. Kirby's Neutral and Down Special behavior is not a
supported compatibility target in this pass.

The runtime caches at most eight donor moveset files per port per match. These
files are loaded during the engine's pre-match character-loading phase rather
than during an attack transition. A recipe using more donors falls back to the
body for donors that cannot be cached. Keeping a first build to a small donor
set is recommended.

## Implementation map

- `extra_imports/CharCreatorMenu.inc` declares the native Settings pages.
- `extra_toggles/css/CharCreator.asm` exposes saved builds per player on the
  VS and Training CSS Player Settings panel.
- `extra_imports/CharCreator.asm` owns recipe lookup, caches, normal command
  redirection, special dispatch, and Training handoff.
- `smashremix_overwrite/Character.asm` supplies the action/special hooks.
- `smashremix_overwrite/command.asm` keeps `GO_TO_FILE` commands on the active
  donor moveset file.
- `character_appender.py` discovers the compiled CSS roster, generates the
  selector catalog, injects the menu, and allocates the SRAM blocks.

Generated files under `build/char_creator/` should not be edited. Change the
source files above and rebuild instead.
