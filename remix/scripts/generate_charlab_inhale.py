"""Borrowed-only inhale gameplay streams and original collision geometry.

Reuse the reviewed source path sampler with a separate catalog, leaving the
original Character Lab catalog and ROM unchanged. Body poses/hats are deferred.
"""
from pathlib import Path
from types import FunctionType
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent/'ssb-decomp-re'
OUT = ROOT/'build/char_creator/runtime'


def generate():
    sys.path.insert(0,str(LAB/'tools'))
    import generateSpecialTiming as timing
    from auditNormalMoves import enum_values, us_text
    from customMoveCatalog import motion_descriptors
    from customMoveTiming import animation_duration
    from generateCustomAnimations import vec
    from customAnimation import IDENTITY
    common=enum_values((LAB/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
    header=(LAB/'src/ft/ftchar/ftkirby/ftkirby.h').read_text()
    ids=enum_values(header.replace('nFTCommonMotionSpecialStart',str(common['nFTCommonMotionSpecialStart'])),'ftKirbyMotion')
    descriptors=motion_descriptors('Kirby')[1]
    rows=[]
    for key,motion in ids.items():
        if not re.fullmatch(r'nFTKirbyMotionSpecial(?:Air)?N(?:Start|Loop|End|Eat|Throw|Wait|Turn|Copy)',key):continue
        asset=descriptors[motion][0]
        source=next((LAB/'src/relocData').glob('*_'+asset[3:-6]+'.c'))
        rows.append((8,motion,animation_duration(asset),'ftAnimLoop(' in us_text(source.read_text()),key))
    assert len(rows)==16
    # Inhale's catch hitboxes are all TopN-relative. Kirby's spit pose includes
    # optional model joints outside the normal rig; those cosmetics are not
    # sampled for this milestone. Assert that geometry has no such dependency.
    for _,motion,_,_,_ in rows:
        for op,args in timing.special_commands(descriptors[motion][1]):
            if 'MakeAttackColl' in op:assert int(args[2],0)==0,(motion,op,args)
    # Separate globals leave the cached original Up/Down B catalog unchanged.
    # Empty poses retain the donor bind transform for the invariant TopN root.
    sampler=timing.path_catalog.__wrapped__
    cases=FunctionType(sampler.__code__,dict(sampler.__globals__,catalog=lambda:tuple(rows),
        sample=lambda fighter,name,frames,flags:[{} for _ in range(frames)],
        world=lambda bones,pose:{0:(IDENTITY,(0,0,0))}))()
    out=['/* Generated original Kirby inhale geometry/events; no donor model commands. */']
    manifest=[]
    for index,c in enumerate(cases):
        p='sCCInhalePath'+str(index)
        frames=list(c['frames'])
        # These source hitboxes use TopN. Trim a constant tail rather than
        # reserving redundant per-frame geometry for every holding loop.
        while len(frames)>1 and frames[-1]==frames[-2]:frames.pop()
        if c['throws']:
            assert len(c['throws'])==1
            out+=['static FTThrowHitDesc '+p+'Throw[] = {\n'+c['throws'][0].strip()+'\n};']
        out+=['static const ftMotionCommand '+p+'Script[] = {']
        out+=['    '+line.replace('SPECIAL_THROW_DESC',p+'Throw')+',' for line in c['script']]
        out+=['};','static const FTCustomCollisionFrame '+p+'Frames[] = {']
        out+=['    { { '+', '.join(vec(v) for v in centers)+' }, '+str(mask)+' },' for mask,centers in frames]
        out+=['};']
        manifest.append(dict(motion=c['motion'],name=c['phase'],duration=c['duration'],loop=c['cycle'],
                             frames=len(frames),script=list(c['script']),geometry=frames))
    out+=['static const FTCharBuilderSpecialPath sCCInhalePaths[] = {']
    for index,c in enumerate(cases):
        p='sCCInhalePath'+str(index)
        out+=['    { 8, '+str(c['motion'])+', { '+p+'Script, ARRAY_COUNT('+p+'Script), '+str(c['duration'])+', '+('4' if c['cycle'] else '0')+' }, { '+p+'Frames, 0, ARRAY_COUNT('+p+'Frames), 0, 1 }, NULL, NULL },']
    out+=['};']
    (OUT/'inhale-paths.inc').write_text('\n'.join(out)+'\n',encoding='utf-8')
    (OUT/'inhale-paths.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Imported sixteen source inhale phases with '+str(sum(c['frames'] for c in manifest))+' collision frames; cosmetics deferred.')


if __name__=='__main__':generate()
