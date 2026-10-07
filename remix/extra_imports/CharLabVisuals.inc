// Included inside CharCreator. Private assets survive donor/body identity
// swaps, and are loaded exclusively by the pre-match donor walk.
scope visual_main_file_: {
    sltiu t0, a0, 12
    beqz t0, _none
    sll t0, a0, 2
    li t1, main_file_pointers
    addu t1, t1, t0
    jr ra
    lw v0, 0(t1)
    _none:
    jr ra
    or v0, r0, r0
}

scope ensure_visual_files_: {
    sltiu t0, a0, 12
    beqz t0, _return
    nop
    addiu sp, sp, -0x30
    sw ra, 0x10(sp)
    sw a0, 0x14(sp)
    li t0, 0x80116E10
    sll t1, a0, 2
    addu t0, t0, t1
    lw a1, 0(t0)
    sw a1, 0x18(sp)
    lli t0, 1
    beq a0, t0, _main
    nop
    lli t0, 3
    beq a0, t0, _main
    nop
    lli t0, 6
    beq a0, t0, _main
    nop
    lli t0, 8
    bne a0, t0, _effects
    nop
    _main:
    jal ensure_main_file_
    nop
    _effects:
    lw t0, 0x14(sp)
    lw t2, 0x18(sp)
    lli t1, 8
    beq t0, t1, _cutter
    nop
    lli t1, 3
    beq t0, t1, _samus
    nop
    lli t1, 7
    bne t0, t1, _end
    nop
    lw a0, 0x18(t2) // Captain special2: Falcon Kick flames
    li a1, CharLabRuntime.sCCVisualFiles + 4
    lw v0, 0(a1)
    bnez v0, _punch
    nop
    jal Render.load_file_
    nop
    _punch:
    lw t2, 0x18(sp)
    lw a0, 0x1C(t2) // Captain special3: Falcon Punch flames
    li a1, CharLabRuntime.sCCVisualFiles + 8
    b _load
    nop
    _cutter:
    lw a0, 0x18(t2) // Kirby special2: Final Cutter sword and trails
    li a1, CharLabRuntime.sCCVisualFiles
    b _load
    nop
    _samus:
    lw a0, 0x18(t2) // Samus special2: native grapple glow tree/materials
    li a1, CharLabRuntime.sCCVisualFiles + 12
    _load:
    lw v0, 0(a1)
    bnez v0, _end
    nop
    jal Render.load_file_
    nop
    _end:
    lw ra, 0x10(sp)
    addiu sp, sp, 0x30
    _return:
    jr ra
    nop
}
