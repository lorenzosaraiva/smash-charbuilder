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
parser.add_argument('--bomb-count',action='store_true',help='Count actual Samus Bomb births across two grounded and two aerial Down B inputs')
parser.add_argument('--falcon-contact',action='store_true',help='Place the CPU in the live Dive hitbox to exercise native capture/release')
parser.add_argument('--editor-test',action='store_true',help='Enter the editor, activate Test in Training with A, then return with B')
parser.add_argument('--editor-slot',type=int,choices=range(1,5),default=1)
parser.add_argument('--editor-play',action='store_true',help='Continue editor Test through CSS Start and stage confirmation into Training')
parser.add_argument('--normal-mechanics',action='store_true',help='Exercise donor jab3/rapid phases and controlled live Link down-air contact')
parser.add_argument('--normal-animations',type=int,choices=range(12),help='Borrow this donor for normals and check real A-input pose streaming')
parser.add_argument('--down-smash',action='store_true',help='Focus normal regression on a real down-smash input')
parser.add_argument('--neutral',type=int,choices=range(1,13),help='Exercise a Neutral B choice with real controller input')
parser.add_argument('--inhale-contact',action='store_true',help='Check live inhale capture, spit, repeat capture, copy and copied Neutral B')
parser.add_argument('--inhale-held-l',action='store_true',help='Exercise L with a swallowed fighter before the ordinary inhale/copy sequence')
parser.add_argument('--full-charge',action='store_true',help='Charge borrowed Giant Punch fully and check its native stored blink through movement and release')
parser.add_argument('--egg-contact',action='store_true',help='Place the CPU in Egg Lay reach to test capture, egg handoff and damage')
parser.add_argument('--projectile-contact',action='store_true',help='Place the CPU at a PK Fire spark to test native flame-pillar creation')
parser.add_argument('--visuals',action='store_true',help='Check real effect/model allocation, finite transforms and recovery cleanup (null renderer)')
parser.add_argument('--paired-donor',type=int,choices=range(12),help='Real grab/contact and forward/back release with this grab donor')
parser.add_argument('--paired-miss',action='store_true',help='Exercise full missed tether extension/retraction and cleanup')
parser.add_argument('--tether-materials',action='store_true',help='Check native Samus beam texture clock during a missed borrowed grab (null renderer)')
parser.add_argument('--throw-donor',type=int,choices=range(12),help='Independent throw donor for paired tests')
parser.add_argument('--back-throw',action='store_true')
parser.add_argument('--paired-airborne',action='store_true',help='Raise the captured pair to exercise the fall phase before landing')
parser.add_argument('--cargo-jump',action='store_true',help='Walk and jump with a DK cargo victim, then toss in the air')
parser.add_argument('--taunt-donor',type=int,choices=range(12),help='Real L input, source taunt duration and cancellation')
parser.add_argument('--run-id',help='Isolated emulator workspace for independent CPU checks')
parser.add_argument('--stage',type=int,choices=range(9),default=6)
parser.add_argument('--edge',choices=('grounded-only','dk-single','dk-repeat','ness-launch','thunder-contact','reflect','absorb','sing','rest','air-land','interrupt','quick-wall','quick-ledge','slope'),help='Controlled contact/transition regression')
args=parser.parse_args()
if args.edge:
    args.donor={'grounded-only':2,'dk-single':2,'dk-repeat':2,'ness-launch':11,'thunder-contact':9,'reflect':1,'absorb':11,'sing':10,'rest':10,'air-land':0,'interrupt':11,'quick-wall':9,'quick-ledge':9,'slope':7}[args.edge]
if args.falcon_contact:assert args.donor==7 and args.special_side in ('both','up')
if args.bomb_count:assert args.donor==3 and args.special_side=='down'
if args.editor_play:assert args.editor_test
if args.normal_mechanics:assert args.normal_animations is not None
if args.down_smash:assert args.normal_animations is not None
if args.paired_miss:assert args.paired_donor is not None
if args.tether_materials:assert args.paired_miss and args.paired_donor==3 and args.body!=3
if args.egg_contact:assert args.neutral==11
if args.projectile_contact:assert args.neutral==5
if args.full_charge:assert args.neutral==8 and args.body!=2
if args.inhale_contact:assert args.neutral==12
if args.inhale_held_l:assert args.inhale_contact

