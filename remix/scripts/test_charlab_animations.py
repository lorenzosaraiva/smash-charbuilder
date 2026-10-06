"""Independent decomp ELF oracle for ROM streaming and production MIPS poses.

The OS DMA service is supplied by the verifier; all pose math/cache code is real
linked MIPS. Rendered meshes/effects and gameplay contact remain playtest items.
"""
from pathlib import Path
import json
import math
import struct
from elfData import read_elf

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent/'ssb-decomp-re'


def multiply(a, b):
    x,y,z,w=a; X,Y,Z,W=b
    return (w*X+x*W+y*Z-z*Y, w*Y-x*Z+y*W+z*X, w*Z+x*Y-y*X+z*W, w*W-x*X-y*Y-z*Z)


def euler(x,y,z):
    sx,cx=math.sin(x/2),math.cos(x/2); sy,cy=math.sin(y/2),math.cos(y/2); sz,cz=math.sin(z/2),math.cos(z/2)
    return (sx*cy*cz-cx*sy*sz,cx*sy*cz+sx*cy*sz,cx*cy*sz-sx*sy*cz,cx*cy*cz+sx*sy*sz)


def matrix(q):
    length=math.sqrt(sum(v*v for v in q)); x,y,z,w=(v/length for v in q)
    return (1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y))


