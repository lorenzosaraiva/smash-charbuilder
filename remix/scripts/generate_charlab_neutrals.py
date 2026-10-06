"""Build private US neutral weapons and the shared, body-safe neutral adapters.

Resource pointers and callbacks belong to Character Lab; the native Remix
descriptors (including expanded characters) are never patched.
"""
from pathlib import Path
import re
if __package__:
    from .generate_charlab_specials import functions
else:
    from generate_charlab_specials import functions

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'ssb-decomp-re'
OUT = ROOT / 'build/char_creator/runtime'
FILES = (
    'wp/wpmario/wpmariofireball.c', 'wp/wppikachu/wppikachuthunderjolt.c',
    'wp/wpness/wpnesspkfire.c', 'it/itfighter/itnesspkfire.c',
    'wp/wpsamus/wpsamuschargeshot.c', 'wp/wplink/wplinkboomerang.c',
)


def generate():
    pieces = [(LAB/'src'/path).read_text(encoding='utf-8') for path in FILES]
    capture = (LAB/'src/ft/ftcommon/ftcommoncaptureyoshi.c').read_text(encoding='utf-8')
    pieces.append(next(fn['text'] for fn in functions(capture)
                       if fn['name'] == 'ftCommonCaptureYoshiProcCaptureWithPhysics'))
    source = '\n'.join(pieces)
    fns = functions(source)
    for fn in fns:
        if fn['name'] == 'ftCommonCaptureYoshiProcCaptureWithPhysics':
            fn['signature'] = 'void ftCommonCaptureYoshiProcCaptureWithPhysics(GObj*, GObj*, void (*)(GObj*))'
    names = {fn['name'] for fn in fns}
    names.update(re.findall(r'^\w+ (d\w+)\s*(?:\[[^\]]*\])?\s*=\s*', source, re.M))
    rename = lambda text: re.sub(r'\b('+'|'.join(sorted(names, key=len, reverse=True))+r')\b',
                                 lambda m: 'ccwp_'+m[0], text)
    declarations = '\n'.join(rename(fn['signature'])+';' for fn in fns)
    source = rename(source)
    source = source.replace('wpManagerMakeWeapon(', 'ccNeutralMakeWeapon(')
    resources = ['gFTMarioFileSpecial1', 'gFTDataLuigiSpecial1', 'gFTDataPikachuSpecial1',
                 'gFTNessFileSpecial1', 'gFTDataSamusSpecial1', 'gFTDataLinkSpecial1']
    for index, name in enumerate(resources):
        source = source.replace(name, f'sCCNeutralFiles[{index}]')
    source = source.replace('gFTMarioFileMain', 'sCCNeutralFiles[0]')
    source = source.replace('gFTDataPikachuSpecial3', 'sCCNeutralFiles[7]')
    source = source.replace('gFTNessParticleBankID', 'sCCNeutralParticleBanks[1]')
    fn = next(fn for fn in functions(source) if fn['name']=='ccwp_wpLinkBoomerangProcUpdate')
    guarded = fn['text'].replace('    WPStruct *wp = wpGetStruct(weapon_gobj);',
        '    WPStruct *wp = wpGetStruct(weapon_gobj);\n'
        '    if (wp->weapon_vars.boomerang.parent_gobj != NULL &&\n'
        '        !ccNeutralBoomerangOwner(wp->weapon_vars.boomerang.parent_gobj, weapon_gobj))\n'
        '    { wp->weapon_vars.boomerang.parent_gobj = NULL; return TRUE; }')
    source = source.replace(fn['text'],guarded)
    # Private boomerangs must never fall through to another body's passive union.
    source = re.sub(r'if \(ftMainCharBuilderBoomerangClear\(fp, weapon_gobj\)\) \{\}.*?wp->weapon_vars.boomerang.parent_gobj = NULL;',
                    'ftMainCharBuilderBoomerangClear(fp, weapon_gobj);\n        wp->weapon_vars.boomerang.parent_gobj = NULL;', source, flags=re.S)
    # The helper already recognizes our sidecar. Native Link/Kirby branches
    # are unreachable for valid ownership, and are removed for recycled owners.
    source = re.sub(r'if \(ftMainCharBuilderBoomerangCatch\(wp->weapon_vars.boomerang.parent_gobj, weapon_gobj\)\) \{\}.*?\n            }',
                    'ftMainCharBuilderBoomerangCatch(wp->weapon_vars.boomerang.parent_gobj, weapon_gobj);\n            }', source, flags=re.S)
    (OUT/'neutral-weapons.inc').write_text(
        '#include <it/item.h>\n#include <wp/weapon.h>\n#include <reloc_data.h>\n'
        'extern GObj *ccNeutralMakeWeapon(GObj*, WPDesc*, Vec3f*, u32);\n'
        'static sb32 ccNeutralBoomerangOwner(GObj*, GObj*);\n'
        'extern void ftCommonEscapeSetStatus(GObj*, s32, f32);\n'
        'void *sCCNeutralFiles[8];\ns32 sCCNeutralParticleBanks[2] = {-1,-1};\n'+declarations+'\n'+source, encoding='utf-8')

    for file in ('ftcharbuilderprojectiles.c.inc', 'ftcharbuilderneutralactions.c.inc'):
        text = (LAB/'src/ft'/file).read_text(encoding='utf-8')
        text = rename(text)
        text = text.replace('fp->motion_scripts[i][2]', 'sCCMotionScripts[fp->player]')
        text = text.replace('    FTStruct *owner;', '    FTStruct *owner;\n    u32 generation;')
        # State cannot survive player-struct recycling on stocks/rematches.
        if 'neutralactions' in file:
            text = text.replace('fp->fkind', 'ccBodyKind(fp)')
            text = text.replace('s->owner = fp; s->body', 's->owner = fp; s->generation = fp->player_num; s->body')
            text = text.replace('(s->owner != fp)', '(s->owner != fp || s->generation != fp->player_num)')
            text = text.replace('s->owner != fp || s->body', 's->owner != fp || s->generation != fp->player_num || s->body')
            text = text.replace('s->owner == fp && s->boomerang', 's->owner == fp && s->generation == fp->player_num && s->boomerang')
            text = text.replace('if (fp->is_special_interrupt && ftCustomMoveGetSlot(fp) != NULL) ftMainCharBuilderStartAction(g, 22, 0);',
                'if (fp->is_special_interrupt && ftCustomMoveGetSlot(fp) != NULL)\n'
                '    { ftMainCharBuilderClearSpecialDonor(fp); ftMainCharBuilderStartAction(g, 22, 0); }')
        else:
            state = 'sFTCharBuilderProjectileStates[fp->player]'
            text = text.replace(state+'.owner = fp;', state+'.owner = fp; '+state+'.generation = fp->player_num;')
            text = text.replace(state+'.owner != fp', state+'.owner != fp || '+state+'.generation != fp->player_num')
            text = text.replace('"ftneutralprojectiles.generated.inc"', '"ft/ftneutralprojectiles.generated.inc"')
        (OUT/file).write_text(text, encoding='utf-8')

    # Versioned overrides of generated upstream Toggles; no SRAM revision bump.
    path = ROOT/'src/Toggles.asm'
    source = path.read_text(encoding='utf-8')
    for scope, helper, anchor in (
        ('save_', 'export_neutral_choices_', '        li      t0, 0'),
        ('load_', 'import_neutral_choices_', '        _end:'),
    ):
        start = source.index('    scope '+scope+': {')
        end = source.index('\n    }', start)
        block = source[start:end]
        call = '        jal     CharCreator.'+helper+'\n        nop\n'
        if call not in block:
            index = block.index(anchor)
            if scope == 'load_': index = block.index('\n', index)+1
            block = block[:index]+call+block[index:]
            source = source[:start]+block+source[end:]
    start=source.index('    scope save_: {'); end=source.index('\n    }',start)
    block=source[start:end]
    call='        jal     CharCreator.import_neutral_choices_\n        nop\n'
    if call not in block:
        index=block.index('\n',block.index('        _end:'))+1
        block=block[:index]+call+block[index:]
        source=source[:start]+block+source[end:]
    path.write_text(source, encoding='utf-8')
