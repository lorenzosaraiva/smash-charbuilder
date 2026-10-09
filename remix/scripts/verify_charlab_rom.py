"""Check the linked Remix port and execute its production MIPS code with Unicorn.

Engine motion parsing runs from the built ROM. Staling, sound, rendering and
status setup services are stubbed where indicated; this is not an emulator
playtest or verification of contact detection, rendering or every special.
"""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'ssb-decomp-re'
sys.path.insert(0, str(LAB / 'tools'))
from elfData import read_elf
from n64crc import calculate_crcs
from verifyCustomMoveData import verify_sources
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.mips_const import *


def linked_object(rom, labels):
    """Independently apply ELF relocations and compare every allocated byte."""
    assert labels['CharLabRuntime.end']%16==0, 'Runtime data left following code unaligned'
    native_addresses={name:int(address,16) for name,address in re.findall(
        r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+);',
        (ROOT.parent/'ssb-decomp-re/symbols/symbols_us.txt').read_text(),re.M)}
    for hook in json.loads((ROOT/'build/char_creator/runtime/special-hooks.json').read_text()):
        if hook['name'] in native_addresses:
            assert hook['address']==native_addresses[hook['name']],('Wrong native hook address',hook['name'])
        assert hook['name']!='ftKirbySpecialNGetCaptureDistance','Vector helper must retain native ABI'
    for name,address in labels.items():
        if name.startswith(('CharLabSpecials.hook_', 'CharLabPairs.hook_', 'CharLabNormals.hook_')):
            assert address%4==0, ('Unaligned MIPS hook',name,hex(address))
    obj, sections, symbols = read_elf(ROOT / 'build/char_creator/runtime/runtime.o', '>')
    runtime = (ROOT / 'build/char_creator/runtime/runtime.asm').read_text()
    externals = {int(i): labels[v] if v in labels else int(v, 0)
                 for i, v in re.findall(r'constant symbol_(\d+)\(([^)]+)\)', runtime)}
    symsec = next(s for s in sections if s[1] == 2)
    addresses = {}
    for i, offset in enumerate(range(symsec[4], symsec[4]+symsec[5], 16)):
        _, value, _, _, _, index = struct.unpack_from('>IIIBBH', obj, offset)
        if index and 'CharLabRuntime.section_'+str(index) in labels:
            addresses[i] = labels['CharLabRuntime.section_'+str(index)] + value
        elif i in externals:
            addresses[i] = externals[i]
    payloads = {i: bytearray(s[5]) if s[1] == 8 else bytearray(obj[s[4]:s[4]+s[5]])
                for i, s in enumerate(sections) if 'CharLabRuntime.section_'+str(i) in labels}
    count = 0
    for s in sections:
        if s[1] != 9 or s[7] not in payloads:
            continue
        target = payloads[s[7]]
        raw = bytes(target)
        pending = {}
        for offset in range(s[4], s[4]+s[5], 8):
            position, info = struct.unpack_from('>II', obj, offset)
            symbol, kind = info >> 8, info & 255
            address = addresses[symbol]
            word = struct.unpack_from('>I', raw, position)[0]
            if kind == 5:
                pending.setdefault(symbol, []).append((position, word))
                continue
            if kind == 2:
                result = (address + word) & 0xFFFFFFFF
            elif kind == 4:
                result = word & 0xFC000000 | ((address + ((word & 0x3FFFFFF) << 2)) >> 2) & 0x3FFFFFF
            elif kind == 6:
                low = word & 65535
                low -= 65536 if low & 32768 else 0
                for highpos, highword in pending.pop(symbol, []):
                    combined = address + ((highword & 65535) << 16) + low
                    struct.pack_into('>I', target, highpos, highword & 0xFFFF0000 | ((combined + 32768) >> 16) & 65535)
                    count += 1
                result = word & 0xFFFF0000 | (address + low) & 65535
            else:
                raise AssertionError('Unexpected relocation '+str(kind))
            struct.pack_into('>I', target, position, result)
            count += 1
        assert not pending, 'Unpaired HI16 relocation'
    for i, payload in payloads.items():
        offset = labels['CharLabRuntime.section_'+str(i)] - 0x80400000 + 0x3800000
        actual=rom[offset:offset+len(payload)]
        differences=[j for j in range(0,len(payload),4) if actual[j:j+4]!=payload[j:j+4]][:8]
        assert actual == payload, ('Linked section differs',i,[(hex(j),actual[j:j+4].hex(),payload[j:j+4].hex()) for j in differences])
    # Compare donor event words, all trajectories and animation poses with the
    # already source-checked shared host build, excluding relocated pointers.
    host, hs, syms = read_elf(LAB / 'build/testCustomMove', '<')
    verify_sources(host, hs, syms)
    checked = 0
    for name, (address, length, index) in syms.items():
        if name not in symbols or not length or hs[index][1] == 8:
            continue
        if not name.startswith(('sFTCustom', 'sFTCharBuilderLaser', 'sFTCharBuilderAction',
                                'sFTCharBuilderProjectile', 'sFTCharBuilderYoshiInterrupt')):
            continue
        actual, actual_length, actual_index = symbols[name]
        if actual_length != length or length % 4:
            continue
        # Records containing pointers are covered by the relocation check.
        if name in ('sFTCustomMoves', 'sFTCustomGrabMoves', 'sFTCustomAnimationPilots',
                    'sFTCustomCollisionTrajectories', 'sFTCharBuilderLaserMoves',
                    'sFTCharBuilderActions', 'sFTCharBuilderProjectileMoves'):
            continue
        if name.startswith(('sFTCustomAnimationRig', 'sFTCustomAnimationSourceRig', 'sFTCustomAnimationSemantic')):
            continue  # Mixed byte/float rig records are checked independently.
        start = hs[index][4] + address - hs[index][3]
        fmt = 'B' if name in ('sFTCustomJointMaps', 'sFTCustomGrabJointMap') else 'H' if name == 'sFTCustomGrabTimings' else 'I'
        count_values = length // struct.calcsize(fmt)
        expected = struct.pack('>'+str(count_values)+fmt, *struct.unpack_from('<'+str(count_values)+fmt, host, start))
        start = sections[actual_index][4] + actual - sections[actual_index][3]
        assert obj[start:start+length] == expected, 'Shared data differs: '+name
        checked += 1
    assert checked >= 650, checked
    geometry=0
    for filename,prefix in (('testNormalMechanics','sFTCustomNormal'),('testSpecialTiming','sFTCharBuilderSpecial')):
        reference,rs,reference_symbols=read_elf(LAB/'build'/filename,'<')
        for name,(address,length,index) in reference_symbols.items():
            if not name.startswith(prefix) or not name.endswith(('Travel','Socket','Frames','Spawn')) or name not in symbols:
                continue
            actual,actual_length,actual_index=symbols[name]
            assert actual_length==length and length%4==0,name
            start=rs[index][4]+address-rs[index][3]
            expected=struct.pack('>'+str(length//4)+'I',*struct.unpack_from('<'+str(length//4)+'I',reference,start))
            start=sections[actual_index][4]+actual-sections[actual_index][3]
            assert obj[start:start+length]==expected,'Source movement/collision differs: '+name
            geometry+=1
    info = json.loads((ROOT/'build/char_creator/runtime/special-collision.json').read_text())
    reference,rs,reference_symbols=read_elf(LAB/'build/testSpecialTiming','<')
    for record in info['records']:
        address,length,index=reference_symbols[record['name']]
        assert length == record['size']
        start=rs[index][4]+address-rs[index][3]
        expected=struct.pack('>'+str(length//4)+'I',*struct.unpack_from('<'+str(length//4)+'I',reference,start))
        start=info['rom_start']+record['offset']
        assert rom[start:start+length] == expected, record['name']
        geometry += 1
    assert geometry>=150,geometry
    assert labels['custom_heap'] < 0x80780000, 'Expansion RAM heap headroom too small'
    print(f'PASS: {count} relocations, all allocated runtime bytes, {checked} shared donor tables/poses and {geometry} source special/normal geometry arrays match; expansion heap at {labels["custom_heap"]:08X}.')


class Runtime:
    FP, GOBJ, ATTR, JOINTS, ENTRIES, VALUES = 0x80200000, 0x80203000, 0x80204000, 0x80206000, 0x80210000, 0x80211000
    STACK, STOP = 0x803FF000, 0x803FE000

    def __init__(self, rom, labels):
        self.labels = labels
        self.rom = rom
        self.uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_BIG_ENDIAN)
        # KSEG0 is translated to physical RAM by Unicorn's MIPS CPU.
        self.uc.mem_map(0, 0x800000)
        self.uc.mem_map(0x80000000, 0x800000)
        # Native math/physics helpers use the original main-code addresses.
        self.uc.mem_write(0x80000400, rom[0x1000:0x415C0])
        self.uc.mem_write(0x400, rom[0x1000:0x415C0])
        self.uc.mem_write(0x80400000, rom[0x3800000:0x3800000+0x400000])
        self.uc.mem_write(0x800D6490, rom[0x51C90:0xAC540])
        # Mirror initial ROM data in the physical alias as well.
        self.uc.mem_write(0x400000, rom[0x3800000:0x3800000+0x400000])
        self.uc.mem_write(0xD6490, rom[0x51C90:0xAC540])
        self.uc.mem_write(0x131B00, rom[0xAC540:0x109FB0])
        self.uc.mem_write(0x80131B00, rom[0xAC540:0x109FB0])
        self.uc.reg_write(UC_MIPS_REG_CP0_STATUS, 0x20000000)
        class Services(dict):
            def __setitem__(services, address, handler):
                if address not in services:
                    self.uc.hook_add(UC_HOOK_CODE, self.service, begin=address, end=address)
                super().__setitem__(address, handler)
        self.services = Services()
        self.calls = []
        names = ('size', 'pkind', 'ga', 'flags', 'attack_id', 'throw_desc', 'update', 'interrupt',
                 'accessory', 'attr_size', 'obj', 'frame', 'translate', 'rotate', 'scale', 'speed',
                 'dobj_size', 'catch', 'capture', 'catch_status', 'catch_motion', 'throw_status',
                 'throw_f', 'throw_b', 'dk_throw_ff', 'shouldered', 'thrown_common', 'vs', 'training', 'air',
                 'thrown_table', 'stick', 'tap', 'b_mask')
        self.layout = dict(zip(names, struct.unpack('>34I', self.read(self.addr('ccLayout'), 136))))
        self.clock_size,self.clock_move,self.clock_frame,self.player_num,self.ground_velocity,self.physics=struct.unpack('>6I',self.read(self.addr('ccClockLayout'),24))
        # Stale queue is match-global state; isolate raw donor values in tests.
        self.services[0x800EA54C] = lambda: self.reg(UC_MIPS_REG_A1)
        self.services[self.labels['CharLab.restore_body_']] = lambda: 0
        # The dedicated visual suite executes these objects/scripts with
        # allocation/audio fixtures. Numeric suites do not run the renderer.
        self.services[self.addr('ccVisualTick')] = lambda: 0
        # DMA itself needs the OS scheduler/message queue. Supply ROM bytes,
        # while executing cache selection/decoding/retargeting as linked MIPS.
        dma = int(re.search(r'syDmaReadRom\s*=\s*(0x[0-9A-Fa-f]+)',
                            (LAB/'symbols/symbols_us.txt').read_text()).group(1), 16)
        bank_info = json.loads((ROOT/'build/char_creator/runtime/animations.json').read_text())
        bank_size = (ROOT/'build/char_creator/runtime/animations.bin').stat().st_size
        pair_info = json.loads((ROOT/'build/char_creator/runtime/paired-geometry.json').read_text())
        pair_size = (ROOT/'build/char_creator/runtime/paired-geometry.bin').stat().st_size
        def read_pose_bank():
            source, target, length = (self.reg(r) for r in (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2))
            pose = bank_info['rom_start'] <= source and source+length <= bank_info['rom_start']+bank_size
            paired = pair_info['rom_start'] <= source and source+length <= pair_info['rom_start']+pair_size
            collision = 0x5800000 <= source and source+length <= len(rom)
            assert pose or paired or collision, (hex(source),length)
            assert source % 16 == 0
            assert 0 < length <= (bank_info['cache_bytes'] if pose else 80 if collision else 8*pair_info['frame_bytes']) and length % 16 == 0
            self.write(target, rom[source:source+length])
        self.services[dma] = read_pose_bank

    def addr(self, name):
        return self.labels['CharLabRuntime.'+name]

    def read(self, address, length):
        # Source oracle only: actual MIPS code must DMA ROM tags through cache.
        if 0x5800000 <= address < 0x5900000:
            return self.rom[address:address+length]
        return bytes(self.uc.mem_read(address & 0x1FFFFFFF, length))

    def write(self, address, value):
        self.uc.mem_write(address & 0x1FFFFFFF, bytes(value))

    def u32(self, address, value=None):
        if value is None:
            return struct.unpack('>I', self.read(address, 4))[0]
        self.write(address, struct.pack('>I', value & 0xFFFFFFFF))

    def f32(self, address, value=None):
        if value is None:
            return struct.unpack('>f', self.read(address, 4))[0]
        self.write(address, struct.pack('>f', value))

    def reg(self, register):
        return self.uc.reg_read(register)

    def service(self, uc, address, size, _):
        fn = self.services.get(address)
        if fn:
            self.calls.append((address, tuple(self.reg(r) for r in (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3))))
            result = fn()
            self.uc.reg_write(UC_MIPS_REG_V0, result or 0)
            self.uc.reg_write(UC_MIPS_REG_PC, self.reg(UC_MIPS_REG_RA))

    def call(self, name, *args, end=None, namespace='CharLabRuntime'):
        for register, value in zip((UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3), args):
            self.uc.reg_write(register, value & 0xFFFFFFFF)
        self.uc.reg_write(UC_MIPS_REG_SP, self.STACK)
        self.uc.reg_write(UC_MIPS_REG_RA, self.STOP)
        address = self.labels[namespace+'.'+name]
        try:
            self.uc.emu_start(address, end or self.STOP, count=300000)
        except Exception as exc:
            raise RuntimeError(f'{name}: PC={self.reg(UC_MIPS_REG_PC):08X}: {exc}') from exc
        assert self.reg(UC_MIPS_REG_PC) == (end or self.STOP), f'{name}: did not return'
        return self.reg(UC_MIPS_REG_V0)

    def setup(self, body, donor, player=0):
        self.u32(self.labels['CharCreator.body_character_data']+player*4,0)
        self.u32(self.labels['CharCreator.body_character_id']+player*4,-1)
        self.u32(self.labels['CharCreator.active_special_donor']+player*4,-1)
        self.u32(self.labels['CharCreator.active_normal_donor']+player*4,-1)
        self.write(self.FP, bytes(self.layout['size']))
        self.write(self.GOBJ, bytes(0x100))
        self.u32(self.FP+8, body)
        self.write(self.FP+0xD, bytes([player]))
        self.u32(self.FP+0x44, 1)
        self.u32(self.FP+0x9C8, self.ATTR)
        self.f32(self.ATTR+self.layout['attr_size'], 2.0)
        self.u32(self.GOBJ+0x84, self.FP)
        self.u32(self.GOBJ+self.layout['obj'], self.JOINTS)
        for i in range(37):
            joint = self.JOINTS+i*0x100
            self.u32(self.FP+0x8E8+i*4, joint)
            # Special-context fixtures may install body FTData directly;
            # mirror the native fallback backup before exercising pose guards.
            self.u32(self.labels['CharCreator.special_joint_backups']+player*148+i*4,joint)
            for axis in range(3):
                self.f32(joint+self.layout['scale']+axis*4, 2.0)
        self.f32(self.JOINTS+self.layout['speed'], 1.0)
        for i in range(22):
            self.u32(self.ENTRIES+i*4, self.VALUES+i*4)
            self.u32(self.VALUES+i*4, donor if i != 1 else body)
        self.u32(self.VALUES, 1)
        self.u32(self.VALUES+15*4, 0)
        self.u32(self.VALUES+21*4, body)
        self.call('ccSync', self.FP, self.ENTRIES, self.layout['training'])

    def motion(self, body, index):
        if index < 29:
            return self.u32(self.addr('sFTCustomMotionIDs')+index*4)
        return self.u32(self.addr('sFTCustomBodyExtraMotionIDs')+(body*4+index-29)*4)

    def advance(self, native=-1.0):
        self.f32(self.GOBJ+self.layout['frame'], native)
        self.call('ccAdvance', self.GOBJ)
        return self.f32(self.GOBJ+self.layout['frame'])

    def events(self):
        self.call('ccEvents', self.GOBJ)

    def preset(self, body, donor, neutral=0):
        table = self.u32(self.labels['CharCreator.slot_tables'])
        for i in range(22):
            self.u32(self.u32(table+i*4), body if i == 1 else donor)
        self.u32(self.u32(table), 1)
        self.u32(self.u32(table+15*4), neutral)
        self.u32(self.u32(table+21*4), body)
        self.u32(self.labels['CharCreator.selected_builds'], 1)
        self.write(0x800A4AD0, bytes([self.layout['training']]))


def test_runtime(rom, labels):
    r = Runtime(rom, labels)
    r.call('ccReset')
    clocks, script = r.addr('sFTCustomMoveClocks'), r.addr('sCCMotionScripts')+4
    cases = 0
    for body in range(12):
        for donor in range(12):
            r.setup(body, donor)
            for index in range(33):
                motion = r.motion(donor if index >= 29 else body, index)
                if motion == 0xFFFFFFFF:
                    continue
                r.u32(r.FP+0x24, 100+index)
                r.u32(r.FP+0x28, motion)
                r.call('ccStart', r.FP, 0)
                assert r.u32(r.addr('gFTCustomMoveValidationFailures')) == 0, ('build', body, donor, index)
                if body == donor:
                    assert r.u32(clocks) == 0 and r.u32(script) == 0, (body, donor, index, hex(r.u32(clocks)), hex(r.u32(script)))
                    continue
                move = r.addr('sFTCustomMoves')+(donor*33+index)*16
                _, word_count, duration, flags = struct.unpack('>4I', r.read(move, 16))
                if duration == 0:
                    assert r.u32(clocks) == 0
                    continue  # Donor has no matching extra jab phase.
                assert r.u32(clocks) == r.FP and r.u32(clocks+r.clock_move) == move, (body, donor, index, motion, hex(r.u32(clocks+r.clock_move)), hex(move))
                assert r.u32(script) and word_count <= 512
                assert r.advance() == struct.unpack('>f', struct.pack('>f', 0.001))[0]
                assert r.f32(clocks+r.clock_frame) == 0
                # Test expiry without pretending that body animation duration
                # or speed determines donor recovery.
                r.f32(clocks+r.clock_frame, duration-1)
                assert r.advance(100) == (struct.unpack('>f', struct.pack('>f', 0.001))[0] if flags & 2 else -1)
                r.u32(r.FP+0x24, 500)
                assert r.advance(17) == 17
                cases += 1
            r.u32(r.FP+0x24, r.layout['catch_status'])
            r.u32(r.FP+0x28, r.layout['catch_motion'])
            r.call('ccStart', r.FP, 0)
            assert r.u32(script) != 0 if body != donor else r.u32(script) == 0
    print(f'PASS: {cases} foreign normal variants, all 144 grab pairings, same-body passthrough and interruption/expiry clocks execute on MIPS.')

    # Execute native ROM motion parsing and root placement for every donor
    # timeline, on an unlike body. Compare offsets to independent table lookup.
    trajectories = r.addr('sFTCustomCollisionTrajectories')
    frames = placements = 0
    for donor in range(12):
        body = (donor+1) % 12
        for index in range(33):
            motion = r.motion(donor if index >= 29 else body, index)
            if motion == 0xFFFFFFFF:
                continue
            r.setup(body, donor)
            r.u32(r.FP+0x24, 100+index)
            r.u32(r.FP+0x28, motion)
            r.call('ccStart', r.FP, 0)
            move = r.addr('sFTCustomMoves')+(donor*33+index)*16
            duration, flags = struct.unpack('>2I', r.read(move+8, 8))
            if not duration:
                continue
            ptr, first, count, loop, period = struct.unpack('>5I', r.read(trajectories+(donor*33+index)*20, 20))
            for frame in range(min(duration+1, 240) if not flags & 2 else 80):
                r.advance(-1)
                r.events()
                before = r.read(r.FP+0x294, 4*0xC4)
                r.call('ccCollision', r.FP)
                sampled = loop+(frame-loop) % period if period and frame >= loop else frame
                sample = ptr+(sampled-first)*52 if ptr and first <= sampled < first+count else 0
                mask = r.u32(sample+48) if sample else 0
                for hit in range(4):
                    base = r.FP+0x294+hit*0xC4
                    if mask & (1 << hit) and r.u32(base):
                        assert r.u32(base+8) == 0 and r.u32(base+0x14) == r.JOINTS
                        expected = struct.unpack('>3f', r.read(sample+hit*12, 12))
                        actual = struct.unpack('>3f', r.read(base+0x18, 12))
                        assert all(abs(a-e*0.5) < 0.002 for a, e in zip(actual, expected)), (donor, index, frame, hit)
                        placements += 1
                    # Root placement must not reset multihit records, radius,
                    # damage/knockback or the engine's swept history.
                    for off, length in ((0, 8), (0xC, 8), (0x24, 0x1C), (0x44, 0x80)):
                        old = before[hit*0xC4+off:hit*0xC4+off+length]
                        assert r.read(base+off, length) == old
                assert r.u32(r.addr('gFTCustomMoveValidationFailures')) == 0, ('events', donor, index, frame)
                frames += 1
    assert placements > 1000 and r.u32(r.addr('gFTCustomMoveValidationFailures')) == 0, (frames, placements, r.u32(r.addr('gFTCustomMoveValidationFailures')))
    assert r.u32(r.addr('gFTCustomAnimationValidationFailures')) == 0
    print(f'PASS: native Remix parser executes {frames} donor frames, {placements} root collision placements and bounded rapid-jab loops without validation failures.')

    # Native collision events must be suppressed and advance all four body
    # streams. The external stream must remain executable.
    r.setup(8, 7)
    r.u32(r.FP+0x24, 140)
    r.u32(r.FP+0x28, r.motion(8, 22))
    r.call('ccStart', r.FP, 0)
    for offset in (0x868, 0x888, 0x8A8, 0x8C8):
        p = r.FP+offset
        r.u32(p+4, r.VALUES)
        r.call('ccParse', r.GOBJ, r.FP, p, 3)
        assert r.u32(p+4) == r.VALUES+20
    # Real assignment lookup feeds ccPrepare; every port can select any preset.
    for player in range(4):
        for preset in range(4):
            r.setup(8, 7, player)
            r.u32(r.FP+0x24, 140)
            r.u32(r.FP+0x28, r.motion(8, 22))
            r.write(0x800A4AD0, bytes([r.layout['training']]))
            table = r.u32(labels['CharCreator.slot_tables']+preset*4)
            for i in range(21):
                r.u32(r.u32(table+i*4), 8 if i == 1 else 7)
            r.u32(r.u32(table), 1)
            r.u32(labels['CharCreator.selected_builds']+player*4, preset+1)
            r.call('ccPrepare', r.GOBJ, 0)
            assert r.u32(clocks+player*r.clock_size) == r.FP
    print('PASS: all four native body streams suppress foreign collisions; 16 player/preset assignments feed the correct independent runtime slot.')
    return r


def test_specials_and_return(r):
    # Execute the real neutral adapter; substitute only the engine's status
    # setup, projectile factory, audio and wait/fall transition services.
    def set_status():
        r.u32(r.FP+0x24, r.reg(UC_MIPS_REG_A1))
        r.u32(r.FP+0x28, 300)
        r.f32(r.GOBJ+r.layout['frame'], 0)

    r.services[0x800E6F24] = set_status
    weapon = r.labels['CharCreator.neutral_make_weapon_']
    r.services[weapon] = lambda: 0
    r.services[0x800269C0] = lambda: 0
    r.services[0x800DEE54] = lambda: 0
    for body in range(12):
        for air in (0, 1):
            r.setup(body, 7)
            r.preset(body, 7, 0)
            r.u32(r.FP+r.layout['ga'], air)
            assert r.call('ccNeutral', r.GOBJ) == 0
            r.preset(body, 7, 1)
            r.calls.clear()
            result = r.call('ccNeutral', r.GOBJ)
            if body == 1:
                assert result == 0  # Fox keeps native callbacks.
                continue
            assert result == 1
            expected_status = r.u32(r.addr('sFTCharBuilderNeutralStatuses')+(body*2+air)*4)
            assert r.u32(r.FP+0x24) == expected_status
            assert r.u32(r.FP+r.layout['accessory']) == r.addr('ftMainCharBuilderMakeLaser')
            # Suppression bridge executed independently of the SetStatus stub.
            for bank in range(4):
                r.u32(r.FP+0x868+bank*32+4, r.VALUES)
            r.u32(r.addr('sFTCharBuilderNeutralStartingOwner'), r.FP)
            r.call('ccStart', r.FP, 0)
            assert all(r.u32(r.FP+0x868+bank*32+4) == 0 for bank in range(4))
            r.u32(r.addr('sFTCharBuilderNeutralStartingOwner'), 0)
            r.call('ccNeutral', r.GOBJ)
            fired = []
            duration = 45 if air else 55
            for frame in range(1, duration+1):
                before = sum(address == weapon for address, _ in r.calls)
                r.advance(-1)
                r.events()
                r.call('ftMainCharBuilderMakeLaser', r.GOBJ)
                if sum(address == weapon for address, _ in r.calls) > before:
                    fired.append(frame)
                assert r.f32(r.GOBJ+r.layout['frame']) > 0 if frame < duration else r.f32(r.GOBJ+r.layout['frame']) == -1
            assert fired == [15 if air else 25], (body, air, fired)
            r.call('ftMainCharBuilderNeutralProcUpdate', r.GOBJ)
            assert any(address == 0x800DEE54 for address, _ in r.calls)
    print('PASS: native-body/Fox neutral choice and every foreign original body execute finite 55/45-frame neutral recovery and one laser at frame 25/15; body event suppression is complete.')

    native_desc, command = 0x80213000, 0x80214000
    native_words = (52, 12, 45, 70, 0, 80, 0, 55, 6, 45, 70, 0, 80, 0)
    r.write(native_desc, struct.pack('>14I', *native_words))
    for body in range(12):
        for donor in range(12):
            for kind in range(3):
                r.setup(body, donor)
                r.u32(r.FP+0x24, r.layout['catch_status'] if kind == 0 else r.layout['throw_status'])
                r.u32(r.FP+r.layout['attack_id'], r.layout['throw_b'] if kind == 2 else r.layout['throw_f'])
                r.write(command, struct.pack('>2I', 12 << 26, native_desc))
                ms = r.FP+0x868
                r.u32(ms+4, command)
                r.call('ccParse', r.GOBJ, r.FP, ms, 12)
                desc = r.u32(r.FP+r.layout['throw_desc'])
                actual = struct.unpack('>14I', r.read(desc, 56))
                expected = struct.unpack('>12I', r.read(r.addr('sFTCustomThrowProperties')+(donor*3+kind)*48, 48))
                assert actual == native_words if body == donor else actual == (52, *expected[:6], 55, *expected[6:])
    # DK foreign forward throws select release, and preserve Remix's mapping
    # for a victim outside the original roster instead of indexing past it.
    victim_gobj, victim_fp, thrown = 0x80215000, 0x80216000, 0x80218000
    r.services[0x800E0830] = lambda: 0
    r.services[0x8014AC0C] = lambda: 0
    r.services[0x8014ACB4] = lambda: 0
    r.services[0x80101E80] = lambda: 0
    for body, donor in ((2, 7), (2, 2), (0, 7)):
        r.setup(body, donor)
        r.preset(body, donor)
        r.u32(r.FP+r.layout['catch'], victim_gobj)
        r.u32(victim_gobj+0x84, victim_fp)
        r.u32(victim_fp+8, 18)
        r.u32(r.ATTR+r.layout['thrown_table'], thrown)
        mapped = r.u32(r.labels['Character.f_thrown_action.table']+18*4)
        r.write(thrown+mapped*16, struct.pack('>4I', 0xFFFFFFFF, r.layout['shouldered'], 0xFFFFFFFF, 187))
        r.calls.clear()
        assert r.call('ccThrow', r.GOBJ, 1) == 1
        assert r.u32(r.FP+0x24) == r.layout['throw_status']
        queued = [args[1] for addr, args in r.calls if addr == 0x8014ACB4]
        expected_queue = r.layout['shouldered'] if body==donor==2 else r.layout['thrown_common']
        assert queued == [expected_queue], queued
    print('PASS: 432 body/donor grab and throw numeric selections; paired donor release/cargo selection uses Remix extended-victim mapping.')

    # Execute the native hooks with rendering services stubbed, including
    # page-two selection so the returned editor shows TEST rather than row 12.
    r.services[r.labels['Menu.redraw_']] = lambda: 0
    r.services[r.labels['Render.toggle_group_display_']] = lambda: 0
    r.services[r.labels['CharLab.training_css_back_._original']] = lambda: 0
    for preset in range(1, 5):
        r.u32(r.labels['CharLab.training_slot'], preset)
        r.call('training_exit_', end=0x801906BC, namespace='CharLab')
        assert r.reg(UC_MIPS_REG_T4) == 0x39
        assert r.u32(r.labels['CharLab.return_slot']) == preset
        r.u32(r.labels['Toggles.info']+0x18, r.labels['Toggles.head_super_menu'])
        r.call('resume_editor_', namespace='CharLab')
        head = r.labels[f'Toggles.head_char_creator_slot_{preset}']
        first = head
        for _ in range(24):
            first = r.u32(first+0x1C)
        assert r.u32(r.labels['Toggles.info']) == head
        assert r.u32(r.labels['Toggles.info']+0x18) == first
        assert r.u32(r.labels['Toggles.info']+0xC) == 24
        assert r.read(r.labels['Toggles.menu_index'], 1) == bytes([preset+8])
        assert r.u32(r.labels['CharLab.return_slot']) == 0
        r.u32(r.labels['CharLab.training_slot'], preset)
        r.call('training_css_back_', namespace='CharLab')
        assert r.read(0x800A4AD0, 1) == b'9'
        assert r.u32(r.labels['CharLab.return_slot']) == preset
    r.u32(r.labels['CharLab.training_slot'], 0)
    r.call('training_exit_', end=0x801906BC, namespace='CharLab')
    assert r.reg(UC_MIPS_REG_T4) == 0x12
    print('PASS: Training exit and CSS Back return all four tested presets to the correct editor page; ordinary Training retains its CSS destination.')

    # Execute the actual launch handler; isolate only SRAM I/O and the
    # native costume lookup, leaving recipe selection and scene setup live.
    scene = 0x800A4AD0
    offsets = struct.unpack('>5I', r.read(r.addr('ccTrainingSetupLayout'),20))
    r.services[r.labels['Toggles.save_']] = lambda: 0
    r.services[0x800EC0EC] = lambda: r.reg(UC_MIPS_REG_A1)
    for preset in range(1,5):
        entry = r.labels[f'Toggles.cc_slot_{preset}_test']
        table = r.u32(r.labels['CharCreator.slot_tables']+(preset-1)*4)
        body_value = r.u32(table+4)
        old_body = r.u32(body_value)
        for body in range(12):
            r.u32(body_value,body)
            for offset in offsets:r.write(scene+offset,b'\xFF')
            r.write(scene,b'\x39')
            r.uc.reg_write(UC_MIPS_REG_V0,entry)
            r.call('test_in_training_',namespace='CharCreator')
            assert r.read(scene,2)==b'\x12\x39'
            assert tuple(r.read(scene+offset,1)[0] for offset in offsets)==(0,body,0,0,int(body==0))
            assert r.u32(r.labels['CharCreator.selected_builds'])==preset
            assert r.u32(r.labels['CharLab.training_slot'])==preset
        r.u32(body_value,old_body)
    assert r.read(r.labels['Toggles.entry_char_creator']+0x28,14)==b'Character Lab\0'
    del r.services[r.labels['Toggles.save_']]
    del r.services[0x800EC0EC]
    print('PASS: 48 actual editor launch handlers replace stale Training selections, select the saved body/P1 and native dummy costumes; Settings label is Character Lab. SRAM/costume services are isolated.')


def test_borrowed_specials(r):
    """Execute pose selection, donor clocks and native Quick Attack callbacks.

    Rendering/status setup and the directional input predicate are isolated;
    the native dash/end callbacks, event parser and owned hooks are real MIPS.
    """
    special = struct.unpack('>8I', r.read(r.addr('ccSpecialLayout'), 32))
    variables, air_velocity, ground_velocity, joints, hi, end, air_hi, air_end = special
    body_data, body_params = 0x80220000, 0x80221000
    donor_data, donor_params = 0x80224000, 0x80225000
    donor_actions = 0x80228000
    table = r.labels['Character.ACTION_ARRAY_TABLE']
    saved_actions = r.u32(table+9*4)
    r.u32(table+9*4, donor_actions)
    r.u32(body_data+0x64, body_params)
    r.u32(donor_data+0x64, donor_params)
    for action, motion in ((hi, 207), (end, 208), (air_hi, 209), (air_end, 210)):
        r.u32(donor_actions+(action-0xDC)*20, motion << 22)
        r.write(donor_params+motion*12, struct.pack('>3I', 0x1234, 0x5678, 0x40000000))
    idle_index = r.u32(0x80128DD8+0xA*20) >> 22
    fall_index = r.u32(0x80128DD8+0x1A*20) >> 22
    r.write(body_params+idle_index*12, struct.pack('>3I', 0x111, 0, 0x222))
    r.write(body_params+fall_index*12, struct.pack('>3I', 0x333, 0, 0x444))
    for body in range(12):
        for player in range(4):
            r.setup(body, 9, player)
            r.u32(r.FP+8, 9)  # Native donor identity during borrowed chain.
            r.u32(r.FP+0x9C4, donor_data)
            r.u32(r.labels['CharCreator.body_character_data']+player*4, body_data)
            r.u32(r.labels['CharCreator.body_character_id']+player*4,body)
            r.u32(r.labels['CharCreator.active_special_donor']+player*4, 9)
            for air, action, motion in ((0, hi, 207), (1, air_hi, 209)):
                r.u32(r.FP+0x24, action)
                r.u32(r.FP+r.layout['ga'], air)
                r.uc.reg_write(UC_MIPS_REG_S1, r.FP)
                r.uc.reg_write(UC_MIPS_REG_T2, motion*12)
                r.call('parameter_record_hook_', donor_params, namespace='CharCreator', end=0x800E7560)
                record = r.reg(UC_MIPS_REG_T3)
                expected = (0x333, 0x5678, 0x444) if air else (0x111, 0x5678, 0x222)
                assert struct.unpack('>3I', r.read(record, 12)) == expected
                assert r.reg(UC_MIPS_REG_V1) == body_data
                assert r.u32(r.FP+0x28) == motion
            # Donor model transforms must not touch scale, root position or
            # velocity on any borrowed body/port.
            r.f32(r.JOINTS+r.layout['translate'], 1234.0)
            r.f32(r.FP+air_velocity, 45.0)
            before = r.read(r.JOINTS, 37*0x100)
            for name in ('pikachu_pitch_scale_', 'fox_pitch_', 'ness_pitch_'):
                r.call(name, r.GOBJ, namespace='CharLab')
            assert r.read(r.JOINTS, 37*0x100) == before
            assert r.f32(r.FP+air_velocity) == 45.0
            # A zero-speed Quick Attack dash must hold its clock until the
            # native counter changes state, despite the idle pose looping.
            r.f32(r.JOINTS+r.layout['speed'], 0)
            r.call('ccPrepare', r.GOBJ, 0)
            for _ in range(12):
                assert r.advance(-1) > 0
            # Each end phase uses Pikachu's 46 frames, not the pose duration.
            r.u32(r.FP+0x24, air_end)
            r.u32(r.FP+0x28, 210)
            r.f32(r.JOINTS+r.layout['speed'], 1)
            r.call('ccPrepare', r.GOBJ, 0)
            for tick in range(47):
                assert (r.advance(-1) < 0) == (tick == 46)
            assert r.f32(r.JOINTS+r.layout['translate']) == 1234.0
            # Shared interruption immediately invalidates the special clock.
            r.u32(r.FP+0x24, 0xA)
            assert r.advance(19.0) == 19.0
            r.u32(r.labels['CharCreator.body_character_data']+player*4, 0)
            r.u32(r.labels['CharCreator.body_character_id']+player*4,-1)
            r.u32(r.labels['CharCreator.active_special_donor']+player*4, -1)
            for name, address in (('pikachu_pitch_scale_', 0x80152AA0),
                                  ('fox_pitch_', 0x8015C054), ('ness_pitch_', 0x80154758)):
                r.call(name, r.GOBJ, namespace='CharLab', end=address+8)
                assert r.reg(UC_MIPS_REG_SP) == r.STACK-0x20
    r.u32(table+9*4, saved_actions)
    # Expanded donors keep their finite legacy pose until their phase clocks
    # are supported. A looping idle must not trap animation-ended callbacks.
    saved_expanded = r.u32(table+12*4)
    r.u32(table+12*4, donor_actions)
    taunt_index = r.u32(0x80128DD8+0xBD*20) >> 22
    r.write(body_params+taunt_index*12, struct.pack('>3I', 0x555, 0, 0x666))
    r.setup(0, 9)
    r.u32(r.FP+0x9C4, donor_data)
    r.u32(r.FP+0x24, hi)
    r.u32(r.labels['CharCreator.body_character_data'], body_data)
    r.u32(r.labels['CharCreator.active_special_donor'], 12)
    r.uc.reg_write(UC_MIPS_REG_S1, r.FP)
    r.uc.reg_write(UC_MIPS_REG_T2, 207*12)
    r.call('parameter_record_hook_', donor_params, namespace='CharCreator', end=0x800E7560)
    assert struct.unpack('>3I', r.read(r.reg(UC_MIPS_REG_T3), 12)) == (0x555, 0x5678, 0x666)
    r.u32(table+12*4, saved_expanded)
    # Test all generated donor phases at accelerated speed, including held
    # loops and forwarded ground/air continuation frames. Native pose ending
    # early (-1) must not end the donor's recovery.
    phases = 0
    for donor in range(12):
        r.setup((donor+1) % 12, donor)
        r.u32(r.FP+8, donor)
        r.u32(r.labels['CharCreator.body_character_data'], body_data)
        r.u32(r.labels['CharCreator.active_special_donor'], donor)
        for motion in range(195, 276):
            timing = r.u32(r.addr('sCCSpecialTimings')+(donor*276+motion)*4)
            duration = timing & 0x7FFFFFFF
            if not duration:
                continue
            r.u32(r.FP+0x24, 0xDC)
            r.u32(r.FP+0x28, motion)
            r.f32(r.JOINTS+r.layout['speed'], 2)
            begin = duration-2
            r.call('ccPrepare', r.GOBJ, struct.unpack('>I', struct.pack('>f', begin))[0])
            assert abs(r.advance(-1)-max(0.001, begin)) < 0.001
            assert (r.advance(-1) > 0) == bool(timing & 0x80000000)
            phases += 1
    r.call('ccReset')
    assert r.advance(13) == 13
    # Exercise the actual Quick Attack end update with the second-dash input
    # predicate accepted, then ensure one subsequent dash and finite recovery.
    r.setup(0, 9)
    r.u32(r.FP+8, 9)
    r.u32(r.labels['CharCreator.body_character_data'], body_data)
    r.u32(r.labels['CharCreator.active_special_donor'], 9)
    r.services[0x801531AC] = lambda: 1  # Direction change input/collision gate.
    r.services[0x80152FEC] = lambda: 0  # Status setup/rendering for second dash.
    r.labels['Test.pika_end_update'] = 0x80153340
    # Run the production native parser for the donor end script's 9-frame
    # wait and flag1 event before invoking the actual second-dash update.
    from auditNormalMoves import enum_values
    opcodes = enum_values((LAB/'src/ft/ftdef.h').read_text(), 'FTMotionEvent')
    script = r.FP+0x868
    words = 0x80229000
    r.write(words, struct.pack('>3I', opcodes['nFTMotionEventSyncWait'] << 26 | 9,
                              opcodes['nFTMotionEventSetFlag1'] << 26 | 1, 0))
    r.u32(script+4, words)
    r.f32(script, 1)
    r.u32(r.FP+r.layout['flags']+4, 0)
    for frame in range(10):
        r.f32(r.GOBJ+r.layout['frame'], frame)
        r.f32(script, r.f32(script)-1)
        while r.u32(script+4) and r.f32(script) <= 0:
            opcode = r.u32(r.u32(script+4)) >> 26
            r.call('ccParse', r.GOBJ, r.FP, script, opcode)
        assert r.u32(r.FP+r.layout['flags']+4) == (1 if frame == 9 else 0)
    r.u32(r.FP+variables+4, 0)
    r.call('pika_end_update', r.GOBJ, namespace='Test')
    assert r.u32(r.FP+r.layout['flags']+4) == 0
    assert r.u32(r.FP+variables+4) == 1
    assert sum(address == 0x80152FEC for address, _ in r.calls) == 1
    del r.services[0x801531AC]
    del r.services[0x80152FEC]
    # Native endpoint backs up and attenuates velocity, not world position.
    r.labels['Test.pika_end_velocity'] = 0x801535C4
    r.f32(r.FP+air_velocity, 90)
    r.f32(r.FP+air_velocity+4, 60)
    r.f32(r.JOINTS+r.layout['translate'], 1800)
    r.call('pika_end_velocity', r.GOBJ, namespace='Test')
    assert r.f32(r.FP+variables+24) == 90
    assert r.f32(r.FP+variables+28) == 60
    assert r.f32(r.FP+air_velocity) == r.f32(r.FP+air_velocity+4) == 0
    assert r.f32(r.JOINTS+r.layout['translate']) == 1800
    r.u32(r.labels['CharCreator.body_character_data'], 0)
    r.u32(r.labels['CharCreator.active_special_donor'], -1)
    print(f'PASS: borrowed special Idle/Fall records, frozen dash/46-frame end clocks and transform guards on 12 bodies x 4 ports; {phases} donor phase speed/loop/continuation checks; native second-dash event/update and endpoint position preservation. Rendering/status setup and direction predicate are stubbed.')


def test_movement_and_special_paths(r):
    """Execute source movement/collision hooks, including real native math.

    Ground transfer and animation-independent donor callbacks are exercised;
    this does not assert contact, projectile sockets or paired mechanics.
    """
    from math import sin,cos
    size,frame_off,path_size,path_count,trajectory_off,travel_off,normal_size,count_off,floor_off,traction_off=struct.unpack('>10I',r.read(r.addr('ccMovementLayout'),40))
    clocks=r.addr('sCCSpecialClocks');common=r.addr('sFTCustomMoveClocks')
    paths=r.addr('sFTCharBuilderSpecialPaths');out=0x8022A000
    callback=0x803FDF00;donor_data=0x80230000;main_pointer=0x80231000;donor_attr=0x80232100
    physics_seen=[]
    r.services[callback]=lambda:physics_seen.append(r.u32(r.FP+0x9C8))
    r.services[0x800E87A0]=lambda:0  # Hit-status color rendering only.
    def near(actual,expected,context):
        assert all(abs(a-b)<0.004 for a,b in zip(actual,expected)),(context,actual,expected)
    normal_checks=0
    for body in range(12):
        for donor,index in ((1,2),(8,14)):  # Fox dash / Kirby straight F-smash.
            if body==donor:continue
            r.setup(body,donor)
            r.u32(r.FP+0x24,100+index);r.u32(r.FP+0x28,r.motion(body,index))
            r.call('ccStart',r.FP,0)
            record=r.addr('sFTCustomNormalMechanics')+(donor*33+index)*normal_size
            travel,count,flags=r.u32(record),r.u32(record+count_off),r.u32(record+count_off+4)
            assert travel and flags&0x40000000,(donor,index)
            for facing in (-1,1):
                r.u32(r.FP+0x44,facing);r.f32(r.JOINTS+r.layout['rotate']+4,facing*1.57)
                r.f32(r.FP+floor_off,0);r.f32(r.FP+floor_off+4,1)
                for frame in range(count):
                    r.f32(common+r.clock_frame,frame)
                    expected=struct.unpack('>3f',r.read(travel+frame*12,12))
                    r.call('ccGroundPhysics',r.GOBJ)
                    near((r.f32(r.FP+r.ground_velocity),r.f32(r.FP+r.ground_velocity+4)),(expected[0],expected[2]*facing),(body,donor,index,frame,facing))
                    r.call('ccAirTravel',r.FP,out,out+4,out+8)
                    near(struct.unpack('>3f',r.read(out,12)),(expected[0]*facing,expected[1],expected[2]*facing),('air',body,donor,index,frame))
                    normal_checks+=1
    placements=travel_checks=parser_frames=0
    for index in range(path_count):
        path=paths+index*path_size;donor,motion=struct.unpack('>2I',r.read(path,8))
        for body in range(12):
            if body==donor:continue
            r.setup(body,donor);r.preset(body,donor)
            r.u32(r.labels['CharCreator.body_character_data'],0x80220000)
            r.u32(r.labels['CharCreator.body_character_id'],body)
            r.u32(r.labels['CharCreator.active_special_donor'],donor)
            r.u32(r.FP+8,donor);r.u32(r.FP+0x24,0xDC);r.u32(r.FP+0x28,motion)
            r.u32(0x80116E10+donor*4,donor_data)
            r.u32(donor_data+0x28,main_pointer);r.u32(main_pointer,donor_attr-0x100);r.u32(donor_data+0x60,0x100)
            r.u32(r.FP+r.physics,callback)
            r.call('ccPrepare',r.GOBJ,0)
            assert r.u32(common+r.clock_move)==path+8,('slot lost during donor identity',body,donor,motion)
            r.labels['Test.phase_physics']=r.u32(r.FP+r.physics)
            r.call('phase_physics',r.GOBJ,namespace='Test')
            assert physics_seen[-1]==donor_attr and r.u32(r.FP+0x9C8)==r.ATTR,('donor attributes/restoration',body,donor,motion)
            ptr,first,count,loop,period=struct.unpack('>5I',r.read(path+trajectory_off,20))
            travel=r.u32(path+travel_off)
            samples=range(count) if body==(donor+1)%12 else sorted({0,count//2,count-1})
            for frame in samples:
                r.f32(clocks+frame_off,frame);r.f32(common+r.clock_frame,frame)
                r.call('ccCollision',r.FP)  # Real engine fields, poisoned body transforms.
                sample=ptr+(frame-first)*52 if first<=frame<first+count else 0
                if sample:
                    mask=r.u32(sample+48)
                    if body==(donor+1)%12:
                        r.events()
                        actual_mask=sum(1<<hit for hit in range(4) if r.u32(r.FP+0x294+hit*0xC4))
                        assert actual_mask==mask,('source special event window',donor,motion,frame,actual_mask,mask)
                        parser_frames+=1
                    for hit in range(4):
                        base=r.FP+0x294+hit*0xC4
                        if mask&(1<<hit):
                            r.u32(base,1)
                            r.u32(base+0x3C,0xFCA01234)  # Includes scaled-position flag.
                    before=r.read(r.FP+0x294,4*0xC4)
                    r.call('ccCollision',r.FP)
                    for hit in range(4):
                        base=r.FP+0x294+hit*0xC4
                        if mask&(1<<hit):
                            near(struct.unpack('>3f',r.read(base+0x18,12)),tuple(x/2 for x in struct.unpack('>3f',r.read(sample+hit*12,12))),('special',body,donor,motion,frame,hit))
                            assert r.u32(base+0x14)==r.JOINTS
                            assert r.u32(base+0x3C)==0xFC801234,('double body scaling',body,donor,motion,frame,hit)
                            placements+=1
                        for off,length in ((0,8),(0xC,8),(0x24,0x18),(0x40,0x84)):
                            assert r.read(base+off,length)==before[hit*0xC4+off:hit*0xC4+off+length]
                if travel:
                    dx,dy,dz,angle=struct.unpack('>4f',r.read(travel+frame*16,16))
                    for facing in (-1,1):
                        r.u32(r.FP+0x44,facing)
                        r.f32(r.JOINTS+0x100+r.layout['rotate']+8,0)
                        r.call('ccAirTravel',r.FP,out,out+4,out+8)
                        near(struct.unpack('>3f',r.read(out,12)),(dx*facing*cos(angle)-dy*sin(angle),dx*facing*sin(angle)+dy*cos(angle),dz*facing),('special air',body,donor,motion,frame))
                        travel_checks+=1
            # Reusing the allocation for a respawn must retire the phase.
            r.u32(r.FP+r.player_num,r.u32(r.FP+r.player_num)+1)
            assert r.advance(17)==17,('stale special clock',body,donor,motion)
            before=len(physics_seen);r.call('phase_physics',r.GOBJ,namespace='Test')
            assert len(physics_seen)==before,('stale donor callback',body,donor,motion)
    del r.services[callback]
    del r.services[0x800E87A0]
    r.call('ccReset')
    r.setup(0,1)
    # No custom move: execute native air TransN fallback through the trampoline.
    r.u32(r.FP+0x24,10);r.u32(r.FP+0x28,10)
    r.f32(r.JOINTS+0x100+r.layout['translate']+8,8)
    r.f32(r.JOINTS+0x100+r.layout['translate']+4,3)
    r.f32(r.JOINTS+0x100+r.layout['translate'],2)
    r.f32(r.JOINTS+0x100+r.layout['rotate']+8,0)
    r.call('ccAirTravel',r.FP,out,out+4,out+8)
    near(struct.unpack('>3f',r.read(out,12)),(16,6,-4),'native air passthrough')
    print(f'PASS: {normal_checks} Fox/Kirby normal momentum samples; {path_count} special paths on eleven foreign bodies, {parser_frames} native special parser frames, {placements} collision placements/{travel_checks} air travel samples, donor attributes, generation cleanup and native air passthrough. Native math executes; contact and animation rendering remain untested.')


def main():
    rom = (ROOT / 'ssb64asm_extra.z64').read_bytes()
    labels = {name: int(address, 16) for address, name in re.findall(r'^([0-9a-fA-F]{8}) (.+)$', (ROOT/'logfile.log').read_text(), re.M)}
    assert rom[:4] == b'\x80\x37\x12\x40'
    assert calculate_crcs(rom) == struct.unpack_from('>II', rom, 0x10)
    hooks = {0xCB9E4: 'CharLab.air_down_b_available_',
             0x631B0: 'CharLab.prepare_', 0x5C00C: 'CharLab.anim_update_',
             0x5A8F0: 'CharLabRuntime.ccParse', 0x5C040: 'CharLab.events_all_',
             0x5C068: 'CharLab.events_forward_', 0x5DC4C: 'CharLab.collisions_',
             0xC4C28: 'CharLab.throw_', 0x116ED4: 'CharLab.training_exit_',
             0x144DAC: 'CharLab.training_css_back_'}
    overlay = re.search(r'- name: ovl28\s+type: code\s+start: (0x[0-9A-Fa-f]+)\s+vram: (0x[0-9A-Fa-f]+)',
                        (LAB/'smashbrothers.us.yaml').read_text(encoding='utf-8'))
    assert overlay is not None
    training_back = int(overlay[1],16) + 0x801357CC - int(overlay[2],16)
    assert hooks[training_back] == 'CharLab.training_css_back_', 'Back hook must target Training overlay'
    base_rom = (ROOT/'smashremix/roms/ssb.rom').read_bytes()
    assert rom[0x13D9CC:0x13D9D4] == base_rom[0x13D9CC:0x13D9D4], 'Ordinary 1P CSS was overwritten by Training Back'
    hooks.update({0xCD4E0: 'CharLab.pikachu_pitch_scale_', 0xD6A94: 'CharLab.fox_pitch_',
                  0xCF198: 'CharLab.ness_pitch_'})
    import json
    hooks[0x62724]='CharLab.status_changing_'
    hooks[0x3800000+labels['CharacterSelect.load_additional_characters_']-0x80400000]='CharLab.editor_css_models_'
    hooks[0x5570]='CharLab.heap_reset_'
    for name,delta,target in (
        ('CharacterSelect.initialize_dynamic_css_._loop',0x1C,'CharLab.css_heap_init_'),
        ('CharacterSelect.dynamically_load_character_._use_alt_heap',0,'CharLab.css_heap_alloc_')):
        hooks[0x3800000+labels[name]+delta-0x80400000]=target
    hooks[0x3800000+labels['CharacterSelect.increase_heap_._return']-0x80400000]='CharLab.heap_cursor_'
    for name,delta in (('CharacterSelect.load_additional_characters_',0x24),('Render.setup_._mode_select',0x34)):
        assert struct.unpack_from('>I',rom,0x3800000+labels[name]+delta-0x80400000)[0]==0, 'UI rewinds native heap cursor'
    for entry in json.loads((ROOT/'build/char_creator/runtime/special-hooks.json').read_text()):
        hooks[entry['offset']]=entry['hook']
    for entry in json.loads((ROOT/'build/char_creator/runtime/paired-hooks.json').read_text()):
        hooks[entry['offset']]=entry['hook']
    for entry in json.loads((ROOT/'build/char_creator/runtime/normal-hooks.json').read_text()):
        hooks[entry['offset']]=entry['hook']
    for offset, label in hooks.items():
        word = struct.unpack_from('>I', rom, offset)[0]
        assert word >> 26 in (2, 3) and word & 0x3FFFFFF == (labels[label] >> 2) & 0x3FFFFFF, label
    assert rom[0x42B3A:0x42B3E] == b'\x00\x7F\x0C\x90', 'Unlock patch missing'
    toggle = labels['Toggles.entry_improved_combo_meter'] - 0x80400000 + 0x3800000
    assert struct.unpack_from('>I', rom, toggle+4)[0] == 1
    linked_object(rom, labels)
    runtime = test_runtime(rom, labels)
    test_specials_and_return(runtime)
    test_borrowed_specials(runtime)
    test_movement_and_special_paths(runtime)
    from test_charlab_special_adapters import test_adapters
    test_adapters(runtime)
    from test_charlab_normals import test_normals
    test_normals(runtime)
    from test_charlab_neutrals import test_neutrals
    test_neutrals(runtime)
    from test_charlab_neutral_weapons import test_weapons
    test_weapons(runtime)
    from test_charlab_visuals import test_visuals
    test_visuals(Runtime(rom, labels))
    from test_charlab_inhale import test_inhale
    test_inhale(Runtime(rom, labels))
    from test_charlab_pairs import test_pairs
    test_pairs(Runtime(rom, labels), rom)
    from test_charlab_edge_fixes import test_edge_fixes
    test_edge_fixes(Runtime(rom, labels))
    from test_charlab_randomizer import test_randomizer
    test_randomizer(Runtime(rom, labels))
    from test_charlab_animations import test_animations
    test_animations(runtime, rom)
    print(f'ROM: {len(rom):,} bytes; SHA-256 {hashlib.sha256(rom).hexdigest()}')


if __name__ == '__main__':
    main()
