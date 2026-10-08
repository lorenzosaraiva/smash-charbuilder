"""Execute linked donor normal callbacks; native status/contact setup is isolated.

Real-input scene checks separately cover the complete status/animation engine.
"""
import json
import struct
from pathlib import Path
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_S1, UC_MIPS_REG_T2, UC_MIPS_REG_T3, UC_MIPS_REG_V1


def test_normals(r):
    root = Path(__file__).resolve().parents[1]
    names = ('attr_size','attr_follow','traction','gravity','terminal','fast_terminal','air_max','air_accel','air_friction',
             'follow','input_count','last_jab','goto','rehit','release','a_mask','fighter','sphere','hit','map','last_z',
             'jab1','jab2','nair','dair','fsmash','landing_null','landing_start','landing_end',
             'rehit_begin','rehit_end','rehit_ticks','flag0','flag1','flag2','flag3')
    fields = dict(zip(names,struct.unpack('>36I',r.read(r.addr('ccNormalLayout'),144))))
    hooks = json.loads((root/'build/char_creator/runtime/normal-hooks.json').read_text())
    # Status setup, sound and stats are explicit service fixtures. Production
    # donor callbacks, source flags, collision scripts and physics execute.
    saved_services = dict(r.services)
    status_calls=[]; refreshed=[]
    def status():
        value=r.reg(UC_MIPS_REG_A1);status_calls.append(value)
        fp=r.reg(UC_MIPS_REG_A0);fp=r.u32(fp+0x84)
        donor=r.call_donor
        if value>=0xDC:
            table=r.u32(r.labels['Character.ACTION_ARRAY_TABLE']+donor*4)
            motion=r.u32(table+(value-0xDC)*20)>>22
        else:motion=r.u32(0x80128DD8+value*20)>>22
        r.u32(fp+0x24,value);r.u32(fp+0x28,motion)
        return 0
    r.services[0x800E6F24]=status
    for address in (0x800E82B8,):
        r.services[address]=lambda:0
    # Resolve engine service addresses from owned US symbol comments.
    import re
    lab=root.parent/'ssb-decomp-re'
    symbols={name:int(address,16) for name,address in re.findall(r'^(\w+)\s*=\s*(0x[0-9A-Fa-f]+);',(lab/'symbols/symbols_us.txt').read_text(),re.M)}
    for file in ('ft/ftanim.c','ft/ftparam.c','ft/ftcommon/ftcommonget.c','mp/mpcommon.c'):
        source=(lab/'src'/file).read_text(encoding='utf-8')
        symbols.update({name:int(address,16) for address,name in re.findall(r'// (0x[0-9A-Fa-f]{8})[^\n]*\n(?:[\w*]+\s+)+(\w+)\(',source)})
    for name in ('ftCommonGetCheckInterruptCommon','ftParamSetMotionID','ftParamSetStatUpdate','ftParamUpdate1PGameAttackStats','ftAnimEndSetWait','ftAnimEndSetFall'):
        r.services[symbols[name]]=lambda:0
    r.services[symbols['ftParamClearAttackCollAll']]=lambda:0
    r.services[symbols['ftParamRefreshAttackCollID']]=lambda:refreshed.append(r.reg(UC_MIPS_REG_A1)) or 0
    def context(body,donor,player=0,index=0):
        r.call('ccReset');r.setup(body,donor,player);r.preset(body,donor)
        r.call_donor=donor
        r.u32(r.FP+fields['fighter'],r.GOBJ)
        r.write(r.FP+fields['a_mask'],b'\x80\x00')
        r.u32(r.FP+0x24,fields['jab1']);r.u32(r.FP+0x28,r.motion(donor,index))
        r.call('ccStart',r.FP,0)
        r.u32(r.FP+fields['last_jab'],fields['jab1'])
        r.f32(r.FP+fields['follow'],30)
        r.write(r.FP+r.layout['tap'],b'\x80\x00')
        r.u32(r.FP+r.layout['flags']+4,1)
        status_calls.clear();refreshed.clear()
    chains=rapid=physics=bounces=spheres=0
    air_velocity=r.u32(r.addr('ccSpecialLayout')+4)
    # Native bitfield ABI: is_reflect is bit 26 of the word after motion_vars;
    # is_fastfall is bit 19. Verify the generated scalar record independently
    # by running its gameplay behavior on bodies with deliberately unlike data.
    bits=r.layout['flags']+16
    for body in range(12):
        for donor in range(12):
            if body==donor:continue
            for player in range(4):
                context(body,donor,player)
                r.call('ccn_ftCommonAttack11ProcUpdate',r.GOBJ)
                # Without a queued follow-up, no callback invents a jab.
                assert not status_calls
                r.u32(r.FP+fields['goto'],1)
                r.call('ccn_ftCommonAttack11ProcUpdate',r.GOBJ)
                assert status_calls[-1]==(fields['jab1'] if donor==9 else fields['jab2'])
                context(body,donor,player)
                r.call('ccn_ftCommonAttack13CheckGoto',r.GOBJ)
                third=donor in (0,4,5,7,11)
                assert bool(status_calls)==third,(body,donor,status_calls)
                if third:
                    assert r.u32(r.labels['CharCreator.active_normal_donor']+player*4)==donor
                    assert r.u32(r.FP+8)==body
                    r.call('ccStart',r.FP,0)
                    clock=r.addr('sFTCustomMoveClocks')+player*r.clock_size
                    assert r.u32(clock+r.clock_move)==r.addr('sFTCustomMoves')+(donor*33+29)*16
                chains+=1
                context(body,donor,player)
                r.u32(r.FP+0x24,fields['jab2'])
                threshold=5 if donor==5 else 6 if donor==7 else 4
                r.u32(r.FP+fields['input_count'],threshold-1)
                if donor==7:
                    table=r.u32(r.labels['Character.ACTION_ARRAY_TABLE']+donor*4)
                    # Captain jab3 is his first unique action.
                    r.u32(r.FP+0x24,0xDC)
                result=r.call('ccn_ftCommonAttack100StartCheckInterruptCommon',r.GOBJ)
                has_rapid=donor in (1,5,7,8,10)
                assert bool(result)==has_rapid,(body,donor,result,status_calls)
                if has_rapid:
                    assert status_calls[-1]>=0xDC
                    r.call('ccn_ftCommonAttack100LoopSetStatus',r.GOBJ)
                    r.call('ccStart',r.FP,0)
                    clock=r.addr('sFTCustomMoveClocks')+player*r.clock_size
                    assert r.u32(clock+r.clock_move)==r.addr('sFTCustomMoves')+(donor*33+31)*16
                    r.f32(clock+r.clock_frame,1000)
                    assert 0<r.advance()<1000
                    r.call('ccn_ftCommonAttack100EndSetStatus',r.GOBJ)
                    r.call('ccStart',r.FP,0)
                    assert r.u32(clock+r.clock_move)==r.addr('sFTCustomMoves')+(donor*33+32)*16
                rapid+=1
            context(body,donor,index=19)
            attrs=r.addr('sCCNormalAttributes')+donor*fields['attr_size']
            r.f32(r.ATTR+fields['gravity'],99)
            r.f32(r.FP+air_velocity+4,0)
            r.f32(r.FP+air_velocity,0)
            r.write(r.FP+r.layout['stick'],b'\0\0')
            r.call('ccn_ftPhysicsApplyAirVelDrift',r.GOBJ)
            assert abs(r.f32(r.FP+air_velocity+4)+r.f32(attrs+fields['gravity']))<.001
            assert r.u32(r.FP+0x9C8)==r.ATTR
            r.f32(r.FP+r.ground_velocity,100)
            floor_angle=r.u32(r.addr('ccMovementLayout')+32)
            r.f32(r.FP+floor_angle,0);r.f32(r.FP+floor_angle+4,1)
            material=r.f32(symbols['dMPCollisionMaterialFrictions'])
            r.call('ccn_ftPhysicsApplyGroundVelFriction',r.GOBJ)
            assert abs(r.f32(r.FP+r.ground_velocity)-(100-material*r.f32(attrs+fields['traction'])))<.001
            r.u32(r.FP+r.player_num,7)
            assert r.call('ftMainCharBuilderGetSpecialAttributes',r.FP)==r.ATTR
            physics+=1
            context(body,donor,index=23)
            r.u32(r.FP+0x24,fields['dair']);r.call('ccStart',r.FP,0)
            r.f32(r.GOBJ+r.layout['frame'],fields['rehit_begin']+1)
            r.u32(r.FP+bits,r.u32(r.FP+bits)|(1<<19))
            r.call('ccn_ftCommonAttackAirLwProcHit',r.GOBJ)
            if donor==5:
                assert r.f32(r.FP+air_velocity+4)==40
                assert not r.u32(r.FP+bits)&(1<<19)
                assert r.u32(r.FP+fields['rehit'])==fields['rehit_ticks']
                r.f32(r.GOBJ+r.layout['frame'],fields['rehit_begin'])
                for _ in range(fields['rehit_ticks']):r.call('ccn_ftCommonAttackAirLwProcUpdate',r.GOBJ)
                assert refreshed==[0,1]
            else:assert not status_calls and not refreshed
            bounces+=1
            context(body,donor,index=14)
            r.u32(r.FP+0x24,fields['fsmash']);r.call('ccStart',r.FP,0)
            r.u32(r.FP+fields['sphere'],r.addr('sCCNessBat'))
            r.call('ccn_ftCommonAttackS4ProcUpdate',r.GOBJ)
            assert bool(r.u32(r.FP+bits)&(1<<26))==(donor==11)
            if donor==11:
                output=0x80235000;clock=r.addr('sFTCustomMoveClocks')
                socket=r.u32(r.addr('sFTCustomNormalMechanics')+(11*33+14)*16+4)
                source_center=struct.unpack('>3f',r.read(socket+10*12,12))
                root_position=(1234,567,89)
                for axis,value in enumerate(root_position):
                    r.f32(r.JOINTS+r.layout['translate']+axis*4,value)
                for facing in (-1,1):
                    r.u32(r.FP+0x44,facing)
                    r.f32(clock+r.clock_frame,10)
                    assert r.call('ftMainCharBuilderGetNormalSphere',r.FP,output,output+64)
                    size=struct.unpack('>3f',r.read(output+64,12))
                    assert all(abs(x-300*r.f32(r.addr('sCCNormalAttributes')+11*fields['attr_size']))<.005 for x in size)
                    translation=struct.unpack('>3f',r.read(output+48,12))
                    expected=tuple(-(root_position[axis]+source_center[axis]*(1 if axis==1 else facing)) for axis in range(3))
                    assert all(abs(a-b)<.005 for a,b in zip(translation,expected)),(body,facing,translation,expected)
                r.u32(r.FP+r.layout['flags']+4,0)
                r.call('ccn_ftCommonAttackS4ProcUpdate',r.GOBJ)
                assert not r.u32(r.FP+bits)&(1<<26)
            spheres+=1
    # Landing branch availability follows each donor, even if the body's
    # native aerial lacks that landing clip. Native map/status setup is isolated.
    landings=0;landing_calls=[]
    r.services[symbols['mpCommonCheckFighterLanding']]=lambda:1
    r.services[symbols['mpCommonSetFighterGround']]=lambda:0
    r.services[symbols['ftCommonLandingAirNullSetStatus']]=lambda:landing_calls.append('null') or 0
    for donor in range(12):
        for index in range(19,24):
            body=(donor+1)%12
            context(body,donor,index=index)
            r.u32(r.FP+0x24,fields['nair']+index-19)
            r.call('ccStart',r.FP,0)
            r.u32(r.FP+fields['last_z'],255)
            r.u32(r.FP+r.layout['flags']+4,50)
            landing_calls.clear()
            r.call('ccn_ftCommonAttackAirProcMap',r.GOBJ)
            motion=r.motion(donor,index+5)
            available=r.read(r.addr('sCCNormalMotionAvailable')+donor*276+motion,1)[0]
            if available:
                assert status_calls==[fields['landing_start']+index-19],(donor,index,status_calls)
            else:assert landing_calls==['null'] and not status_calls,(donor,index,landing_calls,status_calls)
            landings+=1
    # A unique donor jab must never install its figatree/flags on the body.
    # Also verify safe Idle fallback for missing body angle/landing clips.
    body_data,body_params,donor_params=0x80220000,0x80221000,0x80225000
    r.u32(body_data+0x64,body_params)
    for body in range(12):
        donor=(body+1)%12
        context(body,donor)
        r.u32(r.FP+0x9C4,body_data)
        r.u32(r.labels['CharCreator.active_normal_donor'],donor)
        r.write(donor_params,struct.pack('>3I',0xBAD,0xCAB,0x40000000))
        jab_motion=r.u32(0x80128DD8+fields['jab1']*20)>>22
        r.write(body_params+jab_motion*12,struct.pack('>3I',0x111,0x222,0x333))
        r.u32(r.FP+0x24,0xDC)
        r.uc.reg_write(UC_MIPS_REG_S1,r.FP);r.uc.reg_write(UC_MIPS_REG_T2,0)
        r.call('parameter_record_hook_',donor_params,namespace='CharCreator',end=0x800E7560)
        record=r.reg(UC_MIPS_REG_T3)
        assert struct.unpack('>3I',r.read(record,12))==(0x111,0x80000000,0x333)
        assert r.reg(UC_MIPS_REG_V1)==body_data
    # Dynamic labels follow each saved body, including changes after the filter
    # is already synchronized. Test all original bodies on every editor page.
    r.services[r.labels['CharCreator.reset_cache_']]=lambda:0
    for body in range(12):
        for slot in range(4):
            table=r.u32(r.labels['CharCreator.slot_tables']+slot*4)
            r.u32(r.u32(table+4),body)
        r.call('sync_catalog_mode_',namespace='CharCreator')
        name=r.u32(r.labels['CharCreatorCatalog.string_table']+body*4)
        fox=r.u32(r.labels['CharCreatorCatalog.string_table']+4)
        for slot in range(4):
            entry=r.labels[f'Toggles.cc_slot_{slot+1}_nsp']
            table=r.u32(entry+0x14)
            assert table==r.labels['CharCreator.neutral_string_tables']+slot*52
            assert (r.u32(table),r.u32(table+4))==(name,fox)
    # Unsupported expanded donors on an original body retain native normal
    # commands instead of disabling collisions without a compiled clock.
    r.setup(0,0);r.preset(0,12)
    assert r.call('get_normal_donor_',r.FP,fields['jab1'],namespace='CharCreator')==0xFFFFFFFF
    for name,delegate in (('ftCommonAttack12SetStatus','Mewtwo.rapid_jab_patch_'),
                          ('ftCommonAttack100StartSetStatus','Slippy.unique_jab_loop_')):
        r.setup(12,0)
        r.services[r.labels[delegate]]=lambda:0x123
        assert r.call('hook_'+name,r.GOBJ,namespace='CharLabNormals')==0x123
    # Remix's aerial-fastfall dispatcher must enter each complete function,
    # including its guard/stack setup. Its old function+4 entry lost saved RA.
    dispatcher=r.labels['CharLabNormals.aerial_fastfall_']
    for address in (0x80129E38,0x80129E4C,0x80129E60,0x80129E74,0x80129E88):
        assert r.u32(address)==dispatcher
    toggle=r.labels['Toggles.entry_fast_fall_aerials']+4
    old_toggle=r.u32(toggle)
    r.services[0x800D90E0]=lambda:0x456
    r.services[0x800D9160]=lambda:0x789
    for enabled,expected in ((0,0x456),(1,0x789)):
        r.u32(toggle,enabled)
        assert r.call('aerial_fastfall_',r.GOBJ,namespace='CharLabNormals')==expected
    r.u32(toggle,old_toggle)
    # Restore all fixtures, including services installed by earlier checks.
    for address in list(r.services):
        if address not in saved_services:del r.services[address]
    for address,handler in saved_services.items():r.services[address]=handler
    r.call('ccReset')
    print(f'PASS: {len(hooks)} installed normal hooks, {chains} jab-chain and {rapid} rapid-jab cases, {physics} donor air/traction/generation cases, {bounces} bounce/rehit cases, {spheres} bat-flag cases, {landings} donor landing branches, twelve safe jab records and 48 dynamic body-name labels. Native status/contact setup is isolated; rendered acceptance remains pending.')
