# Changes

## 0.1.33 - 2026-10-08: Remix Stone lighting

- Build local Remix preview 0.1.16 and preserve the original Character Lab ROM.
- Install the native one-light count and stage direction before borrowed fighter meshes. Kirby Stone already supplies its brown diffuse/ambient material and texture; it no longer relies on another draw pass's light setup.
- Check light setup ordering and initialized direction in linked MIPS; exercise Stone input, replacement and recovery in the native CPU scene. Rendered colour acceptance remains pending.
- Include the stored Giant Punch flash and visible, body-coloured Morph Ball fixes from 0.1.32 in this checkpoint.

## 0.1.32 - 2026-10-08: Remix charge flash and visible Morph Ball

- Build local Remix preview 0.1.15; preserve the decomp ROM and existing published download links.
- Reapply the native Giant Punch full-charge color script from stored sidecar state, without resetting its blink every frame. Consume/clear the borrowed flash when charge is spent, respect native color priority and guard player generations.
- Initialize borrowed fighter meshes with the native opaque two-cycle render mode before submission. Earlier prop checks missed the incoming blend state.
- Show Samus Bomb's source compression/round/recovery meshes throughout frames 3-48 and tint a private CI4 ball palette for the body. Restore native visibility at frame 49 or interruption. Preserve source-sized geometry, native body hurtboxes, the original hop and one bomb per input.
- Add linked-MIPS color/phase/render-state regressions and real-input stored-charge and Morph Ball hop checks. Automatic checks are distinct from pending rendered acceptance.

## 0.1.31 - 2026-10-08: Remix tether materials and stage state

- Release Remix preview 0.1.14; preserve the decomp ROM and download.
- Move independent borrowed fighter meshes to the native fighter display-list head, leaving their particle glow in the effects pass. Restore one-cycle shading, texture palette/alpha/render settings and stage lighting after drawing; the previous two-cycle effects-pass state contaminated later stage layers.
- Remove the extra paired-prop material tick. Independent effect updates already advance these animations; the duplicate shortened Samus beam texture holds and blink timing.
- Execute native material texture branches and dirty mesh state in linked-MIPS checks, including the post-draw state and an untouched effects display list. Keep donor geometry, reach, collision timing and body hurtboxes unchanged.
- The user confirmed visible tether geometry in 0.1.13 and reported noisy textures and white Dream Land layers. Automated command/material-clock and real-input CPU checks remain distinct from rendered acceptance of this fix.

## 0.1.30 - 2026-10-07: Remix tether render state

- Release Remix preview 0.1.13; preserve the decomp ROM and download.
- Initialize the independent fighter-prop draw pass with native stage environment color, two-cycle shading and zero fog alpha. Samus beam parts and other borrowed fighter meshes cannot inherit a previous effect's transparent environment multiplier.
- Compile the shared Remix runtime with the same F3DEX2 graphics command format as the game. Prefix display-list calls and render-state macros now use the correct opcodes.
- Execute the real prop display callback and native mesh submission in linked-MIPS checks, including transparent incoming state and optional model prefixes. Earlier allocation/transform checks did not establish visible geometry.
- Retain donor beam placement, reach and extension/retraction timing, native body hurtboxes and effect ownership/cleanup. Targeted DK miss/contact/recovery CPU checks remain distinct from rendered acceptance; the local Rice harness did not establish a valid rendered result.

## 0.1.29 - 2026-10-07: One Samus bomb per Down B

- Release Remix preview 0.1.12; preserve the decomp ROM and download.
- Fix extra Samus bombs on DK and other foreign bodies. Ground/air phase resumes now fast-forward consumed one-shot flags, matching the native event parser, instead of replaying the frame-10 spawn after landing. New inputs retain their own bomb and source timing.
- Let the external donor stream exclusively own gameplay flags during supported specials, preventing native scripts from re-arming projectile and movement events.
- Follow the selected donor's aerial Down B availability before native dispatch, allowing DK's body to use Samus Bomb in the air. Check all original bodies/donors across four slots; keep native/expanded fallback and DK's grounded-only rejection.
- Add linked-MIPS checks for 88 flag-ownership cases and 44 casts across all eleven foreign bodies, each with three ground/air continuations. Real-input CPU checks count actual weapon births on DK, Mario and native Samus, with two grounded and two aerial casts each. Morph Ball visibility and cleanup remain checked separately; rendered acceptance remains pending.
- Earlier Bomb visual checks did not count weapons and missed this duplication; the new regression checks actual spawn counts.

## 0.1.28 - 2026-10-07: Remix smash safety and Samus visuals

