// Included inside CharCreator. Values 0/1 and all legacy recipe bits stay stable.
neutral_donors:; dw -1, 1, 0, 4, 9, 11, 7, 10, 2, 3, 5, 6, 8
neutral_choices_by_body:; dw 2, 1, 8, 9, 3, 10, 11, 6, 0, 4, 7, 5
neutral_resources:; dw -1, -1, 0, 1, 2, 3, -1, -1, -1, 4, 5, -1, -1

// PikaShared's generic factory hook reads the caller's saved s1 as FTStruct,
// and caller stack +0x5C as its Thunder owner. Supply the expected ABI even
// when a Clang constructor chose different saved registers/local variables.
scope neutral_weapon_factory_: {
    addiu sp, sp, -0x80
    sw ra, 0x10(sp)
    sw s1, 0x14(sp)
    andi t0, a3, 0xF
    bnez t0, _create
    nop
    lw s1, 0x84(a0)
    sw s1, 0x5C(sp)
    _create:
    jal 0x801655C8
    nop
    lw s1, 0x14(sp)
    lw ra, 0x10(sp)
    addiu sp, sp, 0x80
    jr ra
    nop
}

scope ensure_neutral_files_: {
    lli t0, 1
    beq a0, t0, ensure_laser_file_
    nop
    addiu sp, sp, -0x30
    sw ra, 0x04(sp)
    sw a0, 0x08(sp)
    sltiu t0, a0, 13
    beqz t0, _end
    sll t0, a0, 2
    li t1, neutral_donors
    addu t1, t1, t0
    lw a1, 0(t1)
    li t1, 0x80116E10
    sll t2, a1, 2
    addu t1, t1, t2
    lw t2, 0(t1)
    lli t1, 12
    beq a0, t1, _inhale
    nop
    lli t1, 11
    beq a0, t1, _egg
    li t1, neutral_resources
    addu t1, t1, t0
    lw t1, 0(t1)
    bltz t1, _end
    sll t1, t1, 2
    li a1, CharLabRuntime.sCCNeutralFiles
    addu a1, a1, t1
    lw v0, 0(a1)
    bnez v0, _extra
    nop
    lw a0, 0x14(t2) // donor special1 file ID
    jal Render.load_file_
    nop
    _extra:
    lw t0, 0x08(sp)
    lli t1, 5
    beq t0, t1, _particles
    nop
    lli t1, 4
    bne t0, t1, _end
    nop
    li t0, 0x80116E10 + 9 * 4
    lw t0, 0(t0)
    lw a0, 0x1C(t0)
    li a1, CharLabRuntime.sCCNeutralFiles + 28
    lw v0, 0(a1)
    bnez v0, _particles
    nop
    jal Render.load_file_
    nop
    _particles:
    lw a0, 0x08(sp)
    jal ensure_neutral_particles_
    nop
    b _end
    nop
    _egg:
    // Native egg victims need Yoshi's egg effect, independent of captor body.
    lw a0, 0x1C(t2) // Yoshi special3 file ID
    li a1, CharLabRuntime.sCCNeutralFiles + 24
    lw v0, 0(a1)
    bnez v0, _end
    nop
    jal Render.load_file_
    nop
    b _end
    nop
    _inhale:
    jal ensure_neutral_particles_
    nop
    _end:
    lw ra, 0x04(sp)
    addiu sp, sp, 0x30
    jr ra
    nop
}

scope ensure_neutral_particles_: {
    addiu sp, sp, -0x30
    // Native C may spill all four arguments to the o32 home area 0..0x0F.
    sw ra, 0x10(sp)
    sw a0, 0x18(sp)
    addiu t0, a0, -4 // choice 4 = Pikachu, 5 = Ness
    lli t1, 12
    bne a0, t1, _index
    nop
    lli t0, 2 // Inhale's private Kirby bank
    _index:
    sll t0, t0, 2
    li t1, CharLabRuntime.sCCNeutralParticleBanks
    addu t1, t1, t0
    sw t1, 0x14(sp)
    lw v0, 0(t1)
    bgez v0, _end
    nop
    li t1, neutral_donors
    sll t0, a0, 2
    addu t1, t1, t0
    lw t0, 0(t1)
    li t1, 0x80116E10
    sll t0, t0, 2
    addu t1, t1, t0
    lw t0, 0(t1)
    lw a0, 0x50(t0)
    // Pikachu has no private particle ROM bank. Loading a zero range reads
    // unrelated heap contents as a script descriptor and hangs match setup.
    beqz a0, _common_bank
    nop
    lw a1, 0x54(t0)
    lw a2, 0x58(t0)
    lw a3, 0x5C(t0)
    jal 0x801159F8 // native bank lookup/load, pre-match only
    nop
    b _publish_bank
    nop
    _common_bank:
    li t0, 0x801313C4 // gEFManagerParticleBankID
    lw v0, 0(t0)
    _publish_bank:
    lw t0, 0x14(sp)
    sw v0, 0(t0)
    lw t1, 0x18(sp)
    lli t2, 12
    bne t1, t2, _end
    nop
    jal CharLabRuntime.ccInhaleCaptureParticleBank
    or a0, v0, r0
    lw t0, 0x14(sp)
    lw v0, 0(t0)
    _end:
    lw ra, 0x10(sp)
    addiu sp, sp, 0x30
    jr ra
    nop
}

