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
from auditNormalMoves import enum_values,us_text
from hostFighterHeaders import prepare
from generateSpecialTiming import path_catalog, direct_landing_duration
from auditNormalMoves import ROSTER,SLOTS
from customMoveCatalog import MOTIONS,extra_ids

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--core',default='/usr/lib/x86_64-linux-gnu/libmupen64plus.so.2')
parser.add_argument('--rsp',default='/usr/lib/x86_64-linux-gnu/mupen64plus/mupen64plus-rsp-hle.so')
parser.add_argument('--headers',default='/usr/include/mupen64plus')
parser.add_argument('--data',default='/usr/share/mupen64plus')
parser.add_argument('--rom',type=Path,help='Check an identical copy of the current build, including a downloaded ROM')
parser.add_argument('--boot',action='store_true',help='Check uninterrupted cold boot, the full intro, title and actual Start input')
parser.add_argument('--four-mb',action='store_true')
parser.add_argument('--cases',type=int,default=12)
parser.add_argument('--first-choice',type=int,default=0)
parser.add_argument('--specials',action='store_true',help='Exercise borrowed DK Down B and Ness Up B instead of neutral actions')
parser.add_argument('--path-donor',type=int,choices=(0,2,4,7,11),help='Exercise donor special paths, movement, or Ness steering/self-contact')
parser.add_argument('--superjump',type=int,choices=(0,4),help='Check Mario/Luigi Up B hit fields, source paths, rise, helpless landing and interrupts')
parser.add_argument('--direct-special',type=int,choices=(3,5,10),help='Check Samus Screw Attack, Link Spin Attack or Jigglypuff Rest gameplay on each body')
parser.add_argument('--egg-lay',action='store_true',help='Test Egg Lay on every body instead of cycling neutral choices')
parser.add_argument('--mario-animations',action='store_true',help='Check four Mario donor catalogs using real attack inputs and RAM poses')
parser.add_argument('--roster-animations',action='store_true',help='Check every donor/body pair, live poses, recovery and Training return')
parser.add_argument('--mechanic',type=int,choices=(1,3,5,6,7,8,9,10,11),help='Exercise remaining special mechanics across bodies')
parser.add_argument('--mechanic-kind',choices=('hi','lw'),default='hi')
parser.add_argument('--thunder-contact',action='store_true',help='Place the live native Thunder head in its owner-contact box to check the hit branch')
parser.add_argument('--falcon-contact',action='store_true',help='Place the CPU in the live Falcon Dive catch volume to check native capture/throw')
args=parser.parse_args()
if args.mechanic is not None:args.superjump=args.mechanic
if args.direct_special is not None:args.superjump=args.direct_special
common_statuses=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonStatus')
link_statuses=enum_values((ROOT/'src/ft/ftchar/ftlink/ftlink.h').read_text().replace('nFTCommonStatusSpecialStart',str(common_statuses['nFTCommonStatusSpecialStart'])),'ftLinkStatus')
nFTLinkHi,nFTLinkHiEnd,nFTLinkAirHi=(link_statuses['nFTLinkStatus'+phase] for phase in ('SpecialHi','SpecialHiEnd','SpecialAirHi'))
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
value,length,index=layout_symbols['sSceneSmokeSuperJumpLayout'];start=sections[index][4]+value-sections[index][3]
hitstatus_off,jumps_off,attr_off,jumps_max_off,damage_off,radius_off,angle_off,kbs_off,kbw_off,kbb_off,center_off=struct.unpack_from('>11I',data,start)
value,length,index=layout_symbols['sSceneSmokeSpinLayout'];start=sections[index][4]+value-sections[index][3]
spin_off,wp_kind_off,wp_state_off,wp_radius_off,wp_life_off,wp_damage_off=struct.unpack_from('>6I',data,start)
value,length,index=layout_symbols['sSceneSmokeAnimationLayout'];start=sections[index][4]+value-sections[index][3]
rotation_off,scale_off=struct.unpack_from('>2I',data,start)
value,length,index=layout_symbols['sSceneSmokeMechanicLayout'];start=sections[index][4]+value-sections[index][3]
link_next_off,wp_owner_off,item_off,it_kind_off,it_owner_off,link_bomb_kind,fox_angle_off,percent_off,ga_off,air_kind=struct.unpack_from('>10I',data,start)
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
rom_bytes=(args.rom or ROOT/'build/smashbrothers.us.z64').read_bytes()
if args.rom:assert rom_bytes==(ROOT/'build/smashbrothers.us.z64').read_bytes(),'ROM copy differs from current ELF/build'
rom=C.create_string_buffer(rom_bytes)
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
def s32(a):return C.c_int32.from_address(ram+(a&0x7fffff)).value
def w8(a,v):C.c_uint8.from_address(ram+((a&0x7fffff)^3)).value=v
def w32(a,v):C.c_uint32.from_address(ram+(a&0x7fffff)).value=v
def f32(a):return C.c_float.from_address(ram+(a&0x7fffff)).value
def wf32(a,v):C.c_float.from_address(ram+(a&0x7fffff)).value=v
def fighter():return u32(addr('sFTManagerStructsAllocBuf'))
def opponent():
    node=u32(addr('gGCCommonLinks')+3*4)
    for _ in range(4):
        if not 0x80000000<=node<0x80800000:break
        fp=u32(node+user_off)
        if 0x80400000<=fp<0x80800000 and u8(fp+port_off)!=0:return fp
        node=u32(node+link_next_off)
    return 0
