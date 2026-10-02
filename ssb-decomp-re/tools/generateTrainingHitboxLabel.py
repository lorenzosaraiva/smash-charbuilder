#!/usr/bin/env python3
"""Compose HITBOX from the ROM's own menu letters at a readable 2x size."""
import re
import struct
from pathlib import Path
import relocSpriteTool as sprites

ROOT = Path(__file__).resolve().parents[1]
sprites._bind_version('us')
data = Path(sprites.get_binary_path(33)).read_bytes()
relocs = sprites.parse_reloc_chain(data, sprites.parse_csv_entry(33)['reloc_intern_offset'])
header = (ROOT/'include/reloc_data.us.h').read_text()
letters = []
for letter in 'HITBOX':
    offset = int(re.search('llMNCommonFontsLetter'+letter+r'Sprite; // (0x\w+)',header)[1],16)
    sprite = sprites.parse_sprite(data,offset)
    bitmap_offset = relocs[offset+52]
    bitmap = struct.unpack_from('>4hI2h',data,bitmap_offset)
    width, stride, height = bitmap[0],bitmap[1],bitmap[5]
    assert sprite['bmfmt']==4 and sprite['bmsiz']==0 and sprite['nbitmaps']==1
    start = relocs[bitmap_offset+8]
    pixels = sprites.unswizzle_n64_texture(data[start:start+stride*height//2],stride,height,4,0)
    letters.append([[((pixels[y*stride//2+x//2] >> (0 if x%2 else 4)) & 15) for x in range(width)] for y in range(height)])
visible_width = (sum(len(letter[0]) for letter in letters)+len(letters)-1)*2
stride = (visible_width+15)//16*16
height = max(len(letter) for letter in letters)*2
canvas = [[0]*stride for _ in range(height)]
x = 0
for letter in letters:
    for y,row in enumerate(letter):
        for column,value in enumerate(row):
            for dx in (0,1):
                for dy in (0,1): canvas[y*2+dy][x+column*2+dx]=value
    x += (len(letter[0])+1)*2
texture = bytes(row[i]<<4 | row[i+1] for row in canvas for i in range(0,stride,2))
# The engine loads Sprite textures with LoadBlock. Store odd rows shuffled.
texture = sprites.unswizzle_n64_texture(texture,stride,height,4,0)
out = ['/* Generated from MNCommonFonts by tools/generateTrainingHitboxLabel.py. */',
       'static u8 sSC1PTrainingHitboxPixels[] = {']
out += ['    '+','.join('0x%02X'%byte for byte in texture[i:i+16])+',' for i in range(0,len(texture),16)]
out += ['};',f'static Bitmap sSC1PTrainingHitboxBitmap[] = {{ {{ {visible_width}, {stride}, 0, 0, sSC1PTrainingHitboxPixels, {height}, 0 }} }};',
f'''static Sprite sSC1PTrainingHitboxSprite = {{
    0,0,{visible_width},{height},1.0F,1.0F,0,0,SP_TEXSHUF | SP_TRANSPARENT,0,255,255,255,255,
    0,0,NULL,0,1,1,36,{height},{height},G_IM_FMT_I,G_IM_SIZ_4b,
    sSC1PTrainingHitboxBitmap,NULL,NULL,0,0
}};''']
(ROOT/'src/sc/sc1pmode/sc1ptraininghitbox.inc').write_text('\n'.join(out)+'\n')
print(f'Native-font HITBOX label: {visible_width}x{height}.')
