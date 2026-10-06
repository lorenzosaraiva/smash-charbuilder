"""Optional Mupen64Plus CPU checks of real Remix Training special input/physics.

Uses isolated saves and null rendering. Scene/preset writes are fixtures; attacks
enter through the actual controller and run native update/map/physics callbacks.
"""
import ctypes as C, threading,time,struct,re,sys,subprocess,math,argparse,faulthandler,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];LAB=ROOT.parent/'ssb-decomp-re'
sys.path.insert(0,str(LAB/'tools'))
from elfData import read_elf
faulthandler.enable()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rom',type=Path)
parser.add_argument('--boot-only',action='store_true')
parser.add_argument('--core',type=Path,help='Mupen64Plus core library with large-ROM support')
parser.add_argument('--headers',type=Path,help='Matching Mupen64Plus API header directory')
parser.add_argument('--body',type=int,choices=range(12),default=0,help='Original fighter body (0 = Mario)')
parser.add_argument('--donor',type=int,choices=range(12),help='Exercise this donor Up/Down B instead of the Kick/Quick Attack regression')
parser.add_argument('--special-side',choices=('both','up','down'),default='both')
parser.add_argument('--falcon-contact',action='store_true',help='Place the CPU in the live Dive hitbox to exercise native capture/release')
args=parser.parse_args()
if args.falcon_contact:assert args.donor==7 and args.special_side in ('both','up')

