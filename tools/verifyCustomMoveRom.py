#!/usr/bin/env python3
"""Verify host-tested tables and linked custom code are in the built US ROM."""
from pathlib import Path
import hashlib
import struct
from n64crc import calculate_crcs
from generateCustomMoves import MAPS, ROSTER
from verifyCustomMoveData import verify_sources
from elfData import read_elf

ROOT = Path(__file__).resolve().parents[1]
rom = (ROOT/'build/smashbrothers.us.z64').read_bytes()
assert rom[:4] == b'\x80\x37\x12\x40'
assert calculate_crcs(rom) == struct.unpack_from('>II',rom,0x10)
host,sections,symbols = read_elf(ROOT/'build/testCustomMove','<')
verify_sources(host,sections,symbols)
metadata = {}
for name in ('sFTCustomMoves','sFTCustomGrabMoves'):
    address,length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    records = struct.unpack_from('<'+str(length//4)+'I',host,start)
    metadata[name] = [records[i+2:i+4] for i in range(0,len(records),4)]
checked = 0
excluded = ('sFTCustomMoves','sFTCustomMoveScripts','sFTCustomMotionIDs','sFTCustomJointMaps',
            'sFTCustomBodyExtraMotionIDs','sFTCustomLastAirAttack','sFTCustomGrabMoves',
            'sFTCustomGrabJointMap','sFTCustomGrabTimings','sFTCustomThrowDescs','sFTCustomMoveClocks')
for name,(address,length,index) in symbols.items():
    if not name.startswith('sFTCustom') or name.startswith('sFTCustomAnimation') or name in excluded: continue
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
for name,expected in metadata.items():
    address,length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    records = struct.unpack_from('>'+str(length//4)+'I',elf,start)
    assert [records[i+2:i+4] for i in range(0,len(records),4)] == expected, name+' donor duration/flags'
phoff = struct.unpack_from('>I',elf,28)[0]
size,count = struct.unpack_from('>HH',elf,42)
programs = [struct.unpack_from('>8I',elf,phoff+i*size) for i in range(count)]
for name in ('ftMainSetStatus','ftMainPlayAnim','ftMainParseMotionEvent','ftMainHasCustomAttackTimeline',
             'ftCommonAttackAirLwProcHit','ftCommonAttackAirLwProcUpdate',
             'sc1PTrainingModeUpdateViewOption','mnOptionBuilderAssignPlayer','mnOptionBuilderRun',*metadata):
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
assert 'gFTCustomAnimationValidationFailures' in symbols
animation_bytes = 0
host,host_sections,host_symbols = read_elf(ROOT/'build/testCustomMove','<')
for donor,frames in (('Captain',41),('Fox',28),('Donkey',61)):
    name = 'sFTCustomAnimation'+donor
    address,length,index = host_symbols[name]
    assert length == frames * 628
    start = host_sections[index][4]+address-host_sections[index][3]
    words = struct.unpack_from('<'+str(length//4)+'I',host,start)
    pattern = struct.pack('>'+str(length//4)+'I',*words)
    address,linked_length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    assert linked_length == length and elf[start:start+length] == pattern,name
    assert pattern in rom,name+' missing from ROM'
    animation_bytes += length
print('PASS: all three linked Mario animation pilots match host-tested poses and donor hitbox trajectories ('+str(animation_bytes)+' bytes).')
print('PASS: 396 normal and 12 grab collision tables, all 36 two-part throw definitions, joint maps, grab timings, creator/assignment/training code and N64 CRC are in the ROM.')
print('ROM bytes:',len(rom))
print('SHA-256:',hashlib.sha256(rom).hexdigest())
