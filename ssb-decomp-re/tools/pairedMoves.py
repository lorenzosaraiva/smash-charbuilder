"""Original grab/throw phases, donor capture sockets and victim status pairs."""
from functools import lru_cache
import re
from customMoveCatalog import ROOT, ROSTER, motion_descriptors, source_scripts
from auditNormalMoves import enum_values, arrays, us_text
from customMoveTiming import animation_duration
from customAnimation import sample, rig, world, flag_word, source_size, transform, add, animation
from generateSpecialTiming import special_commands
from specialAnimationCatalog import visual_script, SAFE_EFFECTS

@lru_cache(None)
def catalog():
    common_motion=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
    common_status=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonStatus')
    result=[];taunts=[]
    for donor,fighter in enumerate(ROSTER):
        _,descs=motion_descriptors(fighter)
        phases=[(p,common_status['nFTCommonStatus'+p],common_motion['nFTCommonMotion'+p]) for p in ('Catch','CatchPull','ThrowF','ThrowB')]
        if fighter in ('Donkey','Kirby'):
            header=(ROOT/'src/ft/ftchar'/('ft'+fighter.lower())/('ft'+fighter.lower()+'.h')).read_text()
            statuses=enum_values(header.replace('nFTCommonStatusSpecialStart',str(common_status['nFTCommonStatusSpecialStart'])),'ft'+fighter+'Status')
            motions=enum_values(header.replace('nFTCommonMotionSpecialStart',str(common_motion['nFTCommonMotionSpecialStart'])),'ft'+fighter+'Motion')
            extra=('ThrowFWait','ThrowFWalkSlow','ThrowFWalkMiddle','ThrowFWalkFast','ThrowFTurn','ThrowFKneeBend','ThrowFFall','ThrowFLanding','ThrowFDamage','ThrowFF','ThrowAirFF') if fighter=='Donkey' else ('ThrowF','ThrowFFall','ThrowFLanding')
            if fighter=='Kirby': phases=[v for v in phases if v[0]!='ThrowF']
            phases.extend((p,statuses['nFT'+fighter+'Status'+p],motions['nFT'+fighter+'Motion'+p]) for p in extra)
        phases.append(('Appeal',common_status['nFTCommonStatusAppeal'],common_motion['nFTCommonMotionAppeal']))
        for phase,status,motion in phases:
            desc=descs[motion]
            duration=animation_duration(desc[0]);flags=flag_word(desc[2]);name=desc[0][3:-6]
            assert not flags&0x80000000, 'New ground TransN phase needs paired physics support'
            loop='ftAnimLoop(' in us_text(animation(name)[0].read_text())
            events=special_commands(desc[1]);tick=0;timeline={};script=[]
            for op,args in events:
                if op=='ftMotionCommandWaitAsync':tick=int(args[0],0);continue
                if 'AttackColl' in op or op.startswith('ftMotionCommandSetFlag') or op in ('ftMotionCommandSetHitStatusAll','ftMotionCommandSetSlopeContour'):
                    nums=[int(a,0) for a in args];timeline.setdefault(tick,[]).append((op,nums))
                    if 'MakeAttackColl' in op: nums=list(nums);nums[2]=0
                    script.extend(('ftMotionCommandWaitAsync('+str(tick)+')',op+'('+','.join(map(str,nums))+')'))
            script.append('ftMotionCommandEnd()')
            frames=duration+1
            target=taunts if phase=='Appeal' else result
            visual=visual_script(events)
            if phase=='Appeal':
                # Voice and rumble events have no foreign model/texture pointers.
                # Keep commands ordered; each visual stream starts at tick zero.
                voice=[];tick=0
                for op,args in events:
                    if op=='ftMotionCommandWaitAsync':tick=int(args[0],0)
                    elif op in ('ftMotionPlayVoice','ftMotionCommandMakeRumble','ftMotionPlayFGM') or op=='ftMotionCommandEffect' and args[1].removeprefix('nEFKind') in SAFE_EFFECTS:
                        voice.extend(('ftMotionCommandWaitAsync('+str(tick)+')',op+'('+','.join(args)+')'))
                visual=tuple(voice)+('ftMotionCommandEnd()',)
            target.append(dict(fighter=fighter,donor=donor,phase=phase,status=status,motion=motion,desc=desc,name=name,flags=flags,duration=duration,
                frames=frames,loop_start=0,loop_period=duration if loop else 0,
                events=events,timeline=timeline,script=tuple(script),visual=visual))
    return tuple(result+taunts)

