#!/usr/bin/env python3
"""Compile the remaining original neutral phases, collisions and root movement."""
from functools import lru_cache
import re
from auditNormalMoves import ROOT, enum_values, us_text, arrays
from customMoveCatalog import motion_descriptors
from customMoveTiming import animation_duration
from customAnimation import sample, rig, world, source_size, flag_word, transform, add
from generateCustomAnimations import vec
from generateNeutralProjectiles import commands

# Every row is a ground/air pair; Samus never charges while airborne.
PHASES = (('Captain', 'Attack', '', ''), ('Purin', 'Attack', '', ''),
          ('Donkey', 'Start', 'Start', 'Start'), ('Donkey', 'Loop', 'Loop', 'Loop'),
          ('Donkey', 'End', 'End', 'End'), ('Donkey', 'Full', 'Full', 'Full'),
          ('Samus', 'Start', 'Start', 'Start'), ('Samus', 'Loop', 'Loop', 'Loop'),
          ('Samus', 'End', 'End', 'End'), ('Link', 'Throw', '', ''),
          ('Link', 'Empty', 'Empty', 'Empty'), ('Link', 'Catch', 'Get', 'Return'),
          ('Yoshi', 'Grab', '', ''), ('Yoshi', 'Catch', 'Catch', 'Catch'),
          ('Yoshi', 'Release', 'Release', 'Release'))


@lru_cache(None)
def catalog():
    common = enum_values((ROOT/'src/ft/ftdef.h').read_text(), 'FTCommonMotion')
    result = []
    for fighter, phase, ground, air_suffix in PHASES:
        header = ROOT/'src/ft/ftchar'/('ft'+fighter.lower())/('ft'+fighter.lower()+'.h')
        ids = enum_values(header.read_text().replace('nFTCommonMotionSpecialStart', str(common['nFTCommonMotionSpecialStart'])), 'ft'+fighter+'Motion')
        _, descs = motion_descriptors(fighter)
        for air, suffix in enumerate((ground, air_suffix)):
            key = 'nFT'+fighter+'MotionSpecial'+('AirN' if air else 'N')+suffix
            if fighter == 'Samus' and phase == 'Loop': key = 'nFTSamusMotionSpecialNLoop'
            desc = descs[ids[key]]
            duration = animation_duration(desc[0]); flags = flag_word(desc[2])
            name = desc[0][3:-6]; poses = sample(fighter, name, duration+1, flags)
            bones, _ = rig(fighter, flags); size = source_size(fighter)
            events = commands(desc[1]); timeline = {}; tick = wall = 0
            script = []
            for op, args in events:
                if op in ('ftMotionCommandWait', 'ftMotionCommandWaitAsync'):
                    tick = int(args[0], 0) if op.endswith('Async') else tick+int(args[0], 0)
                    wall = max(wall, tick)
                elif 'AttackColl' in op or op.startswith('ftMotionCommandSetFlag'):
                    a = [int(v, 0) for v in args]
                    timeline.setdefault(wall, []).append((op, a))
                    script.append('ftMotionCommandWaitAsync('+str(wall)+')')
                    a = list(a)
                    if 'MakeAttackColl' in op:
                        assert len(a) == 18 and 0 <= a[0] < 4
                        a[2] = 0  # TopN; the donor trajectory supplies the actual position.
                    script.append(op+'('+','.join(map(str, a))+')')
            script.append('ftMotionCommandEnd()')
            active = {}; frames = []; travel = []; spawn = []; anchors = []
            for frame, pose in enumerate(poses):
                for op, a in timeline.get(frame, ()):
                    if 'MakeAttackColl' in op: active[a[0]] = (a[2], tuple(a[7:10]), 'Scaled' in op)
                    elif op == 'ftMotionCommandClearAttackCollAll': active.clear()
                    elif op == 'ftMotionCommandClearAttackCollID': active.pop(a[0], None)
                    elif op == 'ftMotionCommandSetAttackCollOffset' and a[0] in active:
                        j, _, scaled = active[a[0]]; active[a[0]] = (j, tuple(a[1:]), scaled)
                matrices = world(bones, pose); centers = [(0, 0, 0)]*4
                for aid, (j, offset, scaled) in active.items():
                    r, t = matrices[j]
                    if scaled: offset = tuple(v/size for v in offset)
                    centers[aid] = tuple(v*size for v in add(t, transform(r, offset)))
                frames.append((sum(1 << aid for aid in active), centers))
                previous = poses[max(frame-1, 0)].get(1, (0,)*10)
                transn = pose.get(1, (0,)*10)
                travel.append(((transn[6]-previous[6])*size, 0, (transn[4]-previous[4])*size))
                if fighter in ('Samus', 'Link'):
                    joint = 16 if fighter == 'Samus' else 0
                    r, t = matrices[joint]
                    point = add(t, transform(r, (180, 0, 0) if fighter == 'Samus' else (0, 0, 0)))
                    spawn.append((point[2]*size, point[1]*size, -point[0]*size))
                if fighter == 'Yoshi':
                    # Native heavy-item/capture socket is tongue joint 31.
                    point = matrices[31][1]
                    anchors.append((point[2]*size, point[1]*size, -point[0]*size))
            assert not frames[-1][0], (fighter, phase, 'live collision at recovery end')
            result.append(dict(fighter=fighter, phase=phase, air=air, duration=duration,
                               animation=name, flags=flags, events=events, script=script,
                               frames=tuple(frames), travel=tuple(travel), spawn=tuple(spawn), anchors=tuple(anchors)))
    return tuple(result)


