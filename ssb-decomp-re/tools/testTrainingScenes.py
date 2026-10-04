#!/usr/bin/env python3
"""Optional Linux Mupen64Plus ROM smoke test: real menus/loaders, null rendering.

Requires libmupen64plus2, libmupen64plus-dev and mupen64plus-rsp-hle.
Uses an isolated configuration/save directory; never touches a running emulator.
See docs/neutral-specials.md. The native API is documented at
https://mupen64plus.org/wiki/index.php/Mupen64Plus_v2.0_Core_Front-End
"""
import argparse, ctypes as C, threading, time, subprocess, struct
from pathlib import Path
from elfData import read_elf
from auditNormalMoves import enum_values
from hostFighterHeaders import prepare
from generateSpecialTiming import path_catalog
from auditNormalMoves import ROSTER,SLOTS
from customMoveCatalog import MOTIONS,extra_ids

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--core',default='/usr/lib/x86_64-linux-gnu/libmupen64plus.so.2')
parser.add_argument('--rsp',default='/usr/lib/x86_64-linux-gnu/mupen64plus/mupen64plus-rsp-hle.so')
parser.add_argument('--headers',default='/usr/include/mupen64plus')
parser.add_argument('--data',default='/usr/share/mupen64plus')
parser.add_argument('--four-mb',action='store_true')
parser.add_argument('--cases',type=int,default=12)
parser.add_argument('--first-choice',type=int,default=0)
parser.add_argument('--specials',action='store_true',help='Exercise borrowed DK Down B and Ness Up B instead of neutral actions')
parser.add_argument('--path-donor',type=int,choices=(0,2,4,7,11),help='Exercise donor special paths, movement, or Ness steering/self-contact')
parser.add_argument('--egg-lay',action='store_true',help='Test Egg Lay on every body instead of cycling neutral choices')
parser.add_argument('--mario-animations',action='store_true',help='Check four Mario donor catalogs using real attack inputs and RAM poses')
args=parser.parse_args()
if not 0<=args.first_choice<12 or not 1<=args.cases<=12-args.first_choice:
    parser.error('Choose a contiguous range within the twelve neutral choices.')
build=ROOT/'build/scene-smoke';build.mkdir(parents=True,exist_ok=True)
layout_headers=prepare(ROOT,build/'layout-headers')
subprocess.run(['clang','--target=mips-unknown-none','-c','-EB','-mabi=32','-march=mips2','-ffreestanding','-O1','-I'+str(layout_headers),'-I'+str(ROOT/'include'),
                '-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',
                str(ROOT/'tools/emulator/layout.c'),'-o',str(build/'layout.o')],check=True)
