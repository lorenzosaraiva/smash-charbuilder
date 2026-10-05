"""Shared world-orientation curves and explicit semantic maps for twelve rigs."""
from customAnimation import *
from customMoveCatalog import ROSTER,resolved_moves,extra_ids

# Root, pelvis, chest, L shoulder/upper/elbow/hand, neck/head,
# R shoulder/upper/elbow/hand/grip, L hip/thigh/knee/ankle/foot, R equivalents.
MAPS = {
 'Mario':tuple(range(4,28)), 'Fox':tuple(range(4,28)), 'Luigi':tuple(range(4,28)),
 'Donkey':tuple(range(4,18))+tuple(range(19,29)),
 'Captain':tuple(range(4,18))+tuple(range(19,29)),
 'Samus':(4,5,6,7,8,9,10,12,13,14,15,16,17,24,26,27,28,29,30,31,32,33,34,35),
 'Link':(4,5,6,7,8,9,10,22,23,12,13,14,15,16,25,26,27,28,29,30,31,32,33,34),
 'Yoshi':(4,5,6,10,11,12,13,7,8,14,15,16,17,18,21,22,23,24,25,26,27,28,29,30),
 'Kirby':(4,5,5,8,9,10,11,6,6,13,14,15,16,17,20,21,22,23,24,25,26,27,28,29),
 'Pikachu':(4,5,6,7,8,9,10,11,11,15,16,17,18,18,19,20,21,22,23,24,25,26,27,28),
 'Purin':(4,5,5,8,9,10,11,6,6,12,13,14,15,16,19,20,21,22,23,24,25,26,27,28),
 'Ness':tuple(range(4,23))+(24,25,26,27,28),
}
PRIORITY=(0,1,2,8,7,3,4,5,6,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23)
TOLERANCE=0.0002
ANGLE_QUANT=4096

def qmul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return (w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z)

def qnormal(q):
 length=math.sqrt(sum(v*v for v in q));return tuple(v/length for v in q)

def quaternion(m):
 trace=sum(m[i][i] for i in range(3))
 if trace>0:
  s=math.sqrt(trace+1)*2
  q=((m[2][1]-m[1][2])/s,(m[0][2]-m[2][0])/s,(m[1][0]-m[0][1])/s,s/4)
 else:
  i=max(range(3),key=lambda j:m[j][j]);j=(i+1)%3;k=(i+2)%3
  s=math.sqrt(1+m[i][i]-m[j][j]-m[k][k])*2;q=[0]*4
  q[i]=s/4;q[j]=(m[j][i]+m[i][j])/s;q[k]=(m[k][i]+m[i][k])/s;q[3]=(m[k][j]-m[j][k])/s
 return qnormal(q)

def qmatrix(q):
 x,y,z,w=qnormal(q)
 return ((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)),
         (2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)),
         (2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)))

@lru_cache(None)
def body_rig(fighter):
 bones=model(fighter);active=rig(fighter)[0];roles={}
 for role in PRIORITY:roles.setdefault(MAPS[fighter][role],role)
 bind={j:(*b.rotate,0,*b.translate,1,1,1) for j,b in bones.items()}
 transforms=world(bones,bind)
 return tuple(dict(joint=j,parent=b.parent,role=roles.get(j,-1),required=j in active,
                   translate=b.translate,scale=b.scale,local=quaternion(rotation(b.rotate)),world=quaternion(transforms[j][0])) for j,b in bones.items())

