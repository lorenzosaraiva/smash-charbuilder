"""Import original-roster normal callbacks with native/expanded fallbacks.

Gameplay callbacks and flags follow the donor; body identity, parts and
hurtboxes remain native. Scalar attributes are extracted from owned US sources
so normal physics never loads a donor model file during an active match.
"""
from pathlib import Path
import json
import re
import struct
import sys
from generate_charlab_specials import functions

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT.parent/'ssb-decomp-re'
OUT=ROOT/'build/char_creator/runtime'
FILES=('ftcommonattack1','ftcommonattack100','ftcommonattacks3','ftcommonattackhi3',
       'ftcommonattacks4','ftcommonattackair','ftcommonlandingair')
PHYSICS=('ftPhysicsApplyGroundVelFriction','ftPhysicsApplyAirVelDrift',
         'ftPhysicsApplyAirVelDriftFastFall','ftPhysicsApplyAirVelFriction','ftPhysicsClampAirVelXMax')
FIELDS=('size','traction','gravity','tvel_base','tvel_fast','air_speed_max_x',
        'air_accel','air_friction','attack1_followup_frames','is_have_attack11','is_have_attack12')


def generate():
    sys.path.insert(0,str(LAB/'tools'))
    from auditNormalMoves import ROSTER
    from customMoveCatalog import motion_descriptors
    rows=[];motion_rows=[];manifest=[]
    for fighter in ROSTER:
        # Keep US regions and comments for scalar field names.
        raw=next((LAB/'src/relocData').glob('*_'+fighter+'Main.c')).read_text(encoding='utf-8')
        active=True;stack=[];selected=[]
        for line in raw.splitlines():
            if line.lstrip().startswith('#if'):
                cond='REGION_US' in line
                if '!defined' in line:cond=not cond
                stack.append((active,cond));active=active and cond
            elif line.lstrip().startswith('#else'):
                parent,cond=stack[-1];active=parent and not cond
            elif line.lstrip().startswith('#endif'):active=stack.pop()[0]
            elif active:selected.append(line)
        raw='\n'.join(selected)
        raw=raw[re.search(r'FTAttributes\s+\w+\s*=\s*\{',raw).end():]
        values={field:re.search(r'([-+0-9.eEfF]+),\s*/\* '+field+r' \*/',raw)[1] for field in FIELDS}
        rows.append('    { '+', '.join('.'+key+' = '+value for key,value in values.items())+' },')
        _,descs=motion_descriptors(fighter)
        motion_rows.append('    { '+', '.join('0' if row[0] in ('0','NULL') else '1' for row in descs)+' },')
        manifest.append(dict(fighter=fighter,attributes=values))
    ness=next((LAB/'src/relocData').glob('*_NessMainMotion.c')).read_text(encoding='utf-8')
    bat=re.search(r'FTSpecialColl \w+AttackS4ReflectorFTSpecialColl = (\{.*?\});',ness,re.S)[1]
    data='/* Scalar US attributes only; never replace native hurtbox/model data. */\nstatic FTAttributes sCCNormalAttributes[12] = {\n'+'\n'.join(rows)+'\n};\n'
    data+='static const u8 sCCNormalMotionAvailable[12][276] = {\n'+'\n'.join(motion_rows)+'\n};\n'
    data+='static FTSpecialColl sCCNessBat = '+bat+';\n'
    (OUT/'normal-data.inc').write_text(data,encoding='utf-8')
    (OUT/'normal-data.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    records=[];pieces=[]
    for name in FILES:
        source=(LAB/'src/ft/ftcommon'/ (name+'.c')).read_text(encoding='utf-8')
        found=functions(source)
        for fn in found:fn['file']=name
        records.extend(found);pieces.append(source)
    source=(LAB/'src/ft/ftphysics.c').read_text(encoding='utf-8')
    found={fn['name']:fn for fn in functions(source)}
    for name in PHYSICS:
        fn=found[name];fn['file']='physics';records.append(fn);pieces.append(fn['text'])
    source='\n'.join(pieces).replace('#include <sc/scene.h>','')
    # Captain's rapid eligibility compares Jab3; it does not request a status.
    # Remix uses native unique IDs, so this query must not arm donor ownership.
    query='status_id = ftMainCharBuilderGetJabStatus(fp, nFTCaptainStatusAttack13, 0);'
    assert source.count(query)==1
    source=source.replace(query,'status_id = nFTCaptainStatusAttack13;')
    # Kirby's attached Vulcan effects belong to the later safe-props milestone.
    fn=next(fn for fn in functions(source) if fn['name']=='ftCommonAttack100LoopKirbyUpdateEffect')
    source=source.replace(fn['text'],'// '+hex(fn['address'])+'\n'+fn['signature']+'\n{ if (ccBodyKind(fp)==nFTKindKirby && ftMainCharBuilderGetNormalKind(fp,nSCCharBuilderAttackJab)==nFTKindKirby) ccOriginalKirbyJabEffect(fp); }')
    source=source.replace('(FTSpecialColl*) ((uintptr_t)gFTNessFileMainMotion + (intptr_t)&llNessMainMotionAttackS4ReflectorFTSpecialColl)','&sCCNessBat')
    # These are native donor statuses, selected through the retained normal
    # action-array hook. No unregistered 0xF00 status enters Remix's engine.
    names={fn['name'] for fn in records}
    source=re.sub(r'\b('+'|'.join(sorted(names,key=len,reverse=True))+r')\b',lambda m:'ccn_'+m[0],source)
    signatures='\n'.join(re.sub(r'\b'+fn['name']+r'\b','ccn_'+fn['name'],fn['signature'])+';' for fn in records)
    (OUT/'normal-callbacks.inc').write_text('/* Generated from reviewed decomp normal sources. */\n'+signatures+'\n'+source,encoding='utf-8')
    hooks=[];late=[];base=(ROOT/'smashremix/roms/ssb.rom').read_bytes()
    for fn in records:
        if fn['name']=='ftCommonAttack100LoopKirbyUpdateEffect':continue
        address=fn['address'];offset=address-(0x800D6490-0x51C90) if address<0x80131B00 else address-(0x80131B00-0xAC540)
        kind=int(fn['args'].lstrip().startswith('FTStruct'))
        name='hook_'+fn['name'];words=struct.unpack_from('>2I',base,offset)
        assert all(w>>26 not in (1,4,5,6,7,20,21,22,23) for w in words),fn['name']
        delegate={'ftCommonAttack12SetStatus':'Mewtwo.rapid_jab_patch_',
                  'ftCommonAttack100StartSetStatus':'Slippy.unique_jab_loop_'}.get(fn['name'])
        patch=f'    OS.patch_start(0x{offset:X}, 0x{address:08X})\n    j CharLabNormals.{name}\n    nop\n    OS.patch_end()'
        if delegate:late.append(patch);patch=''
        trampoline=f'    j {delegate}\n    nop' if delegate else f'    OS.copy_segment(0x{offset:X}, 8)\n    j 0x{address+8:08X}\n    nop'
        hooks.append(f'''scope {name}: {{
{patch}
    OS.save_registers()
    CharLab.save_fpu()
    lw a0, 0x0090(sp)
    lli a1, {kind}
    jal CharLabRuntime.ccUseNormalCallback
    nop
    beqz v0, _native
    nop
    CharLab.restore_fpu()
    OS.restore_registers()
    j CharLabRuntime.ccn_{fn['name']}
    nop
    _native:
    CharLab.restore_fpu()
    OS.restore_registers()
{trampoline}
}}
''')
        fn.update(offset=offset,hook='CharLabNormals.'+name)
    # Remix's original fastfall dispatcher enters physics at function+4 after
    # allocating the native stack frame. Entry guards replace that instruction
    # too, so retain the toggle while entering the complete guarded function.
    hooks.append('''scope aerial_fastfall_: {
    Toggles.read(entry_fast_fall_aerials, at)
    beqz at, _normal
    nop
    j 0x800D9160
    nop
    _normal:
    j 0x800D90E0
    nop
}
''')
    for offset in (0xA5638,0xA564C,0xA5660,0xA5674,0xA5688):
        late.append(f'    OS.patch_start(0x{offset:X}, 0x{offset+0x80084800:08X})\n    dw CharLabNormals.aerial_fastfall_\n    OS.patch_end()')
    (OUT/'normal-hooks.asm').write_text('// Original recipe callbacks; native/expanded fallback preserved.\nscope CharLabNormals {\n'+'\n'.join(hooks)+'}\n',encoding='utf-8')
    (OUT/'normal-late-hooks.asm').write_text('// Apply after Remix character entry patches; delegates preserve their native routes.\n'+'\n'.join(late)+'\n',encoding='utf-8')
    (OUT/'normal-hooks.json').write_text(json.dumps([{k:fn[k] for k in ('name','address','offset','hook')} for fn in records if 'hook' in fn],indent=2)+'\n',encoding='utf-8')
    print(f'Imported {len(records)} normal callbacks; {len(records)-1} guarded entry hooks and aerial-fastfall dispatcher; twelve US scalar attribute records.')
