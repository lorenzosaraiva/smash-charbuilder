// Shared Character Lab runtime on Remix's original fighter ABI.
if !{defined __CHAR_LAB__} {
define __CHAR_LAB__()
scope CharLab {
    // Advance the Expansion Pak cursor with native allocations. Otherwise a
    // later overflow restarts at custom_heap and overwrites live GC pools.
    scope heap_reset_: {
        OS.patch_start(0x5570, 0x80004970)
        j heap_reset_
        lw ra, 0x14(sp)
        OS.patch_end()
        // Native scene teardown has ejected its objects before this heap
        // reset. Forget donor ownership now, before results/CSS can reuse
        // fighter slots and animation memory from an interrupted special.
        OS.save_registers()
        jal CharCreator.reset_cache_
        nop
        OS.restore_registers()
        li t0, CharacterSelect.expansion_expansion_ram
        sw r0, 0(t0)
        sw r0, 4(t0)
        li t0, custom_heap_address
        li t1, custom_heap
        sw t1, 0(t0)
        j CharacterSelect.clear_expansion_expansion_ram_._return
        nop
    }
    scope heap_cursor_: {
        OS.patch_start(0x3800000 + CharacterSelect.increase_heap_._return - 0x80400000, CharacterSelect.increase_heap_._return)
        j heap_cursor_
        sw v0, 0xC(a3)
        OS.patch_end()
        addiu sp, sp, -16
        sw t0, 0(sp)
        sw t1, 4(sp)
        li t0, 0x800465E8
        bne a3, t0, _end
        nop
        li t0, custom_heap
        sltu t1, v0, t0
        bnez t1, _end
        nop
        lui t0, 0x8080
        sltu t1, v0, t0
        beqz t1, _end
        nop
        li t0, custom_heap_address
        lw t1, 0(t0)
        sltu t1, t1, v0
        beqz t1, _end
        nop
        sw v0, 0(t0)
        _end:
        lw t0, 0(sp)
        lw t1, 4(sp)
        jr ra
        addiu sp, sp, 16
    }
    // Late UI setup must not rewind the cursor past allocated object pools.
    OS.patch_start(0x3800000 + CharacterSelect.load_additional_characters_ + 0x24 - 0x80400000, CharacterSelect.load_additional_characters_ + 0x24)
    nop
    OS.patch_end()
    OS.patch_start(0x3800000 + Render.setup_._mode_select + 0x34 - 0x80400000, Render.setup_._mode_select + 0x34)
    nop
    OS.patch_end()
    // Original-roster CSS uses original bodies. Loading every large expanded
    // CSS model before reserving its five heaps can exhaust Expansion Pak RAM
    // after the creator runtime grows. Keep native on-demand loading; the
    // experimental expanded creator retains its normal preload path.
    scope editor_css_models_: {
        OS.patch_start(0x3800000 + CharacterSelect.load_additional_characters_ - 0x80400000, CharacterSelect.load_additional_characters_)
        j editor_css_models_
        nop
        OS.patch_end()
        OS.read_byte(Global.current_screen, t0)
        sltiu t1, t0, Global.screen.VS_CSS
        bnez t1, _native
        nop
        sltiu t1, t0, Global.screen.BONUS_2_CSS + 1
        beqz t1, _native
        nop
        li t0, Toggles.block_char_creator_options + 0x10
        lw t0, 0(t0)
        beqz t0, _native
        nop
        addiu sp, sp, -8
        sw ra, 4(sp)
        li s0, CharacterSelectDebugMenu.debug_control_object
        sw r0, 0(s0)
        lli s1, 0
        j CharacterSelect.load_additional_characters_._end
        nop
        _native:
        addiu sp, sp, -8
        sw ra, 4(sp)
        j CharacterSelect.load_additional_characters_ + 8
        nop
    }
    // Original-roster CSS already loads its twelve native model files. Five
    // expanded-model heaps reserved up front consume almost 600 KB and leave
    // too little room for four ready panels. Initialize empty heaps in this
    // mode, then reserve one only if an expanded CSS model actually uses it.
    scope css_heap_init_: {
        OS.patch_start(0x3800000 + CharacterSelect.initialize_dynamic_css_._loop + 0x1C - 0x80400000, CharacterSelect.initialize_dynamic_css_._loop + 0x1C)
        jal css_heap_init_
        sw t0, 0xC(at)
        OS.patch_end()
        li t0, Toggles.cc_original_12_only
        lw t0, 4(t0)
        beqz t0, _native
        nop
        li t0, 0x800465E8
        sw a2, 0xC(t0)
        or a3, r0, r0
        _native:
        j 0x80006D54
        nop
    }
    scope css_heap_alloc_: {
        OS.patch_start(0x3800000 + CharacterSelect.dynamically_load_character_._use_alt_heap - 0x80400000, CharacterSelect.dynamically_load_character_._use_alt_heap)
        jal css_heap_alloc_
        nop
        OS.patch_end()
        OS.save_registers()
        lw t1, 4(t0)
        lw t2, 8(t0)
        bne t1, t2, _restore
        nop
        // Native C may spill four arguments into the o32 home area.
        addiu sp, sp, -0x0010
        li a0, CharacterSelect.dynamic_css.HEAP_SIZE
        jal 0x80004980
        lli a1, 16
        or a2, v0, r0
        lw a0, 0x30(sp) // saved t0 = destination heap
        lw a1, 0(a0)
        li a3, CharacterSelect.dynamic_css.HEAP_SIZE
        jal 0x80006D54
        nop
        addiu sp, sp, 0x0010
        _restore:
        OS.restore_registers()
        li t7, CharacterSelect.dynamic_css.alt_heap_pointer
        jr ra
        nop
    }
    scope body_kind_: {
        lbu t0, 0x000D(a0)
        sltiu t1, t0, 4
        beqz t1, _native
        sll t0, t0, 2
        li t1, CharCreator.body_character_data
        addu t1, t1, t0
        lw t1, 0x0000(t1)
        beqz t1, _native
        nop
        li t1, CharCreator.body_character_id
        addu t1, t1, t0
        lw v0, 0x0000(t1)
        bgez v0, _end
        nop
        _native:
        lw v0, 0x0008(a0)
        _end:
        jr ra
        nop
    }
    scope select_jab_donor_: {
        lbu t0, 0x000D(a0)
        sltiu t1, t0, 4
        beqz t1, _end
        sll t0, t0, 2
        li t1, CharCreator.active_normal_donor
        addu t1, t1, t0
        sw a1, 0x0000(t1)
        _end:
        jr ra
        or v0, a1, r0
    }
    // Source TransN movement is independent of the safe visible body pose.
    OS.patch_start(0x54414, 0x800D8C14)
    j CharLabRuntime.ccGroundTravel
    nop
    OS.patch_end()
    original_ground_travel_:
    OS.copy_segment(0x54414, 8)
    j 0x800D8C1C
    nop
    OS.patch_start(0x54A60, 0x800D9260)
    j CharLabRuntime.ccAirTravel
    nop
    OS.patch_end()
    original_air_travel_:
    OS.copy_segment(0x54A60, 8)
    j 0x800D9268
    nop
    OS.patch_start(0x544CC, 0x800D8CCC)
    j CharLabRuntime.ccGroundPhysics
    nop
    OS.patch_end()
    original_ground_physics_:
    OS.copy_segment(0x544CC, 8)
    j 0x800D8CD4
    nop
    // Donor recovery callbacks address their own base bone (joint 4).
    // That bone is not the same part of another body. Keep the actual
    // movement/velocity callbacks, but suppress donor-only pitching/stretch.
    macro special_pose_guard(offset, address, name) {
        scope {name}: {
            OS.patch_start({offset}, {address})
            j {name}
            nop
            OS.patch_end()
            lw v0, 0x0084(a0)
            lbu t0, 0x000D(v0)
            sltiu t1, t0, 4
            beqz t1, _native
            sll t0, t0, 2
            li t1, CharCreator.body_character_data
            addu t1, t1, t0
            lw t1, 0x0000(t1)
            beqz t1, _native
            nop
            jr ra
            nop
            _native:
            OS.copy_segment({offset}, 8)
            j {address} + 8
            nop
        }
    }
    special_pose_guard(0xCD4E0, 0x80152AA0, pikachu_pitch_scale_)
    special_pose_guard(0xD6A94, 0x8015C054, fox_pitch_)
    special_pose_guard(0xCF198, 0x80154758, ness_pitch_)

    scope special_donor_: {
        lbu t0, 0x000D(a0)
        sltiu t1, t0, 4
        beqz t1, _none
        sll t0, t0, 2
        li t1, CharCreator.body_character_data
        addu t1, t1, t0
        lw t1, 0x0000(t1)
        beqz t1, _none
        nop
        li t1, CharCreator.active_special_donor
        addu t1, t1, t0
        jr ra
        lw v0, 0x0000(t1)
        _none:
        jr ra
        addiu v0, r0, -1
    }
    macro save_fpu() {
        addiu sp, sp, -0x0080
        sdc1 f0, 0x0010(sp); sdc1 f2, 0x0018(sp)
        sdc1 f4, 0x0020(sp); sdc1 f6, 0x0028(sp)
        sdc1 f8, 0x0030(sp); sdc1 f10, 0x0038(sp)
        sdc1 f12, 0x0040(sp); sdc1 f14, 0x0048(sp)
        sdc1 f16, 0x0050(sp); sdc1 f18, 0x0058(sp)
        cfc1 t0, 31
        sw t0, 0x0060(sp)
    }
    macro restore_fpu() {
        ldc1 f0, 0x0010(sp); ldc1 f2, 0x0018(sp)
        ldc1 f4, 0x0020(sp); ldc1 f6, 0x0028(sp)
        ldc1 f8, 0x0030(sp); ldc1 f10, 0x0038(sp)
        ldc1 f12, 0x0040(sp); ldc1 f14, 0x0048(sp)
        ldc1 f16, 0x0050(sp); ldc1 f18, 0x0058(sp)
        lw t0, 0x0060(sp)
        ctc1 t0, 31
        addiu sp, sp, 0x0080
    }
    // Return the common held-bomb exception without changing live registers.
    // The caller additionally preserves v0 when it consumes this result.
    scope keep_bomb_context_: {
        OS.save_registers()
        save_fpu()
        lw a0, 0x0090(sp)
        lw a1, 0x0094(sp)
        jal CharLabRuntime.ccKeepSpecialContext
        nop
        sw v0, 0x0088(sp)
        restore_fpu()
        OS.restore_registers()
        jr ra
        nop
    }
    // Missing donor joints may alias TopN only while callbacks run. Body
    // part/animation initialization must see its original null slots, or a
    // reset of a missing part overwrites the fighter's world-root transform.
    scope suspend_joints_: {
        lbu t0, 0x000D(a0)
        sltiu t1, t0, 4
        beqz t1, _end
        sll t0, t0, 2
        li t1, CharCreator.body_character_data
        addu t1, t1, t0
        lw t1, 0x0000(t1)
        beqz t1, _end
        nop
        j CharCreator.restore_joint_fallbacks_
        nop
        _end:
        jr ra
        nop
    }
    scope resume_joints_: {
        lbu t0, 0x000D(a0)
        sltiu t1, t0, 4
        beqz t1, _end
        sll t0, t0, 2
        li t1, CharCreator.body_character_data
        addu t1, t1, t0
        lw t1, 0x0000(t1)
        beqz t1, _end
        nop
        j CharCreator.install_joint_fallbacks_
        nop
        _end:
        jr ra
        nop
    }
    // Observe transitions before the shared status union/context is reused.
    scope status_changing_: {
        OS.patch_start(0x62724, 0x800E6F24)
        j status_changing_
        nop
        OS.patch_end()
        OS.save_registers()
        save_fpu()
        lw a0, 0x0090(sp)
        lw a1, 0x0094(sp)
        jal CharLabRuntime.ccStatusChanging
        nop
        lw a0, 0x0090(sp)
        lw a0, 0x0084(a0)
        jal suspend_joints_
        nop
        restore_fpu()
        OS.restore_registers()
        OS.copy_segment(0x62724, 8)
        j 0x800E6F2C
        nop
    }
    scope reset_: {
        OS.save_registers()
        save_fpu()
        jal CharLabRuntime.ccReset
        nop
        restore_fpu()
        OS.restore_registers()
        jr ra
        nop
    }
    scope restore_body_: {
        j CharCreator.on_action_changed_
        or a1, r0, r0
    }
    // The native air-input gate precedes donor dispatch. DK's body has no
    // aerial Down B, but that must not block a selected Samus Bomb (or other
    // original donor with an aerial entry). Preserve native/expanded fallback.
    scope air_down_b_available_: {
        OS.patch_start(0xCB9E4, 0x80150FA4)
        j air_down_b_available_
        nop
        OS.patch_end()
        addiu sp, sp, -0x0030
        sw ra, 0x0000(sp)
        sw a0, 0x0004(sp)
        sw a1, 0x0008(sp)
        sw a2, 0x000C(sp)
        sw v0, 0x0010(sp)
        sw v1, 0x0014(sp)
        sw at, 0x0018(sp)
        save_fpu()
        jal CharLabRuntime.ccCanAirDownB
        or a0, a1, r0
        subu t6, r0, v0
        restore_fpu()
        lw ra, 0x0000(sp)
        lw a0, 0x0004(sp)
        lw a1, 0x0008(sp)
        lw a2, 0x000C(sp)
        lw v0, 0x0010(sp)
        lw v1, 0x0014(sp)
        lw at, 0x0018(sp)
        j 0x80150FAC
        addiu sp, sp, 0x0030
    }

    // Both native streams are initialized before the external stream starts.
    scope prepare_: {
        OS.patch_start(0x631B0, 0x800E79B0)
        j prepare_
        nop
        OS.patch_end()
        OS.save_registers()
        save_fpu()
        lw a0, 0x0180(sp)
        lw a1, 0x0188(sp)
        jal CharLabRuntime.ccPrepare
        nop
        lw a0, 0x0180(sp)
        lw a0, 0x0084(a0)
        jal resume_joints_
        nop
        restore_fpu()
        OS.restore_registers()
        lwc1 f8, 0x0098(sp)
        c.eq.s f8, f10
        j 0x800E79B8
        nop
    }
    // Native animation calls determine hitlag/pause ownership of the clock.
    scope anim_update_: {
        OS.patch_start(0x5C00C, 0x800E080C)
        jal anim_update_
        OS.patch_end()
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        sw a0, 0x0018(sp)
        jal 0x800E82B8
        nop
        jal CharLabRuntime.ccAdvance
        lw a0, 0x0018(sp)
        lw ra, 0x0014(sp)
        jr ra
        addiu sp, sp, 0x0020
    }
    // Continue through the native parser, including Remix's event patches.
    OS.patch_start(0x5A8F0, 0x800DF0F0)
    j CharLabRuntime.ccParse
    nop
    OS.patch_end()
    original_parse_:
    addiu sp, sp, -0x00C0
    sw s1, 0x0028(sp)
    j 0x800DF0F8
    nop
    scope events_all_: {
        OS.patch_start(0x5C040, 0x800E0840)
        jal events_all_
        OS.patch_end()
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        sw a0, 0x0018(sp)
        jal 0x800E02A8
        nop
        jal CharLabRuntime.ccEvents
        lw a0, 0x0018(sp)
        lw ra, 0x0014(sp)
        jr ra
        addiu sp, sp, 0x0020
    }
    scope events_forward_: {
        OS.patch_start(0x5C068, 0x800E0868)
        jal events_forward_
        OS.patch_end()
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        sw a0, 0x0018(sp)
        jal 0x800E0478
        nop
        jal CharLabRuntime.ccEventsForward
        lw a0, 0x0018(sp)
        lw ra, 0x0014(sp)
        jr ra
        addiu sp, sp, 0x0020
    }
    // Root offsets are installed before the original swept collision update.
    scope collisions_: {
        OS.patch_start(0x5DC4C, 0x800E244C)
        j collisions_
        nop
        OS.patch_end()
        OS.save_registers()
        save_fpu()
        jal CharLabRuntime.ccCollision
        or a0, s1, r0
        restore_fpu()
        OS.restore_registers()
        or a2, r0, r0
        or v1, s1, r0
        j 0x800E2454
        nop
    }
    scope mapped_thrown_kind_: {
        li t0, Character.f_thrown_action.table
        beqz a1, _lookup
        nop
        li t0, Character.b_thrown_action.table
        _lookup:
        sll t1, a0, 2
        addu t0, t0, t1
        jr ra
        lw v0, 0x0000(t0)
    }
    scope throw_: {
        OS.patch_start(0xC4C28, 0x8014A1E8)
        j throw_
        nop
        OS.patch_end()
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        sw a0, 0x0018(sp)
        sw a1, 0x001C(sp)
        jal CharLabRuntime.ccThrow
        nop
        lw a0, 0x0018(sp)
        lw a1, 0x001C(sp)
        lw ra, 0x0014(sp)
        beqz v0, _original
        addiu sp, sp, 0x0020
        jr ra
        nop
        _original:
        OS.copy_segment(0xC4C28, 8)
        j 0x8014A1F0
        nop
    }
    training_slot:; dw 0
    return_slot:; dw 0
    scope training_exit_: {
        OS.patch_start(0x116ED4, 0x801906B4)
        j training_exit_
        nop
        OS.patch_end()
        lli t4, Global.screen.TRAINING_CSS
        li t0, training_slot
        lw t1, 0x0000(t0)
        beqz t1, _end
        sltiu t2, t1, 5
        beqz t2, _end
        nop
        li t2, return_slot
        sw t1, 0x0000(t2)
        sw r0, 0x0000(t0)
        li t2, Toggles.normal_options
        sb r0, 0x0000(t2)
        lli t4, Global.screen.OPTION
        _end:
        j 0x801906BC
        lw s0, 0x0014(sp)
    }
    scope training_css_back_: {
        // Training CSS is ovl28 (ROM 0x1410E0 -> RAM 0x80131B00).
        // ovl27's same RAM address belongs to the ordinary 1P CSS.
        OS.patch_start(0x144DAC, 0x801357CC)
        j training_css_back_
        nop
        OS.patch_end()
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        jal _original
        nop
        li t0, training_slot
        lw t1, 0x0000(t0)
        beqz t1, _end
        sltiu t2, t1, 5
        beqz t2, _end
        nop
        li t2, return_slot
        sw t1, 0x0000(t2)
        sw r0, 0x0000(t0)
        li t2, Toggles.normal_options
        sb r0, 0x0000(t2)
        li t2, Global.current_screen
        lli t1, Global.screen.OPTION
        sb t1, 0x0000(t2)
        _end:
        lw ra, 0x0014(sp)
        jr ra
        addiu sp, sp, 0x0020
        _original:
        OS.copy_segment(0x144DAC, 8)
        j 0x801357D4
        nop
    }
    scope resume_editor_: {
        addiu sp, sp, -0x0020
        sw ra, 0x0014(sp)
        li t0, return_slot
        lw t1, 0x0000(t0)
        beqz t1, _end
        sltiu t2, t1, 5
        beqz t2, _end
        sw r0, 0x0000(t0)
        addiu t2, t1, -1
        sll t2, t2, 2
        lui t0, editor_heads >> 16
        ori t0, t0, editor_heads & 0xFFFF
        addu t0, t0, t2
        lw t0, 0x0000(t0)
        li a0, Toggles.info
        lw t3, 0x0018(a0) // Retire the previously drawn Settings page.
        sw t3, 0x0018(sp)
        sw t0, 0x0000(a0)
        lli t3, 24 // Taunt makes TEST the first row of page three.
        _page:
        lw t0, 0x001C(t0)
        addiu t3, t3, -1
        bnez t3, _page
        nop
        sw t0, 0x0018(a0)
        sw t0, 0x001C(a0)
        lli t0, 24
        sw t0, 0x000C(a0)
        addiu t1, t1, 8
        li t0, Toggles.menu_index
        sb t1, 0x0000(t0)
        lui t0, editor_titles >> 16
        ori t0, t0, editor_titles & 0xFFFF
        addu t0, t0, t2
        lw t0, 0x0000(t0)
        li t1, Toggles.page_title_pointer
        sw t0, 0x0000(t1)
        jal Menu.redraw_
        lw a1, 0x0018(sp)
        lli a0, 13
        jal Render.toggle_group_display_
        lli a1, 1
        lli a0, 21
        jal Render.toggle_group_display_
        lli a1, 1
        _end:
        lw ra, 0x0014(sp)
        jr ra
        addiu sp, sp, 0x0020
    }
    editor_heads:
    dw Toggles.head_char_creator_slot_1, Toggles.head_char_creator_slot_2
    dw Toggles.head_char_creator_slot_3, Toggles.head_char_creator_slot_4
    editor_titles:
    dw Toggles.cc_hub_slot_1 + 0x28, Toggles.cc_hub_slot_2 + 0x28
    dw Toggles.cc_hub_slot_3 + 0x28, Toggles.cc_hub_slot_4 + 0x28
}
OS.align(16)
include "../build/char_creator/runtime/runtime.asm"
include "../build/char_creator/runtime/special-hooks.asm"
include "../build/char_creator/runtime/normal-hooks.asm"
include "../build/char_creator/runtime/paired-hooks.asm"
}
