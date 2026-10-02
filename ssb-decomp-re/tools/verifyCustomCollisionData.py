"""Check compiled trajectory bytes against source scheduling and native geometry."""
import struct
from customAnimation import ROOT
from generateCustomCollisions import COLLISION_PILOTS, frames_for
from elfData import read_elf


def verify_compiled_collisions(native_geometry):
    host, sections, symbols = read_elf(ROOT/'build/testCustomMove', '<')
    checked = 0
    for fighter, motion, name, label in COLLISION_PILOTS:
        address, length, index = symbols['sFTCustomCollision'+label]
        frames = frames_for(fighter, motion, name)
        assert length == len(frames)*52
        start = sections[index][4]+address-sections[index][3]
        for tick, (mask, centers) in enumerate(frames):
            values = struct.unpack_from('<12fI', host, start+tick*52)
            assert values[-1] == mask, (label, tick, 'active mask')
            for aid in range(4):
                actual = values[aid*3:aid*3+3]
                native = native_geometry[(fighter, motion)][tick][aid]
                assert max(abs(a-b) for a,b in zip(actual, native)) < 0.001, (label, tick, aid, actual, native)
                checked += bool(mask & (1 << aid))
    print(f'PASS: compiled collision-only tables match native geometry and active windows ({checked} active centers).')
