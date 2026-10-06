"""Linked-MIPS attachment/timing/ownership checks; rendering stays a playtest.

EF allocation and audio are explicit fixtures. Source samples, semantic mapping,
world placement, scripts, visibility and interruption cleanup execute in the ROM.
"""
import math
import re
import struct
from pathlib import Path
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1
from elfData import read_elf


def test_visuals(r):
    root = Path(__file__).resolve().parents[1]
    names = ('state_size','model','charge','effect','hidden','dobj_flags','hidden_mask',
             'next','fighter','parts','common','part_size','desc_size','desc_dl','shot_dl','shot_mats',
             'loop','voice','wait_op','end_op','loop_op','stop_op','voice_op','fgm_op',
             'def_size','defs','update','effect_op')
    layout = dict(zip(names, struct.unpack('>28I', r.read(r.addr('ccVisualLayout'), 112))))
    del r.services[r.addr('ccVisualTick')]
    links = 0x800466F0
    state = r.addr('sCCVisualStates')
    definitions = r.addr('sFTCustomSpecialAnimations')
    arena, native_data, attrs = 0x80250000, 0x80240000, 0x80241000
    container, common, parts, desc = 0x80242000,0x80243000,0x80244000,0x80245000
    main = attrs-0x100
    allocated, stopped, sounds, loops, voices = [], [], [], [], []
    counter = 0
    def allocate():
        nonlocal counter
        g = arena+counter*0x400;counter+=1
        assert counter<200
        r.write(g,bytes(0x400));r.u32(g+0x84,g+0x100)
        r.u32(g+r.layout['obj'],g+0x200)
        r.u32(g+layout['next'],r.u32(links+24));r.u32(links+24,g)
        allocated.append((g,r.reg(UC_MIPS_REG_A0)))
        return g
    def stop():
        g = r.reg(UC_MIPS_REG_A0);stopped.append(g)
        prev = links+24;current = r.u32(prev)
        while current:
            if current==g:r.u32(prev,r.u32(g+layout['next']));return
            prev=current+layout['next'];current=r.u32(prev)
        raise AssertionError(('Stopped an unowned/stale effect',hex(g)))
    r.services[0x800FDAFC] = allocate
    r.services[0x800E9BE8] = stop
    r.services[0x800FD5D8] = lambda:0
    native = {}
    native.update({name:int(address,16) for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);',
        (root.parent/'ssb-decomp-re/symbols/symbols_us.txt').read_text(),re.M)})
    for path in (root.parent/'ssb-decomp-re/src').rglob('*.c'):
        native.update({name:int(address,16) for address,name in re.findall(
            r'// (0x[0-9A-Fa-f]{8})[^\n]*\n(?:[\w*]+\s+)+(\w+)\(',path.read_text(encoding='utf-8'))})
    for name in ('lbCommonAddMObjForFighterPartsDObj','gcAddMObjAll','ftParamMakeEffect'):
        r.services[native[name]] = lambda:0
    r.services[0x800269C0] = lambda:sounds.append(r.reg(UC_MIPS_REG_A0))
    def play(field,records):
        fp=r.reg(UC_MIPS_REG_A0);r.u32(fp+layout[field],0x80247000)
        records.append(r.reg(UC_MIPS_REG_A1))
    r.services[native['ftParamPlayLoopSFX']] = lambda:play('loop',loops)
    r.services[native['ftParamPlayVoice']] = lambda:play('voice',voices)
    r.services[native['ftParamStopLoopSFX']] = lambda:r.u32(r.reg(UC_MIPS_REG_A0)+layout['loop'],0)
    r.services[native['ftParamStopVoice']] = lambda:r.u32(r.reg(UC_MIPS_REG_A0)+layout['voice'],0)
    r.write(native_data,bytes(0x100));r.u32(native_data+0x60,0x100)
    r.write(attrs,bytes(0x400));r.u32(attrs+layout['parts'],container);r.u32(attrs+layout['common'],common)
    for joint in range(33):r.u32(container+joint*4,parts)
    r.write(parts,bytes(0x200))
    for index in range(8):r.u32(parts+index*layout['part_size'],0x80249000+index*8)
    r.u32(common,desc)
    for joint in range(33):r.u32(desc+joint*layout['desc_size']+layout['desc_dl'],0x80249100)
    for donor in range(12):
        r.u32(0x80116E10+donor*4,native_data)
        r.u32(r.labels['CharCreator.main_file_pointers']+donor*4,main)
    def context(index,body=0,port=0):
        r.call('ccReset');r.setup(body,0,port)
        r.u32(r.FP+layout['fighter'],r.GOBJ);r.u32(links+12,r.GOBJ)
        r.u32(r.FP+0x24,0xDC);r.u32(r.FP+0x28,300)
        d=definitions+index*layout['def_size'];move=r.u32(d)
        c=r.addr('sFTCustomMoveClocks')+port*r.clock_size
        r.write(c,struct.pack('>6I2fIIf',r.FP,r.u32(r.FP+r.player_num),move,0xDC,300,r.u32(move+8),0,0,r.u32(move+12),0,1))
        r.call('ccVisualStart',r.FP,0)
        return d,c,state+port*layout['state_size']
    def tick(c,time):
        r.f32(c+r.clock_frame,time);r.call('ccVisualTick',r.GOBJ)
    # Independent original ELF prop samples (the visual/audio scripts extend
    # its earlier safe catalog, so those are checked as executed clocks below).
    oracle,sections,symbols=read_elf(root.parent/'ssb-decomp-re/build/testSpecialAnimations','<')
    def original(name):
        a,length,i=symbols[name];s=sections[i];off=s[4]+a-s[3]
        return oracle[off:off+length]
    props=[]
    for index in range(layout['defs']):
        d=definitions+index*layout['def_size'];p=r.u32(d+16)
        if p:
            sample=r.u32(p);name='sFTCustomSpecialAttachment'+str(index)
            raw=original(name)
            expected=b''.join(struct.pack('>9fI',*struct.unpack_from('<9fI',raw,offset)) for offset in range(0,len(raw),40))
            assert r.read(sample,len(expected))==expected,name
            props.append((index,r.u32(d+12),p,len(expected)//40))
    placements=0
    for index,donor,prop,count in props:
        source=r.u32(prop)
        frames=[i for i in range(count) if r.u32(source+i*40+36)]
        if not frames:continue
        for body in range(12):
            if body==donor:continue
            d,c,s=context(index,body,body%4)
            # Isolate script allocation/audio here; tested separately below.
            r.u32(s+32,0)
            for facing in (-1,1):
                r.u32(r.FP+0x44,facing)
                for axis,value in enumerate((120,300,40)):r.f32(r.JOINTS+r.layout['translate']+axis*4,value)
                for frame in sorted(set((frames[0],frames[len(frames)//2],frames[-1]))):
                    # Resetting the clock backwards deliberately restarts the
                    # source script; the allocator remains a fixture.
                    tick(c,frame);g=r.u32(s+layout['model']);assert g,(index,body,frame)
                    model=r.u32(g+r.layout['obj'])
                    values=struct.unpack('>9fI',r.read(source+frame*40,40))
                    expected=(120+values[5]*facing,300+values[4],40-values[3]*facing)
                    actual=struct.unpack('>3f',r.read(model+r.layout['translate'],12))
                    assert max(abs(a-b) for a,b in zip(actual,expected))<.005,(index,body,frame,actual,expected)
                    assert all(math.isfinite(v) for v in struct.unpack('>3f',r.read(model+r.layout['rotate'],12)))
                    assert r.read(model+r.layout['scale'],12)==r.read(source+frame*40+24,12)
                    placements+=1
            hidden=bool(r.u32(prop+12));assert bool(r.u32(s+layout['hidden']))==hidden
            r.call('ccStatusChanging',r.GOBJ,18) # native damage/common interrupt
            assert not any(r.u32(s+layout[f]) for f in ('model','charge','effect','hidden'))
            for i in range(4,37):assert not r.read(r.JOINTS+i*0x100+layout['dobj_flags'],1)[0]&layout['hidden_mask']
            counter=0
    # Exact scheduling, same-frame idempotence, tracked voices/loops and muted
    # playback use a short independently constructed native command stream.
    d,c,s=context(0)
    loops.clear();voices.clear();sounds.clear()
    script=0x80248000
    words=[layout['wait_op']<<26|3,layout['loop_op']<<26|11,
           layout['voice_op']<<26|12,layout['fgm_op']<<26|13,
           layout['wait_op']<<26|8,layout['stop_op']<<26,layout['end_op']<<26]
    r.write(script,struct.pack('>7I',*words));r.u32(s+32,script)
    for time in (0,2.9):tick(c,time)
    assert not loops and not voices
    tick(c,3)
    assert loops==[11] and voices==[12] and sounds[-1]==13
    tick(c,3);assert loops==[11]
    r.call('ccStatusChanging',r.GOBJ,0) # stock loss
    assert r.u32(r.FP+layout['loop'])==0 and r.u32(r.FP+layout['voice'])==0
    # Real flag consumers preserve donor creation/removal windows.
    for kick in (0,1):
        index=next(i for i in range(layout['defs']) if r.u32(definitions+i*layout['def_size']+12)==7)
        _,c,s=context(index)
        r.u32(r.addr('sCCVisualFiles')+(4 if kick else 8),main)
        flag=r.FP+r.layout['flags']+(8 if kick else 0)
        r.u32(flag,1);r.call('ccVisualFalconEffect',r.GOBJ,kick)
        obj=r.u32(s+layout['effect']);assert obj and r.u32(flag)==0
        r.u32(flag,2 if kick else 1);r.call('ccVisualFalconEffect',r.GOBJ,kick)
        assert not r.u32(s+layout['effect']) and r.u32(flag)==(0 if kick else 2)
    index=next(i for i in range(layout['defs']) if r.u32(definitions+i*layout['def_size']+12)==8)
    _,c,s=context(index);r.u32(r.addr('sCCVisualFiles'),main)
    for flag in (2,3,4,5,1):
        r.u32(r.FP+r.layout['flags']+8,flag);r.call('cc_ftKirbySpecialHiUpdateEffect',r.GOBJ)
        assert bool(r.u32(s+layout['effect']))==(flag!=1)
        assert r.u32(r.FP+r.layout['flags']+8)==0
    # A held orb grows through all eight source sizes, remains cosmetic through
    # the release startup, then disappears at the source projectile handoff.
    d,c,s=context(24)
    neutral=r.addr('sFTCharBuilderNeutralStates')
    r.write(neutral,bytes(68));r.u32(neutral,r.FP);r.u32(neutral+12,14)
    resource=0x8024B000
    shot=resource+r.u32(r.addr('ccwp_dWPSamusChargeShotWeaponDesc')+12)
    r.write(shot,bytes(0x100));r.u32(shot+layout['shot_dl'],0x80249000)
    r.u32(r.addr('sCCNeutralFiles')+16,resource)
    for level in range(8):
        r.u32(neutral+20,level);tick(c,level)
        obj=r.u32(s+layout['charge']);assert obj
        dobj=r.u32(obj+r.layout['obj'])
        expected=(150,230,280,340,410,490,600,700)[level]/30
        assert abs(r.f32(dobj+r.layout['scale'])-expected)<.005,(level,r.f32(dobj+r.layout['scale']),expected)
    r.u32(neutral+12,16);r.u32(neutral+24,7)
    release=definitions+26*layout['def_size']
    assert r.call('ccVisualPreserve',r.FP,r.u32(release))==0x804
    r.u32(r.addr('sFTCharBuilderNeutralStartingOwner'),r.FP)
    r.u32(c,0) # native SetStatus clears the old clock during body bootstrap
    r.call('ccVisualTick',r.GOBJ)
    r.call('ccStatusChanging',r.GOBJ,10)
    assert r.u32(s+layout['charge']) and r.u32(r.FP+layout['loop'])
    r.u32(c,r.FP)
    r.u32(r.addr('sFTCharBuilderNeutralStartingOwner'),0)
    r.u32(c+r.clock_move,r.u32(release));tick(c,9)
    assert r.u32(s+layout['charge'])
    r.u32(neutral+48,1);tick(c,10) # fired
    assert not r.u32(s+layout['charge']) and not r.u32(r.FP+layout['loop'])
    r.u32(r.addr('sCCNeutralFiles')+16,0)
    # All six real private constructors execute with native descriptor
    # allocation fixtures and semantic attachment selection on every body.
    fx_cases=(('CaptainFalconPunch',7,6),('CaptainFalconKick',7,109),
              ('KirbyCutterUp',8,88),('KirbyCutterDown',8,88),('KirbyCutterDraw',8,88),('KirbyCutterTrail',8,88))
    constructors=0
    for name,donor,_ in fx_cases:
        index=next(i for i in range(layout['defs']) if r.u32(definitions+i*layout['def_size']+12)==donor)
        for body in range(12):
            if body==donor:continue
            _,c,s=context(index,body)
            g=r.call('ccfx'+name,r.GOBJ);assert g
            r.u32(r.u32(g+0x84)+layout['update'],r.addr('ccVisualEffectUpdate'));r.u32(s+layout['effect'],g)
            r.call('ccStatusChanging',r.GOBJ,18);assert g in stopped
            constructors+=1;counter=0
    # Orphaned effects may reuse an address: never dereference or eject a GObj
    # outside its native link list/owner tag, and never hide a replacement body.
    index=next(i for i,_,p,_ in props if r.u32(p+12))
    d,c,s=context(index);p=r.u32(d+16);sample=r.u32(p)
    first=next(i for i in range(r.u32(r.u32(d+4)+20)) if r.u32(sample+i*40+36))
    tick(c,first);g=r.u32(s+layout['model']);assert g
    r.u32(g+0x84,0x80246000);r.write(0x80246000,bytes(0x80))
    r.u32(r.FP+r.player_num,1)
    before=len(stopped);r.call('ccReset');assert len(stopped)==before
    r.u32(links+24,0);r.u32(links+12,0)
    # Four live ports keep distinct models/visibility owners, then the native
    # scene reset releases every object and restores every body once.
    r.call('ccReset');counter=0
    previous=(r.FP,r.GOBJ,r.JOINTS);players=[]
    for port in range(4):
        r.FP=0x80260000+port*0x8000;r.GOBJ=r.FP+0x2000;r.JOINTS=r.FP+0x4000
        r.setup(0,0,port)
        r.u32(r.FP+layout['fighter'],r.GOBJ)
        r.u32(r.GOBJ+layout['next'],r.u32(links+12));r.u32(links+12,r.GOBJ)
        r.u32(r.FP+0x24,0xDC);r.u32(r.FP+0x28,300)
        c=r.addr('sFTCustomMoveClocks')+port*r.clock_size;move=r.u32(d)
        r.write(c,struct.pack('>6I2fIIf',r.FP,0,move,0xDC,300,r.u32(move+8),first,first,r.u32(move+12),0,1))
        r.call('ccVisualStart',r.FP,first);r.call('ccVisualTick',r.GOBJ)
        s=state+port*layout['state_size'];assert r.u32(s+layout['hidden'])
        players.append((r.JOINTS,r.u32(s+layout['model'])))
    assert len({g for _,g in players})==4
    r.call('ccReset');assert not r.u32(links+24)
    for joints,g in players:
        assert g in stopped
        assert all(not r.read(joints+i*0x100+layout['dobj_flags'],1)[0]&layout['hidden_mask'] for i in range(4,37))
    r.FP,r.GOBJ,r.JOINTS=previous;r.u32(links+12,0)
    assert r.u32(r.addr('gFTCustomMoveValidationFailures'))==0
    print(f'PASS: {len(props)} source prop tables, {placements} linked-MIPS placements, {constructors} attached constructors, Cutter/Falcon flag windows, eight charge sizes/release handoff, source audio clocks and interruption/death/four-port reset/stale-owner cleanup (allocation/audio fixtures).')
