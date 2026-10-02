#!/usr/bin/env python3
"""Compare the pilot with a saved gameplay-checkpoint ELF/ROM in build/."""
from pathlib import Path
from elfData import read_elf

root=Path(__file__).resolve().parents[1]
before=read_elf(root/'build/animation-baseline.elf','>')[2]
after=read_elf(root/'build/smashbrothers.us.elf','>')[2]
for name in ('ovl2_TEXT_SIZE','ovl2_RODATA_SIZE','ovl2_BSS_SIZE','ovl2_VRAM_END','ovl3_VRAM_END','ovl7_VRAM_END'):
    a,b=before[name][0],after[name][0]
    print(name,hex(a),'=>',hex(b),'delta',b-a)
print('ROM delta:',(root/'build/smashbrothers.us.z64').stat().st_size-(root/'build/animation-baseline.z64').stat().st_size)
print('Training arena before transient allocations:',hex(after['gSYFramebufferSets'][0]-after['ovl7_BSS_END'][0]))
