# Tether grabs and paired throws

Version 0.1.14, updated 2026-10-05. Decomp only; Remix retains its previous build.

Choose **Grab**, **Forward Throw** and **Back Throw** independently in Character Lab.
Try Link or Samus Grab on Kirby, or Yoshi Grab on Mario, then select a different
throw donor. Use **Start -> View -> HITBOX** for source grab volumes.

## Coverage and controls

| Selection | Behavior |
| --- | --- |
| Any original grab | Original active window, reach/path, recovery and pull starting frame. |
| Link grab | Moving hook and rope, original hitbox path and pull timing. |
| Samus grab | Original grapple hitbox/beam segments, pull timing and recovery. |
| Yoshi grab | Extending tongue, hidden held victim and original throw release. |
| Forward/back throw | Donor release/facing flags, damage/knockback and native victim status queue for that victim body. |
| DK forward throw | Windup -> shouldered carry. Walk/turn/jump/fall/land with the normal controls; A/B toss. Native mash escape and carry damage policy remain active. |
| Kirby forward throw | Native lift -> fall/landing -> release sequence, including donor root travel and paired positions. |

Grab and throw donors can differ. Matching body/donor choices use native callbacks.
Foreign choices use 61 bounded source phases and 288 original attacker/victim/direction
status pairs. Link, Samus and Yoshi attachments use preloaded native display lists
outside the selected body's skeleton. Every body keeps its native attributes and
hurtboxes outside the short donor physics callback.

## Position and timing policy

Capture positions come from the donor's original heavy-item socket matrix, including
animated scale, sampled with the same clock as its collision/animation script.
The native victim root offset and size are transformed through that matrix at the
attacker's position/facing. Victim rotations use the original matrix-to-Euler routine.
The victim keeps its own capture/thrown animation, selected by the donor's native
victim table. This retains the original pairing policy without attaching a foreign rig.

Throws use the original release flags and descriptors, including interruption
values. Carry and landing transitions install the appropriate donor callbacks.
Attacker poses share the body retargeter, with long carry animations split into
bounded clips. Identical loop cycles and zero movement arrays share storage.
Paired geometry occupies guarded spare fighter-overlay space, leaving the
Expansion Pak bank for pose keys and preserving more scene heap headroom.
Player/generation checks reject stale capture or animation owners; native escape,
damage, KO and reset callbacks retain responsibility for severing the capture links.

Different-sized bodies can intersect visually even when gameplay positions match
the donor policy. This milestone prioritizes reach, timing and release behavior.

## Verification

The standard build includes `testPairedMoves.py`, original C playback/matrix checks,
the actual C retargeter and linked-ROM verification. The production fixture checks
all twelve attacker/victim bodies, four slots, release/facing/cargo behavior, stale
ownership, loop/chunk boundaries and captured transforms at both facings.
Original native capture matrices/root paths cover all 61 phases; the shared catalog
contains 488 normal/special/grab/throw clips from this milestone. Version 0.1.15
adds 13 taunt chunks (501 clips total); see [taunts](custom-taunts.md).

Optional Linux/Mupen64Plus CPU checks:

```bash
python3 tools/testTrainingScenes.py --paired-moves
python3 tools/testTrainingScenes.py --paired-moves --paired-native
python3 tools/testTrainingScenes.py --boot
python3 tools/testTrainingScenes.py --four-mb --cases 1
```

The ROM CPU sweep passed 24 foreign forward/back releases and 24 native controls
across all twelve donors/bodies. It checks tether active windows/centers, source
release ticks/damage, live captured positions, Yoshi visibility, DK carry/toss and
Kirby landing release, plus native/foreign DK mash escape, editor returns and
four assigned VS builds. The standard build verified all 488 clips: 6,120,387
joint-world orientations; 35,370 original-C capture basis samples had maximum
error 0.0001926 engine units.

The mixed twelve-normal-donor Training stress check and four-slot VS loading
passed after the memory change, with at least 251,316 bytes of Training heap
headroom. The fighter overlay still stops before the original framebuffers.
The uninterrupted 19-scene intro/title/Start boot and 4 MB launch guard are also
checked on this layout.

These use null rendering. Rendered tether materials/contact, compact-body alignment,
slopes/ledges, mash escapes and damage interruptions still need manual comparisons.
Kirby copy remains excluded. The paired mechanics port to Remix remains pending.
