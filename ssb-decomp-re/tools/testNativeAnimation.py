#!/usr/bin/env python3
"""Compare the converter with original engine playback compiled on the host."""
import re
import struct
import subprocess
from customAnimation import ROOT, PILOTS, model, sample, animation,source_size
from generateCustomAnimations import collision_definitions,collision_frames
from customMoveTiming import animation_duration
from auditNormalMoves import arrays,us_text,ROSTER
from generateCustomCollisions import COLLISION_PILOTS

ORACLE_CASES = (*PILOTS, *COLLISION_PILOTS)

def function(text,name):
    start=re.search(r'\n(?:void|f32) '+name+r'\(',text).start()+1
    opening=text.index('{',start);depth=1;end=opening+1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]

def main():
    macros=(ROOT/'src/relocData/relocdata_types.h').read_text()
    macros=macros[macros.index('#define FT_ANIM_ROTX'):macros.index('#endif /* _RELOCDATA_TYPES_H_ */')]
    native=function((ROOT/'src/sys/objanim.c').read_text(),'gcPlayDObjAnimJoint')
    collision=(ROOT/'src/gm/gmcollision.c').read_text()
    output=[macros,native,function(collision,'gmCollisionTransformMatrixAll'),function(collision,'gmCollisionGetWorldPosition')]
    for fighter,motion,name,index in ORACLE_CASES:
        path,_=animation(name)
        output.append('#include "../src/relocData/'+path.name+'"')
        text=us_text(next((ROOT/'src/relocData').glob('*_'+fighter+'Model.c')).read_text())
        body=next(body for label,body in arrays(text,'DObjDesc').items() if label.endswith('JointTree'))
        body=re.sub(r'\(void\*\)\w+','NULL',body)
        output.append('static DObjDesc sOracle'+fighter+'Bind[] = { '+body+' };')
        frames=animation_duration('&ll'+name+'FileID')+1
        output.append('static OracleHit sOracle'+fighter+'Hits[][4] = {')
        for active in collision_definitions(fighter,motion,frames):
            output.append('{ '+', '.join('{ '+str(active[aid][0])+', { '+', '.join(str(v) for v in active[aid][1])+' }, '+str(int(active[aid][2]))+' }' if aid in active else '{ -1, { 0,0,0 }, 0 }' for aid in range(4))+' },')
        output.append('};')
    output.append('static const f32 sOracleBodySizes[] = { '+', '.join(str(source_size(f))+'F' for f in ROSTER)+' };')
    (ROOT/'build/nativeAnimationOracle.inc').write_text('\n'.join(output)+'\n')
    subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-O1','-Iinclude','-Isrc','-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US','tools/testNativeAnimation.c','-o','build/testNativeAnimation'],cwd=ROOT,check=True)
    raw=subprocess.check_output([str(ROOT/'build/testNativeAnimation')],cwd=ROOT)
    (ROOT/'build/native-animation-poses.bin').write_bytes(raw)
    cursor=0;comparisons=0;maximum=0
    for fighter,motion,name,index in ORACLE_CASES:
        frames=animation_duration('&ll'+name+'FileID')+1
        poses=sample(fighter,name,frames)
        for joint in model(fighter):
            for frame in range(frames):
                native=struct.unpack_from('<9f',raw,cursor);cursor+=36
                pose=poses[frame][joint];converted=pose[:3]+pose[4:]
                for channel,(a,b) in enumerate(zip(native,converted)):
                    error=abs(a-b);maximum=max(maximum,error);comparisons+=1
                    assert error<0.003,(name,joint,frame,channel,a,b,error)
    geometry_error=0;centers_checked=0;native_geometry={}
    for fighter,motion,name,index in ORACLE_CASES:
        frames=animation_duration('&ll'+name+'FileID')+1
        poses=sample(fighter,name,frames)
        native_geometry[(fighter,motion)]=[]
        for frame,(mask,centers) in enumerate(collision_frames(fighter,motion,poses)):
            native_centers=[]
            for aid,center in enumerate(centers):
                native=struct.unpack_from('<3f',raw,cursor);cursor+=12
                native_centers.append(native)
                for a,b in zip(native,center):
                    error=abs(a-b);geometry_error=max(geometry_error,error)
                    assert error<1,(fighter,frame,aid,native,center,error)
                if mask&(1<<aid):centers_checked+=1
            native_geometry[(fighter,motion)].append(native_centers)
    placement_error=0;placements=0
    for body in ROSTER:
        for facing in (-1,1):
            for frame,(mask,_) in enumerate(collision_frames('Kirby','AttackHi3',sample('Kirby','FTKirbyAnimUTilt',19))):
                for aid in range(4):
                    if not mask&(1<<aid):continue
                    actual=struct.unpack_from('<3f',raw,cursor);cursor+=12
                    expected=struct.unpack_from('<3f',raw,cursor);cursor+=12
                    error=max(abs(a-b) for a,b in zip(actual,expected))
                    placement_error=max(placement_error,error);placements+=1
                    assert error<0.001,(body,facing,frame,aid,actual,expected)
    assert cursor==len(raw)
    print(f'PASS: {comparisons} scalar pose samples match original ftAnimParseDObjFigatree/gcPlayDObjAnimJoint; maximum error {maximum:.7f}.')
    print(f'PASS: {centers_checked} active hitbox centers match original gmCollision matrix/point transforms; maximum coordinate error {geometry_error:.7f} engine units.')
    print(f'PASS: {placements} translated world hitbox positions match at all twelve body sizes and both facings; maximum coordinate error {placement_error:.7f}.')
    from verifyCustomCollisionData import verify_compiled_collisions
    verify_compiled_collisions(native_geometry)

if __name__=='__main__':main()
