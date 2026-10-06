// CharCreator.asm
// Runtime recipe mixer for the +EXTRA in-game Character Creator.
if !{defined __CHAR_CREATOR__} {
define __CHAR_CREATOR__()
print "included CharCreator.asm\n"

scope CharCreator {
    constant SLOT_COUNT(4)
    constant CACHE_SLOTS(8)
    constant NO_DONOR(0xFFFFFFFF)
    // Largest current catalog FTData.file_anim_size is 0xCB10. Keep one
    // aligned buffer per port outside the match task heap, whose late-stage
    // allocator cannot reliably satisfy these reservations in Training.
    constant SPECIAL_ANIMATION_CAPACITY(0xCC00)

    // Per-port CSS selection. 0 = off, 1-4 = saved build.
    selected_builds:
    dw 0, 0, 0, 0

    // The base used by Command.jump_to_moveset_file_ while a borrowed command
    // stream is executing.
    active_moveset_base:
    dw 0, 0, 0, 0

    // Character ID whose unique-action data is currently active for each
    // player. 0xFFFFFFFF means the body owns the action.
    active_special_donor:
    dw NO_DONOR, NO_DONOR, NO_DONOR, NO_DONOR
    // Donor retained while a shared normal (notably Jab) transitions into a
    // character-specific follow-up action such as Jab 3 or a rapid-jab loop.
    active_normal_donor:
    dw NO_DONOR, NO_DONOR, NO_DONOR, NO_DONOR

    // Original FTData pointer saved while a donor special owns the fighter.
    // The adapter temporarily swaps fp->data because donor callbacks read it
    // directly for action, animation, and projectile resources.
    body_character_data:
    dw 0, 0, 0, 0
    body_character_id:
    dw NO_DONOR, NO_DONOR, NO_DONOR, NO_DONOR
    body_animation_heap:
    dw 0, 0, 0, 0
    special_animation_heap:
    dw 0, 0, 0, 0
    special_animation_heap_size:
    dw 0, 0, 0, 0

    OS.align(16)
    special_animation_storage:
    fill SLOT_COUNT * SPECIAL_ANIMATION_CAPACITY

    // Donor animations are authored for the donor's joint tree and cannot be
    // installed on an unrelated body safely. During borrowed specials, the
    // parameter-record hook below substitutes body Idle/Fall. The shared
    // runtime supplies the donor phase clock independently of that pose.
    special_parameter_records:
    fill SLOT_COUNT * 0x000C

    // Shared normals use the body's animation and animation flags with the
    // donor's motion-command stream. Keep one synthetic parameter record per
    // port so simultaneous custom fighters cannot overwrite each other.
    normal_parameter_records:
    fill SLOT_COUNT * 0x000C

    // Donor callbacks can index fp->joints directly, bypassing command guards.
    // Back up all 37 engine slots while a borrowed special is active; missing
    // donor joints temporarily resolve to the body's top joint.
    special_joint_backups:
    fill SLOT_COUNT * 37 * 4

    // Eight lazily-loaded donor moveset files per port. This bounds memory use
    // and turns an over-complex recipe into a safe body-move fallback.
    cache_ids:
    fill SLOT_COUNT * CACHE_SLOTS, 0xFF
    OS.align(4)
    cache_pointers:
    fill SLOT_COUNT * CACHE_SLOTS * 4
    status_by_port:; dw 0, 0, 0, 0
    // One bit per Character.id. Prevents repeated loading of Tag Team's
    // declared special/projectile dependencies during the same screen.
    preloaded_specials:; fill 16
    loaded_main_files:; fill 16
    // The fighter loader clears FTData.p_file_main globals after this
    // preloader runs. Retain the heap-owned file bases so ensure_main_file_
    // can republish them at dispatch time without an unsafe mid-action load.
    main_file_pointers:; fill 0x80 * 4
    // Tracks donor FTData special1-special4 files loaded into their real
    // destination globals (for example gFTDataFoxSpecial1). Tag Team's generic
    // preload list deliberately discards those pointers, which is insufficient
    // when the borrowed callback later constructs a projectile from one.
    loaded_special_files:; fill 16
    preload_pointer:; dw 0
    // Character Creator's laser does not use Fox's shared special-file global.
    // Keeping a private pointer prevents later fighter loads from clearing or
    // republishing the resource behind the projectile descriptor.
    laser_file_pointer:; dw 0
    catalog_mode_last:; dw 0xFFFFFFFF
    neutral_strings:; dw neutral_body, neutral_fox
    neutral_body:; String.insert("Body Move")
    neutral_fox:; String.insert("Fox Laser")

    // Runtime breadcrumbs used to verify that the pre-match loader runs after
    // the final cache reset. They are intentionally outside recipe SRAM.
    diagnostic_reset_calls:; dw 0
    diagnostic_reset_last_ra:; dw 0
    diagnostic_preload_calls:; dw 0
    diagnostic_preload_selected:; dw 0
    diagnostic_preload_heap:; dw 0
    diagnostic_action_array:; dw 0
    diagnostic_action_index:; dw 0
    diagnostic_parameter_array:; dw 0
    diagnostic_parameter_index:; dw 0
    diagnostic_laser_stage:; dw 0
    diagnostic_laser_resource:; dw 0
    diagnostic_laser_weapon:; dw 0

    // Fields in each slot's entry-pointer table.
    constant FIELD_ENABLED(0)
    constant FIELD_BODY(1)
    constant FIELD_JAB(2)
    constant FIELD_DASH(3)
    constant FIELD_FTILT(4)
    constant FIELD_UTILT(5)
    constant FIELD_DTILT(6)
    constant FIELD_FSMASH(7)
    constant FIELD_USMASH(8)
    constant FIELD_DSMASH(9)
    constant FIELD_NAIR(10)
    constant FIELD_FAIR(11)
    constant FIELD_BAIR(12)
    constant FIELD_UAIR(13)
    constant FIELD_DAIR(14)
    constant FIELD_NSP(15)
    constant FIELD_USP(16)
    constant FIELD_DSP(17)
    constant FIELD_GRAB(18)
    constant FIELD_THROWF(19)
    constant FIELD_THROWB(20)
    constant FIELD_COUNT(21)

    macro slot_entry_table(slot) {
        slot_{slot}_entries:
        dw Toggles.cc_slot_{slot}_enabled + 0x4
        dw Toggles.cc_slot_{slot}_body + 0x4
        dw Toggles.cc_slot_{slot}_jab + 0x4
        dw Toggles.cc_slot_{slot}_dash + 0x4
        dw Toggles.cc_slot_{slot}_ftilt + 0x4
        dw Toggles.cc_slot_{slot}_utilt + 0x4
        dw Toggles.cc_slot_{slot}_dtilt + 0x4
        dw Toggles.cc_slot_{slot}_fsmash + 0x4
        dw Toggles.cc_slot_{slot}_usmash + 0x4
        dw Toggles.cc_slot_{slot}_dsmash + 0x4
        dw Toggles.cc_slot_{slot}_nair + 0x4
        dw Toggles.cc_slot_{slot}_fair + 0x4
        dw Toggles.cc_slot_{slot}_bair + 0x4
        dw Toggles.cc_slot_{slot}_uair + 0x4
        dw Toggles.cc_slot_{slot}_dair + 0x4
        dw Toggles.cc_slot_{slot}_nsp + 0x4
        dw Toggles.cc_slot_{slot}_usp + 0x4
        dw Toggles.cc_slot_{slot}_dsp + 0x4
        dw Toggles.cc_slot_{slot}_grab + 0x4
        dw Toggles.cc_slot_{slot}_throwf + 0x4
        dw Toggles.cc_slot_{slot}_throwb + 0x4
    }

    slot_entry_table(1)
    slot_entry_table(2)
    slot_entry_table(3)
    slot_entry_table(4)

    slot_tables:
    dw slot_1_entries, slot_2_entries, slot_3_entries, slot_4_entries

    // @ Description
    // Clears the donor file cache. Loaded files are owned by the game's heap;
    // this only forgets pointers when moving between screens/builds.
    scope reset_cache_: {
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        jal CharLab.reset_
        nop
        lw ra, 0x0014(sp)
        addiu sp, sp, 0x0020
        li      t0, diagnostic_reset_calls
        lw      t1, 0x0000(t0)
        addiu   t1, t1, 0x0001
        sw      t1, 0x0000(t0)
        li      t0, diagnostic_reset_last_ra
        sw      ra, 0x0000(t0)

        li      t0, cache_ids
        lli     t1, SLOT_COUNT * CACHE_SLOTS
        addiu   t2, r0, -0x0001
        _id_loop:
        sb      t2, 0x0000(t0)
        addiu   t0, t0, 0x0001
        addiu   t1, t1, -0x0001
        bnez    t1, _id_loop
        nop

        li      t0, cache_pointers
        lli     t1, SLOT_COUNT * CACHE_SLOTS
        _pointer_loop:
        sw      r0, 0x0000(t0)
        addiu   t0, t0, 0x0004
        addiu   t1, t1, -0x0001
        bnez    t1, _pointer_loop
        nop

        li      t0, active_moveset_base
        sw      r0, 0x0000(t0)
        sw      r0, 0x0004(t0)
        sw      r0, 0x0008(t0)
        sw      r0, 0x000C(t0)

        li      t0, active_special_donor
        addiu   t1, r0, -0x0001
        sw      t1, 0x0000(t0)
        sw      t1, 0x0004(t0)
        sw      t1, 0x0008(t0)
        sw      t1, 0x000C(t0)

        li      t0, active_normal_donor
        sw      t1, 0x0000(t0)
        sw      t1, 0x0004(t0)
        sw      t1, 0x0008(t0)
        sw      t1, 0x000C(t0)

        li      t0, body_character_data
        sw      r0, 0x0000(t0)
        sw      r0, 0x0004(t0)
        sw      r0, 0x0008(t0)
        sw      r0, 0x000C(t0)
        li      t0, body_character_id
        sw      t1, 0x0000(t0)
        sw      t1, 0x0004(t0)
        sw      t1, 0x0008(t0)
        sw      t1, 0x000C(t0)
        li      t0, body_animation_heap
        sw      r0, 0x0000(t0)
        sw      r0, 0x0004(t0)
        sw      r0, 0x0008(t0)
        sw      r0, 0x000C(t0)
        li      t0, special_animation_heap
        li      t1, special_animation_storage
        li      t2, SPECIAL_ANIMATION_CAPACITY
        lli     t3, SLOT_COUNT
        _special_heap_pointer_loop:
        sw      t1, 0x0000(t0)
        addiu   t0, t0, 0x0004
        addu    t1, t1, t2
        addiu   t3, t3, -0x0001
        bnez    t3, _special_heap_pointer_loop
        nop
        li      t0, special_animation_heap_size
        lli     t3, SLOT_COUNT
        _special_heap_size_loop:
        sw      t2, 0x0000(t0)
        addiu   t0, t0, 0x0004
        addiu   t3, t3, -0x0001
        bnez    t3, _special_heap_size_loop
        nop

        li      t0, preloaded_specials
        sw      r0, 0x0000(t0)
        sw      r0, 0x0004(t0)
        sw      r0, 0x0008(t0)
        sw      r0, 0x000C(t0)
        li      t0, loaded_main_files
        sw      r0, 0x0000(t0)
        sw      r0, 0x0004(t0)
        sw      r0, 0x0008(t0)
        sw      r0, 0x000C(t0)
        li      t0, main_file_pointers
        lli     t1, 0x0080
        _main_pointer_loop:
        sw      r0, 0x0000(t0)
        addiu   t0, t0, 0x0004
        addiu   t1, t1, -0x0001
        bnez    t1, _main_pointer_loop
        nop
        li      t0, loaded_special_files
        sw      r0, 0x0000(t0)
        sw      r0, 0x0004(t0)
        sw      r0, 0x0008(t0)
        sw      r0, 0x000C(t0)
        li      t0, laser_file_pointer
        sw      r0, 0x0000(t0)
        li      t0, diagnostic_laser_stage
        sw      r0, 0x0000(t0)
        li      t0, diagnostic_laser_resource
        sw      r0, 0x0000(t0)
        li      t0, diagnostic_laser_weapon
        sw      r0, 0x0000(t0)
        jr      ra
        nop
    }

    // @ Description
    // Returns a slot entry-pointer table in v0, or 0 when disabled/invalid.
    // a0 = port
    scope get_slot_: {
        sltiu   t0, a0, 0x0004
        beqz    t0, _none
        nop
        li      t0, selected_builds
        sll     t1, a0, 0x0002
        addu    t0, t0, t1
        lw      t0, 0x0000(t0)
        beqz    t0, _none
        addiu   t0, t0, -0x0001
        sltiu   t1, t0, SLOT_COUNT
        beqz    t1, _none
        sll     t0, t0, 0x0002
        li      t1, slot_tables
        addu    t1, t1, t0
        lw      v0, 0x0000(t1)
        lw      t0, 0x0000(v0)             // enabled entry value pointer
        lw      t0, 0x0000(t0)             // enabled value
        beqz    t0, _none
        nop
        jr      ra
        nop
        _none:
        jr      ra
        or      v0, r0, r0
    }

    // @ Description
    // Converts a catalog selector index to a Character.id. Invalid indexes
    // return Character.id.NONE.
    // a0 = selector index
    scope catalog_id_: {
        sltiu   t0, a0, CharCreatorCatalog.COUNT
        beqz    t0, _invalid
        li      t0, CharCreatorCatalog.id_table
        addu    t0, t0, a0
        jr      ra
        lbu     v0, 0x0000(t0)
        _invalid:
        jr      ra
        lli     v0, Character.id.NONE
    }

    // @ Description
    // Returns donor character ID in v0, or -1 when the body move should be used.
    // a0 = player struct, a1 = action ID
    scope get_normal_donor_: {
        lw t0, 0x0008(a0)
        sltiu t0, t0, 12
        beqz t0, _legacy
        nop
        jr ra
        addiu v0, r0, -1 // Original bodies use compiled donor tables.
        _legacy:
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        sw      a1, 0x000C(sp)
        lbu     a0, 0x000D(a0)
        jal     get_slot_
        nop
        beqz    v0, _none
        sw      v0, 0x0010(sp)

        // A build only applies to its configured body. This prevents a stale
        // CSS selection from unexpectedly rewriting another fighter.
        lw      t0, 0x0004(v0)             // FIELD_BODY entry pointer
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        lw      t0, 0x0008(sp)
        lw      t1, 0x0008(t0)
        bne     v0, t1, _wrong_body
        lw      a1, 0x000C(sp)

        // Map shared attack/landing actions to recipe fields.
        lli     t0, Action.Jab1
        beq     a1, t0, _jab
        lli     t0, Action.Jab2
        beq     a1, t0, _jab
        lli     t0, Action.DashAttack
        beq     a1, t0, _dash
        sltiu   t1, a1, Action.FTiltHigh
        bnez    t1, _none
        sltiu   t1, a1, Action.FTiltLow + 1
        bnez    t1, _ftilt
        lli     t0, Action.UTilt
        beq     a1, t0, _utilt
        lli     t0, Action.DTilt
        beq     a1, t0, _dtilt
        sltiu   t1, a1, Action.FSmashHigh
        bnez    t1, _none
        sltiu   t1, a1, Action.FSmashLow + 1
        bnez    t1, _fsmash
        lli     t0, Action.USmash
        beq     a1, t0, _usmash
        lli     t0, Action.DSmash
        beq     a1, t0, _dsmash
        lli     t0, Action.AttackAirN
        beq     a1, t0, _nair
        lli     t0, Action.AttackAirF
        beq     a1, t0, _fair
        lli     t0, Action.AttackAirB
        beq     a1, t0, _bair
        lli     t0, Action.AttackAirU
        beq     a1, t0, _uair
        lli     t0, Action.AttackAirD
        beq     a1, t0, _dair
        lli     t0, Action.LandingAirN
        beq     a1, t0, _nair
        lli     t0, Action.LandingAirF
        beq     a1, t0, _fair
        lli     t0, Action.LandingAirB
        beq     a1, t0, _bair
        lli     t0, Action.LandingAirU
        beq     a1, t0, _uair
        lli     t0, Action.LandingAirD
        beq     a1, t0, _dair
        nop
        b       _none
        nop

        _jab:;    lli t2, FIELD_JAB
        b _resolve; nop
        _dash:;   lli t2, FIELD_DASH
        b _resolve; nop
        _ftilt:;  lli t2, FIELD_FTILT
        b _resolve; nop
        _utilt:;  lli t2, FIELD_UTILT
        b _resolve; nop
        _dtilt:;  lli t2, FIELD_DTILT
        b _resolve; nop
        _fsmash:; lli t2, FIELD_FSMASH
        b _resolve; nop
        _usmash:; lli t2, FIELD_USMASH
        b _resolve; nop
        _dsmash:; lli t2, FIELD_DSMASH
        b _resolve; nop
        _nair:;   lli t2, FIELD_NAIR
        b _resolve; nop
        _fair:;   lli t2, FIELD_FAIR
        b _resolve; nop
        _bair:;   lli t2, FIELD_BAIR
        b _resolve; nop
        _uair:;   lli t2, FIELD_UAIR
        b _resolve; nop
        _dair:;   lli t2, FIELD_DAIR

        _resolve:
        lw      v0, 0x0010(sp)
        sll     t2, t2, 0x0002
        addu    t0, v0, t2
        lw      t0, 0x0000(t0)
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        b       _end
        nop

        _wrong_body:
        lw      t0, 0x0008(sp)
        lbu     t0, 0x000D(t0)
        li      t1, status_by_port
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lli     t0, 0x0001                 // configured body mismatch
        sw      t0, 0x0000(t1)
        _none:
        addiu   v0, r0, -0x0001
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // @ Description
    // Returns donor moveset file base in v0. Loads it into the normal heap on
    // first use. a0 = port, a1 = donor ID, a2 = donor character struct.
    scope get_moveset_base_: {
        addiu   sp, sp, -0x0030
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        sw      a1, 0x000C(sp)
        sw      a2, 0x0010(sp)

        _scan:
        lw      a0, 0x0008(sp)
        lw      a1, 0x000C(sp)
        sll     t0, a0, 0x0003             // port * 8 ids
        li      t1, cache_ids
        addu    t1, t1, t0
        lli     t2, CACHE_SLOTS
        lli     t3, 0x00FF                  // empty cache ID marker
        or      t4, r0, r0                 // cache index
        addiu   t5, r0, -0x0001            // first empty index
        _scan_loop:
        lbu     t6, 0x0000(t1)
        beq     t6, a1, _found
        nop
        bnel    t6, t3, _scan_next
        nop
        bgez    t5, _scan_next
        or      t5, t4, r0
        _scan_next:
        addiu   t1, t1, 0x0001
        addiu   t4, t4, 0x0001
        addiu   t2, t2, -0x0001
        bnez    t2, _scan_loop
        nop
        bltz    t5, _fail
        nop

        // Store ID, then let Render.load_file_ write the pointer directly to
        // this cache slot.
        sll     t0, a0, 0x0003
        addu    t0, t0, t5
        li      t1, cache_ids
        addu    t1, t1, t0
        sb      a1, 0x0000(t1)
        sll     t0, t0, 0x0002
        li      a1, cache_pointers
        addu    a1, a1, t0
        sw      a1, 0x0018(sp)
        lw      t0, 0x0010(sp)
        lw      a0, 0x0004(t0)             // donor file 2 ID
        beqz    a0, _fail
        nop
        jal     Render.load_file_
        nop
        lw      t0, 0x0018(sp)
        lw      v0, 0x0000(t0)
        b       _publish
        nop

        _found:
        lw      a0, 0x0008(sp)
        sll     t0, a0, 0x0003
        addu    t0, t0, t4
        sll     t0, t0, 0x0002
        li      t1, cache_pointers
        addu    t1, t1, t0
        lw      v0, 0x0000(t1)

        // A number of stock character callbacks bypass the command-address
        // hook and read *FTData.p_file_mainmotion directly. Keep that stock
        // destination synchronized with the private per-port cache.
        _publish:
        beqz    v0, _end
        lw      t0, 0x0010(sp)
        lw      t1, 0x002C(t0)             // FTData.p_file_mainmotion
        beqz    t1, _end
        nop
        sw      v0, 0x0000(t1)
        b       _end
        nop

        _fail:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0030
        jr      ra
        nop
    }

    // @ Description
    // Loads the selected recipes' donor moveset files during the engine's
    // pre-match character-loading phase. Loading one lazily from
    // ftMainSetStatus can re-enter the file/heap managers while an action is
    // being installed, which is unsafe and can lock the game on the first
    // borrowed attack. The character loader calls this once before loading a
    // normal match, or after reserving the alternate heaps for Tag Team.
    scope preload_selected_builds_: {
        addiu   sp, sp, -0x0040
        sw      ra, 0x0004(sp)
        sw      s0, 0x0008(sp)
        sw      s1, 0x000C(sp)
        sw      s2, 0x0010(sp)
        sw      s3, 0x0014(sp)
        sw      s4, 0x0018(sp)
        sw      s5, 0x001C(sp)

        li      t0, diagnostic_preload_calls
        lw      t1, 0x0000(t0)
        addiu   t1, t1, 0x0001
        sw      t1, 0x0000(t0)
        li      t0, selected_builds
        lw      t1, 0x0000(t0)
        li      t0, diagnostic_preload_selected
        sw      t1, 0x0000(t0)

        jal     reset_cache_
        nop
        or      s0, r0, r0                 // port

        _port_loop:
        jal     get_slot_
        or      a0, s0, r0
        beqz    v0, _next_port
        or      s1, v0, r0                 // selected slot entry table

        // Cache the configured body ID so its already-loaded moveset is not
        // needlessly loaded a second time.
        lw      t0, 0x0004(s1)
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        or      s2, v0, r0                 // body Character.id
        lli     s3, FIELD_JAB               // first donor field

        _field_loop:
        sltiu t0, s3, FIELD_GRAB
        beqz t0, _next_field
        sltiu t0, s2, 12
        beqz t0, _legacy_field
        sltiu t0, s3, FIELD_NSP
        bnez t0, _next_field // Original normal/grab tables need no donor cache.
        nop
        _legacy_field:
        lli     t1, FIELD_NSP
        beq     s3, t1, _fox_nsp
        nop
        sll     t0, s3, 0x0002
        addu    t0, s1, t0
        lw      t0, 0x0000(t0)
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        or      s4, v0, r0                 // donor Character.id
        b       _donor_ready
        nop

        _fox_nsp:
        lw t0, FIELD_NSP * 4(s1)
        lw t0, 0x0000(t0)
        beqz t0, _next_field
        nop
        // Neutral-B owns only Fox's projectile attributes. Loading Fox's
        // complete main/special bundle wastes heap space and leaves the stock
        // constructor dependent on shared globals that later loaders mutate.
        jal     ensure_laser_file_
        nop
        b       _next_field
        nop

        _donor_ready:
        beq     s4, s2, _next_field
        nop

        li      t0, 0x80116E10             // character struct pointer table
        sll     t1, s4, 0x0002
        addu    t0, t0, t1
        lw      s5, 0x0000(t0)
        beqz    s5, _next_field
        nop
        or      a0, s0, r0
        or      a1, s4, r0
        jal     get_moveset_base_
        or      a2, s5, r0
        beqz    v0, _next_field
        nop

        // Load special animation/main data and declared projectile/effect
        // dependencies in the pre-match phase. Doing this from the first
        // button press can re-enter the active match's heap manager.
        sltiu   t0, s3, FIELD_NSP
        bnez    t0, _next_field
        nop
        or      a0, s4, r0
        jal     ensure_main_file_
        or      a1, s5, r0
        beqz    v0, _next_field
        nop
        or      a0, s4, r0
        jal     ensure_special_files_
        or      a1, s5, r0
        beqz    v0, _next_field
        nop
        or      a0, s0, r0
        jal     ensure_special_animation_heap_
        or      a1, s5, r0
        li      t0, diagnostic_preload_heap
        sw      v0, 0x0000(t0)
        // Projectile/effect dependencies are independent of the animation
        // buffer. Keep preloading them when a separate buffer cannot be
        // reserved; the dispatcher can safely reuse the body's heap whenever
        // it is large enough for this donor.
        jal     ensure_special_preloads_
        or      a0, s4, r0

        _next_field:
        addiu   s3, s3, 0x0001
        sltiu   t0, s3, FIELD_COUNT
        bnez    t0, _field_loop
        nop

        _next_port:
        addiu   s0, s0, 0x0001
        sltiu   t0, s0, 0x0004
        bnez    t0, _port_loop
        nop

        lw      ra, 0x0004(sp)
        lw      s0, 0x0008(sp)
        lw      s1, 0x000C(sp)
        lw      s2, 0x0010(sp)
        lw      s3, 0x0014(sp)
        lw      s4, 0x0018(sp)
        lw      s5, 0x001C(sp)
        addiu   sp, sp, 0x0040
        jr      ra
        nop
    }

    // @ Description
    // Loads the four special-resource slots declared by a donor FTData into
    // the exact globals its callbacks and weapon descriptors dereference.
    // This must run during the pre-match load, after reset_cache_; stale global
    // pointers from a previous screen cannot be trusted after a heap reset.
    // a0 = donor Character.id, a1 = donor FTData pointer.
    // Returns v0 = 1 on success, or 0 for an invalid donor record.
    scope ensure_special_files_: {
        addiu   sp, sp, -0x0030
        sw      ra, 0x0004(sp)
        sw      s0, 0x0008(sp)
        sw      s1, 0x000C(sp)
        sw      a0, 0x0010(sp)
        or      s1, a1, r0
        beqz    s1, _fail
        sltiu   t0, a0, 0x0080
        beqz    t0, _fail
        nop

        srl     t0, a0, 0x0005
        sll     t0, t0, 0x0002
        li      t1, loaded_special_files
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        andi    t3, a0, 0x001F
        lli     t4, 0x0001
        sllv    t4, t4, t3
        and     t5, t2, t4
        bnez    t5, _success
        sw      t1, 0x0014(sp)
        sw      t4, 0x0018(sp)

        or      s0, r0, r0                 // special slot 0-3
        _slot_loop:
        sll     t0, s0, 0x0002
        addu    t1, s1, t0
        lw      a0, 0x0014(t1)             // file_specialN_id
        beqz    a0, _next_slot
        lw      a1, 0x003C(t1)             // p_file_specialN
        beqz    a1, _fail                  // malformed FTData must fail closed
        nop
        jal     Render.load_file_
        nop
        // Render.load_file_ stores the resulting file base through a1.
        // A null result means the donor context is not safe to activate.
        sll     t0, s0, 0x0002
        addu    t1, s1, t0
        lw      t1, 0x003C(t1)
        lw      t1, 0x0000(t1)
        beqz    t1, _fail
        nop
        _next_slot:
        addiu   s0, s0, 0x0001
        sltiu   t0, s0, 0x0004
        bnez    t0, _slot_loop
        nop

        lw      t1, 0x0014(sp)
        lw      t2, 0x0000(t1)
        lw      t4, 0x0018(sp)
        or      t2, t2, t4
        sw      t2, 0x0000(t1)
        _success:
        b       _end
        lli     v0, 0x0001
        _fail:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0004(sp)
        lw      s0, 0x0008(sp)
        lw      s1, 0x000C(sp)
        addiu   sp, sp, 0x0030
        jr      ra
        nop
    }

    // @ Description
    // Reserves a per-port animation buffer large enough for every configured
    // special donor. This is deliberately called only by the pre-match loader;
    // ftMainSetStatus must never resize the heap on the first B press.
    // a0 = port, a1 = donor FTData pointer. Returns v0 = buffer or 0.
    scope ensure_special_animation_heap_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        sltiu   t0, a0, SLOT_COUNT
        beqz    t0, _fail
        nop
        beqz    a1, _fail
        nop
        lw      t2, 0x0074(a1)             // FTData.file_anim_size
        beqz    t2, _fail
        sw      t2, 0x000C(sp)
        sll     t0, a0, 0x0002
        li      t1, special_animation_heap_size
        addu    t1, t1, t0
        lw      t3, 0x0000(t1)
        sltu    t4, t3, t2
        bnez    t4, _allocate
        li      t1, special_animation_heap
        addu    t1, t1, t0
        lw      v0, 0x0000(t1)
        bnez    v0, _end
        nop

        _allocate:
        or      a0, t2, r0
        jal     0x80004980                 // syTaskmanMalloc
        lli     a1, 0x0010
        beqz    v0, _fail
        lw      t0, 0x0008(sp)
        sll     t0, t0, 0x0002
        li      t1, special_animation_heap
        addu    t1, t1, t0
        sw      v0, 0x0000(t1)
        li      t1, special_animation_heap_size
        addu    t1, t1, t0
        lw      t2, 0x000C(sp)
        sw      t2, 0x0000(t1)
        b       _end
        nop
        _fail:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // @ Description
    // Makes every legal fighter-joint index dereferenceable for donor code
    // while preserving the selected body's real skeleton.
    // a0 = player struct
    scope install_joint_fallbacks_: {
        lbu     t0, 0x000D(a0)             // port
        sll     t1, t0, 0x0007             // port * 128
        sll     t2, t0, 0x0004             // port * 16
        addu    t1, t1, t2
        sll     t2, t0, 0x0002             // port * 4
        addu    t1, t1, t2                 // port * 148
        li      t2, special_joint_backups
        addu    t2, t2, t1
        addiu   t3, a0, 0x08E8             // fp->joints[0]
        lw      t4, 0x0000(t3)             // body's top joint
        lli     t5, 37
        _loop:
        lw      t6, 0x0000(t3)
        sw      t6, 0x0000(t2)
        bnez    t6, _next
        nop
        sw      t4, 0x0000(t3)
        _next:
        addiu   t3, t3, 0x0004
        addiu   t2, t2, 0x0004
        addiu   t5, t5, -0x0001
        bnez    t5, _loop
        nop
        jr      ra
        nop
    }

    // @ Description
    // Reverses install_joint_fallbacks_ before a shared/body action begins.
    // a0 = player struct
    scope restore_joint_fallbacks_: {
        lbu     t0, 0x000D(a0)             // port
        sll     t1, t0, 0x0007
        sll     t2, t0, 0x0004
        addu    t1, t1, t2
        sll     t2, t0, 0x0002
        addu    t1, t1, t2                 // port * 148
        li      t2, special_joint_backups
        addu    t2, t2, t1
        addiu   t3, a0, 0x08E8
        lli     t5, 37
        _loop:
        lw      t6, 0x0000(t2)
        sw      t6, 0x0000(t3)
        addiu   t3, t3, 0x0004
        addiu   t2, t2, 0x0004
        addiu   t5, t5, -0x0001
        bnez    t5, _loop
        nop
        jr      ra
        nop
    }

    // @ Description
    // Preloads the extra files a donor declares for Tag Team. These are the
    // same projectile/item dependencies that otherwise disappear when a
    // character is not one of the fighters loaded for the match.
    // a0 = donor Character.id
    scope ensure_special_preloads_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        sltiu   t0, a0, 0x0080
        beqz    t0, _end
        nop

        srl     t0, a0, 0x0005
        sll     t0, t0, 0x0002
        li      t1, preloaded_specials
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        andi    t3, a0, 0x001F
        lli     t4, 0x0001
        sllv    t4, t4, t3
        and     t5, t2, t4
        bnez    t5, _end
        or      t2, t2, t4
        sw      t2, 0x0000(t1)

        li      t0, TagTeam.preload_map
        sll     t1, a0, 0x0002
        addu    t0, t0, t1
        lw      t0, 0x0000(t0)
        beqz    t0, _end
        nop
        _load_loop:
        lhu     a0, 0x0000(t0)
        beqz    a0, _end
        sw      t0, 0x000C(sp)
        jal     Render.load_file_
        li      a1, preload_pointer
        lw      t0, 0x000C(sp)
        b       _load_loop
        addiu   t0, t0, 0x0002

        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // @ Description
    // Ensures the donor's primary animation/main file is available through
    // the pointer address in its character struct. Unique action parameters
    // can refer to this file even when the donor is not otherwise in the match.
    // a0 = donor Character.id, a1 = donor character struct.
    // Returns v0 = file base, or 0 on failure.
    scope ensure_main_file_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        sw      a1, 0x000C(sp)
        sltiu   t0, a0, 0x0080
        beqz    t0, _fail
        nop

        srl     t0, a0, 0x0005
        sll     t0, t0, 0x0002
        li      t1, loaded_main_files
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        andi    t3, a0, 0x001F
        lli     t4, 0x0001
        sllv    t4, t4, t3
        and     t5, t2, t4
        sw      t1, 0x0010(sp)
        sw      t4, 0x0014(sp)

        lw      t0, 0x0028(a1)
        beqz    t0, _fail
        sw      t0, 0x0018(sp)
        bnez    t5, _publish_cached
        nop
        lw      a0, 0x0000(a1)
        beqz    a0, _fail
        or      a1, t0, r0
        jal     Render.load_file_
        nop
        lw      t0, 0x0018(sp)
        lw      v0, 0x0000(t0)
        beqz    v0, _fail
        lw      t6, 0x0008(sp)
        sll     t6, t6, 0x0002
        li      t7, main_file_pointers
        addu    t7, t7, t6
        sw      v0, 0x0000(t7)
        lw      t1, 0x0010(sp)
        lw      t2, 0x0000(t1)
        lw      t4, 0x0014(sp)
        or      t2, t2, t4
        sw      t2, 0x0000(t1)

        b       _end
        nop

        _publish_cached:
        lw      t6, 0x0008(sp)
        sll     t6, t6, 0x0002
        li      t7, main_file_pointers
        addu    t7, t7, t6
        lw      v0, 0x0000(t7)
        beqz    v0, _fail
        lw      t0, 0x0018(sp)
        sw      v0, 0x0000(t0)
        b       _end
        nop
        _fail:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // The six engine hooks have five instructions available before VsStats
    // patches the following instruction. Keep the hooks compact and finish
    // loading the field/table arguments here so no JAL lands in another JAL's
    // delay slot.
    scope get_air_nsp_routine_: {
        lli     a1, FIELD_NSP
        li      a2, Character.air_nsp.table
        j       get_special_routine_
        nop
    }

    scope get_air_usp_routine_: {
        lli     a1, FIELD_USP
        li      a2, Character.air_usp.table
        j       get_special_routine_
        nop
    }

    scope get_air_dsp_routine_: {
        lli     a1, FIELD_DSP
        li      a2, Character.air_dsp.table
        j       get_special_routine_
        nop
    }

    scope get_ground_nsp_routine_: {
        lli     a1, FIELD_NSP
        li      a2, Character.ground_nsp.table
        j       get_special_routine_
        nop
    }

    scope get_ground_usp_routine_: {
        lli     a1, FIELD_USP
        li      a2, Character.ground_usp.table
        j       get_special_routine_
        nop
    }

    scope get_ground_dsp_routine_: {
        lli     a1, FIELD_DSP
        li      a2, Character.ground_dsp.table
        j       get_special_routine_
        nop
    }

    // @ Description
    // Resolves one of the six special-entry tables through the active recipe.
    // a0 = player object, a1 = recipe field, a2 = special routine table.
    // Returns the selected entry routine in t9 and restores a0 for the caller.
    scope get_special_routine_: {
        // Establish donor execution/resource ownership before returning the
        // selected special entry routine. Every failure path falls back to the
        // body's table without exposing a partial donor context.
        addiu   sp, sp, -0x0030
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        sw      a1, 0x000C(sp)
        sw      a2, 0x0010(sp)
        lw      t0, 0x0084(a0)             // player struct
        beqz    t0, _no_player
        sw      t0, 0x0014(sp)
        lbu     a0, 0x000D(t0)             // port
        jal     get_slot_
        sw      a0, 0x0018(sp)
        // Starting any special ends ownership retained by Jab/rapid-jab.
        lw      t0, 0x0018(sp)
        li      t1, active_normal_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        addiu   t0, r0, -0x0001
        sw      t0, 0x0000(t1)
        beqz    v0, _body
        sw      v0, 0x001C(sp)

        // Enforce the configured body before borrowing any executable code.
        lw      t0, 0x0004(v0)
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        lw      t0, 0x0014(sp)
        lw      t1, 0x0008(t0)
        bne     v0, t1, _wrong_body
        sw      t1, 0x0020(sp)

        lw      t0, 0x001C(sp)
        lw      t1, 0x000C(sp)
        lli     t2, FIELD_NSP
        beq     t1, t2, _neutral_choice
        sll     t1, t1, 0x0002
        addu    t0, t0, t1
        lw      t0, 0x0000(t0)
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        lw      t1, 0x0020(sp)
        beq     v0, t1, _body              // choosing the body is stock behavior
        sw      v0, 0x0024(sp)

        li      t0, 0x80116E10
        sll     t1, v0, 0x0002
        addu    t0, t0, t1
        lw      a2, 0x0000(t0)
        beqz    a2, _body
        sw      a2, 0x0028(sp)
        lw      a0, 0x0018(sp)
        lw      a2, 0x0028(sp)
        jal     get_moveset_base_
        lw      a1, 0x0024(sp)
        beqz    v0, _body
        nop
        lw      a0, 0x0024(sp)
        jal     ensure_main_file_
        lw      a1, 0x0028(sp)
        beqz    v0, _body
        nop
        lw      a0, 0x0024(sp)
        jal     ensure_special_files_
        lw      a1, 0x0028(sp)
        beqz    v0, _body
        nop
        lw      t0, 0x0018(sp)
        sll     t0, t0, 0x0002
        li      t1, special_animation_heap
        addu    t1, t1, t0
        lw      t1, 0x0000(t1)
        bnez    t1, _animation_heap_ready
        sw      t1, 0x002C(sp)

        // A separate pre-match animation allocation can fail when Training's
        // task heap is already committed to fighter files. Reuse the body's
        // existing figatree heap only when its declared capacity is at least
        // as large as the donor's. This is safe for combinations such as
        // Mario body + Fox special (0x1850 >= 0x1320); larger donors continue
        // to fail closed to the body routine.
        lw      t2, 0x0028(sp)             // donor FTData
        lw      t3, 0x0074(t2)             // donor file_anim_size
        beqz    t3, _body
        lw      t0, 0x0014(sp)             // player struct
        lw      t2, 0x09C4(t0)             // body FTData
        beqz    t2, _body
        nop
        lw      t2, 0x0074(t2)             // body file_anim_size
        sltu    t3, t2, t3                 // body capacity < donor requirement
        bnez    t3, _body
        nop
        lw      t1, 0x09D0(t0)             // body's figatree heap
        beqz    t1, _body
        sw      t1, 0x002C(sp)

        _animation_heap_ready:
        nop
        jal     ensure_special_preloads_
        lw      a0, 0x0024(sp)

        lw      t0, 0x0018(sp)
        li      t1, active_special_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      t2, 0x0024(sp)
        sw      t2, 0x0000(t1)

        // Donor callbacks read fp->data directly. Save the body FTData once,
        // then expose the donor FTData for this special and all of its unique
        // follow-up actions. The shared-action restore path reverses this.
        lw      t0, 0x0014(sp)             // player struct
        lw      t1, 0x0018(sp)             // port
        sll     t1, t1, 0x0002
        li      t3, body_character_data
        addu    t3, t3, t1
        lw      t4, 0x0000(t3)
        bnez    t4, _context_saved
        nop
        lw      t4, 0x09C4(t0)             // body FTData
        sw      t4, 0x0000(t3)
        li      t3, body_character_id
        addu    t3, t3, t1
        lw      t4, 0x0008(t0)             // body Character.id / fkind
        sw      t4, 0x0000(t3)
        li      t3, body_animation_heap
        addu    t3, t3, t1
        lw      t4, 0x09D0(t0)             // body figatree_heap
        sw      t4, 0x0000(t3)
        jal     install_joint_fallbacks_
        or      a0, t0, r0
        _context_saved:
        lw      t0, 0x0014(sp)             // restore after helper call
        lw      t1, 0x0018(sp)
        sll     t1, t1, 0x0002
        lw      t4, 0x0028(sp)             // donor FTData
        sw      t4, 0x09C4(t0)
        lw      t4, 0x0024(sp)             // donor Character.id / fkind
        sw      t4, 0x0008(t0)
        lw      t4, 0x002C(sp)             // dedicated or compatible body heap
        sw      t4, 0x09D0(t0)
        b       _lookup
        nop

        _wrong_body:
        lw      t0, 0x0018(sp)
        li      t1, status_by_port
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lli     t0, 0x0001
        sw      t0, 0x0000(t1)
        _body:
        lw      t2, 0x0014(sp)
        lw      t2, 0x0008(t2)
        lw      t0, 0x0018(sp)
        li      t1, active_special_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        addiu   t0, r0, -0x0001
        sw      t0, 0x0000(t1)

        _lookup:
        // Do not carry t2 (the selected Character.id) across helper calls.
        // install_joint_fallbacks_ and the resource loaders are free to clobber
        // caller-saved registers. Using that stale value here indexed the
        // special routine table with garbage on the first borrowed special and
        // jumped to an invalid address. fp->fkind is authoritative: it is the
        // donor while adapted context is active and the body otherwise.
        lw      t2, 0x0014(sp)             // fighter struct
        lw      t2, 0x0008(t2)             // active Character.id / fkind
        lw      t0, 0x0010(sp)
        sll     t1, t2, 0x0002
        addu    t0, t0, t1
        lw      t9, 0x0000(t0)
        bnez    t9, _end
        nop
        // A missing donor table entry is not callable. Revert atomically to
        // the body's routine and ownership state.
        lw      t2, 0x0020(sp)             // saved body Character.id
        lw      t0, 0x0010(sp)
        sll     t1, t2, 0x0002
        addu    t0, t0, t1
        lw      t9, 0x0000(t0)
        lw      t0, 0x0018(sp)
        li      t1, active_special_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        addiu   t0, r0, -0x0001
        sw      t0, 0x0000(t1)
        // If donor context was already exposed, put the body's FTData back
        // before dispatching its fallback routine.
        lw      t0, 0x0018(sp)
        sll     t0, t0, 0x0002
        li      t1, body_character_data
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        beqz    t2, _end
        lw      t0, 0x0014(sp)
        jal     restore_joint_fallbacks_
        or      a0, t0, r0
        lw      t0, 0x0014(sp)
        lw      t5, 0x0018(sp)
        sll     t5, t5, 0x0002
        li      t1, body_character_data
        addu    t1, t1, t5
        lw      t2, 0x0000(t1)
        sw      t2, 0x09C4(t0)
        sw      r0, 0x0000(t1)
        li      t1, body_character_id
        addu    t1, t1, t5
        lw      t2, 0x0000(t1)
        sw      t2, 0x0008(t0)
        addiu   t2, r0, -0x0001
        sw      t2, 0x0000(t1)
        li      t1, body_animation_heap
        addu    t1, t1, t5
        lw      t2, 0x0000(t1)
        sw      t2, 0x09D0(t0)
        sw      r0, 0x0000(t1)
        b       _end
        nop

        _no_player:
        or      t9, r0, r0
        b _end
        nop
        _neutral_choice:
        lw t0, FIELD_NSP * 4(t0)
        lw t0, 0x0000(t0)
        beqz t0, _body
        lw t1, 0x0020(sp)
        sltiu t2, t1, 12
        beqz t2, _body
        lli t2, Character.id.FOX
        beq t1, t2, _body
        nop
        lui t9, CharLabRuntime.ccNeutral >> 16
        ori t9, t9, CharLabRuntime.ccNeutral & 0xFFFF
        _end:
        lw      a0, 0x0008(sp)
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0030
        jr      ra
        nop
    }

    // @ Description
    // Loads Fox's laser attribute file into a Character Creator-owned pointer.
    // This runs only in the pre-match load phase; Neutral-B never allocates.
    // Returns v0 = file base, or 0 when the resource could not be established.
    scope ensure_laser_file_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        li      t0, laser_file_pointer
        lw      v0, 0x0000(t0)
        bnez    v0, _end
        nop

        li      t0, 0x80116E10             // character struct pointer table
        lli     t1, Character.id.FOX
        sll     t1, t1, 0x0002
        addu    t0, t0, t1
        lw      t0, 0x0000(t0)             // Fox FTData
        beqz    t0, _fail
        nop
        lw      a0, 0x0014(t0)             // Fox file_special1 (laser attributes)
        beqz    a0, _fail
        li      a1, laser_file_pointer
        sw      r0, 0x0000(a1)             // never accept a stale scene pointer
        jal     Render.load_file_
        nop
        li      t0, laser_file_pointer
        lw      v0, 0x0000(t0)
        beqz    v0, _fail
        li      t1, diagnostic_laser_resource
        sw      v0, 0x0000(t1)
        b       _end
        nop

        _fail:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // Neutral-B intentionally does not borrow Fox's fighter state. The body
    // owns its native neutral action and animation; when that script raises
    // flag0, these hooks consume it and construct Fox's laser directly.
    scope neutral_is_custom_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        lw      t0, 0x0084(a0)             // fighter struct
        beqz    t0, _no
        sw      t0, 0x000C(sp)
        lw      t1, 0x0288(t0)             // motion_attack_id (0x28C is motion_count)
        lw t2, 0x0008(t0)
        sltiu t2, t2, 12
        bnez t2, _no // The shared adapter owns original-body laser callbacks.
        nop
        lli     t2, 0x0012                 // nFTMotionAttackIDSpecialN
        bne     t1, t2, _no
        lbu     a0, 0x000D(t0)             // port
        jal     get_slot_
        nop
        beqz    v0, _no
        nop
        lw t0, FIELD_NSP * 4(v0)
        lw t0, 0x0000(t0)
        beqz t0, _no
        nop
        lw      t0, 0x0004(v0)             // configured body entry
        jal     catalog_id_
        lw      a0, 0x0000(t0)
        lw      t0, 0x000C(sp)
        lw      t1, 0x0008(t0)             // actual body Character.id
        bne     v0, t1, _no
        nop
        b       _end
        lli     v0, 0x0001
        _no:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // a0 = fighter GObj. Returns v0 = 1 when this is a custom Neutral-B,
    // whether or not its projectile flag was raised on this frame.
    scope neutral_try_spawn_: {
        addiu   sp, sp, -0x0030
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        jal     neutral_is_custom_
        nop
        beqz    v0, _end
        sw      v0, 0x000C(sp)
        lw      a0, 0x0008(sp)
        lw      t0, 0x0084(a0)             // fighter struct
        lw      t1, 0x017C(t0)             // motion_vars.flags.flag0
        beqz    t1, _end
        nop
        sw      r0, 0x017C(t0)             // consume before spawning
        lw      t1, 0x08E8(t0)             // TopN joint
        beqz    t1, _end
        nop
        lwc1    f0, 0x001C(t1)             // world X
        lwc1    f2, 0x0020(t1)             // world Y
        lwc1    f4, 0x0024(t1)             // world Z
        lw      t2, 0x0044(t0)             // facing direction
        mtc1    t2, f6
        cvt.s.w f6, f6
        lui     t2, 0x4270                 // 60.0F
        mtc1    t2, f8
        mul.s   f6, f6, f8
        add.s   f0, f0, f6
        lui     t2, 0x42A0                 // 80.0F
        mtc1    t2, f8
        add.s   f2, f2, f8
        swc1    f0, 0x0010(sp)
        swc1    f2, 0x0014(sp)
        swc1    f4, 0x0018(sp)
        addiu   a1, sp, 0x0010
        jal     neutral_make_weapon_
        nop
        _end:
        lw      v0, 0x000C(sp)
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0030
        jr      ra
        nop
    }

    // @ Description
    // Creates a stock-behaving Fox laser without entering Remix's patched
    // wpFoxBlasterMakeWeapon. The descriptor uses a private, match-lifetime
    // resource pointer and the same callback block as the stock projectile.
    // a0 = fighter GObj, a1 = spawn position. Returns v0 = weapon GObj or 0.
    scope neutral_make_weapon_: {
        addiu   sp, sp, -0x0030
        sw      ra, 0x0014(sp)
        sw      a0, 0x0020(sp)
        sw      a1, 0x0024(sp)

        li      t0, diagnostic_laser_stage
        lli     t1, 0x0001
        sw      t1, 0x0000(t0)
        li      t0, laser_file_pointer
        lw      t1, 0x0000(t0)
        li      t0, diagnostic_laser_resource
        sw      t1, 0x0000(t0)
        beqz    t1, _fail                  // missing resource fails closed
        nop

        li      t0, diagnostic_laser_stage
        lli     t1, 0x0002
        sw      t1, 0x0000(t0)
        lw      a0, 0x0020(sp)
        li      a1, laser_projectile_struct
        lw      a2, 0x0024(sp)
        jal     0x801655C8                 // generic weapon creation
        lui     a3, 0x8000                 // parent is a fighter
        li      t0, diagnostic_laser_weapon
        sw      v0, 0x0000(t0)
        beqz    v0, _fail
        sw      v0, 0x0018(sp)

        lw      v1, 0x0084(v0)             // weapon struct
        beqz    v1, _fail
        lui     at, 0x4320                 // Fox laser speed: 160.0F
        mtc1    at, f8
        lwc1    f12, 0x0024(v1)            // Y velocity
        lw      t0, 0x0018(v1)             // projectile direction
        mtc1    t0, f6
        cvt.s.w f6, f6
        mul.s   f14, f6, f8
        swc1    f14, 0x0020(v1)            // X velocity
        jal     0x8001863C                 // atan2(Y, X)
        nop

        lw      t7, 0x0018(sp)
        lw      t8, 0x0074(t7)             // projectile DObj
        beqz    t8, _effect
        nop
        swc1    f0, 0x0038(t8)             // face along velocity

        _effect:
        jal     0x80103320                 // Fox laser muzzle/glow effect
        lw      a0, 0x0024(sp)
        li      t0, diagnostic_laser_stage
        lli     t1, 0x0003
        sw      t1, 0x0000(t0)
        b       _end
        lw      v0, 0x0018(sp)

        _fail:
        or      v0, r0, r0
        _end:
        lw      ra, 0x0014(sp)
        addiu   sp, sp, 0x0030
        jr      ra
        nop
    }

    OS.align(16)
    laser_projectile_struct:
    dw 0x00000000                        // render flags
    dw 0x00000001                        // nWPKindBlaster
    dw laser_file_pointer                // private loaded Fox Special1 file
    OS.copy_segment(0x10391C, 0x28)      // stock attributes offset + callbacks

    // Replaces the stock proc_accessory indirect calls. A custom Neutral-B
    // consumes flag0 above and skips the body's projectile callback; every
    // other action tail-calls the original callback unchanged.
    scope neutral_accessory_dispatch_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      v0, 0x0008(sp)             // original proc_accessory
        sw      a0, 0x000C(sp)
        jal     neutral_try_spawn_
        nop
        beqz    v0, _original
        nop
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra                         // suppress body projectile callback
        nop
        _original:
        lw      t9, 0x0008(sp)
        lw      a0, 0x000C(sp)
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      t9
        nop
    }

    OS.patch_start(0x5D8B8, 0x800E20B8)
    jal     neutral_accessory_dispatch_
    OS.patch_end()

    OS.patch_start(0x62784, 0x800E6F84)
    jal     neutral_accessory_dispatch_
    OS.patch_end()

    // Character.move_action_array_table_ jumps here. Substitute the donor's
    // unique action array only while a borrowed special owns the action chain.
    scope action_array_hook_: {
        addiu   t0, v0, 0xFF24             // original instruction
        lbu     t8, 0x000D(s1)
        li      t9, active_special_donor
        sll     t8, t8, 0x0002
        addu    t9, t9, t8
        lw      t8, 0x0000(t9)
        bgez    t8, _selected
        nop
        li      t9, active_normal_donor
        lbu     t8, 0x000D(s1)
        sll     t8, t8, 0x0002
        addu    t9, t9, t8
        lw      t8, 0x0000(t9)
        bltz    t8, _body
        nop
        _selected:
        or      t7, t8, r0
        _body:
        li      t9, Character.ACTION_ARRAY_TABLE
        sll     t8, t7, 0x0002
        addu    t9, t9, t8
        lw      t9, 0x0000(t9)
        li      at, diagnostic_action_array
        sw      t9, 0x0000(at)
        sw      t0, 0x0004(at)
        sw      t0, 0x0074(sp)             // original: unique action index
        j       0x800E73E8
        nop
    }

    // Character.move_parameter_base_ jumps here during unique-action setup.
    scope parameter_base_hook_: {
        // If a donor special is returning to the shared action set, restore
        // the body's FTData before ftMainSetStatus selects the next animation
        // and command descriptor. The later action-change callback is too late
        // for this particular decision.
        lbu     t6, 0x000D(s1)
        sll     t6, t6, 0x0002
        li      t7, body_character_data
        addu    t7, t7, t6
        lw      t8, 0x0000(t7)
        beqz    t8, _load_current
        lw      t9, 0x0024(s1)
        sltiu   t9, t9, 0x00DC
        beqz    t9, _load_current           // unique donor follow-up
        nop
        OS.save_registers()
        or      a0, s1, r0
        lw      a1, 0x0024(s1)
        jal     CharLab.keep_bomb_context_
        nop
        beqz    v0, _restore_common
        nop
        OS.restore_registers()
        b       _load_current
        nop
        _restore_common:
        OS.restore_registers()
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        sw      t6, 0x0008(sp)
        sw      t8, 0x000C(sp)
        sw      a0, 0x0010(sp)
        jal     restore_joint_fallbacks_
        or      a0, s1, r0
        lw      ra, 0x0004(sp)
        lw      t6, 0x0008(sp)
        lw      t8, 0x000C(sp)
        lw      a0, 0x0010(sp)
        addiu   sp, sp, 0x0020
        li      t7, body_character_data
        addu    t7, t7, t6
        sw      t8, 0x09C4(s1)
        sw      r0, 0x0000(t7)
        li      t7, body_character_id
        addu    t7, t7, t6
        lw      t8, 0x0000(t7)
        sw      t8, 0x0008(s1)
        addiu   t8, r0, -0x0001
        sw      t8, 0x0000(t7)
        li      t7, body_animation_heap
        addu    t7, t7, t6
        lw      t8, 0x0000(t7)
        sw      t8, 0x09D0(s1)
        sw      r0, 0x0000(t7)
        li      t7, active_special_donor
        addu    t7, t7, t6
        addiu   t8, r0, -0x0001
        sw      t8, 0x0000(t7)
        li      t7, active_moveset_base
        addu    t7, t7, t6
        sw      r0, 0x0000(t7)

        _load_current:
        lw      v1, 0x09C4(s1)             // body character struct fallback
        lbu     t0, 0x000D(s1)
        li      t1, active_special_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      t0, 0x0000(t1)
        bgez    t0, _selected
        nop

        // Shared actions are a fresh ownership decision. Do not trust the
        // retained normal donor here: this hook runs before command_address_hook_
        // can clear it. In particular, an aerial's donor used to leak into the
        // Wait action after its landing animation and install the wrong data.
        lw      t0, 0x0024(s1)
        sltiu   t1, t0, 0x00DC
        beqz    t1, _retained_normal
        nop
        addiu   sp, sp, -0x0050
        sw      ra, 0x0004(sp)
        sw      v0, 0x0008(sp)
        sw      a0, 0x000C(sp)
        sw      a1, 0x0010(sp)
        sw      a2, 0x0014(sp)
        sw      a3, 0x0018(sp)
        sw      t2, 0x001C(sp)
        sw      t3, 0x0020(sp)
        sw      t4, 0x0024(sp)
        sw      t5, 0x0028(sp)
        sw      t6, 0x002C(sp)
        sw      t7, 0x0030(sp)
        sw      t8, 0x0034(sp)
        sw      t9, 0x0038(sp)
        or      a0, s1, r0
        jal     get_normal_donor_
        or      a1, t0, r0
        or      t0, v0, r0
        lbu     t1, 0x000D(s1)
        sll     t1, t1, 0x0002
        li      v1, active_normal_donor
        addu    v1, v1, t1
        sw      t0, 0x0000(v1)
        lw      ra, 0x0004(sp)
        lw      v0, 0x0008(sp)
        lw      a0, 0x000C(sp)
        lw      a1, 0x0010(sp)
        lw      a2, 0x0014(sp)
        lw      a3, 0x0018(sp)
        lw      t2, 0x001C(sp)
        lw      t3, 0x0020(sp)
        lw      t4, 0x0024(sp)
        lw      t5, 0x0028(sp)
        lw      t6, 0x002C(sp)
        lw      t7, 0x0030(sp)
        lw      t8, 0x0034(sp)
        lw      t9, 0x0038(sp)
        addiu   sp, sp, 0x0050
        bltz    t0, _body_normal
        nop
        b       _normal_selected
        nop

        _retained_normal:
        li      t1, active_normal_donor
        lbu     t0, 0x000D(s1)
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      t0, 0x0000(t1)
        bltz    t0, _end
        nop
        _normal_selected:
        lw      v1, 0x09C4(s1)
        _selected:
        li      t1, 0x80116E10
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      t0, 0x0000(t1)
        beqz    t0, _end
        nop
        or      v1, t0, r0
        b       _end
        nop
        _body_normal:
        lw      v1, 0x09C4(s1)
        _end:
        sra     v0, v0, 0x0016             // original instruction
        j       0x800E7504
        nop
    }

    // ftMainSetStatus has resolved the selected action parameter record here.
    // Shared normals combine the body's animation and flags with the donor's
    // command stream. Borrowed specials instead copy the donor record and
    // replace its animation with body Idle/Fall. A separate donor phase clock
    // supplies event time and recovery without applying the donor figatree to
    // an incompatible skeleton or running taunt growth/root displacement.
    scope parameter_record_hook_: {
        OS.patch_start(0x62D54, 0x800E7554)
        j       parameter_record_hook_
        nop
        OS.patch_end()

        addu    t3, a0, t2                  // original: selected param record

        // TwelveCharBattle normally owns the following two instructions. Our
        // earlier jump supersedes its hook, so call it explicitly before the
        // Character Creator override and preserve ftMainSetStatus's return RA.
        sw      ra, 0x0010(sp)
        jal     TwelveCharBattle.defeated_action_override_
        nop
        lw      ra, 0x0010(sp)

        li      t4, diagnostic_parameter_array
        lw      t5, 0x0080(sp)
        sw      t5, 0x0000(t4)
        lw      t5, 0x0074(sp)
        sw      t5, 0x0004(t4)

        lbu     t0, 0x000D(s1)              // port
        sll     t1, t0, 0x0002

        // A shared normal's selected record belongs to the donor because
        // parameter_base_hook_ temporarily substituted the donor FTData.
        // Rebuild that record with the matching body animation while retaining
        // the donor command pointer, whose waits and commands define startup,
        // active frames, hitbox data, and clear timing.
        li      t4, active_normal_donor
        addu    t4, t4, t1
        lw      t5, 0x0000(t4)
        bltz    t5, _check_special
        nop
        lw      t5, 0x0024(s1)              // current action
        sltiu   t6, t5, 0x00DC
        beqz    t6, _check_special           // unique follow-ups use donor data
        nop

        // Shared action record -> body parameter-array index.
        li      t6, 0x80128DD8
        sll     t7, t5, 0x0002
        addu    t7, t7, t5                  // action * 5
        sll     t7, t7, 0x0002              // action * 20
        addu    t6, t6, t7
        lhu     t7, 0x0000(t6)
        srl     t7, t7, 0x0006
        sltiu   t6, t7, 0x03FE
        beqz    t6, _check_special
        nop
        lw      t5, 0x09C4(s1)              // body FTData
        beqz    t5, _check_special
        nop
        lw      t6, 0x0064(t5)              // body parameter array
        sll     t8, t7, 0x0001
        addu    t8, t8, t7                  // parameter index * 3
        sll     t8, t8, 0x0002              // parameter index * 12
        addu    t6, t6, t8                  // body parameter record

        // t4 = this port's 12-byte synthetic normal record.
        sll     t4, t0, 0x0003              // port * 8
        addu    t4, t4, t1                  // port * 12
        li      t7, normal_parameter_records
        addu    t4, t4, t7
        lw      t7, 0x0000(t6)              // body animation ID
        sw      t7, 0x0000(t4)
        lw      t7, 0x0004(t3)              // donor command offset/pointer
        sw      t7, 0x0004(t4)
        lw      t7, 0x0008(t6)              // body animation flags
        sw      t7, 0x0008(t4)
        or      v1, t5, r0                  // resolve animation through body
        or      t3, t4, r0
        b       _return
        nop

        _check_special:
        li      t4, body_character_data
        addu    t4, t4, t1
        lw      t5, 0x0000(t4)              // saved body FTData
        beqz    t5, _return                  // ordinary body-owned action
        nop

        // Resolve the donor's unique action parameter record directly. The
        // selected donor FTData is installed on the fighter for the duration
        // of the borrowed special.
        li      t6, active_special_donor
        addu    t6, t6, t1
        lw      t6, 0x0000(t6)              // donor ID
        bltz    t6, _return
        nop
        lw      t7, 0x0024(s1)
        sltiu   t7, t7, 0x00DC
        bnez    t7, _special_record         // retained Link bomb common throw
        nop
        li      t7, Character.ACTION_ARRAY_TABLE
        sll     t8, t6, 0x0002
        addu    t7, t7, t8
        lw      t7, 0x0000(t7)              // donor unique action array
        beqz    t7, _return
        nop
        lw      t6, 0x0024(s1)              // current action
        addiu   t6, t6, -0x00DC
        bltz    t6, _return                  // only unique actions are adapted
        nop
        sll     t8, t6, 0x0002
        addu    t8, t8, t6                  // unique index * 5
        sll     t8, t8, 0x0002              // unique index * 20
        addu    t7, t7, t8
        lw      t6, 0x0000(t7)
        srl     t6, t6, 0x0016              // donor parameter index
        sltiu   t7, t6, 0x03FE
        beqz    t7, _return
        nop
        sw      t6, 0x0028(s1)              // repair ftMainSetStatus's index
        sll     t7, t6, 0x0001
        addu    t7, t7, t6                  // parameter index * 3
        sll     t7, t7, 0x0002              // parameter index * 12
        lw      t3, 0x09C4(s1)              // donor FTData
        lw      t3, 0x0064(t3)              // donor parameter array
        addu    t3, t3, t7

        _special_record:
        // t4 = this port's 12-byte synthetic parameter record.
        sll     t4, t0, 0x0003              // port * 8
        addu    t4, t4, t1                  // port * 12
        li      t6, special_parameter_records
        addu    t4, t4, t6
        lw      t6, 0x0000(t3)
        lw      t7, 0x0004(t3)
        lw      t8, 0x0008(t3)
        sw      t6, 0x0000(t4)
        sw      t7, 0x0004(t4)
        sw      t8, 0x0008(t4)

        // Idle/Fall have no taunt growth or root displacement. Donor phase
        // timing is supplied separately by ccPrepare/ccAdvance.
        // Character.SHARED_ACTION_ARRAY is a ROM offset; this routine needs
        // the stock array's runtime address.
        li      t6, 0x80128DD8
        // Expanded donors do not yet have a compiled phase clock. Preserve
        // their finite legacy pose rather than giving them an endless idle.
        li      t7, active_special_donor
        addu    t7, t7, t1
        lw      t7, 0x0000(t7)
        sltiu   t8, t7, 12
        beqz    t8, _body_pose_ready
        lli     t7, 0x00BD                  // legacy Action.Taunt
        lli     t7, 0x000A                  // Action.Idle
        lw      t8, 0x014C(s1)              // ground = 0, air = 1
        beqz    t8, _body_pose_ready
        nop
        lli     t7, 0x001A                  // Action.Fall
        _body_pose_ready:
        sll     t8, t7, 0x0002
        addu    t8, t8, t7                  // action * 5
        sll     t8, t8, 0x0002              // action * 20
        addu    t6, t6, t8
        lw      t6, 0x0000(t6)
        srl     t6, t6, 0x0016              // body param index
        sll     t7, t6, 0x0001
        addu    t7, t7, t6                  // index * 3
        sll     t7, t7, 0x0002              // index * 12
        lw      t6, 0x0064(t5)              // body parameter array
        addu    t6, t6, t7
        lw      t7, 0x0000(t6)              // body-safe animation ID
        sw      t7, 0x0000(t4)

        // Animation flags are meaningful only together with their animation.
        // In particular, Fox's aerial Up-B uses 0x40000000; retaining that
        // flag with a body pose makes the animation walker treat figatree
        // data as a node pointer. Use the complete body flag word.
        lw      t6, 0x0008(t6)
        sw      t6, 0x0008(t4)
        // ftMainSetStatus resolves the animation file base through v1 at
        // 0x800E7574. The synthetic animation ID belongs to the body, so use
        // the saved body FTData for that lookup. Command resolution later
        // reloads fp->data and is independently redirected to the donor.
        or      v1, t5, r0
        or      t3, t4, r0

        _return:
        sw      t3, 0x0024(sp)              // selected parameter record
        lw      t4, 0x0008(t3)              // original flag load
        j       0x800E7560
        nop
    }

    // Replaces the tail of ftMainSetStatus' command-address setup. v0 already
    // contains the body command address, and s1 is the player struct.
    scope command_address_hook_: {
        OS.patch_start(0x63140, 0x800E7940)
        j       command_address_hook_
        nop
        origin  0x6316C
        base    0x800E796C
        _return:
        OS.patch_end()

        addiu   sp, sp, -0x0060
        sw      ra, 0x0004(sp)
        sw      at, 0x0008(sp)
        sw      v1, 0x000C(sp)
        sw      a0, 0x0010(sp)
        sw      a1, 0x0014(sp)
        sw      a2, 0x0018(sp)
        sw      a3, 0x001C(sp)
        sw      t0, 0x0020(sp)
        sw      t1, 0x0024(sp)
        sw      t2, 0x0028(sp)
        sw      t3, 0x002C(sp)
        sw      t4, 0x0030(sp)
        sw      t5, 0x0034(sp)
        sw      t6, 0x0038(sp)
        sw      t7, 0x003C(sp)
        sw      t8, 0x0040(sp)
        sw      t9, 0x0044(sp)
        sw      v0, 0x0048(sp)             // body command address fallback

        // Unique actions already use the retained donor's parameter struct via
        // parameter_base_hook_. Shared actions start a new ownership decision.
        lw      t5, 0x0024(s1)
        sltiu   t5, t5, 0x00DC
        beqz    t5, _select_unique
        nop
        or      a0, s1, r0
        lw      a1, 0x0024(s1)
        jal     CharLab.keep_bomb_context_
        nop
        beqz    v0, _shared
        nop
        _select_unique:
        lbu     t0, 0x000D(s1)
        li      t1, active_special_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      a1, 0x0000(t1)
        bgez    a1, _unique_selected
        nop
        li      t1, active_normal_donor
        lbu     t0, 0x000D(s1)
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      a1, 0x0000(t1)
        bltz    a1, _normal
        nop
        _unique_selected:
        li      t0, 0x80116E10
        sll     t1, a1, 0x0002
        addu    t0, t0, t1
        lw      a2, 0x0000(t0)
        beqz    a2, _special_none
        sw      a2, 0x004C(sp)
        lw      t2, 0x0028(sp)
        lw      t3, 0x0004(t2)
        li      t4, 0x80000000
        beq     t3, t4, _special_none
        nop
        bltz    t3, _special_absolute
        sw      t3, 0x0054(sp)
        lbu     a0, 0x000D(s1)
        jal     get_moveset_base_
        nop
        beqz    v0, _special_none
        sw      v0, 0x0050(sp)
        lw      t3, 0x0054(sp)
        addu    v0, v0, t3
        b       _set_active
        nop

        _special_absolute:
        or      v0, t3, r0
        lbu     a0, 0x000D(s1)
        jal     get_moveset_base_
        nop
        sw      v0, 0x0050(sp)
        lw      v0, 0x0054(sp)
        b       _set_active
        nop

        _special_none:
        or      v0, r0, r0
        b       _clear_active
        nop

        _shared:
        // A shared action has left any borrowed special chain.
        lbu     t0, 0x000D(s1)
        li      t1, active_special_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        addiu   t2, r0, -0x0001
        sw      t2, 0x0000(t1)
        _normal:
        or      a0, s1, r0
        jal     get_normal_donor_
        lw      a1, 0x0024(s1)
        bltz    v0, _body
        or      a1, v0, r0                 // a1 = donor ID

        lbu     t0, 0x000D(s1)
        li      t1, active_normal_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        sw      a1, 0x0000(t1)

        li      t0, 0x80116E10             // character struct pointer table
        sll     t1, a1, 0x0002
        addu    t0, t0, t1
        lw      a2, 0x0000(t0)             // donor character struct
        beqz    a2, _body
        sw      a2, 0x004C(sp)

        // Shared action record -> parameter-array index.
        lw      t2, 0x0024(s1)
        li      t0, 0x80128DD8             // vanilla shared action array
        sll     t1, t2, 0x0002             // action * 4
        addu    t1, t1, t2                 // action * 5
        sll     t1, t1, 0x0002             // action * 20
        addu    t0, t0, t1
        lhu     t1, 0x0000(t0)
        srl     t1, t1, 0x0006
        sltiu   t0, t1, 0x03FE
        beqz    t0, _body
        nop
        lw      t0, 0x0064(a2)             // donor parameter array
        sll     t2, t1, 0x0001
        addu    t2, t2, t1                 // index * 3
        sll     t2, t2, 0x0002             // index * 12
        addu    t0, t0, t2
        lw      t3, 0x0004(t0)             // donor command offset/pointer
        li      t4, 0x80000000
        beq     t3, t4, _none
        nop
        bltz    t3, _absolute
        nop

        lbu     a0, 0x000D(s1)
        lw      a2, 0x004C(sp)
        jal     get_moveset_base_
        nop
        beqz    v0, _body
        sw      v0, 0x0050(sp)             // donor moveset base
        lw      a2, 0x004C(sp)
        lw      t0, 0x0064(a2)
        // Recompute donor parameter to reload the command offset.
        lw      t2, 0x0024(s1)
        li      t1, 0x80128DD8
        sll     t0, t2, 0x0002
        addu    t0, t0, t2
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lhu     t0, 0x0000(t1)
        srl     t0, t0, 0x0006
        sll     t1, t0, 0x0001
        addu    t1, t1, t0
        sll     t1, t1, 0x0002
        lw      a2, 0x004C(sp)
        lw      t0, 0x0064(a2)
        addu    t0, t0, t1
        lw      t3, 0x0004(t0)
        addu    v0, v0, t3
        b       _set_active
        nop

        _absolute:
        or      v0, t3, r0
        // Absolute command streams can still use GO_TO_FILE, so acquire the
        // donor base when possible; failure does not invalidate the pointer.
        lbu     a0, 0x000D(s1)
        lw      a2, 0x004C(sp)
        jal     get_moveset_base_
        nop
        sw      v0, 0x0050(sp)             // donor moveset base (0 if unavailable)
        lw      t0, 0x004C(sp)
        lw      t0, 0x0064(t0)
        lw      t2, 0x0024(s1)
        li      t1, 0x80128DD8
        sll     t3, t2, 0x0002
        addu    t3, t3, t2
        sll     t3, t3, 0x0002
        addu    t1, t1, t3
        lhu     t1, 0x0000(t1)
        srl     t1, t1, 0x0006
        sll     t3, t1, 0x0001
        addu    t3, t3, t1
        sll     t3, t3, 0x0002
        addu    t0, t0, t3
        lw      v0, 0x0004(t0)             // restore absolute command pointer

        _set_active:
        lbu     t0, 0x000D(s1)
        li      t1, active_moveset_base
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        lw      t2, 0x0050(sp)
        sw      t2, 0x0000(t1)
        b       _finish
        nop

        _none:
        or      v0, r0, r0
        b       _clear_active
        nop
        _body:
        lw      v0, 0x0048(sp)
        lbu     t0, 0x000D(s1)
        li      t1, active_normal_donor
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        addiu   t0, r0, -0x0001
        sw      t0, 0x0000(t1)
        // Preserve the stock Moveset hook's absolute-pointer and no-command
        // handling when this action is not borrowed.
        lw      t2, 0x0028(sp)             // original action parameter struct
        lw      t0, 0x0004(t2)
        bgez    t0, _clear_active
        li      t1, 0x80000000
        beq     t0, t1, _body_none
        nop
        or      v0, t0, r0
        b       _clear_active
        nop
        _body_none:
        or      v0, r0, r0
        _clear_active:
        lbu     t0, 0x000D(s1)
        li      t1, active_moveset_base
        sll     t0, t0, 0x0002
        addu    t1, t1, t0
        sw      r0, 0x0000(t1)

        _finish:
        sw      v0, 0x0048(sp)
        lw      ra, 0x0004(sp)
        lw      at, 0x0008(sp)
        lw      v1, 0x000C(sp)
        lw      a0, 0x0010(sp)
        lw      a1, 0x0014(sp)
        lw      a2, 0x0018(sp)
        lw      a3, 0x001C(sp)
        lw      t0, 0x0020(sp)
        lw      t1, 0x0024(sp)
        lw      t2, 0x0028(sp)
        lw      t3, 0x002C(sp)
        lw      t4, 0x0030(sp)
        lw      t5, 0x0034(sp)
        lw      t6, 0x0038(sp)
        lw      t7, 0x003C(sp)
        lw      t8, 0x0040(sp)
        lw      t9, 0x0044(sp)
        lw      v0, 0x0048(sp)
        addiu   sp, sp, 0x0060
        sw      v0, 0x08AC(s1)
        sw      v0, 0x086C(s1)
        j       _return
        nop
    }

    // A borrowed script can name a model joint that the selected body does
    // not contain. The stock hitbox command stores that null pointer and later
    // dereferences it. Keep valid cross-rig joints unchanged, but attach an
    // otherwise-invalid custom hitbox to the body's top joint.
    scope hitbox_joint_guard_: {
        OS.patch_start(0x5AB30, 0x800DF330)
        j       hitbox_joint_guard_
        nop
        _return:
        OS.patch_end()

        lw      t8, 0x08E8(t7)             // original joint lookup
        // Replay the second instruction replaced by this hook. The stock
        // parser needs this constant for its integer-to-float conversions;
        // without it, otherwise-valid donor hitboxes receive invalid values.
        lui     at, 0x4F80                 // original at 0x800DF334
        beqz    t8, _check_custom
        nop
        j       _return
        nop

        _check_custom:
        lbu     at, 0x000D(s1)
        sll     at, at, 0x0002
        li      t9, active_normal_donor
        addu    t9, t9, at
        lw      at, 0x0000(t9)
        bgez    at, _fallback
        nop
        lbu     at, 0x000D(s1)
        sll     at, at, 0x0002
        li      t9, active_special_donor
        addu    t9, t9, at
        lw      at, 0x0000(t9)
        bgez    at, _fallback
        nop
        j       _return
        lui     at, 0x4F80                 // restore parser conversion constant

        _fallback:
        lw      t8, 0x08E8(s1)             // body top joint
        j       _return
        lui     at, 0x4F80                 // restore after using at as scratch
    }

    // Donor motion scripts can request costume/model parts that only exist on
    // the donor's skeleton (Fox's blaster is a common example). The stock
    // routine indexes the body's model-part table without validating the donor
    // part ID. Suppress those cosmetic mutations for cross-character actions;
    // gameplay commands such as hitboxes and projectile creation still run.
    scope model_part_guard_: {
        OS.patch_start(0x64470, 0x800E8C70)
        j       model_part_guard_
        nop
        _return:
        OS.patch_end()

        lw      t0, 0x0084(a0)              // fighter struct
        beqz    t0, _normal
        nop
        lbu     t1, 0x000D(t0)
        sll     t1, t1, 0x0002
        li      t2, body_character_data
        addu    t2, t2, t1
        lw      t3, 0x0000(t2)
        bnez    t3, _suppress               // borrowed special owns fighter
        nop
        li      t2, active_normal_donor
        addu    t2, t2, t1
        lw      t3, 0x0000(t2)
        bltz    t3, _normal
        lw      t4, 0x0008(t0)
        bne     t3, t4, _suppress            // donor part IDs are body-unsafe
        nop

        _normal:
        addiu   sp, sp, -0x0060             // original instruction 1
        sw      ra, 0x0024(sp)              // original instruction 2
        j       _return
        nop

        _suppress:
        jr      ra
        nop
    }

    // @ Description
    // Shared actions belong to the configured body. End special ownership as
    // soon as a borrowed unique-action chain returns to the shared action set.
    // a0 = player struct, a1 = new action ID.
    scope on_action_changed_: {
        sltiu   t0, a1, 0x00DC             // first unique action ID
        beqz    t0, _end
        nop
        OS.save_registers()
        jal     CharLab.keep_bomb_context_
        nop
        beqz    v0, _restore_body
        nop
        OS.restore_registers()
        jr      ra
        nop
        _restore_body:
        OS.restore_registers()
        lbu     t0, 0x000D(a0)
        sll     t0, t0, 0x0002
        li      t1, active_special_donor
        addu    t1, t1, t0
        addiu   t2, r0, -0x0001
        sw      t2, 0x0000(t1)
        li      t1, active_moveset_base
        addu    t1, t1, t0
        sw      r0, 0x0000(t1)
        li      t1, body_character_data
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        beqz    t2, _end
        nop
        addiu   sp, sp, -0x0010
        sw      ra, 0x0004(sp)
        sw      a0, 0x0008(sp)
        jal     restore_joint_fallbacks_
        nop
        lw      a0, 0x0008(sp)
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0010
        lbu     t0, 0x000D(a0)
        sll     t0, t0, 0x0002
        li      t1, body_character_data
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        sw      t2, 0x09C4(a0)
        sw      r0, 0x0000(t1)
        li      t1, body_character_id
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        sw      t2, 0x0008(a0)
        addiu   t2, r0, -0x0001
        sw      t2, 0x0000(t1)
        li      t1, body_animation_heap
        addu    t1, t1, t0
        lw      t2, 0x0000(t1)
        sw      t2, 0x09D0(a0)
        sw      r0, 0x0000(t1)
        _end:
        jr      ra
        nop
    }

    // @ Description
    // Applies the global catalog filter selected on the creator hub. The first
    // twelve generated catalog entries are the original US roster. Menu entry
    // types retain their compile-time width so SRAM packing is stable; only
    // the interactive max and out-of-range values are updated.
    scope sync_catalog_mode_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        li      t0, Toggles.cc_original_12_only
        lw      t0, 0x0004(t0)
        li      t1, catalog_mode_last
        lw      t2, 0x0000(t1)
        beq     t0, t2, _end
        sw      t0, 0x0000(t1)

        beqz    t0, _all
        lli     t7, 0x000B                  // Ness is catalog index 11
        b       _begin
        nop
        _all:
        lli     t7, CharCreatorCatalog.COUNT - 1

        _begin:
        li      t6, slot_tables
        lli     t5, SLOT_COUNT
        _slot_loop:
        lw      t4, 0x0000(t6)             // slot entry-pointer table
        lw      t3, 0x0004(t4)             // body entry
        sw      t7, 0x0008(t3)             // interactive maximum
        lw      t2, 0x0000(t3)             // body catalog index
        sltu    t1, t7, t2
        beqzl   t1, _body_ready
        nop
        or      t2, r0, r0                 // filtered body falls back to Mario
        sw      t2, 0x0000(t3)

        _body_ready:
        addiu   t4, t4, FIELD_JAB * 4
        lli     t3, FIELD_COUNT - FIELD_JAB
        lli     t8, FIELD_JAB
        _field_loop:
        lw      t1, 0x0000(t4)             // move entry
        lli     at, FIELD_NSP
        beq     t8, at, _lock_nsp
        nop
        or t9, t7, r0
        sltiu at, t8, FIELD_GRAB
        bnez at, _set_max
        nop
        lli t9, 11 // Grab/throw data is original-roster only.
        _set_max:
        sw      t9, 0x0008(t1)
        lw      t0, 0x0000(t1)
        sltu    at, t9, t0
        beqzl   at, _field_next
        nop
        sltu at, t9, t2
        beqz at, _fallback_body
        nop
        b _field_next
        sw r0, 0x0000(t1)
        _fallback_body:
        sw      t2, 0x0000(t1)             // filtered donor becomes the body
        b       _field_next
        nop

        _lock_nsp:
        sw r0, 0x0004(t1)
        lli t0, 1
        sw t0, 0x0008(t1)

        _field_next:
        addiu   t4, t4, 0x0004
        addiu   t3, t3, -0x0001
        addiu   t8, t8, 0x0001
        bnez    t3, _field_loop
        nop
        addiu   t6, t6, 0x0004
        addiu   t5, t5, -0x0001
        bnez    t5, _slot_loop
        nop
        jal     reset_cache_
        nop

        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // @ Description
    // Menu action that initializes every move donor to the selected body. This
    // gives a new recipe a known-good baseline before individual moves change.
    // v0 = title entry; entry.extra is the 1-based slot number.
    scope copy_body_to_all_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        lw      t0, 0x0024(v0)
        addiu   t0, t0, -0x0001
        sltiu   t1, t0, SLOT_COUNT
        beqz    t1, _end
        sll     t0, t0, 0x0002
        li      t1, slot_tables
        addu    t1, t1, t0
        lw      t1, 0x0000(t1)
        sw      t1, 0x0008(sp)
        lw      t0, 0x0004(t1)             // body entry pointer
        lw      t0, 0x0000(t0)             // body catalog index
        sw      t0, 0x000C(sp)
        addiu   t1, t1, FIELD_JAB * 4
        lli     t2, FIELD_COUNT - FIELD_JAB
        lli     t3, FIELD_JAB
        _loop:
        lw      v0, 0x0000(t1)
        lli     t4, FIELD_NSP
        beq     t3, t4, _set_fox_nsp
        nop
        lw      t0, 0x000C(sp)
        sltiu t4, t3, FIELD_GRAB
        bnez t4, _write_body
        nop
        sltiu t4, t0, 12
        bnez t4, _write_body
        nop
        or t0, r0, r0
        _write_body:
        b       _update
        sw      t0, 0x0000(v0)

        _set_fox_nsp:
        sw r0, 0x0000(v0) // Body Move is the baseline.

        _update:
        sw      t1, 0x0010(sp)
        sw      t2, 0x0014(sp)
        sw      t3, 0x0018(sp)
        jal     Menu.update_pointer_
        addiu   v0, v0, -0x0004            // value pointer -> entry base
        lw      t1, 0x0010(sp)
        lw      t2, 0x0014(sp)
        lw      t3, 0x0018(sp)
        addiu   t1, t1, 0x0004
        addiu   t2, t2, -0x0001
        addiu   t3, t3, 0x0001
        bnez    t2, _loop
        nop
        jal     reset_cache_
        nop
        _end:
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }

    // @ Description
    // CSS menu onchange handler.
    scope on_build_changed_: {
        addiu   sp, sp, -0x0010
        sw      ra, 0x0004(sp)
        jal     reset_cache_
        nop
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0010
        jr      ra
        nop
    }

    // @ Description
    // Saves all creator pages, selects this slot for P1 and opens Training CSS.
    // v0 = TEST menu entry; entry.extra is the 1-based slot number.
    scope test_in_training_: {
        addiu   sp, sp, -0x0020
        sw      ra, 0x0004(sp)
        lw      t0, 0x0024(v0)
        sw      t0, 0x0008(sp)
        jal     Toggles.save_
        nop
        li      t1, selected_builds
        lw      t0, 0x0008(sp)
        sw      t0, 0x0000(t1)
        lui t1, CharLab.training_slot >> 16
        ori t1, t1, CharLab.training_slot & 0xFFFF
        sw t0, 0x0000(t1)
        jal     reset_cache_
        nop
        // Settings does not initialize the native 1P Training selections.
        // Use this recipe's body and a native Mario dummy rather than stale
        // expanded-roster preview IDs/costumes left by another screen.
        lw      t0, 0x0008(sp)
        addiu   t0, t0, -1
        sll     t0, t0, 2
        li      t1, slot_tables
        addu    t1, t1, t0
        lw      t1, 0x0000(t1)
        lw      t1, 0x0004(t1)
        jal     catalog_id_
        lw      a0, 0x0000(t1)
        jal     CharLabRuntime.ccSetupTraining
        or      a0, v0, r0
        jal     Menu.change_screen_
        lli     a0, Global.screen.TRAINING_CSS
        lw      ra, 0x0004(sp)
        addiu   sp, sp, 0x0020
        jr      ra
        nop
    }
}

} // __CHAR_CREATOR__
