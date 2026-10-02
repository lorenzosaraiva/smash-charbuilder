"""One descriptor/fallback catalog for normal scripts and collision trajectories."""
from functools import lru_cache
import re
from auditNormalMoves import ROOT,ROSTER,SLOTS,arrays,enum_values,us_text
from customMoveTiming import animation_duration,landing_duration

MOTIONS=tuple(m for family in SLOTS.values() for m in family)+tuple('LandingAir'+m for m in ('N','F','B','Hi','Lw'))+('Jab3','RapidStart','RapidLoop','RapidEnd')
EXTRA_PATTERNS=(r'MainMotion_Jab3',r'AnimJabLoopStart',r'AnimJabLoopFile',r'AnimJabLoopEnd')

@lru_cache(None)
def motion_descriptors(fighter):
    tables=arrays(us_text((ROOT/'src/ft/ftdata.c').read_text()),'FTMotionDesc')
    ids=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTCommonMotion')
    fields=[x.strip() for x in re.sub(r'[{}]','',tables['dFT'+fighter+'MotionDescs']).split(',') if x.strip()]
    return ids,[tuple(fields[i:i+3]) for i in range(0,len(fields),3)]

@lru_cache(None)
def source_scripts():
    scripts={}
    for path in (ROOT/'src/relocData').glob('*MainMotion.c'):
        scripts.update(arrays(us_text(path.read_text()),r'(?:ftMotionCommand|u32)'))
    scripts.update(arrays(us_text((ROOT/'src/relocData/201_FTCommonMoveset.c').read_text()),r'(?:ftMotionCommand|u32)'))
    return scripts

@lru_cache(None)
def extra_ids(fighter):
    _,descs=motion_descriptors(fighter)
    return tuple(next((i for i,d in enumerate(descs) if re.search(pattern,','.join(d))),-1) for pattern in EXTRA_PATTERNS)

@lru_cache(None)
def resolved_moves(fighter):
    from generateCustomMoves import expand
    ids,descs=motion_descriptors(fighter);extras=extra_ids(fighter);result=[]
    for index,motion in enumerate(MOTIONS):
        null_landing=False
        if index>=29:
            extra=extras[index-29]
            if extra>=0:desc=descs[extra]
            elif motion in ('Jab3','RapidLoop'):desc=descs[ids['nFTCommonMotionAttack11']]
            else:desc=('1','dCustomEmpty','0')
        else:desc=descs[ids['nFTCommonMotion'+motion]]
        if desc[0] in ('0','0x00000000') or desc[1]=='0x80000000':
            family=next((v for v in SLOTS.values() if motion in v),['LandingAirNull'])
            desc=next(descs[ids['nFTCommonMotion'+m]] for m in family if descs[ids['nFTCommonMotion'+m]][0] not in ('0','0x00000000') and descs[ids['nFTCommonMotion'+m]][1]!='0x80000000')
            null_landing=motion.startswith('LandingAir')
        duration=0 if desc[1]=='dCustomEmpty' else animation_duration(desc[0])
        if null_landing:
            air='AttackAir'+motion.removeprefix('LandingAir')
            duration=landing_duration(desc[0],expand(descs[ids['nFTCommonMotion'+air]][1],source_scripts()))
        result.append((motion,desc,duration))
    return tuple(result)
