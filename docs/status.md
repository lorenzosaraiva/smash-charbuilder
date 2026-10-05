# Done / not done

Checkboxes mean implemented, not tested in every matchup.

## Repository

- [x] Custom taunt donors on every original body: poses, duration/cancel flags, safe effects and Luigi's original hitbox.
- [x] Mario taunt original growth/shrink track on foreign bodies, with interruption cleanup.
- [ ] Rendered taunt acceptance and facial/mesh variants.
- [x] Both creator codebases in one project repository.
- [x] Preserve both source histories and existing creator edits.
- [x] Root play/build documentation, changelog and issue forms.
- [x] Pinned build dependencies available through recursive clone.
- [x] Character Lab build command with checked ROM and ZIP in root `dist/`.
- [x] GitHub release workflow with fixed download filenames.
- [ ] Configure the original-ROM source for automatic hosted builds.
- [x] Publish and verify the first public download.
- [ ] Automatic Remix ROM builds/releases.

## Gameplay

- [x] Default VS rules: four stocks, items off; ordinary menu changes remain available.
- [x] Results-screen Expansion Pak arena fixes the match-end heap overflow.
- [x] ROM CPU regression: fresh VS defaults, native stock KOs, results/Start/rematch and Yoshi's Mario taunt growth/cleanup (null rendering).
- [ ] Rendered results/rematch and Mario-on-Yoshi growth acceptance.
- [x] Native root-movement flag and regenerated donor normal velocities, including Fox dash attack and Kirby forward smash.
- [x] MIPS flag-packing, original C playback and live ROM normal movement/recovery checks.
- [ ] Rendered movement/contact acceptance for the corrected normals.

- [x] Default Build One uses the documented Yoshi starter recipe, checked in the linked ROM.
- [ ] Rendered playtesting of the complete Yoshi starter recipe.

Character Lab's [detailed feature checklist](../ssb-decomp-re/docs/status.md)
covers normal attacks, grabs/throws, human/CPU assignments, Training HITBOX view,
grab-preserving combo counters, full-roster normal animations and remaining work.

- [x] All twelve decomp donor normal animations on all twelve bodies, angled variants, aerial landings and supported jab phases.
- [x] Shared compact donor curves and body maps with native-source and linked-ROM checks.
- [x] Live ROM CPU checks: 132 foreign donor/body pairs, 15,248 poses, twelve editor returns and four assigned VS builds.
- [ ] Rendered animation/contact acceptance across the full roster.
- [x] Shared borrowed-special startup/charge/transition/release/recovery poses on all twelve bodies.
- [x] Safe native effects, blaster/tongue/Stone props and a held Samus charge orb.
- [x] Donor tether paths/props, grab/pull timing, paired release/positioning and native victim queues.
- [x] Shared grab/throw attacker poses, DK cargo carry and Kirby landing throws.
- [ ] Rendered tether/victim alignment, contact, stage edges and interruptions.

The [Remix guide](../remix/character_creator_guide.md) and
[port checklist](../remix/docs/character-lab-status.md) cover the separate preview.

## Character Lab neutral specials

- [x] Body Move and Fox Laser.
- [x] Mario/Luigi Fireball, Pikachu Thunder Jolt and Ness PK Fire on all original bodies.
- [x] Donor firing/recovery timing, native projectile collision values and donor spawn geometry.
- [x] Ground/air continuation, independent player state and duplicate/interruption guards.
- [x] Host adapter tests, native spawn geometry checks and linked-ROM verification.
- [ ] Rendered projectile/contact/reflect/absorb acceptance in Training and VS.
- [x] Falcon Punch and Jigglypuff Pound: dedicated hitbox and movement timelines.
- [x] DK Giant Punch and Samus Charge Shot: charge/store/release state.
- [x] Link Boomerang: return/catch lifecycle; Yoshi Egg Lay: paired capture state.
- [x] Borrowed neutral phase animations, charge orb, native props and safe source sound/effect events.
- [ ] Complete donor voice/color/model polish and paired victim rotation. Kirby copy remains outside this milestone.
- [ ] Port the ten new neutral adapters to Remix.
- [x] Fix Training/VS heap overflow using separate Expansion Pak memory (8 MB required).
- [x] Fix cold-boot opening-room overflow; all nineteen intro scenes use Expansion Pak memory.
- [x] Uninterrupted CPU boot through all nineteen intro scenes, title and Start into the main menu (null rendering).
- [x] Emulator CPU regression: twelve body/neutral choices, four preset returns, four-slot VS and the 4 MB launch guard (null rendering).

## Character Lab on Remix

