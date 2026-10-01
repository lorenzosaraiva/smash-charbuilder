# Character Lab: full normal attack roster

The working Mario aerial was committed as `f0d2e1a6c` before this extension. The new ROM supports all thirteen normal attack families from all twelve playable fighters on all twelve bodies: jab, dash attack, three tilts, three smashes and five aerials. The generated table contains 396 entries including angled variants, landing scripts, third jabs and rapid-jab phases.

## Playing

1. Open **Options → Character Lab**. Select one of four builds with A, edit donor values with left/right, and return with B.
2. On the lab's main screen, select **Player One/Two/Three/Four** and use left/right to assign a build or **Vanilla**. Assigning a build enables it. The player number is the controller/CPU slot, independently of team color.
3. Select **Play VS**. Assigned bodies are preselected. Change the usual player-type control to CPU for a custom opponent. Keep that build's body selected; choosing a different body plays that body normally. Two slots can use distinct builds with the same body, or share one build.
4. **Test in Training** assigns the edited build to player one. In training, press Start, select **View**, and choose **HITBOX** with left/right. It uses the engine's red attack outlines and hurtbox visualization for both fighters. NORMAL/CLOSE UP restore ordinary rendering.

The four unlockable fighters (Luigi, Captain Falcon, Jigglypuff and Ness) and Item Switch are unlocked on fresh and existing saves. Existing records and options are preserved. These unlocks survive a restart; creator builds and player assignments currently last for the running ROM session.

## Compatibility rules

- Normal attacks execute the body's own animation, status, sounds, visual effects, input/chain logic, recovery, invulnerability and landing policy. No donor-specific state function or donor animation is introduced by this extension.
- A generated local collision timeline replaces native collision events, including native parallel collision events. It supports creation, phased changes, damage/size/sound changes, moving offsets, individual/all clears, refresh and hit groups. Native parallel effects retain their own slot; the generic collisions use a third slot.
- Each source joint becomes a semantic body location. Explicit JointTree maps for each target resolve that location to its own initialized skeleton. Missing/invalid joints, attack IDs, truncated commands, foreign opcodes or oversized buffers reject the complete generated script safely and increment `gFTCustomMoveValidationFailures`.
- Weapon sockets map to the holding hand. Tails map to the torso on bodies without an equivalent part. These are geometry approximations. The tested Mario/Falcon down-air retains its smaller knee/torso offsets.
- Third-jab and rapid-jab collision choices run only in states supported by the body. A donor cannot add a new chain to a body without that chain. Rapid collision loops wait for the native animation cycle and jump only within that player's own generated buffer.
- Landing collisions follow the selected aerial donor while retaining the body's landing animation and recovery. A body animation/status ending early can shorten the donor timeline. Link's bounce, Ness's reflector, donor-specific effects and hurtbox behavior are not transplanted.
- The earlier special adapters remain separate, as in the working checkpoint. This extension normalizes normal/aerial collisions; it does not add a new special-move system.
- Custom definitions apply in VS and training only. Demo/preview fighters and unrelated modes keep their normal behavior.

The lab uses the game's existing option tabs, font sprites at readable 2x size, gold headings, red selection and purple/gray panels. The HITBOX label is composed from the same native alphabet, rather than an external font.

## Validation

Generate the data with `python3 tools/generateCustomMoves.py` and `python3 tools/generateTrainingHitboxLabel.py`. `tools/auditNormalMoves.py` remains a read-only census of the source moves.

The freestanding host test includes the actual runtime implementation. It checks all 12 × 12 × 33 = **4,752 body/donor/variant combinations**, per-player buffers, CPU/vanilla/demo/scene eligibility, native event suppression, local rapid-loop pointers, malformed definitions and the tested Mario aerial parameters. It does not simulate N64 animations or collision detection.

```sh
gcc -m32 -nostdlib -static -fno-pie -fno-stack-protector -O1 \
  -Iinclude -Isrc -D__sgi -D_LANGUAGE_C -D_MIPS_SZLONG=32 \
  tools/testCustomMove.c -o build/testCustomMove
build/testCustomMove
make -j4 COLOR=0
python3 tools/verifyCustomMoveRom.py
```

The ROM verifier checks all 396 host-tested data tables, all twelve semantic maps, linked creator/assignment/training code at ELF load addresses, N64 byte order and the patched checksum. The modified ROM is expected to differ from vanilla, so the Makefile's vanilla comparison prints `FAILURE` after a successful compile/link. In-emulator playtesting of this expanded build is still required.

Output: `build/smashbrothers.us.z64`, also copied to `C:\Users\Lorenzo\Desktop\Smash 64\roms\smash-character-lab-full-roster.z64`. A companion Windows shortcut opens that copy with the installed RMG-K.
