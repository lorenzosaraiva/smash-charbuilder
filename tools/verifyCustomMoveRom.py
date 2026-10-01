#!/usr/bin/env python3
"""Verify host-tested tables and linked custom code are in the built US ROM."""
from pathlib import Path
import hashlib
import struct
from n64crc import calculate_crcs
from generateCustomMoves import MAPS, ROSTER

ROOT = Path(__file__).resolve().parents[1]
def read_elf(path, endian):
    data = path.read_bytes()
    assert data[:4] == b'\x7fELF' and data[4] == 1
    shoff = struct.unpack_from(endian+'I',data,32)[0]
    size,count = struct.unpack_from(endian+'HH',data,46)
    sections = [struct.unpack_from(endian+'10I',data,shoff+i*size) for i in range(count)]
    symbols = {}
    for section in sections:
        if section[1] != 2: continue
        strings = sections[section[6]]
        for offset in range(section[4],section[4]+section[5],section[9]):
            name,value,length,info,other,index = struct.unpack_from(endian+'IIIBBH',data,offset)
            start = strings[4]+name
            label = data[start:data.index(b'\0',start)].decode()
            symbols[label] = (value,length,index)
    return data,sections,symbols

rom = (ROOT/'build/smashbrothers.us.z64').read_bytes()
assert rom[:4] == b'\x80\x37\x12\x40'
assert calculate_crcs(rom) == struct.unpack_from('>II',rom,0x10)
host,sections,symbols = read_elf(ROOT/'build/testCustomMove','<')
checked = 0
excluded = ('sFTCustomMoves','sFTCustomMoveScripts','sFTCustomMotionIDs','sFTCustomJointMaps',
            'sFTCustomBodyExtraMotionIDs','sFTCustomLastAirAttack','sFTCustomGrabMoves',
            'sFTCustomGrabJointMap','sFTCustomGrabTimings','sFTCustomThrowDescs')
for name,(address,length,index) in symbols.items():
    if not name.startswith('sFTCustom') or name in excluded: continue
    if not length or sections[index][1] == 8: continue
    start = sections[index][4]+address-sections[index][3]
    words = struct.unpack_from('<'+str(length//4)+'I',host,start)
    pattern = struct.pack('>'+str(length//4)+'I',*words)
    assert pattern in rom,'Missing collision data: '+name
    checked += 1
assert checked == 409,checked  # 396 normals, 12 grabs, one numeric throw table
joint_map = bytes(joint for fighter in ROSTER for joint in MAPS[fighter]+[0])
assert joint_map in rom
for name,format in (('sFTCustomGrabJointMap','B'),('sFTCustomGrabTimings','H')):
    address,length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    count = length//struct.calcsize(format)
    values = struct.unpack_from('<'+str(count)+format,host,start)
    assert struct.pack('>'+str(count)+format,*values) in rom,name
elf,sections,symbols = read_elf(ROOT/'build/smashbrothers.us.elf','>')
phoff = struct.unpack_from('>I',elf,28)[0]
size,count = struct.unpack_from('>HH',elf,42)
programs = [struct.unpack_from('>8I',elf,phoff+i*size) for i in range(count)]
for name in ('ftMainSetStatus','ftMainParseMotionEvent','sc1PTrainingModeUpdateViewOption','mnOptionBuilderAssignPlayer','mnOptionBuilderRun'):
    value,length,index = symbols[name]
    assert length>0,name
    for typ,fileoffset,vaddr,paddr,filesz,memsz,flags,align in programs:
        if typ == 1 and vaddr <= value and value+length <= vaddr+filesz:
            delta = value-vaddr
            assert elf[fileoffset+delta:fileoffset+delta+length] == rom[paddr+delta:paddr+delta+length],name
            break
    else: raise AssertionError('Code missing from ROM: '+name)
assert 'gSCManagerCharBuilderPlayerSlots' in symbols
assert 'gFTCustomMoveValidationFailures' in symbols
print('PASS: 396 normal and 12 grab collision tables, all 36 two-part throw definitions, joint maps, grab timings, creator/assignment/training code and N64 CRC are in the ROM.')
print('ROM bytes:',len(rom))
print('SHA-256:',hashlib.sha256(rom).hexdigest())
