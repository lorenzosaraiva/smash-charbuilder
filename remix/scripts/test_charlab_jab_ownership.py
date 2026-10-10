"""Unique IDs require a requested jab phase, rather than a motion-number match."""
import struct


def test_jab_ownership(r):
    motion_start, count = struct.unpack('>2I', r.read(r.addr('ccJabOwnershipLayout'), 8))
    native_cases = struct.unpack('>'+str(count*2)+'I', r.read(r.addr('ccJabNativeCases'), count*8))
    clocks = r.addr('sFTCustomMoveClocks')
    donors = r.labels['CharCreator.active_normal_donor']
    native_checks = phases = 0
    for body, status in zip(native_cases[::2], native_cases[1::2]):
        table = r.u32(r.labels['Character.ACTION_ARRAY_TABLE']+body*4)
        motion = r.u32(table+(status-0xDC)*20)>>22
        for donor in range(12):
            for port in range(4):
                r.call('ccReset'); r.setup(body, donor, port); r.preset(body, donor)
                # A preceding normal cannot own this native entrance/special.
                r.u32(donors+port*4, donor)
                r.call('ccJabStatusChanging', r.FP, status)
                assert r.u32(donors+port*4)==0xFFFFFFFF
                r.u32(r.FP+0x24, status); r.u32(r.FP+0x28, motion)
                r.call('ccStart', r.FP, 0)
                assert r.u32(clocks+port*r.clock_size)==0, (body, donor, port, status, motion)
                loads = r.u32(r.addr('gCCAnimationLoads'))
                assert r.advance(52)==52
                assert r.u32(r.addr('gCCAnimationLoads'))==loads
                native_checks += 1
    for body in range(12):
        for donor in range(12):
            if body==donor: continue
            for phase in range(4):
                motion = r.u32(r.addr('sFTCustomBodyExtraMotionIDs')+(donor*4+phase)*4)
                if motion==0xFFFFFFFF: continue
                status = 0xDC+motion-motion_start
                for port in range(4):
                    r.call('ccReset'); r.setup(body, donor, port); r.preset(body, donor)
                    assert r.call('ftMainCharBuilderGetJabStatus', r.FP, status, phase)==status
                    r.call('ccJabStatusChanging', r.FP, status)
                    assert r.u32(donors+port*4)==donor
                    r.u32(r.FP+0x24, status); r.u32(r.FP+0x28, motion)
                    r.call('ccStart', r.FP, 0)
                    clock = clocks+port*r.clock_size
                    assert r.u32(clock+r.clock_move)==r.addr('sFTCustomMoves')+(donor*33+29+phase)*16
                    duration = r.u32(clock+20)
                    r.f32(clock+r.clock_frame, duration-1)
                    frame = r.advance()
                    assert (0<frame<1) if phase==2 else frame==-1, (body, donor, phase, frame)
                    # Identical numeric IDs do not grant a second request.
                    r.call('ccJabStatusChanging', r.FP, status)
                    r.call('ccStart', r.FP, 0)
                    assert r.u32(clock)==0 and r.u32(donors+port*4)==0xFFFFFFFF
                    phases += 1
    # Captain's eligibility query compares Jab3 without installing that phase.
    r.call('ccReset'); r.setup(11, 7); r.preset(11, 7)
    r.call('ccn_ftCommonAttack100StartCheckInterruptCommon', r.GOBJ)
    assert r.u32(donors)==0xFFFFFFFF
    r.call('ccJabStatusChanging', r.FP, 0xDC)
    r.u32(r.FP+0x24, 0xDC); r.u32(r.FP+0x28, motion_start)
    r.call('ccStart', r.FP, 0)
    assert r.u32(clocks)==0
    # A recycled fighter cannot consume an earlier fighter's request.
    r.call('ftMainCharBuilderGetJabStatus', r.FP, 0xDC, 0)
    r.u32(r.FP+r.player_num, r.u32(r.FP+r.player_num)+1)
    r.call('ccJabStatusChanging', r.FP, 0xDC)
    r.call('ccStart', r.FP, 0)
    assert r.u32(clocks)==0
    # Expanded bodies keep the existing Remix callback/ownership fallback.
    for port in range(4):
        r.setup(12, 1, port)
        r.u32(donors+port*4, 1)
        r.call('ccJabStatusChanging', r.FP, 0xDC)
        assert r.u32(donors+port*4)==1
    r.call('ccReset')
    print(f'PASS: {native_checks} native entrance/special cases preserve their clocks; {phases} requested jab phases retain timing and clear on unrequested transitions; Captain eligibility and recycled-owner guards.')