def constant(name):
    address,length,index=syms[name];section=sections[index]
    return struct.unpack_from('>'+str(length//4)+'I',elf,section[4]+address-section[3])
elf,sections,syms=read_elf(ROOT/'build/char_creator/runtime/runtime.o','>')
layout=constant('ccLayout');special=constant('ccSpecialLayout')
labels={name:int(address,16) for address,name in re.findall(r'^([0-9a-fA-F]{8})\s+(\S+)',(ROOT/'logfile.log').read_text(),re.M)}
native={name:int(address,16) for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);',(LAB/'symbols/symbols_us.txt').read_text(),re.M)}
build=ROOT/'build/char_creator/emulator';build.mkdir(parents=True,exist_ok=True)
source='''#include <sc/scene.h>
#include <ft/fighter.h>
const unsigned int layout[]={__builtin_offsetof(SCCommonData,training_man_fkind),__builtin_offsetof(SCCommonData,training_com_fkind),__builtin_offsetof(SCCommonData,maps_training_gkind),__builtin_offsetof(SCBattleState,players),sizeof(SCPlayerData),__builtin_offsetof(SCPlayerData,fighter_gobj),__builtin_offsetof(FTStruct,item_gobj),__builtin_offsetof(FTStruct,attack_colls),sizeof(FTAttackColl),__builtin_offsetof(FTAttackColl,pos_curr),__builtin_offsetof(FTStruct,percent_damage),__builtin_offsetof(FTStruct,coll_data),sizeof(MPCollData)};
'''
(build/'layout.c').write_text(source)
subprocess.run(['clang','--target=mips-unknown-none','-c','-EB','-mabi=32','-march=mips2','-ffreestanding','-I'+str(ROOT/'build/char_creator/runtime/include'),'-I'+str(LAB/'include'),'-I'+str(LAB/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',str(build/'layout.c'),'-o',str(build/'layout.o')],check=True)
d,s,y=read_elf(build/'layout.o','>');a,l,i=y['layout'];off=s[i][4]+a-s[i][3]
man_off,cpu_off,stage_off,players_off,player_size,fighter_off,item_off,attack_off,attack_size,center_off,percent_off,collision_off,collision_size=struct.unpack_from('>13I',d,off)
unpacked=LAB/'build/emulator/root/usr';library=unpacked/'lib/x86_64-linux-gnu'
headers=args.headers or unpacked/'include/mupen64plus'
input_source=(LAB/'tools/emulator/input.c').read_text().replace('*a=0x20000','*a=0x20100')
(build/'input.c').write_text(input_source)
for name,source in (('input',build/'input.c'),('video',LAB/'tools/emulator/video.c')):
    subprocess.run(['gcc','-shared','-fPIC','-O2','-I'+str(headers),str(source),'-o',str(build/(name+'.so'))],check=True)
core=C.CDLL(str(args.core or library/'libmupen64plus.so.2.0.0'))
core.CoreStartup.argtypes=[C.c_int,C.c_char_p,C.c_char_p,C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p]
core.CoreDoCommand.argtypes=[C.c_int,C.c_int,C.c_void_p];core.CoreAttachPlugin.argtypes=[C.c_int,C.c_void_p]
core.ConfigOpenSection.argtypes=[C.c_char_p,C.POINTER(C.c_void_p)];core.ConfigSetParameter.argtypes=[C.c_void_p,C.c_char_p,C.c_int,C.c_void_p]
core.DebugMemGetPointer.restype=core.DebugGetCPUDataPtr.restype=C.c_void_p
@C.CFUNCTYPE(None,C.c_void_p,C.c_int,C.c_char_p)
def log(ctx,level,message):
    if level in (1,2):print('CORE:',message.decode(),flush=True)
def check(value):assert value==0,('Mupen API',value)
check(core.CoreStartup(0x20001,str(build/'config').encode(),str(unpacked/'share/mupen64plus').encode(),None,log,None,None))
section=C.c_void_p();check(core.ConfigOpenSection(b'Core',C.byref(section)))
for name,typ,value in ((b'R4300Emulator',1,2),(b'DisableExtraMem',3,0),(b'OnScreenDisplay',3,0)):
    check(core.ConfigSetParameter(section,name,typ,C.byref(C.c_int(value))))
saves=build/'saves';saves.mkdir(exist_ok=True)
for name in (b'SaveSRAMPath',b'SaveStatePath',b'ScreenshotPath'):
    check(core.ConfigSetParameter(section,name,4,C.c_char_p(str(saves).encode())))
rom=(args.rom or ROOT/'ssb64asm_extra.z64').read_bytes();buffer=C.create_string_buffer(rom)
check(core.CoreDoCommand(1,len(rom),buffer))
plugins=[]
for typ,path in ((2,build/'video.so'),(3,None),(4,build/'input.so'),(1,library/'mupen64plus/mupen64plus-rsp-hle.so')):
    if path is None:check(core.CoreAttachPlugin(typ,None));continue
    plugin=C.CDLL(str(path));plugin.PluginStartup.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p]
    check(plugin.PluginStartup(core._handle,None,log));check(core.CoreAttachPlugin(typ,plugin._handle));plugins.append(plugin)
keys=plugins[1].LabKeys;ram=core.DebugMemGetPointer(1)
def u8(a):return C.c_uint8.from_address(ram+((a&0x7fffff)^3)).value
def u32(a):return C.c_uint32.from_address(ram+(a&0x7fffff)).value
def f32(a):return C.c_float.from_address(ram+(a&0x7fffff)).value
def w8(a,v):C.c_uint8.from_address(ram+((a&0x7fffff)^3)).value=v
def w32(a,v):C.c_uint32.from_address(ram+(a&0x7fffff)).value=v
def wf32(a,v):C.c_float.from_address(ram+(a&0x7fffff)).value=v
scene=native['gSCManagerSceneData'];updates=native['dSYTaskmanUpdateCount']
def fighter(player=0):
    battle=u32(native['gSCManagerBattleState'])
    if not 0x80000000<=battle<0x80800000:return 0
    gobj=u32(battle+players_off+player_size*player+fighter_off)
    return u32(gobj+0x84) if 0x80000000<=gobj<0x80800000 else 0
trace=[];tracking=False;travel_errors=[];travel_samples=0;falcon_contact_done=False
@C.CFUNCTYPE(None,C.c_uint)
def frame_callback(frame):
    global travel_samples,falcon_contact_done
    if tracking and u8(scene)==54:
        fp=fighter()
        if not 0x80000000<=fp<0x80800000:return
        top=u32(fp+0x8E8);model=u32(fp+0x8E8+16)
        trace.append((u32(fp+0x24),u32(fp+0x28),tuple(f32(top+layout[12]+j) for j in (0,4,8)),
                      tuple(f32(model+layout[14]+j) for j in (0,4,8)),tuple(f32(fp+special[1]+j) for j in (0,4,8))))
        if args.falcon_contact and u32(fp+0x24) in (235,238) and u32(fp+attack_off):
            cpu=fighter(1)
            if cpu:
                target=u32(cpu+0x8E8)+layout[12];center=fp+attack_off+center_off
                for j in (0,4,8):wf32(target+j,f32(center+j)-(200 if j==4 else 0))
                w32(cpu+layout[2],layout[29]);falcon_contact_done=True
        clock=labels['CharLabRuntime.sCCSpecialClocks'];path=u32(clock+28)
        if u32(clock)==fp and u32(clock+12)==7 and u32(fp+0x14C)==0 and path:
            travel=u32(path+44)
            if travel:
                tick=max(0,min(int(f32(clock+20)),u32(path+32)-1))
                expected=f32(travel+tick*16)
                actual=f32(fp+special[2])
                if abs(expected-actual)>.004:travel_errors.append((u32(fp+0x28),tick,expected,actual))
                if abs(expected)>1:travel_samples+=1
check(core.CoreDoCommand(15,0,C.cast(frame_callback,C.c_void_p)))
thread=threading.Thread(target=lambda:check(core.CoreDoCommand(5,0,None)),daemon=True);thread.start()
def diagnostic():
    fault=u32(native['__osFaultedThread'])
    return dict(scene=u8(scene),updates=u32(updates),pc=hex(C.c_uint32.from_address(core.DebugGetCPUDataPtr(1)).value),fault=hex(fault),context=[hex(u32(fault+j)) for j in (0x118,0x11c,0x120,0x124,0x128)] if fault else [],fighter=hex(fighter()),trace=trace[-8:])
def wait(predicate,label,seconds=20):
    end=time.monotonic()+seconds
    while not predicate():
        if time.monotonic()>end:raise AssertionError((label,diagnostic()))
        time.sleep(.002)
def frames(n):
    tick=u32(updates);wait(lambda:u32(updates)>=tick+n,'Frames stopped')
def pulse(value,n=3):keys(value);frames(n);keys(0);frames(3)
try:
    print('BOOT: starting CPU.',flush=True)
    time.sleep(2);ram=core.DebugMemGetPointer(1)
    assert ram, 'Core did not initialize RDRAM'
    wait(lambda:u32(updates)>30,'Cold boot',seconds=90)
    check(core.CoreDoCommand(17,5,C.byref(C.c_int(0))))
    print('BOOT:',diagnostic(),flush=True)
    if args.boot_only:
        time.sleep(8);print('BOOT:',diagnostic(),flush=True);raise SystemExit(0)
    # Change scenes only after real Start inputs reach the stable main menu.
    # Writing a destination while the opening overlay is still loading can
    # invalidate an asynchronous asset load and is not a gameplay regression.
    keys(0x10);wait(lambda:u8(scene) in (1,7),'Skip intro with Start',seconds=40);keys(0)
    if u8(scene)==1:
        frames(180);pulse(0x10);wait(lambda:u8(scene)==7,'Title Start',seconds=40)
    frames(40)
    check(core.CoreDoCommand(7,0,None))
    state=C.c_int()
    def paused():
        check(core.CoreDoCommand(9,1,C.byref(state)));return state.value==3
    wait(paused,'Pause before Training fixture')
    # Retain source recipe defaults except the two selected special donors.
    table=u32(labels['CharCreator.slot_tables'])
    for i in range(21):w32(u32(table+i*4),0)
    w32(u32(table),1);w32(u32(table+4),args.body)
    w32(u32(table+16*4),args.donor if args.donor is not None else 9)
    w32(u32(table+17*4),args.donor if args.donor is not None else 7)
    w32(labels['CharCreator.selected_builds'],1)
    w8(scene+man_off,args.body);w8(scene+cpu_off,8);w8(scene+stage_off,6)
    w8(scene+1,u8(scene));w8(scene,54);w32(native['sSYTaskmanStatus'],1)
    check(core.CoreDoCommand(8,0,None))
    wait(lambda:u8(scene)==54 and fighter() and u32(updates)>240,'Training load',seconds=60)
    check(core.CoreDoCommand(17,4,C.byref(C.c_int(120))))
    check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
    frames(180);wait(lambda:u32(fighter()+0x24)==10,'Mario idle')
    start_top=u32(fighter()+0x8E8)
    start_position=tuple(f32(start_top+layout[12]+j) for j in (0,4,8))
    collision_fixture=C.string_at(ram+((fighter()+collision_off)&0x7fffff),collision_size)
    initial_kinetics=u32(fighter()+layout[2])
    print('PASS: Remix Training loads body',args.body,'with donor',args.donor if args.donor is not None else 'Kick/Quick Attack','; no CPU fault.',flush=True)
    moves=(('Falcon Kick',0x40|(176<<24)),('Quick Attack',0x40|(80<<24)))
    if args.donor is not None:
        moves=tuple((name,button) for name,button,side in (('Donor Up B',0x40|(80<<24),'up'),('Donor Down B',0x40|(176<<24),'down')) if args.special_side in ('both',side))
    for name,button in moves:
        fp=fighter();top=u32(fp+0x8E8);model=u32(fp+0x8E8+16)
        # Position/collision state is a fixture, like the Training scene itself.
        # Restore the original floor and swept-position caches as well as the
        # coordinates, so a ledge landing cannot become the next launch site.
        check(core.CoreDoCommand(7,0,None));wait(paused,'Pause between casts')
        C.memmove(ram+((fp+collision_off)&0x7fffff),collision_fixture,collision_size)
        w32(fp+layout[2],initial_kinetics)
        for j,value in zip((0,4,8),start_position):
            wf32(top+layout[12]+j,value);wf32(fp+special[1]+j,0);wf32(fp+special[2]+j,0)
        check(core.CoreDoCommand(8,0,None));frames(3)
        initial_scale=tuple(f32(model+layout[14]+j) for j in (0,4,8))
        cast_position=tuple(f32(top+layout[12]+j) for j in (0,4,8))
        trace.clear();tracking=True;pulse(button)
        if name=='Quick Attack':
            wait(lambda:u32(fighter()+0x24) in (special[5],special[7]),'First Quick Attack endpoint')
            # Aim the second zip back down toward the launch platform. A
            # horizontal full-strength zip legitimately exits this stage's
            # floor and cannot serve as a no-KO recovery regression.
            keys(176<<24);frames(12);keys(0)
        wait(lambda:u32(fighter()+0x24)==10 and any(row[0]>=220 for row in trace),'Special recovery/landing',seconds=30)
        frames(3);tracking=False
        if args.donor==5 and name=='Donor Down B':
            assert u32(fighter()+item_off),('Link did not create a held bomb',diagnostic())
            trace.clear();tracking=True;pulse(button)
            wait(lambda:u32(fighter()+0x24)==10 and not u32(fighter()+item_off),'Bomb throw recovery',seconds=30)
            frames(3);tracking=False
            assert not u32(fighter()+item_off),('Held bomb not released',diagnostic())
            assert any(row[0] in (constant('ccPairedSpecialLayout')[4],constant('ccPairedSpecialLayout')[5]) for row in trace),('Common bomb throw not entered',diagnostic())
            print('PASS: Link second Down B enters common bomb throw and releases the held item.',flush=True)
        (build/('trace-'+str(args.body)+'-'+str(args.donor)+'-'+name.replace(' ','-')+'.json')).write_text(json.dumps(trace))
        assert trace and (any(row[0]>=220 for row in trace) or (args.donor==5 and name=='Donor Down B')),('Special not entered',name,diagnostic())
        assert math.dist(trace[0][2],cast_position)<250,('Special entry moved the world root',name,cast_position,trace[0],diagnostic())
        assert not u32(native['__osFaultedThread']),('CPU fault',name,diagnostic())
        if name=='Falcon Kick' and args.body!=7:
            assert travel_samples>=5 and not travel_errors,('Kick differs from source travel',travel_samples,travel_errors[:8])
        if name=='Quick Attack':
            saw_end=False;second=False
            for row in trace:
                if row[0] in (special[5],special[7]):saw_end=True
                if saw_end and row[0] in (special[4],special[6]):second=True
            assert second,('Second Quick Attack dash not entered',diagnostic())
        assert all(math.isfinite(v) and abs(v)<50000 for row in trace for v in row[2]),('Bad position',name,diagnostic())
        assert not any(row[0] in (0,7,8,9) for row in trace),('Cast ended with KO/respawn',name,diagnostic())
        if not (args.body==9 and name=='Quick Attack'):
            # Kirby's native ledge climb squashes/stretches his body. Enforce
            # scale during borrowed phases and final idle, allowing body-owned
            # landing/cliff animation tracks to keep their original behavior.
            assert all(max(abs(a-b) for a,b in zip(row[3],initial_scale))<.001 for row in trace if row[0]>=220 or row[0]==10),('Borrowed/final body scale changed',name,diagnostic())
        distance=max(math.dist(row[2],trace[0][2]) for row in trace)
        if args.donor is None:assert distance>100,('Special missing travel',name,distance,diagnostic())
        wait(lambda:u32(fighter()+0x24)==10,'Special recovery/landing',seconds=20)
        assert u32(fighter()+8)==args.body,('Donor identity not restored',name)
        if args.falcon_contact and name=='Donor Up B':
            assert falcon_contact_done and any(row[0]==236 for row in trace),('Dive capture missing',diagnostic())
            assert any(row[0]==237 for row in trace),('Dive release missing',diagnostic())
            assert u32(fighter(1)+percent_off)>=20,('Dive throw damage missing',diagnostic())
            print('PASS: controlled live Dive hitbox contact enters native capture, paired release and throw damage.',flush=True)
        print('PASS:',name,'real B input, native callbacks, stable body scale, movement and recovery; travel',round(distance,2),'statuses',sorted(set(row[0] for row in trace)),flush=True)
    print('PASS: live Remix CPU special checks (null rendering).',flush=True)
    report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'donor':args.donor,'checks':['Training load',*[name+' input/recovery' for name,_ in moves],'body scale/identity'],'rendering':'null','kick_source_samples':travel_samples}
    if args.falcon_contact:report['controlled_dive_contact']='native capture, release and throw damage passed'
    report_name='cpu-scenes.json' if args.donor is None else f'cpu-scenes-{args.body}-{args.donor}-{args.special_side}.json'
    if args.falcon_contact:report_name=report_name.replace('.json','-contact.json')
    (build/report_name).write_text(json.dumps(report,indent=2)+'\n')
finally:
    keys(0);core.CoreDoCommand(6,0,None);thread.join(timeout=3)
