#!/usr/bin/env python3
"""Add the separately loaded pose bank to a generated US linker script."""
import sys
from pathlib import Path

source, target = map(Path, sys.argv[1:])
text = source.read_text()
marker = '    /DISCARD/ :'
assert text.count(marker) == 1, 'Unexpected generated linker script'
bank = '''    charbuilder_animation_bank_ROM_START = __romPos;
    .charbuilder_animation_bank 0x80400000 : AT(charbuilder_animation_bank_ROM_START) SUBALIGN(16)
    {
        build/us/src/ft/ftanimationbank.o(.rodata);
        . = ALIGN(16);
    }
    charbuilder_animation_bank_VRAM_END = .;
    __romPos += SIZEOF(.charbuilder_animation_bank);
    ASSERT(charbuilder_animation_bank_VRAM_END < 0x80600000, "Pose bank leaves too little gameplay heap")
    ASSERT(ovl3_VRAM_END <= gSYFramebufferSets, "Fighter overlay overlaps framebuffers")

'''
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(text.replace(marker, bank + marker))
