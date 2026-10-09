"""Execute the linked creator hub action with RNG/SRAM/colour services isolated.

Checks every controller-presence mask, independent recipe draws, ready VS state,
duplicate-body palette selection and save-before-navigation. Real input, native
CSS initialization and four-fighter loading are checked by --randomizer scenes.
"""
import random
import struct
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_T0, UC_MIPS_REG_T6, UC_MIPS_REG_T7, UC_MIPS_REG_V0


def test_css_heaps(r):
    heap, main, base, capacity = 0x80220000, 0x800465E8, 0x80230000, 0x1D000
    allocations = []
    saved = dict(r.services)
    def allocate():
        assert (r.reg(UC_MIPS_REG_A0),r.reg(UC_MIPS_REG_A1)) == (capacity,16)
        allocations.append(base)
        # Native malloc can destroy caller-saved attribute offsets. The hook
        # must preserve these for the surrounding fighter loader, too.
        r.uc.reg_write(UC_MIPS_REG_T6,0xDEADBEEF)
        r.uc.reg_write(UC_MIPS_REG_A0,0)
        r.uc.reg_write(UC_MIPS_REG_A1,0)
        return base
    r.services[0x80004980] = allocate
    for original in (0,1):
        r.u32(r.labels['Toggles.cc_original_12_only']+4,original)
        # The patched native call's delay slot advances the main cursor first.
        r.u32(main+12,base+capacity)
        r.call('css_heap_init_',heap,123,base,capacity,namespace='CharLab')
        assert [r.u32(heap+i) for i in (0,4,8,12)] == [123,base,base+(0 if original else capacity),base]
        assert r.u32(main+12) == base+(0 if original else capacity)
        before = len(allocations)
        r.uc.reg_write(UC_MIPS_REG_T0,heap)
        r.uc.reg_write(UC_MIPS_REG_T6,0x13579BDF)
        r.uc.reg_write(UC_MIPS_REG_V0,0x80221000)
        r.call('css_heap_alloc_',namespace='CharLab')
        assert len(allocations)-before == original
        assert r.u32(heap+8) == base+capacity
        assert r.reg(UC_MIPS_REG_V0) == 0x80221000
        assert r.reg(UC_MIPS_REG_T0) == heap
        assert r.reg(UC_MIPS_REG_T6) == 0x13579BDF
        assert r.reg(UC_MIPS_REG_T7) == r.labels['CharacterSelect.dynamic_css.alt_heap_pointer']
        # A used heap must never be allocated again or overwrite live models.
        r.call('css_heap_alloc_',namespace='CharLab')
        assert len(allocations)-before == original
    for address in list(r.services):
        if address not in saved: del r.services[address]
    r.services.update(saved)
    print('PASS: original-roster CSS skips unused model reservations; native heap initialization and one-time lazy allocation preserve live heaps, expanded mode and loader registers.')


