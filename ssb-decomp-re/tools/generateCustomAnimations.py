#!/usr/bin/env python3
"""Compile Mario donor poses; shared, bounded tables and no runtime allocations."""
import json
from customAnimation import *
from customMoveTiming import animation_duration
from generateCustomMoves import expand

TARGET_JOINTS = tuple(range(4,28))

def bind_pose(bones):
    return {j:(*b.rotate,0,*b.translate,*b.scale) for j,b in bones.items()}

def rig_map(fighter):
    return {j:j+(1 if fighter in ('Captain','Donkey') and j>=18 else 0) for j in TARGET_JOINTS}

@lru_cache(None)
def retarget_basis(fighter,flags):
    source,_=rig(fighter,flags)
    if flags==0:source=model(fighter) # Preserve the original pilot's bind bases.
    target=model('Mario')
    assert all(b.scale==(1,1,1) for b in (*source.values(),*target.values())), 'non-unit bind basis unsupported'
    source_bind=world(source,bind_pose(source));target_bind=world(target,bind_pose(target))
    return source,target,source_bind,target_bind

def retarget(fighter,pose,flags=0):
    source,target,source_bind,target_bind=retarget_basis(fighter,flags)
    # Donor squash/stretch contributes to its collision FK, but body bone
    # lengths remain fixed. Extract orientation from a unit-scale pose.
    orientations={j:(*v[:7],1,1,1) for j,v in pose.items()}
    animated=world({j:b for j,b in source.items() if j in orientations},orientations);parents={0:IDENTITY};result={}
    for j,s in rig_map(fighter).items():
        desired=mul(mul(animated[s][0],transpose(source_bind[s][0])),target_bind[j][0])
        local=mul(transpose(parents[target[j].parent]),desired)
        angles=euler(local);parents[j]=desired
        translation=target[j].translate
        if j==4:
            ratio=target[4].translate[1]/source[4].translate[1]
            delta=tuple(a-b for a,b in zip(animated[s][1],source_bind[s][1])) if flags else tuple(a-b for a,b in zip(pose[s][4:7],source[s].translate))
            translation=add(translation,tuple(v*ratio for v in delta))
        assert all(abs(v-1)<0.0001 for v in target[j].scale),('target bind scale',j)
        result[j]=(*angles,0,*translation,*target[j].scale)
        recovered=mul(parents[target[j].parent],rotation(angles))
        assert max(abs(recovered[i][k]-desired[i][k]) for i in range(3) for k in range(3))<1e-5
    return result

def collision_definitions(fighter,motion,frames):
    from customMoveCatalog import MOTIONS,resolved_moves,source_scripts
    motion,desc,duration=resolved_moves(fighter)[MOTIONS.index(motion)]
    commands=[] if desc[1]=='dCustomEmpty' else expand(desc[1],source_scripts())
    timeline={};tick=0;wall=0
    for op,args in commands:
        if op=='ftMotionCommandWait':tick+=int(args[0],0)
        elif op=='ftMotionCommandWaitAsync':tick=int(args[0],0)
        wall=max(wall,tick)
        if 'AttackColl' in op:timeline.setdefault(wall,[]).append((op,[int(a,0) for a in args]))
    active={};result=[]
    for frame in range(frames):
        tick=frame%duration if motion=='RapidLoop' else frame
        for op,a in timeline.get(tick,[]):
            if 'MakeAttackColl' in op:active[a[0]]=(a[2],tuple(a[7:10]),'Scaled' in op)
            elif op=='ftMotionCommandClearAttackCollAll':active.clear()
            elif op=='ftMotionCommandClearAttackCollID':active.pop(a[0],None)
            elif op=='ftMotionCommandSetAttackCollOffset' and a[0] in active:
                j,offset,scaled=active[a[0]];active[a[0]]=(j,tuple(a[1:]),scaled)
        result.append(dict(active))
    return result


def collision_frames(fighter,motion,poses):
    from customMoveCatalog import MOTIONS,resolved_moves
    _,desc,_=resolved_moves(fighter)[MOTIONS.index(motion)]
    flags=flag_word(desc[2]);bones,_=rig(fighter,flags)
    result=[];size=source_size(fighter)
    for pose,active in zip(poses,collision_definitions(fighter,motion,len(poses))):
        transforms=world(bones,pose);centers=[(0,0,0)]*4
        for aid,(j,offset,scaled) in active.items():
            assert j in transforms,(fighter,motion,j,flags)
            r,t=transforms[j]
            if scaled:offset=tuple(v/size for v in offset)
            centers[aid]=tuple(v*size for v in add(t,transform(r,offset)))
        result.append((sum(1<<aid for aid in active),centers))
    return result

def number(value):
    value=f32(value)
    return format(value,'.9g')+('F' if '.' in format(value,'.9g') or 'e' in format(value,'.9g') else '.0F')

def vec(values):return '{ '+', '.join(number(v) for v in values)+' }'

ANIMATION_DONORS = ('Fox','Donkey','Luigi','Captain')