- Release Remix preview 0.1.11; preserve decomp 0.1.18 and its download.
- Fix both DK/Samus borrowed down-smash crashes: native donor effects now resolve valid body joints; donor mesh/part-hurtbox commands cannot modify foreign bodies.
- Add Samus Bomb's donor-sized Morph Ball replacement on source frames 10-42, with native body restoration at recovery and interruption. Body hurtboxes remain native.
- Preload paired visual dependencies independently of special animation heaps. Add Samus's missing native tether glow at sampled donor joint 23 alongside the six existing beam parts, with owned cleanup.
- Check single-tap DK Down B on native DK and a foreign body: one cycle contains the original slap windows at 16-17 and 26-27; another B tap requests another cycle. Preserve this source behavior.
- Add production MIPS checks for 396 missing normal-effect joints, all foreign-body Morph Ball placements and 88 tether-glow placements. Real-input CPU fixtures cover both reported smash combinations, Bomb and tether miss/contact/recovery; rendered appearance remains pending.

## 0.1.27 - 2026-10-07: Remix taunt, presets and special edge cases

- Release Remix preview 0.1.10; preserve decomp 0.1.18 and its download.
- Anchor borrowed Mario taunt growth to the body's rest-height pivot, keeping feet planted instead of translating the scaled body below the platform.
- Set explicit original-body Neutral B choices when using All moves from body; retain native fallback for Kirby copy and expanded bodies.
- Reject unavailable donor ground/air special entries before changing fighter context or allocating resources, preventing aerial DK Down B from becoming the body's Down B.
- Add production MIPS checks for every original-body preset, four player slots, unavailable aerial DK inputs and all eleven foreign Mario taunt pivots.
- Add real-input CPU fixtures for special contacts, hitlag-aware DK repeats, recovery/landing and interruption cleanup. Track the evidence and remaining rendered walls/slopes/ledges acceptance in the special edge-case guide.

## 0.1.26 - 2026-10-06: Remix paired grabs, throws and taunts

- Release Remix preview 0.1.9; preserve decomp 0.1.18 and its download.
- Port Link/Samus tether and Yoshi tongue reach/props, donor pull timing, attacker/victim sockets, facing and source release flags.
- Connect DK cargo wait/walk/turn/jump/fall/toss and Kirby lift/fall/landing throws, donor physics and independent long-phase clocks.
- Add twelve-donor Taunt selection, source poses/duration/cancel flags/effects, Mario growth/shrink and Luigi's original damage window.
- Stream 73 source paired/taunt geometry phases through independent eight-frame player caches; retain donor reach independently of body proportions and native victim rigs/parent mapping.
- Stream 96 existing special collision tracks through independent 80-byte player caches, freeing about 240 KiB of native menu RAM while preserving exact source samples.
- Keep old recipe fields/bits; save full four-slot taunt choices in spare options bytes with validated body defaults for older saves.
- Avoid Remix costume hooks for independent effect props; install a donor clock for native CatchWait's null animation and clean phase props/scales on interruptions and scene resets. Guard menu objects sharing the fighter list and distinguish native throw callbacks from compiled fallbacks. Prevent duplicate cargo release on air-to-ground transitions; defer expanded CSS model preloads for original-roster CSS screens to preserve native UI/heap space. Track the native Expansion Pak allocation cursor so UI scene changes cannot overwrite live GC pools.
- Add independent source ELF/bank, production MIPS cache/save checks and real-input CPU capture/release/cargo/landing/taunt regressions. Rendered alignment/effects, broader stage/interrupt acceptance and expanded-roster fidelity remain pending.

## 0.1.25 - 2026-10-06: Remix special effects and attachments

- Release Remix preview 0.1.8; preserve the decomp 0.1.18 ROM and links.
- Add Final Cutter sword/trails, Stone replacement, Falcon Punch/Kick flames, Fox blaster, Yoshi tongue and the source-sized Samus charging orb.
- Reuse source prop samples and semantic joints on foreign bodies; keep gameplay clocks, collision paths and native body hurtboxes independent.
- Play safe source-timed effects, sounds, voices and loops; keep the charge orb through release startup and remove it at projectile handoff.
- Preserve neutral attachments and loop audio across internal body-pose phase changes; real interruptions still clear them.
- Preload private effect resources before the match; validate effect/fighter ownership and clean up attachments, sound loops and Stone visibility on interruptions, death and scene resets.
- Add source-prop and linked-MIPS timing/cleanup checks, plus optional real-input native effect allocation checks. Full rendered acceptance remains separate.

## 0.1.24 - 2026-10-06: Remix remaining neutral specials

- Release Remix preview 0.1.7; preserve the decomp 0.1.18 ROM and download.
- Add Mario/Luigi Fireball, Pikachu Thunder Jolt and Ness PK Fire; keep source spawn/fire/recovery timing and private native weapon/item callbacks.
- Add Falcon Punch/Pound source collision paths, travel and aerial boosts; Giant Punch and Charge Shot charging, storage, partial/full release, recoil and interruption behavior.
- Add Boomerang throw/empty/catch and private return/reflection lifecycle, plus Egg Lay source grab/capture/release timing and native egg damage/escape. Kirby copy stays excluded.
- Connect shared neutral phase poses with body-safe status assets and original gameplay clocks. Charge orb, attached props/effects and rendered acceptance remain pending.
- Preserve existing SRAM recipe bit layout with a validated four-choice supplement in spare creator-options bytes.
- Supply the caller register/stack contract expected by Remix's generic weapon hook, avoiding borrowed projectile freezes.
- Preload private Jolt/PK Fire particle banks with the native call convention; clear Boomerang ownership using the actual body during another borrowed special.
- Extend linked-MIPS and real-input CPU coverage; keep rendered contact/reflect/absorb and broader stage/interrupt acceptance separate.