- [x] Original-roster donor normal timing, collision paths and numeric values.
- [x] Grab/throw selectors, donor throw values and DK foreign forward release.
- [x] Body Move/Fox Laser and the three Mario animation pilots.
- [x] Borrowed-special idle/falling poses, original-roster phase clocks and recovery transform guards.
- [x] Retained actual-body recipes, donor normal TransN momentum and 96 shared special source paths/travel phases.
- [x] Special donor attributes around native phase physics, source gameplay clocks and generation cleanup.
- [ ] Full special hitbox/projectile/capture fidelity and rendered two-dash acceptance.
- [x] Existing SRAM recipes and human/CPU assignments integrated with the port.
- [x] Training exit/CSS Back return to the tested editor.
- [x] Native hitbox display, improved grab-aware combo meter and unlocks retained.
- [x] Compiled MIPS execution, linked-data/CRC checks and separate ROM/ZIP packaging.
- [ ] Rendered emulator acceptance and contact/interrupt comparison.
- [ ] Full animation retargeting, broader neutral specials and tether choreography.
- [ ] Donor jab/bounce/bat mechanics, special sockets/ownership/recovery, custom taunts and decomp starter defaults.
- [ ] Shared donor fidelity for Remix-exclusive fighters.

The port uses the same generated vanilla US donor data as Character Lab and
hooks Remix's native animation clock, motion parser and swept collision engine.
Original bodies keep native fighter data and hurtboxes. Expanded-roster creator
adapters remain legacy; their fidelity is a separate future effort.
See the [full port matrix and next batches](../remix/docs/decomp-port.md).

## Gameplay order

- [x] Shared collision trajectories independent of visible body animations.
- [x] Complete normal-attack path catalog for all twelve donors and bodies,
  including angled variants, landing collisions and donor jab phases on every body.
- [x] Direct donor/variant registry with shared trajectory data and loop handling.
- [x] Original animation/matrix checks for every resolved donor timeline.
- [ ] In-game comparison with vanilla donors, including contact and interruptions.

1. **Original normal-attack collisions and timing.** Reproduce donor hitbox paths
   and sizes relative to fighter position/facing, independent of body proportions.
   Full source coverage is implemented; finish rendered/gameplay acceptance.
2. **Donor animations on each body.** Use the collision clock for visible poses.
3. **Neutral specials, excluding Kirby's copy system.** Include projectiles,
   charging, movement, ground/air transitions and recovery.
4. **Tether grabs and paired throws.** Include reach, capture/release timing and
   attacker/victim positioning, followed by matching visuals.

Also track multihits/refresh rules, jab chains, aerial landing lag, hitlag and
interruption cleanup, donor movement and move-specific behavior such as Link's
down-air bounce. Body hurtboxes remain the initial policy.

Normal trajectories, retargeted poses and donor-specific gameplay mechanics are
implemented. Rendered acceptance, visual polish and the Remix mechanics port
remain on the detailed checklist.

## Decomp Up/Down B timing fixes

