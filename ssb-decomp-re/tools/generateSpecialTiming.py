#!/usr/bin/env python3
"""Source phase durations for borrowed Up/Down B; no body animation timings."""
from functools import lru_cache
import re
from auditNormalMoves import ROOT, ROSTER, enum_values, us_text
from customMoveCatalog import motion_descriptors
from customMoveTiming import animation_duration
from customAnimation import sample, rig, world, source_size, flag_word, transform, add
from generateCustomAnimations import vec, number
from generateNeutralProjectiles import commands
from math import ceil

GAMEPLAY_OPS=('ftMotionCommandSetHitStatusAll','ftMotionCommandSetSlopeContour','ftMotionCommandSetAirJumpMax')

def superjump_landing_duration():
    rate=float(re.search(r'#define FTMARIO_SUPERJUMP_LANDING_LAG\s+([\d.]+)F',
                        (ROOT/'src/ft/ftchar/ftmario/ftmario.h').read_text())[1])
    common=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
    durations=[ceil(animation_duration(motion_descriptors(f)[1][common['nFTCommonMotionLandingFallSpecial']][0])/rate)
               for f in ('Mario','Luigi')]
    assert durations[0]==durations[1]
    return durations[0]

@lru_cache(None)
def catalog():
    common=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
    result=[]
    for donor,fighter in enumerate(ROSTER):
        header=ROOT/'src/ft/ftchar'/('ft'+fighter.lower())/('ft'+fighter.lower()+'.h')
        ids=enum_values(header.read_text().replace('nFTCommonMotionSpecialStart',str(common['nFTCommonMotionSpecialStart'])),'ft'+fighter+'Motion')
        _,descs=motion_descriptors(fighter)
        for key,motion in ids.items():
            if 'MotionSpecial' not in key or not any(x in key for x in ('Hi','Lw')):continue
            desc=descs[motion]
            if not desc[0].startswith('&ll'):continue
            duration=animation_duration(desc[0])
            animation=next((ROOT/'src/relocData').glob('*_'+desc[0][3:-6]+'.c'))
            cycle='ftAnimLoop(' in us_text(animation.read_text())
            if fighter=='Ness' and key.endswith('HiJibaku'):
                # The 9-frame pose loops during a 28-tick native launch action.
                duration=int(re.search(r'#define FTNESS_PKJIBAKU_ANIM_LENGTH\s+(\d+)',header.read_text())[1])
                cycle=False
            result.append((donor,motion,duration,cycle,key))
    return tuple(result)

@lru_cache(None)
def donkey_frames():
    row=next(row for row in catalog() if row[-1]=='nFTDonkeyMotionSpecialLwLoop')
    _,descs=motion_descriptors('Donkey');desc=descs[row[1]]
    poses=sample('Donkey',desc[0][3:-6],row[2]+1,flag_word(desc[2]))
    bones,_=rig('Donkey',flag_word(desc[2]));size=source_size('Donkey')
    events={};tick=0
    for op,args in commands(desc[1]):
        if op in ('ftMotionCommandWait','ftMotionCommandWaitAsync'):
            tick=int(args[0],0) if op.endswith('Async') else tick+int(args[0],0)
        elif 'AttackColl' in op:events.setdefault(tick,[]).append((op,[int(a,0) for a in args]))
    active={};frames=[]
    for frame,pose in enumerate(poses):
        for op,a in events.get(frame,()):
            if 'MakeAttackColl' in op:active[a[0]]=(a[2],tuple(a[7:10]))
            elif op=='ftMotionCommandClearAttackCollAll':active.clear()
        matrices=world(bones,pose);centers=[(0,0,0)]*4
        for aid,(joint,offset) in active.items():
            r,t=matrices[joint];centers[aid]=tuple(v*size for v in add(t,transform(r,offset)))
        frames.append((sum(1<<aid for aid in active),tuple(centers)))
    assert [i for i,(mask,_) in enumerate(frames) if mask]==[16,17,26,27]
    return tuple(frames)

def donkey_case():
    row=next(row for row in catalog() if row[-1]=='nFTDonkeyMotionSpecialLwLoop')
    _,descs=motion_descriptors('Donkey');desc=descs[row[1]]
    return dict(fighter='Donkey',phase='HandSlap',air=0,duration=row[2],
                animation=desc[0][3:-6],flags=flag_word(desc[2]),events=commands(desc[1]),
                frames=donkey_frames(),spawn=(),anchors=(),travel=())

