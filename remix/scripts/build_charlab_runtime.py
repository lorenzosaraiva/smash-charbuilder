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
    (OUT / 'neutral.c.inc').write_text(neutral, encoding='utf-8')
    throw = (LAB / 'src/ft/ftcommon/ftcommonthrow.c').read_text(encoding='utf-8')
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
        'wpFoxBlasterMakeWeapon': 'CharCreator.neutral_make_weapon_',
        'func_800269C0_275C0': '0x800269C0',
    }
    # Engine symbols come from the decompilation's original US function labels,
    # not addresses of the relocated Character Lab build.
    wanted = {name for name,_,_,_,index in symbols if not index and name}
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
                    looffset = next(o for o,inf in entries if o > offset and inf >> 8 == symbol and inf & 255 == 6)
                    low = struct.unpack_from('>I', payload, looffset)[0] & 65535
                    low = low - 65536 if low & 32768 else low
                    addend = ((word & 65535) << 16) + low
                    expression = f'0x{word & 0xFFFF0000:08X} | (({label} + {addend} + 0x8000) >> 16 & 0xFFFF)'
                else:
                    low = word & 65535
                    addend = low - 65536 if low & 32768 else low
                    # The LO relocation has the full low addend; the high part
                    # is represented only on its paired HI relocation.
                    expression = f'0x{word & 0xFFFF0000:08X} | (({label} + {addend}) & 0xFFFF)'
            else:
                raise ValueError(f'Unsupported MIPS relocation {kind}; compile without PIC/GP.')
            relocations.setdefault(target,{})[offset] = expression
    for i in sorted(allocated):
        section = sections[i]
        alignment = max(4, section[8])
        lines += [f'OS.align({alignment})', f'section_{i}:']
        target = OUT / f'section-{i}.bin'
        if section[1] != 8:
            target.write_bytes(data[section[4]:section[4]+section[5]])
        relative = target.name  # Bass resolves inserts relative to runtime.asm.
        cursor = 0
        boundaries = set(labels.get(i, {})) | set(relocations.get(i, {})) | {section[5]}
        for offset in sorted(boundaries):
            if offset > cursor:
                lines.append(f'fill {offset-cursor}' if section[1] == 8 else f'insert "{relative}", {cursor}, {offset-cursor}')
                cursor = offset
            assert cursor == offset, 'Symbol inside a relocation word.'
            lines.extend(label + ':' for label in labels.get(i, {}).get(offset, []))
            if offset in relocations.get(i, {}):
                lines.append(f'dw {relocations[i][offset]}')
                cursor = offset + 4
    lines += ['end:', '}', '']
    (OUT / 'runtime.asm').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Compiled shared Character Lab runtime: {sum(sections[i][5] for i in allocated):,} bytes; {sum(len(r) for r in relocations.values())} relocations.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prepare_headers()
    command = ['clang', '-target', 'mips-unknown-none', '-march=mips2', '-mabi=32',
               '-mno-abicalls', '-fno-pic', '-G0', '-O2', '-ffreestanding', '-fno-builtin',
               '-fno-stack-protector', '-D__sgi', '-D_LANGUAGE_C', '-D_MIPS_SZLONG=32', '-DREGION_US',
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