// The existing one-bit recipe field remains packed exactly as before. Full
// choices occupy unused bytes of the existing 16-byte creator-options payload.
scope export_neutral_choices_: {
    li t0, slot_tables
    lli t1, 4
    li t2, 0x54410000 // TA + four donor nibbles in spare options bytes
    lli t5, 0
    _taunt_loop:
    lw t3, 0(t0)
    lw t3, FIELD_TAUNT * 4(t3)
    lw t4, 0(t3)
    andi t4, t4, 0xF
    sllv t4, t4, t5
    or t2, t2, t4
    sw r0, 0(t3) // append one safe bit without shifting old recipe fields
    addiu t5, t5, 4
    addiu t0, t0, 4
    addiu t1, t1, -1
    bnez t1, _taunt_loop
    nop
    li t0, Toggles.block_char_creator_options + 0x1C
    sw t2, 0(t0)
    li t0, Toggles.block_char_creator_options + 0x14
    li t1, 0x4E535031 // NSP1
    sw t1, 0(t0)
    li t1, slot_tables
    lli t2, 4
    _loop:
    lw t3, 0(t1)
    lw t3, FIELD_NSP * 4(t3)
    lw t3, 0(t3)
    sb t3, 4(t0)
    // Menu.export_ does not mask a value to its declared bit width.
    // Temporarily write its legacy bit; restore all choices after SRAM save.
    lw t4, 0(t1)
    lw t4, FIELD_NSP * 4(t4)
    sltiu t5, t3, 2
    bnez t5, _legacy
    nop
    or t3, r0, r0
    _legacy:
    sw t3, 0(t4)
    addiu t0, t0, 1
    addiu t1, t1, 4
    addiu t2, t2, -1
    bnez t2, _loop
    nop
    jr ra
    nop
}

scope import_neutral_choices_: {
    li t0, Toggles.block_char_creator_options + 0x14
    lw t1, 0(t0)
    li t2, 0x4E535031
    bne t1, t2, _end // pre-upgrade SRAM keeps its native/Fox selections
    li t1, slot_tables
    lli t2, 4
    _loop:
    lw t3, 0(t1)
    lw t3, FIELD_NSP * 4(t3)
    lbu t4, 4(t0)
    sltiu t5, t4, 13
    bnez t5, _valid
    nop
    or t4, r0, r0
    _valid:
    sw t4, 0(t3)
    addiu t0, t0, 1
    addiu t1, t1, 4
    addiu t2, t2, -1
    bnez t2, _loop
    nop
    _end:
    li t0, Toggles.block_char_creator_options + 0x1C
    lw t2, 0(t0)
    srl t3, t2, 16
    lli t4, 0x5441
    li t0, slot_tables
    lli t1, 4
    _taunt_loop:
    lw t5, 0(t0)
    bne t3, t4, _taunt_body
    andi t6, t2, 0xF
    sltiu t7, t6, 12
    bnez t7, _taunt_valid
    nop
    _taunt_body:
    lw t6, FIELD_BODY * 4(t5)
    lw t6, 0(t6)
    sltiu t7, t6, 12
    bnez t7, _taunt_valid
    nop
    lli t6, 0
    _taunt_valid:
    lw t5, FIELD_TAUNT * 4(t5)
    sw t6, 0(t5)
    srl t2, t2, 4
    addiu t0, t0, 4
    addiu t1, t1, -1
    bnez t1, _taunt_loop
    nop
    jr ra
    nop
}

// Inhale can acquire any original Neutral B. Load private weapon/visual files
// before the match so absorbing a fighter never enters the active task heap.
scope ensure_inhale_files_: {
    addiu sp, sp, -0x30
    sw ra, 0x10(sp)
    sw s6, 0x14(sp)
    lli s6, 1
    _loop:
    jal ensure_neutral_files_
    or a0, s6, r0
    li t0, neutral_donors
    sll t1, s6, 2
    addu t0, t0, t1
    jal ensure_visual_files_
    lw a0, 0(t0)
    addiu s6, s6, 1
    sltiu t0, s6, 12
    bnez t0, _loop
    nop
    // Load the inhale bank after copied-move dependencies have initialized.
    jal ensure_neutral_files_
    lli a0, 12
    lw s6, 0x14(sp)
    lw ra, 0x10(sp)
    addiu sp, sp, 0x30
    jr ra
    nop
}
