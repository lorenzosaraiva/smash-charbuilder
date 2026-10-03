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

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--core',default='/usr/lib/x86_64-linux-gnu/libmupen64plus.so.2')
parser.add_argument('--rsp',default='/usr/lib/x86_64-linux-gnu/mupen64plus/mupen64plus-rsp-hle.so')
parser.add_argument('--headers',default='/usr/include/mupen64plus')
parser.add_argument('--data',default='/usr/share/mupen64plus')
parser.add_argument('--four-mb',action='store_true')
parser.add_argument('--cases',type=int,default=12)
parser.add_argument('--first-choice',type=int,default=0)
parser.add_argument('--egg-lay',action='store_true',help='Test Egg Lay on every body instead of cycling neutral choices')
args=parser.parse_args()
if not 0<=args.first_choice<12 or not 1<=args.cases<=12-args.first_choice:
    parser.error('Choose a contiguous range within the twelve neutral choices.')
build=ROOT/'build/scene-smoke';build.mkdir(parents=True,exist_ok=True)
subprocess.run(['clang','--target=mips-unknown-none','-c','-EB','-mabi=32','-march=mips2','-ffreestanding','-O1','-I'+str(ROOT/'include'),
                '-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',
                str(ROOT/'tools/emulator/layout.c'),'-o',str(build/'layout.o')],check=True)
data,sections,layout_symbols=read_elf(build/'layout.o','>')
value,length,index=layout_symbols['sSceneSmokeLayout'];start=sections[index][4]+value-sections[index][3]
layout=struct.unpack_from('>'+str(length//4)+'I',data,start)
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
thread=threading.Thread(target=lambda:check(core.CoreDoCommand(5,0,None)),daemon=True)
thread.start()
try:
    wait(lambda:u32(0x80000318)==(0x400000 if args.four_mb else 0x800000),'Boot memory size')
    time.sleep(2)
    check(core.CoreDoCommand(17,5,C.byref(C.c_int(0)))) # Disable core speed limiter.
    # Skip the intro only. From Options onward, use the actual button handlers.
    w8(scene+1,u8(scene));w8(scene,57);w32(addr('sSYTaskmanStatus'),1)
    wait(lambda:u8(scene)==57 and u32(addr('sMNOptionTotalTimeTics'))>30,'Options load')
    w32(addr('sMNOptionOption'),3);pulse(0x80)
    wait(lambda:u32(addr('sMNOptionBuilderMode'))==1,'Lab hub')
    minima=[]
    for case in range(args.first_choice,args.first_choice+args.cases):
        choice=11 if args.egg_lay else case
        if u32(addr('sMNOptionBuilderMode'))==2:pulse(0x40)
        preset=case%4;body=(case+2)%12
        w32(addr('sMNOptionBuilderSlot'),preset)
        slot=addr('gSCManagerCharBuilderSlots')+preset*slot_size
        w8(slot,1);w8(slot+1,body)
        for i in range(16):w8(slot+2+i,body)
        w8(slot+18,body);w8(slot+19,body);w8(slot+neutral_field,choice)
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
        pulse(0x40);frames(200) # Actual B input and recovery/charging.
        pulse(0x20);frames(30) # Store a charge where supported.
        pulse(0x40);frames(120)
        pulse(0x10);frames(12) # Pause, then native Exit button handler.
        w32(addr('sSC1PTrainingModeMenu'),5);pulse(0x80)
        wait(lambda:u8(scene)==57 and u32(addr('sMNOptionBuilderMode'))==2,'Return to editor')
        assert u32(addr('sMNOptionBuilderSlot'))==preset and u32(addr('sMNOptionBuilderEntry'))==23
        print(f'PASS: body {body}, neutral {choice}, preset {preset}: Test -> CSS -> stage -> Training -> B/store/B -> same editor.',flush=True)
    if not args.four_mb:
        print('PASS: Training heap headroom at least',min(minima),'bytes.',flush=True)
        pulse(0x40);wait(lambda:u32(addr('sMNOptionBuilderMode'))==1,'Lab hub for VS')
        transfer=addr('gSCManagerTransferBattleState')
        for player,body in enumerate((0,2,8,9)):
            w8(addr('gSCManagerCharBuilderPlayerSlots')+player,player)
            slot=addr('gSCManagerCharBuilderSlots')+player*slot_size
            w8(slot,1);w8(slot+1,body)
            for attack in range(16):w8(slot+2+attack,body)
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