data,sections,layout_symbols=read_elf(build/'layout.o','>')
value,length,index=layout_symbols['sSceneSmokeLayout'];start=sections[index][4]+value-sections[index][3]
layout=struct.unpack_from('>'+str(length//4)+'I',data,start)
value,length,index=layout_symbols['sSceneSmokeFighterLayout'];start=sections[index][4]+value-sections[index][3]
fighter_layout=struct.unpack_from('>'+str(length//4)+'I',data,start)
value,length,index=layout_symbols['sSceneSmokeSpecialLayout'];start=sections[index][4]+value-sections[index][3]
joints_off,lr_off,thunder_off,delay_off,obj_off,user_off,position_off,weapon_vel_off,battle_status_off=struct.unpack_from('>9I',data,start)
value,length,index=layout_symbols['sSceneSmokeAnimationLayout'];start=sections[index][4]+value-sections[index][3]
rotation_off,scale_off=struct.unpack_from('>2I',data,start)
ftsize,kind_off,port_off,gobj_off,status_off,motion_off,attack_off,attack_size,attack_state_off,passive_off,passive_size,generation_off,physics_off,vel_air_off,hitlag_off,gobj_frame_off=fighter_layout
slot_size,neutral_field,players_field,player_size,pkind_field,fkind_field,man_field,cpu_field,reset_field,stage_field=layout
for name in ('input','video'):
    subprocess.run(['gcc','-shared','-fPIC','-I'+args.headers,str(ROOT/'tools/emulator'/f'{name}.c'),
                    '-o',str(build/f'{name}.so')],check=True)
core=C.CDLL(args.core)
core.CoreStartup.argtypes=[C.c_int,C.c_char_p,C.c_char_p,C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p]
core.CoreDoCommand.argtypes=[C.c_int,C.c_int,C.c_void_p]
core.CoreAttachPlugin.argtypes=[C.c_int,C.c_void_p]
core.ConfigOpenSection.argtypes=[C.c_char_p,C.POINTER(C.c_void_p)]
core.ConfigSetParameter.argtypes=[C.c_void_p,C.c_char_p,C.c_int,C.c_void_p]
core.DebugMemGetPointer.restype=core.DebugGetCPUDataPtr.restype=C.c_void_p
@C.CFUNCTYPE(None,C.c_void_p,C.c_int,C.c_char_p)
def log(ctx,level,text):
    if level==1:print('CORE:',text.decode(),flush=True)
def check(code):assert code==0,('Emulator API error',code)
check(core.CoreStartup(0x20001,str(build/('config-4mb' if args.four_mb else 'config-8mb')).encode(),
                       str(Path(args.data)).encode(),None,log,None,None))
section=C.c_void_p();check(core.ConfigOpenSection(b'Core',C.byref(section)))
for name,typ,value in ((b'R4300Emulator',1,2),(b'DisableExtraMem',3,int(args.four_mb)),(b'OnScreenDisplay',3,0)):
    check(core.ConfigSetParameter(section,name,typ,C.byref(C.c_int(value))))
rom=C.create_string_buffer((ROOT/'build/smashbrothers.us.z64').read_bytes())
check(core.CoreDoCommand(1,len(rom)-1,rom))
plugins=[]
for typ,path in ((2,build/'video.so'),(3,None),(4,build/'input.so'),(1,Path(args.rsp))):
    if path is None:check(core.CoreAttachPlugin(typ,None));continue
    plugin=C.CDLL(str(path));plugin.PluginStartup.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p]
    check(plugin.PluginStartup(core._handle,None,log));check(core.CoreAttachPlugin(typ,plugin._handle))
    plugins.append(plugin)
keys=plugins[1].LabKeys
_,_,symbols=read_elf(ROOT/'build/smashbrothers.us.elf','>')
def addr(name):return symbols[name][0]
scene=addr('gSCManagerSceneData');heap=addr('gSYTaskmanGeneralHeap')
ram=core.DebugMemGetPointer(1)
def u8(a):return C.c_uint8.from_address(ram+((a&0x7fffff)^3)).value
def u32(a):return C.c_uint32.from_address(ram+(a&0x7fffff)).value
def w8(a,v):C.c_uint8.from_address(ram+((a&0x7fffff)^3)).value=v
def w32(a,v):C.c_uint32.from_address(ram+(a&0x7fffff)).value=v
def f32(a):return C.c_float.from_address(ram+(a&0x7fffff)).value
def wf32(a,v):C.c_float.from_address(ram+(a&0x7fffff)).value=v
def fighter():return u32(addr('sFTManagerStructsAllocBuf'))
def head():return u32(fighter()+thunder_off)
def weapon_velocity():
    wp=u32(head()+user_off)
    return tuple(f32(wp+weapon_vel_off+j) for j in (0,4))
def diagnostic():
    fault=u32(addr('__osFaultedThread'))
    context=[hex(u32(fault+j)) for j in (0x118,0x11c,0x120,0x124,0x128)] if fault else []
    return dict(scene=u8(scene),pc=hex(C.c_uint32.from_address(core.DebugGetCPUDataPtr(1)).value),fault=context,
                heap=[hex(u32(heap+j)) for j in (4,8,12)],updates=u32(addr('dSYTaskmanUpdateCount')))
def wait(predicate,label,seconds=15):
    deadline=time.monotonic()+seconds
    while not predicate():
        if time.monotonic()>deadline:raise AssertionError((label,diagnostic()))
        time.sleep(.01)
def frames(count=12):
    initial=u32(addr('dSYTaskmanUpdateCount'))
    wait(lambda:u32(addr('dSYTaskmanUpdateCount'))>=initial+count,'Game stopped updating')
def pulse(value):
    keys(value);time.sleep(.07);keys(0);time.sleep(.07)
def heap_ok():
    start,end,ptr=(u32(heap+j) for j in (4,8,12))
    assert start==0x80400000 and end==0x80800000 and start<=ptr<=end,diagnostic()
    return end-ptr
trace=[];travel_trace=[];last_trace=None
animation_seen=set();animation_samples=0;animation_errors=[]
motion_ids=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
animation_variants={motion_ids['nFTCommonMotion'+m]:i for i,m in enumerate(MOTIONS[:29])}
animation_variants[extra_ids('Mario')[0]]=29
animation_rows=[next(i for i,family in enumerate(SLOTS.values()) if m in family) for m in MOTIONS[:24]]+list(range(8,13))+[0]
@C.CFUNCTYPE(None,C.c_uint)
def frame_callback(frame):
    global last_trace,animation_samples
    if args.mario_animations:
        if u8(scene)!=54:return
        fp=fighter()
        if not 0x80400000<=fp<0x80800000:return
        variant=animation_variants.get(u32(fp+motion_off))
        if variant is None:return
        preset=u8(addr('gSCManagerCharBuilderPlayerSlots'))
        if preset>=4:return
        slot=addr('gSCManagerCharBuilderSlots')+preset*slot_size
        donor=u8(slot+2+animation_rows[variant])
        if donor>=12:return
        clip=addr('sFTCustomAnimationPackedClips')+(donor*33+variant)*8
        pointer,count=u32(clip),u32(clip+4)
        if not pointer or not count:return
        source_frame=f32(u32(fp+gobj_off)+gobj_frame_off)
        # Normal animation frames are supplied by the donor clock; -1 is its
        # native completion sentinel, after applying the final pose sample.
        sample=pointer+(count-1 if source_frame<0 else min(int(source_frame),count-1))*150
        def s16(a):
            value=(u8(a)<<8)|u8(a+1)
            return value-65536 if value&32768 else value
        # Native ground slope contour may adjust leg chains after pose playback.
        # Check all limbs in aerials, and the root/torso/arms/head on ground.
        for joint in range(24 if 19<=variant<=23 else 14):
            obj=u32(fp+joints_off+(joint+4)*4)
            if not obj:return
            for channel in range(3):
                expected=s16(sample+(joint*3+channel)*2)/4096
                actual=f32(obj+rotation_off+channel*4)
                if abs(expected-actual)>0.00001 and len(animation_errors)<10:
                    animation_errors.append((donor,variant,source_frame,joint+4,channel,expected,actual))
        animation_seen.add((donor,variant));animation_samples+=1
        return
    if (not args.specials and args.path_donor is None) or u8(scene)!=54:return
    fp=u32(addr('sFTManagerStructsAllocBuf'))
    if not 0x80400000<=fp<0x80800000:return
    if u8(fp+port_off)!=0:return
    gobj=u32(fp+gobj_off)
    if not 0x80400000<=gobj<0x80800000:return
    source_frame=C.c_float.from_address(ram+((gobj+gobj_frame_off)&0x7fffff)).value
    mask=sum(1<<i for i in range(4) if u32(fp+attack_off+i*attack_size+attack_state_off))
    record=(u32(fp+status_off),u32(fp+motion_off),int(source_frame),mask)
    if args.path_donor is not None:
        travel_trace.append((record,tuple(f32(fp+physics_off+vel_air_off+j) for j in (0,4))))
    if record!=last_trace:trace.append(record);last_trace=record
check(core.CoreDoCommand(15,0,C.cast(frame_callback,C.c_void_p)))
thread=threading.Thread(target=lambda:check(core.CoreDoCommand(5,0,None)),daemon=True)
thread.start()
try:
    wait(lambda:u32(0x80000318)==(0x400000 if args.four_mb else 0x800000),'Boot memory size')
    time.sleep(2)
    check(core.CoreDoCommand(17,5,C.byref(C.c_int(0)))) # Run menus uncapped; limit speed during frame-by-frame gameplay checks.
    # Skip the intro only. From Options onward, use the actual button handlers.
    w8(scene+1,u8(scene));w8(scene,57);w32(addr('sSYTaskmanStatus'),1)
    wait(lambda:u8(scene)==57 and u32(addr('sMNOptionTotalTimeTics'))>30,'Options load')
    w32(addr('sMNOptionOption'),3);pulse(0x80)
    wait(lambda:u32(addr('sMNOptionBuilderMode'))==1,'Lab hub')
    minima=[]
    for case in (range(4) if args.mario_animations else range(args.first_choice,args.first_choice+args.cases)):
        choice=0 if args.path_donor is not None else 11 if args.egg_lay else case
        if u32(addr('sMNOptionBuilderMode'))==2:pulse(0x40)
        preset=case%4;body=(case+2)%12
        if args.mario_animations:body=0
        w32(addr('sMNOptionBuilderSlot'),preset)
        slot=addr('gSCManagerCharBuilderSlots')+preset*slot_size
        w8(slot,1);w8(slot+1,body)
        for i in range(16):w8(slot+2+i,body)
        if args.mario_animations:
            for i in range(13):w8(slot+2+i,(1,2,4,7)[case])
        w8(slot+18,11 if args.specials else args.path_donor if args.path_donor in (2,11) else body)
        w8(slot+19,2 if args.specials else args.path_donor if args.path_donor in (0,4,7) else body)
        w8(slot+neutral_field,0 if args.path_donor is not None else choice)
        pulse(0x80);wait(lambda:u32(addr('sMNOptionBuilderMode'))==2,'Build editor')
        w32(addr('sMNOptionBuilderEntry'),23);pulse(0x80)
        if args.four_mb:
            frames(90);assert u8(scene)==57 and u32(addr('sMNOptionBuilderMode'))==2,diagnostic()
            print('PASS: 4 MB Test in Training stays in the editor, without a heap overflow.',flush=True);break
        wait(lambda:u8(scene)==18 and u32(addr('sMNPlayers1PTrainingTotalTimeTics'))>70,'Training character select')
        frames(30);minima.append(heap_ok());pulse(0x10)
        wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'Training stage select')
        pulse(0x80);wait(lambda:u8(scene)==54 and u32(addr('dSYTaskmanUpdateCount'))>180,'Training match load')
        frames(30);minima.append(heap_ok())
        if args.mario_animations:
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            animation_seen.clear();animation_errors.clear();animation_samples=0
            def act(value,ticks=3,recovery=90):
                keys(value);frames(ticks);keys(0);frames(recovery)
            def stick(x=0,y=0):return ((x&255)<<16)|((y&255)<<24)
            act(0x80);act(0x80) # Jabs.
            for x,y in ((35,0),(0,35),(0,-35)):
                keys(stick(x,y));frames(5);act(stick(x,y)|0x80)
            for x,y in ((80,0),(0,80),(0,-80)):act(stick(x,y)|0x80)
            keys(stick(80));frames(12);act(stick(80)|0x80)
            for x,y in ((0,0),(50,0),(-50,0),(0,50),(0,-50)):
                act(0x0800,3,10);act(stick(x,y)|0x80,3,100)
            assert not animation_errors,('Mario ROM pose mismatch',animation_errors)
            assert animation_samples>=30 and len(animation_seen)>=7,('Mario attack coverage',animation_samples,animation_seen)
            assert u32(addr('gFTCustomAnimationValidationFailures'))==0
            print(f'PASS: Mario donor {(1,2,4,7)[case]}, {animation_samples} live compact poses, variants {sorted(v for _,v in animation_seen)}.',flush=True)
        elif args.path_donor is not None:
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            donor=args.path_donor;name=ROSTER[donor]
            common=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonStatus')
            header=(ROOT/'src/ft/ftchar'/('ft'+name.lower())/('ft'+name.lower()+'.h')).read_text()
            statuses=enum_values(header.replace('nFTCommonStatusSpecialStart',str(common['nFTCommonStatusSpecialStart'])),'ft'+name+'Status')
            paths={statuses[c['phase'].replace('Motion','Status')]:c for c in path_catalog() if c['donor']==donor}
            def check_paths():
                seen=set();hits=0;previous_status=None;resume_frame=-1;resumed_masks=()
                for status,motion,frame,mask in trace:
                    if status not in paths:continue
                    c=paths[status];seen.add(status)
                    if status!=previous_status:
                        resume_frame=frame if frame>1 else -1;wall=0;events={};resumed_masks=[]
                        for op,a in c['events']:
                            if op=='ftMotionCommandWait':wall+=int(a[0],0)
                            elif op=='ftMotionCommandWaitAsync':wall=max(wall,int(a[0],0))
                            elif 'AttackColl' in op and wall>resume_frame:events.setdefault(wall,[]).append((op,a))
                        active=0
                        for tick in range(len(c['frames'])):
                            for op,a in events.get(tick,()):
                                if 'MakeAttackColl' in op:active|=1<<int(a[0],0)
                                elif op=='ftMotionCommandClearAttackCollAll':active=0
                                elif op=='ftMotionCommandClearAttackCollID':active&=~(1<<int(a[0],0))
                            resumed_masks.append(active)
                        previous_status=status
                    if body==donor and name=='Ness' and c['phase'].endswith('HiJibaku'):
                        hits+=bool(mask);continue # Native nine-frame pose clock; action timer is separate.
                    if 0<=frame<len(c['frames']):
                        expected=c['frames'][frame][0]
                        # Native ground/air switching clears attacks and fast-forwards
                        # earlier creations. Each attack ID resumes when created again.
                        if donor in (0,4) and resume_frame>=0:expected=resumed_masks[frame]
                        assert mask==expected,(body,c['phase'],frame,'mask',mask,expected,trace)
                        hits+=bool(mask)
                assert seen and hits,(body,'No donor hitbox phase',seen,trace)
                assert trace[-1][0] not in paths,(body,'Special recovery',trace[-1])
                return seen
            trace.clear();travel_trace.clear();last_trace=None
            if donor==11:
                keys(0x40 | (80<<24));frames(3);keys(0)
                wait(lambda:u32(fighter()+status_off) in (statuses['nFTNessStatusSpecialHiHold'],statuses['nFTNessStatusSpecialAirHiHold']),'PK Thunder hold')
                keys(80<<16);frames(8);right=weapon_velocity()
                keys(176<<16);frames(8);left=weapon_velocity();keys(0)
                assert max(abs(a-b) for a,b in zip(right,left))>1,(body,'PK Thunder steering',right,left)
                wait(lambda:u32(fighter()+delay_off)==0,'PK Thunder self-contact delay')
                check(core.CoreDoCommand(7,0,None));time.sleep(.03)
                fp=fighter();gobj=u32(fp+gobj_off);top=u32(gobj+obj_off);thunder=head()
                assert thunder,(body,'Missing controlled PK Thunder head')
                pos=u32(thunder+obj_off)+position_off;root=top+position_off
                wf32(pos,f32(root)-100*f32(fp+lr_off));wf32(pos+4,f32(root+4)+50);wf32(pos+8,0)
                check(core.CoreDoCommand(8,0,None));frames(240)
                seen=check_paths()
                assert statuses['nFTNessStatusSpecialAirHiJibaku'] in seen or statuses['nFTNessStatusSpecialHiJibaku'] in seen,(body,'PK Thunder launch',seen,trace)
                print('PASS: Ness Up B on body',body,'steers, controlled self-contact launches and recovers with source collision timing.',flush=True)
            else:
                direction=80 if donor==2 else 176
                keys(0x40 | (direction<<24));frames(3);keys(0);frames(210)
                seen=check_paths()
                if donor==7:assert max(abs(v[0]) for r,v in travel_trace if r[0] in paths)>50,(body,'Falcon Kick travel')
                print('PASS:',name,'special on body',body,'ground start, source hit masks and recovery.',flush=True)
                trace.clear();travel_trace.clear();last_trace=None
                keys(0x0800);frames(3);keys(0);frames(8)
                keys(0x40 | (direction<<24));frames(3);keys(0)
                if donor in (0,4):
                    frames(12);before=f32(fighter()+physics_off+vel_air_off+4)
                    keys(0x40);frames(3);keys(0)
                    after=f32(fighter()+physics_off+vel_air_off+4)
                    assert after>before+5,(body,'Tornado B-tap rise',before,after)
                frames(240)
                seen=check_paths()
                assert any('SpecialAir' in paths[status]['phase'] for status in seen),(body,'Aerial special phase',seen,trace)
                print('PASS:',name,'special on body',body,'aerial start, source hit masks and recovery.',flush=True)
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(0))))
        elif args.specials:
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            trace.clear();last_trace=None
            pulse(0x40 | (176<<24));frames(200) # B + down, analog -80.
            hits={(r[2],r[3]) for r in trace if r[0]==233 and r[3]}
            assert hits=={(16,15),(17,15),(26,15),(27,15)},(body,'DK phase hit windows',hits,trace)
            if body!=2:
                wait_motion=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')['nFTCommonMotionWait']
                assert all(r[1]==wait_motion for r in trace if 232<=r[0]<=234),(body,'Body special replay',trace)
            print('PASS: DK Down B on body',body,'hits at phase frames 16-17/26-27; recovered.',flush=True)
            trace.clear();last_trace=None
            keys(0x40 | (176<<24));frames(4);keys(0);frames(8)
            keys(0x40 | (176<<24));frames(3);keys(0);frames(120)
            repeated=[r[2] for r in trace if r[0]==233 and r[3]]
            assert repeated==[16,17,26,27]*2,(body,'Repeated DK cycle',repeated)
            print('PASS: repeated DK cycle on body',body,'has both original slap windows twice.',flush=True)
            trace.clear();last_trace=None
            pulse(0x40 | (80<<24));frames(400) # B + up, analog +80.
            phases={r[0] for r in trace}
            assert {228,229,230}<=phases,(body,'Ness start/hold/end',phases)
            assert not 228<=trace[-1][0]<=236,(body,'Ness recovery',trace[-1])
            print('PASS: Ness Up B on body',body,'start -> hold/projectile expiry -> end/recovery, no freeze.',flush=True)
        else:pulse(0x40);frames(200) # Actual B input and recovery/charging.
        if args.path_donor is None and not args.mario_animations:
            pulse(0x20);frames(30) # Store a charge where supported.
            pulse(0x40);frames(120)
        if args.path_donor is not None or args.mario_animations:
            paused=enum_values((ROOT/'src/sc/scdef.h').read_text(),'SCBattleGameStatus')['nSCBattleGameStatusPause']
            # Native Training ignores Start during KO/respawn. Wait for a legal
            # pause instead of firing Exit at an unopened menu.
            for attempt in range(4):
                keys(0x10);frames(3);keys(0);frames(12)
                if u8(u32(addr('gSCManagerBattleState'))+battle_status_off)==paused:break
                frames(120)
            assert u8(u32(addr('gSCManagerBattleState'))+battle_status_off)==paused,('Training pause',diagnostic())
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(0))))
        else:
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(0))))
            pulse(0x10);frames(12) # Pause, then native Exit button handler.
        w32(addr('sSC1PTrainingModeMenu'),5);pulse(0x80)
        wait(lambda:u8(scene)==57 and u32(addr('sMNOptionBuilderMode'))==2,'Return to editor')
        assert u32(addr('sMNOptionBuilderSlot'))==preset and u32(addr('sMNOptionBuilderEntry'))==23
        action_label='Mario normal poses' if args.mario_animations else 'donor special' if args.path_donor is not None else 'B/store/B'
        print(f'PASS: body {body}, neutral {choice}, preset {preset}: Test -> CSS -> stage -> Training -> {action_label} -> same editor.',flush=True)
    if not args.four_mb:
        print('PASS: Training heap headroom at least',min(minima),'bytes.',flush=True)
        pulse(0x40);wait(lambda:u32(addr('sMNOptionBuilderMode'))==1,'Lab hub for VS')
        transfer=addr('gSCManagerTransferBattleState')
        for player,body in enumerate((0,2,8,9)):
            if args.mario_animations:body=0
            w8(addr('gSCManagerCharBuilderPlayerSlots')+player,player)
            slot=addr('gSCManagerCharBuilderSlots')+player*slot_size
            w8(slot,1);w8(slot+1,body)
            for attack in range(16):w8(slot+2+attack,body)
            if args.mario_animations:
                for attack in range(13):w8(slot+2+attack,(1,2,4,7)[player])
            w8(slot+18,body);w8(slot+19,body);w8(slot+neutral_field,(9,10,11,6)[player])
            record=transfer+players_field+player*player_size
            w8(record+pkind_field,0 if player==0 else 1);w8(record+fkind_field,body)
        w8(transfer+man_field,1);w8(transfer+cpu_field,3);w8(transfer+reset_field,0);w8(transfer+stage_field,1)
        w32(addr('sMNOptionBuilderSlot'),8);pulse(0x80)
        wait(lambda:u8(scene)==16 and u32(addr('sMNPlayersVSTotalTimeTics'))>75,'Four-slot VS select')
        frames(30);heap_ok();pulse(0x10)
        wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'VS stage select')
        pulse(0x80);wait(lambda:u8(scene)==22 and u32(addr('dSYTaskmanUpdateCount'))>240,'Four-slot VS battle')
        frames(180);heap_ok();pulse(0x40);frames(160)
        print('PASS: four assigned builds, human/three CPUs: Play VS -> CSS -> stage -> battle/B, upper-bank heap in bounds.',flush=True)
finally:
    keys(0);core.CoreDoCommand(6,0,None);thread.join(timeout=3)