def yoshi_interrupt_throws():
    text=us_text((ROOT/'src/relocData/246_YoshiMainMotion.c').read_text())
    scripts=arrays(text,'ftMotionCommand')
    grab=next(body for name,body in scripts.items() if name.startswith('dYoshiMainMotion_EggLay_') and 'ftMotionCommandSetThrow' in body)
    name=re.search(r'ftMotionCommandSetThrow\(\(u32\)(\w+)\)',grab)[1]
    rows=tuple(tuple(int(v.strip(),0) for v in row.split(',')) for row in re.findall(r'\{([^{}]+)\}',arrays(text,'FTThrowHitDesc')[name]))
    assert len(rows)==2 and all(len(row)==7 for row in rows)
    return rows


def render():
    out = ['/* Generated by tools/generateNeutralActions.py. */',
           'FTThrowHitDesc sFTCharBuilderYoshiInterruptThrows[2] = {',
           *('    { '+', '.join(map(str,row))+' },' for row in yoshi_interrupt_throws()), '};']
    for i, c in enumerate(catalog()):
        prefix = 'sFTCharBuilderAction'+str(i)
        out += ['static const ftMotionCommand '+prefix+'Script[] = {']
        out += ['    '+line+',' for line in c['script']]; out += ['};']
        if any(mask for mask, _ in c['frames']):
            out += ['static const FTCustomCollisionFrame '+prefix+'Frames[] = {']
            out += ['    { { '+', '.join(vec(v) for v in centers)+' }, '+str(mask)+' },' for mask, centers in c['frames']]
            out += ['};']
        for label, values in (('Travel', c['travel'] if c['fighter'] in ('Captain', 'Purin') and not c['air'] else ()),
                              ('Spawn', c['spawn']), ('Anchor', c['anchors'])):
            if values:
                out += ['static const Vec3f '+prefix+label+'[] = {']
                out += ['    '+vec(v)+',' for v in values]; out += ['};']
    out += ['static const FTCharBuilderNeutralActionDesc sFTCharBuilderActions[] = {']
    for i, c in enumerate(catalog()):
        prefix = 'sFTCharBuilderAction'+str(i)
        trajectory = prefix+'Frames, 0, '+str(c['duration']+1)+', 0, 0' if any(mask for mask, _ in c['frames']) else 'NULL, 0, 0, 0, 0'
        refs = [prefix+label if values else 'NULL' for label, values in
                (('Travel', c['fighter'] in ('Captain', 'Purin') and not c['air']), ('Spawn', c['spawn']), ('Anchor', c['anchors']))]
        out += ['    { { '+prefix+'Script, ARRAY_COUNT('+prefix+'Script), '+str(c['duration'])+', 0 }, { '+trajectory+' }, '+', '.join(refs)+' },']
    out += ['};']
    return '\n'.join(out)+'\n'


if __name__ == '__main__':
    (ROOT/'src/ft/ftneutralactions.generated.inc').write_text(render(), encoding='utf-8')
    for c in catalog(): print(c['fighter'], c['phase'], c['air'], c['duration'], 'active frames', sum(bool(m) for m, _ in c['frames']))
