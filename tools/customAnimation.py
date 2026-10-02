"""Native US figatree decoding and matrix helpers for the retargeting pilot."""
from dataclasses import dataclass
from functools import lru_cache
import math
import re
import struct
from auditNormalMoves import ROOT, arrays, us_text

TRACKS = ('ROTX','ROTY','ROTZ','TRAI','TRAX','TRAY','TRAZ','SCAX','SCAY','SCAZ')
VALUE_SCALE = (512,512,512,16384,4,4,4,4096,4096,4096)
RATE_SCALE = (512,512,512,16384,32,32,32,8192,8192,8192)
PILOTS = (('Captain','AttackAirLw','FTCaptainAnimAttackAirD',23),
          ('Fox','AttackS3','FTFoxAnimFTilt',5),
          ('Donkey','AttackS4','FTDonkeyAnimFSmash',14))

@dataclass
class Bone:
    parent: int
    translate: tuple
    rotate: tuple
    scale: tuple
    display: bool

@lru_cache(None)
def model(fighter):
    path = next((ROOT/'src/relocData').glob('*_'+fighter+'Model.c'))
    text = us_text(path.read_text())
    name,body = next((n,b) for n,b in arrays(text,'DObjDesc').items() if n.endswith('JointTree'))
    rows = re.findall(r'\{\s*(\d+|0x[\da-fA-F]+),\s*([^,]+),\s*\{([^}]+)\},\s*\{([^}]+)\},\s*\{([^}]+)\}\s*\}',body)
    result,stack = {}, {}
    for i,(depth,display,*vectors) in enumerate(rows):
        depth=int(depth,0)
        if depth==18: break
        assert depth<18, (fighter,depth)
        vectors=[tuple(float(v.strip().rstrip('fF')) for v in vector.split(',')) for vector in vectors]
        result[i+4]=Bone(stack.get(depth-1,0),*vectors,'0x00000000' not in display and display.strip()!='NULL')
        stack[depth]=i+4
    assert result,fighter
    return result

def source_size(fighter):
    text = next((ROOT/'src/relocData').glob('*_'+fighter+'Main.c')).read_text()
    # Keep comments for locating the attribute; select the US conditional.
    active=True;stack=[];lines=[]
    for line in text.splitlines():
        if line.lstrip().startswith('#if'):
            cond='REGION_US' in line
            if '!defined' in line: cond=not cond
            stack.append((active,cond));active=active and cond
        elif line.lstrip().startswith('#else'):
            parent,cond=stack[-1];active=parent and not cond
        elif line.lstrip().startswith('#endif'): active=stack.pop()[0]
        elif active: lines.append(line)
    return float(re.search(r'([\d.]+)f?,\s*/\* size \*/','\n'.join(lines))[1])

@lru_cache(None)
def animation(name):
    path=next((ROOT/'src/relocData').glob('*_'+name+'.c'))
    text=us_text(path.read_text())
    table=next(iter(arrays(text,r'AObjEvent32\s*\*').values()))
    pointers=re.findall(r'\(AObjEvent32\s*\*\)\s*(\w+)|\b(NULL)\b',table)
    scripts=arrays(text,'u16')
    return path, {i+4:encode(scripts[p]) for i,(p,null) in enumerate(pointers) if p}

def encode(body):
    macros={'End':0,'Block':1,'Block0':1,'SetValBlock':2,'SetVal':3,'SetValRateBlock':4,
            'SetValRate':5,'SetTargetRateBlock':6,'SetTargetRate':6,'SetVal0RateBlock':7,
            'SetVal0Rate':8,'SetValAfterBlock':9,'SetValAfter':10,'SetFlags':14}
    def macro(m):
        op=m[1];args=[v.strip() for v in m[2].split(',') if v.strip()]
        toggle=op.endswith('T') or op=='Block'
        if op.endswith('T'):op=op[:-1]
        assert op in macros,op
        flags=0 if not args else sum(1<<TRACKS.index(flag.strip().removeprefix('FT_ANIM_')) for flag in args[0].split('|') if flag.strip()!='0')
        command=(macros[op]<<11)|(flags<<1)|toggle
        return str(command)+(','+args[1] if toggle else '')
    body=re.sub(r'ftAnim(\w+)\(([^()]*)\)',macro,body)
    return [int(v.strip(),0)&65535 for v in body.split(',') if v.strip()]

def signed(word): return word if word<32768 else word-65536
def f32(value): return struct.unpack('<f',struct.pack('<f',value))[0]