## 0.1.23 - 2026-10-06: Remix donor normal mechanics

- Release Remix preview 0.1.6; preserve the decomp 0.1.18 ROM and download.
- Port donor jab availability, buffering, third/rapid phases and independent source loop/end clocks using body-safe native status setup. Preserve unused Jigglypuff rapid gates and native/expanded fallback, including Mewtwo and Slippy entry patches.
- Connect Link down-air bounce/late-hit rewind/rehit and Ness bat source reflector windows/socket/size to native weapon/item collision paths.
- Apply donor angle/landing availability, TransN travel, traction, gravity, terminal velocity and air drift during normals; retain native body hurtboxes, weight and movement outside attacks. Source scalar data avoids loading donor model files for normal physics.
- Replace the neutral selector labels with fighter names; native neutral follows each build's Body without changing saved values or SRAM layout.
- Add linked-MIPS normal regressions and real-input jab/contact fixtures. Rendered contact, landing, effects/props and interruption acceptance remain pending.
- Preserve Remix's aerial-fastfall toggle through complete guarded physics entries, avoiding the old function+4 route that lost the saved return address.

## 0.1.22 - 2026-10-06: Shared Remix animation catalog

- Release Remix preview 0.1.5; preserve the decomp 0.1.18 ROM and download.
- Reuse the decomp compressed curves, bind/semantic rigs and quaternion retargeter for normals and supported special/recovery poses on all twelve original bodies. Keep the three accepted Mario pilots unchanged.
- Pack 501 clips into a 2,180,944-byte ROM bank; load selected clips into independent 15,200-byte caches for four players instead of consuming a resident bank in Expansion Pak RAM. Paired/taunt data is reserved for their later mechanics port.
- Suspend missing-joint callback aliases during pose writes, preventing cosmetic-joint resets from teleporting the world root. Preserve original move clocks, collision paths, native body hurtboxes and world movement. Apply directional Fire Fox/Quick Attack and Mario/Luigi steering presentation separately.
- Add independent decomp ELF checks for packed keys/roots/rigs and production MIPS joint/cache/isolation checks. Rendered mesh, effects/props and contact acceptance remain pending.

## 0.1.21 - 2026-10-06: Remix Training launch and menu label

- Release Remix preview 0.1.4; keep the decomp ROM at 0.1.18.
- Initialize editor-launched Training CSS with the selected build body, valid native costumes, P1 and a Mario dummy, replacing stale/random expanded-roster preview selections.
- Display **Character Lab** in title case in the Settings menu and update the play guide.
- Correct the CSS Back hook to Training's overlay, restoring return to the tested editor without modifying the ordinary 1P CSS at the same RAM address.
- Fix the special-callback importer when invoked through a full asset build, alongside direct runtime builds.
- Add real-input editor launch/return CPU coverage; distinguish it from direct Training scene fixtures. Rendered acceptance remains pending.

## 0.1.20 - 2026-10-05: Remix special gameplay and recovery adapters

- Release Remix preview 0.1.3; preserve the decomp 0.1.18 ROM and downloads.
- Import reviewed decomp callbacks through borrowed-only hooks; native and expanded Remix fighters retain their own entry routines.
- Keep Mario/Luigi steering and Falcon Kick slope angles outside body joints. Rotate Fire Fox hitboxes around the source launch pivot.
- Carry donor air attributes through helpless fall and use independent source landing clocks for Mario/Luigi, Link, Samus, Fox, Pikachu, Falcon and Ness.
- Connect donor-sized Reflector/PSI Magnet weapon/item collision volumes and source projectile sockets.
- Isolate Tornado expenditure, held eggs, Spin Attack weapons, Thunder and PK Thunder pointers/passives/trails from the body's unions; clean owned weapons on interruption and reject stale generations.
- Port Final Cutter movement/projectile placement and Stone armor/hold/timeout without installing donor-only model overlays.
- Preserve native PC-relative branches in callback trampolines and Dark Samus's initializer patch. Replace register-dependent borrowed PK Thunder wave/weapon creation paths.
- Guard donor mesh/texture/hurtbox-part commands and attached effects on borrowed bodies, fixing Samus Bomb morph/reset crashes while keeping source gameplay flags and native body hurtboxes.
- Add MIPS steering, recovery, volume, socket, interruption, armor, body-part command and native-fallback checks; extend the optional real-input CPU fixture with donor selections.
- Connect Link held-bomb common throw ownership, timing/events, donor throw values and source release sockets; preserve body-safe animation records.
- Connect Falcon Dive source attacker positioning and frame-16 release while retaining Remix native victim offsets.
- Suspend missing-joint fallbacks during native status setup, preserving the body's world position when starting borrowed specials.
- Check 24 real-input Up/Down B casts across all twelve donors, Link's second-input bomb throw, 72 Kick velocity samples, two Quick Attack zips and controlled Dive capture/release/damage with null rendering.
- Remaining special work includes rendered contact/steering acceptance and visual attachments. Full neutral, normal-specific callbacks, animations, paired grabs/throws and taunts remain later milestones.

