#!/usr/bin/env python3
"""Package a checked US build; use fixed asset names for permanent download links."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile

from n64crc import calculate_crcs

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA1 = 'e2929e10fccc0aa84e5776227e798abc07cedabf'


def check_base():
    path = ROOT / 'baserom.us.z64'
    if not path.is_file():
        raise ValueError('Place the original US Smash 64 ROM at baserom.us.z64. See docs/building.md.')
    if hashlib.sha1(path.read_bytes()).hexdigest() != BASE_SHA1:
        raise ValueError('baserom.us.z64 is not the expected original US ROM. See docs/building.md for its SHA-1.')


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=ROOT, text=True, timeout=30).strip()


def source_dirty():
    try:
        return bool(git('status', '--porcelain', '--untracked-files=normal', '--ignore-submodules=untracked', '--', '.'))
    except subprocess.TimeoutExpired:
        print('Git status timed out; recording local change status as unknown.')
        return None


def package():
    check_base()
    source = ROOT / 'build/smashbrothers.us.z64'
    rom = source.read_bytes()
    if len(rom) < 0x101000 or rom[:4] != b'\x80\x37\x12\x40':
        raise ValueError('The build is not a big-endian N64 ROM.')
    if calculate_crcs(rom) != struct.unpack_from('>II', rom, 0x10):
        raise ValueError('The built ROM checksum is invalid; rebuild before packaging.')
    metadata = {
        'project': 'Smash 64 Character Lab',
        'commit': git('rev-parse', 'HEAD'),
        'source_dirty': source_dirty(),
        'source_directory': git('rev-parse', '--show-prefix').rstrip('/') or '.',
        'rom': 'character-lab.z64',
        'rom_bytes': len(rom),
        'rom_sha256': hashlib.sha256(rom).hexdigest(),
        'base_sha1': BASE_SHA1,
        'version': '0.1.15',
        'built_at': datetime.now(timezone.utc).isoformat(),
    }
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    shutil.copyfile(source, output / metadata['rom'])
    (output / 'build-info.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    notes = f'''# Smash 64 Character Lab — experimental build

Source commit: `{metadata['commit']}`
Version: {metadata['version']} | Built (UTC): {metadata['built_at'][:10]}
Local uncommitted changes: {metadata['source_dirty'] if metadata['source_dirty'] is not None else 'unknown'}

Mix normal attacks, grabs and throw parameters across the twelve original fighters.
Normal and implemented special animations follow the selected donor on every
body, including charge loops, phase transitions, recovery and required props.
Donor tether paths and paired grab/throw mechanics are implemented; rendered
contact and visual polish still need testing.
TAUNT selects any original donor's poses, duration and cancel window. Press L;
Luigi's taunt keeps its original 1-damage hitbox on frames 47-49. See custom-taunts.md.

1. Enable 8 MB RDRAM / Expansion Pak, then open `character-lab.z64`.
2. Go to Options -> Character Lab and select a build with A.
3. Choose a body and change attack donors with left/right.
4. Use Test in Training, or assign a build to a player/CPU slot and choose Play VS.
5. In Training, press Start -> View -> HITBOX to see attack and hurtbox outlines.
6. Exit a training test to reopen the same build's editor.

Builds and player assignments last for the running ROM session.
Training combo count/damage survive grabs, cargo holds and throw windup, then
reset after release and hitstun end. A bare grab adds no hit or damage.
Neutral B offers Body Move, Fox Laser, Mario Fireball, Luigi Fireball,
Thunder Jolt, PK Fire, Falcon Punch, Pound, Giant Punch, Charge Shot, Boomerang
and Egg Lay. The projectiles keep native weapon behavior,
donor spawn positions and firing/recovery timing on all original bodies. Landing
and edge transitions continue the clock without a second shot. Borrowed neutral
phase poses, charge loops, native props and a held charge orb are implemented;
complete voice/color polish and rendered acceptance remain pending.
Giant Punch/Charge Shot charge on ground: B/A releases, Z or a ground roll stores.
A fully stored charge fires on the next B; airborne Charge Shot fires immediately.
Boomerang returns/catches natively; Egg Lay captures into the native egg state.
Training/VS and all opening movie scenes now use the extra memory bank.
This fixes the preview allocation freeze and the black-screen cold-boot intro overflow.
These new choices are decomp only; rendered projectile acceptance is pending.
Borrowed Up/Down B use source phase clocks and shared retargeted phase poses.
DK Down B keeps its original startup/slap/recovery and repeated hit windows;
tap B during a cycle to queue another. Ness Up B now loads its wave/trail models
on foreign bodies and keeps separate trail state, fixing the freeze.
DK Up B, Mario/Luigi Tornado and Falcon Kick now keep original donor collision
paths and numeric values. Falcon Kick uses source movement; spin/Tornado use
donor aerial physics. Foreign Tornado rise state resets on landing/respawn.
Ness uses its source projectile socket and native 28-tick self-launch clock.
Safe native special effects and shared phase poses are implemented; rendered acceptance remains pending.
Mario/Luigi Up B now use original donor collision paths and distinct hit phases,
source movement/steering, donor helpless physics and 25-tick landing recovery.
Luigi retains his original 25-damage opening sweetspot and weak continuation.
Shared Up B and recovery poses are implemented; rendered contact/ledge acceptance is pending.
Link Spin Attack, Samus Screw Attack and Rest now preserve source collision
paths, hit fields, timing and movement. Grounded Spin Attack keeps its native
expanding weapon and 40-frame ending. Screw Attack keeps distinct ground/air
multihits, intangibility and donor recovery. Rest hits once for 20 damage and
keeps its 30-frame invulnerability and 250-frame sleep across landings/edges.
Remaining Up/Down B mechanics now include bombs, eggs, Thunder, Fire Fox,
Quick Attack, Reflector, PSI Magnet, Sing, Falcon Dive, Final Cutter and Stone.
Hold B for egg charge/Reflector/PSI Magnet; change direction for Quick Attack's
second zip; tap B after Stone's minimum hold to release. Native projectiles,
source hit paths/timing, capture/absorb/reflect behavior and donor recovery work
on original bodies. Link's second Down B toss keeps its frame-8 release and throw
values. Thunder trails are preloaded; owned weapons survive status-union changes.
Stage selection uses the Expansion Pak arena too.
Normal mechanics now include donor jab chains on every body, Link down-air
bounce, Ness bat reflection and donor root travel/attack physics. Angle and
landing availability follow the donor. Training/VS caches hold 512 assets for
mixed builds. Part-intangibility follows donor timing on native body hurtboxes.
Grabs keep native release setup, and interrupted Egg Lay uses original escape
descriptors. With 4 MB, startup skips the intro and lab gameplay stays blocked.

Shared special animations are implemented; rendered contact acceptance remains pending.
Throws retain donor damage/knockback, release timing, capture positions and victim
queues. DK forward throw enables cargo carry; Kirby forward throw enables its
lift/landing mechanic. Each fighter keeps its own rig.
All twelve bodies now perform all twelve donor normal attacks, including angled
variants, aerial landings and donor jab phases on every body. Shared curves adapt
motion to the body skeleton. Special, grab and throw phases use the shared catalog.
Link/Samus/Yoshi tethers retain source reach and native props. Rendered contact,
victim alignment and materials remain pending.
Original donor collision paths now cover every normal attack on every foreign
body, including angled variants, weapon/tail paths, multihits, landing collisions
and donor jab phases on every body. Size, timing, damage and knockback follow the donor.
Try Kirby Body -> Up Air: Falcon -> Test in Training -> View: HITBOX, or change
any normal donor. The visible normal animation now follows the donor on the selected body.
Full native-code geometry checks pass; in-game acceptance remains pending.

See paired-grabs-and-throws.md for tether/cargo controls and paired throw coverage.
See the repository README, docs/status.md and CHANGELOG.md for scope and known gaps.
The package contains the ROM, guides, build information and SHA-256 checksums.
'''
    (output / 'PLAY.md').write_text(notes, encoding='utf-8')
    inner_sums = ''.join(f'{hashlib.sha256((output / name).read_bytes()).hexdigest()}  {name}\n'
                         for name in ('character-lab.z64', 'build-info.json'))
    (output / 'SHA256SUMS.txt').write_text(inner_sums, encoding='utf-8')
    with zipfile.ZipFile(output / 'character-lab.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('character-lab.z64', 'PLAY.md', 'build-info.json', 'SHA256SUMS.txt'):
            archive.write(output / name, arcname=name)
        for name in ('CHANGELOG.md', 'docs/status.md', 'docs/paired-grabs-and-throws.md', 'docs/custom-taunts.md'):
            archive.write(ROOT / name, arcname=Path(name).name)
    sums = ''.join(f'{hashlib.sha256((output / name).read_bytes()).hexdigest()}  {name}\n'
                   for name in ('character-lab.z64', 'character-lab.zip', 'build-info.json'))
    (output / 'SHA256SUMS.txt').write_text(sums, encoding='utf-8')
    (output / 'release-notes.md').write_text(notes, encoding='utf-8')
    print(f'Packaged {metadata["rom_bytes"]:,} ROM bytes from {metadata["commit"][:9]}.')
    print(f'ROM SHA-256: {metadata["rom_sha256"]}')
    print(f'Files ready in {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-base', action='store_true', help='Check the original ROM and exit.')
    args = parser.parse_args()
    try:
        check_base() if args.check_base else package()
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
