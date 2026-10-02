"""Check compiled trajectories and coverage against source/native geometry."""
import struct
from customAnimation import ROOT
from generateCustomCollisions import catalog,stored_frames
from elfData import read_elf


def verify_compiled_collisions(native_geometry):
    host,sections,symbols=read_elf(ROOT/'build/testCustomMove','<');checked=0;cases,rows=catalog()
    for case_id,case in enumerate(cases):
        first,frames=stored_frames(case_id)
        if not frames:continue
        address,length,index=symbols['sFTCustomCollision'+case['label']]
        assert length==len(frames)*52
        start=sections[index][4]+address-sections[index][3]
        for tick,(mask,centers) in enumerate(frames,first):
            values=struct.unpack_from('<12fI',host,start+(tick-first)*52)
            assert values[-1]==mask,(case['label'],tick,'active mask')
            for aid in range(4):
                actual=values[aid*3:aid*3+3];native=native_geometry[case_id][tick][aid]
                assert max(abs(a-b) for a,b in zip(actual,native))<0.001,(case['label'],tick,aid,actual,native)
                # Literal C table also equals the converter's floats, without
                # relying solely on a tolerance against the native oracle.
                assert actual==struct.unpack('<3f',struct.pack('<3f',*centers[aid]))
                checked+=bool(mask&(1<<aid))
    address,length,index=symbols['sFTCustomCollisionTrajectories'];assert length==12*33*20
    start=sections[index][4]+address-sections[index][3]
    for donor,row in enumerate(rows):
        for variant,case_id in enumerate(row):
            record=struct.unpack_from('<5I',host,start+(donor*33+variant)*20)
            if case_id is None:assert record==(0,0,0,0,0);continue
            case=cases[case_id];first,frames=stored_frames(case_id)
            pointer=symbols['sFTCustomCollision'+case['label']][0] if frames else 0
            assert record==(pointer,first,len(frames),case['loop_start'],case['loop_period']),(donor,variant,record)
    print(f'PASS: all 396 registry entries and {checked} compiled active centers match donor scheduling/native geometry.')
