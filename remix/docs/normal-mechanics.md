# Donor normal mechanics on Remix

Preview **0.1.11**, updated **2026-10-07**. Original twelve bodies/donors only.
Implementation and automated checks are separate from rendered acceptance.

Foreign normal effect commands resolve donor bones to valid body joints or
TopN before native effect placement. Donor model/texture and part-hurtbox
commands cannot address foreign body parts. This fixes both DK/Samus borrowed
down-smash freezes; both combinations pass real-input CPU recovery checks,
alongside 396 missing-effect-joint production MIPS cases. Original donor
collision paths, timing, damage and knockback remain unchanged.

The Jab row chooses the donor's whole playable chain. Mario/Luigi/Ness have
three jabs; DK/Samus/Yoshi/Jigglypuff have two; Pikachu repeats jab one;
Fox/Kirby can enter rapid jabs; Link forks from jab two into jab three or rapid
jabs; Falcon reaches rapid jabs after jab three. Jigglypuff's unused rapid
entries remain unreachable through its original jab-two event gate.

Tap A within the source follow-up window. Repeated presses/releases request
rapid jabs where supported. Source thresholds count press/release events:
five for Link, six for Falcon, four for Fox/Kirby. Stop tapping to finish through
the donor's ending. The source event stream owns jab gates and loop boundaries;
the body cannot add flags or shorten the attack with its own animation.

Unique jab phases select the donor's native Remix status array while keeping
the actual body identity. A safe body Jab1 clip sits under the shared donor pose;
source collision events supply timing and hit groups without donor model files.
Missing body angle/landing clips use a safe Idle pose underneath the shared pose.
Native/expanded fighters retain their original entry routes, including Remix's
Mewtwo and Slippy jab patches.
Remix's aerial-fastfall toggle enters complete guarded physics functions;
its earlier function+4 shortcut would skip their return-address setup.

Link down-air clears attacks on contact, cancels fastfall and gives upward
velocity 40. Hits after frame 35 rewind there, start a 30-tick rehit timer and
refresh hitboxes before the original frame-65 cutoff. This follows the selected
down-air donor, not the body.

Ness forward-smash enables reflection from source flag timing (frames 16-22).
Its TopN-relative bat sphere retains offset `(0,150,0)`, dimensions
`(300,300,300)`, resistance 1000 and Ness's original size. The sampled donor
socket supplies placement independently of the body's animated limbs. Native
Remix weapon/item collision paths own reflection and outgoing behavior.

Forward-/up-tilt and forward-smash variants use donor motion availability.
Aerial landing branches use donor clips/flags and native Z-cancel rules. During
a borrowed normal or its landing clock, source TransN travel, traction, gravity,
terminal speed, fastfall speed and air drift apply. Exits and fighter-generation
changes restore body physics. Body weight, hurtbox shapes, jump inventory and
movement outside the attack stay native. Scalar donor fields come from owned
original US sources; normal physics does not allocate donor model files.

Neutral Special now displays the selected Body's name or **Fox**, just like the
other donor rows. The native selection follows body edits independently on each
of the four saved builds. The two saved enum values and SRAM layout are unchanged.

## Verification and remaining acceptance

Shared production host checks validate donor normal sources. The linked-ROM
verifier checks all forty guarded entry hooks and executes donor jab transitions,
rapid-loop/end clocks, bounce/rehit, bat flags/geometry, donor air/traction,
landing branch availability, safe jab poses and dynamic labels. Native status,
contact and rendering services are explicitly isolated in these MIPS fixtures.
Real-input CPU scene checks separately exercise the complete native state setup.
On preview 0.1.6 they pass Fox and Link chains on Mario, Mario's third jab on
Kirby, and Pikachu's repeating jab on Yoshi, plus ground/aerial clip streaming,
finite joints and recovery. Link's two jab forks and controlled native down-air
contact/bounce both pass. These scenes use null rendering.
The existing Falcon Kick/Quick Attack regression and editor Test -> CSS Start ->
stage confirmation -> running Training also pass with the new normal hooks.

Run `scripts/test_charlab_scenes.py --normal-animations DONOR --normal-mechanics`
with the documented compatible Mupen64Plus core/header options for these optional
controller checks. `--body BODY` selects a target rig; IDs are the original
roster order used by the shared catalog (Mario 0, Fox 1, Link 5, Yoshi 6,
Kirby 8, Pikachu 9). Build metadata includes only reports matching that ROM's
SHA-256.

Rendered contact, bat projectiles/items, slopes, aerial starts, Z-cancel windows,
hitlag, interruptions, four-player stress and expanded native-fighter regressions
remain acceptance work. The listed special attachments are now ported; see
[special effects](special-effects.md). Other normal overlays/materials,
tether/paired throws and taunts remain separate work.
