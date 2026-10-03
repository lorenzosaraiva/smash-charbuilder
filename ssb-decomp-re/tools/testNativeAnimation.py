#!/usr/bin/env python3
"""Compare all donor paths with original playback and collision C on the host."""
import re,struct,subprocess
from customAnimation import ROOT,sample,animation,source_size,attributes
from generateCustomCollisions import catalog,case_frames,stored_frames
from auditNormalMoves import arrays,us_text,ROSTER
from customMoveCatalog import resolved_moves,source_scripts,MOTIONS
from generateCustomMoves import expand
from generateNeutralProjectiles import catalog as projectile_catalog
from generateNeutralActions import catalog as action_catalog
from generateSpecialTiming import donkey_case


def function(text,name):
    start=re.search(r'\n(?:void|f32) '+name+r'\(',text).start()+1
    opening=text.index('{',start);depth=1;end=opening+1
    while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]


def main():
    # Independent US attribute values catch a nearby shield/item 'size' field
    # accidentally being used for donor reach or target compensation.
    assert tuple(source_size(f) for f in ROSTER)==(1.12,1.0,1.25,1.0,1.12,1.24,1.1,1.05,0.91,0.95,1.05,1.05)
    macros=(ROOT/'src/relocData/relocdata_types.h').read_text()
    macros=macros[macros.index('#define FT_ANIM_ROTX'):macros.index('#endif /* _RELOCDATA_TYPES_H_ */')]
    obj=(ROOT/'src/sys/objanim.c').read_text();collision=(ROOT/'src/gm/gmcollision.c').read_text()
    output=[macros,function(obj,'gcPlayDObjAnimJoint'),function(obj,'gcGetInterpValueCubic'),function(obj,'gcGetAObjValue'),
            function((ROOT/'src/lb/lbcommon.c').read_text(),'lbCommonPlayTranslateScaledDObjAnim'),
            function(collision,'gmCollisionTransformMatrixAll'),function(collision,'gmCollisionGetWorldPosition')]
    pose_calls=[];placement_calls=[];seen_models=set();seen_files=set();cases,_=catalog()
    for case_id,case in enumerate(cases):
        fighter,motion,name=(case[k] for k in ('fighter','motion','name'))
        path,_=animation(name)
        if path not in seen_files:output.append('#include "../src/relocData/'+path.name+'"');seen_files.add(path)
        if fighter not in seen_models:
            text=us_text(next((ROOT/'src/relocData').glob('*_'+fighter+'Model.c')).read_text())
            body=next(b for n,b in arrays(text,'DObjDesc').items() if n.endswith('JointTree'))
            body=re.sub(r'\(void\*\)[^,]+','NULL',body)
            output.append('static DObjDesc sOracle'+fighter+'Bind[] = { '+body+' };')
            setup,hidden,scales=attributes(fighter)
            output.append('static OracleHidden sOracle'+fighter+'Hidden[] = { '+','.join('{ '+','.join(map(str,h))+' }' for h in hidden)+' };')
            if scales:output.append('static Vec3f sOracle'+fighter+'Scale[] = { '+','.join('{ '+','.join(str(v)+'F' for v in scale)+' }' for scale in scales)+' };')
            seen_models.add(fighter)
        frames=len(case_frames(case_id));event_symbol='sOracle'+str(case_id)+'Events'
        output.append('static const OracleEvent '+event_symbol+'[] = {')
        desc=resolved_moves(fighter)[MOTIONS.index(motion)][1];tick=0
        for op,a in expand(desc[1],source_scripts()):
            kind=value=aid=joint=scaled=0;offset=(0,0,0)
            if op=='ftMotionCommandWait':kind=1;value=int(a[0],0);tick+=value
            elif op=='ftMotionCommandWaitAsync':
                value=int(a[0],0);kind=2
                if case['loop_period']:kind=1;value-=tick;tick+=value
                else:tick=value
            elif 'MakeAttackColl' in op:
                a=[int(v,0) for v in a];kind=3;aid=a[0];joint=a[2];offset=a[7:10];scaled=int('Scaled' in op)
            elif op=='ftMotionCommandClearAttackCollAll':kind=4
            elif op=='ftMotionCommandClearAttackCollID':kind=5;aid=int(a[0],0)
            elif op=='ftMotionCommandSetAttackCollOffset':kind=6;aid=int(a[0],0);offset=tuple(int(v,0) for v in a[1:])
            else:continue
            output.append('{ '+','.join(map(str,(kind,value,aid,joint)))+', { '+','.join(map(str,offset))+' }, '+str(scaled)+' },')
        if case['loop_period']:
            output.append('{ 1,'+str(case['duration']-tick)+',0,0,{0,0,0},0 }, { 7,0,0,0,{0,0,0},0 },')
        output.append('{ 0,0,0,0,{0,0,0},0 } };')
        table=next(iter(arrays(us_text(path.read_text()),r'AObjEvent32\s*\*')))
        setup,hidden,scales=attributes(fighter)
        scaling='sOracle'+fighter+'Scale' if scales and not case['flags']&4 else 'NULL'
        pose_calls.append(f'dump(sOracle{fighter}Bind,{table},ARRAY_COUNT({table}),{setup[0]}U,{setup[1]}U,sOracle{fighter}Hidden,ARRAY_COUNT(sOracle{fighter}Hidden),{case["flags"]}U,{scaling},{frames},{event_symbol},{source_size(fighter)}F);')
        if stored_frames(case_id)[1]:
            symbol='sFTCustomCollision'+case['label'];placement_calls.append('dumpRootPlacement('+symbol+',ARRAY_COUNT('+symbol+'));')
    projectile_calls=[]
    for i,case in enumerate(projectile_catalog()):
        fighter=case['fighter'];path,_=animation(case['animation'])
        if path not in seen_files:
            output.append('#include "../src/relocData/'+path.name+'"');seen_files.add(path)
        events='sOracleProjectile'+str(i)
        output.append('static const OracleEvent '+events+'[] = { {2,'+str(case['firing'])+',0,0,{0,0,0},0}, {3,0,0,'+str(case['joint'])+',{0,0,0},0}, {0,0,0,0,{0,0,0},0} };')
        table=next(iter(arrays(us_text(path.read_text()),r'AObjEvent32\s*\*')))
        setup,hidden,scales=attributes(fighter)
        scaling='sOracle'+fighter+'Scale' if scales and not case['flags']&4 else 'NULL'
        projectile_calls.append(f'dump(sOracle{fighter}Bind,{table},ARRAY_COUNT({table}),{setup[0]}U,{setup[1]}U,sOracle{fighter}Hidden,ARRAY_COUNT(sOracle{fighter}Hidden),{case["flags"]}U,{scaling},{case["firing"]+1},{events},{source_size(fighter)}F);')
    action_calls=[]
    for i,case in enumerate(action_catalog()+(donkey_case(),)):
        fighter=case['fighter'];path,_=animation(case['animation'])
        if path not in seen_files:
            output.append('#include "../src/relocData/'+path.name+'"');seen_files.add(path)
        event_symbol='sOracleNeutralAction'+str(i)
        output.append('static const OracleEvent '+event_symbol+'[] = {')
        probe = ('{3,0,3,16,{180,0,0},0},' if fighter=='Samus' else
                 '{3,0,3,31,{0,0,0},0},' if fighter=='Yoshi' else
                 '{3,0,3,0,{0,0,0},0},' if fighter=='Link' else '')
        if probe:output.append(probe)
        for op,a in case['events']:
            kind=value=aid=joint=scaled=0;offset=(0,0,0)
            if op=='ftMotionCommandWait':kind=1;value=int(a[0],0)
            elif op=='ftMotionCommandWaitAsync':kind=2;value=int(a[0],0)
            elif 'MakeAttackColl' in op:
                a=[int(v,0) for v in a];kind=3;aid=a[0];joint=a[2];offset=a[7:10];scaled=int('Scaled' in op)
            elif op=='ftMotionCommandClearAttackCollAll':kind=4
            elif op=='ftMotionCommandClearAttackCollID':kind=5;aid=int(a[0],0)
            elif op=='ftMotionCommandSetAttackCollOffset':kind=6;aid=int(a[0],0);offset=tuple(int(v,0) for v in a[1:])
            else:continue
            output.append('{ '+','.join(map(str,(kind,value,aid,joint)))+', { '+','.join(map(str,offset))+' }, '+str(scaled)+' },')
            if kind==4 and probe:output.append(probe)
        output.append('{0,0,0,0,{0,0,0},0} };')
        table=next(iter(arrays(us_text(path.read_text()),r'AObjEvent32\s*\*')))
        setup,hidden,scales=attributes(fighter)
        scaling='sOracle'+fighter+'Scale' if scales and not case['flags']&4 else 'NULL'
        action_calls.append(f'dump(sOracle{fighter}Bind,{table},ARRAY_COUNT({table}),{setup[0]}U,{setup[1]}U,sOracle{fighter}Hidden,ARRAY_COUNT(sOracle{fighter}Hidden),{case["flags"]}U,{scaling},{case["duration"]+1},{event_symbol},{source_size(fighter)}F);')
    output.append('static const f32 sOracleBodySizes[] = { '+', '.join(str(source_size(f))+'F' for f in ROSTER)+' };')
    (ROOT/'build/nativeAnimationOracle.inc').write_text('\n'.join(output)+'\n',encoding='utf-8')
    (ROOT/'build/nativeAnimationCalls.inc').write_text('\n'.join(pose_calls+placement_calls+projectile_calls+action_calls)+'\n',encoding='utf-8')
    subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-O1','-Iinclude','-Isrc','-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US','tools/testNativeAnimation.c','-o','build/testNativeAnimation'],cwd=ROOT,check=True)
    raw=subprocess.check_output([str(ROOT/'build/testNativeAnimation')],cwd=ROOT)
    (ROOT/'build/native-animation-poses.bin').write_bytes(raw)
    cursor=0;comparisons=0;maximum=0;geometry_error=0;centers_checked=0;native_geometry={}
    for case_id,case in enumerate(cases):
        fighter,motion,name=(case[k] for k in ('fighter','motion','name'))
        frames=len(case_frames(case_id));poses=sample(fighter,name,frames,case['flags']);native_geometry[case_id]=[]
        for frame,(mask,centers) in enumerate(case_frames(case_id)):
            for joint in sorted(poses[frame]):
                native=struct.unpack_from('<9f',raw,cursor);cursor+=36
                pose=poses[frame][joint];converted=pose[:3]+pose[4:]
                for channel,(a,b) in enumerate(zip(native,converted)):
                    error=abs(a-b);maximum=max(maximum,error);comparisons+=1
                    assert error<0.003,(name,joint,frame,channel,a,b,error)
            native_centers=[]
            for aid,center in enumerate(centers):
                native=struct.unpack_from('<3f',raw,cursor);cursor+=12;native_centers.append(native)
                for a,b in zip(native,center):
                    error=abs(a-b);geometry_error=max(geometry_error,error)
                    assert error<0.001,(fighter,motion,frame,aid,native,center,error)
                if mask&(1<<aid):centers_checked+=1
            native_mask=struct.unpack_from('<I',raw,cursor)[0];cursor+=4
            assert native_mask==mask,(fighter,motion,frame,'native motion-event active mask',native_mask,mask)
            native_geometry[case_id].append(native_centers)
    placement_error=0;placements=0
    for case_id,case in enumerate(cases):
        _,frames=stored_frames(case_id)
        if not frames:continue
        for body in ROSTER:
            for facing in (-1,1):
                for frame,(mask,_) in enumerate(frames):
                    for aid in range(4):
                        if not mask&(1<<aid):continue
                        actual=struct.unpack_from('<3f',raw,cursor);cursor+=12
                        expected=struct.unpack_from('<3f',raw,cursor);cursor+=12
                        error=max(abs(a-b) for a,b in zip(actual,expected));placement_error=max(placement_error,error);placements+=1
                        assert error<0.001,(case['label'],body,facing,frame,aid,actual,expected)
    projectile_error=0
    for case in projectile_catalog():
        poses=sample(case['fighter'],case['animation'],case['firing']+1,case['flags'])
        for frame,pose in enumerate(poses):
            cursor+=len(pose)*36
            centers=struct.unpack_from('<12f',raw,cursor);cursor+=48
            mask=struct.unpack_from('<I',raw,cursor)[0];cursor+=4
            assert mask==int(frame==case['firing'])
            if mask and case['joint']:
                native=(centers[2],centers[1],-centers[0])
                error=max(abs(a-b) for a,b in zip(native,case['offset']))
                projectile_error=max(projectile_error,error)
                assert error<0.003,(case['fighter'],case['air'],native,case['offset'],error)
    action_error=0;action_centers=0
    for case in action_catalog()+(donkey_case(),):
        previous_trans=(0,0,0)
        poses=sample(case['fighter'],case['animation'],case['duration']+1,case['flags'])
        for frame,pose in enumerate(poses):
            trans=(0,0,0)
            for joint in sorted(pose):
                native=struct.unpack_from('<9f',raw,cursor);cursor+=36
                expected=pose[joint][:3]+pose[joint][4:]
                assert max(abs(a-b) for a,b in zip(native,expected))<0.003,(case['fighter'],case['phase'],joint,frame)
                if joint==1: trans=native[3:6]
            centers=struct.unpack_from('<12f',raw,cursor);cursor+=48
            mask=struct.unpack_from('<I',raw,cursor)[0];cursor+=4
            expected_mask,expected_centers=case['frames'][frame]
            hand_slap=case['phase']=='HandSlap'
            assert mask&(15 if hand_slap else 7)==expected_mask,(case['fighter'],case['phase'],frame,mask,expected_mask)
            for aid in range(4 if hand_slap else 3):
                if not expected_mask&(1<<aid):continue
                error=max(abs(a-b) for a,b in zip(centers[aid*3:aid*3+3],expected_centers[aid]))
                action_error=max(action_error,error);action_centers+=1
                assert error<0.003,(case['fighter'],case['phase'],frame,aid,error)
            if case['fighter'] in ('Captain','Purin') and not case['air']:
                movement=(0,0,0) if frame==0 else ((trans[2]-previous_trans[2])*source_size(case['fighter']),0,(trans[0]-previous_trans[0])*source_size(case['fighter']))
                assert max(abs(a-b) for a,b in zip(movement,case['travel'][frame]))<0.003,(case['fighter'],'root movement',frame)
            previous_trans=trans
            probe=case['spawn'] or case['anchors']
            if probe:
                native=(centers[11],centers[10],-centers[9])
                assert mask&8 and max(abs(a-b) for a,b in zip(native,probe[frame]))<0.003,(case['fighter'],case['phase'],'socket',frame,native,probe[frame])
    print(f'PASS: all 30 remaining neutral phases and DK Hand Slap, {action_centers} active centers, grounded root movement, charge/boomerang sockets and Yoshi capture anchors match original playback/matrices; max center error {action_error:.7f}.')
    assert cursor==len(raw),(cursor,len(raw))
    print(f'PASS: all eight projectile-neutral spawn poses match original animation/collision matrices; max error {projectile_error:.7f}.')
    print(f'PASS: {len(cases)} donor timelines, {comparisons} scalar samples match original ftAnimParseDObjFigatree and playback; max error {maximum:.7f}.')
    print(f'PASS: {centers_checked} active centers/masks match original collision matrices and native wait scheduling; max error {geometry_error:.7f} engine units.')
    print(f'PASS: {placements} world positions at all twelve body sizes/both facings; max error {placement_error:.7f}.')
    from verifyCustomCollisionData import verify_compiled_collisions
    verify_compiled_collisions(native_geometry)

if __name__=='__main__':main()
