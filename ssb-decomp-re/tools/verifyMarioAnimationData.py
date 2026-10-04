"""Check compiled Mario poses against original C playback and world orientations."""
import struct
from customAnimation import ROOT,world,mul,transpose
from generateCustomAnimations import pose_catalog,retarget_basis,rig_map,TARGET_JOINTS
from elfData import read_elf


def verify_mario_poses(native_poses):
    host,sections,symbols=read_elf(ROOT/'build/testCustomMove','<')
    orientation_error=0;translation_error=0;frames=0
    for case in pose_catalog()[0]:
        address,length,index=symbols[case['symbol']]
        assert length==case['frames']*150,(case['symbol'],length)
        start=sections[index][4]+address-sections[index][3]
        source,target,source_bind,target_bind=retarget_basis(case['fighter'],case['flags'])
        poses=native_poses[(case['fighter'],case['name'],case['flags'])]
        assert len(poses)>=case['frames']
        for frame,pose in enumerate(poses[:case['frames']]):
            values=struct.unpack_from('<75h',host,start+frame*150)
            # Use unit scales to preserve Mario's bone lengths, as documented.
            donor=world({j:b for j,b in source.items() if j in pose},{j:(*v[:7],1,1,1) for j,v in pose.items()})
            decoded={j:(*(v/4096 for v in values[i*3:i*3+3]),0,
                        *((tuple(v/16 for v in values[72:75])) if i==0 else target[j].translate),
                        1,1,1) for i,j in enumerate(TARGET_JOINTS)}
            actual=world({j:target[j] for j in TARGET_JOINTS},decoded)
            for j,s in rig_map(case['fighter']).items():
                expected=mul(mul(donor[s][0],transpose(source_bind[s][0])),target_bind[j][0])
                error=max(abs(expected[a][b]-actual[j][0][a][b]) for a in range(3) for b in range(3))
                orientation_error=max(orientation_error,error)
                assert error<0.002,(case['symbol'],frame,j,'world orientation',error)
            ratio=target[4].translate[1]/source[4].translate[1]
            expected=tuple(t+(a-b)*ratio for t,a,b in zip(target[4].translate,donor[4][1],source_bind[4][1]))
            error=max(abs(a-b) for a,b in zip(expected,decoded[4][4:7]))
            translation_error=max(translation_error,error)
            assert error<0.0313,(case['symbol'],frame,'root translation',error)
            frames+=1
    print(f'PASS: {frames} compiled Mario pose frames match native donor world orientations and root translations; max matrix error {orientation_error:.7f}, root error {translation_error:.7f}.')
