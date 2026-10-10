"""Linked-MIPS body mesh ownership; native pause/render acceptance is separate."""
import struct
from unicorn.mips_const import UC_MIPS_REG_A1, UC_MIPS_REG_AT, UC_MIPS_REG_T0, UC_MIPS_REG_T1


def test_body_models(r):
    offset, stride, base, current = struct.unpack('>4I', r.read(r.addr('ccBodyModelLayout'), 16))
    saved = dict(r.services)
    checks = 0
    for body in range(12):
        for port in range(4):
            donor = 0 if body == 5 else 5
            r.setup(body, donor, port)
            r.u32(r.FP+8, donor)
            r.u32(r.FP+0x9C4, 0x80215000)
            r.u32(r.labels['CharCreator.body_character_data']+port*4, 0x80214000)
            r.u32(r.labels['CharCreator.body_character_id']+port*4, body)
            r.u32(r.labels['CharCreator.active_special_donor']+port*4, donor)
            # Callback aliases make otherwise absent joints dereferenceable;
            # model code must see the actual NULL, without editing TopN.
            missing = 25
            r.u32(r.FP+0x8E8+missing*4, r.JOINTS)
            r.u32(r.labels['CharCreator.special_joint_backups']+port*148+missing*4, 0)
            initial = bytes([7, 0])*33
            r.write(r.FP+offset, initial)
            attr = r.u32(r.FP+0x9C8)
            r.call('ccLinkShield', r.GOBJ)
            expected = bytearray(initial)
            if body == 5:
                expected[(19-4)*stride+base] = 255
                expected[(21-4)*stride+base] = 0
            assert r.read(r.FP+offset, len(initial)) == bytes(expected), (body, port)
            assert r.u32(r.FP+8) == donor and r.u32(r.FP+0x9C4) == 0x80215000
            assert r.u32(r.FP+0x9C8) == attr

            def detail():
                assert r.u32(r.FP+8) == body
                assert r.u32(r.FP+0x8E8+missing*4) == 0
                assert r.u32(r.FP+0x9C4) == 0x80215000 and r.u32(r.FP+0x9C8) == attr
                assert r.reg(UC_MIPS_REG_A1) == 1
                return 0
            r.services[r.labels['CharLab.original_model_detail_']] = detail
            r.call('ccModelDetail', r.GOBJ, 1)
            assert r.u32(r.FP+8) == donor
            assert r.u32(r.FP+0x8E8+missing*4) == r.JOINTS
            assert r.u32(r.labels['CharCreator.special_joint_backups']+port*148+missing*4) == 0
            # Native SetStatus may have suspended aliases before changing
            # detail. The inner guard must keep that suspended entry state.
            r.call('suspend_joints_', r.FP, namespace='CharLab')
            assert r.u32(r.FP+0x8E8+missing*4) == 0
            r.call('ccModelDetail', r.GOBJ, 1)
            assert r.u32(r.FP+0x8E8+missing*4) == 0 and r.u32(r.FP+8) == donor
            r.call('resume_joints_', r.FP, namespace='CharLab')
            r.uc.reg_write(UC_MIPS_REG_AT, r.FP)
            r.uc.reg_write(UC_MIPS_REG_T0, 0x12345678)
            r.uc.reg_write(UC_MIPS_REG_T1, 0x87654321)
            r.call('body_kind_', namespace='StaticPart')
            assert r.reg(UC_MIPS_REG_AT) == body
            assert r.reg(UC_MIPS_REG_T0) == 0x12345678 and r.reg(UC_MIPS_REG_T1) == 0x87654321
            r.u32(r.labels['CharCreator.body_character_data']+port*4, 0)
            r.uc.reg_write(UC_MIPS_REG_AT, r.FP)
            r.call('body_kind_', namespace='StaticPart')
            assert r.reg(UC_MIPS_REG_AT) == donor
            checks += 1
    for address in list(r.services):
        if address not in saved: del r.services[address]
    r.services.update(saved)
    # Every static-part lookup must use the body helper, including native
    # animation loading and shield poses; donor FTData remains gameplay-owned.
    from pathlib import Path
    source=(Path(__file__).resolve().parents[1]/'extra_imports/StaticPart.asm').read_text()
    assert source.count('        body_kind(') == 7
    print(f'PASS: {checks} body/port model ownership cases: real Link shield defaults, foreign-body preservation, pause mesh holes, donor identity/resources restored and static-part body lookup with native fallback.')
