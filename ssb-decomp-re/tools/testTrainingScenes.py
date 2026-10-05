#!/usr/bin/env python3
"""Optional Linux Mupen64Plus ROM smoke test: real menus/loaders, null rendering.

Requires libmupen64plus2, libmupen64plus-dev and mupen64plus-rsp-hle.
Uses an isolated configuration/save directory; never touches a running emulator.
See docs/neutral-specials.md. The native API is documented at
https://mupen64plus.org/wiki/index.php/Mupen64Plus_v2.0_Core_Front-End
"""
import argparse, ctypes as C, threading, time, subprocess, struct, re
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
parser.add_argument('--paired-moves',action='store_true',help='Check native tether contacts and donor paired throw releases')
parser.add_argument('--taunts',action='store_true',help='Check selectable donor taunt durations, cancel windows and Luigi hitbox/contact')
parser.add_argument('--taunt-body',type=int,choices=range(12),help='Use a particular body for donor taunt regressions')
parser.add_argument('--paired-native',action='store_true',help='Run native grab/throw controls for paired checks')
parser.add_argument('--normal-mechanics',action='store_true',help='Check all donor jab chains, Link bounce and Ness bat windows on each body')
parser.add_argument('--normal-movement',action='store_true',help='Check Fox dash and Kirby forward-smash root velocities, facing and recovery on each body')
parser.add_argument('--vs-results',action='store_true',help='Finish stock VS through native KOs, load results and return to character select')
parser.add_argument('--vs-defaults',action='store_true',help='Check fresh-boot VS defaults: four stocks, stock rules and items off')
parser.add_argument('--special-animations',action='store_true',help='Compare live borrowed-special poses with native-engine references')
parser.add_argument('--charge-animations',action='store_true',help='Check partial/full Giant Punch and Charge Shot pose transitions')
parser.add_argument('--mechanic',type=int,choices=(1,3,5,6,7,8,9,10,11),help='Exercise remaining special mechanics across bodies')
parser.add_argument('--mechanic-kind',choices=('hi','lw'),default='hi')
parser.add_argument('--thunder-contact',action='store_true',help='Place the live native Thunder head in its owner-contact box to check the hit branch')
parser.add_argument('--falcon-contact',action='store_true',help='Place the CPU in the live Falcon Dive catch volume to check native capture/throw')
args=parser.parse_args()
if args.normal_movement:args.normal_mechanics=True
if args.charge_animations:
    args.first_choice=8;args.cases=2;args.special_animations=True
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
value,length,index=layout_symbols['sSceneSmokeNormalLayout'];start=sections[index][4]+value-sections[index][3]
proc_hit_off,flag1_off,rehit_off,pkind_off,special_coll_off,wp_reflect_off,vel_ground_off,training_cpu_kind_off,coll_prev_off,floor_line_off=struct.unpack_from('>10I',data,start)
value,length,index=layout_symbols['sSceneSmokeReflectFlags'];start=sections[index][4]+value-sections[index][3]
reflect_bits=[(i,b) for i,b in enumerate(data[start:start+length]) if b]
assert len(reflect_bits)==1;reflect_flag_off,reflect_flag_mask=reflect_bits[0]
value,length,index=layout_symbols['sSceneSmokePairLayout'];start=sections[index][4]+value-sections[index][3]
catch_off,capture_off,throw_desc_off,flag2_off,child_off=struct.unpack_from('>5I',data,start)
value,length,index=layout_symbols['sSceneSmokeInvisibleFlags'];start=sections[index][4]+value-sections[index][3]
invisible_bits=[(i,b) for i,b in enumerate(data[start:start+length]) if b]
assert len(invisible_bits)==1;invisible_off,invisible_mask=invisible_bits[0]
ftsize,kind_off,port_off,gobj_off,status_off,motion_off,attack_off,attack_size,attack_state_off,passive_off,passive_size,generation_off,physics_off,vel_air_off,hitlag_off,gobj_frame_off=fighter_layout
slot_size,neutral_field,players_field,player_size,pkind_field,fkind_field,man_field,cpu_field,reset_field,stage_field=layout
value,length,index=layout_symbols['sSceneSmokeTauntLayout'];start=sections[index][4]+value-sections[index][3]
taunt_field=struct.unpack_from('>I',data,start)[0]
value,length,index=layout_symbols['sSceneSmokeVSLayout'];start=sections[index][4]+value-sections[index][3]
rules_off,stocks_off,items_off,item_rate_off,player_stock_off,player_fighter_off,fighter_stock_off=struct.unpack_from('>7I',data,start)
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
keys_port=plugins[1].LabKeysPort
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
def fighter():
    if args.paired_moves or args.taunts:
        node=u32(addr('gGCCommonLinks')+3*4)
        for _ in range(4):
            if not 0x80000000<=node<0x80800000:break
            fp=u32(node+user_off)
            if 0x80400000<=fp<0x80800000 and u8(fp+port_off)==0:return fp
            node=u32(node+link_next_off)
    return u32(addr('sFTManagerStructsAllocBuf'))
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
                fault_thread=hex(fault), fault_gprs=[hex(u32(fault+j)) for j in range(0x24,0x118,8)] if fault else [],
                fault_registers=[hex(u32(fault+j)) for j in range(0xe0,0x118,4)] if fault else [],
                fighter=[hex(u32(fighter()+j)) for j in (status_off,motion_off,spin_off,generation_off)] if fault else [],
                heap=[hex(u32(heap+j)) for j in (4,8,12)],updates=u32(addr('dSYTaskmanUpdateCount')))
def wait(predicate,label,seconds=15):
    deadline=time.monotonic()+seconds
    while not predicate():
        if time.monotonic()>deadline:raise AssertionError((label,diagnostic()))
        time.sleep(.001 if args.mechanic is not None or args.superjump is not None or args.normal_mechanics or args.charge_animations else .01)
def frames(count=12):
    initial=u32(addr('dSYTaskmanUpdateCount'))
    wait(lambda:u32(addr('dSYTaskmanUpdateCount'))>=initial+count,'Game stopped updating')
def pulse(value):
    keys(value);time.sleep(.07);keys(0);time.sleep(.07)
def heap_ok():
    start,end,ptr=(u32(heap+j) for j in (4,8,12))
    assert start==((addr('charbuilder_animation_bank_VRAM_END')+63)&~63) and end==0x80800000 and start<=ptr<=end,diagnostic()
    return end-ptr
