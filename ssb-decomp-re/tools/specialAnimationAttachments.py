"""Native prop transforms kept outside the borrowing fighter's rig."""
from customAnimation import sample, rig, world, euler, source_size

def attachment(phase):
    fighter,name=phase['fighter'],phase['phase']
    if fighter=='Fox' and name in ('SpecialN','SpecialAirN'):
        return 17,0,0,lambda frame:True
    if fighter=='Yoshi' and name.startswith(('Grab','Catch','Release')):
        return 9,-1,0,lambda frame:(18<=frame<=29 if name.startswith(('Grab','Catch')) else frame<6)
    if fighter=='Kirby' and 'Lw' in name and not name.endswith('End'):
        first=(18 if 'Air' in name else 6) if name.endswith('Start') else 0
        return 6,2,1,lambda frame:frame>=first
    return None

def frames(phase):
    spec=attachment(phase)
    if spec is None:return ()
    joint,part,hide,active=spec;bones,_=rig(phase['fighter'],phase['flags'])
    poses=sample(phase['fighter'],phase['name'],phase['frames'],phase['flags']);size=source_size(phase['fighter'])
    result=[]
    for frame,pose in enumerate(poses):
        unscaled={j:(*v[:7],1,1,1) for j,v in pose.items()}
        r,_=world(bones,unscaled)[joint];_,point=world(bones,pose)[joint]
        result.append((euler(r),tuple(v*size for v in point),tuple(v*size for v in pose[joint][7:10]),int(active(frame))))
    return tuple(result)
