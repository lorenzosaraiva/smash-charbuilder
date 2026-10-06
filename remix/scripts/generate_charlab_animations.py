"""Pack the checked decomp pose catalog into ROM, with one bounded cache per port.

Reuse generated source curves verbatim: no combination-specific animations and
no resampling of gameplay clocks. Bind/semantic rigs remain small resident data.
"""
from pathlib import Path
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'ssb-decomp-re'
OUT = ROOT / 'build/char_creator/runtime'
ROM_START = 0x5000000


def generate():
    shared = (LAB/'src/ft/ftcustomanimationshared.generated.inc').read_text(encoding='utf-8')
    key_text = (LAB/'src/ft/ftcustomanimationkeys.generated.inc').read_text(encoding='utf-8')
    keys = [tuple(map(int, row)) for row in re.findall(r'\{ (\d+), (\d+), (\d+) \}', key_text)]
    curve_text = re.search(r'const FTCustomAnimationCurve .*? = \{ (.*?) \};', shared).group(1)
    curves = [tuple(map(int, row)) for row in re.findall(r'\{ (\d+), (\d+), 0 \}', curve_text)]
    channel_rows = {name: list(map(int, data.split(', '))) for name, data in
                    re.findall(r'const u16 (\w+)\[\] = \{ (.*?) \};', shared)}
    roots = {name: [tuple(map(int, row.split(', '))) for row in re.findall(r'\{ ([^{}]+) \}', data)]
             for name, data in re.findall(r'const Vec3h (\w+)\[\] = \{ (.*?) \};', shared)}
    definitions = re.findall(r'const FTCustomAnimationClip (\w+) = \{ &(\w+), (\w+), (\w+), (\d+), (\d+), (\d+) \};', shared)
    bank = bytearray()
    records = []
    manifest = []
    max_size = 0
    for symbol, rig, channels, root, count, loop_start, period in definitions:
        channels = channel_rows[channels]
        payload = bytearray(len(channels)*8)
        clip_keys = bytearray()
        for i, index in enumerate(channels):
            first, length = curves[index]
            struct.pack_into('>IHH', payload, i*8, len(clip_keys)//3, length, 0)
            clip_keys.extend(b''.join(bytes(value) for value in keys[first:first+length]))
        key_offset = len(payload)
        payload.extend(clip_keys)
        payload.extend(bytes((-len(payload)) % 16))
        root_offset = len(payload)
        payload.extend(b''.join(struct.pack('>hhh', *value) for value in roots[root]))
        payload.extend(bytes((-len(payload)) % 16))
        assert len(roots[root]) == int(count)
        offset = len(bank)
        bank.extend(payload)
        max_size = max(max_size, len(payload))
        records.append('static const CCAnimationRecord '+symbol+' __attribute__((used)) = { &'+rig+', '+
                       ', '.join(map(str, (offset, len(payload), key_offset, root_offset, int(count), int(loop_start), int(period))))+' };')
        manifest.append(dict(symbol=symbol, offset=offset, size=len(payload), channels=channels,
                             key_offset=key_offset, root_offset=root_offset, count=int(count)))
    # Only bind rigs/maps stay resident. Every curve, key and root sample lives
    # in the ROM bank, including clips reserved for later paired-move adapters.
    declarations = re.findall(r'const (FTCustomAnimationSourceBone|FTCustomAnimationSourceRig|FTCustomAnimationBone|FTCustomAnimationRig|u8) (\w+)(.*?) = (.*?);', shared, re.S)
    out = ['/* Generated shared rigs and ROM clip descriptors. */',
           '#define CC_ANIMATION_CACHE_BYTES '+str(max_size),
           '#define CC_ANIMATION_ROM_START '+hex(ROM_START)]
    for kind, name, suffix, value in declarations:
        out.append('static const '+kind+' '+name+suffix+' = '+value+';')
    out.extend(records)
    table = re.search(r'const FTCustomAnimationClip \*const sFTCustomAnimationClips\[12\]\[33\] = (.*?);', shared, re.S).group(1)
    out.append('static const CCAnimationRecord *const sCCNormalAnimations[12][33] = '+table+';')
    sys.path.insert(0, str(LAB/'tools'))
    from sharedAnimation import special_rows, catalog
    from customMoveCatalog import motion_descriptors
    from customAnimation import flag_word
    cases, _ = catalog()
    out.append('static const struct { s32 donor, motion; const CCAnimationRecord *clip; } sCCSpecialAnimations[] = {')
    seen = set()
    for phase, index in special_rows():
        motion = phase['motion']
        if motion < 0:
            matches = [i for i, desc in enumerate(motion_descriptors(phase['fighter'])[1])
                       if desc[0] == '&ll'+phase['name']+'FileID' and flag_word(desc[2]) == phase['flags']]
        else:
            matches = [motion]
        for motion in matches:
            identity = (phase['donor'], motion)
            if identity in seen:
                continue
            seen.add(identity)
            out.append('    { '+str(identity[0])+', '+str(motion)+', &'+cases[index]['symbol']+' },')
    out.append('};')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'animations.inc').write_text('\n'.join(out)+'\n', encoding='utf-8')
    (OUT/'animations.bin').write_bytes(bank)
    (OUT/'animations.json').write_text(json.dumps(dict(rom_start=ROM_START, cache_bytes=max_size, clips=manifest), indent=2)+'\n', encoding='utf-8')
    assert max_size <= 0x8000, 'Pose clip exceeds the reserved per-player RAM budget'
    print(f'Packed {len(records)} donor clips: {len(bank):,} ROM bytes, {max_size:,} cache bytes per player.')


if __name__ == '__main__':
    generate()
