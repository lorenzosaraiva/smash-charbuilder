"""Native US figatree decoding and matrix helpers for shared donor collision paths."""
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

@lru_cache(None)
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
    selected='\n'.join(lines)
    selected=selected[re.search(r'FTAttributes\s+\w+\s*=\s*\{',selected).end():]
    size=float(re.search(r'([\d.]+)f?,\s*/\* size \*/',selected)[1])
    assert 0.25<=size<=2,(fighter,'invalid fighter size',size)
    return size

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
        if op=='Loop': return ','.join(args)
        toggle=op.endswith('T') or op=='Block'
        if op.endswith('T'):op=op[:-1]
        assert op in macros,op
        flags=0 if not args else sum(1<<TRACKS.index(flag.strip().removeprefix('FT_ANIM_')) for flag in args[0].split('|') if flag.strip()!='0')
        command=(macros[op]<<11)|(flags<<1)|toggle
        return str(command)+(','+args[1] if toggle else '')
    def raw(m):
        op,flags,toggle=[v.strip() for v in m[1].split(',')]
        mask=sum(1<<TRACKS.index(v.strip().removeprefix('FT_ANIM_')) for v in flags.split('|') if v.strip()!='0')
        return str((int(op)<<11)|(mask<<1)|int(toggle))
    body=re.sub(r'_FT_ANIM_CMD\(([^()]*)\)',raw,body)
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
                if op==13:
                    self.cursor+=signed(self.words[self.cursor])//2
                    continue
                payload=self.words[self.cursor] if toggle else 0
                self.cursor+=toggle
                if op==0:
                    self.ended=True
                    # Native End adds speed+wait and skips the normal tick.
                    for track in self.tracks.values():track['length']+=1+self.wait
                    break
                if op in (1,14):self.wait+=payload;continue
                if op==11:
                    for i in range(10):
                        if mask&(1<<i):
                            track=self.tracks.setdefault(i,dict(kind=0,base=0,target=0,rate=0,target_rate=0,invert=0,length=0))
                            track['length']+=payload
                    continue
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
            if not t['kind']: continue
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

@lru_cache(None)
def attributes(fighter):
    text=us_text(next((ROOT/'src/relocData').glob('*_'+fighter+'Main.c')).read_text())
    setup=next(b for n,b in arrays(text,'u32').items() if 'setup_parts' in n)
    setup=[int(v.strip(),0) for v in setup.split(',') if v.strip()]
    hidden=next(iter(arrays(text,'FTHiddenPart').values()))
    hidden=[tuple(int(v.strip(),0) for v in row.split(',')) for row in re.findall(r'\{([^}]+)\}',hidden)]
    scales=next((b for n,b in arrays(text,'Vec3f').items() if 'translate_scales' in n),None)
    scales=[] if scales is None else [tuple(float(v.strip().rstrip('fF')) for v in row.split(',')) for row in re.findall(r'\{([^}]+)\}',scales)]
    return setup,hidden,scales


@lru_cache(None)
def flag_word(flags):
    defines=dict(re.findall(r'#define\s+(FTANIM_FLAG_\w+)\s+(0x[0-9A-Fa-f]+|0)\b',(ROOT/'src/ft/ftdef.h').read_text()))
    return sum(int(defines.get(v.strip(),v.strip()),0) for v in flags.split('|'))


@lru_cache(None)
def rig(fighter,flags=0):
    """Engine setup_parts, hidden-part insertion and figatree traversal order.

    TransN is bound before being detached: its translation drives movement,
    and must not be counted again in the fighter-relative hitbox center.
    """
    source=model(fighter);setup,hidden,_=attributes(fighter)
    children={0:[]};bones={};stack={}
    for i,(j,b) in enumerate(source.items()):
        # Depth is reconstructed from the complete descriptor, but only enabled
        # nodes update the native setup traversal's depth stack.
        depth=0;p=b.parent
        while p: depth+=1;p=source[p].parent
        if not setup[i//32]&(1<<(31-i%32)): continue
        parent=stack[depth-1] if depth else 0
        bones[j]=Bone(parent,b.translate,b.rotate,b.scale,b.display)
        children.setdefault(parent,[]).append(j);children[j]=[];stack[depth]=j
    for i,(joint,parent,partindex,kind) in enumerate(hidden):
        if not flags&(1<<(31-i)): continue
        assert joint not in bones and parent in children,(fighter,flags,joint,parent)
        original=source.get(joint,Bone(parent,(0,0,0),(0,0,0),(1,1,1),False))
        bones[joint]=Bone(parent,original.translate,original.rotate,original.scale,original.display)
        children[joint]=[]
        if kind==3:
            children[joint]=children[parent];children[parent]=[joint]
            for child in children[joint]:bones[child].parent=joint
        elif kind==0:children[parent].append(joint)
        elif kind==1:children[parent].insert(0,joint)
        elif kind==2:children[parent].insert(1,joint)
        else:raise ValueError(kind)
    assert flags&~0x1f == sum(1<<(31-i) for i in range(len(hidden)) if flags&(1<<(31-i))), (fighter,flags)
    order=[]
    def visit(parent):
        for child in children[parent]:order.append(child);visit(child)
    visit(0)
    if 1 in bones:
        for child in children[1]:bones[child].parent=bones[1].parent
    # Parent-before-child order for FK differs from binding order when TransN
    # was detached. It stays a leaf and its own original script is retained.
    pending=dict(bones);ordered={}
    while pending:
        for j,b in list(pending.items()):
            if b.parent==0 or b.parent in ordered:ordered[j]=b;del pending[j]
    return ordered,tuple(order)


def animation_scripts(fighter,name,flags=0):
    path,raw=animation(name);bones,order=rig(fighter,flags)
    assert not set(raw)-set(range(4,4+len(order))), (fighter,name,len(order),set(raw))
    return {order[i-4]:words for i,words in raw.items()}


def sample(fighter,name,frames,flags=0):
    bones,_=rig(fighter,flags);scripts=animation_scripts(fighter,name,flags)
    players={joint:JointPlayback(words,bones[joint]) for joint,words in scripts.items()}
    scales=attributes(fighter)[2] if not flags&4 else []
    result=[]
    for frame in range(frames):
        pose={j:players[j].play(frame) if j in players else (*b.rotate,0,*b.translate,*b.scale) for j,b in bones.items()}
        for j,player in players.items():
            if not scales:continue
            values=list(pose[j])
            for channel in (4,5,6):
                if channel in player.tracks and player.tracks[channel]['kind']:
                    values[channel]=f32(values[channel]*f32(scales[j][channel-4]))
            pose[j]=tuple(values)
        result.append(pose)
    return result

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