## 0.1.19 - 2026-10-05: Remix port audit and donor movement foundation

- Release Remix preview 0.1.2; keep the decomp ROM at 0.1.18.
- Retain the actual body recipe while Remix temporarily uses special donor identity.
- Compile all 96 shared special collision/travel phases and connect borrowed Up/Down B statuses to external source scripts and body-size-compensated root geometry.
- Restore source TransN travel for Falcon Kick, Fox dash attack and Kirby forward smash; use donor attributes around native special physics.
- Use source gameplay clock overrides for phases that outlive their looping poses, retain Pikachu/Fox/Ness transform guards and generation cleanup.
- Correct the shared C importer for current animation/throw source and ELF HI16/LO16 relocation order; keep the animation pilots bounded until a streamed bank is implemented.
- Extend source/linked-byte/MIPS checks and add an optional real-input Remix CPU regression with isolated saves and null rendering.
- Add a feature-by-feature and special-by-special decomp-to-Remix matrix. Full neutral/normal callbacks, special ownership/sockets/recovery, shared animations, paired grabs/throws, taunts and rendered acceptance remain pending.

## 0.1.18 - 2026-10-05: Taunt growth, VS defaults and match endings

- Apply Mario's original growth/shrink track to borrowed taunts, including Yoshi, and restore body scale on interruption.
- Start VS with four stocks and items off without changing 1P/demo defaults or preventing later rule changes.
- Fix the match-end freeze by giving the full-roster results/victory scene the guarded Expansion Pak arena.
- Add source-animation growth checks and live ROM regressions for Yoshi's L taunt and stock results/Start/rematch flow. Rendered acceptance remains pending.

## 0.1.17 - 2026-10-05: Normal attack momentum

- Fix the donor normal TransN flag: legacy descriptor macro labels were reversed, so Fox dash attack and Kirby forward smash lost their original movement.
- Regenerate normal travel using the native flag and keep donor size, source clocks and native traction selection.
- Keep the sampled end-to-start velocity at repeated rapid-jab loop boundaries.
- Check flag packing with the MIPS compiler, compare root velocities with original C animation playback, and add live ROM movement/recovery checks.
- Rendered movement/contact acceptance remains pending; Build One retains its Yoshi recipe.

## 0.1.16 - 2026-10-05: Yoshi starter build

- Set default Build One to the requested Yoshi recipe, including all normal attacks, specials, grab/throws and Mario's taunt.
- Document every donor in the play guide and include that guide in the download package.
- Check the initialized recipe in the linked ROM alongside the existing build/host checks; rendered playtesting remains pending.

## 0.1.15 - 2026-10-05: Customizable taunts

- Add an independent TAUNT donor to each build, plus body reset and randomization.
- Share all twelve donor taunt poses, original durations and grab/guard cancel windows across all twelve bodies.
- Preserve Luigi's original 1-damage foot hitbox/path and frames 47-49 active window.
- Retain safe donor audio/rumble/common effects; keep body hurtboxes native.
- Add production selection/cancel, original-C collision, ROM-input and linked-data checks.
- Foreign body scaling, facial/mesh variants and rendered visual acceptance remain pending.

## 0.1.14 - 2026-10-05: Tether grabs and paired throws

- Add 61 donor grab/pull/throw/carry phases and 288 native victim status pairs.
- Retain donor grab hitbox paths/windows, pull offsets, release flags, facing,
  throw descriptors and capture matrices, including animated scale.
- Extend shared attacker poses to grabs/throws; victims retain their own rigs and
  donor-selected native capture/thrown animations. Add native hook/rope/beam/tongue props.
- Run DK cargo movement/jump/fall/damage/toss and Kirby lift/fall/landing mechanics
  on foreign bodies, with donor movement attributes and source timing.
- Keep state isolated by player and fighter generation; use donor sockets for
  catch effects instead of requiring hidden body joints.
- Add original-C matrix/pose, production phase/ownership and linked-ROM checks.
  Rendered contact, body intersections, materials and stage/interrupt acceptance remain pending.
- Build the checked decomp ROM/package; Remix remains unchanged.

## 0.1.13 - 2026-10-04: Shared special animations

