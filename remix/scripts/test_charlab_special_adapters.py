"""Production MIPS regressions for foreign special ownership and recovery.

Runs through the installed bridges where possible. Weapon creation and status
setup are explicit fixtures; donor math, clocks, callbacks and fields execute.
Contact/render acceptance is separate from these CPU checks.
"""
import json
import math
import struct
import re
from pathlib import Path
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_S1, UC_MIPS_REG_T2, UC_MIPS_REG_T3, UC_MIPS_REG_T6, UC_MIPS_REG_V1


def test_adapters(r):
    root = Path(__file__).resolve().parents[1]
    names = ('state_size','angle','tornado','ness','weapons','fighter','attack_id','sphere',
             'passive','passive_size','accelerate','fox_angle','stone_health','gravity','terminal',
             'air_speed','air_accel','helpless','landing','hi_id','lw_id','mario_hi','mario_air_hi',
             'mario_status','mario_air_status','fox_status','fox_air_status','fox_hi','fox_air_hi',
             'yoshi_hi','pika_lw','ness_hold','reflect_loop','magnet_hold',
             'ness_delay','stone_duration','stone_hold','yoshi_status','weapon_vars','weapon_generation','weapon_object')
    layout = dict(zip(names, struct.unpack('>41I', r.read(r.addr('ccAdapterLayout'), 164))))
    air_velocity = r.u32(r.addr('ccSpecialLayout')+4)
    manifest = json.loads((root/'build/char_creator/runtime/special-hooks.json').read_text())
    hooks = {entry['name']: entry for entry in manifest}
    donor_data, pointer, attr = 0x80230000, 0x80231000, 0x80232000
    output = 0x80234000
    def context(body, donor, motion, status=0xDC, attack=None, player=0):
        r.setup(body,donor,player);r.preset(body,donor)
        for axis in range(3):r.f32(r.JOINTS+r.layout['translate']+axis*4,0)
        # ccSyncCurrent uses this port's selected saved build.
        r.u32(r.labels['CharCreator.selected_builds']+player*4,1)
        r.u32(r.labels['CharCreator.body_character_data']+player*4,0x80228000)
        r.u32(r.labels['CharCreator.body_character_id']+player*4,body)
        r.u32(r.labels['CharCreator.active_special_donor']+player*4,donor)
        r.u32(r.FP+8,donor);r.u32(r.FP+0x24,status);r.u32(r.FP+0x28,motion)
        r.u32(r.FP+layout['fighter'],r.GOBJ)
        r.u32(r.FP+layout['attack_id'],attack if attack is not None else layout['hi_id'])
        r.u32(0x80116E10+donor*4,donor_data)
        r.u32(donor_data+0x28,pointer);r.u32(pointer,attr-0x100);r.u32(donor_data+0x60,0x100)
        r.write(attr,bytes(0x400));r.f32(attr+r.layout['attr_size'],1.0)
        r.f32(attr+layout['gravity'],1.25);r.f32(attr+layout['terminal'],40)
        r.f32(attr+layout['air_speed'],50);r.f32(attr+layout['air_accel'],0)
        r.call('ccPrepare',r.GOBJ,0)
        return r.addr('sCCSpecialClocks')+player*36
    def hook(name,*args):
        r.labels['Test.adapter_hook']=r.labels[hooks[name]['hook']]
        return r.call('adapter_hook',*args,namespace='Test')
    def near(a,b):
        assert all(abs(x-y)<.005 for x,y in zip(a,b)),(a,b)
    angles = recovery = sockets = 0
    for body in range(12):
        for donor in (0,4):
            if body==donor:continue
            clock=context(body,donor,layout['mario_air_hi'],layout['mario_air_status'])
            r.f32(r.JOINTS+0x100+r.layout['rotate']+8,1.1)
            r.f32(r.JOINTS+r.layout['rotate']+8,.4)
            r.write(r.FP+r.layout['stick'],bytes([80,0]))
            before=r.read(r.JOINTS,0x200)
            hook('ftMarioSpecialHiProcInterrupt',r.GOBJ)
            state=r.addr('sCCSpecialStates')
            angle=r.f32(state+layout['angle'])
            assert -.4<angle<-.05,('Mario steering missing',body,donor,angle)
            assert r.read(r.JOINTS,0x200)==before,('Steering changed body joints',body,donor)
            path=r.u32(clock+28);travel=r.u32(path+44)
            r.f32(clock+20,5)
            dx,dy,dz,base=struct.unpack('>4f',r.read(travel+5*16,16))
            r.call('ccAirTravel',r.FP,output,output+4,output+8)
            near(struct.unpack('>3f',r.read(output,12)),(dx*math.cos(base+angle)-dy*math.sin(base+angle),dx*math.sin(base+angle)+dy*math.cos(base+angle),dz))
            angles+=1
        for donor,duration in ((0,25),(4,25),(5,13),(3,20),(1,24),(9,20),(7,17),(11,42)):
            if body==donor:continue
            # Get any source Hi phase for this donor.
            timings=r.addr('sCCSpecialTimings')+donor*276*4
            motion=next(i for i in range(195,276) if r.u32(timings+i*4))
            context(body,donor,motion)
            r.call('ccStatusChanging',r.GOBJ,layout['helpless'])
            r.u32(r.FP+0x24,layout['helpless']);r.u32(r.FP+0x28,26)
            r.u32(r.labels['CharCreator.active_special_donor'],-1)
            assert r.call('ftMainCharBuilderGetSuperJumpAttributes',r.FP)==attr
            r.u32(r.FP+layout['accelerate'],1)
            r.f32(r.FP+air_velocity+4,0)
            # The native physics hook must retain donor gravity after body restoration.
            hook('ftCommonFallSpecialProcPhysics',r.GOBJ)
            assert abs(r.f32(r.FP+air_velocity+4)+1.25)<.005,('Recovery gravity',body,donor,r.f32(r.FP+air_velocity+4))
            r.call('ccStatusChanging',r.GOBJ,layout['landing'])
            r.u32(r.FP+0x24,layout['landing']);r.u32(r.FP+0x28,96)
            r.call('ccPrepare',r.GOBJ,0)
            for frame in range(duration):
                value=r.advance()
                assert value>=0,('Early donor landing end',body,donor,frame)
            assert r.advance()==-1,('Donor landing never ends',body,donor,duration)
            r.call('ccStatusChanging',r.GOBJ,10);r.u32(r.FP+0x24,10)
            assert r.call('ftMainCharBuilderGetSuperJumpAttributes',r.FP)==r.ATTR
            r.u32(r.FP+r.player_num,7)
            r.u32(r.FP+0x24,layout['helpless'])
            assert r.call('ftMainCharBuilderGetSuperJumpAttributes',r.FP)==r.ATTR
            recovery+=1
        # Source sockets use donor coordinates, even with poisoned body joints.
        for donor,motion,attack in ((6,layout['yoshi_hi'],layout['hi_id']),
                                   (9,layout['pika_lw'],layout['lw_id']),
                                   (11,layout['ness_hold'],layout['hi_id'])):
            if body==donor:continue
            clock=context(body,donor,motion,attack=attack)
            path=r.u32(clock+28);spawn=r.u32(path+48)
            assert spawn,(donor,motion)
            r.f32(clock+20,4)
            for facing in (-1,1):
                r.u32(r.FP+0x44,facing)
                for axis,value in enumerate((200,300,40)):r.f32(r.JOINTS+r.layout['translate']+axis*4,value)
                assert r.call('ftMainCharBuilderGetSpecialSpawn',r.GOBJ,output)
                x,y,z=struct.unpack('>3f',r.read(spawn+4*12,12))
                near(struct.unpack('>3f',r.read(output,12)),(200+x*facing,300+y,40+z*facing))
                sockets+=1
            r.u32(r.FP+r.player_num,5)
            assert not r.call('ftMainCharBuilderGetSpecialSpawn',r.GOBJ,output)
    volumes = turns = 0
    for body in range(12):
        for donor,motion in ((1,layout['reflect_loop']),(11,layout['magnet_hold'])):
            if body==donor:continue
            clock=context(body,donor,motion,attack=layout['lw_id'])
            volume=0x80238000
            r.u32(r.FP+layout['sphere'],volume)
            r.write(volume,bytes(36))
            for i,v in enumerate((10,20,30)):r.f32(volume+20+i*4,v)
            assert r.call('ftMainCharBuilderGetSpecialSphere',r.FP,output,output+64)
            near(struct.unpack('>3f',r.read(output+64,12)),(10,20,30))
            path=r.u32(clock+28);spawn=r.u32(path+48)
            point=struct.unpack('>3f',r.read(spawn,12))
            near(tuple(r.f32(output+48+i*4) for i in range(3)),tuple(-v for v in point))
            volumes+=1
        if body!=1:
            clock=context(body,1,layout['fox_air_hi'],layout['fox_air_status'])
            path=r.u32(clock+28);frames=r.u32(path+24);count=r.u32(path+32)
            tick=next(i for i in range(count) if r.u32(frames+i*52+48))
            mask=r.u32(frames+tick*52+48);hit=next(i for i in range(4) if mask&(1<<i))
            center=struct.unpack('>3f',r.read(frames+tick*52+hit*12,12))
            pivot=struct.unpack('>3f',r.read(r.u32(path+48)+tick*12,12))
            r.f32(clock+20,tick);base=r.FP+0x294+hit*0xC4;r.u32(base,1)
            for angle in (-math.pi/2,-math.pi/4,0,math.pi/4,math.pi/2):
                r.f32(r.FP+layout['fox_angle'],angle);r.call('ccCollision',r.FP)
                x=center[2]-pivot[0];y=center[1]-pivot[1]
                expected=(center[0]/2,(pivot[1]+x*math.sin(angle)+y*math.cos(angle))/2,
                          (pivot[0]+x*math.cos(angle)-y*math.sin(angle))/2)
                near(struct.unpack('>3f',r.read(base+0x18,12)),expected);turns+=1
    # A real held-egg callback creates external ownership. Poisoning the native
    # status union before damage must still destroy exactly the owned egg.
    native={name:int(address,16) for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);',
            (root.parent/'ssb-decomp-re/symbols/symbols_us.txt').read_text(),re.M)}
    egg,wp=0x80240000,0x80241000
    r.write(egg,bytes(0x100));r.write(wp,bytes(0x800));r.u32(egg+0x84,wp)
    r.u32(wp+layout['weapon_object'],egg)
    spawned=[];destroyed=[]
    def make_egg():
        spawned.append(struct.unpack('>3f',r.read(r.reg(UC_MIPS_REG_A1),12)))
        return egg
    r.services[native['wpYoshiEggThrowMakeWeapon']]=make_egg
    r.services[native['wpMainDestroyWeapon']]=lambda:destroyed.append(r.reg(UC_MIPS_REG_A0))
    context(0,6,layout['yoshi_hi'],layout['yoshi_status'])
    r.u32(r.FP+r.layout['flags']+8,1)
    hook('ftYoshiSpecialHiUpdateEggVars',r.GOBJ)
    owner=r.call('ftMainCharBuilderGetSpecialWeapon',r.FP,6)
    assert r.u32(owner)==egg and len(spawned)==1
    variables=r.u32(r.addr('ccSpecialLayout'))
    r.write(r.FP+variables,b'\xA5'*64)
    r.call('ccStatusChanging',r.GOBJ,10)
    assert destroyed==[egg] and r.u32(owner)==0,('Held egg cleanup',destroyed,r.u32(owner))
    del r.services[native['wpYoshiEggThrowMakeWeapon']]
    del r.services[native['wpMainDestroyWeapon']]
    paired_names=('item','item_kind','item_owner','bomb_kind','bomb_ground','bomb_air',
                  'bomb_ground_motion','bomb_air_motion','dive_motion','dive_status','item_velocity','item_scale','capture_flags')
    paired=dict(zip(paired_names,struct.unpack('>13I',r.read(r.addr('ccPairedSpecialLayout'),52))))
    bombs=dives=releases=0
    for name in ('lbCommonEjectTreeDObj','mpCommonRunItemCollisionDefault','ftParamSetHammerParams','itMainRefreshAttackColl'):
        r.services[native[name]]=lambda:0
    item_model=0x80242000
    r.u32(egg+r.layout['obj'],item_model)
    r.write(item_model,bytes(r.layout['dobj_size']))
    for body in range(12):
        if body==5:continue
        for status,motion in ((paired['bomb_ground'],paired['bomb_ground_motion']),(paired['bomb_air'],paired['bomb_air_motion'])):
            context(body,5,motion,attack=layout['lw_id'])
            r.u32(wp+paired['item_kind'],paired['bomb_kind']);r.u32(wp+paired['item_owner'],r.GOBJ)
            r.u32(r.FP+paired['item'],egg)
            r.call('ccStatusChanging',r.GOBJ,status)
            assert r.call('ccKeepSpecialContext',r.FP,status)
            r.u32(r.FP+0x24,status)
            r.call('on_action_changed_',r.FP,status,namespace='CharCreator')
            assert r.u32(r.labels['CharCreator.active_special_donor'])==5
            assert r.u32(r.labels['CharCreator.body_character_data'])==0x80228000
            # Both parameter and command selection must retain this common
            # throw's donor stream while using body animation and flags.
            body_data,body_params,params=0x80228000,0x80229000,0x8022B000
            r.u32(body_data+0x64,body_params);r.u32(r.FP+0x9C4,donor_data)
            r.u32(donor_data+0x64,params)
            idle=r.u32(0x80128DD8+10*20)>>22
            r.write(body_params+idle*12,struct.pack('>3I',0x123,0,0x456))
            r.write(params+motion*12,struct.pack('>3I',0x789,0x8022D000,0xABC))
            r.u32(r.labels['CharCreator.active_normal_donor'],-1)
            r.uc.reg_write(UC_MIPS_REG_S1,r.FP)
            r.call('parameter_base_hook_',namespace='CharCreator',end=0x800E7504)
            assert r.reg(UC_MIPS_REG_V1)==donor_data
            r.uc.reg_write(UC_MIPS_REG_T2,motion*12)
            r.call('parameter_record_hook_',params,namespace='CharCreator',end=0x800E7560)
            record=r.reg(UC_MIPS_REG_T3)
            assert struct.unpack('>3I',r.read(record,12))==(0x123,0x8022D000,0x456)
            r.uc.reg_write(UC_MIPS_REG_T2,record)
            r.services[r.labels['CharCreator.get_moveset_base_']]=lambda:0x8022E000
            r.call('command_address_hook_',namespace='CharCreator',end=0x800E796C)
            assert r.u32(r.labels['CharCreator.active_special_donor'])==5
            del r.services[r.labels['CharCreator.get_moveset_base_']]
            r.call('ccPrepare',r.GOBJ,0)
            clock=r.addr('sCCSpecialClocks');path=r.u32(clock+28)
            assert r.u32(clock)==r.FP and path
            duration=r.u32(clock+16)&0x7FFFFFFF
            for tick in range(duration):assert r.advance()>=0
            assert r.advance()==-1
            r.f32(clock+20,4)
            assert r.call('ftMainCharBuilderGetSpecialSpawn',r.GOBJ,output)
            expected=struct.unpack('>3f',r.read(output,12))
            r.write(output+16,struct.pack('>3f',12,24,0));r.f32(wp+paired['item_scale'],1)
            hook('itMainSetFighterRelease',egg,output+16,0x3F800000,0)
            near(struct.unpack('>3f',r.read(item_model+r.layout['translate'],12)),(expected[0],expected[1],0))
            near(struct.unpack('>3f',r.read(wp+paired['item_velocity'],12)),(12,24,0))
            assert not r.u32(r.FP+paired['item'])
            assert r.call('ccKeepSpecialContext',r.FP,status),('Context lost on release',body,status)
            r.call('ccStatusChanging',r.GOBJ,10)
            assert not r.call('ccKeepSpecialContext',r.FP,status)
            bombs+=1
    for name in ('lbCommonEjectTreeDObj','mpCommonRunItemCollisionDefault','ftParamSetHammerParams','itMainRefreshAttackColl'):
        del r.services[native[name]]
    victim,victim_fp=0x80243000,0x80244000
    r.write(victim,bytes(0x100));r.write(victim_fp,bytes(r.layout['size']));r.u32(victim+0x84,victim_fp)
    original_dive=r.labels['CharLabSpecials.hook_ftCommonCaptureCaptainUpdatePositions._original']
    def native_dive():
        assert r.reg(UC_MIPS_REG_A0)==r.GOBJ and r.reg(UC_MIPS_REG_A1)==victim
        r.write(r.reg(UC_MIPS_REG_A2),struct.pack('>3f',80,160,240))
    def native_socket():
        r.write(r.reg(UC_MIPS_REG_A1),struct.pack('>3f',100,200,300))
    r.services[original_dive]=native_dive
    r.services[native['gmCollisionGetFighterPartsWorldPosition']]=native_socket
    r.labels['Test.dive_update']=native['ftCaptainSpecialHiCatchProcUpdate']
    r.services[native['efManagerQuakeMakeEffect']]=lambda:0
    for body in range(12):
        if body==7:continue
        clock=context(body,7,paired['dive_motion'],paired['dive_status'])
        for victim_kind in (0,8,11,30):
            r.u32(victim_fp+8,victim_kind)
            r.f32(clock+20,4);r.call('ftMainCharBuilderGetSpecialSpawn',r.GOBJ,output+16)
            point=struct.unpack('>3f',r.read(output+16,12))
            hook('ftCommonCaptureCaptainUpdatePositions',r.GOBJ,victim,output)
            near(struct.unpack('>3f',r.read(output,12)),tuple(v-20*(i+1) for i,v in enumerate(point)))
            dives+=1
        r.f32(clock+20,-1);r.u32(r.FP+r.layout['catch'],victim)
        released=[]
        r.services[native['ftCaptainSpecialHiThrowSetStatus']]=lambda:released.append(r.f32(clock+20))
        # Native Dive ends at the original 16-frame animation endpoint,
        # before its later frame-20 command flag can be reached.
        for tick in range(17):
            r.advance();r.events();r.call('dive_update',r.GOBJ,namespace='Test')
            assert len(released)==(1 if tick==16 else 0),('Dive donor release window',body,tick,released)
        assert released==[16] and struct.unpack('>H',r.read(victim_fp+paired['capture_flags'],2))[0]&2
        r.u32(victim_fp+paired['capture_flags'],0);releases+=1
    for address in (original_dive,native['gmCollisionGetFighterPartsWorldPosition'],native['efManagerQuakeMakeEffect'],native['ftCaptainSpecialHiThrowSetStatus']):del r.services[address]
    # Stone uses donor armor and timeout without a donor-only model overlay.
    context(0,8,layout['stone_hold'],attack=layout['lw_id'])
    hook('ftKirbySpecialLwSetDamageResist',r.GOBJ)
    assert r.u32(r.FP+layout['stone_health'])==38
    assert struct.unpack('>h',r.read(r.FP+layout['stone_duration'],2))[0]==160
    r.write(r.FP+layout['stone_duration'],struct.pack('>h',1))
    assert not hook('ftKirbySpecialLwCheckRelease',r.GOBJ,1)
    assert hook('ftKirbySpecialLwCheckRelease',r.GOBJ,1)
    # Independent passives survive the union reuse that precedes damage/capture.
    for player in range(4):
        context(6,11,layout['ness_hold'],player=player)
        r.write(r.FP+layout['passive'],b'\x5A'*layout['passive_size'])
        passive=r.read(r.FP+layout['passive'],layout['passive_size'])
        ness=r.call('ftMainCharBuilderGetNessPassive',r.FP)
        tornado=r.call('ftMainCharBuilderGetTornadoExpend',r.FP)
        thunder=r.call('ftMainCharBuilderGetPikachuThunderDestroy',r.FP)
        assert ness!=r.FP+layout['passive'] and tornado!=thunder
        r.u32(tornado,1);r.u32(thunder,1);r.u32(ness,1)
        assert r.read(r.FP+layout['passive'],layout['passive_size'])==passive
        r.u32(r.FP+r.player_num,9)
        assert r.u32(r.call('ftMainCharBuilderGetTornadoExpend',r.FP))==0
        assert r.u32(r.call('ftMainCharBuilderGetPikachuThunderDestroy',r.FP))==0
    # Native fallback must preserve PC-relative branches and their delay slots.
    r.setup(11,11)
    r.u32(r.FP+layout['ness_delay'],3)
    hook('ftNessSpecialHiDecThunderTimers',r.FP)
    assert r.u32(r.FP+layout['ness_delay'])==2
    r.u32(r.FP+layout['ness_delay'],0)
    hook('ftNessSpecialHiDecThunderTimers',r.FP)
    assert r.u32(r.FP+layout['ness_delay'])==0
    # Native Samus morph commands must not hide/reset a foreign body's parts
    # or rewrite hurtbox IDs. Multiword skips must leave the next event intact.
    commands=struct.unpack('>9I',r.read(r.addr('ccVisualCommandLayout'),36))
    parser=r.labels['CharLab.original_parse_'];delegated=[]
    r.services[parser]=lambda:delegated.append(1)
    script,words=0x80250000,0x80251000
    for body in range(12):
        if body==3:continue
        context(body,3,204,attack=layout['lw_id'])
        before=r.read(r.FP,r.layout['size'])
        joints_before=r.read(r.JOINTS,37*0x100)
        for i,opcode in enumerate(commands):
            count=4 if i>=6 else 1
            r.write(words,struct.pack('>5I',opcode<<26,0xFFFFFFFF,0xFFFFFFFF,0xFFFFFFFF,0x12345678))
            r.u32(script+4,words)
            r.call('ccParse',r.GOBJ,r.FP,script,opcode)
            assert r.u32(script+4)==words+count*4,(body,opcode,count)
        assert not delegated and r.read(r.FP,r.layout['size'])==before
        assert r.read(r.JOINTS,37*0x100)==joints_before
    del r.services[parser]
    # Both Samus Bomb phases have a source gameplay stream. A native motion
    # flag must not re-arm bomb creation or change the donor movement gates;
    # the same command from the external source stream must still execute.
    flag_checks=0
    for body in range(12):
        if body==3:continue
        for motion,status in ((204,229),(205,230)):
            clock=context(body,3,motion,status,attack=layout['lw_id'])
            assert r.u32(clock+28),('Samus Bomb source path missing',body,motion)
            flags=r.FP+r.layout['flags']
            r.write(flags,struct.pack('>4I',0,0,0,0))
            for flag in range(4):
                opcode=21+flag
                r.write(words,struct.pack('>I',opcode<<26|1))
                r.u32(script+4,words)
                r.call('ccParse',r.GOBJ,r.FP,script,opcode)
                assert r.u32(script+4)==words+4
                assert r.read(flags,16)==bytes(16),('Native events re-armed special flags',body,motion,flag)
                external=r.addr('sCCMotionScripts')
                r.u32(external+4,words)
                r.call('ccParse',r.GOBJ,r.FP,external,opcode)
                assert r.u32(flags+flag*4)==1,('Source special flag suppressed',body,motion,flag)
                assert r.u32(external+4)==words+4
                r.u32(flags+flag*4,0)
                flag_checks+=1
    # Run real source event parsing and the imported bomb callback. Only the
    # native weapon allocator is isolated. Resuming either phase after the
    # frame-10 spawn must seek past it without spawning another weapon.
    bomb_spawns=[]
    r.services[native['wpSamusBombMakeWeapon']]=lambda:bomb_spawns.append(1) or 0
    for body in range(12):
        if body==3:continue
        for start_air in (False,True):
            for repeat in range(2):
                motion,status=(205,230) if start_air else (204,229)
                clock=context(body,3,motion,status,attack=layout['lw_id'])
                before=len(bomb_spawns)
                for tick in range(57):
                    if tick in (11,44,45):
                        motion,status=(204,229) if motion==205 else (205,230)
                        r.u32(r.FP+0x24,status);r.u32(r.FP+0x28,motion)
                        r.f32(r.GOBJ+r.layout['frame'],tick)
                        r.call('ccPrepare',r.GOBJ,struct.unpack('>I',struct.pack('>f',tick))[0])
                        r.call('ccEventsForward',r.GOBJ)
                    r.advance();r.events()
                    r.call('cc_ftSamusSpecialLwMakeBomb',r.GOBJ)
                    assert len(bomb_spawns)-before==(1 if tick>=10 else 0),('Bomb timing/replay',body,start_air,repeat,tick,len(bomb_spawns)-before)
    del r.services[native['wpSamusBombMakeWeapon']]
    air_gates=0
    for port in range(4):
        table=r.u32(r.labels['CharCreator.slot_tables']+port*4)
        for body in range(12):
            for donor in range(12):
                r.setup(body,donor,port)
                r.u32(r.labels['CharCreator.selected_builds']+port*4,port+1)
                r.u32(r.u32(table),1);r.u32(r.u32(table+4),body)
                r.u32(r.u32(table+17*4),donor)
                assert r.call('ccCanAirDownB',r.FP)==(donor!=2),('Aerial Down B body gate',port,body,donor)
                if body==2 and donor in (2,3):
                    r.uc.reg_write(UC_MIPS_REG_V1,r.ATTR)
                    r.call('air_down_b_available_',r.GOBJ,r.FP,r.GOBJ,end=0x80150FAC,namespace='CharLab')
                    assert r.reg(UC_MIPS_REG_T6)==(0 if donor==2 else 0xFFFFFFFF)
                    assert r.reg(UC_MIPS_REG_A1)==r.FP and r.reg(UC_MIPS_REG_A2)==r.GOBJ and r.reg(UC_MIPS_REG_V1)==r.ATTR
                air_gates+=1
        r.setup(2,3,port)
        r.u32(r.labels['CharCreator.selected_builds']+port*4,0)
        for enabled in (False,True):
            r.u32(r.ATTR+0x100,0x1000 if enabled else 0)
            assert r.call('ccCanAirDownB',r.FP)==enabled,('Native aerial gate fallback',port,enabled)
    # Missing body slots stay null through status/animation initialization;
    # callback fallbacks resume afterward without resetting the world root.
    context(8,0,layout['mario_air_hi'],layout['mario_air_status'])
    missing=r.FP+0x8E8+35*4
    r.u32(missing,0)
    r.call('install_joint_fallbacks_',r.FP,namespace='CharCreator')
    assert r.u32(missing)==r.JOINTS
    r.f32(r.JOINTS+r.layout['translate']+4,1400)
    r.call('suspend_joints_',r.FP,namespace='CharLab')
    assert r.u32(missing)==0 and r.f32(r.JOINTS+r.layout['translate']+4)==1400
    r.call('resume_joints_',r.FP,namespace='CharLab')
    assert r.u32(missing)==r.JOINTS and r.f32(r.JOINTS+r.layout['translate']+4)==1400
    r.call('suspend_joints_',r.FP,namespace='CharLab')
    assert r.u32(missing)==0
    for port in (4,5):
        r.write(r.FP+0xD,bytes([port]))
        before=r.read(r.FP+0x8E8,37*4)
        r.call('suspend_joints_',r.FP,namespace='CharLab')
        r.call('resume_joints_',r.FP,namespace='CharLab')
        assert r.read(r.FP+0x8E8,37*4)==before
    r.write(r.FP+0xD,b'\0')
    r.call('ccReset')
    print(f'PASS: {len(manifest)} installed special adapters; {angles} Mario/Luigi steering/travel cases, {recovery} donor helpless/landing/interrupt/generation cases, {sockets} source socket/facing cases, {volumes} reflector/magnet volumes, {turns} Fire Fox directional placements, {bombs} Link common throws, {dives} Dive socket adjustments and {releases} original frame-16 releases; {flag_checks} native/source Samus Bomb flag ownership cases and {len(bomb_spawns)} single-bomb casts with frame-10 timing and three ground/air continuations each; {air_gates} donor aerial availability cases across all bodies/four ports plus native fallback; held egg interruption, Stone armor/timeout, four-port passive isolation and native branch fallbacks. Item/effect/contact setup is isolated; rendering remains pending.')