def head():return u32(fighter()+thunder_off)
def weapon_velocity():
    wp=u32(head()+user_off)
    return tuple(f32(wp+weapon_vel_off+j) for j in (0,4))
def diagnostic():
    fault=u32(addr('__osFaultedThread'))
    context=[hex(u32(fault+j)) for j in (0x118,0x11c,0x120,0x124,0x128)] if fault else []
    return dict(scene=u8(scene),pc=hex(C.c_uint32.from_address(core.DebugGetCPUDataPtr(1)).value),fault=context,
                fault_registers=[hex(u32(fault+j)) for j in range(0xe0,0x118,4)] if fault else [],
                fighter=[hex(u32(fighter()+j)) for j in (status_off,motion_off,spin_off,generation_off)] if fault else [],
                heap=[hex(u32(heap+j)) for j in (4,8,12)],updates=u32(addr('dSYTaskmanUpdateCount')))
def wait(predicate,label,seconds=15):
    deadline=time.monotonic()+seconds
    while not predicate():
        if time.monotonic()>deadline:raise AssertionError((label,diagnostic()))
        time.sleep(.001 if args.mechanic is not None else .01)
def frames(count=12):
    initial=u32(addr('dSYTaskmanUpdateCount'))
    wait(lambda:u32(addr('dSYTaskmanUpdateCount'))>=initial+count,'Game stopped updating')
def pulse(value):
    keys(value);time.sleep(.07);keys(0);time.sleep(.07)
def heap_ok():
    start,end,ptr=(u32(heap+j) for j in (4,8,12))
    assert start==0x80400000 and end==0x80800000 and start<=ptr<=end,diagnostic()
    return end-ptr
trace=[];travel_trace=[];superjump_trace=[];spin_trace=[];last_trace=None
weapon_seen=set();item_seen=set();pitch_trace=[]
thunder_contact_done=False
falcon_contact_done=False
falcon_flight_statuses=set()
animation_seen=set();animation_samples=0;animation_errors=[]
motion_ids=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
animation_variants={motion_ids['nFTCommonMotion'+m]:i for i,m in enumerate(MOTIONS[:29])}
animation_variants[extra_ids('Mario')[0]]=29
animation_rows=[next(i for i,family in enumerate(SLOTS.values()) if m in family) for m in MOTIONS[:24]]+list(range(8,13))+[0]
if args.mario_animations or args.roster_animations:
    from sharedAnimation import catalog as pose_catalog,body_rig,qmul,quaternion,rotation,qmatrix
    pose_cases,pose_rows=pose_catalog()
    pose_data=(ROOT/'build/shared-animation-poses.bin').read_bytes()
    pose_offsets={};cursor=0
    for case_id,case in enumerate(pose_cases):
        for body_id,body_name in enumerate(ROSTER):
            pose_offsets[case_id,body_id]=cursor
            cursor+=case['frames']*(len(body_rig(body_name))*16+12)
    assert cursor==len(pose_data),'Run tools/testNativeAnimation.py for current runtime pose references.'
    body_variants=[]
    for name in ROSTER:
        variants=dict(animation_variants)
        for variant,motion in enumerate(extra_ids(name),29):
            if motion>=0:variants[motion]=variant
        body_variants.append(variants)
