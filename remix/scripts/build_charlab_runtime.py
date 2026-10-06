"""Compile the shared Character Lab runtime for Remix's original fighter ABI.

The generated header shim removes IDO-only incomplete extern arrays and retains
Remix's two native motion streams. Extra collision scripts live outside fighters.
Clang emits an o32 MIPS-II object (supported by the N64); Bass resolves its
absolute relocations at the runtime's actual expansion-RAM address.
"""
from pathlib import Path
import os
import re
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'ssb-decomp-re'
OUT = ROOT / 'build/char_creator/runtime'


def special_timings():
    """Read US donor phase durations/loops without installing donor skeletons."""
    import sys
    sys.path.insert(0, str(LAB / 'tools'))
    from auditNormalMoves import ROSTER, us_text
    from customMoveCatalog import motion_descriptors
    from customMoveTiming import animation_duration
    from generateSpecialTiming import catalog
    rows = []
    paths = {re.sub(r'^\d+_', '', p.stem): p for p in (LAB/'src/relocData').glob('*.c')}
    for fighter in ROSTER:
        _, descriptors = motion_descriptors(fighter)
        row = [0] * 276
        for motion, desc in enumerate(descriptors):
            # Unique specials follow the shared 0..194 motion catalog.
            match = re.fullmatch(r'&ll(\w+)FileID', desc[0])
            if motion < 195 or not match:
                continue
            duration = animation_duration(desc[0])
            if duration > 4096:  # Entry assets are not fighter special phases.
                continue
            loop = bool(re.search(r'ftAnimLoop\(', us_text(paths[match[1]].read_text())))
            row[motion] = duration | (0x80000000 if loop else 0)
        rows.append(row)
    # Gameplay may intentionally outlive a looping visual (PK Thunder launch,
    # Thunder/PSI hit phases). Use the same overrides as the decomp runtime.
    for donor,motion,duration,loop,_ in catalog():
        rows[donor][motion] = duration | (0x80000000 if loop else 0)
    (OUT/'special-timings.inc').write_text(
        '/* Generated from original US motion/animation sources. */\n'
        'static const u32 sCCSpecialTimings[12][276] = {\n' +
        '\n'.join('    { '+', '.join(hex(v) for v in row)+' },' for row in rows) + '\n};\n',
        encoding='utf-8')


