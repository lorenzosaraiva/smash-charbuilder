"""Port donor paired/taunt phases; stream unchanged source geometry from ROM."""
from pathlib import Path
import json
import re
import struct
if __package__:
    from .generate_charlab_specials import functions
else:
    from generate_charlab_specials import functions

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent/'ssb-decomp-re'
OUT = ROOT/'build/char_creator/runtime'
ROM_START = 0x5400000


def generate():
    bindings = (LAB/'src/ft/ftpairedmoves.generated.inc').read_text()
    geometry = (LAB/'src/ft/ftpairedgeometry.generated.inc').read_text()
    arrays = dict(re.findall(r'const (?:Vec3f|FTCustomPairAnchor|FTCustomCollisionFrame|FTCustomSpecialAttachmentFrame) (\w+)\[\] = \{(.*?)\n?\};', geometry, re.S))
    def values(name, width):
        nums = [float(v.rstrip('Ff')) for v in re.findall(r'-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?[Ff]?', arrays[name])]
        assert len(nums) % width == 0, name
        return [nums[i:i+width] for i in range(0, len(nums), width)]
    table = bindings[bindings.index('const FTCustomPairPhase sFTCustomPairPhases'):bindings.index('const FTThrownStatus')]
    bank = bytearray(); manifest = []; offsets = {}
    for line in table.splitlines()[1:-1]:
        if not line.strip().startswith('{'): continue
        phase = len(manifest)
        anchor = re.search(r'(sFTCustomPair\d+Anchors), (\w+), (sFTCustomPair\d+Clips), (\d+)', line)
        assert anchor, line
        anchors, travel_name, clips, count = anchor.groups(); count = int(count)
        collision = re.search(r'\}, \{ (\w+), 0, (\d+), (\d+), (\d+) \}', line)
        collision_name = collision[1]
        prop_names = re.findall(r'\{ (sFTCustomPair'+str(phase)+r'Prop\d+Frames),', bindings)
        positions = values(anchors, 12)
        travel = values(travel_name, 3) if travel_name != 'NULL' else [[0]*3]*count
        hits = values(collision_name, 13) if collision_name != 'NULL' else [[0]*13]*count
        props = [values(p, 10) for p in prop_names]
        assert len(positions) == len(travel) == len(hits) == count
        offset = len(bank)
        for frame in range(count):
            bank.extend(struct.pack('>15f12fI', *positions[frame], *travel[frame], *hits[frame][:12], int(hits[frame][12])))
            for prop in range(6):
                sample = props[prop][frame] if prop < len(props) else [0]*10
                bank.extend(struct.pack('>9fI', *sample[:9], int(sample[9])))
        assert len(bank)-offset == count*352
        offsets[phase] = offset
        line = line.replace(collision_name+', 0,', 'NULL, 0,', 1)
        line = line.replace(anchors+', '+travel_name+',', str(offset)+', '+('TRUE' if travel_name != 'NULL' else 'FALSE')+',')
        table = table.replace(next(l for l in table.splitlines() if l.strip().startswith('{') and clips+',' in l), line)
        manifest.append(dict(index=phase, offset=offset, count=count, props=len(props), anchor=anchors, travel=travel_name, collision=collision_name, prop_arrays=prop_names))
    assert len(manifest) == 73
    bindings = bindings[:bindings.index('const FTCustomPairPhase sFTCustomPairPhases')]+table+bindings[bindings.index('const FTThrownStatus'):]
    bindings = re.sub(r'^extern const (?:Vec3f|FTCustomPairAnchor|FTCustomCollisionFrame|FTCustomSpecialAttachmentFrame) [^\n]+\n', '', bindings, flags=re.M)
    bindings = bindings.replace('FTCustomAnimationClip', 'CCAnimationRecord')
    bindings = re.sub(r'(\{ )sFTCustomPair\d+Prop\d+Frames,', r'\1NULL,', bindings)
    scales = values('sFTCustomPairMarioTauntScales', 3)
    bindings += '\nstatic const Vec3f sFTCustomPairMarioTauntScales[] = { '+', '.join('{ '+', '.join(str(v)+'F' for v in row)+' }' for row in scales)+' };\n'
    (OUT/'paired-data.inc').write_text(bindings)
    (OUT/'paired-geometry.bin').write_bytes(bank)
    (OUT/'paired-geometry.json').write_text(json.dumps(dict(rom_start=ROM_START, frame_bytes=352, phases=manifest), indent=2)+'\n')

    # Reuse the reviewed implementation, adapting only storage, native ABI and
    # actual-body identity. Native/expanded fighters keep their own callbacks.
    source = (LAB/'src/ft/ftpairedmoves.c.inc').read_text()
    source = source.replace('#include "ftpairedmoves.generated.inc"\n#include "ftpairedgeometry.generated.inc"', '#include "paired-data.inc"')
    source = source.replace('const FTCustomPairAnchor *anchors;\n    const Vec3f *travel;', 'u32 offset;\n    sb32 has_travel;')
    source = source.replace('FTCustomAnimationClip', 'CCAnimationRecord')
    source = source.replace('fp->fkind', 'ccBodyKind(fp)').replace('owner->fkind', 'ccBodyKind(owner)')
    # Victim statuses use Remix\'s existing original-victim mapping for the
    # expanded roster; the victim always keeps its own native animation rig.
    source = source.replace('if ((victim->fkind < 0) || (victim->fkind >= 12)) return FALSE;', 'if ((u32)ccPairVictimKind(victim->fkind, kind-1) >= 12) return FALSE;')
    source = source.replace('[victim->fkind][kind - 1]', '[ccPairVictimKind(victim->fkind, kind-1)][kind - 1]')
    source = source.replace('anchor = &s->phase->anchors[frame];', 'anchor = &ccPairSample(fp, frame)->anchor;')
    source = source.replace('anchor = &s->phase->anchors[index];', 'anchor = &ccPairSample(owner, index)->anchor;')
    source = source.replace('if (s->phase->travel != NULL) travel = s->phase->travel[index];', 'if (s->phase->has_travel) travel = ccPairSample(fp, index)->travel;')
    source = source.replace('prop = &phase->props[i]; sample = &prop->frames[frame];', 'prop = &phase->props[i]; sample = &ccPairSample(fp, frame)->props[i];')
    source = source.replace('lbCommonAddMObjForFighterPartsDObj', 'ccPropMaterials')
    # Native EF update already plays each prop's joint/material animations.
    # The imported fighter-owned path's extra material tick would double the
    # beam texture clock (e.g. its original 50-frame hold becomes 25 frames).
    material_tick = '''        for (mobj = dobj->mobj; mobj != NULL; mobj = mobj->next)
        { gcParseMObjMatAnimJoint(mobj); gcPlayMObjMatAnim(mobj); }'''
    assert source.count(material_tick) == 1
    source = source.replace(material_tick, '')
    source = source.replace('ftCustomAnimationFindLiveEffect', 'ccVisualLive').replace('ftCustomAnimationStopProp', 'ccPairStopProp').replace('ftCustomAnimationMakeProp', 'ccVisualMakeProp')
    source = source.replace('if ((data->p_file_main == NULL) || (*data->p_file_main == NULL)) return fp->attr;\n    return lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);', 'if (!ccVisualMainFile(s->donor)) return fp->attr;\n    return (FTAttributes*)((uintptr_t)ccVisualMainFile(s->donor)+(uintptr_t)data->o_attributes);')
    source = source.replace('if (!data->p_file_main || !*data->p_file_main) return;\n    attr = lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);', 'if (!ccVisualMainFile(phase->donor)) return;\n    attr = (FTAttributes*)((uintptr_t)ccVisualMainFile(phase->donor)+(uintptr_t)data->o_attributes);')
    start = source.index('        fp->motion_scripts[i][0].p_script = NULL;')
    end = source.index('\n    if (phase->throws != NULL)', start)
    source = source[:start]+'''        fp->motion_scripts[i][0].p_script = fp->motion_scripts[i][1].p_script = NULL;
    }
    sCCMotionScripts[fp->player].p_script = (ftMotionCommand*)phase->move.events;
    sCCMotionScripts[fp->player].script_wait = 1.0F-begin;
    sCCMotionScripts[fp->player].script_id = 0;
    ccVisualStart(fp, begin);
'''+source[end:]
    # throw.c also defines a private numeric fallback. Engine action tables
    # retain the original callback address, so compare both identities.
    source = source.replace('fp->proc_update == ftCommonThrowProcUpdate',
        '(uintptr_t)fp->proc_update == 0x8014A0C0 || fp->proc_update == ftCommonThrowProcUpdate')
    source = source.replace('clock->trajectory = &phase->trajectory;', 'clock->trajectory = NULL;')
    source = source.replace('s->phase = phase; s->donor = phase->donor;', 'sCCPairDonors[fp->player] = phase->donor;\n    s->phase = phase; s->donor = phase->donor;')
    source = source.replace('if (phase == NULL) { s->owner = NULL; return NULL; }', 'if (phase == NULL) { s->owner = NULL; sCCPairDonors[fp->player] = -1; return NULL; }')
    source = source.replace('ftMainSetStatus(g, status,', 'ccPairSetStatus(g, status,')
    marker = 'void ftMainCharBuilderResetPairedMoves(void)'
    source = source.replace(marker, '#include "../../../extra_imports/CharLabPairStorage.c.inc"\n'+marker)
    (OUT/'paired.c.inc').write_text(source)

    common = LAB/'src/ft/ftcommon'
    files = list((LAB/'src/ft/ftchar/ftdonkey').glob('ftdonkeythrowf*.c'))+[LAB/'src/ft/ftchar/ftkirby/ftkirbythrowf.c']
    files += [common/name for name in ('ftcommoncatch1.c','ftcommoncatch2.c','ftcommoncapturepulled.c','ftcommoncapturewait.c','ftcommonthrown1.c','ftcommonappeal.c')]
    records = []; pieces = []
    for path in files:
        assert path.is_file(), path
        text = path.read_text()
        if path.name == 'ftdonkeythrowff.c':
            # A ground/air switch replays earlier source flags at the retained
            # frame. The victim may already have been released in the air.
            text = text.replace('if (fp->motion_vars.flags.flag2 != 0)',
                'if (fp->motion_vars.flags.flag2 != 0 && fp->catch_gobj != NULL)')
        # Headers/macros must precede imported functions (cargo interrupt macros).
        pieces.append(text)
        for fn in functions(text):
            fn['mode'] = 2 if path.name.startswith('ftcommoncapture') or path.name.startswith('ftcommonthrown') else 1 if path.name == 'ftcommonappeal.c' else 0
            records.append(fn)
    for fn in functions((common/'ftcommoncapture.c').read_text()):
        if fn['name'] in ('ftCommonCaptureShoulderedProcInterrupt', 'ftCommonCaptureShoulderedSetStatus'):
            fn['mode'] = 2; records.append(fn); pieces.append(fn['text'])
    damage = next(fn for fn in functions((common/'ftcommondamage.c').read_text()) if 'ftMainCharBuilderGetGrabKind' in fn['text'])
    damage['mode'] = 3; records.append(damage); pieces.append(damage['text'])
    names = {fn['name'] for fn in records}
    callbacks = '\n'.join(pieces)
    callbacks = re.sub(r'\b('+'|'.join(sorted(names, key=len, reverse=True))+r')\b',lambda m:'ccp_'+m[0],callbacks)
    callbacks = callbacks.replace('ftMainSetStatus(', 'ccPairSetStatus(')
    signatures = '\n'.join(re.sub(r'\b'+fn['name']+r'\b','ccp_'+fn['name'],fn['signature'])+';' for fn in records)
    (OUT/'paired-callbacks.inc').write_text(signatures+'\n'+callbacks)
    base = (ROOT/'smashremix/roms/ssb.rom').read_bytes(); hooks = []
    for fn in records:
        address = fn['address']; offset = address-(0x80131B00-0xAC540)
        original = struct.unpack_from('>2I',base,offset)
        branches = [i for i,w in enumerate(original) if w>>26 in (1,4,5,6,7,20,21,22,23)]
        if branches:
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
        if fn['args'].lstrip().startswith('FTStruct'): fn['mode'] |= 128
        hook = 'hook_'+fn['name']
        hooks.append(f'''scope {hook}: {{
    OS.patch_start(0x{offset:X}, 0x{address:08X})
    j {hook}
    nop
    OS.patch_end()
    OS.save_registers()
    CharLab.save_fpu()
    lw a0, 0x0090(sp)
    lli a1, {fn['mode']}
    jal CharLabRuntime.ccUsePairCallback
    nop
    beqz v0, _native
    nop
    CharLab.restore_fpu()
    OS.restore_registers()
    j CharLabRuntime.ccp_{fn['name']}
    nop
    _native:
    CharLab.restore_fpu()
    OS.restore_registers()
    _original:
{trampoline}
}}
''')
        fn.update(offset=offset, hook='CharLabPairs.'+hook)
    (OUT/'paired-hooks.asm').write_text('scope CharLabPairs {\n'+'\n'.join(hooks)+'}\n')
    (OUT/'paired-hooks.json').write_text(json.dumps([{k:fn[k] for k in ('name','address','offset','hook','mode')} for fn in records],indent=2)+'\n')
    print(f'Imported {len(records)} paired callbacks, 73 phases and {len(bank):,} source geometry ROM bytes.')


if __name__ == '__main__':
    generate()