- Reserve an Expansion Pak pose bank so the expanded catalog cannot push game
  overlays into video buffers; add link/ROM memory boundary checks.

- Extend the common retargeter to all implemented special adapters on all twelve
  bodies: 40 neutral phases, 99 Up/Down B phases and 16 helpless/landing recovery
  entries. The catalog contains 429 distinct normal/special clips.
- Keep source gameplay clocks and donor collision/travel/socket paths independent
  of pose loops, source body proportions, charge speed and directional flight.
- Fix charge loops using a permanently positive animation countdown: donor cycle
  boundaries now advance Giant Punch charge/store/release and Charge Shot loops.
- Fire stored full Giant Punch after donor startup, and keep frame-zero Up B timing
  by avoiding duplicate borrowed Mario/Luigi playback.
- Restore safe Reflector, Sing, PSI Magnet, Final Cutter and Falcon Punch effects;
  map visual joints by semantic role and retain standard interruption/hitlag cleanup.
- Add standalone native blaster, extending tongue and Stone props and a held
  Charge Shot orb. Preload required assets and keep prop scales outside body rigs.
- Add production selector/loop/recovery tests, original-engine pose/prop comparisons,
  live ROM pose sampling and linked visual-registry checks. Rendered acceptance,
  full voice/color polish, tethers and paired victim choreography remain pending.
- Build and publish the checked decomp ROM; the separate Remix ROM is unchanged.

## 0.1.12 - 2026-10-04: Donor normal mechanics

- Make jab-chain availability, buffering and third/rapid phases follow the donor
  on every original body. Preserve native thresholds, loop/end timing and refresh
  groups; Pikachu repeats jab one and Puff's unused rapid states stay unreachable.
- Add Link down-air's original contact bounce, frame-35 rewind, 30-tick rehit
  timer and fastfall cancellation to borrowed down-air.
- Add Ness bat reflection with source frame-16/22 window, socket/size and native
  projectile/item ownership behavior. Foreign normals suppress body gameplay events.
- Use donor root travel, normal traction/air physics, angled variant availability,
  aerial landing selection and mapped part-intangibility timing. Body hurtbox
  shapes, jump inventory and movement outside attacks stay native.
- Keep donor normal collision scripts valid on bodies missing a corresponding
  joint, including Samus's absent right hand; donor world paths keep the hitbox.
- Expand Training/VS asset caches to 512 entries so all twelve normal donor
  attribute/model files can load without the old cache-full freeze.
- Skip the resource-heavy intro with 4 MB memory so menus can show the existing
  8 MB gameplay requirement instead of overflowing before that guard.
- Keep native release setup for customized grabs. Fix an Egg Lay interruption
  crash by installing the original donor escape-damage descriptors on every body.
- Add production normal callback, source data and linked-ROM checks. Live CPU
  tests pass for all 144 donor/body jab chains, twelve Link bounces/Ness bat
  reflections, editor returns and four assigned VS builds (null rendering).
  Rendered contact/stage/interrupt acceptance and visual/audio polish remain open.
  This milestone is decomp only; Remix is unchanged.

## 0.1.11 - 2026-10-04: Remaining special mechanics

- Add source paths/events/sockets for bombs, eggs, Thunder, Fire Fox, Quick
  Attack, Reflector, PSI Magnet, Sing, Falcon Dive, Final Cutter and Stone on
  all original bodies. Keep native item/weapon/capture mechanics and body hurtboxes.
- Expand to 99 donor clocks and 96 collision/travel/socket phases, including
  Link's common bomb toss: frame-8 release, source hand socket and donor throw values.
- Keep native charge/zip/travel/hold/release timers independently of pose loops;
  merge parallel gameplay streams and stop at pauses. Preserve source hit fields,
  radii, changing sizes, active windows and recovery physics.
- Isolate held egg and Thunder ownership/destruction state from common status
  unions; guard cleanup across damage, capture, Training reset and respawn.
  Preload Pikachu Model for Thunder trails and all selected donor attributes.
- Reflector and PSI Magnet use source field geometry and native ownership/healing
  rules. Sing keeps its sleep collision. Falcon Dive keeps donor catch anchors
  and safe source throw descriptors. Final Cutter keeps its landing beam and
  movement multiplier without shrinking the foreign body. Stone keeps native
  38% US armor, 18-tick minimum and 160-tick timeout and is now selectable.
- Move stage selection into the Expansion Pak arena to accommodate the larger
  gameplay overlay. Add production callback, source geometry, linked-ROM and
  live CPU regression coverage; see the remaining-special-mechanics guide.
- Borrowed special poses/effects and rendered contact/stage acceptance remain
  pending. Decomp only; Remix is unchanged.

## 0.1.10 - 2026-10-04: Spin Attack, Screw Attack and Rest gameplay

- Complete donor collision paths, hit fields and gameplay clocks for Link Spin
  Attack, Samus Screw Attack and Jigglypuff Rest on every original body.
