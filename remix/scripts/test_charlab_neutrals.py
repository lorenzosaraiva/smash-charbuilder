"""Run neutral donor clocks, charge storage and legacy SRAM packing on linked MIPS.

Status installation/projectile allocation are explicit fixtures here. Live CPU
scene checks exercise those engine services, collision and resource loading.
"""
import struct
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2


def test_neutrals(r, full=True):
    saved = dict(r.services)
    def status():
        r.u32(r.FP+0x24, r.reg(UC_MIPS_REG_A1))
        r.u32(r.FP+0x28, 300)
        r.f32(r.GOBJ+r.layout['frame'], 0)
    r.services[0x800E6F24] = status
    r.services[0x800DEE54] = lambda: r.u32(r.FP+0x24, 10)
    r.services[0x800E02A8] = lambda: 0  # UpdateMotionEventsAll; events called explicitly.
    r.services[0x800269C0] = lambda: 0
    # Generic weapon allocation remains native in live scenes. This test records
    # the source spawn position and factory choice independently of rendering.
    fired = []
    for name in ('ccwp_wpMarioFireballMakeWeapon', 'ccwp_wpPikachuThunderJoltAirMakeWeapon',
                 'ccwp_wpNessPKFireMakeWeapon', 'ccwp_wpSamusChargeShotMakeWeapon',
                 'ccwp_wpLinkBoomerangMakeWeapon'):
        address = r.addr(name)
        def make(address=address):
            pos = r.reg(UC_MIPS_REG_A1)
            fired.append((address, tuple(struct.unpack('>3f', r.read(pos, 12)))))
            return 0x80218000
        r.services[address] = make
    def allocation():
        fired.append((r.reg(UC_MIPS_REG_A1), struct.unpack('>3f',r.read(r.reg(UC_MIPS_REG_A2),12))))
        return 0
    r.services[0x801655C8] = allocation
    # Engine capture-mask/catch registration accesses match lists; isolate it.
    import re
    from pathlib import Path
    lab = Path(__file__).resolve().parents[2]/'ssb-decomp-re'
    symbols = {}
    for file in ('ft/ftparam.c', 'ft/ftcommon/ftcommonescape.c'):
        source = (lab/'src'/file).read_text(encoding='utf-8')
        symbols.update({name:int(address,16) for address,name in re.findall(r'// (0x[0-9A-Fa-f]{8})[^\n]*\n(?:[\w*]+\s+)+(\w+)\(',source)})
    for name in ('ftParamSetCatchParams', 'ftParamSetCaptureImmuneMask'):
        r.services[symbols[name]] = lambda: 0
    r.services[symbols['ftCommonEscapeGetStatus']] = lambda: -1
    donors = (None,1,0,4,9,11,7,10,2,3,5,6)
    actions = r.addr('sFTCharBuilderActions')
    state = r.addr('sFTCharBuilderNeutralStates')
    clock = r.addr('sFTCustomMoveClocks')
    def start(body, choice, air=0, port=0):
        r.setup(body, 0, port);r.preset(body, 0, choice)
        # Map port to recipe one, as the menu supports.
        r.u32(r.labels['CharCreator.selected_builds']+port*4, 1)
        r.u32(r.FP+r.layout['ga'], air)
        return r.call('ccNeutral', r.GOBJ)
    checks=0
    for body in (range(12) if full else (0,)):
        print(f'Checking neutral adapters on body {body+1}/12...',flush=True)
        for choice in range(2,12):
            for air in (0,1):
                for port in range(4):
                    r.call('ccReset');fired.clear()
                    result = start(body, choice, air, port)
                    assert bool(result) == (body != donors[choice]), (body,choice,air,port,result)
                    if not result:continue
                    c=clock+port*r.clock_size
                    move=r.u32(c+r.clock_move)
                    duration=r.u32(move+8)
                    assert r.u32(c)==r.FP
                    for tick in range(1,duration+1):
                        r.advance(-1);r.events();r.call('ccCollision',r.FP)
                        accessory=r.u32(r.FP+r.layout['accessory'])
                        r.call(next(name[15:] for name,a in r.labels.items() if a==accessory and name.startswith('CharLabRuntime.')),r.GOBJ)
                    assert r.f32(c+r.clock_frame)==duration
                    if choice in (2,3,4,5,10):assert len(fired)==1,(body,choice,air,port,fired)
                    # Generation recycling invalidates both script clock and sidecar.
                    r.u32(r.FP+r.player_num, r.u32(r.FP+r.player_num)+1)
                    assert r.advance(77)==77
                    checks+=1
    # Independent charges survive a normal interruption, and reset on respawn.
    for choice,charge_offset,start_pair in ((8,16,4),(9,20,12)):
        r.call('ccReset');start(0,choice)
        r.u32(state+charge_offset,3)
        r.u32(r.FP+0x24,10)
        assert start(0,choice)==1
        assert r.u32(state+charge_offset)==3
        r.u32(r.FP+r.player_num,1)
        assert r.call('ccNeutral',r.GOBJ)==1
        assert r.u32(state+charge_offset)==0
    # All twelve values survive all four recipe slots without changing legacy
    # recipe width or overwriting throws/other toggles.
    options=r.labels['Toggles.block_char_creator_options']
    # Upstream Menu.move assembles to N64 DADDU. Unicorn's MIPS32 CPU lacks
    # that instruction; replace only these two pointer-register moves with
    # equivalent ADDU in fixture RAM. The ROM remains untouched; the live
    # editor test executes the original N64 instructions and real SRAM I/O.
    menu_moves=[]
    for name in ('export_','import_'):
        address=r.labels['Menu.'+name]+24
        word=r.u32(address)
        assert word & 63 == 0x2D
        menu_moves.append((address,word));r.u32(address,(word&~63)|0x21)
    r.u32(options+0x10,1)
    tables=[r.u32(r.labels['CharCreator.slot_tables']+i*4) for i in range(4)]
    for base in range(12):
        values=[(base+i)%12 for i in range(4)]
        for table,value in zip(tables,values):
            entry=r.u32(table+15*4)
            assert r.u32(entry-4)==1  # compile-time one-bit serialization type
            r.u32(entry,value)
        r.call('export_neutral_choices_',namespace='CharCreator')
        expected=[]
        for i,table in enumerate(tables):
            entry=r.u32(table+15*4)
            assert r.u32(entry) in (0,1)
            # Run the real packing/unpacking, including all adjacent throws.
            snapshot=[r.u32(r.u32(table+j*4)) for j in range(21)]
            expected.append(snapshot)
            head=r.u32(table)-4
            block=r.labels[f'Toggles.block_char_creator_{i+1}']
            r.call('export_',head,block,namespace='Menu')
            for j in range(21):r.u32(r.u32(table+j*4),0)
            r.call('import_',head,block,namespace='Menu')
            assert [r.u32(r.u32(table+j*4)) for j in range(21)]==snapshot
        r.call('import_neutral_choices_',namespace='CharCreator')
        assert [r.u32(r.u32(t+15*4)) for t in tables]==values
        assert r.u32(options+0x10)==1
    r.u32(options+0x14,0)
    r.call('import_neutral_choices_',namespace='CharCreator')
    assert [r.u32(r.u32(t+15*4)) for t in tables]==values
    for address,word in menu_moves:r.u32(address,word)
    # Source charging callbacks: cycle boundaries, queued release, store,
    # charge-dependent startup and damage interruption are executed directly.
    def button(mask):
        r.write(r.FP+r.layout['b_mask']-2,struct.pack('>3H',0x8000,0x4000,0x2000))
        r.write(r.FP+r.layout['tap'],struct.pack('>H',mask))
        r.call('ftMainCharBuilderActionInterrupt',r.GOBJ)
        r.write(r.FP+r.layout['tap'],b'\0\0')
    def tick(count):
        for _ in range(count):
            r.advance(-1);r.events()
            r.call('ftMainCharBuilderActionAccessory',r.GOBJ)
            r.call('ftMainCharBuilderActionUpdate',r.GOBJ)
    r.call('ccReset');start(0,8);tick(8)
    assert r.u32(state+12)==6 and r.u32(state+16)==0
    tick(12);assert r.u32(state+16)==1
    button(0x2000);tick(12)
    assert r.u32(r.FP+0x24)==10 and r.u32(state+16)==2
    start(0,8);tick(8);button(0x4000);tick(12)
    assert r.u32(state+12)==8 and r.u32(state+24)==3 and r.u32(state+16)==0
    r.call('ccReset');start(0,9);tick(16)
    assert r.u32(state+12)==14
    tick(40);assert r.u32(state+20)==2
    button(0x2000);assert r.u32(r.FP+0x24)==10 and r.u32(state+20)==2
    start(0,9);assert r.f32(clock+40)<1.0
    tick(20);button(0x8000)
    assert r.u32(state+12)==16 and r.u32(state+24)==2
    tick(31);assert r.u32(state+20)==0
    start(0,9);tick(36);r.call('ftMainCharBuilderActionDamage',r.GOBJ)
    assert r.u32(state+20)==0
    for address in list(r.services):
        if address not in saved:del r.services[address]
    r.services.update(saved)
    print(f'PASS: {checks} neutral body/air/port clocks, native donor passthrough, source projectile firing, charge generation/storage and twelve-choice SRAM supplements execute on MIPS.')
