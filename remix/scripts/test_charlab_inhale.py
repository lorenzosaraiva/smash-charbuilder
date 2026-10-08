"""Exercise borrowed inhale entry, source events, copy ownership and reset on MIPS.

Native status installation/resource loading are fixtures here. Optional real CPU
scenes separately check actual capture, held victims and both star releases.
"""
import json
import re
import struct
from pathlib import Path
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_T9, UC_MIPS_REG_F0


def test_inhale(r):
    root = Path(__file__).resolve().parents[1]
    lab = root.parent/'ssb-decomp-re'
    il = struct.unpack('>20I',r.read(r.addr('ccInhaleLayout'),80))
    for slot in range(4):
        entry=r.labels[f'Toggles.cc_slot_{slot+1}_nsp']
        assert r.u32(entry+12)==12,('Picker omits Kirby',slot)
        assert r.u32(entry+20)==r.labels['CharCreator.neutral_string_tables']+slot*52
    hooks = {v['name']:v for v in json.loads((root/'build/char_creator/runtime/special-hooks.json').read_text())}
    native = {n:int(a,16) for n,a in re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);',(lab/'symbols/symbols_us.txt').read_text(),re.M)}
    phases = json.loads((root/'build/char_creator/runtime/inhale-paths.json').read_text())
    motion = {v['name']:v['motion'] for v in phases}
    state = r.addr('sCCInhaleStates')
    passive = il[3]
    data, pointer, attr = 0x80230000,0x80231000,0x80232000
    original = dict(r.services)
    installed=[]
    discarded_stars=[]
    r.services[0x80103F78]=lambda:discarded_stars.append(r.reg(UC_MIPS_REG_A0)) or 0
    fighter_field=struct.unpack('>28I',r.read(r.addr('ccVisualLayout'),112))[8]
    def status():
        status=r.reg(UC_MIPS_REG_A1);installed.append(status)
        r.u32(r.FP+0x24,status)
        if il[4]<=status<=286:
            name=('nFTKirbyMotionSpecialAirN' if status>=278 else 'nFTKirbyMotionSpecialN')
            index=(status-278 if status>=278 else status-il[4])
            suffix=('Start','Loop','End','Loop','Eat','Throw','Wait','Turn','Copy')[index]
            r.u32(r.FP+0x28,motion[name+suffix])
    r.services[native['ftMainSetStatus']]=status
    for name in ('ftMainPlayAnimEventsAll','ftMainPlayAnimEventsForward','ftMainUpdateMotionEventsAll','ftParamProcStopEffect'):
        r.services[native[name]]=lambda:0
    r.services[native['func_800269C0_275C0']]=lambda:0
    # Pre-match file services are isolated, but dispatcher identity/context,
    # ABI argument spills, ownership and returned entry routine execute.
    for name in ('get_moveset_base_','ensure_main_file_','ensure_special_files_'):
        r.services[r.labels['CharCreator.'+name]]=lambda:0x80233000
    r.services[r.labels['CharCreator.ensure_special_preloads_']]=lambda:0
    r.services[r.labels['CharCreator.install_joint_fallbacks_']]=lambda:0
    def setup(body,port=0,air=0):
        r.call('ccReset');r.setup(body,8,port);r.preset(body,8,12)
        r.u32(r.FP+fighter_field,r.GOBJ)
        r.u32(r.labels['CharCreator.selected_builds']+port*4,1)
        r.u32(r.FP+r.layout['ga'],air)
        r.u32(r.FP+0x9C4,0x80228000)
        r.u32(r.FP+0x9D0,0x80229000)
        r.u32(r.labels['CharCreator.special_animation_heap']+port*4,0x8022A000)
        r.u32(0x80116E10+8*4,data)
        r.u32(data+0x28,pointer);r.u32(pointer,attr-0x100);r.u32(data+0x60,0x100)
        r.write(attr,bytes(0x400));r.f32(attr+r.layout['attr_size'],.91)
        r.write(r.FP+passive,b'\xA5'*32)
        r.u32(r.VALUES+15*4,12)
        r.call('ccSync',r.FP,r.ENTRIES,r.layout['training'])
        return state+port*il[0]
    def hook(name):
        r.labels['Test.inhale_hook']=r.labels[hooks[name]['hook']]
        r.call('inhale_hook',r.GOBJ,namespace='Test')
    entries=geometry=0
    for body in range(12):
        if body==8:continue
        for port in range(4):
            for air in (0,1):
                s=setup(body,port,air)
                r.call('get_air_nsp_routine_' if air else 'get_ground_nsp_routine_',r.GOBJ,namespace='CharCreator')
                entry='cc_ftKirbySpecialAirNStartSetStatus' if air else 'cc_ftKirbySpecialNStartSetStatus'
                assert r.reg(UC_MIPS_REG_T9)==r.addr(entry),(body,port,air,hex(r.reg(UC_MIPS_REG_T9)))
                assert r.u32(r.FP+8)==8
                assert r.u32(r.labels['CharCreator.body_character_id']+port*4)==body
                r.call(entry,r.GOBJ)
                assert r.u32(r.FP+0x24)==il[11 if air else 4]
                r.f32(r.GOBJ+r.layout['frame'],-1)
                hook('ftKirbySpecialAirNStartProcUpdate' if air else 'ftKirbySpecialNStartProcUpdate')
                assert r.u32(r.FP+0x24)==il[12 if air else 5]
                r.call('ccPrepare',r.GOBJ,0)
                # Native parser writes source catch attacks and throw values.
                r.advance();r.events()
                assert r.u32(r.FP+0x294) and r.u32(r.FP+0x294+0xC4)
                assert r.u32(r.FP+r.layout['throw_desc'])
                for frame in (0,1,5,23,80):
                    clock=r.addr('sCCSpecialClocks')+port*36
                    r.f32(clock+20,frame);r.call('ccCollision',r.FP)
                    for i,z in enumerate((200,410)):
                        attack=r.FP+0x294+i*0xC4
                        actual=struct.unpack('>3f',r.read(attack+0x18,12))
                        expected=(0,240*.91/2,z*.91/2)
                        assert all(abs(a-b)<.004 for a,b in zip(actual,expected)),(body,port,air,frame,actual,expected)
                        assert r.u32(attack+0x14)==r.JOINTS
                        geometry+=1
                assert r.read(r.FP+passive,32)==b'\xA5'*32
                assert r.u32(s+il[1])==12
                # The held-button gate and original minimum release lag execute.
                r.write(r.FP+il[18],struct.pack('>H',0x4000))
                r.write(r.FP+r.layout['b_mask'],struct.pack('>H',0x4000))
                hook('ftKirbySpecialAirNLoopProcInterrupt' if air else 'ftKirbySpecialNLoopProcInterrupt')
                assert r.u32(r.FP+0x24)==il[12 if air else 5]
                r.write(r.FP+il[18],b'\0\0')
                for _ in range(40):hook('ftKirbySpecialAirNLoopProcInterrupt' if air else 'ftKirbySpecialNLoopProcInterrupt')
                assert r.u32(r.FP+0x24)==(280 if air else 271)
                entries+=1
    copies=0
    for body in range(12):
        if body==8:continue
        for port in range(4):
            for choice in range(1,13):
                s=setup(body,port)
                r.u32(r.labels['CharCreator.body_character_data']+port*4,0x80228000)
                r.u32(r.labels['CharCreator.body_character_id']+port*4,body)
                r.u32(r.labels['CharCreator.active_special_donor']+port*4,8)
                r.u32(r.FP+8,8)
                r.write(r.FP+il[2],struct.pack('>h',choice));r.u32(r.FP+r.layout['flags']+4,1)
                hook('ftKirbySpecialNCopyInitCopyVars')
                assert r.u32(s+il[1])==choice,(body,port,choice,hex(s),r.read(s,12).hex(),r.read(r.FP+r.layout['flags'],16).hex(),r.layout['flags'])
                assert not r.u32(r.FP+r.layout['flags']+4)
                assert r.read(r.FP+passive,32)==b'\xA5'*32
                # Recovery restores the body; the next dispatch still sees copy.
                r.u32(r.FP+8,body)
                r.u32(r.labels['CharCreator.body_character_data']+port*4,0)
                r.u32(r.labels['CharCreator.active_special_donor']+port*4,-1)
                assert r.call('ccInhaleChoice',r.FP,12)==choice
                assert r.u32(r.u32(r.u32(r.labels['CharCreator.slot_tables'])+15*4))==12
                r.call('get_ground_nsp_routine_',r.GOBJ,namespace='CharCreator')
                donor=(None,1,0,4,9,11,7,10,2,3,5,6,8)[choice]
                expected=(r.u32(r.labels['Character.ground_nsp.table']+body*4) if body==donor else
                          r.addr('cc_ftKirbySpecialNStartSetStatus') if choice==12 else r.addr('ccNeutral'))
                assert r.reg(UC_MIPS_REG_T9)==expected,(body,port,choice,hex(r.reg(UC_MIPS_REG_T9)),hex(expected))
                r.u32(r.FP+8,body)
                r.u32(r.labels['CharCreator.active_special_donor']+port*4,-1)
                r.u32(r.labels['CharCreator.body_character_data']+port*4,0)
                r.u32(r.FP+r.player_num,1)
                assert r.call('ccInhaleChoice',r.FP,12)==12,('Respawn retained copy',body,port,choice)
                copies+=1
    # A caught opponent contributes its actual Neutral B, including a custom
    # recipe or native Kirby's current copy; temporary donor identity is ignored.
    victim,vgobj,vtop=0x80240000,0x80243000,0x80244000
    victims=0
    body_choices=(2,1,8,9,3,10,11,6,12,4,7,5)
    for body in range(12):
        for selected in range(13):
            setup(0)
            r.u32(r.labels['CharCreator.body_character_data'],0x80228000)
            r.u32(r.labels['CharCreator.body_character_id'],0)
            r.u32(r.labels['CharCreator.active_special_donor'],8)
            r.u32(r.FP+8,8);r.u32(r.FP+0x24,il[7])
            for name,value in (('body_character_data',0),('body_character_id',-1),('active_special_donor',-1)):
                r.u32(r.labels['CharCreator.'+name]+4,value)
            r.write(victim,bytes(r.layout['size']));r.write(vgobj,bytes(0x100));r.write(vtop,bytes(0x100))
            r.u32(vgobj+0x84,victim);r.u32(vgobj+r.layout['obj'],vtop)
            r.u32(victim+8,body);r.write(victim+0xD,b'\1')
            r.u32(victim+passive,1) # Native Kirby already has Fox.
            for i,v in enumerate((160,100,0)):r.f32(vtop+r.layout['translate']+i*4,v)
            r.u32(r.FP+r.layout['catch'],vgobj)
            table=r.u32(r.labels['CharCreator.slot_tables']+4)
            for field,value in ((0,1),(1,body),(15,selected)):r.u32(r.u32(table+field*4),value)
            r.u32(r.labels['CharCreator.selected_builds']+4,2)
            hook('ftKirbySpecialNCatchProcUpdate')
            actual=struct.unpack('>h',r.read(r.FP+il[2],2))[0]
            expected=1 if body==8 and selected in (0,12) else selected or body_choices[body]
            assert actual==expected,('Captured Neutral choice',body,selected,actual,expected)
            assert r.u32(r.FP+0x24)==il[8]
            victims+=1
    # Native common damage calls this hook for every body. Its probability and
    # owned-state reset execute without touching foreign passive copy fields.
    setup(2)
    r.u32(r.labels['CharCreator.body_character_data'],0x80228000)
    r.u32(r.labels['CharCreator.body_character_id'],2)
    r.u32(r.FP+8,8)
    r.write(r.FP+il[2],struct.pack('>h',9))
    r.u32(r.FP+r.layout['flags']+4,1)
    r.u32(r.labels['CharCreator.active_special_donor'],8)
    hook('ftKirbySpecialNCopyInitCopyVars')
    r.u32(r.FP+8,2)
    r.u32(r.labels['CharCreator.body_character_data'],0)
    r.u32(r.labels['CharCreator.active_special_donor'],-1)
    random_value=[.5]
    def random():r.uc.reg_write(UC_MIPS_REG_F0,struct.unpack('>I',struct.pack('>f',random_value[0]))[0])
    r.services[native['syUtilsRandFloat']]=random
    hook('ftKirbySpecialNDamageCheckLoseCopy')
    assert r.u32(state+il[1])==9
    random_value[0]=.01;hook('ftKirbySpecialNDamageCheckLoseCopy')
    assert r.u32(state+il[1])==12
    assert r.read(r.FP+passive,32)==b'\xA5'*32
    # Ground and aerial source absorb flags fire exactly at frame eight;
    # copied ability remains match-owned and native passive memory is untouched.
    for air in (0,1):
        setup(0)
        r.u32(r.labels['CharCreator.body_character_data'],0x80228000)
        r.u32(r.labels['CharCreator.body_character_id'],0)
        r.u32(r.labels['CharCreator.active_special_donor'],8)
        r.u32(r.FP+8,8);r.u32(r.FP+0x24,286 if air else il[10])
        r.u32(r.FP+0x28,motion['nFTKirbyMotionSpecial'+('Air' if air else '')+'NCopy'])
        r.write(r.FP+il[2],struct.pack('>h',2));r.call('ccPrepare',r.GOBJ,0)
        for frame in range(12):
            r.advance();r.events();hook('ftKirbySpecialNCopyInitCopyVars')
            assert r.u32(state+il[1])==(12 if frame<8 else 2),(air,frame)
        before=len(discarded_stars)
        r.call('ccStatusChanging',r.GOBJ,189) # native Appeal
        assert r.u32(state+il[1])==12
        assert discarded_stars[before:]==[r.GOBJ], 'Copy discard did not emit exactly one star'
        r.call('ccStatusChanging',r.GOBJ,189)
        assert len(discarded_stars)==before+1, 'Empty copy discard emitted another star'
        r.write(r.FP+il[2],struct.pack('>h',9));r.u32(r.FP+r.layout['flags']+4,1)
        hook('ftKirbySpecialNCopyInitCopyVars')
        r.call('ccStatusChanging',r.GOBJ,0)
        assert r.call('ccInhaleChoice',r.FP,12)==12
    # A native Kirby keeps Remix's own dispatcher and copy-loss routines.
    setup(8)
    assert r.call('ccUseSpecialCallback',r.GOBJ,0,-3,0)==0
    assert r.call('ccInhaleChoice',r.FP,12)==12
    assert not r.u32(state)
    for selected in (0,12):
        r.preset(8,8,selected)
        for side in ('ground','air'):
            r.call('get_'+side+'_nsp_routine_',r.GOBJ,namespace='CharCreator')
            assert r.reg(UC_MIPS_REG_T9)==r.u32(r.labels['Character.'+side+'_nsp.table']+8*4)
            assert r.reg(UC_MIPS_REG_A1)==r.FP, 'Native Kirby magic-hat ABI lost fighter argument'
    for address in list(r.services):
        if address not in original:del r.services[address]
    r.services.update(original)
    print(f'PASS: {entries} foreign inhale entries/ground-air button transitions, {geometry} donor catch placements, {copies} copy choices across bodies/ports, {victims} captured recipe/native choices, source absorb events, passive isolation, damage/respawn/taunt/death reset and native Kirby dispatch. Status/resource services are fixtures; contact is checked in optional real CPU scenes.')
