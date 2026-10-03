"""Check the linked Remix port and execute its production MIPS code with Unicorn.

Engine motion parsing runs from the built ROM. Staling, sound, rendering and
status setup services are stubbed where indicated; this is not an emulator
playtest or verification of contact detection, rendering or every special.
"""
from pathlib import Path
import hashlib
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
        assert rom[offset:offset+len(payload)] == payload, 'Linked section differs: '+str(i)
    # Compare donor event words, all trajectories and animation poses with the
    # already source-checked shared host build, excluding relocated pointers.
    host, hs, syms = read_elf(LAB / 'build/testCustomMove', '<')
    verify_sources(host, hs, syms)
    checked = 0
    for name, (address, length, index) in syms.items():
        if name not in symbols or not length or hs[index][1] == 8:
            continue
        if not (name.startswith('sFTCustom') or name.startswith('sFTCharBuilderLaser')):
            continue
        actual, actual_length, actual_index = symbols[name]
        if actual_length != length or length % 4:
            continue
        # Records containing pointers are covered by the relocation check.
        if name in ('sFTCustomMoves', 'sFTCustomGrabMoves', 'sFTCustomAnimationPilots',
                    'sFTCustomCollisionTrajectories', 'sFTCharBuilderLaserMoves'):
            continue
        start = hs[index][4] + address - hs[index][3]
        fmt = 'B' if name in ('sFTCustomJointMaps', 'sFTCustomGrabJointMap') else 'H' if name == 'sFTCustomGrabTimings' else 'I'
        count_values = length // struct.calcsize(fmt)
        expected = struct.pack('>'+str(count_values)+fmt, *struct.unpack_from('<'+str(count_values)+fmt, host, start))
        start = sections[actual_index][4] + actual - sections[actual_index][3]
        assert obj[start:start+length] == expected, 'Shared data differs: '+name
        checked += 1
    assert checked >= 650, checked
    assert labels['custom_heap'] < 0x80780000, 'Expansion RAM heap headroom too small'
    print(f'PASS: {count} relocations, all allocated runtime bytes and {checked} shared donor tables/poses match; expansion heap at {labels["custom_heap"]:08X}.')