@lru_cache(None)
def phase_data(index):
    c=catalog()[index];f=c['fighter'];bones,_=rig(f,c['flags']);size=source_size(f)
    text=next((ROOT/'src/relocData').glob('*_'+f+'Main.c')).read_text()
    anchor=int(re.search(r'(\d+),\s*/\* joint_itemheavy_id',text)[1])
    if c['phase']=='Appeal':anchor=4  # Taunts have no captured victim/socket.
    poses=sample(f,c['name'],c['frames'],c['flags']);collisions=[];anchors=[];travel=[];active={}
    for frame,pose in enumerate(poses):
        for op,a in c['timeline'].get(frame,()):
            if 'MakeAttackColl' in op:active[a[0]]=(a[2],tuple(a[7:10]),'Scaled' in op)
            elif op=='ftMotionCommandClearAttackCollAll':active.clear()
            elif op=='ftMotionCommandClearAttackCollID':active.pop(a[0],None)
            elif op=='ftMotionCommandSetAttackCollOffset' and a[0] in active:
                j,_,scaled=active[a[0]];active[a[0]]=(j,tuple(a[1:]),scaled)
        matrices=world(bones,pose);centers=[(0,0,0)]*4
        for aid,(j,offset,scaled) in active.items():
            if scaled:offset=tuple(v/size for v in offset)
            r,t=matrices[j];centers[aid]=tuple(v*size for v in add(t,transform(r,offset)))
        collisions.append((sum(1<<aid for aid in active),tuple(centers)))
        # Full source basis includes animated scale, matching native capture FK.
        r,t=matrices[anchor];anchors.append((tuple(tuple(v*size for v in row) for row in r),tuple(v*size for v in t)))
        previous=poses[max(0,frame-1)].get(1,(0,)*10);trans=pose.get(1,(0,)*10)
        travel.append(((trans[6]-previous[6])*size,(trans[5]-previous[5])*size,-(trans[4]-previous[4])*size))
    return tuple(collisions),tuple(anchors),tuple(travel)

@lru_cache(None)
def throw_descriptors(fighter,phase):
    c=next(c for c in catalog() if c['fighter']==fighter and c['phase']==phase)
    pointer=next((a[0] for op,a in c['events'] if op=='ftMotionCommandSetThrow'),None)
    if pointer is None:return None
    text=us_text(next((ROOT/'src/relocData').glob('*_'+fighter+'MainMotion.c')).read_text())
    body=arrays(text,'FTThrowHitDesc')[pointer]
    return tuple(tuple(int(v.strip(),0) for v in row.split(',')) for row in re.findall(r'\{([^{}]+)\}',body))

@lru_cache(None)
def victims():
    result=[]
    for f in ROSTER:
        text=us_text(next((ROOT/'src/relocData').glob('*_'+f+'Main.c')).read_text())
        body=next(iter(arrays(text,'FTThrownStatus').values()))
        result.append(tuple(tuple(v.strip() for v in row.split(',')) for row in re.findall(r'\{([^{}]+)\}',body)[:24]))
    return tuple(result)

@lru_cache(None)
def props(index):
    from customAnimation import euler
    import math
    c=catalog()[index];fighter=c['fighter']
    if c['phase']=='Appeal':return ()
    joints=(16,17,18) if fighter=='Link' else tuple(range(17,23)) if fighter=='Samus' else (9,) if fighter=='Yoshi' else ()
    if not joints:return ()
    bones,_=rig(fighter,c['flags']);poses=sample(fighter,c['name'],c['frames'],c['flags']);size=source_size(fighter)
    result=[]
    for joint in joints:
        selected=-1;tick=0;timeline={}
        for op,a in c['events']:
            if op=='ftMotionCommandWaitAsync':tick=int(a[0],0)
            elif op=='ftMotionCommandSetModelPartID' and int(a[0],0)==joint:timeline[tick]=int(a[1],0)
        if joint not in bones or (fighter!='Yoshi' and 0 not in timeline.values()):continue
        frames=[]
        for frame,pose in enumerate(poses):
            selected=timeline.get(frame,selected)
            full=world(bones,pose)[joint];unit=world(bones,{j:(*v[:7],1,1,1) for j,v in pose.items()})[joint]
            sc=tuple(math.sqrt(sum(full[0][row][axis]**2 for row in range(3)))*size for axis in range(3))
            active=fighter=='Yoshi' or selected==0
            frames.append((euler(unit[0]),tuple(v*size for v in full[1]),sc,int(active)))
        if any(row[-1] for row in frames):result.append((joint,-1 if fighter=='Yoshi' else 0,tuple(frames)))
    return tuple(result)