@lru_cache(None)
def pose_catalog():
    from customMoveCatalog import ROSTER,resolved_moves,extra_ids
    cases=[];rows=[];seen={}
    pilots={(f,i) for f,_,_,i in PILOTS}
    for fighter in ROSTER:
        row=[]
        for index,(motion,desc,duration) in enumerate(resolved_moves(fighter)):
            supported=(fighter in ANIMATION_DONORS and
                       (index<29 or (index==29 and extra_ids(fighter)[0]>=0)))
            if not supported or (fighter,index) in pilots:
                row.append(None);continue
            key=(fighter,desc[0],desc[2],duration)
            if key not in seen:
                seen[key]=len(cases)
                cases.append(dict(fighter=fighter,motion=motion,name=desc[0][3:-6],
                                  flags=flag_word(desc[2]),frames=duration+1,
                                  symbol='sFTCustomAnimationPacked'+fighter+motion))
            row.append(seen[key])
        rows.append(tuple(row))
    return tuple(cases),tuple(rows)

def packed_pose(pose):
    rotations=tuple(round(v*4096) for j in TARGET_JOINTS for v in pose[j][:3])
    root=tuple(round(v*16) for v in pose[4][4:7])
    assert all(-32768<=v<=32767 for v in rotations+root), 'packed pose overflow'
    return rotations+root

def generate_packed():
    from customMoveCatalog import ROSTER
    cases,rows=pose_catalog()
    out=['/* Shared Mario poses. Rotations /4096 radians; root translation /16. */']
    out.append('const Vec3f sFTCustomAnimationMarioBind[24] = { '+', '.join(vec(model('Mario')[j].translate) for j in TARGET_JOINTS)+' };')
    for case in cases:
        out.append('const FTCustomAnimationPackedFrame '+case['symbol']+'[] = {')
        for source in sample(case['fighter'],case['name'],case['frames'],case['flags']):
            values=packed_pose(retarget(case['fighter'],source,case['flags']))
            rotations=', '.join('{ '+', '.join(map(str,values[j*3:j*3+3]))+' }' for j in range(24))
            out.append('    { { '+rotations+' }, { '+', '.join(map(str,values[72:]))+' } },')
        out.append('};')
    out.append('const FTCustomAnimationPackedClip sFTCustomAnimationPackedClips[12][33] = {')
    for fighter,row in zip(ROSTER,rows):
        out.append('    { /* '+fighter+' */')
        out.extend('        { '+('NULL, 0' if i is None else cases[i]['symbol']+', '+str(cases[i]['frames']))+' },' for i in row)
        out.append('    },')
    out.append('};')
    (ROOT/'src/ft/ftcustomanimationpacked.generated.inc').write_text('\n'.join(out)+'\n',encoding='utf-8')
    (ROOT/'build/animation-expanded-manifest.json').write_text(json.dumps(dict(cases=cases,rows=rows),indent=2)+'\n',encoding='utf-8')
    print('Generated',len(cases),'shared Mario clips;',sum(c['frames']*150 for c in cases),'packed bytes;',sum(i is not None for row in rows for i in row),'new donor/variant entries.')

def main():
    out=['/* Generated by tools/generateCustomAnimations.py; bounded three-move pilot. */']
    report=[]
    for fighter,motion,name,index in PILOTS:
        from auditNormalMoves import enum_values
        ids=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
        tables=arrays(us_text((ROOT/'src/ft/ftdata.c').read_text()),'FTMotionDesc')
        fields=[x.strip() for x in re.sub(r'[{}]','',tables['dFT'+fighter+'MotionDescs']).split(',') if x.strip()]
        desc=fields[ids['nFTCommonMotion'+motion]*3:ids['nFTCommonMotion'+motion]*3+3]
        assert desc[0]=='&ll'+name+'FileID' and desc[2]=='FTANIM_FLAG_NONE',(fighter,motion,'reserved animation channels unsupported',desc)
        assert re.search(r'NULL,\s*/\* translate_scales \*/',next((ROOT/'src/relocData').glob('*_'+fighter+'Main.c')).read_text()),(fighter,'translate scaling unsupported')
        duration=animation_duration('&ll'+name+'FileID');poses=sample(fighter,name,duration+1)
        collisions=collision_frames(fighter,motion,poses)
        assert collisions[-1][0]==0,(fighter,'active collision at recovery end')
        symbol='sFTCustomAnimation'+fighter
        out.append('const FTCustomAnimationFrame '+symbol+'[] = {')
        for pose,(mask,centers) in zip(poses,collisions):
            target=retarget(fighter,pose)
            out.append('    { { '+', '.join('{ '+vec(target[j][:3])+', '+vec(target[j][4:7])+' }' for j in TARGET_JOINTS)+' }, { { '+', '.join(vec(c) for c in centers)+' }, '+str(mask)+' } },')
        out.append('};')
        report.append(dict(donor=fighter,motion=motion,variant=index,frames=len(poses),bytes=len(poses)*628,rig=rig_map(fighter)))
    (ROOT/'src/ft/ftcustomanimations.generated.inc').write_text('\n'.join(out)+'\n')
    (ROOT/'build/animation-pilot-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Generated three Mario pilots:',sum(r['bytes'] for r in report),'bytes;',sum(r['frames'] for r in report),'frames; 24 mapped joints per frame.')
    generate_packed()

if __name__=='__main__':main()