trace=[];travel_trace=[];superjump_trace=[];spin_trace=[];last_trace=None
weapon_seen=set();item_seen=set();pitch_trace=[]
thunder_contact_done=False
falcon_contact_done=False
falcon_flight_statuses=set()
normal_trace=[];normal_contact=False;normal_bounced=False;normal_reflect_contact=False;normal_reflected=False
normal_movement_trace=[]
FT_LINK_REHIT=int(re.search(r'#define FTCOMMON_ATTACKAIRLW_LINK_REHIT_TIMER\s+(\d+)',(ROOT/'src/ft/ftcommon.h').read_text())[1])
animation_seen=set();animation_samples=0;animation_errors=[]
motion_ids=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
animation_variants={motion_ids['nFTCommonMotion'+m]:i for i,m in enumerate(MOTIONS[:29])}
animation_variants[extra_ids('Mario')[0]]=29
animation_rows=[next(i for i,family in enumerate(SLOTS.values()) if m in family) for m in MOTIONS[:24]]+list(range(8,13))+[0]
if args.mario_animations or args.roster_animations or args.special_animations:
    from sharedAnimation import catalog as pose_catalog,body_rig,qmul,quaternion,rotation,qmatrix
    pose_cases,pose_rows=pose_catalog()
    pose_data=(ROOT/'build/shared-animation-poses.bin').read_bytes()
    pose_offsets={};cursor=0
    for case_id,case in enumerate(pose_cases):
        for body_id,body_name in enumerate(ROSTER):
            pose_offsets[case_id,body_id]=cursor
            cursor+=case['frames']*(len(body_rig(body_name))*16+12)
    assert cursor==len(pose_data),'Run tools/testNativeAnimation.py for current runtime pose references.'
    if args.special_animations:
        from sharedAnimation import special_rows
        special_pose_rows=[(phase,index) for phase,index in special_rows() if phase['binding'] is not None]
        special_clock=addr('sFTCustomMoveClocks')
    body_variants=[]
    for name in ROSTER:
        variants=dict(animation_variants)
        for variant,motion in enumerate(extra_ids(name),29):
            if motion>=0:variants[motion]=variant
        body_variants.append(variants)