def test_animations(r, rom):
    host, sections, symbols = read_elf(LAB/'build/testCustomMove', '<')
    manifest=json.loads((ROOT/'build/char_creator/runtime/animations.json').read_text())
    bank=(ROOT/'build/char_creator/runtime/animations.bin').read_bytes()
    assert rom[manifest['rom_start']:manifest['rom_start']+len(bank)] == bank
    assert manifest['cache_bytes'] <= 0x8000
    assert r.addr('sCCAnimationCache')%16==0 and manifest['cache_bytes']%16==0
    def read(address, size):
        for section in sections:
            if section[1] != 8 and section[3] <= address < section[3]+section[5]:
                start=section[4]+address-section[3]
                return host[start:start+size]
        raise AssertionError(hex(address))
    def symbol(name):
        address,length,_=symbols[name]
        return read(address,length)
    all_keys=symbol('sFTCustomAnimationKeys')
    all_curves=symbol('sFTCustomAnimationCurves')
    body_table=struct.unpack('<24I',symbol('sFTCustomAnimationRigs'))
    bodies=[]
    for pointer,count in zip(body_table[::2],body_table[1::2]):
        bodies.append([struct.unpack('<BBbB14f',read(pointer+i*60,60)) for i in range(count)])
    # Check mixed-endian bind records, including their semantic byte fields.
    for name,(address,length,_) in symbols.items():
        if not name.startswith(('sFTCustomAnimationRig','sFTCustomAnimationSourceRig','sFTCustomAnimationSemantic')) or 'CharLabRuntime.'+name not in r.labels:
            continue
        raw=read(address,length)
        if name.startswith('sFTCustomAnimationRig') and name!='sFTCustomAnimationRigs':
            expected=b''.join(struct.pack('>BBbB14f',*struct.unpack_from('<BBbB14f',raw,i)) for i in range(0,length,60))
        elif name.endswith('Bones'):
            expected=b''.join(struct.pack('>BBH4f',*struct.unpack_from('<BBH4f',raw,i)) for i in range(0,length,20))
        elif name=='sFTCustomAnimationSemanticJoints': expected=raw
        else: continue  # Pointer records already covered by ELF relocations.
        assert r.read(r.addr(name),length)==expected,name
    records={row['symbol']:row for row in manifest['clips']}
    references={}
    total_keys=0
    for name,row in records.items():
        rig,channels,root,count,loop,period=struct.unpack('<6I',symbol(name))
        bones,bone_count=struct.unpack('<2I',read(rig,8)); roles=read(rig+8,24)
        sources=[struct.unpack('<BBH4f',read(bones+i*20,20)) for i in range(bone_count)]
        channel_ids=struct.unpack('<'+str(bone_count*3)+'H',read(channels,bone_count*6))
        payload=bank[row['offset']:row['offset']+row['size']]
        assert count==row['count'] and row['size']<=manifest['cache_bytes']
        curves=[]
        for i,index in enumerate(channel_ids):
            start,length,_=struct.unpack_from('<IHH',all_curves,index*8)
            actual_start,actual_length,_=struct.unpack_from('>IHH',payload,i*8)
            assert length==actual_length
            raw=all_keys[start*3:(start+length)*3]
            assert payload[row['key_offset']+actual_start*3:row['key_offset']+(actual_start+length)*3]==raw
            curves.append([(raw[j],struct.unpack('>h',raw[j+1:j+3])[0]/4096) for j in range(0,len(raw),3)])
            total_keys+=length
        roots=[struct.unpack('<3h',read(root+i*6,6)) for i in range(count)]
        assert payload[row['root_offset']:row['root_offset']+count*6]==b''.join(struct.pack('>3h',*v) for v in roots)
        record=r.addr(name)
        assert struct.unpack('>7I',r.read(record+4,28))==(row['offset'],row['size'],row['key_offset'],row['root_offset'],count,loop,period)
        references[record]=(name,sources,roles,curves,roots,count,loop,period)
    # Independently translate the original normal selector's pointers.
    host_names={value[0]:name for name,value in symbols.items() if name in records}
    host_table=struct.unpack('<396I',symbol('sFTCustomAnimationClips'))
    original_table=r.read(r.addr('sCCNormalAnimations'),396*4)
    actual_table=struct.unpack('>396I',original_table)
    assert actual_table==tuple(r.addr(host_names[p]) if p else 0 for p in host_table)
    def evaluate(keys,frame):
        if frame<=keys[0][0]:return keys[0][1]
        if frame>=keys[-1][0]:return keys[-1][1]
        for (a,x),(b,y) in zip(keys,keys[1:]):
            if a<=frame<=b:return x+(y-x)*(frame-a)/(b-a)
        raise AssertionError(frame)
    checks=0; maximum=0
    # Route every retained clip through the real normal selector as a fixture,
    # exercising packed curves/roots and all twelve target rigs. Special and
    # normal binding selection are also exercised separately below.
    for body in range(12):
        print(f'Checking streamed poses on body {body+1}/12...', flush=True)
        r.call('ccReset'); r.setup(body,0,body%4)
        player=body%4; clock=r.addr('sFTCustomMoveClocks')+player*r.clock_size
        r.u32(r.FP+0x24,10);r.u32(r.FP+0x28,10)
        r.write(clock,struct.pack('>6I',r.FP,r.u32(r.FP+r.player_num),r.addr('sFTCustomMoves'),10,10,60))
        for record,ref in references.items():
            name,sources,roles,curves,roots,count,loop,period=ref
            frame=count//2
            if period and frame>=loop:frame=loop+(frame-loop)%period
            r.u32(r.addr('sCCNormalAnimations'),record)
            r.f32(clock+r.clock_frame,frame)
            before=(r.read(r.JOINTS,0x100),r.read(r.FP+0x294,4*0xC4),r.read(clock,r.clock_size))
            r.call('ccApplyAnimation',r.FP)
            assert before==(r.read(r.JOINTS,0x100),r.read(r.FP+0x294,4*0xC4),r.read(clock,r.clock_size)),name
            source={0:(0,0,0,1)}
            for i,bone in enumerate(sources):
                source[bone[0]]=multiply(source[bone[1]],euler(*(evaluate(curves[i*3+j],frame) for j in range(3))))
            delta=[multiply(source[sources[i][0]],sources[i][3:7]) for i in roles]
            observed={0:(0,0,0,1)};desired={0:(0,0,0,1)}
            for bone in bodies[body]:
                joint,parent,role,required,*values=bone
                expected=multiply(delta[role],values[10:14]) if role>=0 else multiply(desired[parent],values[6:10])
                desired[joint]=expected
                rotation=struct.unpack('>3f',r.read(r.JOINTS+joint*0x100+r.layout['rotate'],12))
                observed[joint]=multiply(observed[parent],euler(*rotation))
                error=max(abs(a-b) for a,b in zip(matrix(expected),matrix(observed[joint])))
                maximum=max(maximum,error);checks+=1
                assert error<.008,(name,body,frame,joint,error)
                translation=struct.unpack('>3f',r.read(r.JOINTS+joint*0x100+r.layout['translate'],12))
                expected_translation=tuple(values[i]+(roots[frame][i]*values[1]/4096 if joint==4 else 0) for i in range(3))
                assert max(abs(a-b) for a,b in zip(translation,expected_translation))<.06,(name,body,'translation')
        # Cache hit must not issue another DMA; changing clips must issue one.
        loads=r.u32(r.addr('gCCAnimationLoads'))
        r.call('ccApplyAnimation',r.FP)
        assert r.u32(r.addr('gCCAnimationLoads'))==loads
    r.write(r.addr('sCCNormalAnimations'),original_table)
    # Real Remix callback aliases: absent cosmetic/optional joints point to
    # TopN. Retargeting must suspend them or it teleports the fighter.
    aliases=0
    for body in range(12):
        player=body%4;r.call('ccReset');r.setup(body,7,player)
        r.u32(r.FP+0x24,220);r.u32(r.FP+0x28,205)
        r.u32(r.FP+8,7)
        r.u32(r.labels['CharCreator.body_character_data']+player*4,r.ATTR)
        r.u32(r.labels['CharCreator.body_character_id']+player*4,body)
        r.u32(r.labels['CharCreator.active_special_donor']+player*4,7)
        for joint in (2,3):r.u32(r.FP+0x8E8+joint*4,0)
        for bone in bodies[body]:
            if not bone[3]:r.u32(r.FP+0x8E8+bone[0]*4,0)
        r.call('install_joint_fallbacks_',r.FP,namespace='CharCreator')
        special=r.addr('sCCSpecialClocks')+player*36
        r.write(special,struct.pack('>5If3I',r.FP,220,205,7,60,12.,r.u32(r.FP+r.player_num),0,0))
        for i,v in enumerate((1234.,5678.,90.)):r.f32(r.JOINTS+r.layout['translate']+i*4,v)
        before=r.read(r.JOINTS,0x100)
        r.call('ccApplyAnimation',r.FP)
        assert before==r.read(r.JOINTS,0x100),(body,'callback alias changed world root')
        assert r.u32(r.FP+0x8E8+2*4)==r.JOINTS,(body,'callback alias not restored')
        aliases+=1
    # Exercise each native special binding through its own production clock,
    # including frozen phases, charge/hold loops and four interleaved ports.
    _,_,runtime_symbols=read_elf(ROOT/'build/char_creator/runtime/runtime.o','>')
    size=runtime_symbols['sCCSpecialAnimations'][1]
    special_rows=[struct.unpack('>3I',r.read(r.addr('sCCSpecialAnimations')+i,12)) for i in range(0,size,12)]
    for body in range(12):
        for donor,motion,record in special_rows:
            player=body%4
            r.call('ccReset');r.setup(body,donor,player)
            r.u32(r.FP+8,donor);r.u32(r.FP+0x24,220);r.u32(r.FP+0x28,motion)
            r.u32(r.labels['CharCreator.body_character_data']+player*4,r.ATTR)
            r.u32(r.labels['CharCreator.body_character_id']+player*4,body)
            r.u32(r.labels['CharCreator.active_special_donor']+player*4,donor)
            special=r.addr('sCCSpecialClocks')+player*36
            ref=references[record];frame=ref[5]//2
            r.write(special,struct.pack('>5If3I',r.FP,220,motion,donor,60,float(frame),r.u32(r.FP+r.player_num),0,0))
            r.call('ccApplyAnimation',r.FP)
            assert r.u32(r.addr('sCCAnimationLoaded')+player*4)==record,(body,donor,motion)
    assert r.u32(r.addr('gFTCustomAnimationValidationFailures'))==0
    print(f'PASS: {len(records)} ROM clips/{total_keys:,} packed keys match the decomp ELF; {checks:,} MIPS joint poses on twelve bodies, {len(special_rows)*12} special selections, {aliases} live callback-alias guards, all four caches, root/hitbox/clock isolation (max matrix error {maximum:.6f}).')