class Runtime:
    FP, GOBJ, ATTR, JOINTS, ENTRIES, VALUES = 0x80200000, 0x80203000, 0x80204000, 0x80206000, 0x80210000, 0x80211000
    STACK, STOP = 0x803FF000, 0x803FE000

    def __init__(self, rom, labels):
        self.labels = labels
        self.uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_BIG_ENDIAN)
        # KSEG0 is translated to physical RAM by Unicorn's MIPS CPU.
        self.uc.mem_map(0, 0x800000)
        self.uc.mem_map(0x80000000, 0x800000)
        self.uc.mem_write(0x80400000, rom[0x3800000:0x3800000+0x400000])
        self.uc.mem_write(0x800D6490, rom[0x51C90:0xAC540])
        # Mirror initial ROM data in the physical alias as well.
        self.uc.mem_write(0x400000, rom[0x3800000:0x3800000+0x400000])
        self.uc.mem_write(0xD6490, rom[0x51C90:0xAC540])
        self.uc.reg_write(UC_MIPS_REG_CP0_STATUS, 0x20000000)
        self.services = {}
        self.calls = []
        self.uc.hook_add(UC_HOOK_CODE, self.service)
        names = ('size', 'pkind', 'ga', 'flags', 'attack_id', 'throw_desc', 'update', 'interrupt',
                 'accessory', 'attr_size', 'obj', 'frame', 'translate', 'rotate', 'scale', 'speed',
                 'dobj_size', 'catch', 'capture', 'catch_status', 'catch_motion', 'throw_status',
                 'throw_f', 'throw_b', 'dk_throw_ff', 'shouldered', 'thrown_common', 'vs', 'training', 'air',
                 'thrown_table', 'stick', 'tap', 'b_mask')
        self.layout = dict(zip(names, struct.unpack('>34I', self.read(self.addr('ccLayout'), 136))))
        # Stale queue is match-global state; isolate raw donor values in tests.
        self.services[0x800EA54C] = lambda: self.reg(UC_MIPS_REG_A1)
        self.services[self.labels['CharLab.restore_body_']] = lambda: 0

    def addr(self, name):
        return self.labels['CharLabRuntime.'+name]

    def read(self, address, length):
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
            for axis in range(3):
                self.f32(joint+self.layout['scale']+axis*4, 2.0)
        self.f32(self.JOINTS+self.layout['speed'], 1.0)
        for i in range(21):
            self.u32(self.ENTRIES+i*4, self.VALUES+i*4)
            self.u32(self.VALUES+i*4, donor if i != 1 else body)
        self.u32(self.VALUES, 1)
        self.u32(self.VALUES+15*4, 0)
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
        for i in range(21):
            self.u32(self.u32(table+i*4), body if i == 1 else donor)
        self.u32(self.u32(table), 1)
        self.u32(self.u32(table+15*4), neutral)
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
                motion = r.motion(body, index)
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
                assert r.u32(clocks) == r.FP and r.u32(clocks+4) == move, (body, donor, index, motion, hex(r.u32(clocks+4)), hex(move))
                assert r.u32(script) and word_count <= 512
                assert r.advance() == (-1.0 if flags & 2 else struct.unpack('>f', struct.pack('>f', 0.001))[0])
                assert r.f32(clocks+20) == 0
                # Test expiry without pretending that body animation duration
                # or speed determines donor recovery.
                r.f32(clocks+20, duration-1)
                assert r.advance(100) == (100 if flags & 2 else -1)
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
            motion = r.motion(body, index)
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
            assert r.u32(clocks+player*32) == r.FP
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
    print('PASS: Body Move/Fox Laser choice and every foreign original body execute finite 55/45-frame neutral recovery and one laser at frame 25/15; body event suppression is complete.')

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
    r.services[0x8014AB64] = lambda: 0
    r.services[0x8014AFD0] = lambda: 0
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
        assert r.u32(r.FP+0x24) == (r.layout['dk_throw_ff'] if body == 2 and donor != 2 else r.layout['throw_status'])
        queued = [args[1] for addr, args in r.calls if addr == 0x8014AFD0]
        assert queued == [r.layout['thrown_common'] if body == 2 and donor != 2 else r.layout['shouldered']], queued
    print('PASS: 432 body/donor grab and throw numeric selections preserve victim statuses; DK release/cargo selection uses Remix extended-victim mapping.')

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
        for _ in range(12):
            first = r.u32(first+0x1C)
        assert r.u32(r.labels['Toggles.info']) == head
        assert r.u32(r.labels['Toggles.info']+0x18) == first
        assert r.u32(r.labels['Toggles.info']+0xC) == 23
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


def main():
    rom = (ROOT / 'ssb64asm_extra.z64').read_bytes()
    labels = {name: int(address, 16) for address, name in re.findall(r'^([0-9a-fA-F]{8}) (.+)$', (ROOT/'logfile.log').read_text(), re.M)}
    assert rom[:4] == b'\x80\x37\x12\x40'
    assert calculate_crcs(rom) == struct.unpack_from('>II', rom, 0x10)
    hooks = {0x631B0: 'CharLab.prepare_', 0x5C00C: 'CharLab.anim_update_',
             0x5A8F0: 'CharLabRuntime.ccParse', 0x5C040: 'CharLab.events_all_',
             0x5C068: 'CharLab.events_forward_', 0x5DC4C: 'CharLab.collisions_',
             0xC4C28: 'CharLab.throw_', 0x116ED4: 'CharLab.training_exit_',
             0x13D9CC: 'CharLab.training_css_back_'}
    for offset, label in hooks.items():
        word = struct.unpack_from('>I', rom, offset)[0]
        assert word >> 26 in (2, 3) and word & 0x3FFFFFF == (labels[label] >> 2) & 0x3FFFFFF, label
    assert rom[0x42B3A:0x42B3E] == b'\x00\x7F\x0C\x90', 'Unlock patch missing'
    toggle = labels['Toggles.entry_improved_combo_meter'] - 0x80400000 + 0x3800000
    assert struct.unpack_from('>I', rom, toggle+4)[0] == 1
    linked_object(rom, labels)
    runtime = test_runtime(rom, labels)
    test_specials_and_return(runtime)
    print(f'ROM: {len(rom):,} bytes; SHA-256 {hashlib.sha256(rom).hexdigest()}')


if __name__ == '__main__':
    main()
