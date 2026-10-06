"""Generate, assemble, execute-check and package Character Lab on Remix."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
DIST = PROJECT / 'dist'
BASE_SHA1 = 'e2929e10fccc0aa84e5776227e798abc07cedabf'
VERSION = '0.1.3'
UPDATED = '2026-10-05'


def run(command, stage, cwd=ROOT):
    print(stage+'...', flush=True)
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, errors='replace')
    log = ROOT / ('charlab-'+stage.replace(' ', '-').lower()+'.log')
    log.write_text(result.stdout+result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{stage} failed; see {log}\n'+(result.stdout+result.stderr)[-5000:])
    if stage == 'Verify ROM':
        print(result.stdout, end='', flush=True)


def linux(command):
    return ['wsl.exe', '-d', os.environ.get('SMASH_WSL_DISTRO', 'Ubuntu'), '--', *command] if os.name == 'nt' else command


def git(*args):
    return subprocess.check_output(['git', *args], cwd=PROJECT, text=True).strip()


def source_hash():
    digest = hashlib.sha256()
    names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=PROJECT).decode().split('\0')
    for name in sorted(set(names)):
        path = PROJECT/name
        if name and path.is_file():
            digest.update(name.encode()+b'\0'+path.read_bytes())
    digest.update(git('submodule', 'status', '--recursive').encode())
    return digest.hexdigest()


def package(desktop=None):
    receipt = json.loads((ROOT/'build/char_creator/build-source.json').read_text())
    assert receipt['source_sha256'] == source_hash(), 'Source changed since assembly; rebuild before packaging.'
    rom = (ROOT/'ssb64asm_extra.z64').read_bytes()
    assert receipt['rom_sha256'] == hashlib.sha256(rom).hexdigest(), 'ROM changed after verification.'
    info = {
        'version': VERSION, 'last_updated': UPDATED,
        'commit': git('rev-parse', 'HEAD'),
        'source_dirty': bool(git('status', '--porcelain', '--untracked-files=normal')),
        'source_directory': 'remix', 'base_sha1': BASE_SHA1,
        **receipt, 'rom_bytes': len(rom),
        'scope': 'Character Lab features for original twelve bodies/donors on Smash Remix +EXTRA',
        'in_game_acceptance': 'pending',
    }
    scene_reports=[]
    for scene_report in sorted((ROOT/'build/char_creator/emulator').glob('cpu-scenes*.json')):
        report=json.loads(scene_report.read_text())
        if report.get('rom_sha256')==info['rom_sha256']:
            scene_reports.append(report)
    if scene_reports:
        info['optional_cpu_scene_checks']=scene_reports
    DIST.mkdir(exist_ok=True)
    play = (ROOT/'character_creator_guide.md').read_bytes()
    notes = f'''# Character Lab on Remix {VERSION} - original-roster preview

Updated: {UPDATED}. This is a partial port; see STATUS.md and PLAY.md.

Source commit: `{info['commit']}`; uncommitted changes: {info['source_dirty']}.

Original donor collision paths/timing, normal values, grab/throw choices,
Body Move/Fox Laser, Mario animation pilots and return from Training to the
tested editor. Borrowed Up/Down B now connects original donor collision paths,
phase clocks, TransN travel and donor physics attributes while showing safe
body idle/falling poses. Donor helpless/landing recovery, Mario/Luigi steering,
Fire Fox directional geometry, Reflector/Magnet volumes and source projectile
sockets are connected. Tornado, egg, Spin Attack, Thunder and PK Thunder own
state outside the body's unions; Final Cutter and Stone gameplay callbacks
retain source timing ahead of visual retargeting. Link held-bomb common throws
retain donor timing, values and release sockets; Falcon Dive uses the source
attacker socket and frame-16 release with native Remix victim offsets.
Pikachu/Fox/Ness recovery transform guards remain active.
Use Settings -> CHARACTER LAB; keep Original 12 Only enabled.
Assign Custom Build in the VS/Training CSS Player Settings for human/CPU slots.
Remix's existing HITBOX/HITBOX+ display and improved combo meter remain available.

The ROM is checked with shared host tests, linked-byte/CRC verification and
production MIPS execution tests. Rendered gameplay acceptance is still pending.
Full decomp parity is pending: neutral adapters beyond Laser, rendered
special acceptance,
normal jab/bounce/reflection mechanics, taunts, retargeted animations and paired
grabs/throws. Expanded-roster fidelity and Kirby copy are outside this milestone.
The changed SRAM layout resets older Remix settings/recipes once.

SHA-256: `{info['rom_sha256']}`
'''
    payloads = {
        'remix-character-lab.z64': rom,
        'build-info.json': (json.dumps(info, indent=2)+'\n').encode(),
        'PLAY.md': play,
        'STATUS.md': (ROOT/'docs/character-lab-status.md').read_bytes(),
        'PORT-STATUS.md': (ROOT/'docs/decomp-port.md').read_bytes(),
        'CHANGELOG.md': (PROJECT/'CHANGELOG.md').read_bytes(),
        'release-notes.md': notes.encode(),
    }
    checksum = ''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name, data in payloads.items()).encode()
    payloads['SHA256SUMS.txt'] = checksum
    archive = DIST/'remix-character-lab.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in payloads.items():
            z.writestr(name, data)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and z.read('remix-character-lab.z64') == rom
    (DIST/'remix-character-lab.z64').write_bytes(rom)
    (DIST/'remix-build-info.json').write_bytes(payloads['build-info.json'])
    (DIST/'remix-PLAY.md').write_bytes(play)
    (DIST/'remix-release-notes.md').write_text(notes, encoding='utf-8')
    names = ('remix-character-lab.z64', 'remix-character-lab.zip', 'remix-build-info.json')
    (DIST/'remix-SHA256SUMS.txt').write_text(''.join(hashlib.sha256((DIST/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in names), encoding='utf-8')
    if desktop:
        destination = Path(desktop)
        destination.mkdir(parents=True, exist_ok=True)
        target = destination/'smash-character-lab-remix.z64'
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != info['rom_sha256']:
            shutil.copy2(target, target.with_suffix('.previous.z64'))
        shutil.copy2(DIST/'remix-character-lab.z64', target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == info['rom_sha256']
        print('ROM copied to '+str(target), flush=True)
    print('Checked Remix ROM and ZIP ready in '+str(DIST), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--incremental', action='store_true', help='Reuse generated assets/menu; rebuild owned runtime/ASM only.')
    parser.add_argument('--package-only', action='store_true', help='Recheck and package an unchanged verified build after committing.')
    parser.add_argument('--desktop', help='Optional directory for smash-character-lab-remix.z64')
    args = parser.parse_args()
    base = ROOT/'smashremix/roms/ssb.rom'
    assert base.is_file() and hashlib.sha1(base.read_bytes()).hexdigest() == BASE_SHA1, 'Place the original US ROM at remix/smashremix/roms/ssb.rom (see docs/building.md).'
    if not args.package_only:
        if args.incremental:
            run([sys.executable, 'scripts/build_charlab_runtime.py'], 'Compile shared runtime')
        else:
            run([sys.executable, 'character_appender.py'], 'Generate Remix assets')
        assembler = ROOT/'smashremix/assembler'
        prefix = [] if os.name == 'nt' else ['wine']
        run([*prefix, str(assembler/'bass.exe'), '-o', 'ssb64asm_extra.z64', 'main.asm', '-sym', 'logfile.log'], 'Assemble ROM')
        run([*prefix, str(assembler/'rn64crc.exe'), '-u', 'ssb64asm_extra.z64'], 'Update CRC')
    lab = PROJECT/'ssb-decomp-re'
    (lab/'build').mkdir(exist_ok=True)
    run(linux(['gcc', '-m32', '-nostdlib', '-static', '-fno-pie', '-fno-stack-protector', '-O1',
               '-Iinclude', '-Isrc', '-D__sgi', '-D_LANGUAGE_C', '-D_MIPS_SZLONG=32', '-DREGION_US',
               'tools/testCustomMove.c', '-o', 'build/testCustomMove']), 'Compile shared host tests', lab)
    run(linux(['build/testCustomMove']), 'Run shared host tests', lab)
    run(linux(['python3','tools/testNormalMechanics.py']), 'Check source normal travel', lab)
    run(linux(['python3','tools/testSpecialTiming.py']), 'Check source special paths', lab)
    run([sys.executable, 'scripts/verify_charlab_rom.py'], 'Verify ROM')
    if not args.package_only:
        receipt = {'source_sha256': source_hash(), 'rom_sha256': hashlib.sha256((ROOT/'ssb64asm_extra.z64').read_bytes()).hexdigest()}
        (ROOT/'build/char_creator/build-source.json').write_text(json.dumps(receipt, indent=2)+'\n')
    package(args.desktop)


if __name__ == '__main__':
    main()