def prepare_headers():
    include = OUT / 'include'
    include.mkdir(parents=True, exist_ok=True)
    for path in (LAB / 'src').rglob('*.h'):
        source = path.read_text(encoding='utf-8')
        adjusted = re.sub(r'^extern (?:FTStatusDesc|FTMotionDesc) [^;]*;\s*$', '', source, flags=re.M)
        if path.name == 'fttypes.h':
            assert 'motion_scripts[2][3]' in adjusted
            adjusted = adjusted.replace('motion_scripts[2][3]', 'motion_scripts[2][2]')
        target = include / path.relative_to(LAB / 'src')
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_text(encoding='utf-8') != adjusted:
            target.write_text(adjusted, encoding='utf-8')
    # The shared neutral adapter uses the same external collision stream in
    # Remix instead of adding a third stream to the native fighter struct.
    neutral = (LAB / 'src/ft/ftcharbuilderneutral.c.inc').read_text(encoding='utf-8')
    assert neutral.count('fp->motion_scripts[i][2]') == 3
    neutral = neutral.replace('fp->motion_scripts[i][2]', 'sCCMotionScripts[fp->player]')
    neutral = neutral.replace('    sFTCharBuilderNeutralStartingOwner = fp;',
                              '    fp->proc_status = NULL;\n    sFTCharBuilderNeutralStartingOwner = fp;')
    (OUT / 'neutral.c.inc').write_text(neutral, encoding='utf-8')
    # Keep the shared retargeter; stream selected curves instead of embedding
    # the decomp's entire resident animation catalog in Remix expansion RAM.
    animation = (LAB/'src/ft/ftcustomanimation.c.inc').read_text(encoding='utf-8')
    animation=animation.replace('#include "ftcustomanimations.generated.inc"','#include "ft/ftcustomanimations.generated.inc"')
    animation=animation.replace('    const u16 *channels;', '    const u16 *channels;\n    const FTCustomAnimationCurve *curves;\n    const FTCustomAnimationKey *keys;')
    animation=animation.replace('#include "ftcustomanimationshared.generated.inc"',
        'static const FTCustomAnimationClip* ccSelectAnimation(FTStruct*, s32*);')
    animation=animation.replace('ftCustomAnimationReadCurve(const FTCustomAnimationCurve *curve, s32 frame)',
        'ftCustomAnimationReadCurve(const FTCustomAnimationKey *bank, const FTCustomAnimationCurve *curve, s32 frame)')
    animation=animation.replace('&sFTCustomAnimationKeys[curve->first]', '&bank[curve->first]')
    animation=animation.replace('ftCustomAnimationReadCurve(&sFTCustomAnimationCurves[', 'ftCustomAnimationReadCurve(clip->keys, &clip->curves[')
    start=animation.index('static const FTCustomAnimationClip* ftCustomAnimationGetClip(')
    end=animation.index('static void ftCustomAnimationSharedPose(',start)
    animation=animation[:start]+'''static const FTCustomAnimationClip* ftCustomAnimationGetClip(FTStruct *fp, s32 *frame)
{ return ccSelectAnimation(fp, frame); }

'''+animation[end:]
    animation=animation.replace('sFTCustomAnimationRigs[fp->fkind]', 'sFTCustomAnimationRigs[ccBodyKind(fp)]')
    # Rigs/descriptors are needed before the shared pose function, while the
    # selector is defined after the special/recovery clock types in runtime C.
    animation=animation.replace('u32 gFTCustomAnimationValidationFailures;', '''typedef struct CCAnimationRecord
{
    const FTCustomAnimationSourceRig *rig;
    u32 offset, size, keys, root;
    s32 count, loop_start, loop_period;
} CCAnimationRecord;
#include "animations.inc"
u32 gFTCustomAnimationValidationFailures;''')
    (OUT/'animation.c.inc').write_text(animation,encoding='utf-8')
    move=(LAB/'src/ft/ftcustommove.c.inc').read_text(encoding='utf-8')
    assert move.count('(slot->body != fp->fkind)') == 1
    move=move.replace('(slot->body != fp->fkind)','(slot->body != ccBodyKind(fp))')
    move=move.replace('&fp->motion_scripts[0][2]', '&sCCMotionScripts[fp->player]')
    move=move.replace('&fp->motion_scripts[1][2]', '&sCCMotionScripts[fp->player]')
    # Unique jab motion IDs belong to the donor selected by action_array_hook_.
    move=move.replace('sFTCustomBodyExtraMotionIDs[fp->fkind]', 'sFTCustomBodyExtraMotionIDs[slot->attacks[nSCCharBuilderAttackJab]]')
    move=move.replace('#include "ftcustomanimation.c.inc"','#include "animation.c.inc"')
    move=re.sub(r'#include "(ft[^"/]+\.inc)"',r'#include "ft/\1"',move)
    (OUT/'move.c.inc').write_text(move,encoding='utf-8')
    throw = (LAB / 'src/ft/ftcommon/ftcommonthrow.c').read_text(encoding='utf-8')
    throw=re.sub(r'^    if \(ftMainCharBuilderTryPairedThrow\([^\n]+\n','',throw,flags=re.M)
    for direction in (0, 1):
        throw = throw.replace(f'this_fp->attr->thrown_status[catch_fp->fkind].ft_thrown[{direction}]',
                              f'this_fp->attr->thrown_status[ccMappedThrownKind(catch_fp->fkind, {direction})].ft_thrown[{direction}]')
    (OUT / 'throw.c').write_text(throw, encoding='utf-8')