- Preserve Link's grounded spin weapon, expanding attack radii, native lifetime,
  hitlag, ground/air continuation and 40-frame ending. Remove the native wrong
  fighter/weapon pointer call and clean up owned weapons on damaging/reset exits.
  Isolate foreign spin-weapon ownership from common landing/capture status data;
  guard cleanup and move clocks against recycled fighter generations.
- Preserve Samus's separate ground/air movement, multihit/finisher sequences,
  intangible startup, platform/cliff callbacks and donor recovery physics.
- Rest keeps its one-frame 20-damage hit, original radius/knockback, 30-frame
  invulnerability and 250-frame sleep. Landing/edge transitions continue sleep.
- Use donor friction, gravity and speed limits during borrowed specials;
  recovery retains donor attributes and source landing lengths (Link 13 ticks,
  Samus 20, Mario/Luigi 25). Body hurtboxes and jump inventory remain native.
- Add production callback/physics/weapon lifecycle checks and original animation
  matrix checks for all 30 special path phases. Add optional live ROM coverage
  for these three donors, Training reset/editor return and four-slot VS.
  All three passed on all twelve bodies: 72 ground/air starts and 36 editor returns.
- Recheck the complete intro/title boot, Mario Up B, Ness steering/self-launch
  and 1,288 live normal poses on Mario.
- Special animation retargeting and rendered contact/ledge acceptance remain
  pending. Decomp only; Remix is unchanged.

## 0.1.9 - 2026-10-04: Mario/Luigi Up B gameplay

- Add source ground/air Super Jump Punch collision paths and movement on every
  original body. Preserve Mario's opening/multihit/finisher and Luigi's distinct
  25-damage sweetspot, weak continuation, angles and knockback.
- Keep native steering, facing, ground-to-air timing, aerial startup damping,
  opening invulnerability, helpless physics and 25-tick landing recovery.
- Avoid foreign TransN joints; preload donor attributes and isolate steering and
  recovery ownership. Exhaust the body's jump inventory during helpless fall.
- Add native-versus-borrowed callback/physics checks for twelve bodies, four slots,
  both facings and ground/air starts, with interruption and respawn cleanup.
- Add optional live ROM checks for source collision centers/fields, recovery and
  Training reset. Special animation retargeting and rendered acceptance remain pending.
- Live CPU checks passed both donors on all twelve bodies: 48 ground/air starts,
  24 Training resets/editor returns and four assigned VS builds.
- Recheck the full intro/title/menu boot and Ness steering/self-launch on DK.
- Decomp only; Remix retains its previous special coverage.

## 0.1.8 - 2026-10-04: black-screen startup fix

- Fix the opening room exhausting its lower-bank heap before the first frame
  after the normal animation expansion. All nineteen opening scenes now use
  the same separate Expansion Pak arena as Training/VS.
- Add an uninterrupted cold-boot regression through the full intro, title and
  actual Start input into the main menu, with heap bounds and progress checks.
  It passes all nineteen scenes with at least 2,309,952 bytes of heap headroom.
- Recheck Mario's eleven foreign normal donors (1,288 live poses), Training
  return and four assigned builds in VS with three CPUs.
- Verify every linked opening scene calls the Expansion Pak helper. Keep the
  SDK/controller layout and normal animation/gameplay tables unchanged.
- Public ROM assets and the Desktop ROM come from the same checked binary;
  downloaded copies can be tested with the new smoke-test `--rom` option.

## 0.1.7 - 2026-10-04: normal animations for everyone

- Decomp: all twelve donor normal catalogs now animate all twelve bodies, including
  angled variants, aerial landings and body-supported third/rapid jab phases.
- Share 293 compact donor clips and twelve skeleton maps instead of storing every
  body/donor combination. Preserve body meshes, bone lengths and bind scales;
  collapse shared semantic joints on compact rigs and retain native accessories.
- Keep the three established Mario pilots; normal hitbox trajectories, damage,
  knockback and donor clocks remain independent of cosmetic poses.
- Compare actual runtime output for every clip/frame/body against original C
  playback: 3,626,238 joint-world orientations, maximum matrix error 0.0007014.
- Update generators, runtime guards, source/ROM checks and play documentation.
- Live ROM CPU checks: all 132 foreign donor/body pairs, 15,248 pose samples,
  twelve Training/editor returns and four assigned VS builds. Minimum measured
  Training heap headroom is 1,971,044 bytes.
- Specials, tethers, paired throws and rendered full-roster acceptance remain
  pending. This expansion is decomp only.

## 0.1.6 - 2026-10-03: more Mario donor animations

- Decomp Mario now performs Fox, DK, Luigi and Falcon normal attacks, including
  angled variants, aerial landing poses and supported Falcon/Luigi third jabs.
- Share 94 compact clips across 115 new move variants; retain the three existing
  pilots. Donor collision values/timing remain independent of the visible pose.
