# Up/Down B timing first

The decomp adapter uses the donor status callbacks with a separate donor clock
and event stream. A body's idle/falling animation supplies a temporary visible
pose; its own special animation, duration and root displacement do not control
the borrowed phases. Matching donor bodies still run their native specials.

Generated phase data comes from the original US motion descriptors and animation
tracks. Donor loops reset at the donor boundary. Hitlag and pause stop advancement;
ground/air phase switches preserve the donor progress requested by the native
callback. Normal/neutral clocks remain separate from these phase definitions.

## DK Down B

The native phases are startup (3 frames), Hand Slap (34 frames, looping when B
is tapped again) and recovery (5 frames). The slap cycle creates four hitboxes
on frames 16-17 and again on 26-27. Collision centers use DK's original positions
and size, with the original numeric collision fields. They do not follow the
body's hands or its Down B pose. DK's move is grounded; leaving the floor exits
into the ordinary fall behavior. Repeated taps queue complete cycles.

## Ness Up B freeze

PK Thunder's weapon uses Ness's Main file, but its trail/wave effects also need
Ness's Model file. The previous adapter loaded Main/motion/special data without
Model when Ness was absent, causing a null model descriptor in effect creation.
Active Ness Up B presets now preload that model. Foreign bodies store Thunder's
trail ring and destruction flag independently, so delayed weapon callbacks cannot
replace their native passive state.

## Checks and remaining work

`testSpecialTiming.py` compiles the actual clock/accessor on a 32-bit host, covers
96 source phases, twelve bodies/four slots, loops/transitions and passive storage.
The animation oracle compares DK's four active centers and event masks with
original C playback/matrices. The ROM verifier checks the source phase table and
collision data in the linked ROM.

Optional Linux emulator test (see [setup](neutral-specials.md)):

```bash
python3 tools/testTrainingScenes.py --specials
```

This uses actual menu/input/CPU execution for DK single/repeated cycles and Ness
start/hold/expiry/recovery on all twelve bodies, plus returning to the creator.
It uses null video/audio. Rendered steering/self-launch, contact/reflection,
interruption and visual acceptance remain pending. Other Up/Down B collision
paths, spawn sockets, movement and effects remain experimental. Donor animation
retargeting follows timing/collision fidelity. Remix does not include this batch.