- [x] Link Spin Attack source paths and full ground/air gameplay, grounded attack weapon and 40-frame ending.
- [x] Samus Screw Attack source paths, distinct ground/air physics and hit sequences, startup intangibility and recovery.
- [x] Jigglypuff Rest one-frame hit, original damage/knockback/radius, invulnerability and uninterrupted 250-frame sleep.
- [x] Donor friction/air limits, Link/Samus recovery attributes and source landing lengths.
- [x] Production native-versus-borrowed callback/physics/weapon lifecycle checks across twelve bodies, four slots and both facings.
- [x] Live ROM CPU checks for all three donors on all twelve bodies: 72 ground/air starts, reset/editor return and four-slot VS loading.
- [ ] Rendered contact, platform/ledge and damage-interruption acceptance for Spin Attack, Screw Attack and Rest.
- [x] Mario/Luigi Up B source collision paths, distinct hit phases, travel/steering, ground/air timing and donor helpless/landing recovery.
- [x] Native-versus-borrowed Mario/Luigi physics and recovery checks across all bodies/slots, with interruption and respawn guards.
- [x] Live ROM CPU checks for both Up B donors on all twelve bodies: ground/air hit fields, foreign source centers, recovery, reset/editor return and four-slot VS.
- [ ] Rendered Mario/Luigi Up B sweetspot/multihit contact, platforms, ledges and interruptions.
- [x] Donor phase durations/loop boundaries and independent event clocks; shared donor poses.
- [x] DK Down B startup/slap/recovery, four source hitboxes and queued repeat cycles.
- [x] Ness Up B weapon/wave/trail preloads and independent foreign-body passive state.
- [x] Host/native/linked-ROM checks and all-body ROM CPU regressions for DK slaps and Ness expiry.
- [x] DK Up B and Mario/Luigi Tornado: source collision positions/fields and donor aerial physics.
- [x] Falcon Kick: source collision paths and movement for all five phases.
- [x] Foreign Tornado state isolated from body passives; landing/respawn reset.
- [x] Ness source projectile socket and 28-tick self-launch gameplay clock.
- [x] Original C playback/matrix comparisons and packed-field/linked-pointer checks for all 96 collision/travel/socket phases.
- [x] ROM CPU regressions across all twelve bodies: grounded/aerial spin, Tornado B-tap rise, Kick travel, Ness steering/controlled self-contact/recovery, editor returns and four-slot VS.
- [x] Remaining special mechanics: bombs/eggs/Thunder, Fire Fox/Quick Attack, Reflector/PSI Magnet/Sing, Falcon Dive, Final Cutter and Stone on original bodies.
- [x] Link held-bomb Down B toss keeps source release timing, socket and throw values.
- [x] Donor reflection/absorption fields; native ownership and PSI healing rules.
- [x] Independent held egg/Thunder ownership and interruption/generation cleanup; required Thunder trail models preloaded.
- [x] Stone selection, native US armor/minimum hold/timeout; Cutter travel without body rescaling.
- [x] 99 donor clocks and 96 source collision/travel/socket phases, original-C geometry and linked-ROM checks.
- [x] Production callback checks across twelve bodies/four slots for movement, zip gate, ownership, healing, capture/release, armor and bomb throw values.
- [x] Live CPU checks for thirteen donor specials on all twelve bodies: 312 ground/air casts, native projectile creation, recovery, reset/editor return and four-slot VS; controlled Falcon Dive capture/throw and Thunder owner contact included (null rendering).
- [ ] Rendered projectile/contact, sleep/capture, slopes/ledges, interruption and visual acceptance across bodies and stages.
- [x] Retarget implemented special phases, charge loops and recovery; add semantic effects and native props.
- [ ] Port this special mechanics/animation batch to Remix.
- [ ] Rendered contact, steering, self-launch, reflection and interruption acceptance.

## Decomp normal-specific mechanics

- [x] Donor jab chains, third/rapid phases, source buffering and native loop endings on every original body.
- [x] Pikachu repeats jab one; Jigglypuff retains its native two-jab chain (unused rapid descriptors stay unreachable).
- [x] Link down-air contact bounce, fastfall cancellation, late-hit rewind and 30-tick rehit timer.
- [x] Ness bat source reflector window/socket/size and native projectile/item reflection.
- [x] Donor root travel, attack traction/air physics, angled variants and landing fallback selection.
- [x] Donor part-intangibility timing mapped onto native body hurtboxes; body script suppression and status cleanup.
- [x] Training/VS 512-entry asset caches for all twelve selected donor files.
- [x] Production callbacks on twelve donors/bodies/four slots and all 396 movement records verified in the ROM.
- [x] Live ROM CPU checks: all 144 donor/body jab chains, twelve controlled Link
  bounces and Ness bat reflections, editor returns and four assigned VS builds.
- [ ] Rendered contact/shield, slopes/edges, interruptions and part-intangibility acceptance.
- [ ] Normal mesh/effect/audio polish and port this mechanics batch to Remix.

See the [normal mechanics guide](../ssb-decomp-re/docs/normal-mechanics.md).

## Decomp tether grabs and paired throws

- [x] All twelve donor grab and forward/back throw choices retain independent source clocks.
- [x] Link hook/rope, Samus beam and Yoshi tongue use source reach, windows and native props.
- [x] Full donor capture matrices include animated scale and preserve each victim's own rig.
- [x] Donor release flags, throw descriptors, facing changes and native victim status pairs.
- [x] DK carry/walk/turn/jump/fall/landing/damage/toss and Kirby lift/fall/landing callbacks.
- [x] Per-player ownership/generation guards, original-C geometry and linked-ROM checks.
- [x] Paired ROM CPU checks: 24 foreign and 24 native forward/back releases, donor reach/ticks/damage, live victim positions and DK mash escape (null rendering).
- [ ] Rendered contact, materials, compact-body intersections, slopes/edges and damage/escape acceptance.
- [ ] Port this paired mechanics/animation batch to Remix.

See [controls and verification](../ssb-decomp-re/docs/paired-grabs-and-throws.md).

See [custom taunts](../ssb-decomp-re/docs/custom-taunts.md) for controls and verification.