@lru_cache(None)
def catalog():
 cases=[];rows=[];seen={}
 for fighter in ROSTER:
  row=[]
  for index,(motion,desc,duration) in enumerate(resolved_moves(fighter)):
   if desc[1]=='dCustomEmpty':row.append(None);continue
   loop=motion=='RapidLoop';native_loop=loop and extra_ids(fighter)[2]>=0
   key=(fighter,desc[0],desc[2],duration,loop)
   if key not in seen:
    seen[key]=len(cases)
    cases.append(dict(fighter=fighter,motion=motion,name=desc[0][3:-6],flags=flag_word(desc[2]),
                      frames=duration*(2 if native_loop else 1)+1,loop_start=duration if native_loop else 0,
                      loop_period=duration if loop else 0,symbol='sFTCustomAnimationShared'+fighter+motion))
   row.append(seen[key])
  rows.append(tuple(row))
 from specialAnimationCatalog import catalog as special_catalog
 for phase in special_catalog():
  key=(phase['fighter'],phase['name'],phase['flags'],phase['frames'],phase['loop_start'],phase['loop_period'])
  if key not in seen:
   seen[key]=len(cases)
   cases.append(dict(fighter=phase['fighter'],motion=phase['phase'],name=phase['name'],flags=phase['flags'],
                     frames=phase['frames'],loop_start=phase['loop_start'],loop_period=phase['loop_period'],
                     symbol='sFTCustomAnimationSpecial'+str(len(cases))))
 from pairedMoves import catalog as paired_catalog
 for phase in paired_catalog():
  for start in range(0,phase['frames'],128):
   frames=min(128,phase['frames']-start)
   key=('pair',phase['fighter'],phase['name'],phase['flags'],start,frames)
   if key not in seen:
    seen[key]=len(cases)
    cases.append(dict(fighter=phase['fighter'],motion=phase['phase'],name=phase['name'],flags=phase['flags'],
                      frames=frames,start_frame=start,loop_start=0,loop_period=0,
                      symbol='sFTCustomAnimationPaired'+str(len(cases))))
 return tuple(cases),tuple(rows)

@lru_cache(None)
def special_rows():
 from specialAnimationCatalog import catalog as special_catalog
 cases,_=catalog()
 result=[]
 for phase in special_catalog():
  index=next(i for i,c in enumerate(cases) if (c['fighter'],c['name'],c['flags'],c['frames'],c['loop_start'],c['loop_period'])==
             (phase['fighter'],phase['name'],phase['flags'],phase['frames'],phase['loop_start'],phase['loop_period']))
  result.append((phase,index))
 return tuple(result)

@lru_cache(None)
def paired_rows():
 from pairedMoves import catalog as paired_catalog
 cases,_=catalog();result=[]
 for phase in paired_catalog():
  indices=[]
  for start in range(0,phase['frames'],128):
   frames=min(128,phase['frames']-start)
   indices.append(next(i for i,c in enumerate(cases) if c.get('start_frame')==start and
       (c['fighter'],c['name'],c['flags'],c['frames'])==(phase['fighter'],phase['name'],phase['flags'],frames)))
  result.append((phase,tuple(indices)))
 return tuple(result)

@lru_cache(None)
def clip_data(index):
 c=catalog()[0][index]
 bones,_=rig(c['fighter'],c['flags'])
 start=c.get('start_frame',0)
 poses=sample(c['fighter'],c['name'],start+c['frames'],c['flags'])[start:]
 bind=world(bones,{j:(*b.rotate,0,*b.translate,1,1,1) for j,b in bones.items()})
 keys=[];roots=[]
 for joint in bones:
  for axis in range(3):
   values=[round(((p[joint][axis]+math.pi)%(2*math.pi)-math.pi)*ANGLE_QUANT) for p in poses]
   kept={0,len(values)-1};pending=[(0,len(values)-1)]
   if max(values)==min(values):kept={0};pending=[]
   while pending:
    first,last=pending.pop()
    if last-first<2:continue
    error,i=max((abs(values[i]-(values[first]+(values[last]-values[first])*(i-first)/(last-first))),i) for i in range(first+1,last))
    if error>TOLERANCE*ANGLE_QUANT:kept.add(i);pending.extend(((first,i),(i,last)))
   keys.append(tuple((i,values[i]) for i in sorted(kept)))
 for p in poses:
  transforms=world(bones,{j:(*v[:7],1,1,1) for j,v in p.items()})
  roots.append(tuple((a-b)/bones[4].translate[1] for a,b in zip(transforms[4][1],bind[4][1])))
 # Dimensionless translations /4096; target root height is applied at runtime.
 roots=tuple(tuple(round(v*4096) for v in point) for point in roots)
 assert all(-32768<=v<=32767 for point in roots for v in point),(c['symbol'],'root overflow')
 return tuple(keys),roots

@lru_cache(None)
def source_rig(fighter,flags):
 bones,_=rig(fighter,flags);original=model(fighter)
 bind=world(bones,{j:(*b.rotate,0,*b.translate,1,1,1) for j,b in bones.items()})
 roles=[]
 for joint in MAPS[fighter]:
  while joint not in bones:joint=original[joint].parent
  roles.append(joint)
 return tuple(dict(joint=j,parent=b.parent,inverse=quaternion(transpose(bind[j][0]))) for j,b in bones.items()),tuple(tuple(bones).index(j) for j in roles)
