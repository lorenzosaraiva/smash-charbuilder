"""Import source prop samples, safe visual/audio commands and private FX assets."""
from pathlib import Path
import re
import sys
if __package__:
    from .generate_charlab_specials import functions
else:
    from generate_charlab_specials import functions

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent/'ssb-decomp-re'
OUT = ROOT/'build/char_creator/runtime'


def generate():
    text = (LAB/'src/ft/ftspecialanimations.generated.inc').read_text(encoding='utf-8')
    text = text[:text.index('const FTCustomAnimationClip *const sFTCustomSpecialRecoveryClips')]
    text = re.sub(r'\bFTCustomSpecialAnimation\b', 'CCVisualDefinition', text)
    # Keep the source samples verbatim. Clips are our small ROM descriptors.
    # Source audio also contains tracked voices/loops, omitted by the earlier
    # minimal decomp visual catalog. Import these on their original clocks.
    sys.path.insert(0, str(LAB/'tools'))
    from sharedAnimation import special_rows
    from specialAnimationCatalog import SAFE_EFFECTS
    from generateNeutralActions import catalog as actions
    from generateSpecialTiming import path_catalog, special_commands
    from customMoveCatalog import motion_descriptors
    from customAnimation import flag_word
    audio = {'ftMotionPlayFGM', 'ftMotionCommandPlayFGMStoreInfo',
             'ftMotionCommandPlayLoopSFXStoreInfo', 'ftMotionCommandStopLoopSFX',
             'ftMotionPlayVoice', 'ftMotionPlayInterruptableVoice'}
    rows = special_rows()
    for i, (phase, _) in enumerate(rows):
        binding = phase['binding']
        if binding is None:
            continue
        if 'sFTCharBuilderActions[' in binding:
            events = actions()[int(re.search(r'\[(\d+)\]', binding)[1])]['events']
        elif 'sFTCharBuilderSpecialPaths[' in binding:
            events = path_catalog()[int(re.search(r'\[(\d+)\]', binding)[1])]['events']
        else:
            desc = next(d for d in motion_descriptors(phase['fighter'])[1]
                        if d[0] == '&ll'+phase['name']+'FileID' and flag_word(d[2]) == phase['flags'])
            events = special_commands(desc[1]) if desc[1] != '0x80000000' else ()
        commands = []; tick = 0
        for op, args in events:
            if op == 'ftMotionCommandWait':
                tick += int(args[0], 0)
            elif op == 'ftMotionCommandWaitAsync':
                tick = max(tick, int(args[0], 0))
            elif op in audio or (op == 'ftMotionCommandEffect' and
                    args[1].removeprefix('nEFKind') in SAFE_EFFECTS):
                commands.extend(('ftMotionCommandWaitAsync('+str(tick)+')', op+'('+','.join(args)+')'))
        commands.append('ftMotionCommandEnd()')
        pattern = r'(const ftMotionCommand sFTCustomSpecialVisual'+str(i)+r'\[\] = )\{[^\n]*\};'
        text, count = re.subn(pattern, lambda m:m[1]+'{ '+', '.join(commands)+' };', text)
        assert count == 1, i
        family = 3 if any(name in binding for name in ('LaserMoves', 'ProjectileMoves', 'Actions')) else 2 if 'Lw' in phase['phase'] else 1
        pattern = r'(sFTCustomSpecialVisual'+str(i)+r', \d+, (?:NULL|&sFTCustomSpecialProp\d+)) \}'
        text, count = re.subn(pattern, lambda m:m[1]+', '+str(family)+' }', text)
        assert count == 1, ('family', i)
    (OUT/'visual-data.inc').write_text(text, encoding='utf-8')

    ef = (LAB/'src/ef/efmanager.c').read_text(encoding='utf-8')
    names = ('CaptainFalconKick', 'CaptainFalconPunch', 'KirbyCutterUp',
             'KirbyCutterDown', 'KirbyCutterDraw', 'KirbyCutterTrail')
    constructors = {fn['name']:fn for fn in functions(ef)}
    source = []
    for name in names:
        descriptor = re.search(r'EFDesc dEFManager'+name+r'EffectDesc =\s*\{.*?\n\};', ef, re.S)[0]
        source.append(descriptor.replace('dEFManager'+name+'EffectDesc', 'sCC'+name+'EffectDesc'))
        fn = constructors['efManager'+name+'MakeEffect']
        body = fn['text'].replace('efManager'+name+'MakeEffect', 'ccfx'+name)
        body = body.replace('dEFManager'+name+'EffectDesc', 'sCC'+name+'EffectDesc')
        source.append(body)
    source = '\n'.join(source)
    source = source.replace('gFTDataKirbySpecial2', 'sCCVisualFiles[0]')
    source = source.replace('gFTDataCaptainSpecial2', 'sCCVisualFiles[1]')
    source = source.replace('gFTDataCaptainSpecial3', 'sCCVisualFiles[2]')
    # These constructors always run for a foreign body. Map the hand/foot
    # through semantic roles, independent of the temporary callback identity.
    source = re.sub(r'joint = \(\(fp->fkind.*?;\n    if \(ftMainCharBuilderIsSpecialVisual\(fp\)\) joint = .*?;',
                    'joint = ftMainCharBuilderGetSpecialVisualJoint(fp, nFTKindCaptain, 16);', source)
    source = source.replace('efManagerMakeEffectForce(', 'efManagerMakeEffectNoForce(')
    (OUT/'visual-effects.inc').write_text('void *sCCVisualFiles[3];\n'+source, encoding='utf-8')
    print('Imported source-timed visual/audio scripts, prop samples and six private attached FX descriptors.')


if __name__ == '__main__':
    generate()
