"""Import reviewed decomp special callbacks and generate borrowed-only hooks.

Native Remix fighters keep their original routines. Imported code has unique
names, the Remix two-stream ABI, and external ownership for foreign weapons.
The manifest also lets the ROM verifier check every installed hook.
"""
from pathlib import Path
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'ssb-decomp-re'
OUT = ROOT / 'build/char_creator/runtime'

FILES = {
    'ft/ftchar/ftmario/ftmariospecialhi.c': 0,
    'ft/ftchar/ftmario/ftmariospeciallw.c': 0,
    'ft/ftchar/ftsamus/ftsamusspeciallw.c': 3,
    'ft/ftchar/ftlink/ftlinkspecialhi.c': 5,
    'ft/ftchar/ftkirby/ftkirbyspecialhi.c': 8,
    'ft/ftchar/ftkirby/ftkirbyspeciallw.c': 8,
    'ft/ftchar/ftpikachu/ftpikachuspeciallw.c': 9,
    'ft/ftchar/ftyoshi/ftyoshispecialhi.c': 6,
    'ft/ftchar/ftness/ftnessspecialhi.c': 11,
}
SELECTED = {
    'ft/ftcommon/ftcommonfallspecial.c': (('ftCommonFallSpecialProcPhysics', 'ftCommonFallSpecialSetStatus'), -1),
    'ft/ftchar/ftcaptain/ftcaptainspeciallw.c': (('ftCaptainSpecialLwAirSetStatus',), 7),
    'gm/gmcollision.c': (('gmCollisionCheckWeaponAttackSpecialCollide', 'gmCollisionCheckItemAttackSpecialCollide'), -2),
    'wp/wppikachu/wppikachuthunder.c': (('wpPikachuThunderHeadSetDestroy',), 9),
    'wp/wpness/wpnesspkthunder.c': (('wpNessPKThunderHeadSetDestroyTrails', 'wpNessPKThunderTrailUpdatePositions', 'wpNessPKThunderHeadMakeTrail', 'wpNessPKThunderHeadProcUpdate', 'wpNessPKThunderHeadMakeWeapon', 'wpNessPKThunderTrailProcUpdate', 'wpNessPKThunderTrailMakeWeapon'), 11),
    'ef/efmanager.c': (('efManagerNessPKThunderTrailProcUpdate', 'efManagerNessPKThunderTrailMakeEffect', 'efManagerNessPKThunderWaveMakeEffect'), 11),
    'it/itmain.c': (('itMainSetFighterRelease',), 5),
    'ft/ftcommon/ftcommoncapturecaptain.c': (('ftCommonCaptureCaptainUpdatePositions',), 7),
    'ft/ftcommon/ftcommonitemthrow.c': (('ftCommonItemThrowProcUpdate',), 5),
}


def functions(source):
    """Read definitions with their original US addresses, not build addresses."""
    result = []
    pattern = r'// (0x[0-9A-Fa-f]{8})[^\n]*\n((?:[\w*]+\s+)+)(\w+)\(([^)]*)\)[^\n]*\n\{'
    for m in re.finditer(pattern, source):
        start = source.index('{', m.start()); end = start + 1; depth = 1
        while depth:
            depth += (source[end] == '{') - (source[end] == '}'); end += 1
        result.append(dict(address=int(m[1], 16), name=m[3], signature=m[2]+m[3]+'('+m[4]+')',
                           args=m[4], text=source[m.start():end]))
    return result