def object_to_bass(path):
    data = path.read_bytes()
    assert data[:6] == b'\x7fELF\x01\x02', 'Expected big-endian ELF32.'
    shoff = struct.unpack_from('>I', data, 32)[0]
    shentsize, shnum, shstr = struct.unpack_from('>HHH', data, 46)
    sections = [struct.unpack_from('>10I', data, shoff + i * shentsize) for i in range(shnum)]
    def string(table, offset):
        return table[offset:table.index(0, offset)].decode()
    strings = data[sections[shstr][4]:sections[shstr][4]+sections[shstr][5]]
    names = [string(strings, s[0]) for s in sections]
    allocated = {i for i,s in enumerate(sections) if s[2] & 2 and s[5] and names[i] not in ('.reginfo', '.MIPS.abiflags')}
    symindex = next(i for i,s in enumerate(sections) if s[1] == 2)
    symsection = sections[symindex]
    symstrings = sections[symsection[6]]
    symstrings = data[symstrings[4]:symstrings[4]+symstrings[5]]
    symbols = []
    for offset in range(symsection[4], symsection[4]+symsection[5], 16):
        name, value, size, info, other, index = struct.unpack_from('>IIIBBH', data, offset)
        symbols.append((string(symstrings, name), value, size, info, index))
    bindings = {
        'ccOriginalParse': 'CharLab.original_parse_',
        'ccGetEntries': 'CharCreator.get_slot_',
        'ccRestoreBody': 'CharLab.restore_body_',
        'ccMappedThrownKind': 'CharLab.mapped_thrown_kind_',
        'ccSpecialDonor': 'CharLab.special_donor_',
        'ccBodyKind': 'CharLab.body_kind_',
        'ccSelectJabDonor': 'CharLab.select_jab_donor_',
        'ccOriginalKirbyJabEffect': '0x8014F1BC',
        'ccSuspendJoints': 'CharLab.suspend_joints_',
        'ccResumeJoints': 'CharLab.resume_joints_',
        'ccOriginalGroundTravel': 'CharLab.original_ground_travel_',
        'ccOriginalAirTravel': 'CharLab.original_air_travel_',
        'ccOriginalGroundPhysics': 'CharLab.original_ground_physics_',
        'ccOriginalDivePositions': 'CharLabSpecials.hook_ftCommonCaptureCaptainUpdatePositions._original',
        'wpFoxBlasterMakeWeapon': 'CharCreator.neutral_make_weapon_',
        'ccNeutralMakeWeapon': 'CharCreator.neutral_weapon_factory_',
        'func_800269C0_275C0': '0x800269C0',
    }
    # Engine symbols come from the decompilation's original US function labels,
    # not addresses of the relocated Character Lab build.
    wanted = {name for name,_,_,_,index in symbols if not index and name}
    for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);', (LAB/'symbols/reloc_data_symbols.us.txt').read_text(),re.M):
        if name in wanted: bindings[name]=address
    for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);', (LAB/'symbols/symbols_us.txt').read_text(),re.M):
        if name in wanted and name not in bindings:bindings[name]=address
    for path in (LAB / 'src').rglob('*.c'):
        source = path.read_text(encoding='utf-8')
        for address, name in re.findall(r'// (0x[0-9A-Fa-f]{8})[^\n]*\n(?:[\w*]+\s+)+([\w]+)\(', source):
            if name in wanted and name not in bindings:
                bindings[name] = address
    lines = ['// Generated MIPS object with Bass relocations. Do not edit.', 'scope CharLabRuntime {']
    labels = {}
    for i,(name,value,size,info,index) in enumerate(symbols):
        if not index:
            if name:
                if name not in bindings:
                    raise ValueError('Unbound runtime engine symbol: '+name)
                lines.append(f'constant symbol_{i}({bindings[name]})')
        elif index in allocated:
            position = labels.setdefault(index, {}).setdefault(value, [])
            position.append(f'symbol_{i}')
            if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
                position.append(name)
    relocations = {}
    for s in sections:
        if s[1] != 9 or s[7] not in allocated:
            continue
        assert s[6] == symindex
        target = s[7]
        payload = data[sections[target][4]:sections[target][4]+sections[target][5]]
        entries = [struct.unpack_from('>II', data, offset) for offset in range(s[4],s[4]+s[5],8)]
        pending = {}
        for offset, info in entries:
            symbol, kind = info >> 8, info & 255
            word = struct.unpack_from('>I', payload, offset)[0]
            label = f'symbol_{symbol}'
            if kind == 2:  # R_MIPS_32
                expression = f'{label} + 0x{word:08X}'
            elif kind == 4:  # R_MIPS_26
                expression = f'0x{word & 0xFC000000:08X} | (({label} + {(word & 0x3FFFFFF) << 2}) >> 2 & 0x03FFFFFF)'
            elif kind in (5,6):  # paired R_MIPS_HI16 / LO16
                if kind == 5:
                    # ELF relocation order defines the pairs; optimized Clang
                    # output does not necessarily sort them by code offset.
                    pending.setdefault(symbol, []).append((offset,word))
                    continue
                else:
                    low = word & 65535
                    addend = low - 65536 if low & 32768 else low
                    for highoffset, highword in pending.pop(symbol, []):
                        combined = ((highword & 65535) << 16) + addend
                        relocations.setdefault(target,{})[highoffset] = f'0x{highword & 0xFFFF0000:08X} | (({label} + {combined} + 0x8000) >> 16 & 0xFFFF)'
                    # The LO relocation has the full low addend; the high part
                    # is represented only on its paired HI relocation.
                    expression = f'0x{word & 0xFFFF0000:08X} | (({label} + {addend}) & 0xFFFF)'
            else:
                raise ValueError(f'Unsupported MIPS relocation {kind}; compile without PIC/GP.')
            relocations.setdefault(target,{})[offset] = expression
        assert not pending, 'Unpaired MIPS HI16 relocation'
    for i in sorted(allocated):
        section = sections[i]
        alignment = max(4, section[8])
        lines += [f'OS.align({alignment})', f'section_{i}:']
        lines.append(f'constant section_{i}_origin(origin())')
        target = OUT / f'section-{i}.bin'
        if section[1] != 8:
            target.write_bytes(data[section[4]:section[4]+section[5]])
        relative = target.name  # Bass resolves inserts relative to runtime.asm.
        # Insert once. Thousands of tiny inserts reopen the same binary on
        # every assembler pass and become very slow on Windows/WSL filesystems.
        lines.append(f'fill {section[5]}' if section[1] == 8 else f'insert "{relative}"')
        lines.append('pushvar origin, base')
        boundaries = set(labels.get(i, {})) | set(relocations.get(i, {}))
        for offset in sorted(boundaries):
            lines += [f'origin section_{i}_origin + {offset}', f'base section_{i} + {offset}']
            lines.extend(label + ':' for label in labels.get(i, {}).get(offset, []))
            if offset in relocations.get(i, {}):
                lines.append(f'dw {relocations[i][offset]}')
        lines.append('pullvar base, origin')
    lines += ['end:', '}', 'pushvar origin, base', 'origin 0x5000000',
              'insert "animations.bin"', 'pullvar base, origin', '']
    (OUT / 'runtime.asm').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Compiled shared Character Lab runtime: {sum(sections[i][5] for i in allocated):,} bytes; {sum(len(r) for r in relocations.values())} relocations.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    main=ROOT/'main.asm'
    assembly=main.read_text(encoding='utf-8')
    late='include "build/char_creator/runtime/normal-late-hooks.asm"'
    if late not in assembly:
        marker='OS.align(16)\nmidi_memory_block:'
        assert marker in assembly, 'Cannot place final normal hooks before the heap.'
        main.write_text(assembly.replace(marker,late+'\n\n'+marker),encoding='utf-8')
    count=(ROOT/'build/char_creator/catalog_count.asm').read_text(encoding='utf-8')
    count=re.search(r'constant COUNT\((\d+)\)',count)[1]
    menu=(ROOT/'extra_imports/CharCreatorMenu.inc').read_text(encoding='utf-8')
    (ROOT/'build/char_creator/menu.inc').write_text(menu.replace('CharCreatorCatalog.COUNT - 1',str(int(count)-1)),encoding='utf-8')
    if __package__:
        from .generate_charlab_animations import generate as generate_animations
    else:
        from generate_charlab_animations import generate as generate_animations
    generate_animations()
    prepare_headers()
    special_timings()
    if __package__:
        from .generate_charlab_specials import generate
    else:
        from generate_charlab_specials import generate
    generate()
    if __package__:
        from .generate_charlab_normals import generate as generate_normals
    else:
        from generate_charlab_normals import generate as generate_normals
    generate_normals()
    if __package__:
        from .generate_charlab_neutrals import generate as generate_neutrals
    else:
        from generate_charlab_neutrals import generate as generate_neutrals
    generate_neutrals()
    command = ['clang', '-target', 'mips-unknown-none', '-march=mips2', '-mabi=32',
               '-mno-abicalls', '-fno-pic', '-G0', '-O2', '-ffreestanding', '-fno-builtin',
               '-fno-stack-protector', '-DFTCHARBUILDER_NORMAL_MECHANICS', '-DFTCHARBUILDER_NEUTRAL_EXTENDED', '-D__sgi', '-D_LANGUAGE_C', '-D_MIPS_SZLONG=32', '-DREGION_US',
               '-Ibuild/char_creator/runtime/include', '-I../ssb-decomp-re/include', '-I../ssb-decomp-re/src',
               '-c', 'extra_imports/CharLabRuntime.c', '-o', 'build/char_creator/runtime/runtime.o']
    if os.name == 'nt':
        command = ['wsl.exe', '-d', os.environ.get('SMASH_WSL_DISTRO', 'Ubuntu'), '--', *command]
    elif not shutil.which('clang'):
        raise RuntimeError('Install clang to build the shared MIPS runtime.')
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (OUT / 'compile.log').write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Runtime compiler failed:\n' + result.stderr[-5000:])
    object_to_bass(OUT / 'runtime.o')


if __name__ == '__main__':
    main()
