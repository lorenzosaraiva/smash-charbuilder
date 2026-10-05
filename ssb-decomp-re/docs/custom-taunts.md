# Customizable taunts

Version 0.1.18, updated 2026-10-05. Decomp Character Lab.

In **Options -> Character Lab**, open a build and change **TAUNT** (below
**DOWN B**) with left/right. Each build has its own donor. **Use Body For All**
restores the body's taunt; **Randomize Moves** includes it. Test in Training or
assign the build to a human/CPU slot in VS. Press the normal **L** taunt button.

All twelve original taunts use donor poses through the shared retargeter, original
duration and flag-controlled grab/guard cancel windows. Matching body/donor choices
retain native playback. Borrowed taunts retain safe source sounds, voice events,
rumble and common effects; voices respect the body's native voice/mute policy.

| Donor | Duration (frames) | Grab/guard cancel flag (frame) |
| --- | ---: | ---: |
| Mario | 180 | 128 |
| Fox | 60 | 60 |
| Donkey Kong | 60 | 60 |
| Samus | 60 | 60 |
| Luigi | 80 | 60 |
| Link | 60 | None |
| Yoshi | 80 | 60 |
| Captain Falcon | 60 | 60 |
| Kirby | 60 | 60 |
| Pikachu | 80 | 60 |
| Jigglypuff | 90 | 60 |
| Ness | 60 | 60 |

Luigi's taunt also retains its original foot collision path on frames **47-49**:
**1 damage**, radius **50** (source size field 100), angle **361**, knockback scaling
**100**, weight knockback **60** and base knockback **0**. Reach stays donor-sized on every body.
Use **Start -> View -> HITBOX** to see it. The other taunts have no attack hitbox.

Mario's borrowed taunt now applies his sampled original model-root growth/shrink
track on every foreign body, including Yoshi. The source reaches about **2.25x**
scale, returns to normal on the original timeline, and restores the body's bind
scale immediately on interruption. It does not change TopN scale, body attributes
or the donor collision catalog. Taunts retain the body's native hurtbox definitions;
their joint transforms follow the animated model as usual.
Facial/texture swaps and donor hand/weapon mesh variants remain pending for foreign
bodies. Rendered pose/effect acceptance still needs playtesting.
Kirby's native body copy-drop policy remains native; borrowing its taunt does
not grant copy abilities. These changes have not been ported to Remix.

The standard build checks selection/native fallback and cancel policy across all
twelve bodies/donors/four slots, original C playback/collision data, all shared
clips on all twelve rigs, and the linked ROM. Optional ROM CPU checks (null rendering):

```bash
python3 tools/testTrainingScenes.py --taunts
python3 tools/testTrainingScenes.py --taunts --paired-native
python3 tools/testTrainingScenes.py --taunts --taunt-body 6 --cases 1
```

These exercise actual L/guard inputs, donor duration/cancel flags, Luigi's hitbox
fields/path/contact, cleanup, editor return and four assigned VS builds.

The checked ROM passed twelve borrowed taunts and twelve native controls, including
menu left/right wraparound, body reset, randomization and Luigi's live damage.
For that small contact window the dummy temporarily uses a human slot with no
inputs, then returns to CPU control; native AI would jump away. All 501 shared
clips passed 6,430,305 runtime joint-world orientation checks across twelve rigs.
These CPU checks use null rendering; rendered visual acceptance remains pending.
Version 0.1.18 also checks every original Mario growth sample against native C
playback, scale application/cleanup across the foreign bodies and four slots,
and a live Yoshi/Mario Training test with natural recovery and guard cancellation.

The mixed twelve-normal-donor Training stress check retains at least 188,532
bytes of heap headroom on this layout. DK cargo/back-throw/mash-escape and
four assigned VS builds also pass after the catalog expansion.
Cold boot passes all nineteen opening scenes, title and Start; the 4 MB launch
guard keeps unsupported Training tests in the editor.
