"""Check streamed paired geometry against the independent source ELF.

Execute real MIPS cache/socket code and SRAM packing; OS DMA is a fixture.
Native capture, release, cargo, landing and taunt transitions run in CPU scenes.
"""
import json
import math
import struct
from pathlib import Path
from elfData import read_elf
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_V0


def test_pairs(r, rom):
    collision = json.loads((Path(__file__).resolve().parents[1]/
        'build/char_creator/runtime/special-collision.json').read_text())
    cache_samples = 0
    retained = {}
    for record in collision['records']:
        for offset in (0, 52, record['size']-52):
            for port in range(4):
                r.setup(0, 1)
                r.write(r.FP+0xD, bytes([port]))
                source = collision['rom_start']+record['offset']+offset
                pointer = r.call('ccCollisionSourceFrame', r.FP, source)
                expected = rom[source:source+52]
                assert r.read(pointer,52) == expected
                retained[port] = (pointer,expected)
                for previous,(address,data) in retained.items():
                    assert r.read(address,52) == data, ('collision cache eviction',port,previous)
                cache_samples += 1
            retained.clear()
    r.call('ccReset')
    print(f'PASS: {cache_samples} exact special collision DMA samples across four independent player caches.')
    # Native heap overflow must continue beyond live pools, rather than reuse
    # their starting address on the next overflow/UI setup.
    cursor = r.labels['custom_heap_address']; base = r.labels['custom_heap']
    for heap,end,expected in ((0x800465E8,base+64,base+64),(0x800465E8,base+32,base+64),
                              (0x80240000,base+128,base+64),(0x800465E8,0x80310000,base+64)):
        r.uc.reg_write(UC_MIPS_REG_V0,end)
        r.call('_return',0,0,0,heap,namespace='CharacterSelect.increase_heap_')
        assert r.u32(heap+12)==end and r.u32(cursor)==expected
    r.call('heap_reset_',namespace='CharLab')
    assert r.u32(cursor)==base
    # Settings uses link 3 for menu objects too, whose user_data can be NULL.
    # An empty sidecar must not mistake one for its stored fighter on reset.
    r.write(0x80230000,bytes(0x100))
    r.u32(0x800466F0+12,0x80230000)
    r.call('ccReset')
    r.u32(0x800466F0+12,0)
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root/'build/char_creator/runtime/paired-geometry.json').read_text())
    oracle, sections, symbols = read_elf(root.parent/'ssb-decomp-re/build/testPairedMoves', '<')
    def original(name, fmt):
        address, length, index = symbols[name]
        section = sections[index]
        data = oracle[section[4]+address-section[3]:section[4]+address-section[3]+length]
        width = struct.calcsize('<'+fmt)
        return [struct.unpack_from('<'+fmt, data, offset) for offset in range(0, length, width)]
    scripts = 0
    for name in symbols:
        if name.startswith('sFTCustomPair') and name.endswith(('Script','Visual','Throws','MarioTauntScales')):
            values = original(name,'I')
            expected = b''.join(struct.pack('>I',word) for word, in values)
            assert r.read(r.addr(name),len(expected)) == expected, name
            scripts += 1
    assert scripts >= 170, scripts
    layout = struct.unpack('>15I', r.read(r.addr('ccPairLayout'), 60))
    state_size, phase_size, frame_size, state_phase, phase_offset = layout[:5]
    phases = r.addr('sFTCustomPairPhases')
    bank = manifest['rom_start']
    total = 0
    releases = 0
    saved = dict(r.services)
    release_calls = []
    r.services[0x8014AB64] = lambda: release_calls.append(('position',r.reg(UC_MIPS_REG_A0)))
    r.services[0x8014AFD0] = lambda: release_calls.append(('release',r.reg(UC_MIPS_REG_A0),r.reg(UC_MIPS_REG_A1),r.reg(UC_MIPS_REG_A2)))
    r.services[0x800E8098] = lambda: release_calls.append(('immune',r.reg(UC_MIPS_REG_A1)))
    # Native status setup installs the original engine callback, rather than
    # the separately compiled numeric fallback with the same C name.
    r.services[0x800E6F24] = lambda: r.u32(r.FP+r.layout['update'],0x8014A0C0)
    for item in manifest['phases']:
        anchors = original(item['anchor'], '12f')
        travel = original(item['travel'], '3f') if item['travel'] != 'NULL' else [(0.,)*3]*item['count']
        hits = original(item['collision'], '12fI') if item['collision'] != 'NULL' else [(0.,)*12+(0,)]*item['count']
        props = [original(name, '9fI') for name in item['prop_arrays']]
        expected = b''.join(struct.pack('>15f12fI', *anchors[t], *travel[t], *hits[t]) +
                            b''.join(struct.pack('>9fI', *(prop[t] if i < len(props) else (0.,)*9+(0,)))
                                     for i, prop in enumerate(props+[[None]*item['count']]*(6-len(props))))
                            for t in range(item['count']))
        # Every source float/active mask, including all tether/prop samples.
        assert len(expected) == item['count']*frame_size
        assert rom[bank+item['offset']:bank+item['offset']+len(expected)] == expected, item
        phase = phases+item['index']*phase_size
        assert r.u32(phase+phase_offset) == item['offset']
        for port in range(4):
            r.setup((port+1)%12, 0, port)
            s = r.addr('sFTCustomPairStates')+port*state_size
            r.write(s, struct.pack('>5I', r.FP, 0, r.u32(r.FP+r.player_num), 0, phase))
            status, motion = r.u32(phase+4), r.u32(phase+8)
            r.u32(s+20, r.u32(phase)); r.u32(s+28, status)
            r.u32(r.FP+0x24,status); r.u32(r.FP+0x28,motion)
            fighter_offset = r.u32(r.addr('ccVisualLayout')+8*4)
            r.u32(r.FP+fighter_offset,r.GOBJ)
            clock = r.addr('sFTCustomMoveClocks')+port*r.clock_size
            move = phase+layout[5]
            r.write(clock,struct.pack('>6I2fIIf',r.FP,r.u32(r.FP+r.player_num),move,status,motion,r.u32(move+8),0,0,r.u32(move+12),0,1))
            for axis, value in enumerate((1234.,-56.,78.)):
                r.f32(r.JOINTS+r.layout['translate']+axis*4,value)
            # Both sides of every eight-frame DMA block and the last sample.
            for t in sorted({0, item['count']-1} | set(range(7,item['count'],8)) | set(range(8,item['count'],8))):
                sample = r.call('ccPairSample', r.FP, t)
                assert r.read(sample, frame_size) == expected[t*frame_size:(t+1)*frame_size]
                r.f32(clock+r.clock_frame,t)
                for facing in (-1,1):
                    angle = facing*math.pi/2
                    r.f32(r.JOINTS+r.layout['rotate']+4,angle)
                    assert r.call('ftMainCharBuilderPairSocket',r.FP,0x80218000)
                    x,y,z = anchors[t][9:12]
                    actual = struct.unpack('>3f',r.read(0x80218000,12))
                    wanted = (1234+math.cos(angle)*x+math.sin(angle)*z,-56+y,78-math.sin(angle)*x+math.cos(angle)*z)
                    assert max(abs(a-b) for a,b in zip(actual,wanted)) < .003, (item['index'],port,t,facing,actual,wanted)
                total += 1
            if status in (r.layout['throw_status'],r.layout['throw_status']+1):
                r.call('ccPairSetStatus',r.GOBJ,status,0,0x3F800000)
                assert r.u32(r.FP+r.layout['update'])==r.addr('ftMainCharBuilderPairThrowUpdate'), ('Native throw callback not handed off',item)
                for flag in (1,2):
                    release_calls.clear()
                    kind = 2 if status==r.layout['throw_status']+1 else 1
                    r.u32(s+24,kind)
                    r.u32(r.FP+0x44,1); r.u32(r.FP+0x180,1); r.u32(r.FP+0x184,flag)
                    r.u32(r.FP+r.layout['catch'],0x80219000)
                    r.f32(r.GOBJ+r.layout['frame'],12)
                    r.call('ftMainCharBuilderPairThrowUpdate',r.GOBJ)
                    assert release_calls==[('position',0x80219000),('release',0x80219000,1 if flag==1 else 0xFFFFFFFF,kind==2),('immune',0)], (item,flag,release_calls)
                    assert r.u32(r.FP+r.layout['catch'])==0 and r.u32(r.FP+0x184)==0
                    assert r.u32(r.FP+0x44)==0xFFFFFFFF and r.u32(r.FP+0x180)==0
                    releases += 1
            if r.u32(phase)==2 and status in (244,245):
                # Landing after an air toss can replay the retained source
                # release flag. An already released victim cannot be used twice.
                release_calls.clear()
                r.u32(r.FP+r.layout['catch'],0); r.u32(r.FP+0x184,1)
                r.f32(r.GOBJ+r.layout['frame'],12)
                r.call('ccp_ftDonkeyThrowFFProcUpdate',r.GOBJ)
                assert not release_calls, ('Repeated cargo release',port,status,release_calls)
            # A reused fighter must not keep the donor socket.
            r.u32(r.FP+r.player_num,r.u32(r.FP+r.player_num)+1)
            assert r.call('ftMainCharBuilderPairSocket',r.FP,0x80218000)==0
    assert releases == 184, releases
    for address in list(r.services):
        if address not in saved: del r.services[address]
    r.services.update(saved)
    r.call('ccReset')
    # Full donor taunts round-trip alongside all old fields, using the actual
    # recipe serializer. DADDU->ADDU only accommodates Unicorn's MIPS32 CPU.
    patched = []
    for name in ('export_', 'import_'):
        address = r.labels['Menu.'+name]+24
        word = r.u32(address); assert word & 63 == 0x2D
        patched.append((address, word)); r.u32(address, (word & ~63)|0x21)
    tables = [r.u32(r.labels['CharCreator.slot_tables']+i*4) for i in range(4)]
    options = r.labels['Toggles.block_char_creator_options']
    for donor in range(12):
        values = [(donor+port)%12 for port in range(4)]
        for table, value in zip(tables, values):
            r.u32(r.u32(table+21*4), value)
        r.call('export_neutral_choices_', namespace='CharCreator')
        snapshots = [[r.u32(r.u32(table+field*4)) for field in range(22)] for table in tables]
        for port, table in enumerate(tables):
            block = r.labels[f'Toggles.block_char_creator_{port+1}']
            head = r.u32(table)-4
            r.call('export_', head, block, namespace='Menu')
            for field in range(22): r.u32(r.u32(table+field*4), 0)
            r.call('import_', head, block, namespace='Menu')
            assert [r.u32(r.u32(table+field*4)) for field in range(22)] == snapshots[port]
        r.call('import_neutral_choices_', namespace='CharCreator')
        assert [r.u32(r.u32(table+21*4)) for table in tables] == values
    for marker in (0, 0x5441FFFF):
        r.u32(options+0x1C, marker)
        bodies = [3,6,9,11]
        for table, body in zip(tables,bodies): r.u32(r.u32(table+4), body)
        r.call('import_neutral_choices_', namespace='CharCreator')
        assert [r.u32(r.u32(table+21*4)) for table in tables] == bodies
    for address,word in patched: r.u32(address,word)
    r.call('ccReset')
    print(f'PASS: all 73 paired/taunt phase geometry banks and {scripts} event/audio/throw/scale arrays match independent ELF; {total} MIPS cache/boundary samples, {total*2} donor sockets and {releases} release/facing/ownership checks across four ports; all twelve taunt choices round-trip with legacy recipes and old/invalid-save fallback.')