@C.CFUNCTYPE(None,C.c_uint)
def frame_callback(frame):
    global last_trace,animation_samples,thunder_contact_done,falcon_contact_done
    if args.mario_animations or args.roster_animations:
        if u8(scene)!=54:return
        fp=fighter()
        if not 0x80400000<=fp<0x80800000:return
        body=u32(fp+kind_off)
        if body>=12:return
        variant=body_variants[body].get(u32(fp+motion_off))
        if variant is None:return
        if variant>=30:return # Rapid states have a separate looping source clock.
        preset=u8(addr('gSCManagerCharBuilderPlayerSlots'))
        if preset>=4:return
        slot=addr('gSCManagerCharBuilderSlots')+preset*slot_size
        donor=u8(slot+2+animation_rows[variant])
        if donor>=12 or donor==body:return
        case_id=pose_rows[donor][variant]
        if case_id is None:return
        count=pose_cases[case_id]['frames']
        source_frame=f32(u32(fp+gobj_off)+gobj_frame_off)
        # Normal animation frames are supplied by the donor clock; -1 is its
        # native completion sentinel, after applying the final pose sample.
        sample_frame=count-1 if source_frame<0 else min(int(source_frame),count-1)
        rig=body_rig(ROSTER[body]);stride=len(rig)*16+12
        sample=pose_offsets[case_id,body]+sample_frame*stride
        # Native ground slope contour may adjust leg chains after pose playback.
        # Check all limbs in aerials, and the root/torso/arms/head on ground.
        worlds={0:(0,0,0,1)}
        for i,bone in enumerate(rig):
            joint=bone['joint'];obj=u32(fp+joints_off+joint*4)
            if not obj:continue
            if bone['parent'] not in worlds:continue
            local=quaternion(rotation(tuple(f32(obj+rotation_off+axis*4) for axis in range(3))))
            worlds[joint]=qmul(worlds[bone['parent']],local)
            if not bone['required'] or bone['role']<0 or (variant not in range(19,24) and bone['role']>=14):continue
            # Keep the three visually approved float pilots; all other paths use shared curves.
            if body==0 and (donor,variant) in ((7,23),(1,5),(2,14)):continue
            expected=struct.unpack_from('<4f',pose_data,sample+i*16)
            a,b=qmatrix(worlds[joint]),qmatrix(expected)
            error=max(abs(a[x][y]-b[x][y]) for x in range(3) for y in range(3))
            if error>0.003 and len(animation_errors)<10:
                animation_errors.append((body,donor,variant,source_frame,joint,error))
        animation_seen.add((donor,variant));animation_samples+=1
        return
    if (not args.specials and args.path_donor is None and args.superjump is None) or u8(scene)!=54:return
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
    if args.superjump is not None:
        root=u32(gobj+obj_off)+position_off
        attacks=[]
        for i in range(4):
            a=fp+attack_off+i*attack_size
            attacks.append((tuple(u32(a+j) for j in (damage_off,angle_off,kbs_off,kbw_off,kbb_off)),
                            f32(a+radius_off),tuple(f32(a+center_off+j) for j in (0,4,8))))
        superjump_trace.append((record,tuple(f32(root+j) for j in (0,4,8)),s32(fp+lr_off),
                                u32(fp+hitstatus_off),u8(fp+jumps_off),u32(u32(fp+attr_off)+jumps_max_off),attacks))
        if args.mechanic is not None:
            pitch_trace.append(f32(fp+fox_angle_off))
            node=u32(addr('gGCCommonLinks')+5*4)
            for _ in range(64):
                if not 0x80000000<=node<0x80800000:break
                wp=u32(node+user_off)
                if 0x80000000<=wp<0x80800000 and u32(wp+wp_owner_off)==gobj:
                    kind=u32(wp+wp_kind_off);weapon_seen.add(kind)
                    if args.thunder_contact and kind==11 and not thunder_contact_done:
                        pos=u32(node+obj_off)+position_off
                        wf32(pos,f32(root));wf32(pos+4,f32(root+4)+225);wf32(pos+8,0)
                        thunder_contact_done=True
                node=u32(node+link_next_off)
            item=u32(fp+item_off)
            if 0x80000000<=item<0x80800000:
                ip=u32(item+user_off)
                if 0x80000000<=ip<0x80800000 and u32(ip+it_owner_off)==gobj:item_seen.add(u32(ip+it_kind_off))
            if args.falcon_contact and record[0] in falcon_flight_statuses and mask&1:
                cpu=opponent();cpu_gobj=u32(cpu+gobj_off) if cpu else 0
                if 0x80000000<=cpu_gobj<0x80800000:
                    target=u32(cpu_gobj+obj_off)+position_off
                    center=attacks[0][2]
                    wf32(target,center[0]);wf32(target+4,center[1]-200);wf32(target+8,0)
                    w32(cpu+ga_off,air_kind)
                    falcon_contact_done=True
        if args.superjump==5:
            spin=u32(fp+spin_off) if u32(fp+kind_off)==5 else u32(addr('gFTLinkCharBuilderSpinWeapons')+8)
            if record[0] in (nFTLinkHi,nFTLinkHiEnd,nFTLinkAirHi) and 0x80400000<=spin<0x80800000:
                wp=u32(spin+user_off)
                spin_trace.append((record,u32(wp+wp_kind_off),u32(wp+wp_state_off),f32(wp+wp_radius_off),u32(wp+wp_life_off),u32(wp+wp_damage_off)))
    if record!=last_trace:trace.append(record);last_trace=record
