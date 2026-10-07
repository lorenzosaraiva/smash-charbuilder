# Paired grabs, throws and taunts

Remix preview **0.1.10**, updated **2026-10-07**. Original twelve bodies/donors.

## Controls and behavior

Choose **Grab**, **Forward Throw**, **Back Throw** and **Taunt** separately in
Settings -> Character Lab. Assign the build to a human/CPU slot, or use Test in
Training. Z+A grabs; A/forward or back throws; L taunts. Selecting the actual
body retains native behavior.

Link and Samus keep donor tether reach, source prop samples and pull timing.
Yoshi uses donor tongue capture. Capture/throw positions use donor socket
matrices and native victim child offsets/scales. Source facing and release
flags determine direction and timing. Attacker source poses and movement use
bounded ROM caches rather than the body's limb locations; native body
hurtboxes remain unchanged. Victim motion queues retain Remix's parent
mapping, including original polygon/Metal Mario/Giant DK variants.

DK Forward Throw enters cargo carry. Move/turn/jump and press a throw input to
toss from the appropriate ground/air phase. Kirby Forward Throw lifts, falls
and releases on landing, with source timing and physics. Numeric damage and
knockback stay with the selected donor.

Taunts use donor poses, duration, cancel flags, safe effects and sounds. Mario
grows/shrinks the chosen body on his 180-frame track and can guard/grab cancel
from frame 128. Luigi's 80-frame taunt has its original one-damage hitbox at
frames 47-49 and cancel flag at frame 60. Other donors retain source flags;
Link finishes naturally. Interrupted Mario taunts restore model scale.
Borrowed Mario growth uses the body's scaled rest-height pivot so its feet
stay planted instead of sliding through the floor. The world/collision root
remains unchanged; all eleven foreign body pivots have linked-MIPS checks.

Original-roster CSS screens load expanded preview models on demand,
keeping room for native UI and character heaps.
The 96 existing special hitbox tracks now stream through independent 80-byte
player caches, freeing about 240 KiB of resident RAM. Their samples match the
original source exactly; damage, reach, collision paths and timing are unchanged.

Existing recipes keep their bit layout. The four full taunt choices use spare
creator-options bytes; older/invalid saves default each taunt to its body.

## Implemented and automatically checked

- 73 shared phase descriptors and complete source anchor/travel/collision/prop
  geometry; source values are independent of body proportions.
- All source phases, release flags, victim matrices, long clips/loops and taunt
  cancel policy in independent host checks.
- Linked ROM hooks/data/CRC, source ELF geometry comparison, production MIPS
  cache boundaries on four ports, 10,232 donor socket samples, native throw
  callback handoff/release/facing/ownership and twelve-choice taunt SRAM round trips. Scene reset rejects empty menu
  objects sharing the fighter link, and air-toss landing cannot release a victim twice.
- Real-input CPU scenes for tether/tongue contact, paired release/damage,
  DK cargo and Kirby landing, plus taunt duration/growth/cancel behavior.

CPU scenes use null rendering. Rendered tether/victim alignment, mesh/material
acceptance, broader slopes/edges/damage/KO/scene interruption playtests and
expanded-roster pose fidelity remain pending. Kirby copy remains excluded.