@lru_cache(None)
def path_catalog():
    result=[]
    for donor,motion,duration,cycle,key in catalog():
        selected=((donor==2 and ('SpecialHi' in key or 'SpecialAirHi' in key)) or
                  (donor in (0,4) and ('SpecialHi' in key or 'SpecialAirHi' in key)) or
                  (donor in (0,4,7) and ('SpecialLw' in key or 'SpecialAirLw' in key)) or
                  (donor==11 and ('SpecialHi' in key or 'SpecialAirHi' in key)))
        if not selected:continue
        fighter=ROSTER[donor];desc=motion_descriptors(fighter)[1][motion];flags=flag_word(desc[2])
        name=desc[0][3:-6];poses=sample(fighter,name,duration+1,flags)
        bones,_=rig(fighter,flags);size=source_size(fighter)
        source=commands(desc[1]);timeline={};script=[];wall=0
        for op,args in source:
            if op=='ftMotionCommandWait':wall+=int(args[0],0)
            elif op=='ftMotionCommandWaitAsync':wall=max(wall,int(args[0],0))
            elif 'AttackColl' in op or op.startswith('ftMotionCommandSetFlag') or op in GAMEPLAY_OPS:
                a=[int(v,0) for v in args];timeline.setdefault(wall,[]).append((op,a))
                a=list(a)
                if 'MakeAttackColl' in op:a[2]=0
                script+=['ftMotionCommandWaitAsync('+str(wall)+')',op+'('+','.join(map(str,a))+')']
        script.append('ftMotionCommandEnd()')
        active={};frames=[];travel=[];spawn=[]
        for frame,pose in enumerate(poses):
            for op,a in timeline.get(frame,()):
                if 'MakeAttackColl' in op:active[a[0]]=(a[2],tuple(a[7:10]),'Scaled' in op)
                elif op=='ftMotionCommandClearAttackCollAll':active.clear()
                elif op=='ftMotionCommandClearAttackCollID':active.pop(a[0],None)
                elif op=='ftMotionCommandSetAttackCollOffset' and a[0] in active:
                    j,_,scaled=active[a[0]];active[a[0]]=(j,tuple(a[1:]),scaled)
            matrices=world(bones,pose);centers=[(0,0,0)]*4
            for aid,(joint,offset,scaled) in active.items():
                r,t=matrices[joint]
                if scaled:offset=tuple(v/size for v in offset)
                centers[aid]=tuple(v*size for v in add(t,transform(r,offset)))
            frames.append((sum(1<<aid for aid in active),tuple(centers)))
            prev=poses[max(frame-1,0)].get(1,(0,)*10);cur=pose.get(1,(0,)*10)
            travel.append((((cur[6]-prev[6])*size,(cur[5]-prev[5])*size,-(cur[4]-prev[4])*size),cur[2]))
            if donor==11 and key.endswith('HiHold'):
                point=matrices[12][1];spawn.append((point[2]*size,point[1]*size,-point[0]*size))
        assert not frames[-1][0],(key,'active collision at action end')
        result.append(dict(donor=donor,motion=motion,fighter=fighter,phase=key,duration=duration,
                           flags=flags,animation=name,events=source,script=tuple(script),frames=tuple(frames),
                           cycle=cycle,travel=tuple(travel) if donor==7 or (donor in (0,4) and 'Hi' in key) else (),spawn=tuple(spawn),anchors=(),air=int('SpecialAir' in key)))
    return tuple(result)

def render():
    out=['/* Generated by tools/generateSpecialTiming.py. */',
         '/* Cycle is the donor animation loop, independent of the visible body. */',
         'static const FTCharBuilderSpecialTiming sFTCharBuilderSpecialTimings[] = {']
    out += ['    { '+str(donor)+', '+str(motion)+', { NULL, 0, '+str(duration)+', '+('4' if cycle else '0')+' } }, /* '+key+' */' for donor,motion,duration,cycle,key in catalog()]
    out+=['};','static const FTCustomCollisionFrame sFTCharBuilderDonkeyLwFrames[] = {']
    out+=['    { { '+', '.join(vec(v) for v in centers)+' }, '+str(mask)+' },' for mask,centers in donkey_frames()]
    out+=['};']
    for i,c in enumerate(path_catalog()):
        prefix='sFTCharBuilderSpecialPath'+str(i)
        out+=['static const ftMotionCommand '+prefix+'Script[] = {']
        out+=['    '+line+',' for line in c['script']];out+=['};']
        out+=['static const FTCustomCollisionFrame '+prefix+'Frames[] = {']
        out+=['    { { '+', '.join(vec(v) for v in centers)+' }, '+str(mask)+' },' for mask,centers in c['frames']];out+=['};']
        if c['travel']:
            out+=['static const FTCharBuilderSpecialTravel '+prefix+'Travel[] = {']
            out+=['    { '+vec(delta)+', '+number(angle)+' },' for delta,angle in c['travel']];out+=['};']
        if c['spawn']:
            out+=['static const Vec3f '+prefix+'Spawn[] = {']
            out+=['    '+vec(v)+',' for v in c['spawn']];out+=['};']
    out+=['static const FTCharBuilderSpecialPath sFTCharBuilderSpecialPaths[] = {']
    for i,c in enumerate(path_catalog()):
        p='sFTCharBuilderSpecialPath'+str(i)
        out+=['    { '+str(c['donor'])+', '+str(c['motion'])+', { '+p+'Script, ARRAY_COUNT('+p+'Script), '+str(c['duration'])+', '+('4' if c['cycle'] else '0')+' }, { '+p+'Frames, 0, '+str(c['duration']+1)+', 0, 0 }, '+(p+'Travel' if c['travel'] else 'NULL')+', '+(p+'Spawn' if c['spawn'] else 'NULL')+' },']
    out+=['};']
    out+=['static const FTCustomMoveDefinition sFTCharBuilderSuperJumpLanding = { NULL, 0, '+str(superjump_landing_duration())+', 0 };']
    return '\n'.join(out)+'\n'

if __name__=='__main__':
    (ROOT/'src/ft/ftspecialtiming.generated.inc').write_text(render(),encoding='utf-8')
    print('Generated',len(catalog()),'donor phase durations,',len(path_catalog()),'collision/travel/socket phases and DK slap windows.')