check(core.CoreDoCommand(15,0,C.cast(frame_callback,C.c_void_p)))
thread=threading.Thread(target=lambda:check(core.CoreDoCommand(5,0,None)),daemon=True)
thread.start()
try:
    wait(lambda:u32(0x80000318)==(0x400000 if args.four_mb else 0x800000),'Boot memory size')
    if args.boot:
        scene_text=(ROOT/'src/sc/scdef.h').read_text().split('typedef enum SCKind',1)[1].split('}',1)[0]
        scenes=enum_values(us_text('typedef enum SCKind'+scene_text+'}'),'SCKind')
        title=scenes['nSCKindTitle'];mode=scenes['nSCKindModeSelect']
        opening=set(range(scenes['nSCKindOpeningRoom'],scenes['nSCKindOpeningNewcomers']+1))
        seen=set();last=None;min_headroom=0x400000;changed=time.monotonic()
        deadline=time.monotonic()+110
        # Never patch scene memory or skip the intro in this regression.
        while time.monotonic()<deadline:
            current=u8(scene);fault=u32(addr('__osFaultedThread'))
            assert not fault,('Cold boot CPU fault',diagnostic())
            if current!=last:changed=time.monotonic()
            if current in opening:
                seen.add(current)
                start,end,ptr=(u32(heap+j) for j in (4,8,12))
                if start==0x80400000 and end==0x80800000:
                    assert start<=ptr<=end,('Opening heap',diagnostic())
                    min_headroom=min(min_headroom,end-ptr)
                else:
                    # scene_curr changes before overlay loading/heap setup.
                    assert time.monotonic()-changed<.5,('Opening arena initialization',diagnostic())
            if current!=last:
                print('BOOT: scene',current,diagnostic(),flush=True);last=current
            if current==title and seen==opening and u32(addr('dSYTaskmanUpdateCount'))>15:break
            time.sleep(.01)
        else:raise AssertionError(('Full intro/title progress',sorted(seen),diagnostic()))
        assert seen==opening,('Missing opening scenes',opening-seen)
        # The first title presentation rejects Start until its logo animation
        # marks is_title_anim_viewed. Respect that native input gate.
        wait(lambda:u32(addr('sMNTitleAllowProceedWait'))>0 and
                    u32(addr('sMNTitleTransitionTotalTimeTics'))>=u32(addr('sMNTitleAllowProceedWait')),
             'Title logo input gate',seconds=10)
        frames(3);pulse(0x10)
        wait(lambda:u8(scene)==mode and u32(addr('dSYTaskmanUpdateCount'))>20,'Cold boot title Start -> main menu')
        print('PASS: cold boot, all 19 opening scenes, title and Start -> main menu; opening heap headroom at least',min_headroom,'bytes.',flush=True)
        raise SystemExit(0)
    time.sleep(2)
    check(core.CoreDoCommand(17,5,C.byref(C.c_int(0)))) # Run menus uncapped; limit speed during frame-by-frame gameplay checks.
    # Skip the intro only. From Options onward, use the actual button handlers.
    w8(scene+1,u8(scene));w8(scene,57);w32(addr('sSYTaskmanStatus'),1)
    wait(lambda:u8(scene)==57 and u32(addr('sMNOptionTotalTimeTics'))>30,'Options load')
    w32(addr('sMNOptionOption'),3);pulse(0x80)
    wait(lambda:u32(addr('sMNOptionBuilderMode'))==1,'Lab hub')
    minima=[]
    for case in (range(4) if args.mario_animations else range(args.first_choice,args.first_choice+args.cases)):
        choice=0 if args.path_donor is not None or args.superjump is not None else 11 if args.egg_lay else case
        if u32(addr('sMNOptionBuilderMode'))==2:pulse(0x40)
        preset=case%4;body=(case+2)%12
        if args.mario_animations:body=0
        if args.roster_animations:body=case
        w32(addr('sMNOptionBuilderSlot'),preset)
        slot=addr('gSCManagerCharBuilderSlots')+preset*slot_size
        w8(slot,1);w8(slot+1,body)
        for i in range(16):w8(slot+2+i,body)
        if args.mario_animations:
            for i in range(13):w8(slot+2+i,(1,2,4,7)[case])
        if args.roster_animations:
            for i in range(13):w8(slot+2+i,(body+1)%12)
        w8(slot+18,args.superjump if args.superjump is not None and args.superjump!=10 else 11 if args.specials else args.path_donor if args.path_donor in (2,11) else body)
        w8(slot+19,10 if args.superjump==10 else 2 if args.specials else args.path_donor if args.path_donor in (0,4,7) else body)
        if args.mechanic is not None:
            w8(slot+18,args.mechanic if args.mechanic_kind=='hi' else body)
            w8(slot+19,args.mechanic if args.mechanic_kind=='lw' else body)
        w8(slot+neutral_field,0 if args.path_donor is not None else choice)
        pulse(0x80);wait(lambda:u32(addr('sMNOptionBuilderMode'))==2,'Build editor')
        w32(addr('sMNOptionBuilderEntry'),23);pulse(0x80)
        if args.four_mb:
            frames(90);assert u8(scene)==57 and u32(addr('sMNOptionBuilderMode'))==2,diagnostic()
            print('PASS: 4 MB Test in Training stays in the editor, without a heap overflow.',flush=True);break
        wait(lambda:u8(scene)==18 and u32(addr('sMNPlayers1PTrainingTotalTimeTics'))>70,'Training character select')
        frames(30);minima.append(heap_ok());pulse(0x10)
        wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'Training stage select')
        if args.direct_special is not None or args.mechanic is not None:
            # Dream Land avoids Castle's bumper/other stage attacks interrupting
            # the scripted rise before source timing/recovery can be measured.
            w32(addr('sMNMapsCursorSlot'),6)
        pulse(0x80);wait(lambda:u8(scene)==54 and u32(addr('dSYTaskmanUpdateCount'))>180,'Training match load')
        frames(30);minima.append(heap_ok())
        if args.mario_animations or args.roster_animations:
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(0 if args.mechanic is not None else 1))))
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
            if args.roster_animations:
                for donor in range(12):
                    if donor==body:continue
                    for i in range(13):w8(slot+2+i,donor)
                    # Tilt and aerial exercise grounded and airborne reconstruction for every pair.
                    keys(stick(0,35));frames(5);act(stick(0,35)|0x80,3,75)
                    act(0x0800,3,10);act(0x80,3,85)
                    assert any(d==donor for d,v in animation_seen),('Unexercised donor/body',body,donor,animation_seen)
            assert not animation_errors,('ROM pose mismatch',animation_errors)
            assert animation_samples>=30 and len(animation_seen)>=7,('Attack coverage',animation_samples,animation_seen)
            assert u32(addr('gFTCustomAnimationValidationFailures'))==0
            print(f'PASS: body {body}, {animation_samples} live shared poses, donor/variants {sorted(animation_seen)}.',flush=True)
        elif args.path_donor is not None or args.superjump is not None:
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(0 if args.mechanic is not None else 1))))
            donor=args.superjump if args.superjump is not None else args.path_donor;name=ROSTER[donor]
            common=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonStatus')
            header=(ROOT/'src/ft/ftchar'/('ft'+name.lower())/('ft'+name.lower()+'.h')).read_text()
            statuses=enum_values(header.replace('nFTCommonStatusSpecialStart',str(common['nFTCommonStatusSpecialStart'])),'ft'+name+'Status')
            paths={statuses[c['phase'].replace('Motion','Status')]:c for c in path_catalog() if c['donor']==donor and (args.superjump is None or (('Hi' if args.mechanic_kind=='hi' else 'Lw') if args.mechanic is not None else ('Lw' if donor==10 else 'Hi')) in c['phase'])}
            if donor==10 and (args.mechanic is None or args.mechanic_kind=='lw'):paths[statuses['nFTPurinStatusSpecialAirLw']]=paths[statuses['nFTPurinStatusSpecialLw']]
            if donor==10 and args.mechanic is not None and args.mechanic_kind=='hi':paths[statuses['nFTPurinStatusSpecialAirHi']]=paths[statuses['nFTPurinStatusSpecialHi']]
            if donor==5 and args.mechanic is not None and args.mechanic_kind=='lw':
                for c in path_catalog():
                    if c['donor']==5 and c['phase'].startswith('nFTCommonMotionLightThrow'):paths[common[c['phase'].replace('Motion','Status')]]=c
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
                        if resume_frame>=0:expected=resumed_masks[frame]
                        assert mask==expected,(body,c['phase'],frame,'mask',mask,expected,trace)
                        hits+=bool(mask)
                assert seen and hits,(body,'No donor hitbox phase',seen,trace)
                assert trace[-1][0] not in paths,(body,'Special recovery',trace[-1])
                return seen
            trace.clear();travel_trace.clear();last_trace=None
            if args.mechanic is not None:
                def check_mechanic_fields():
                    reference={};samples=0
                    for status,c in paths.items():
                        wall=0;events={};active={};ticks=[]
                        for op,a in c['events']:
                            if op=='ftMotionCommandWait':wall+=int(a[0],0)
                            elif op=='ftMotionCommandWaitAsync':wall=max(wall,int(a[0],0))
                            else:events.setdefault(wall,[]).append((op,a))
                        for tick in range(len(c['frames'])):
                            for op,a in events.get(tick,()):
                                if 'MakeAttackColl' in op:active[int(a[0],0)]=[int(v,0) for v in a]
                                elif op=='ftMotionCommandClearAttackCollAll':active.clear()
                                elif op=='ftMotionCommandClearAttackCollID':active.pop(int(a[0],0),None)
                                elif op=='ftMotionCommandSetAttackCollSize' and int(a[0],0) in active:active[int(a[0],0)][6]=int(a[1],0)
                                elif op=='ftMotionCommandSetAttackCollDamage' and int(a[0],0) in active:active[int(a[0],0)][3]=int(a[1],0)
                            ticks.append({i:tuple(a) for i,a in active.items()})
                        reference[status]=ticks
                    for sample,(r,root,lr,hitstatus,jumps,jumps_max,attacks) in enumerate(superjump_trace):
                        status,_,frame,mask=r
                        if status not in reference or not 0<=frame<len(reference[status]):continue
                        for aid,a in reference[status][frame].items():
                            if not mask&(1<<aid):continue
                            fields,radius,center=attacks[aid]
                            angle=(a[10] if a[10]<512 else a[10]-1024)&0xffffffff
                            assert fields==(a[3],angle,a[11],a[12],a[17]),(body,'Special hit fields',r,fields,a)
                            assert abs(radius-a[6]*.5)<.01,(body,'Special radius',r,radius,a[6]*.5)
                            if body!=donor:
                                x,y,z=paths[status]['frames'][frame][1][aid]
                                if donor==1 and args.mechanic_kind=='hi' and paths[status]['phase'].endswith(('SpecialHi','SpecialAirHi')):
                                    from math import cos,sin
                                    pivot=paths[status]['spawn'][frame];angle=pitch_trace[sample]
                                    dz,dy=z-pivot[0],y-pivot[1]
                                    z=pivot[0]+dz*cos(angle)-dy*sin(angle)
                                    y=pivot[1]+dz*sin(angle)+dy*cos(angle)
                                expected=(root[0]+z*lr,root[1]+y,root[2]-x*lr)
                                assert max(abs(v-w) for v,w in zip(center,expected))<.1,(body,'Special center',r,center,expected)
                            samples+=1
                    return samples
                direction=80 if args.mechanic_kind=='hi' else 176
                allowed=set(statuses[k] for k in statuses if ('SpecialHi' in k or 'SpecialAirHi' in k) if args.mechanic_kind=='hi') if args.mechanic_kind=='hi' else set(statuses[k] for k in statuses if 'SpecialLw' in k or 'SpecialAirLw' in k)
                if donor==5 and args.mechanic_kind=='lw':allowed.update((common['nFTCommonStatusLightThrowF4'],common['nFTCommonStatusLightThrowAirF4']))
                if args.falcon_contact:falcon_flight_statuses={statuses['nFTCaptainStatusSpecialHi'],statuses['nFTCaptainStatusSpecialAirHi']}
                for air in (False,True):
                    pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(50)
                    if air:keys(0x0800);frames(3);keys(0);frames(9)
                    trace.clear();travel_trace.clear();superjump_trace.clear();pitch_trace.clear();weapon_seen.clear();item_seen.clear();last_trace=None
                    thunder_contact_done=False
                    falcon_contact_done=False
                    keys(0x40 | (direction<<24));frames(3)
                    # Keep the original hold controls for egg force, Reflector, Magnet and Stone.
                    keys(0x40);frames(35);keys(0)
                    if donor==5 and args.mechanic_kind=='lw':
                        frames(18)
                        assert u32(fighter()+item_off),(body,'Link bomb not held for second Down B')
                        keys(0x40 | (176<<24));frames(3);keys(0);frames(100)
                        assert any(r[0] in (common['nFTCommonStatusLightThrowF4'],common['nFTCommonStatusLightThrowAirF4']) for r in trace),(body,'Link Down B common toss dispatch')
                    else:frames(240)
                    seen=[r for r in trace if r[0] in allowed]
                    assert seen,(body,name,args.mechanic_kind,'Special never entered',trace)
                    assert u32(fighter()+status_off) not in allowed,(body,name,'Special did not recover',trace[-15:])
                    assert u32(fighter()+hitstatus_off)==1,(body,name,'Invulnerability remained after recovery')
                    assert u32(addr('gFTCustomMoveValidationFailures'))==0
                    samples=check_mechanic_fields()
                    expected_weapon={(3,'lw'):3,(6,'hi'):5,(9,'lw'):11,(8,'hi'):4}.get((donor,args.mechanic_kind))
                    if expected_weapon is not None:assert expected_weapon in weapon_seen,(body,name,'Native projectile missing',weapon_seen,trace)
                    if donor==5 and args.mechanic_kind=='lw':assert link_bomb_kind in item_seen,(body,'Held Link bomb missing',item_seen)
                    if args.thunder_contact:
                        assert thunder_contact_done and samples>0,(body,'Controlled Thunder owner contact missing',samples,trace)
                    if args.falcon_contact:
                        assert falcon_contact_done and any(r[0]==statuses['nFTCaptainStatusSpecialHiCatch'] for r in trace),(body,'Falcon Dive capture missing',falcon_contact_done,sorted({r[0] for r in trace}))
                        assert any(r[0]==statuses['nFTCaptainStatusSpecialHiThrow'] for r in trace),(body,'Falcon Dive release missing',sorted({r[0] for r in trace}))
                        assert u32(opponent()+percent_off)>=20,(body,'Falcon Dive throw damage missing',u32(opponent()+percent_off))
                    print('PASS:',name,args.mechanic_kind,'on body',body,'air' if air else 'ground','native state phases',sorted({r[0] for r in seen}),'source hit samples',samples,flush=True)
                # Interrupt while an egg/Thunder/Stone/movement action is active.
                keys(0x40 | (direction<<24));frames(8);keys(0)
                pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(50)
                assert u32(fighter()+status_off) not in allowed and u32(fighter()+hitstatus_off)==1,(body,'Reset cleanup',diagnostic())
            elif args.superjump is not None:
                def check_superjump():
                    seen=check_paths();samples=0;damage_seen=set();landing=[];center_error=0
                    active_data={};hitstatus_data={};source_damage=set()
                    for status,c in paths.items():
                        wall=0;events={};active={};frames_data=[];hitstatus=1;hitstatuses=[]
                        for op,a in c['events']:
                            if op=='ftMotionCommandWait':wall+=int(a[0],0)
                            elif op=='ftMotionCommandWaitAsync':wall=max(wall,int(a[0],0))
                            else:events.setdefault(wall,[]).append((op,a))
                        for tick in range(len(c['frames'])):
                            for op,a in events.get(tick,()):
                                if 'MakeAttackColl' in op:
                                    active[int(a[0],0)]=tuple(int(v,0) for v in a)
                                    if status in seen:source_damage.add(int(a[3],0))
                                elif op=='ftMotionCommandClearAttackCollAll':active.clear()
                                elif op=='ftMotionCommandClearAttackCollID':active.pop(int(a[0],0),None)
                                elif op=='ftMotionCommandSetHitStatusAll':hitstatus=int(a[0],0)
                            frames_data.append(dict(active))
                            hitstatuses.append(hitstatus)
                        active_data[status]=frames_data;hitstatus_data[status]=hitstatuses
                    for r,root,lr,hitstatus,jumps,jumps_max,attacks in superjump_trace:
                        status,_,frame,mask=r
                        if status==common['nFTCommonStatusLandingFallSpecial']:landing.append(frame)
                        if status in (common['nFTCommonStatusFallSpecial'],common['nFTCommonStatusLandingFallSpecial']):
                            if status==common['nFTCommonStatusFallSpecial']:
                                assert jumps==jumps_max,(body,'Helpless jump inventory',jumps,jumps_max)
                            assert not mask and hitstatus==1,(body,'Recovery cleanup',r,hitstatus)
                        if status not in paths or frame not in range(len(paths[status]['frames'])):continue
                        c=paths[status]
                        assert hitstatus==hitstatus_data[status][frame],(body,'Donor hit status window',r,hitstatus,hitstatus_data[status][frame])
                        for aid,a in active_data[status][frame].items():
                            if not mask&(1<<aid):continue
                            fields,radius,center=attacks[aid]
                            assert fields==(a[3],a[10],a[11],a[12],a[17]),(body,'Source hit fields',r,fields,a)
                            assert abs(radius-a[6]*.5)<.01,(body,'Donor radius',r,radius,a[6]*.5)
                            x,y,z=c['frames'][frame][1][aid]
                            expected=(root[0]+z*lr,root[1]+y,root[2]-x*lr)
                            error=max(abs(v-w) for v,w in zip(center,expected));center_error=max(center_error,error)
                            # Native fallback uses its original binary animation/
                            # matrix data. Enforce the compiled source-path bound
                            # on foreign adapters; native hit fields/timing are
                            # still checked above and source geometry has its own
                            # original-C playback oracle in testNativeAnimation.
                            if body!=donor:assert error<.1,(body,'Donor collision center',r,center,expected)
                            damage_seen.add(a[3]);samples+=1
                    assert samples>=(1 if donor==10 else 20) and source_damage<=damage_seen,(body,'Hit-phase coverage',samples,damage_seen,source_damage)
                    if donor==5:
                        ending=[r[2] for r in trace if r[0]==nFTLinkHiEnd]
                        if ending:
                            assert min(ending)<=1,(body,'Link ending phase',ending)
                            if body!=donor:assert max(ending)==39,(body,'40-tick Link ending',ending)
                        else:
                            duration=direct_landing_duration(name)
                            cliff=any(r[0]==common['nFTCommonStatusCliffCatch'] for r in trace)
                            assert cliff or (landing and duration-1<=len(landing)<=duration+1),(body,'Link recovery path',landing,trace)
                            if landing and body!=donor:assert max(landing)==duration-1,(body,'Link landing clock',landing)
                        if spin_trace:
                            assert all(kind==8 and life>0 and damage>0 for _,kind,_,_,life,damage in spin_trace),(body,'Spin weapon data',spin_trace)
                            assert {80.0,100.0,120.0}<={radius for _,_,state,radius,_,_ in spin_trace if state},(body,'Spin weapon expansion',spin_trace)
                    elif donor!=10:
                        duration=direct_landing_duration(name) if donor==3 else 25
                        assert landing and min(landing)==0 and duration-1<=len(landing)<=duration+1,(body,'Donor landing',duration,landing)
                        if body!=donor:assert max(landing)==duration-1,(body,'Owned landing clock',landing)
                    else:
                        sleep=[r[2] for r in trace if r[0] in paths]
                        assert max(sleep)>=248,(body,'Full Rest sleep',sleep)
                    print('Donor samples:',samples,'maximum center error:',round(center_error,6),flush=True)
                    return seen
                for air in (False,True):
                    trace.clear();superjump_trace.clear();spin_trace.clear();last_trace=None
                    if air:
                        # A native wide hit can contact the CPU and stale the
                        # next move. Reset via the real menu before comparing
                        # raw donor fields on the second start.
                        pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(50)
                        trace.clear();superjump_trace.clear();spin_trace.clear();last_trace=None
                        keys(0x0800);frames(3);keys(0);frames(8)
                    keys(0x40 | ((176 if donor==10 else 80)<<24));frames(3);keys(0);frames(300 if donor==10 else 220)
                    check_superjump()
                    if donor==5 and not air:assert spin_trace,(body,'Grounded spin weapon missing')
                    if donor==5 and air:assert not spin_trace,(body,'Aerial Spin Attack spawned a ground weapon')
                    coverage='native hit fields/timing' if body==donor else 'source centers/damage/radius/knockback'
                    print('PASS:',name,'direct special on body',body,'air' if air else 'ground',coverage+', hit-status windows and donor recovery.',flush=True)
                # Reset during an active special through the real Training handler.
                trace.clear();superjump_trace.clear();last_trace=None
                keys(0x40 | ((176 if donor==10 else 80)<<24));frames(10);keys(0)
                # Request a normal Training reset through the pause menu; it must
                # discard the running action and all donor recovery state.
                pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(50)
                assert u32(fighter()+status_off) not in paths and u32(fighter()+hitstatus_off)==1,(body,'Training reset cleanup',diagnostic())
            elif donor==11:
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
                wf32(pos,f32(root)-100*s32(fp+lr_off));wf32(pos+4,f32(root+4)+50);wf32(pos+8,0)
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
        if args.path_donor is None and args.superjump is None and not (args.mario_animations or args.roster_animations):
            pulse(0x20);frames(30) # Store a charge where supported.
            pulse(0x40);frames(120)
        if args.path_donor is not None or args.superjump is not None or args.mario_animations or args.roster_animations:
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
        action_label='normal poses' if args.mario_animations or args.roster_animations else 'donor special' if args.path_donor is not None or args.superjump is not None else 'B/store/B'
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
            if args.roster_animations:
                for attack in range(13):w8(slot+2+attack,(1,2,4,7)[player])
            w8(slot+18,args.superjump if args.direct_special in (3,5) else (0,4,0,4)[player] if args.superjump is not None and args.superjump!=10 else body);w8(slot+19,10 if args.superjump==10 else body);w8(slot+neutral_field,(9,10,11,6)[player])
            if args.mechanic is not None:
                w8(slot+18,args.mechanic if args.mechanic_kind=='hi' else body)
                w8(slot+19,args.mechanic if args.mechanic_kind=='lw' else body)
            record=transfer+players_field+player*player_size
            w8(record+pkind_field,0 if player==0 else 1);w8(record+fkind_field,body)
        w8(transfer+man_field,1);w8(transfer+cpu_field,3);w8(transfer+reset_field,0);w8(transfer+stage_field,1)
        w32(addr('sMNOptionBuilderSlot'),8);pulse(0x80)
        wait(lambda:u8(scene)==16 and u32(addr('sMNPlayersVSTotalTimeTics'))>75,'Four-slot VS select')
        frames(30);heap_ok();pulse(0x10)
        wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'VS stage select')
        pulse(0x80);wait(lambda:u8(scene)==22 and u32(addr('dSYTaskmanUpdateCount'))>240,'Four-slot VS battle')
        frames(180);heap_ok();pulse(0x40 | ((80 if args.mechanic_kind=='hi' else 176)<<24) if args.mechanic is not None else 0x40 | ((176 if args.superjump==10 else 80)<<24) if args.superjump is not None else 0x40);frames(300 if args.superjump==10 else 160)
        print('PASS: four assigned builds, human/three CPUs: Play VS -> CSS -> stage -> battle/B, upper-bank heap in bounds.',flush=True)
finally:
    keys(0);core.CoreDoCommand(6,0,None);thread.join(timeout=3)