def test_randomizer(r):
    # Scene heap initialization must drop borrowed ownership even when native
    # teardown already removed the fighters. No old animation heap is reused
    # by results/CSS fighters occupying the same player slot.
    for port in range(4):
        r.u32(r.labels['CharCreator.body_character_data']+port*4,0x801276A0)
        r.u32(r.labels['CharCreator.body_animation_heap']+port*4,0x80230000)
        r.u32(r.labels['CharCreator.active_special_donor']+port*4,1)
    for link in range(32):r.u32(0x800466F0+link*4,0)
    before=r.u32(r.labels['CharCreator.diagnostic_reset_calls'])
    r.call('heap_reset_',namespace='CharLab')
    assert r.u32(r.labels['CharCreator.diagnostic_reset_calls'])==before+1
    for port in range(4):
        assert r.u32(r.labels['CharCreator.body_character_data']+port*4)==0
        assert r.u32(r.labels['CharCreator.body_animation_heap']+port*4)==0
        assert r.u32(r.labels['CharCreator.active_special_donor']+port*4)==0xFFFFFFFF
    print('PASS: native scene heap reset clears interrupted donor ownership before results/CSS reuse fighter memory.')
    test_css_heaps(r)
    # Pikachu's FTData declares no private particle bank. A zero-range DMA
    # would reinterpret stale memory as a descriptor during multi-build setup.
    saved_particles = dict(r.services)
    bank_loads = []
    r.services[0x801159F8] = lambda: bank_loads.append(r.reg(UC_MIPS_REG_A0)) or 3
    r.u32(0x801313C4,1)
    r.u32(r.addr('sCCNeutralParticleBanks'),-1)
    r.call('ensure_neutral_particles_',4,namespace='CharCreator')
    assert not bank_loads and r.u32(r.addr('sCCNeutralParticleBanks')) == 1
    r.u32(r.addr('sCCNeutralParticleBanks')+4,-1)
    r.call('ensure_neutral_particles_',5,namespace='CharCreator')
    assert bank_loads and bank_loads[0] != 0
    assert r.u32(r.addr('sCCNeutralParticleBanks')+4) == 3
    for address in list(r.services):
        if address not in saved_particles: del r.services[address]
    r.services.update(saved_particles)
    print('PASS: Pikachu reuses the common effect bank without a zero-range DMA; Ness retains its real private-bank load.')
    layout = struct.unpack('>19I', r.read(r.addr('ccRandomizerLayout'), 76))
    size, players, stride, fkind, pkind, costume, shade, level, handicap, stocks, *battle_fields = layout
    stock, rules, teams, items, rate, reset, humans, cpus, stage_select = battle_fields
    battle, devices, scene = 0x800A4D08, 0x800451A4, 0x800A4AD0
    saved = dict(r.services)
    # Native body files must precede any cross-recipe donor publication.
    events = []
    r.services[0x800D786C] = lambda: events.append(('body',r.reg(UC_MIPS_REG_A0)))
    r.services[r.labels['CharCreator.get_slot_']] = lambda: events.append(('recipe',r.reg(UC_MIPS_REG_A0))) or 0
    r.u32(0x800A50E8,battle)
    r.write(scene,b'\x16')
    r.write(0x80046A12,b'\x00\x41')
    r.u32(0x80130D9C,0xFEF0)
    # FTManager computes these fields at match initialization. This suite
    # isolates that loader, so supply its original-roster buffer-size fixture.
    for kind,size in enumerate((0x1850,0x1320,0x2D30,0x19F0,0x1A40,0x1CA0,0x2490,0x2A20,0x2EC0,0x2A00,0x2030,0x2100)):
        r.u32(r.u32(0x80116E10+kind*4)+0x74,size)
    for port,body in enumerate((0,7,3,10)):
        r.write(battle+players+port*stride+fkind,bytes([body]))
        r.write(battle+players+port*stride+pkind,b'\0')
    for mode in (0,2):
        events.clear()
        r.u32(r.labels['VsRemixMenu.vs_mode_flag'],mode)
        r.call('preload_selected_builds_',namespace='CharCreator')
        assert events == ([('body',0),('body',7),('body',3),('body',10)] if mode==0 else [])+[('recipe',port) for port in range(4)]
    assert r.read(0x80046A12,2)==b'\x00\x80'
    original_max=max(r.u32(r.u32(0x80116E10+kind*4)+0x74) for kind in range(12))
    assert original_max==0x2EC0 and r.u32(0x80130D9C)==original_max
    for cap in (256,65535):
        r.write(0x80046A12,struct.pack('>H',cap))
        r.call('ccPreloadVSBodyFiles')
        assert r.read(0x80046A12,2)==struct.pack('>H',cap)
    events.clear()
    r.write(battle+players+pkind,b'\x02')
    r.write(battle+players+stride+fkind,b'\x0C')
    r.u32(0x80130D9C,0xFEF0)
    r.call('ccPreloadVSBodyFiles')
    assert events == [('body',3),('body',10)]
    assert r.u32(0x80130D9C)==0xFEF0, 'Expanded participants retain the full native buffer size'
    events.clear()
    r.write(scene,b'\x36')
    r.call('ccPreloadVSBodyFiles')
    assert not events, 'Training keeps its separate established file-load path'
    for address in list(r.services):
        if address not in saved: del r.services[address]
    r.services.update(saved)
    print('PASS: ordinary VS completes native participant files before donor recipes and raises the 65-object cap; higher/unlimited caps, absent/expanded slots, Tag Team and Training retain their load paths.')
    # The engine clears main-file globals per match. Native participants can
    # share that current file; immutable scripts can share across port caches.
    data, main_pointer, motion_pointer = 0x80221000, 0x80221300, 0x80221304
    r.write(data,bytes(0x80))
    r.u32(data,75);r.u32(data+4,76)
    r.u32(data+0x28,main_pointer);r.u32(data+0x2C,motion_pointer)
    r.u32(main_pointer,0x80250000);r.u32(motion_pointer,0)
    r.call('reset_cache_',namespace='CharCreator')
    loaded=[]
    def load_file():
        loaded.append(r.reg(UC_MIPS_REG_A0))
        r.u32(r.reg(UC_MIPS_REG_A1),0x80260000)
        return 0x80260000
    loader=r.labels['Render.load_file_'];old_loader=r.services.get(loader)
    r.services[loader]=load_file
    r.call('ensure_main_file_',3,data,namespace='CharCreator')
    assert not loaded and r.reg(UC_MIPS_REG_V0)==0x80250000
    assert r.u32(r.labels['CharCreator.main_file_pointers']+12)==0x80250000
    for port in range(4):
        r.call('get_moveset_base_',port,3,data,namespace='CharCreator')
        assert r.reg(UC_MIPS_REG_V0)==0x80260000
        assert r.u32(motion_pointer)==0x80260000
    assert loaded==[76],('Duplicate immutable script allocation',loaded)
    if old_loader is None:del r.services[loader]
    else:r.services[loader]=old_loader
    print('PASS: native current-match main data is reused without DMA; four independent port caches share one immutable donor-script allocation.')
    draws, palettes, snapshots = [], [], []
    rng = random.Random(640037)
    force = None
    def draw():
        assert r.reg(UC_MIPS_REG_A0) == 12
        value = rng.randrange(12) if force is None else force
        draws.append(value)
        return value
    def palette():
        body, colour = r.reg(UC_MIPS_REG_A0), r.reg(UC_MIPS_REG_A1)
        palettes.append((body, colour))
        return colour
    def recipes():
        return [tuple(r.u32(r.u32(r.u32(r.labels['CharCreator.slot_tables']+port*4)+field*4))
                      for field in range(22)) for port in range(4)]
    def save():
        # Save sees all four enabled recipes and bindings before CSS opens.
        assert r.read(scene, 1) == b'9'
        snapshot = recipes()
        assert all(row[0] == 1 for row in snapshot)
        assert [r.u32(r.labels['CharCreator.selected_builds']+port*4) for port in range(4)] == [1,2,3,4]
        snapshots.append(snapshot)
    r.services[r.labels['Global.get_random_int_safe_']] = draw
    r.services[0x800EC0EC] = palette
    r.services[r.labels['Toggles.save_']] = save
    counts = [set() for _ in range(21)]
    title = r.labels['Toggles.cc_randomize_all']
    assert r.u32(r.labels['Toggles.cc_original_12_only']+0x1C) == title
    assert r.read(title+0x28, 19) == b'Randomize 4 Builds\0'
    for case in range(144):
        mask = case % 16
        ports = [i for i in range(4) if mask & (1 << i)]
        r.write(devices, bytes(ports+[255]*(4-len(ports))))
        r.write(battle, bytes([255])*size)
        r.write(scene, b'9')
        for name in ('CharLab.training_slot','CharLab.return_slot','VsRemixMenu.vs_mode_flag','TwelveCharBattle.twelve_cb_flag'):
            r.u32(r.labels[name], 3)
        for name in ('StockMode.stockmode_table','VsRemixMenu.global_stockmode_table'):
            for port in range(4): r.u32(r.labels[name]+port*4, 2)
        for name in ('global_game_mode','global_stage_select','global_teams'):
            r.u32(r.labels['VsRemixMenu.'+name],3)
        r.u32(r.labels['Toggles.cc_original_12_only']+4, 0)
        before = len(draws)
        palettes.clear()
        # Boundary and duplicate-body cases, followed by reproducible mixed draws.
        force = 0 if case == 0 else 11 if case == 1 else None
        r.call('randomize_all_', namespace='CharCreator')
        rows = recipes()
        assert len(draws)-before == 84, 'One independent draw per body/move'
        assert rows == snapshots[-1]
        for port, row in enumerate(rows):
            expected = draws[before+port*21:before+(port+1)*21]
            assert list(row[1:15])+[row[15]-1]+list(row[16:]) == expected
            for field, value in enumerate(expected): counts[field].add(value)
            player = battle+players+port*stride
            assert r.read(player+fkind,1)[0] == row[1]
            assert r.read(player+pkind,1)[0] == (0 if port in ports else 1)
            duplicate = sum(old[1] == row[1] for old in rows[:port])
            assert palettes[port] == (row[1], duplicate)
            assert tuple(r.read(player+off,1)[0] for off in (costume,shade,level,handicap,stocks)) == (duplicate,0,5,9,3)
        assert tuple(r.read(battle+off,1)[0] for off in (stock,rules,teams,rate,reset,humans,cpus,stage_select)) == (3,2,0,0,0,len(ports),4-len(ports),1)
        assert r.u32(battle+items) == 0
        assert r.read(scene,2) == b'\x10\x39'
        assert r.u32(r.labels['Toggles.cc_original_12_only']+4) == 1
        for name in ('CharLab.training_slot','CharLab.return_slot','VsRemixMenu.vs_mode_flag','TwelveCharBattle.twelve_cb_flag'):
            assert r.u32(r.labels[name]) == 0
        for name in ('StockMode.stockmode_table','VsRemixMenu.global_stockmode_table'):
            assert all(r.u32(r.labels[name]+port*4) == 0 for port in range(4))
        assert [r.u32(r.labels['VsRemixMenu.'+name]) for name in ('global_game_mode','global_stage_select','global_teams')] == [2,1,0]
    assert all(values == set(range(12)) for values in counts), counts
    assert len(set(row[1:] for snapshot in snapshots[2:] for row in snapshot)) == 568
    # Exercise real legacy packing, including the new non-persisted hub title
    # and Neutral B/taunt supplements, rather than only intercepting save I/O.
    moves = []
    for name in ('export_','import_'):
        address = r.labels['Menu.'+name]+24
        word = r.u32(address)
        assert word & 63 == 0x2D
        moves.append((address,word))
        r.u32(address,(word&~63)|0x21)  # Equivalent DADDU fixture move on MIPS32.
    for force in range(12):
        r.write(scene,b'9')
        r.call('randomize_all_',namespace='CharCreator')
        expected = recipes()
        r.call('export_neutral_choices_',namespace='CharCreator')
        for port in range(4):
            head = r.labels[f'Toggles.head_char_creator_slot_{port+1}']
            block = r.labels[f'Toggles.block_char_creator_{port+1}']
            r.call('export_',head,block,namespace='Menu')
            table = r.u32(r.labels['CharCreator.slot_tables']+port*4)
            for field in range(22): r.u32(r.u32(table+field*4),0)
            r.call('import_',head,block,namespace='Menu')
        options = r.labels['Toggles.block_char_creator_options']
        r.call('export_',r.labels['Toggles.head_char_creator'],options,namespace='Menu')
        r.u32(r.labels['Toggles.cc_original_12_only']+4,0)
        r.call('import_',r.labels['Toggles.head_char_creator'],options,namespace='Menu')
        r.call('import_neutral_choices_',namespace='CharCreator')
        assert recipes() == expected, ('Randomized SRAM roundtrip',force,recipes(),expected)
        assert r.u32(r.labels['Toggles.cc_original_12_only']+4) == 1
    for address, word in moves: r.u32(address,word)
    for address in list(r.services):
        if address not in saved: del r.services[address]
    r.services.update(saved)
    print('PASS: 144 linked hub randomizations, all 16 controller masks, all 12 choices in every field, duplicate costumes, four enabled/assigned builds, four-stock items-off VS state, save-before-navigation and 12 four-recipe SRAM roundtrips.')