class JointPlayback:
    """Mirror command scheduling and AObj scalar interpolation at unit speed."""
    def __init__(self,words,bone):
        self.words=words;self.cursor=0;self.wait=0;self.ended=False
        self.tracks={};self.values=[*bone.rotate,0,*bone.translate,*bone.scale]

    def play(self,frame):
        if not self.ended:
            self.wait-=1 if frame else 0
            while self.wait<=0:
                word=self.words[self.cursor];self.cursor+=1
                op=word>>11;mask=(word>>1)&1023;toggle=word&1
                payload=self.words[self.cursor] if toggle else 0
                self.cursor+=toggle
                if op==0:
                    self.ended=True
                    # Native End adds speed+wait and skips the normal tick.
                    for track in self.tracks.values():track['length']+=1+self.wait
                    break
                if op in (1,14):self.wait+=payload;continue
                assert op in (2,3,4,5,6,7,8,9,10),op
                for i in range(10):
                    if not mask&(1<<i):continue
                    track=self.tracks.setdefault(i,dict(kind=0,base=0,target=0,rate=0,target_rate=0,invert=0,length=0))
                    if op==6:
                        track['target_rate']=f32(signed(self.words[self.cursor])/RATE_SCALE[i]);self.cursor+=1;continue
                    track['base']=track['target']
                    track['target']=f32(signed(self.words[self.cursor])/VALUE_SCALE[i]);self.cursor+=1
                    if op in (4,5,7,8):
                        track['rate']=track['target_rate']
                        track['target_rate']=f32(signed(self.words[self.cursor])/RATE_SCALE[i]) if op in (4,5) else 0
                        self.cursor+=op in (4,5)
                        track['kind']=3
                        if payload:track['invert']=f32(1/payload)
                    elif op in (2,3):
                        track['kind']=2
                        if payload:track['rate']=f32((track['target']-track['base'])/payload)
                        track['target_rate']=0
                    else:
                        track['kind']=1;track['invert']=payload;track['target_rate']=0
                    track['length']=-self.wait-1
                if op in (2,4,7,9):self.wait+=payload
        for i,t in self.tracks.items():
            if not self.ended:t['length']+=1
            length=t['length']
            if t['kind']==1: value=t['target'] if length>=t['invert'] else t['base']
            elif t['kind']==2:value=t['base']+length*t['rate']
            else:
                u=length*t['invert']
                # Hermite interpolation, same polynomial as gcPlayDObjAnimJoint.
                value=t['base']*(2*u**3-3*u**2+1)+t['target']*(3*u**2-2*u**3)+t['rate']*(length*(u*u-2*u+1))+t['target_rate']*(length*(u*u-u))
            self.values[i]=f32(value)
        return tuple(self.values)

def sample(fighter,name,frames):
    bones=model(fighter);path,scripts=animation(name)
    assert set(scripts)<=set(bones),(fighter,name,set(scripts)-set(bones))
    players={joint:JointPlayback(words,bones[joint]) for joint,words in scripts.items()}
    return [{j:players[j].play(frame) if j in players else (*b.rotate,0,*b.translate,*b.scale) for j,b in bones.items()} for frame in range(frames)]

def rotation(r):
    x,y,z=r;sx,sy,sz=map(math.sin,r);cx,cy,cz=map(math.cos,r)
    # Column-vector form of gmCollisionTransformMatrixAll's row-vector matrix.
    return ((cy*cz,sx*sy*cz-cx*sz,cx*sy*cz+sx*sz),
            (cy*sz,sx*sy*sz+cx*cz,cx*sy*sz-sx*cz),(-sy,sx*cy,cx*cy))

def mul(a,b): return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)) for i in range(3))
def transpose(a):return tuple(zip(*a))
def transform(a,v):return tuple(sum(a[i][k]*v[k] for k in range(3)) for i in range(3))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
IDENTITY=rotation((0,0,0))

def world(bones,pose):
    result={0:(IDENTITY,(0,0,0))}
    for j,b in bones.items():
        values=pose[j];local=rotation(values[:3]);sca=values[7:10]
        local=tuple(tuple(local[i][k]*sca[k] for k in range(3)) for i in range(3))
        parent_r,parent_t=result[b.parent]
        result[j]=(mul(parent_r,local),add(parent_t,transform(parent_r,values[4:7])))
    return result

def euler(matrix):
    y=math.asin(max(-1,min(1,-matrix[2][0])))
    if abs(math.cos(y))>1e-7:return (math.atan2(matrix[2][1],matrix[2][2]),y,math.atan2(matrix[1][0],matrix[0][0]))
    return (math.atan2(-matrix[1][2],matrix[1][1]),y,0)