- Fold reserved donor rotations into the mapped rig and clear body cosmetic
  channels to prevent double rotation; preserve TopN/facing/TransN physics.
- Add native-source world-orientation checks, complete compact runtime lifecycle
  checks and linked-ROM clip/registry verification. Rendered acceptance remains pending.
- ROM CPU checks pass for four Mario donor presets, 2,082 live compact poses,
  editor returns and four differently assigned Mario builds in VS.
- Update guides/checklists and rebuild the decomp ROM. Remix unchanged.

## 0.1.5 - 2026-10-03: donor special paths and movement

- Decomp: add generated safe event scripts and donor collision paths for 20 phases covering DK Up B, Mario/Luigi Down B, all Falcon Kick phases and Ness Up B. Original damage, radii, knockback, flags and collision timing follow the source independently of visible body poses.
- Falcon Kick follows original root movement/rotation through its native ground/air/landing/bound callbacks. DK spin/Tornado/Ness aerial physics read donor attributes; foreign Tornado state is isolated and resets on landing/respawn.
- Fix foreign Falcon Kick crashing when a placeholder pose has no TransN joint; donor movement bypasses the missing joint and stores slope-transfer angles independently.
- Ness PK Thunder spawns from its original donor socket. Its self-launch clock follows the native 28-tick action timer, keeping the nine-frame looping pose from shifting collision/recovery events.
- Add original-engine geometry/movement/socket comparisons, all-body/four-slot/both-facing helper checks, and linked-ROM pointer/packed-field verification. Emulator CPU tests pass across all twelve bodies for grounded/aerial spin, Tornado B-tap rise, Kick travel and Ness steering/controlled self-contact/recovery, plus editor returns and four-slot VS.
- Full body animation retargeting, other Up/Down B donor paths/effects and rendered contact/interruption acceptance remain pending. These changes are decomp only; Remix is unchanged.

## 0.1.4 - 2026-10-03: special timing and PK Thunder freeze fixes

- Decomp: borrowed Up/Down B phases now use 96 original source durations/loop boundaries and an independent event clock. Temporary body idle/falling poses replace repeated body specials and their unrelated root movement. Native matching-body specials retain their original implementation.
- DK Down B uses the original 3-frame startup, 34-frame slap cycle and 5-frame recovery. All four hitboxes activate on cycle frames 16-17 and 26-27, with donor positions, damage and knockback. B taps queue the next complete cycle; ending, hitlag and ground/air transitions follow the phase state.
- Fix Falcon + Ness Up B freezing in PK Thunder: preload Ness's model file for wave/trail effects as well as weapon/motion files. Foreign bodies keep Thunder trail data in separate per-player storage instead of their native passive union.
- Add host clock/state tests, linked source-table checks and original animation/matrix validation for DK's slaps. ROM CPU smoke tests cover single/repeated slaps and Ness startup/hold/expiry/recovery across all twelve bodies. Null video does not verify rendered appearance.
- Up/Down B remain experimental beyond these fixes: full donor collision paths, weapon sockets, movement/effects and rendered acceptance still need further work. Matching donor animations remain a later milestone. Remix is unchanged.

## 0.1.3 - 2026-10-03: remaining neutral donors and Training loading fix

- Decomp: add Falcon Punch, Pound, Giant Punch, Charge Shot, Boomerang and Egg Lay on all original bodies. All eleven non-copy neutral donors are now selectable alongside Body Move.
- Preserve source melee hitboxes/knockback/timing, ground travel and aerial boosts. Add independent charge/store/release state, native boomerang return/catch and Yoshi capture/egg handoff without borrowing another body's passive union.
- Fix the Test in Training freeze: full-roster preview resources overflowed the original lower-bank heap. Training/VS selection and matches now use a separate Expansion Pak arena. The ROM requires 8 MB RDRAM; the editor displays this and blocks launching tests/VS with only 4 MB.
- Check all 30 donor phases against original animation playback/matrices and all foreign bodies/four slots against the actual adapters. Linked-ROM checks include every phase pointer and packed source hitbox field.
- Emulator CPU smoke tests exercise the full Training launch/return flow across twelve body/neutral choices, four presets, a four-slot VS match and the 4 MB launch guard. Borrowed Egg Lay initializes captured physics from the donor path, avoiding missing body sockets, and preloads native egg effects. These tests use null rendering; visual acceptance remains pending.
- Visible neutral animations still belong to the body. Samus's held charge orb, donor effects/voices and exact captured-victim rotation remain pending, along with rendered contact/reflect/absorb acceptance. New adapters remain decomp only.

## 0.1.2 - 2026-10-03

