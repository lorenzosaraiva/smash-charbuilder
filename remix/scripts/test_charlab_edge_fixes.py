"""Execute reported UI, unavailable-move and taunt-pivot regressions in MIPS."""
import json
import struct
from pathlib import Path
from unicorn.mips_const import UC_MIPS_REG_V0, UC_MIPS_REG_T9


def test_edge_fixes(r):
    saved=dict(r.services)
    r.services[r.labels['Menu.update_pointer_']]=lambda:0
    r.services[r.labels['CharCreator.reset_cache_']]=lambda:0
    expected=(2,1,8,9,3,10,11,6,0,4,7,5)
    for port in range(4):
        table=r.u32(r.labels['CharCreator.slot_tables']+port*4)
        entry=0x80228000;r.u32(entry+0x24,port+1)
        for body,neutral in enumerate(expected):
            r.u32(r.u32(table+4),body)
            for field in range(2,22):r.u32(r.u32(table+field*4),11)
            r.uc.reg_write(UC_MIPS_REG_V0,entry)
            r.call('copy_body_to_all_',namespace='CharCreator')
            values=[r.u32(r.u32(table+field*4)) for field in range(2,22)]
            assert values[13]==neutral,('Copy-body neutral selector',port,body,values)
            assert all(v==body for i,v in enumerate(values) if i!=13),(port,body,values)
    r.services.update(saved)
    for address in list(r.services):
        if address not in saved:del r.services[address]
    # Real original tables expose DK's missing air Down B. No file loads or
    # native-body entry may run, and no donor context may be installed.
    for body in range(12):
        if body==2:continue
        for port in range(4):
            r.setup(body,2,port);r.preset(body,2)
            r.u32(r.labels['CharCreator.selected_builds']+port*4,1)
            before=r.read(r.FP,r.layout['size'])
            r.call('get_air_dsp_routine_',r.GOBJ,namespace='CharCreator')
            assert r.reg(UC_MIPS_REG_T9)==r.labels['CharCreator.unavailable_special_'],(body,port)
            assert r.read(r.FP,r.layout['size'])==before
            assert r.u32(r.labels['CharCreator.active_special_donor']+port*4)==0xFFFFFFFF
    manifest=json.loads((Path(__file__).resolve().parents[1]/'build/char_creator/runtime/paired-geometry.json').read_text())
    phase=next(p for p in manifest['phases'] if p['index']==61)
    sizes=struct.unpack('>15I',r.read(r.addr('ccPairLayout'),60))
    state_size,phase_size=sizes[:2]
    for body in range(1,12):
        r.setup(body,0)
        r.u32(r.FP+0x24,189);r.u32(r.FP+0x28,164)
        r.u32(r.FP+r.u32(r.addr('ccVisualLayout')+32),r.GOBJ)
        s=r.addr('sFTCustomPairStates');p=r.addr('sFTCustomPairPhases')+61*phase_size
        r.write(s,struct.pack('>10I',r.FP,0,r.u32(r.FP+r.player_num),0,p,0,0,189,0,0))
        r.u32(r.addr('sCCPairDonors'),0)
        clock=r.addr('sFTCustomMoveClocks');move=p+sizes[5]
        r.write(clock,struct.pack('>6I2fIIf',r.FP,r.u32(r.FP+r.player_num),move,189,164,180,0,0,0,0,1))
        model=r.JOINTS+0x400;root=r.JOINTS
        r.f32(root+r.layout['translate']+4,1234)
        standing=None
        for tick in (0,20,40,60,100,120,140,180):
            r.f32(clock+r.clock_frame,tick)
            r.call('ccAdvance',r.GOBJ)
            pivot=r.f32(model+r.layout['translate']+4)/r.f32(model+r.layout['scale']+4)
            if standing is None:standing=pivot
            assert standing>0 and abs(pivot-standing)<.001,(body,tick,pivot,standing)
            assert r.f32(root+r.layout['translate']+4)==1234
    r.call('ccReset')
    print('PASS: copy-body Neutral B/all fields on twelve bodies/four slots; unavailable aerial DK Down B never calls body fallback; Mario growth pivots stay planted on eleven foreign rigs without moving TopN.')