pair_trace=[];pair_errors=[];pair_hits=[];pair_position_samples=0;pair_escape=False;pair_contact=False;pair_first_point=None;pair_direction=0;pair_cargo_frames=0
taunt_trace=[];taunt_menu_target=None
@C.CFUNCTYPE(None,C.c_uint)
def frame_callback(frame):
    global pair_cargo_frames,pair_position_samples
    global last_trace,animation_samples,thunder_contact_done,falcon_contact_done,normal_bounced,normal_reflected
    if taunt_menu_target is not None and u8(taunt_menu_target[0])==taunt_menu_target[1]:keys(0)
    if args.taunts and u8(scene)==54:
        fp=fighter()
        if 0x80400000<=fp<0x80800000 and u32(fp+status_off)==common_statuses['nFTCommonStatusAppeal']:
            clock=addr('sFTCustomMoveClocks');gobj=u32(fp+gobj_off);root=u32(gobj+obj_off)+position_off
            tick=int(f32(clock+24) if u32(clock)==fp else f32(gobj+gobj_frame_off))
            mask=sum(1<<aid for aid in range(4) if u32(fp+attack_off+aid*attack_size+attack_state_off))
            hits=tuple((tuple(u32(fp+attack_off+aid*attack_size+j) for j in (damage_off,angle_off,kbs_off,kbw_off,kbb_off)),
                        f32(fp+attack_off+aid*attack_size+radius_off),
                        tuple(f32(fp+attack_off+aid*attack_size+center_off+j) for j in (0,4,8))) for aid in range(4))
            model=u32(fp+joints_off+4*4)
            taunt_trace.append((tick,u32(fp+flag1_off),mask,hits,tuple(f32(root+j) for j in (0,4,8)),s32(fp+lr_off),
                                tuple(f32(model+scale_off+j) for j in (0,4,8)),tuple(f32(root-position_off+scale_off+j) for j in (0,4,8))))
            if mask:
                cpu=opponent();target=u32(u32(cpu+gobj_off)+obj_off)+position_off
                center=hits[0][2]
                # Keep the CPU standing on the attacker's floor. Putting a
                # head at this ground-level toe volume drops it under the stage.
                placed=(center[0],f32(root+4),f32(root+8))
                for j,v in zip((0,4,8),placed):
                    wf32(target+j,v);wf32(cpu+coll_prev_off+j,v);wf32(cpu+physics_off+vel_air_off+j,0)
                wf32(cpu+physics_off+vel_ground_off,0)
    if args.paired_moves and u8(scene)==54 and u32(addr('dSYTaskmanUpdateCount'))>180:
        fp=fighter();cpu=opponent()
        if 0x80400000<=fp<0x80800000 and cpu:
            status=u32(fp+status_off);clock=addr('sFTCustomMoveClocks')
            frame_value=f32(clock+24) if u32(clock)==fp else f32(u32(fp+gobj_off)+gobj_frame_off)
            root=u32(u32(fp+gobj_off)+obj_off)+position_off
            if pair_contact and u32(fp+catch_off) and u32(cpu+capture_off)==u32(fp+gobj_off) and not args.paired_native:
                phase=next((addr('sFTCustomPairPhases')+i*80 for i in range(symbols['sFTCustomPairPhases'][1]//80) if addr('sFTCustomPairPhases')+i*80+12==u32(clock+8)),0)
                if u32(clock)==fp and u32(clock+12)==status and phase:
                    anchors=u32(phase+48);count=u32(phase+60);tick=max(0,int(frame_value))
                    period=u32(phase+44);begin=u32(phase+40)
                    if period and tick>=begin:tick=begin+(tick-begin)%period
                    tick=min(tick,count-1);sample=anchors+tick*48
                    victim_root=u32(u32(cpu+gobj_off)+obj_off);child=u32(victim_root+child_off)
                    if child:
                        offset=tuple(-f32(child+position_off+j)*f32(victim_root+scale_off+j) for j in (0,4,8))
                        local=tuple(f32(sample+36+axis*4)+sum(f32(sample+(axis*3+k)*4)*offset[k] for k in range(3)) for axis in range(3))
                        from math import sin,cos
                        yaw=f32(root-position_off+rotation_off+4)
                        expected=(f32(root)+cos(yaw)*local[0]+sin(yaw)*local[2],f32(root+4)+local[1],f32(root+8)-sin(yaw)*local[0]+cos(yaw)*local[2])
                        observed=tuple(f32(victim_root+position_off+j) for j in (0,4,8))
                        axes=(0,2) if status in (167,168) else (0,1,2)
                        error=max(abs(observed[j]-expected[j]) for j in axes)
                        pair_position_samples+=1
                        if error>.2 and len(pair_errors)<8:pair_errors.append((status,frame_value,error,observed,expected))
            if pair_contact and status==common_statuses['nFTCommonStatusCatch']:
                mask=sum(1<<aid for aid in range(4) if u32(fp+attack_off+aid*attack_size+attack_state_off))
                centers=tuple(tuple(f32(fp+attack_off+aid*attack_size+center_off+j) for j in (0,4,8)) for aid in range(4))
                pair_hits.append((int(frame_value),mask,centers,tuple(f32(root+j) for j in (0,4,8)),s32(fp+lr_off)))
            pair_trace.append((status,frame_value,u32(fp+catch_off),u32(cpu+capture_off),u32(cpu+status_off),u32(cpu+percent_off),bool(u8(cpu+invisible_off)&invisible_mask),tuple(f32(root+j) for j in (0,4,8))))
            if pair_contact and status==common_statuses['nFTCommonStatusCatch']:
                for aid in range(4):
                    hit=fp+attack_off+aid*attack_size
                    if u32(hit+attack_state_off):
                        cpu_root=u32(u32(cpu+gobj_off)+obj_off)+position_off
                        center=tuple(f32(hit+center_off+j) for j in (0,4,8))
                        for j,value in zip((0,4,8),(center[0],center[1]-200,center[2])):
                            wf32(cpu_root+j,value);wf32(cpu+coll_prev_off+j,value)
                            wf32(cpu+physics_off+vel_air_off+j,0)
                        wf32(cpu+physics_off+vel_ground_off,0)
                        break
                else:
                    if args.paired_native and pair_first_point is not None:
                        tick,point=pair_first_point
                        if frame_value<=tick:
                            cpu_root=u32(u32(cpu+gobj_off)+obj_off)+position_off;facing=s32(fp+lr_off)
                            center=(f32(root)+point[2]*facing,f32(root+4)+point[1],f32(root+8)-point[0]*facing)
                            for j,value in zip((0,4,8),(center[0],center[1]-200,center[2])):
                                wf32(cpu_root+j,value);wf32(cpu+coll_prev_off+j,value);wf32(cpu+physics_off+vel_air_off+j,0)
                            wf32(cpu+physics_off+vel_ground_off,0)
            if pair_direction and status==common_statuses['nFTCommonStatusCatchWait']:

                facing=s32(fp+lr_off);keys(((80*facing*pair_direction)&255)<<16)
            elif pair_direction and status==235 and u32(fp+kind_off)!=2:
                pair_cargo_frames+=1
                keys(0x80 if pair_cargo_frames>=6 and not pair_escape else 0)
            elif pair_direction and status==235 and args.paired_native:
                pair_cargo_frames+=1;keys(0x80 if pair_cargo_frames>=6 and not pair_escape else 0)
            elif pair_direction and status>=common_statuses["nFTCommonStatusThrowF"]:
                keys(0)
    if args.special_animations and u8(scene)==54:
        fp=fighter()
        if 0x80400000<=fp<0x80800000:
            body=u32(fp+kind_off);clock=special_clock
            if body<12 and u32(clock)==fp and u32(clock+4)==u32(fp+generation_off) and u32(clock+12)==u32(fp+status_off):
                move=u32(clock+8)
                for row,(phase,case_id) in enumerate(special_pose_rows):
                    if u32(addr('sFTCustomSpecialAnimations')+row*20)!=move:continue
                    c=pose_cases[case_id];source_frame=max(0,int(f32(clock+24)))
                    if c['loop_period'] and source_frame>=c['loop_start']:source_frame=c['loop_start']+(source_frame-c['loop_start'])%c['loop_period']
                    source_frame=min(source_frame,c['frames']-1)
                    rig=body_rig(ROSTER[body]);sample=pose_offsets[case_id,body]+source_frame*(len(rig)*16+12)
                    worlds={0:(0,0,0,1)};correction=(0,0,0,1)
                    from sharedAnimation import qnormal
                    for i,bone in enumerate(rig):
                        obj=u32(fp+joints_off+bone['joint']*4)
                        if not obj or bone['parent'] not in worlds:continue
                        local=quaternion(rotation(tuple(f32(obj+rotation_off+axis*4) for axis in range(3))))
                        worlds[bone['joint']]=qmul(worlds[bone['parent']],local)
                        expected=struct.unpack_from('<4f',pose_data,sample+i*16)
                        if bone['joint']==4:
                            q=qnormal(expected);correction=qmul(worlds[4],(-q[0],-q[1],-q[2],q[3]))
                        # Directional flight pitches the root; native ground slope
                        # processing can adjust legs after the shared pose.
                        expected=qmul(correction,expected)
                        if not bone['required'] or bone['role']<0 or (u32(fp+ga_off)!=air_kind and bone['role']>=14):continue
                        a,b=qmatrix(worlds[bone['joint']]),qmatrix(expected)
                        error=max(abs(a[x][y]-b[x][y]) for x in range(3) for y in range(3))
                        if error>0.008 and len(animation_errors)<10:animation_errors.append((body,phase['phase'],source_frame,bone['joint'],error))
                    animation_seen.add((phase['donor'],phase['phase']));animation_samples+=1
                    break
    if args.normal_mechanics:
        if u8(scene)!=54:return
        fp=fighter()
        if not 0x80400000<=fp<0x80800000:return
        gobj=u32(fp+gobj_off);status=u32(fp+status_off)
        root=u32(gobj+obj_off)+position_off
        mask=sum(1<<i for i in range(4) if u32(fp+attack_off+i*attack_size+attack_state_off))
        record=(status,u32(fp+motion_off),f32(gobj+gobj_frame_off),mask,u32(fp+flag1_off),f32(fp+physics_off+vel_air_off+4),u32(fp+rehit_off),u32(fp+special_coll_off),bool(u8(fp+reflect_flag_off)&reflect_flag_mask))
        normal_trace.append(record)
        if args.normal_movement:
            clock=addr('sFTCustomMoveClocks')+u8(fp+port_off)*44
            source_frame=f32(clock+24) if u32(clock)==fp and u32(clock+12)==status else record[2]
            normal_movement_trace.append((u32(addr('dSYTaskmanUpdateCount')),status,source_frame,
                f32(fp+physics_off+vel_ground_off),f32(root),s32(fp+lr_off),s32(fp+hitlag_off)))
        if normal_contact and status==common_statuses['nFTCommonStatusAttackAirLw'] and mask and not normal_bounced:
            cpu=opponent();cg=u32(cpu+gobj_off) if cpu else 0
            if cg:
                target=u32(cg+obj_off)+position_off;center=fp+attack_off+center_off
                wf32(target,f32(center));wf32(target+4,f32(center+4)-200);wf32(target+8,0);w32(cpu+ga_off,air_kind)
        if normal_contact and record[6]==FT_LINK_REHIT:normal_bounced=True
        if normal_reflect_contact:
            cpu=opponent();cg=u32(cpu+gobj_off) if cpu else 0
            node=u32(addr('gGCCommonLinks')+5*4)
            for _ in range(64):
                if not 0x80000000<=node<0x80800000:break
                wp=u32(node+user_off)
                if 0x80000000<=wp<0x80800000:
                    if u32(wp+wp_reflect_off)==gobj or u32(wp+wp_owner_off)==gobj:normal_reflected=True
                    if cg and u32(wp+wp_owner_off)==cg:
                        point=u32(node+obj_off)+position_off
                        # Hold the controlled projectile outside contact until
                        # the native source reflector window opens.
                        wf32(point,f32(root) if record[8] else f32(root)+2500)
                        wf32(point+4,f32(root+4)+157.5);wf32(point+8,0)
                node=u32(node+link_next_off)
        return
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
                if start==((addr('charbuilder_animation_bank_VRAM_END')+63)&~63) and end==0x80800000:
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
    default_build_one=[u8(addr('gSCManagerCharBuilderSlots')+i) for i in range(slot_size)]
    if args.vs_defaults:
        transfer=addr('gSCManagerTransferBattleState')
        assert (u8(transfer+rules_off),u8(transfer+stocks_off),u32(transfer+items_off),u8(transfer+item_rate_off))==(2,3,0,0),'Fresh-boot VS rules must be four stocks/items off'
        print('PASS: fresh-boot VS stock rules, four stocks and items off.',flush=True)
    minima=[]
    for case in (range(0) if args.vs_results else range(4) if args.mario_animations else range(args.first_choice,args.first_choice+args.cases)):
        if args.special_animations:animation_seen.clear();animation_errors.clear();animation_samples=0
        choice=0 if args.path_donor is not None or args.superjump is not None else 11 if args.egg_lay else case
        if u32(addr('sMNOptionBuilderMode'))==2:pulse(0x40)
        preset=case%4;body=(case+2)%12
        if args.mario_animations:body=0
        if args.roster_animations:body=case
        if args.paired_native:body=case
        if args.taunts and args.taunt_body is not None:body=args.taunt_body
        w32(addr('sMNOptionBuilderSlot'),preset)
        slot=addr('gSCManagerCharBuilderSlots')+preset*slot_size
        w8(slot,1);w8(slot+1,body)
        for i in range(16):w8(slot+2+i,body)
        if args.normal_mechanics:
            for i in range(13):w8(slot+2+i,i%12)
            w8(slot+2+5,11);w8(slot+2+12,5) # Preload all donor attributes and Ness's bat file.
        if args.mario_animations:
            for i in range(13):w8(slot+2+i,(1,2,4,7)[case])
        if args.roster_animations:
            for i in range(13):w8(slot+2+i,(body+1)%12)
        if args.paired_moves:
            grab=case if args.paired_native else (5,3,6)[case%3]
            if grab==body and not args.paired_native:grab=(5,3,6)[(case+1)%3]
            w8(slot+2+13,grab);w8(slot+2+14,case);w8(slot+2+15,case)
        w8(slot+18,args.superjump if args.superjump is not None and args.superjump!=10 else 11 if args.specials else args.path_donor if args.path_donor in (2,11) else body)
        w8(slot+19,10 if args.superjump==10 else 2 if args.specials else args.path_donor if args.path_donor in (0,4,7) else body)
        if args.mechanic is not None:
            w8(slot+18,args.mechanic if args.mechanic_kind=='hi' else body)
            w8(slot+19,args.mechanic if args.mechanic_kind=='lw' else body)
        w8(slot+neutral_field,0 if args.path_donor is not None else choice)
        w8(slot+taunt_field,case if args.taunts else body)
        pulse(0x80);wait(lambda:u32(addr('sMNOptionBuilderMode'))==2,'Build editor')
        if args.taunts:
            check(core.CoreDoCommand(17,4,C.byref(C.c_int(200))))
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            w32(addr('sMNOptionBuilderEntry'),22);taunt_menu_target=(slot+taunt_field,(case+1)%12);keys(0x01)
            wait(lambda:u8(slot+taunt_field)==(case+1)%12,'Taunt editor right');keys(0);taunt_menu_target=None;frames(15)
            assert u8(slot+taunt_field)==(case+1)%12,('Taunt editor right/wrap',case,u8(slot+taunt_field))
            taunt_menu_target=(slot+taunt_field,case);keys(0x02)
            wait(lambda:u8(slot+taunt_field)==case,'Taunt editor left');keys(0);taunt_menu_target=None;frames(15)
            assert u8(slot+taunt_field)==case,('Taunt editor left/wrap',case,u8(slot+taunt_field))
            saved=[u8(slot+i) for i in range(slot_size)]
            w32(addr('sMNOptionBuilderEntry'),2);pulse(0x80);assert u8(slot+taunt_field)==body,'Taunt body reset'
            w8(slot+taunt_field,255);w32(addr('sMNOptionBuilderEntry'),23);pulse(0x80)
            assert u8(slot+taunt_field)<12,'Taunt randomization'
            for i,value in enumerate(saved):w8(slot+i,value)
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(0))))
        w32(addr('sMNOptionBuilderEntry'),24);pulse(0x80)
        if args.four_mb:
            frames(90);assert u8(scene)==57 and u32(addr('sMNOptionBuilderMode'))==2,diagnostic()
            print('PASS: 4 MB Test in Training stays in the editor, without a heap overflow.',flush=True);break
        wait(lambda:u8(scene)==18 and u32(addr('sMNPlayers1PTrainingTotalTimeTics'))>70,'Training character select')
        frames(30);minima.append(heap_ok());pulse(0x10)
        wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'Training stage select')
        if args.superjump is not None or args.direct_special is not None or args.mechanic is not None or args.normal_mechanics or args.charge_animations or args.paired_moves or args.taunts:
            # Dream Land avoids Castle's bumper/other stage attacks interrupting
            # the scripted rise before source timing/recovery can be measured.
            w32(addr('sMNMapsCursorSlot'),6)
        if args.normal_mechanics or args.paired_moves or args.taunts:w8(scene+training_cpu_kind_off,0)
        pulse(0x80);wait(lambda:u8(scene)==54 and u32(addr('dSYTaskmanUpdateCount'))>180,'Training match load')
        frames(30);minima.append(heap_ok())
        if args.paired_moves:
            from pairedMoves import catalog as pair_catalog,phase_data
            grab_index=next(i for i,c in enumerate(pair_catalog()) if c['donor']==grab and c['phase']=='Catch')
            grab_frames=phase_data(grab_index)[0]
            first_tick,first_mask,first_centers=next((tick,mask,centers) for tick,(mask,centers) in enumerate(grab_frames) if mask)
            pair_first_point=(first_tick,first_centers[next(aid for aid in range(4) if first_mask&(1<<aid))])
            check(core.CoreDoCommand(17,4,C.byref(C.c_int(200))))
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            fp=fighter();cpu=opponent()
            # Real grab/throw inputs; contact placement only avoids CPU AI wandering.
            for direction in (1,-1):
                pair_direction=0;pair_contact=False;keys(0)
                pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(240)
                wait(lambda:u8(scene)==54 and u32(fighter()+status_off)==common_statuses["nFTCommonStatusWait"],"Reset fighter ready")
                fp=fighter();cpu=opponent();cpu_root=u32(u32(cpu+gobj_off)+obj_off)+position_off
                wf32(cpu_root,1000);wf32(cpu_root+4,400)
                pair_trace.clear();pair_hits.clear();pair_errors.clear();pair_position_samples=0;pair_cargo_frames=0;pair_direction=direction;pair_contact=True
                keys(0xA0);frames(3);keys(0)
                wait(lambda:any(r[2] for r in pair_trace),'Tether contact/capture',seconds=5)
                wait(lambda:any(r[2] and r[3] for r in pair_trace),'Bidirectional native capture')
                wait(lambda:any(r[5]>0 and not r[2] and not r[3] for r in pair_trace),'Paired donor throw release',seconds=8)
                pair_direction=0;pair_contact=False;keys(0);frames(100)
                statuses={r[0] for r in pair_trace};captured=[r for r in pair_trace if r[2]]
                assert common_statuses['nFTCommonStatusCatchPull'] in statuses,('Missing pull',body,case,statuses)
                assert common_statuses['nFTCommonStatusCatchWait'] in statuses,('Missing wait',body,case,statuses)
                if case==2 and direction==1:assert 235 in statuses and 244 in statuses,('DK carry/toss phases',statuses)
                if case==8 and direction==1:assert 228 in statuses and 230 in statuses,('Kirby lift/landing phases',statuses)
                releases=[r for r in pair_trace if r[5]>0 and not r[2] and not r[3]]
                assert u32(fp+status_off)<166,("Throw recovery",body,case,pair_trace[-10:])
                assert releases and not u32(fp+catch_off) and not u32(cpu+capture_off),('Stuck capture',pair_trace[-10:])
                assert not (u8(cpu+invisible_off)&invisible_mask),('Hidden victim after release',case)
                assert u32(fp+attr_off)!=0 and u32(addr('gFTCustomMoveValidationFailures'))==0 and u32(addr('gFTCustomAnimationValidationFailures'))==0
                if grab==6:assert any(r[6] for r in captured),('Yoshi capture visibility',body,case)
                assert not pair_errors,('Paired victim positioning',body,case,pair_errors)
                if not args.paired_native:assert pair_position_samples>0,('No paired positions',body,case)
                first=releases[0]
                release_phase=next(c for c in pair_catalog() if c['donor']==case and c['status']==first[0])
                release_ticks=[tick for tick,events in release_phase['timeline'].items() if any(op=='ftMotionCommandSetFlag2' and a[0] for op,a in events)]
                assert int(first[1]) in set(release_ticks),('Donor release tick',body,case,first,release_ticks)
                from pairedMoves import throw_descriptors,phase_data
                descriptors=throw_descriptors(release_phase['fighter'],release_phase['phase']) or throw_descriptors(release_phase['fighter'],'ThrowF')
                expected_damage=descriptors[0][1]+(8 if case==2 and direction==1 else 0)
                assert first[5]==expected_damage,('Donor throw damage',body,case,first[5],expected_damage)
                grab_index=next(i for i,c in enumerate(pair_catalog()) if c['donor']==grab and c['phase']=='Catch')
                grab_frames=phase_data(grab_index)[0]
                if not args.paired_native:assert any(mask for tick,mask,centers,root,facing in pair_hits),('Grab never became active',body,grab)
                for tick,mask,centers,root,facing in pair_hits:
                    if not 0<=tick<len(grab_frames):continue
                    expected_mask,points=grab_frames[tick]
                    assert mask==expected_mask,('Grab active timing',body,grab,tick,mask,expected_mask)
                    for aid,point in enumerate(points):
                        if not mask&(1<<aid):continue
                        expected=(root[0]+point[2]*facing,root[1]+point[1],root[2]-point[0]*facing)
                        assert max(abs(a-b) for a,b in zip(centers[aid],expected))<.1,('Grab center',body,grab,tick,aid,centers[aid],expected)
                print('PASS: paired body',body,'grab',grab,'throw',case,'direction',direction,'phases',sorted(statuses),'release',first[:7],'heap',heap_ok(),flush=True)
            if case==2:
                pair_direction=0;pair_contact=False;keys(0)
                pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(240)
                wait(lambda:u32(fighter()+status_off)==common_statuses['nFTCommonStatusWait'],'Cargo escape reset')
                fp=fighter();cpu=opponent();pair_trace.clear();pair_escape=True;pair_direction=1;pair_contact=True;pair_cargo_frames=0
                keys(0xA0);frames(3);keys(0)
                wait(lambda:any(r[0]==235 for r in pair_trace),'Cargo hold before mash escape')
                pair_direction=0;pair_contact=False;keys(0);w32(cpu+pkind_off,0)
                for i in range(20):
                    keys_port(u8(cpu+port_off),(0x80 if i%2 else 0x40)|(((80 if i%2 else -80)&255)<<16));frames(2)
                    keys_port(u8(cpu+port_off),0);frames(1)
                    if not u32(cpu+capture_off):break
                keys_port(u8(cpu+port_off),0);pair_escape=False;w32(cpu+pkind_off,1);frames(100)
                assert not u32(fp+catch_off) and not u32(cpu+capture_off),('Cargo mash escape links',body)
                assert u32(fp+status_off)<235 and not (u8(cpu+invisible_off)&invisible_mask),('Cargo escape cleanup',body)
                print('PASS: cargo mash escape body',body,'native bidirectional release and status cleanup.',flush=True)
            pair_direction=0;pair_contact=False
        elif args.taunts:
            from pairedMoves import catalog as pair_catalog,phase_data
            from customAnimation import sample
            from sharedAnimation import body_rig
            index=next(i for i,c in enumerate(pair_catalog()) if c['donor']==case and c['phase']=='Appeal')
            taunt=pair_catalog()[index];source_hits=phase_data(index)[0]
            root_bind=next(bone['scale'] for bone in body_rig(ROSTER[body]) if bone['joint']==4)
            source_scales=[pose[4][7:10] for pose in sample(taunt['fighter'],taunt['name'],taunt['frames'],taunt['flags'])] if case==0 else None
            cancel=next((tick for tick,commands in taunt['timeline'].items() if any(op=='ftMotionCommandSetFlag1' and a[0] for op,a in commands)),None)
            check(core.CoreDoCommand(17,4,C.byref(C.c_int(200))))
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            frames(200) # Finish GO and native spawn protection before contact checks.
            wait(lambda:u32(fighter()+status_off)==common_statuses['nFTCommonStatusWait'],'Taunt ready')
            top=u32(u32(fighter()+gobj_off)+obj_off)
            top_scale=tuple(f32(top+scale_off+j) for j in (0,4,8))
            if case==4:
                w32(opponent()+pkind_off,0);keys_port(u8(opponent()+port_off),0)
                # Use the center of the floor so the dummy's native ledge
                # recovery cannot jump out of the three-frame toe window.
                point=source_hits[47][1][0];facing=s32(fighter()+lr_off)
                for actor,x in ((fighter(),0),(opponent(),point[2]*facing)):
                    actor_root=u32(u32(actor+gobj_off)+obj_off)+position_off
                    for j,v in zip((0,4,8),(x,0,0)):
                        wf32(actor_root+j,v);wf32(actor+coll_prev_off+j,v);wf32(actor+physics_off+vel_air_off+j,0)
                    wf32(actor+physics_off+vel_ground_off,0)
                frames(90)
            taunt_trace.clear();pulse(0x2000)
            wait(lambda:len(taunt_trace)>0,'L starts chosen taunt')
            wait(lambda:u32(fighter()+status_off)==common_statuses['nFTCommonStatusWait'],'Taunt natural recovery')
            seen={r[0]:r for r in taunt_trace};assert max(seen)>=taunt['duration']-2,('Taunt duration',body,case,max(seen),taunt['duration'])
            active=[]
            for tick,flag,mask,hits,root,facing,model_scale,world_scale in taunt_trace:
                if tick<0 or tick>=len(source_hits):continue
                if source_scales is not None:
                    expected_scale=tuple(a*b for a,b in zip(root_bind,source_scales[tick]))
                    assert max(abs(a-b) for a,b in zip(model_scale,expected_scale))<.00002,('Mario growth scale',body,tick,model_scale,expected_scale)
                    assert world_scale==top_scale,('Mario taunt changed TopN/body size',body,tick,world_scale,top_scale)
                expected_mask,centers=source_hits[tick]
                assert mask==expected_mask,('Taunt active mask',body,case,tick,mask,expected_mask)
                if cancel is not None:assert bool(flag)==(tick>=cancel),('Taunt cancel flag',body,case,tick,flag,cancel)
                for aid,point in enumerate(centers):
                    if not mask&(1<<aid):continue
                    expected=(root[0]+point[2]*facing,root[1]+point[1],root[2]-point[0]*facing)
                    assert max(abs(a-b) for a,b in zip(hits[aid][2],expected))<(1 if args.paired_native else .2),('Taunt hit center',body,case,tick,hits[aid][2],expected)
                    assert hits[aid][0]==(1,361,100,60,0) and abs(hits[aid][1]-50)<.01,('Luigi taunt hit fields',hits[aid])
                    active.append(tick)
            if case==4:
                assert {47,48,49}<=set(active),('Luigi taunt window',active)
                assert u32(opponent()+percent_off)>=1,('Luigi taunt actual damage',body,'CPU kind/status/hitstatus',u32(opponent()+kind_off),u32(opponent()+status_off),u32(opponent()+hitstatus_off),'game',u8(u32(addr('gSCManagerBattleState'))+battle_status_off),'active',[(r[0],r[3][0][2]) for r in taunt_trace if r[2]])
            else:assert not active,('Unexpected taunt hitbox',body,case)
            assert u32(addr('gFTCustomAnimationValidationFailures'))==0,'Invalid retargeted taunt skeleton'
            # A second real taunt rejects early guard input, then uses the
            # original flag-controlled guard interrupt when that window opens.
            taunt_trace.clear();pulse(0x2000);wait(lambda:u32(fighter()+status_off)==common_statuses['nFTCommonStatusAppeal'],'Second taunt')
            keys(0x20);frames(8);keys(0);assert u32(fighter()+status_off)==common_statuses['nFTCommonStatusAppeal'],'Early taunt guard'
            if cancel is not None and cancel<taunt['duration']:
                wait(lambda:u32(fighter()+flag1_off)!=0,'Original donor cancel window')
                keys(0x20);wait(lambda:u32(fighter()+status_off)!=common_statuses['nFTCommonStatusAppeal'],'Taunt guard cancel');keys(0)
                frames(90)
            else:wait(lambda:u32(fighter()+status_off)==common_statuses['nFTCommonStatusWait'],'Uncancelled taunt ending')
            assert u32(addr('sFTCustomMoveClocks'))!=fighter(),'Stale taunt clock after interruption/recovery'
            if case==0:
                model=u32(fighter()+joints_off+4*4)
                assert max(abs(f32(model+scale_off+j)-v) for j,v in zip((0,4,8),root_bind))<.00002,'Mario growth left behind after guard cancel'
            if case==4:w32(opponent()+pkind_off,1)
            print(f'PASS: taunt body {body}, donor {case}, duration {taunt["duration"]}, cancel {cancel}, source hit windows/fields/contact and cleanup.',flush=True)
        elif args.normal_movement:
            from generateNormalMechanics import catalog as normal_movement_catalog
            check(core.CoreDoCommand(17,4,C.byref(C.c_int(300))))
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            frames(200) # Finish GO before placing either live fighter.
            fp=fighter();cpu=opponent()
            root=u32(u32(fp+gobj_off)+obj_off)+position_off
            cpu_root=u32(u32(cpu+gobj_off)+obj_off)+position_off
            # A human dummy with no input stays behind the attacker; CPU ledge
            # recovery/respawn must not introduce contact or jostle into travel.
            w32(cpu+pkind_off,0);keys_port(u8(cpu+port_off),0)
            origin_y=f32(root+4)
            for donor,variant,attack,status_name in ((1,2,1,'AttackDash'),(8,14,5,'AttackS4')):
                w8(slot+2+attack,donor)
                movement=normal_movement_catalog()[donor][variant]
                assert movement['travel'] and sum(v[0] for v in movement['travel'])>100
                for facing in (1,-1):
                    keys(0);wait(lambda:u32(fp+status_off)==common_statuses['nFTCommonStatusWait'],'Normal movement idle')
                    for offset,value in ((0,-1800*facing),(4,origin_y),(8,0)):
                        wf32(cpu_root+offset,value);wf32(cpu+coll_prev_off+offset,value)
                        wf32(cpu+physics_off+vel_air_off+offset,0)
                    wf32(cpu+physics_off+vel_ground_off,0)
                    # Position only is a fixture; real input chooses facing and starts attacks.
                    for offset,value in ((0,-1000*facing),(4,origin_y),(8,0)):
                        wf32(root+offset,value);wf32(fp+coll_prev_off+offset,value)
                        wf32(fp+physics_off+vel_air_off+offset,0)
                    wf32(fp+physics_off+vel_ground_off,0)
                    keys(((35*facing)&255)<<16);frames(5);keys(0);frames(15)
                    assert s32(fp+lr_off)==facing,('Normal facing',body,donor,facing)
                    normal_movement_trace.clear()
                    if attack==1:
                        keys(((80*facing)&255)<<16)
                        wait(lambda:u32(fp+status_off)==common_statuses['nFTCommonStatusRun'],'Run before dash attack')
                        keys((((80*facing)&255)<<16)|0x80)
                    else:keys((((80*facing)&255)<<16)|0x80)
                    target=common_statuses['nFTCommonStatus'+status_name]
                    wait(lambda:any(r[1]==target for r in normal_movement_trace),'Normal attack started')
                    keys(0)
                    wait(lambda:u32(fp+status_off)==common_statuses['nFTCommonStatusWait'],'Normal donor recovery')
                    rows={int(r[2]):r for r in normal_movement_trace if r[1]==target and r[6]==0}
                    assert len(rows)>=movement['duration']-3,('Normal movement coverage',body,donor,facing,sorted(rows))
                    distance=0
                    for tick,r in rows.items():
                        assert 0<=tick<len(movement['travel']),('Normal movement frame',r)
                        expected=movement['travel'][tick][0]
                        assert abs(r[3]-expected)<.01,('Normal donor velocity',body,donor,facing,tick,r[3],expected)
                        distance+=r[3]
                    assert distance>100,('Stationary borrowed attack',body,donor,facing,distance)
                    assert max(rows)>=movement['duration']-2,('Normal recovery duration',body,donor,facing,max(rows))
                    ordered=sorted(rows.values())
                    for previous,current in zip(ordered,ordered[1:]):
                        if current[0]!=previous[0]+1 or current[2]!=previous[2]+1:continue
                        assert abs(current[4]-previous[4]-current[3]*facing)<.1,('Normal world displacement',body,donor,facing,previous,current)
                    assert u32(addr('sFTCustomMoveClocks'))!=fp,('Stale normal movement clock',body,donor)
                    print(f'PASS: {ROSTER[donor]} {status_name}, body {body}, facing {facing}: {len(rows)} source velocities/world displacement, donor duration and native recovery.',flush=True)
            w32(cpu+pkind_off,1)
        elif args.normal_mechanics:
            # Cap input sampling so short pulses cannot disappear between
            # Python's polls on fast hosts. Speed affects wall time only.
            check(core.CoreDoCommand(17,4,C.byref(C.c_int(300))))
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            fp=fighter();cpu=opponent();cg=u32(cpu+gobj_off);cpu_root=u32(cg+obj_off)+position_off
            human_root=u32(u32(fp+gobj_off)+obj_off)+position_off
            spawn=tuple(f32(human_root+j) for j in (0,4,8));spawn_floor=u32(fp+floor_line_off)
            def recenter():
                # Start each independent donor trial at the native ground spawn.
                # Repeated jab root travel otherwise accumulates toward a ledge.
                for j,value in zip((0,4,8),spawn):
                    wf32(human_root+j,value);wf32(fp+coll_prev_off+j,value)
                w32(fp+floor_line_off,spawn_floor)
                for j in (0,4,8):wf32(fp+physics_off+vel_air_off+j,0)
                wf32(fp+physics_off+vel_ground_off,0)
            def park_cpu():
                wf32(cpu_root,3000);wf32(cpu_root+4,500);w32(cpu+ga_off,air_kind)
            for donor in range(12):
                for i in range(13):w8(slot+2+i,donor)
                recenter();normal_trace.clear();park_cpu()
                for tap in range(24):
                    keys(0x80);frames(3);keys(0);frames(3)
                keys(0);frames(140)
                if donor==5:
                    # Slower presses choose the third slash; mashing chooses
                    # Link's native rapid-jab fork before that follow-up window.
                    check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
                    for gap in (9,12,75):
                        keys(0x80);frames(3);keys(0);frames(gap)
                seen={r[0] for r in normal_trace}
                assert common_statuses['nFTCommonStatusAttack11'] in seen,(body,donor,'jab one',seen)
                if donor==9:
                    assert common_statuses['nFTCommonStatusAttack12'] not in seen,(body,donor,'Pikachu must repeat jab one',seen)
                else:assert common_statuses['nFTCommonStatusAttack12'] in seen,(body,donor,'jab two',seen)
                name=ROSTER[donor];header=(ROOT/'src/ft/ftchar'/('ft'+name.lower())/('ft'+name.lower()+'.h')).read_text()
                statuses=enum_values(header.replace('nFTCommonStatusSpecialStart',str(common_statuses['nFTCommonStatusSpecialStart'])),'ft'+name+'Status')
                if donor in (0,4,5,7,11):
                    third=0xF00 if donor!=body else common_statuses['nFTCommonStatusSpecialStart']
                    assert third in seen,(body,donor,'third jab',seen)
                if donor in (1,5,7,8):
                    loop=0xF02 if donor!=body else statuses['nFT'+name+'StatusAttack100Loop']
                    end=0xF03 if donor!=body else statuses['nFT'+name+'StatusAttack100End']
                    assert loop in seen and end in seen,(body,donor,'rapid loop/release',seen,normal_trace[:32],u32(addr('gFTCustomMoveValidationFailures')),[i for i in range(40) if u32(fp+joints_off+i*4)])
                elif donor==10:
                    # Vanilla Puff has unused rapid descriptors, but jab two
                    # never opens their flag1 gate. Do not invent a new chain.
                    unused={statuses['nFTPurinStatusAttack100'+phase] for phase in ('Start','Loop','End')} if donor==body else set(range(0xF01,0xF04))
                    assert not seen&unused,(body,'Puff native two-jab chain',seen)
                assert u32(fp+status_off)==common_statuses['nFTCommonStatusWait'],(body,donor,'jab recovery',normal_trace[-8:])
                print('PASS: normal jabs body',body,'donor',donor,'native chain, loop/release and recovery',flush=True)
            for i in range(13):w8(slot+2+i,5)
            keys(0);frames(240)
            normal_trace.clear();normal_contact=True;normal_bounced=False
            keys(0x0800);frames(3);keys(0);frames(10);keys(0x80|(176<<24));frames(3);keys(0);frames(140)
            normal_contact=False
            assert normal_bounced,(body,'controlled Link down-air contact/bounce',normal_trace[-12:])
            assert any(r[5]>=39 and r[6] for r in normal_trace),(body,'source bounce velocity/timer')
            print('PASS: body',body,'Link down-air native contact -> bounce/rehit timer',flush=True)
            keys(0);frames(240)
            wait(lambda:u32(fp+status_off)==common_statuses['nFTCommonStatusWait'],'Ground recovery before bat reflection')
            for i in range(13):w8(slot+2+i,11)
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            park_cpu();w32(cpu+pkind_off,0)
            normal_reflect_contact=True;normal_reflected=False
            keys_port(u8(cpu+port_off),0x40);frames(3);keys_port(u8(cpu+port_off),0);frames(24)
            normal_trace.clear()
            keys(0x80|(80<<16));frames(3);keys(0);frames(65)
            normal_reflect_contact=False;w32(cpu+pkind_off,1)
            bat_rows=[r for r in normal_trace if r[0]==common_statuses['nFTCommonStatusAttackS4']]
            assert any(r[8] and r[7] for r in bat_rows),(body,'Ness bat source reflector window',bat_rows,{r[0] for r in normal_trace})
            assert not normal_trace[-1][8],(body,'Ness bat reflector cleanup')
            assert normal_reflected,(body,'controlled native fireball reflection')
            assert u32(addr('gFTCustomMoveValidationFailures'))==0 and u32(addr('gFTCustomAnimationValidationFailures'))==0
            print('PASS: body',body,'Ness bat source window/native fireball reflection/cleanup',flush=True)
        elif args.mario_animations or args.roster_animations:
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
                    assert samples>=(1 if donor==10 else 20) and source_damage<=damage_seen,(body,'Hit-phase coverage',samples,damage_seen,source_damage,
                        [(r,[a[0][0] for a in attacks]) for r,_,_,_,_,_,attacks in superjump_trace if r[0] in paths][:12])
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
        elif args.charge_animations:
            check(core.CoreDoCommand(17,4,C.byref(C.c_int(300))))
            check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
            pulse(0x40);frames(80) # Startup and a partial charge.
            pulse(0x40);frames(100) # Release while charging.
            pulse(0x10);w32(addr('sSC1PTrainingModeMenu'),4);pulse(0x80);frames(50)
            pulse(0x40);frames(400) # Charge fully and store automatically.
            pulse(0x40);frames(120) # Fire the stored full charge.
        else:pulse(0x40);frames(200) # Actual B input and recovery/charging.
        if args.path_donor is None and args.superjump is None and not (args.mario_animations or args.roster_animations or args.normal_mechanics or args.charge_animations or args.taunts):
            pulse(0x20);frames(30) # Store a charge where supported.
            pulse(0x40);frames(120)
        if args.special_animations:
            assert not animation_errors,('Special pose mismatch',animation_errors)
            expected_donor=args.path_donor if args.path_donor is not None else args.superjump if args.superjump is not None else 11 if args.specials else (-1,1,0,4,9,11,7,10,2,3,5,6)[choice]
            if expected_donor>=0 and body!=expected_donor:assert animation_samples>4,('Missing borrowed special poses',body,expected_donor)
            if args.charge_animations:
                required={'Start0','Loop0','End0'}|({'Full0'} if choice==8 else set())
                assert required<={phase for donor,phase in animation_seen},('Charge pose transitions',body,required,animation_seen)
            if animation_seen:print(f'PASS: body {body}, {animation_samples} live special poses, phases {sorted(animation_seen)}.',flush=True)
        if args.path_donor is not None or args.superjump is not None or args.mario_animations or args.roster_animations or args.normal_mechanics or args.taunts:
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
        assert u32(addr('sMNOptionBuilderSlot'))==preset and u32(addr('sMNOptionBuilderEntry'))==24
        action_label='taunts' if args.taunts else 'normal movement' if args.normal_movement else 'normal mechanics' if args.normal_mechanics else 'normal poses' if args.mario_animations or args.roster_animations else 'donor special' if args.path_donor is not None or args.superjump is not None else 'B/store/B'
        print(f'PASS: body {body}, neutral {choice}, preset {preset}: Test -> CSS -> stage -> Training -> {action_label} -> same editor.',flush=True)
    if not args.four_mb:
        if minima:print('PASS: Training heap headroom at least',min(minima),'bytes.',flush=True)
        if u32(addr('sMNOptionBuilderMode'))==2:pulse(0x40)
        wait(lambda:u32(addr('sMNOptionBuilderMode'))==1,'Lab hub for VS')
        transfer=addr('gSCManagerTransferBattleState')
        for player,body in enumerate((0,2,8,9)):
            if args.vs_results and player==0:body=default_build_one[1]
            if args.mario_animations:body=0
            w8(addr('gSCManagerCharBuilderPlayerSlots')+player,player)
            slot=addr('gSCManagerCharBuilderSlots')+player*slot_size
            w8(slot,1);w8(slot+1,body)
            for attack in range(16):w8(slot+2+attack,body)
            w8(slot+taunt_field,(4,0,7,11)[player] if args.taunts else body)
            if args.mario_animations:
                for attack in range(13):w8(slot+2+attack,(1,2,4,7)[player])
            if args.roster_animations:
                for attack in range(13):w8(slot+2+attack,(1,2,4,7)[player])
            if args.normal_mechanics:
                for attack in range(13):w8(slot+2+attack,(1,5,7,11)[player])
            w8(slot+18,args.superjump if args.direct_special in (3,5) else (0,4,0,4)[player] if args.superjump is not None and args.superjump!=10 else body);w8(slot+19,10 if args.superjump==10 else body);w8(slot+neutral_field,(9,10,11,6)[player])
            if args.vs_results and player==0:
                for i,value in enumerate(default_build_one):w8(slot+i,value)
            if args.mechanic is not None:
                w8(slot+18,args.mechanic if args.mechanic_kind=='hi' else body)
                w8(slot+19,args.mechanic if args.mechanic_kind=='lw' else body)
            record=transfer+players_field+player*player_size
            w8(record+pkind_field,0 if player==0 else 1);w8(record+fkind_field,body)
        w8(transfer+man_field,1);w8(transfer+cpu_field,3);w8(transfer+reset_field,0);w8(transfer+stage_field,1)
        if args.vs_results and not args.vs_defaults:w8(transfer+rules_off,2)
        w32(addr('sMNOptionBuilderSlot'),8);pulse(0x80)
        wait(lambda:u8(scene)==16 and u32(addr('sMNPlayersVSTotalTimeTics'))>75,'Four-slot VS select')
        frames(30);heap_ok();pulse(0x10)
        wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'VS stage select')
        pulse(0x80);wait(lambda:u8(scene)==22 and u32(addr('dSYTaskmanUpdateCount'))>240,'Four-slot VS battle')
        if args.vs_defaults:
            battle=u32(addr('gSCManagerBattleState'))
            assert (u8(battle+rules_off),u8(battle+stocks_off),u32(battle+items_off),u8(battle+item_rate_off))==(2,3,0,0),'VS menus lost the default rules'
            for player in range(4):
                record=battle+players_field+player*player_size
                fp=u32(u32(record+player_fighter_off)+user_off)
                assert u8(record+player_stock_off)==u8(fp+fighter_stock_off)==3,('Initial four stocks',player)
        frames(180);heap_ok();pulse(0x40 | ((80 if args.mechanic_kind=='hi' else 176)<<24) if args.mechanic is not None else 0x40 | ((176 if args.superjump==10 else 80)<<24) if args.superjump is not None else 0x40);frames(300 if args.superjump==10 else 160)
        print('PASS: four assigned builds, human/three CPUs: Play VS -> CSS -> stage -> battle/B, upper-bank heap in bounds.',flush=True)
        if args.vs_results:
            battle=u32(addr('gSCManagerBattleState'))
            for player in (1,2,3):
                record=battle+players_field+player*player_size
                fp=u32(u32(record+player_fighter_off)+user_off)
                w8(record+player_stock_off,0);w8(fp+fighter_stock_off,0)
                root=u32(u32(fp+gobj_off)+obj_off)+position_off
                wf32(root,-90000);wf32(fp+coll_prev_off,-90000)
            results_scene=enum_values((ROOT/'src/sc/scdef.h').read_text(),'SCKind')['nSCKindVSResults']
            wait(lambda:u8(scene)==results_scene,'Native stock KOs -> results scene',seconds=20)
            frames(240);remaining=heap_ok()
            assert u32(addr('sMNVSResultsTotalTimeTics'))>120,'Results did not update'
            print('PASS: stock match end -> results/victory fighters; heap headroom',remaining,'bytes.',flush=True)
            wait(lambda:u32(addr('sMNVSResultsTotalTimeTics'))>=u32(addr('sMNVSResultsAllowExitWait')),'Native results input gate')
            pulse(0x10)
            wait(lambda:u8(scene)==16 and u32(addr('sMNPlayersVSTotalTimeTics'))>30,'Results -> VS character select',seconds=20)
            frames(30);heap_ok()
            assert [u8(addr('gSCManagerCharBuilderSlots')+i) for i in range(slot_size)]==default_build_one,'Results changed Build One'
            print('PASS: results Start input -> character select; creator recipe preserved.',flush=True)
            pulse(0x10)
            wait(lambda:u8(scene)==21 and u32(addr('sMNMapsTotalTimeTics'))>30,'Rematch stage select')
            pulse(0x80);wait(lambda:u8(scene)==22 and u32(addr('dSYTaskmanUpdateCount'))>240,'Rematch battle')
            frames(180);heap_ok()
            print('PASS: results -> CSS -> stage -> rematch loads and updates.',flush=True)
finally:
    keys(0);core.CoreDoCommand(6,0,None);thread.join(timeout=3)