- Decomp: add Mario Fireball, Luigi Fireball, Pikachu Thunder Jolt and Ness PK Fire to Neutral B, alongside Body Move/Fox Laser.
- Borrowed projectiles use native weapon behavior, donor spawn positions and original firing/recovery timing on every original body. Landing/edge transitions preserve progress and prevent duplicate shots.
- Add all-body/four-slot adapter tests, original animation/matrix spawn checks and linked-ROM verification. Rendered gameplay acceptance remains pending.
- Publish a new Character Lab ROM/package; new choices are not yet ported to Remix.

## 0.1.1 - Remix borrowed-special pose/timing fix - 2026-10-03

- Replaced borrowed original-roster Up/Down B taunts with body idle/falling poses. Mario no
  longer uses his growing taunt or its root displacement for these moves.
- Added independent original-roster donor phase clocks, including frozen dash
  phases, animation speed, loops and ground/air continuation frames.
- Suppressed Pikachu Quick Attack stretching and Fox/Ness recovery pitching on
  foreign bodies; donor movement callbacks remain active.
- Added production MIPS regressions for pose selection and transform guards on
  all twelve bodies/four ports, Quick Attack recovery and its second-dash event.
- Preserved finite legacy poses for expanded donors without compiled phase clocks.
- Borrowed specials still need rendered playtesting; full donor poses, special
  hitbox paths, projectiles and paired/capture mechanics remain unfinished.

## Download/version information - 2026-10-03

- Put both ROM and play-package downloads together in the root README.
- Added project version 0.1.0, a last-updated date and each published ROM's date
  and exact source build.
- Documented how to keep these fields current when publishing releases.

## Character Lab on Remix preview - 2026-10-03

- Ported original-roster donor normal values, timing and root-relative collision
  paths through Remix native engine hooks, using the shared Character Lab tables.
- Added grab/throw selections, donor throw values, DK direct foreign throw,
  Body Move/Fox Laser, Mario animation pilots and return from Training to the editor.
- Preserved SRAM presets, human/CPU assignments, native display/unlocks and
  the improved combo meter. Expanded-roster fidelity remains a future task.
- Added checked build/ROM/ZIP packaging and production MIPS execution tests;
  rendered gameplay acceptance remains pending. Older Remix SRAM resets once.
- Updated play/build guides and both feature checklists.

## Training grab combo continuity - 2026-10-02

- Training keeps combo count and damage during capture, cargo carry and throw
  windup, continuing into throw hitstun for native fighters and creator builds.
- Production counter regression tests cover all bodies/slots, recovery and escape,
  empty grabs and scene isolation; linked counter code is verified in the new ROM.
- Updated guides/checklists and recorded a future Remix port assessment. Remix
  gameplay is unchanged; it already has an improved combo meter.

## Full normal donor collision paths - 2026-10-02

- Original paths across all twelve donor/body choices for normal attacks, angled
  variants, weapon/tail attacks, multihits, landing hits and body-supported jab phases.
- One shared descriptor/fallback catalog; direct lookup and trimmed frame tables
  preserve donor reach without per-body trajectory data or new player allocations.
- Engine joint enable/insertion/traversal, extra rotation channels, Luigi translation
  scaling, raw track-length commands and rapid-jab cycles supported by the converter.
- Native playback/matrix checks for all 293 resolved timelines; 396 registry entries,
  repeated loops, foreign bodies and linked ROM bytes verified.
- Updated checklist and new ROM/ZIP. Visible animations remain body-owned outside
  the Mario pilot; in-game acceptance and donor-specific mechanics remain pending.

## Falcon up-air and shared move registration — 2026-10-02

- Falcon up-air follows its original collision path on Kirby and all other bodies,
  preserving damage/knockback phases, active windows, recovery and landing timing.
- Generated donor-move registry replaces individual runtime move branches.
  One donor trajectory serves every body; native verification expands from the
  same move catalog, including multiple attacks from one donor.
- Updated documentation/checklists and checked ROM/ZIP release.

## Donor collision paths — 2026-10-02

- Kirby up-tilt uses its original hitbox path on DK and every other foreign body.
- Falcon down-air, Fox straight forward tilt and DK straight forward smash paths
  now work across bodies; visible retargeted poses remain Mario-only.
- Native engine geometry, both facings, body-size compensation and runtime
  lifecycle checks; checked local ROM/ZIP builds include these tests.
- Updated the roadmap and retained pending in-game acceptance explicitly.

## Combined project repository

- Both creator experiments now live in `lorenzosaraiva/smash-charbuilder`.
- Remix and decompilation main-branch histories are preserved as parents of the import.
- Existing Remix creator edits are included; its dependency's Sonic creator hook
  is stored as a reproducible source override.
- One root README, issue forms, build entry point and release workflow.
- Character Lab ROM and play package are also copied to root `dist/`.
- Python environments stay local and are no longer tracked.

The current Character Lab gameplay is unchanged by this migration. See its
[gameplay changelog](ssb-decomp-re/CHANGELOG.md),
[feature checklist](ssb-decomp-re/docs/status.md), and the
[Remix creator guide](remix/character_creator_guide.md) for each version's behavior.