def generate():
    pieces = []; records = []
    for file, donor in FILES.items():
        source = (LAB/'src'/file).read_text(encoding='utf-8')
        found = functions(source)
        assert found, file
        for fn in found: fn.update(donor=donor, file=file)
        records.extend(found); pieces.append(source)
    for file, (wanted, donor) in SELECTED.items():
        # Correct a historical address-comment typo; the US symbol is AEA8.
        original_source = (LAB/'src'/file).read_text(encoding='utf-8').replace('0x8016AEA68', '0x8016AEA8')
        found = {fn['name']: fn for fn in functions(original_source)}
        for name in wanted:
            fn = found[name]; fn.update(donor=donor, file=file)
            records.append(fn); pieces.append(fn['text'])
    source = '\n'.join(pieces)
    # Keep Remix's expanded victim-offset table in the native helper, then
    # replace only the attacker's body socket with the original donor socket.
    dive = next(fn for fn in functions(source) if fn['name'] == 'ftCommonCaptureCaptainUpdatePositions')
    source = source.replace(dive['text'], '''// 0x8014D0F0
void ftCommonCaptureCaptainUpdatePositions(GObj *fighter_gobj, GObj *capture_gobj, Vec3f *pos)
{
    Vec3f native_socket = {0.0F, 0.0F, 0.0F}, donor_socket;
    FTStruct *fp = ftGetStruct(fighter_gobj);
    ccOriginalDivePositions(fighter_gobj, capture_gobj, pos);
    if (ftMainCharBuilderGetSpecialSpawn(fighter_gobj, &donor_socket))
    {
        gmCollisionGetFighterPartsWorldPosition(fp->joints[29], &native_socket);
        pos->x += donor_socket.x - native_socket.x;
        pos->y += donor_socket.y - native_socket.y;
        pos->z += donor_socket.z - native_socket.z;
    }
}''')
    # Identity temporarily names the donor in Remix. These getters must test
    # the actual body, so foreign pointers never enter status/passive unions.
    for helper in ('ftYoshiSpecialHiGetWeapon', 'ftPikachuSpecialLwGetWeapon', 'ftLinkSpecialHiGetWeapon'):
        start = source.index('static GObj** '+helper); end = source.index('\n}', start)+2
        text = source[start:end].replace('fp->fkind', 'ccBodyKind(fp)')
        source = source[:start]+text+source[end:]
    source = source.replace('fp->status_vars.ness.specialhi.pkthunder_gobj', '(*ccNessWeapon(fp))')
    # Reach comes from the source socket; the held egg uses donor scale rather
    # than the unrelated body's head scale. Released eggs relinquish ownership.
    source = source.replace('DObjGetStruct((*ftYoshiSpecialHiGetWeapon(fp)))->scale.vec.f = joint->scale.vec.f;',
                            'DObjGetStruct((*ftYoshiSpecialHiGetWeapon(fp)))->scale.vec.f.x =\n        DObjGetStruct((*ftYoshiSpecialHiGetWeapon(fp)))->scale.vec.f.y =\n        DObjGetStruct((*ftYoshiSpecialHiGetWeapon(fp)))->scale.vec.f.z = ftMainCharBuilderGetSpecialAttributes(fp)->size;')
    source = source.replace('gmCollisionGetFighterPartsWorldPosition(ftMainCharBuilderGetSpecialJoint(fp, FTLINK_SPINATTACK_SPAWN_JOINT), &pos);',
                            'if (!ftMainCharBuilderGetSpecialSpawn(fighter_gobj, &pos))\n                gmCollisionGetFighterPartsWorldPosition(ftMainCharBuilderGetSpecialJoint(fp, FTLINK_SPINATTACK_SPAWN_JOINT), &pos);')
    # Body-safe visuals are a separate milestone. Do not attach donor sword
    # effects to unrelated body joints or run a donor-only effect error loop.
    for name, body in {'ftKirbySpecialHiUpdateEffect': 'FTStruct *fp = ftGetStruct(fighter_gobj); fp->motion_vars.flags.flag1 = fp->motion_vars.flags.flag2 = 0;'}.items():
        fn = next(fn for fn in functions(source) if fn['name'] == name)
        replacement = '// '+hex(fn['address'])+'\n'+fn['signature']+'\n{ '+body+' }'
        source = source.replace(fn['text'], replacement)
    source = source.replace('if (efManagerLinkSpinAttackMakeEffect(fighter_gobj) != NULL)', 'if (!ftMainCharBuilderIsSpecialAdapter(fighter_gobj) && efManagerLinkSpinAttackMakeEffect(fighter_gobj) != NULL)')
    # Imported entry routines retain the engine's two animation calls. Source
    # clocks follow each call, as they do for the original donor in Remix.
    source = source.replace('if (!ftMainCharBuilderIsSpecialVisual(fp)) ftMainPlayAnimEventsAll(fighter_gobj);', 'ftMainPlayAnimEventsAll(fighter_gobj);')
    names = {fn['name'] for fn in records}
    source = re.sub(r'\b('+'|'.join(sorted(names, key=len, reverse=True))+r')\b', lambda m: 'cc_'+m[0], source)
    signatures = '\n'.join(re.sub(r'\b'+fn['name']+r'\b', 'cc_'+fn['name'], fn['signature'])+';' for fn in records)
    (OUT/'special-callbacks.inc').write_text('/* Generated from owned decomp sources. */\n'+signatures+'\n'+source, encoding='utf-8')
    hooks = []
    base_rom = (ROOT/'smashremix/roms/ssb.rom').read_bytes()
    # The old Ness pitch guard already occupies this function. Its compiled
    # counterpart also returns before pitching the body.
    for fn in records:
        # Remix's Dark Samus initializer owns the latter entry patch. Borrowed
        # Samus entry routines call our renamed initializer directly instead.
        if fn['address'] in (0x80154758, 0x8015E218): continue
        address = fn['address']
        offset = address - (0x800D6490-0x51C90) if address < 0x80131B00 else address - (0x80131B00-0xAC540)
        kind = 1 if fn['args'].lstrip().startswith('FTStruct') else 0
        if fn['donor'] == -2: kind = 2
        if fn['file'].startswith('wp/'): kind = 3
        if fn['name'] == 'wpNessPKThunderHeadMakeWeapon': kind = 0
        if fn['file'].startswith('it/'): kind = 5
        if fn['file'].startswith('ef/') and fn['name'].endswith('ProcUpdate'): kind = 4
        name = 'hook_'+fn['name']
        original = struct.unpack_from('>2I', base_rom, offset)
        branches = [i for i,w in enumerate(original) if w>>26 in (1,4,5,6,7,20,21,22,23)]
        if branches:
            # A relative branch cannot be copied to expansion RAM verbatim,
            # nor can our return jump serve as its delay-slot instruction.
            assert len(branches)==1 and original[branches[0]]>>26 in (4,5), fn['name']
            i=branches[0]; word=original[i]; displacement=word&65535
            if displacement&32768: displacement-=65536
            target=address+i*4+4+displacement*4
            trampoline=(f'    OS.copy_segment(0x{offset:X}, 4)\n' if i else '')+f'''    _branch:
    dw 0x{word&0xFFFF0000:08X} | ((_taken - _branch - 4) >> 2 & 0xFFFF)
    OS.copy_segment(0x{offset+i*4+4:X}, 4)
    j 0x{address+i*4+8:08X}
    nop
    _taken:
    j 0x{target:08X}
    nop'''
        else:
            trampoline=f'    OS.copy_segment(0x{offset:X}, 8)\n    j 0x{address+8:08X}\n    nop'
        hooks.append(f'''scope {name}: {{
    OS.patch_start(0x{offset:X}, 0x{address:08X})
    j {name}
    nop
    OS.patch_end()
    OS.save_registers()
    CharLab.save_fpu()
    lw a0, 0x0090(sp)
    lw a1, 0x0098(sp)
    addiu a2, r0, {fn['donor']}
    lli a3, {kind}
    jal CharLabRuntime.ccUseSpecialCallback
    nop
    beqz v0, _native
    nop
    CharLab.restore_fpu()
    OS.restore_registers()
    j CharLabRuntime.cc_{fn['name']}
    nop
    _native:
    CharLab.restore_fpu()
    OS.restore_registers()
    _original:
{trampoline}
}}
''')
        fn.update(offset=offset, hook='CharLabSpecials.'+name)
    (OUT/'special-hooks.asm').write_text('// Generated borrowed-only callbacks.\nscope CharLabSpecials {\n'+'\n'.join(hooks)+'}\n', encoding='utf-8')
    (OUT/'special-hooks.json').write_text(json.dumps([{k: fn[k] for k in ('name','address','offset','donor','hook')} for fn in records if 'hook' in fn], indent=2)+'\n', encoding='utf-8')
    print(f'Imported {len(records)} special callbacks; {len(hooks)} borrowed-only hooks.')