def constant(name):
    address,length,index=syms[name];section=sections[index]
    return struct.unpack_from('>'+str(length//4)+'I',elf,section[4]+address-section[3])
elf,sections,syms=read_elf(ROOT/'build/char_creator/runtime/runtime.o','>')
layout=constant('ccLayout');special=constant('ccSpecialLayout')
labels={name:int(address,16) for address,name in re.findall(r'^([0-9a-fA-F]{8})\s+(\S+)',(ROOT/'logfile.log').read_text(),re.M)}
native={name:int(address,16) for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);',(LAB/'symbols/symbols_us.txt').read_text(),re.M)}
report_directory=ROOT/'build/char_creator/emulator'
if args.run_id:assert re.fullmatch(r'[a-z0-9_-]+',args.run_id)
build=report_directory/args.run_id if args.run_id else report_directory
build.mkdir(parents=True,exist_ok=True)
source='''#include <sc/scene.h>
#include <ft/fighter.h>
#include <wp/weapon.h>
const unsigned int layout[]={__builtin_offsetof(SCCommonData,training_man_fkind),__builtin_offsetof(SCCommonData,training_com_fkind),__builtin_offsetof(SCCommonData,maps_training_gkind),__builtin_offsetof(SCBattleState,players),sizeof(SCPlayerData),__builtin_offsetof(SCPlayerData,fighter_gobj),__builtin_offsetof(FTStruct,item_gobj),__builtin_offsetof(FTStruct,attack_colls),sizeof(FTAttackColl),__builtin_offsetof(FTAttackColl,pos_curr),__builtin_offsetof(FTStruct,percent_damage),__builtin_offsetof(FTStruct,coll_data),sizeof(MPCollData),__builtin_offsetof(SCCommonData,player),__builtin_offsetof(SCCommonData,training_man_costume),__builtin_offsetof(SCCommonData,training_com_costume)};
const unsigned int egg_statuses[]={nFTCommonStatusCaptureYoshi,nFTCommonStatusYoshiEgg};
const unsigned int material_layout[]={__builtin_offsetof(DObj,mobj),__builtin_offsetof(MObj,anim_frame),__builtin_offsetof(MObj,texture_id_curr)};
const unsigned int edge_layout[]={__builtin_offsetof(WPStruct,kind),__builtin_offsetof(WPStruct,owner_gobj),__builtin_offsetof(WPStruct,reflect_gobj),__builtin_offsetof(WPStruct,absorb_gobj),__builtin_offsetof(WPStruct,physics.vel_air),__builtin_offsetof(FTStruct,status_vars.ness.specialhi.pkjibaku_delay),__builtin_offsetof(MPCollData,pos_prev),__builtin_offsetof(FTStruct,hitstatus),nFTCommonStatusFuraSleep,nFTNessStatusSpecialHiHold,nFTNessStatusSpecialAirHiHold,nFTNessStatusSpecialHiJibaku,nFTNessStatusSpecialAirHiJibaku,nFTPikachuStatusSpecialLwHit,nFTPikachuStatusSpecialAirLwHit,nFTDonkeyStatusSpecialLwLoop,nFTMarioStatusSpecialLw,nFTMarioStatusSpecialAirLw,__builtin_offsetof(FTStruct,input.controller),sizeof(SYController),__builtin_offsetof(MPCollData,floor_line_id),nGMHitStatusIntangible,nGMHitStatusNormal};
const unsigned int edge_stage[]={sizeof(MPVertexInfo),sizeof(MPVertexData),__builtin_offsetof(DObj,user_data),__builtin_offsetof(DObj,anim_joint.event32),__builtin_offsetof(MPCollData,mask_curr),__builtin_offsetof(MPCollData,mask_stat),__builtin_offsetof(MPCollData,map_coll.center),__builtin_offsetof(MPCollData,floor_angle),MAP_FLAG_LWALL|MAP_FLAG_RWALL,MAP_FLAG_CLIFF_MASK,nFTCommonStatusCliffCatch,nFTCommonStatusCliffWait,MAP_VERTEX_COLL_CLIFF,__builtin_offsetof(SCCommonData,gkind)};
FTStruct reflect_bits={.is_reflect=TRUE},absorb_bits={.is_absorb=TRUE};
'''
(build/'layout.c').write_text(source)
subprocess.run(['clang','--target=mips-unknown-none','-c','-EB','-mabi=32','-march=mips2','-ffreestanding','-I'+str(ROOT/'build/char_creator/runtime/include'),'-I'+str(LAB/'include'),'-I'+str(LAB/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',str(build/'layout.c'),'-o',str(build/'layout.o')],check=True)
d,s,y=read_elf(build/'layout.o','>');a,l,i=y['layout'];off=s[i][4]+a-s[i][3]
man_off,cpu_off,stage_off,players_off,player_size,fighter_off,item_off,attack_off,attack_size,center_off,percent_off,collision_off,collision_size,port_off,man_costume_off,cpu_costume_off=struct.unpack_from('>16I',d,off)
a,l,i=y['egg_statuses'];egg_statuses=struct.unpack_from('>2I',d,s[i][4]+a-s[i][3])
a,l,i=y['material_layout'];material_layout=struct.unpack_from('>3I',d,s[i][4]+a-s[i][3])
a,l,i=y['edge_layout'];edge_layout=struct.unpack_from('>'+str(l//4)+'I',d,s[i][4]+a-s[i][3])
a,l,i=y['edge_stage'];edge_stage=struct.unpack_from('>'+str(l//4)+'I',d,s[i][4]+a-s[i][3])
edge_bits={}
for name in ('reflect','absorb'):
    a,l,i=y[name+'_bits'];raw=d[s[i][4]+a-s[i][3]:s[i][4]+a-s[i][3]+l]
    edge_bits[name]=next((j,v) for j,v in enumerate(raw) if v)
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
tether_material_samples=[]
animation_samples=0;animation_records=set();animation_errors=[]
normal_fields=constant('ccNormalLayout');link_contact_done=False;link_bounce_samples=0
egg_contact_done=False;egg_observed=set();neutral_samples=[]
inhale_capture=False;inhale_observed=set();inhale_choices=set();inhale_victims=set()
inhale_visual_samples={'wind':0};inhale_visual_errors=[];inhale_wind_diagnostics=set();inhale_source_checks=set()
visual_layout=constant('ccVisualLayout')
visual_objects=set();visual_samples=0;visual_hidden=False;visual_errors=[]
charge_visual_samples=[];ball_samples=[]
pair_contact=False;pair_samples=[];taunt_samples=[]
weapon_kinds=set();item_kinds=set();projectile_contact_done=False
bomb_live=set();bomb_births=[];bomb_casts=[]
@C.CFUNCTYPE(None,C.c_uint)
def frame_callback(frame):
    global travel_samples,falcon_contact_done,animation_samples,link_contact_done,link_bounce_samples,egg_contact_done,projectile_contact_done,visual_samples,visual_hidden,pair_contact
    if tracking and u8(scene)==54:
        fp=fighter()
        if not 0x80000000<=fp<0x80800000:return
        if args.edge and 'edge_tick' in globals():edge_tick()
        if args.visuals:
            vs=labels['CharLabRuntime.sCCVisualStates']
            if u32(vs)==fp:
                visual_hidden|=bool(u32(vs+visual_layout[4]))
                for field in visual_layout[1:4]:
                    obj=u32(vs+field)
                    if not obj:continue
                    # Native SetStatus may eject attachments between this
                    # port's visual updates. The sidecar validates membership
                    # on its next tick; do not dereference that stale handle.
                    live=u32(native['gGCCommonLinks']+24)
                    for _ in range(256):
                        if not live or live==obj:break
                        live=u32(live+visual_layout[7])
                    if live!=obj:continue
                    user=u32(obj+0x84);dobj=u32(obj+layout[10])
                    if not user or u32(user+4)!=u32(fp+visual_layout[8]):visual_errors.append(('owner',hex(obj)))
                    if not dobj:visual_errors.append(('model',hex(obj)));continue
                    for offset in layout[12:15]:
                        values=tuple(f32(dobj+offset+j) for j in (0,4,8))
                        if not all(math.isfinite(v) and abs(v)<50000 for v in values):visual_errors.append(('transform',hex(obj),values))
                    visual_objects.add(obj);visual_samples+=1
                if args.donor==3:
                    obj=u32(vs+visual_layout[1]);clock=labels['CharLabRuntime.sCCSpecialClocks']
                    if obj and u32(vs+visual_layout[4]) and u32(clock)==fp:
                        dobj=u32(obj+layout[10]);draw=constant('ccVisualDrawLayout');mat=constant('ccVisualMaterialLayout')
                        m=u32(dobj+mat[1]);ci=constant('ccChargeVisualLayout')
                        ball_samples.append((f32(clock+20),f32(dobj+layout[12]+4),u32(dobj+draw[0]),u8(dobj+visual_layout[5]),u32(m+ci[7]) if m else 0))
        if args.full_charge:
            ci=constant('ccChargeVisualLayout');col=fp+ci[0]
            charge_visual_samples.append((u32(fp+0x24),u32(col),u32(col+4),u32(labels['CharLabRuntime.sFTCharBuilderNeutralStates']+16)))
        top=u32(fp+0x8E8);model=u32(fp+0x8E8+16)
        trace.append((u32(fp+0x24),u32(fp+0x28),tuple(f32(top+layout[12]+j) for j in (0,4,8)),
                      tuple(f32(model+layout[14]+j) for j in (0,4,8)),tuple(f32(fp+special[1]+j) for j in (0,4,8))))
        if args.bomb_count:
            live=set();g=u32(native['gGCCommonLinks']+5*4)
            for _ in range(64):
                if not 0x80000000<=g<0x80800000:break
                wp=u32(g+0x84)
                if 0x80000000<=wp<0x80800000 and u32(wp+edge_layout[0])==3 and u32(wp+edge_layout[1])==u32(fp+visual_layout[8]):
                    live.add(g)
                g=u32(g+4)
            clock=labels['CharLabRuntime.sCCSpecialClocks']
            for g in sorted(live-bomb_live):
                bomb_births.append({'update':u32(updates),'weapon':hex(g),'status':u32(fp+0x24),
                                    'source_frame':f32(clock+20) if u32(clock)==fp else None,
                                    'animation_frame':f32(u32(fp+visual_layout[8])+layout[11])})
            bomb_live.clear();bomb_live.update(live)
        if args.paired_donor is not None or args.taunt_donor is not None:
            clock=labels['CharLabRuntime.sFTCustomMoveClocks']
            tick=f32(clock+24) if u32(clock)==fp else -1
            if args.tether_materials and u32(fp+0x24)==166:
                g=u32(labels['CharLabRuntime.sFTCustomPairProps']+8)
                if g:
                    m=u32(u32(g+layout[10])+material_layout[0])
                    if m:
                        index=u8(m+material_layout[2])*256+u8(m+material_layout[2]+1)
                        tether_material_samples.append((tick,f32(m+material_layout[1]),index))
            cpu=fighter(1)
            if cpu:
                held=u32(fp+layout[17]);capture=u32(cpu+layout[18])
                pair_samples.append((u32(fp+0x24),u32(cpu+0x24),tick,held,capture,u32(cpu+percent_off)))
                if args.paired_donor is not None and not args.paired_miss and not held and u32(fp+attack_off)>=2:
                    center=fp+attack_off+center_off;target=u32(cpu+0x8E8)+layout[12]
                    for j in (0,4,8):wf32(target+j,f32(center+j)-(200 if j==4 else 0))
                    w32(cpu+layout[2],layout[29]);pair_contact=True
            taunt_samples.append((u32(fp+0x24),tick,u32(fp+0x180),tuple(f32(model+layout[14]+j) for j in (0,4,8)),u32(fp+attack_off),f32(model+layout[12]+4)))
        if args.neutral is not None:
            state=labels['CharLabRuntime.sFTCharBuilderNeutralStates']
            if u32(state)==fp:neutral_samples.append(tuple(u32(state+j) for j in (12,16,20,24)))
            # Native common links: weapon=5, item=4; these GObj/user_data ABI
            # offsets are shared with the production loader and fighter ABI.
            for link,kinds in ((5,weapon_kinds),(4,item_kinds)):
                g=u32(native['gGCCommonLinks']+link*4)
                for _ in range(64):
                    if not 0x80000000<=g<0x80800000:break
                    user=u32(g+0x84)
                    if 0x80000000<=user<0x80800000:
                        kind=u32(user+12);kinds.add(kind)
                        if args.projectile_contact and link==5 and kind==13 and not projectile_contact_done:
                            cpu=fighter(1);obj=u32(g+layout[10])
                            if cpu and obj:
                                target=u32(cpu+0x8E8)+layout[12]
                                for j in (0,4,8):wf32(target+j,f32(obj+layout[12]+j)-(80 if j==4 else 0))
                                w32(cpu+layout[2],layout[29]);projectile_contact_done=True
                    g=u32(g+4)
        if args.egg_contact:
            cpu=fighter(1)
            if cpu:
                egg_observed.add(u32(cpu+0x24))
                if not egg_contact_done and u32(fp+attack_off):
                    target=u32(cpu+0x8E8)+layout[12];center=fp+attack_off+center_off
                    for j in (0,4,8):wf32(target+j,f32(center+j)-(200 if j==4 else 0))
                    w32(cpu+layout[2],layout[29]);egg_contact_done=True
        if args.inhale_contact:
            iv=constant('ccInhaleVisualLayout')
            si=labels['CharLabRuntime.sCCInhaleStates']
            inhale_wind_diagnostics.add((u32(fp+0x24),u32(fp+layout[3]),u32(labels['CharLabRuntime.sCCNeutralParticleBanks']+8),u32(si+iv[0])))
            for name,field in (('wind',iv[0]),):
                effect=u32(si+field)
                live=u32(native['gGCCommonLinks']+24)
                for _ in range(256):
                    if not live or live==effect:break
                    live=u32(live+visual_layout[7])
                if not effect or live!=effect:continue
                bank=u32(labels['CharLabRuntime.sCCNeutralParticleBanks']+8)
                if bank not in inhale_source_checks:
                    lo=u32(u32(0x80116E10+8*4)+0x50)
                    offset=int.from_bytes(rom[lo+4+12*4:lo+8+12*4],'big')
                    script=u32(u32(0x800D6400+bank*4)+12*4)
                    actual=bytes(u8(script+j) for j in range(64))
                    if actual!=rom[lo+offset:lo+offset+64]:
                        inhale_visual_errors.append(('Wind source bank mismatch',bank,actual.hex()))
                    inhale_source_checks.add(bank)
                ep=u32(effect+0x84);xf=u32(ep+iv[2])
                values=[f32(xf+iv[3]+j) for j in (0,4,8)] if xf else [float('nan')]
                if not all(math.isfinite(v) and abs(v)<50000 for v in values):inhale_visual_errors.append((name,values))
                inhale_visual_samples[name]+=1
            cpu=fighter(1);il=constant('ccInhaleLayout')
            inhale_observed.add(u32(fp+0x24))
            state=labels['CharLabRuntime.sCCInhaleStates']
            if u32(state)==fp:inhale_choices.add(u32(state+il[1]))
            if cpu:
                inhale_victims.add(u32(cpu+0x24))
                if inhale_capture and u32(fp+0x24) in (il[5],il[12]) and u32(fp+attack_off):
                    target=u32(cpu+0x8E8)+layout[12];center=fp+attack_off+center_off
                    for j in (0,4,8):wf32(target+j,f32(center+j)-(100 if j==4 else 0))
                    w32(cpu+layout[2],layout[29])
        record=u32(labels['CharLabRuntime.sCCAnimationLoaded'])
        clock=labels['CharLabRuntime.sFTCustomMoveClocks']
        special_clock=labels['CharLabRuntime.sCCSpecialClocks']
        if record and (u32(clock)==fp or u32(special_clock)==fp):
            clip=labels['CharLabRuntime.sCCAnimationClips']
            count=u32(clip+20)
            if not (0<count<=256):animation_errors.append(('bad clip',hex(record),count))
            for joint in range(4,37):
                obj=u32(fp+0x8E8+joint*4)
                if obj:
                    rotation=tuple(f32(obj+layout[13]+j) for j in (0,4,8))
                    if not all(math.isfinite(v) and abs(v)<10 for v in rotation):animation_errors.append(('bad joint',joint,rotation))
            animation_samples+=1;animation_records.add(record)
        if args.falcon_contact and u32(fp+0x24) in (235,238) and u32(fp+attack_off):
            cpu=fighter(1)
            if cpu:
                target=u32(cpu+0x8E8)+layout[12];center=fp+attack_off+center_off
                for j in (0,4,8):wf32(target+j,f32(center+j)-(200 if j==4 else 0))
                w32(cpu+layout[2],layout[29]);falcon_contact_done=True
        if args.normal_mechanics and args.normal_animations==5 and u32(fp+0x24)==normal_fields[24]:
            if u32(fp+normal_fields[13]) and f32(fp+special[1]+4)>30:link_bounce_samples+=1
            if not link_contact_done and u32(fp+attack_off):
                cpu=fighter(1)
                if cpu:
                    target=u32(cpu+0x8E8)+layout[12];center=fp+attack_off+center_off
                    for j in (0,4,8):wf32(target+j,f32(center+j)-(200 if j==4 else 0))
                    w32(cpu+layout[2],layout[29]);link_contact_done=True
        clock=labels['CharLabRuntime.sCCSpecialClocks'];path=u32(clock+28)
        if u32(clock)==fp and u32(clock+12)==7 and u32(fp+0x14C)==0 and path:
            travel=u32(path+44)
            if travel:
                tick=max(0,min(int(f32(clock+20)),u32(path+32)-1))
                expected=f32(travel+tick*16)
                facing=u32(fp+0x44);facing=facing if facing<0x80000000 else facing-0x100000000
                if facing*f32(top+layout[13]+4)<0:expected=-expected
                actual=f32(fp+special[2])
                if abs(expected-actual)>.004:travel_errors.append((u32(fp+0x28),tick,expected,actual))
                if abs(expected)>1:travel_samples+=1
check(core.CoreDoCommand(15,0,C.cast(frame_callback,C.c_void_p)))
thread=threading.Thread(target=lambda:check(core.CoreDoCommand(5,0,None)),daemon=True);thread.start()
def diagnostic():
    fault=u32(native['__osFaultedThread'])
    pc_pointer=core.DebugGetCPUDataPtr(1)
    data=dict(scene=u8(scene),updates=u32(updates),pc=hex(C.c_uint32.from_address(pc_pointer).value) if pc_pointer else 'unavailable',fault=hex(fault),context=[hex(u32(fault+j)) for j in (0x118,0x11c,0x120,0x124,0x128)] if fault else [],fighter=hex(fighter()),trace=trace[-8:])
    if fault:
        (build/'fault-ram.bin').write_bytes(C.string_at(ram,0x800000))
        data['registers']={name:hex(u32(fault+offset)) for name,offset in [('v0',0x2C),('a0',0x3C),('a1',0x44),('a2',0x4C),('s0',0x9C),('s1',0xA4),('sp',0xF4),('ra',0x104)]}
        fp=fighter()
        if 0x80000000<=fp<0x807FF000:
            data['fault_fighter']={name:hex(u32(fp+offset)) for name,offset in [('kind',8),('status',0x24),('attr',0x9C8),('textures',0x9BC)]}
            data['normal_donor']=hex(u32(labels['CharCreator.active_normal_donor']))
            data['normal_clock']=[hex(u32(labels['CharLabRuntime.sFTCustomMoveClocks']+j)) for j in range(0,40,4)]
        stack=u32(fault+0xF4)
        if 0x80000000<=stack<0x807FFE00:
            data['stack']=[hex(u32(stack+j)) for j in range(0,128,4)]
    return data
def wait(predicate,label,seconds=20):
    end=time.monotonic()+seconds
    while not predicate():
        if time.monotonic()>end:
            (build/'timeout-ram.bin').write_bytes(C.string_at(ram,0x800000))
            raise AssertionError((label,diagnostic()))
        time.sleep(.002)
def frames(n):
    tick=u32(updates);wait(lambda:u32(updates)>=tick+n,'Frames stopped')
def pulse(value,n=3):keys(value);frames(n);keys(0);frames(3)
def visual_report(report):
    if not args.visuals:return
    vs=labels['CharLabRuntime.sCCVisualStates']
    assert not visual_errors,visual_errors[:8]
    assert not any(u32(vs+field) for field in visual_layout[1:5]),('Visual survived recovery',diagnostic())
    counters={name:u32(labels['CharLabRuntime.gCCVisual'+name]) for name in ('Models','Effects','Sounds','Stops')}
    if args.neutral in (1,9,11) or args.donor==8 or (args.donor==3 and args.special_side!='up'):assert counters['Models']>0,('No donor prop/orb',counters)
    if args.neutral==6 or args.donor==7 or (args.donor==8 and args.special_side!='down') or (args.neutral is None and args.donor is None and args.paired_donor is None and args.taunt_donor is None):assert counters['Effects']>0,('No donor attached FX',counters)
    if args.donor==8 and args.special_side!='up':assert visual_hidden,('Stone did not replace body',counters)
    if args.donor==3 and args.special_side!='up':assert visual_hidden,('Bomb did not replace body',counters)
    if args.paired_donor==3:assert counters['Effects']>0,('Missing Samus beam glow',counters,[hex(u32(labels['CharLabRuntime.sCCVisualFiles']+i*4)) for i in range(4)])
    if args.neutral==9:assert counters['Models']==2,('Charge orb restarted during internal phases',counters)
    assert visual_samples>0,('No source visual updates',counters)
    report['visual_cpu_checks']={'checks':['native prop/effect allocation','source-clock audio dispatch','finite transforms','owned recovery cleanup'],
                               'samples':visual_samples,'objects':len(visual_objects),'body_replacement':visual_hidden,**counters}
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
    if args.editor_test:
        # Recreate stale 1P selections; production launch must replace them.
        w8(scene+man_off,255);w8(scene+man_costume_off,255)
        w8(scene+cpu_off,33);w8(scene+cpu_costume_off,255)
        w8(scene+port_off,3)
        w8(labels['Toggles.normal_options'],0)
        w32(labels['CharLab.return_slot'],args.editor_slot)
        w8(scene+1,u8(scene));w8(scene,57);w32(native['sSYTaskmanStatus'],1)
        check(core.CoreDoCommand(8,0,None))
        wait(lambda:u8(scene)==57 and u8(labels['Toggles.menu_index'])==args.editor_slot+8,'Editor initialization',seconds=40)
        frames(30)
        print('EDITOR: before Test input',diagnostic(),flush=True)
        pulse(0x80)
        wait(lambda:u8(scene)==18,'Test in Training CSS transition',seconds=40)
        frames(150)
        assert not u32(native['__osFaultedThread']),('Training CSS fault',diagnostic())
        assert u32(labels['CharLab.training_slot'])==args.editor_slot
        body_entry=u32(u32(labels['CharCreator.slot_tables']+(args.editor_slot-1)*4)+4)
        body=u8(labels['CharCreatorCatalog.id_table']+u32(body_entry))
        assert u8(scene+man_off)==body and u8(scene+cpu_off)==0 and u8(scene+port_off)==0
        print('PASS: real editor A input reaches a running Training CSS.',flush=True)
        if args.editor_play:
            pulse(0x10)
            wait(lambda:u8(scene)==21,'Training stage select',seconds=40)
            frames(90);pulse(0x80)
            wait(lambda:u8(scene)==54 and fighter(),'Editor-launched Training match',seconds=60)
            frames(150)
            assert not u32(native['__osFaultedThread']) and u32(fighter()+8)==body,diagnostic()
            report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'editor_slot':args.editor_slot,'checks':['editor Test A input','CSS Start','stage A confirmation','Training match load and updates'],'rendering':'null'}
            (build/f'cpu-scenes-editor-{args.editor_slot}-play.json').write_text(json.dumps(report,indent=2)+'\n')
            print('PASS: editor Test, CSS Start and stage confirmation load a running Training match.',flush=True)
            raise SystemExit(0)
        pulse(0x40)
        frames(90);pulse(0x40) # First B recalls the preselected human puck.
        wait(lambda:u8(scene)==57 and u8(labels['Toggles.menu_index'])==args.editor_slot+8,'CSS Back to editor',seconds=40)
        frames(30)
        assert not u32(native['__osFaultedThread']),('Returned editor fault',diagnostic())
        report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'editor_slot':args.editor_slot,'checks':['editor Test A input','Training CSS continues running','CSS Back to tested editor'],'rendering':'null'}
        (build/f'cpu-scenes-editor-{args.editor_slot}.json').write_text(json.dumps(report,indent=2)+'\n')
        print('PASS: Test in Training and CSS Back for editor slot',args.editor_slot,flush=True)
        raise SystemExit(0)
    # Retain source recipe defaults except the two selected special donors.
    table=u32(labels['CharCreator.slot_tables'])
    for i in range(22):w32(u32(table+i*4),0)
    if args.normal_animations is not None:
        for i in range(2,15):w32(u32(table+i*4),args.normal_animations)
    w32(u32(table),1);w32(u32(table+4),args.body)
    w32(u32(table+16*4),args.donor if args.donor is not None else 9)
    w32(u32(table+17*4),args.donor if args.donor is not None else 7)
    if args.neutral is not None:w32(u32(table+15*4),args.neutral)
    if args.paired_donor is not None:
        w32(u32(table+18*4),args.paired_donor)
        for field in (19,20):w32(u32(table+field*4),args.throw_donor if args.throw_donor is not None else args.paired_donor)
    w32(u32(table+21*4),args.taunt_donor if args.taunt_donor is not None else args.body)
    w32(labels['CharCreator.selected_builds'],1)
    w8(scene+man_off,args.body);w8(scene+cpu_off,0 if args.edge or args.inhale_contact else 8);w8(scene+stage_off,args.stage)
    # Training copies the current scene's stage, not the remembered SSS byte.
    w8(scene+edge_stage[13],args.stage)
    w8(scene+1,u8(scene));w8(scene,54);w32(native['sSYTaskmanStatus'],1)
    check(core.CoreDoCommand(8,0,None))
    wait(lambda:u8(scene)==54 and fighter() and u32(updates)>240,'Training load',seconds=60)
    check(core.CoreDoCommand(17,4,C.byref(C.c_int(120))))
    check(core.CoreDoCommand(17,5,C.byref(C.c_int(1))))
    frames(180);wait(lambda:u32(fighter()+0x24)==10,'Mario idle')
    assert u8(u32(native['gSCManagerBattleState'])+1)==args.stage,('Wrong native stage',args.stage,u8(u32(native['gSCManagerBattleState'])+1))
    start_top=u32(fighter()+0x8E8)
    start_position=tuple(f32(start_top+layout[12]+j) for j in (0,4,8))
    collision_fixture=C.string_at(ram+((fighter()+collision_off)&0x7fffff),collision_size)
    initial_kinetics=u32(fighter()+layout[2])
    print('PASS: Remix Training loads body',args.body,'with donor',args.donor if args.donor is not None else 'Kick/Quick Attack','; no CPU fault.',flush=True)
    if args.edge:
        from charlab_scene_edges import run
        run(globals());raise SystemExit(0)
    if args.paired_donor is not None:
        # Idle human victim avoids Training AI jumping out of the short window.
        w32(fighter(1)+layout[1],0)
        if args.paired_donor == args.body:
            # Native short grabs can open/close between frame callbacks. Put
            # the dummy within standing reach before the real grab input.
            target=u32(fighter(1)+0x8E8)+layout[12]
            facing=1 if u32(fighter()+0x44)==1 else -1
            for j in (0,4,8):wf32(target+j,f32(start_top+layout[12]+j)+(200*facing if j==0 else 0))
            pair_contact=True
        tracking=True;pulse(0xA0)
        if args.paired_miss:
            frames(160);tracking=False
            wait(lambda:u32(fighter()+0x24)==10,'Missed tether recovery')
            assert not u32(native['__osFaultedThread']),diagnostic()
            assert not any(row[3] and row[4] for row in pair_samples),('Missed tether fixture captured opponent',pair_samples)
            report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'grab_donor':args.paired_donor,'checks':['real missed tether input','full extension/retraction','recovery cleanup'],'rendering':'null'}
            if args.tether_materials:
                # Native Samus reference: image 0 holds through material frame
                # 50, then 1/1/2/2/0/1/2/2/0. EF creation starts its clock
                # at zero; check progression as well as the actual images.
                rows={int(t): (age,image) for t,age,image in tether_material_samples}
                assert len(rows)>=65,('Too few material samples',rows)
                for t,(age,image) in rows.items():
                    assert abs(age-(t-1))<.01,('Beam material advanced twice or stalled',t,age)
                    frame=int(age)
                    if frame<=50:assert image==0,('Native 50-frame texture hold shortened',t,age,image)
                    elif frame<=59:
                        assert image==(1,1,2,2,0,1,2,2,0)[frame-51],('Wrong native beam texture sequence',t,age,image)
                report['tether_material_checks']={'samples':len(rows),'checks':['one material update per frame','native 50-frame image hold','native blink sequence'],'rendering':'null'}
            visual_report(report)
            (report_directory/f'cpu-scenes-tether-miss-{args.body}-{args.paired_donor}.json').write_text(json.dumps(report,indent=2)+'\n')
            print('PASS: missed tether',report,flush=True);raise SystemExit(0)
        wait(lambda:u32(fighter()+layout[17])!=0,'Donor grab contact',seconds=30)
        frames(12)
        if args.paired_airborne:
            wf32(u32(fighter()+0x8E8)+layout[12]+4,4000)
        facing=1 if u32(fighter()+0x44)==1 else -1
        if args.back_throw:pulse(((-80*facing)&255)<<16)
        else:pulse(0x80)
        donor=args.throw_donor if args.throw_donor is not None else args.paired_donor
        if donor==2 and not args.back_throw:
            frames(35);pulse(((35*facing)&255)<<16,5);frames(15)
            if args.cargo_jump:pulse(0x0800);frames(15)
            pulse(0x80)
        frames(180);tracking=False
        assert not u32(native['__osFaultedThread']),diagnostic()
        wait(lambda:u32(fighter()+0x24)==10,'Paired throw recovery',seconds=30)
        assert pair_contact and any(row[3] and row[4] for row in pair_samples),('No paired ownership',pair_samples)
        assert not u32(fighter()+layout[17]) and not u32(fighter(1)+layout[18]),('Capture survived release',diagnostic())
        assert u32(fighter(1)+percent_off)>0,('No throw damage',pair_samples[-8:])
        assert u32(fighter()+8)==args.body and not animation_errors,diagnostic()
        seen={row[0] for row in pair_samples}
        if donor==2 and not args.back_throw:
            assert 235 in seen and any(s in seen for s in (236,237,238)),('DK cargo/walk phases absent',seen)
            if args.cargo_jump:assert {240,241,245}<=seen,('DK cargo jump/air toss phases absent',seen)
            else:assert 244 in seen,('DK cargo ground toss absent',seen)
        if donor==8 and not args.back_throw:
            assert {228,230}<=seen,('Kirby lift/landing phases absent',seen)
            if args.paired_airborne:assert 229 in seen,('Kirby airborne fall phase absent',seen)
        if args.back_throw:assert 170 in seen,('Back throw input did not enter donor backward phase',seen)
        report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'grab_donor':args.paired_donor,'throw_donor':donor,'back_throw':args.back_throw,'airborne_start':args.paired_airborne,'cargo_jump':args.cargo_jump,'observed_phases':sorted(seen),'checks':['real Z+A grab/contact','native paired ownership','throw input/release/damage','native body identity and recovery'],'rendering':'null'}
        visual_report(report)
        (report_directory/f'cpu-scenes-paired-{args.body}-{args.paired_donor}-{donor}-{int(args.back_throw)}-{int(args.paired_airborne)}-{int(args.cargo_jump)}.json').write_text(json.dumps(report,indent=2)+'\n')
        print('PASS: real donor grab/paired throw release',report,flush=True);raise SystemExit(0)
    if args.taunt_donor is not None and args.neutral is None:
        durations=(180,60,60,60,80,60,80,60,60,80,90,60)
        tracking=True;pulse(0x2000)
        frames(durations[args.taunt_donor]+12)
        tracking=False
        assert not u32(native['__osFaultedThread']),diagnostic()
        assert any(row[0]==189 for row in taunt_samples),('Taunt not entered',diagnostic())
        samples=[r for r in taunt_samples if r[0]==189]
        assert max(r[1] for r in samples)>=durations[args.taunt_donor]-2,('Source taunt duration',samples[-8:])
        if args.taunt_donor==0:
            assert max(r[3][0] for r in samples)>2,('Mario growth absent',samples[:8])
            assert abs(f32(u32(fighter()+0x8E8+16)+layout[14])-1)<.0001,('Mario scale survived recovery',diagnostic())
            grown=[r for r in samples if r[3][1]>2]
            assert grown and min(r[5] for r in grown)>100, ('Mario growth sank below its standing pivot',grown[:3])
        if args.taunt_donor==4:
            active={int(r[1]) for r in samples if r[4]}
            assert {47,48,49}<=active,('Luigi damage window',active)
        assert u32(fighter()+0x24)==10 and not animation_errors,diagnostic()
        tracking=True;pulse(0x2000);pulse(0x20)
        assert u32(fighter()+0x24)==189,('Early taunt cancellation',diagnostic())
        cancel=(128,60,60,60,60,None,60,60,60,60,60,60)[args.taunt_donor]
        if cancel is not None and cancel<durations[args.taunt_donor]:
            wait(lambda:u32(fighter()+0x180)!=0,'Donor taunt cancel flag')
            keys(0x20);wait(lambda:u32(fighter()+0x24)!=189,'Donor taunt guard cancel');keys(0);frames(90)
        else:frames(durations[args.taunt_donor]+15)
        tracking=False
        assert not u32(native['__osFaultedThread']),diagnostic()
        if args.taunt_donor==0:
            assert abs(f32(u32(fighter()+0x8E8+16)+layout[14])-1)<.0001,('Mario scale survived cancellation',diagnostic())
        report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'taunt_donor':args.taunt_donor,'checks':['real L input','source taunt pose clock and natural recovery','early guard rejection and donor cancel policy','planted scaled pivot' if args.taunt_donor==0 else 'native donor scale'],'rendering':'null'}
        (report_directory/f'cpu-scenes-taunt-{args.body}-{args.taunt_donor}.json').write_text(json.dumps(report,indent=2)+'\n')
        print('PASS: donor taunt',report,flush=True);raise SystemExit(0)
    if args.neutral is not None:
        if args.inhale_contact:
            il=constant('ccInhaleLayout');state=labels['CharLabRuntime.sCCInhaleStates']
            w32(fighter(1)+layout[1],0)
            tracking=True
            releases=([(0x2000,'held L')] if args.inhale_held_l else [])+[(0x80,'spit'),(0x40,'copy')]
            for button,label in releases:
                inhale_capture=True;keys(0x40)
                wait(lambda:u32(fighter()+0x24) in (il[6],il[13]),'Inhale held victim: '+label,seconds=30)
                keys(0);inhale_capture=False;frames(12)
                assert u32(fighter()+layout[17])==u32(fighter(1)+visual_layout[8]),('Missing native catch owner',diagnostic())
                before_position=tuple(f32(u32(fighter()+0x8E8)+layout[12]+j) for j in (0,4,8))
                pulse(button)
                if label=='held L':
                    assert u32(fighter()+0x24) in (il[9],il[9]+9),('L did not enter donor spit',label,diagnostic())
                frames(100)
                wait(lambda:u32(fighter()+0x24)==10,'Inhale '+label+' recovery',seconds=30)
                assert not u32(native['__osFaultedThread']),diagnostic()
                assert not u32(fighter()+layout[17]),('Victim survived release',diagnostic())
                assert not u32(fighter(1)+layout[18]),('Victim retained capture owner',diagnostic())
                if label=='held L':
                    after_position=tuple(f32(u32(fighter()+0x8E8)+layout[12]+j) for j in (0,4,8))
                    assert max(abs(a-b) for a,b in zip(before_position,after_position))<500,('L teleported attacker',before_position,after_position)
                    assert not any(row[0]<7 for row in trace),('L killed attacker',diagnostic())
                frames(160)
            copy_choice=u32(fighter()+il[3]) if args.body==8 else u32(state+il[1])
            assert copy_choice==(0 if args.body==8 else 2),('Mario ability was not copied',copy_choice,inhale_choices,diagnostic())
            pulse(0x40);frames(110)
            assert 0 in weapon_kinds,('Copied Mario Fireball missing',weapon_kinds,diagnostic())
            wait(lambda:u32(fighter()+0x24)==10,'Copied Neutral recovery',seconds=30)
            stars_before=u32(labels['CharLabRuntime.gCCVisualEffects'])
            pulse(0x2000);frames(200) # Plugin L trigger; 0x2 is Training reset.
            wait(lambda:u32(fighter()+0x24)==10,'L-discard taunt recovery',seconds=30)
            copy_choice=u32(fighter()+il[3]) if args.body==8 else u32(state+il[1])
            assert copy_choice==(8 if args.body==8 else 12),('Taunt did not discard copy',copy_choice,diagnostic())
            assert args.body==8 or u32(labels['CharLabRuntime.gCCVisualEffects'])==stars_before+1,('Native discarded star was not created once',stars_before,u32(labels['CharLabRuntime.gCCVisualEffects']),diagnostic())
            pulse(0x0800);frames(4);keys(0x40)
            wait(lambda:u32(fighter()+0x24)==il[12],'Aerial inhale loop',seconds=30)
            frames(90);keys(0);frames(130)
            wait(lambda:u32(fighter()+0x24)==10,'Aerial inhale landing/release',seconds=30)
            assert il[11] in inhale_observed and il[12] in inhale_observed
            assert {il[7],il[8],il[9],il[10]}<=inhale_observed,('Missing inhale phases',inhale_observed,il,diagnostic())
            assert {il[14],il[15],il[16],il[17]}<=inhale_victims,('Missing native victim phases',inhale_victims,il,diagnostic())
            assert u32(fighter()+8)==args.body and u32(fighter(1)+8)==0
            iv=constant('ccInhaleVisualLayout')
            assert args.body==8 or all(inhale_visual_samples.values()),('Missing inhale wind',inhale_visual_samples,sorted(inhale_wind_diagnostics))
            assert not inhale_visual_errors,inhale_visual_errors[:8]
            assert not u32(state+iv[0]),('Inhale wind survived recovery',diagnostic())
            assert all(math.isfinite(v) and abs(v)<50000 for row in trace for v in row[2])
            tracking=False
            report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'neutral':12,
                    'checks':['real held B inhale','native capture and held ownership','A star spit and release','repeat inhale and B copy release','copied Mario Fireball input','L discards copied ability']+(['grounded L with held victim follows donor spit and preserves attacker position/life'] if args.inhale_held_l else [])+['aerial inhale and ground handoff/release','native body identity and recovery'],
                    'fighter_statuses':sorted(inhale_observed),'victim_statuses':sorted(inhale_victims),'copied_choices':sorted(inhale_choices),'rendering':'null'}
            report['inhale_visual_checks']={'samples':inhale_visual_samples,'native_presentation':args.body==8,'checks':[] if args.body==8 else ['native Kirby wind script matches source ROM','native wind particle allocation','finite particle transforms','exactly one native L-discard star','wind recovery cleanup; no mouth overlay'],'rendering':'null'}
            (report_directory/f'cpu-scenes-inhale-{args.body}.json').write_text(json.dumps(report,indent=2)+'\n')
            print('PASS: inhale, spit, copy and copied Neutral B',report,flush=True);raise SystemExit(0)
        trace.clear();tracking=True;pulse(0x40)
        if args.neutral in (8,9):
            if args.full_charge:
                state=labels['CharLabRuntime.sFTCharBuilderNeutralStates'];ci=constant('ccChargeVisualLayout')
                wait(lambda:u32(state+16)==ci[2] and u32(fighter()+0x24)==10,'Full Giant Punch storage',seconds=30)
                frames(40);assert u32(fighter()+ci[0])==ci[1],('Stored full-charge flash missing',diagnostic())
                keys(64<<16);frames(12);keys(0);frames(30)
                assert u32(fighter()+ci[0])==ci[1],('Movement lost full-charge flash',diagnostic())
                pulse(0x40);frames(100)
                assert u32(state+16)==0 and u32(fighter()+ci[0])!=ci[1],('Spent Giant Punch still flashes',diagnostic())
                assert len({row[2] for row in charge_visual_samples if row[1]==ci[1]})>1,('Blink script did not advance',charge_visual_samples[-20:])
            else:
                frames(100)
                # Store with Z, start charging again, then release with B.
                pulse(0x20);frames(35)
                wait(lambda:u32(fighter()+0x24)==10,'Charge store recovery',seconds=30)
                pulse(0x40);frames(30);pulse(0x40)
        frames(150);tracking=False
        assert trace and any(row[0]>=220 for row in trace),('Neutral was not entered',args.neutral,diagnostic())
        if args.neutral==12:
            il=constant('ccInhaleLayout')
            assert any(row[0] in (il[4],il[11]) for row in trace),('Inhale entry missing',sorted({row[0] for row in trace}),diagnostic())
        assert not u32(native['__osFaultedThread']),('Neutral CPU fault',args.neutral,diagnostic())
        wait(lambda:u32(fighter()+0x24)==10,'Neutral recovery',seconds=30)
        assert u32(fighter()+8)==args.body
        assert all(math.isfinite(v) and abs(v)<50000 for row in trace for v in row[2])
        assert not animation_errors,animation_errors[:8]
        expected_weapon={1:1,2:0,3:0,4:9,5:13,9:2,10:7}.get(args.neutral)
        if expected_weapon is not None:assert expected_weapon in weapon_kinds,('Neutral weapon missing',args.neutral,weapon_kinds)
        if args.neutral in (8,9):
            index=1 if args.neutral==8 else 2
            release_pairs=(8,10) if args.neutral==8 else (16,)
            assert any(sample[index]>0 for sample in neutral_samples),('No stored charge',neutral_samples[-8:])
            assert any((sample[0]&~1) in release_pairs and sample[3]>0 for sample in neutral_samples),('No charged release',neutral_samples[-8:])
        if args.egg_contact:
            assert egg_contact_done and set(egg_statuses)<=egg_observed,('Egg capture/handoff missing',egg_statuses,egg_observed,diagnostic())
            assert u32(fighter(1)+percent_off)>=5,('Egg damage missing',diagnostic())
        if args.projectile_contact:
            pk_item=constant('ccPairedSpecialLayout')[3]-1
            assert projectile_contact_done and pk_item in item_kinds,('PK Fire flame missing',pk_item,item_kinds,diagnostic())
            assert u32(fighter(1)+percent_off)>0,('PK Fire contact damage missing',diagnostic())
        report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'neutral':args.neutral,
                'checks':['Training resource load','real Neutral B input','native projectile/callback execution','finite joints','neutral recovery']+
                         (['charge Z store and B release'] if args.neutral in (8,9) and not args.full_charge else []),
                'animation_samples':animation_samples,'animation_clips':len(animation_records),'rendering':'null'}
        if args.egg_contact:report['checks'].append('controlled native Egg Lay capture, handoff and damage')
        if args.projectile_contact:report['checks'].append('controlled PK Fire contact and native flame-pillar item/damage')
        if args.full_charge:report['checks'].append('full Giant Punch native color script advances while stored/moving and clears on release')
        report['weapon_kinds']=sorted(weapon_kinds);report['item_kinds']=sorted(item_kinds)
        visual_report(report)
        suffix='-contact' if args.egg_contact or args.projectile_contact else ''
        (build/f'cpu-scenes-neutral-{args.body}-{args.neutral}{suffix}.json').write_text(json.dumps(report,indent=2)+'\n')
        print('PASS: Neutral B',args.neutral,'input/native callbacks/charge/recovery on body',args.body,'statuses',sorted({row[0] for row in trace}),flush=True)
        raise SystemExit(0)
    if args.normal_animations is not None:
        # Real A input: jab, up tilt/smash, then jump + forward/down aerials.
        # Native inputs select states; fixtures supply only the saved recipe.
        starting_loads=u32(labels['CharLabRuntime.gCCAnimationLoads'])
        normal_checks=[]
        if args.normal_mechanics:
            third_motions=set()
            if args.normal_animations==5:
                # Link forks jab two into jab three OR rapid jabs. Deliberate
                # taps exercise the third jab before the rapid-input sequence.
                trace.clear();tracking=True
                for _ in range(3):pulse(0x80);frames(6)
                frames(120);tracking=False
                wait(lambda:u32(fighter()+0x24)==10,'Third jab recovery',seconds=30)
                third_motions={row[1] for row in trace}
            trace.clear();tracking=True
            for _ in range(36):pulse(0x80,1)
            frames(180);tracking=False
            wait(lambda:u32(fighter()+0x24)==10,'Jab recovery',seconds=30)
            observed=third_motions|{row[1] for row in trace}
            donor=args.normal_animations
            extra=labels['CharLabRuntime.sFTCustomBodyExtraMotionIDs']+donor*16
            if donor in (0,4,5,7,11):
                assert u32(extra) in observed,('Missing donor jab3',donor,observed,diagnostic())
                normal_checks.append('real donor jab3')
            if donor in (1,5,7,8):
                assert u32(extra+8) in observed and u32(extra+12) in observed,('Missing rapid loop/end',donor,observed,diagnostic())
                normal_checks.append('real donor rapid loop/end')
            if donor==9:
                second=u32(labels['CharLabRuntime.sFTCustomMotionIDs']+4)
                assert second not in observed,('Pikachu entered jab2',observed)
                normal_checks.append('real Pikachu repeat jab')
            assert not u32(native['__osFaultedThread']),('Jab fault',diagnostic())
            print('PASS: real donor jab input, source phase transitions and recovery; motions',sorted(observed),flush=True)

        inputs=(('down smash',0x80|(176<<24)),) if args.down_smash else (('jab',0x80),('up attack',0x80|(80<<24)),('forward aerial',0x80|(80<<16)),('down aerial',0x80|(176<<24)))
        for name,button in inputs:
            print('NORMAL:',name,flush=True)
            wait(lambda:u32(fighter()+0x24)==10,'Normal idle',seconds=30)
            if 'aerial' in name:pulse(0x800);frames(15)
            trace.clear();tracking=True;pulse(button);frames(80);tracking=False
            assert trace and not u32(native['__osFaultedThread']),('Normal fault',name,diagnostic())
            if args.down_smash:assert 208 in {row[0] for row in trace},('Down-smash status absent',trace)
            wait(lambda:u32(fighter()+0x24)==10,'Normal recovery',seconds=30)
        if args.normal_mechanics and args.normal_animations==5:
            assert link_contact_done and link_bounce_samples,('Link live bounce missing',link_contact_done,link_bounce_samples,diagnostic())
            normal_checks.append('controlled live Link down-air bounce')
        assert u32(labels['CharLabRuntime.gCCAnimationLoads'])>starting_loads and len(animation_records)>=(1 if args.down_smash else 3),('Missing normal clips',animation_samples,animation_records)
        assert not animation_errors,animation_errors[:8]
        print('PASS: real A-input normals stream distinct donor clips; finite native joints and recovery on body',args.body,flush=True)
        report={'rom_sha256':hashlib.sha256(rom).hexdigest(),'body':args.body,'normal_animation_donor':args.normal_animations,
                'checks':['Training load',*normal_checks,'real down-smash input' if args.down_smash else 'real jab/up attack/forward aerial/down aerial input','normal clip DMA','finite native joints','normal recovery'],
                'animation_samples':animation_samples,'animation_clips':len(animation_records),'rendering':'null'}
        (report_directory/(f'cpu-scenes-normals-{args.body}-{args.normal_animations}'+('-dsmash.json' if args.down_smash else '.json'))).write_text(json.dumps(report,indent=2)+'\n')
        raise SystemExit(0)
    moves=(('Falcon Kick',0x40|(176<<24)),('Quick Attack',0x40|(80<<24)))
    if args.donor is not None:
        moves=tuple((name,button) for name,button,side in (('Donor Up B',0x40|(80<<24),'up'),('Donor Down B',0x40|(176<<24),'down')) if args.special_side in ('both',side))
    if args.bomb_count:
        moves=tuple((name,0x40|(176<<24)) for name in ('Ground bomb 1','Ground bomb 2','Air bomb 1','Air bomb 2'))
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
        if args.bomb_count and name.startswith('Air'):
            pulse(0x800);frames(18)
            assert u32(fighter()+layout[2])!=initial_kinetics,('Bomb fixture did not jump',diagnostic())
        initial_scale=tuple(f32(model+layout[14]+j) for j in (0,4,8))
        cast_position=tuple(f32(top+layout[12]+j) for j in (0,4,8))
        birth_start=len(bomb_births);ball_start=len(ball_samples)
        trace.clear();tracking=True;pulse(button)
        if name=='Quick Attack':
            wait(lambda:u32(fighter()+0x24) in (special[5],special[7]),'First Quick Attack endpoint')
            # Aim the second zip back down toward the launch platform. A
            # horizontal full-strength zip legitimately exits this stage's
            # floor and cannot serve as a no-KO recovery regression.
            keys(176<<24);frames(12);keys(0)
        try:
            wait(lambda:u32(fighter()+0x24)==10 and any(row[0]>=220 for row in trace),'Special recovery/landing',seconds=30)
        except AssertionError:
            (build/('failed-'+name.replace(' ','-')+'.json')).write_text(json.dumps(trace))
            raise
        frames(3);tracking=False
        if args.bomb_count:
            births=bomb_births[birth_start:]
            bomb_casts.append({'cast':name,'births':births,'statuses':sorted({row[0] for row in trace})})
            (build/'bomb-count-trace.json').write_text(json.dumps(bomb_casts,indent=2)+'\n')
            print('BOMBS:',name,births,flush=True)
            assert len(births)==1,('Expected one Samus Bomb per Down B input',name,births)
            entered=next(row[0] for row in trace if row[0] in (229,230))
            assert entered==(230 if name.startswith('Air') else 229),('Wrong bomb entry phase',name,entered)
            if args.body!=3:assert births[0]['source_frame']==10,('Bomb source timing changed',name,births)
            if args.visuals and args.body!=3:
                samples=ball_samples[ball_start:]
                assert samples and {3,10,43,48} <= {int(row[0]) for row in samples},('Incomplete Morph Ball source phases',name,samples)
                assert all(row[2] and row[3]==0 and row[4] for row in samples),('Undrawable Morph Ball mesh/material',name,samples)
                bomb_casts[-1]['morph_ball']={'samples':len(samples),'phases':[3,10,43,48],
                    'mesh_and_private_palette':'present','hidden_prop_flags':False}
                if name.startswith('Ground'):
                    rise=max(row[1] for row in samples)-samples[0][1]
                    assert rise>300,('Morph Ball did not follow native hop',name,rise)
                    bomb_casts[-1]['morph_ball']['rise']=rise
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
    assert not animation_errors,animation_errors[:8]
    report['animation_samples']=animation_samples;report['animation_clips']=len(animation_records)
    visual_report(report)
    if args.normal_animations is not None:report['normal_animation_donor']=args.normal_animations
    if args.bomb_count:
        report['bomb_casts']=bomb_casts
        report['checks'].append('one actual bomb per grounded/aerial input, including new casts and ground/air handoff')
        if args.visuals and args.body!=3:report['checks'].append('all Morph Ball phases have drawable meshes/private palettes and follow the original grounded hop')
    if args.falcon_contact:report['controlled_dive_contact']='native capture, release and throw damage passed'
    report_name='cpu-scenes.json' if args.donor is None else f'cpu-scenes-{args.body}-{args.donor}-{args.special_side}.json'
    if args.falcon_contact:report_name=report_name.replace('.json','-contact.json')
    if args.normal_animations is not None:report_name=report_name.replace('.json','-normals-'+str(args.normal_animations)+'.json')
    if args.bomb_count:report_name=report_name.replace('.json','-bomb-count.json')
    (report_directory/report_name).write_text(json.dumps(report,indent=2)+'\n')
except BaseException as exc:
    if not isinstance(exc,SystemExit):print('SCENE FAILURE:',repr(exc),flush=True)
    raise
finally:
    keys(0);core.CoreDoCommand(6,0,None);thread.join(timeout=3)
