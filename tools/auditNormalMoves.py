#!/usr/bin/env python3
"""Read-only US normal-attack census, traced from ftdata motion descriptors.

Classifies collision timelines, not full move/animation portability. Outputs
Markdown; never emits a runtime donor script or changes game data.
"""
from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ('Mario', 'Fox', 'Donkey', 'Samus', 'Luigi', 'Link', 'Yoshi',
          'Captain', 'Kirby', 'Pikachu', 'Purin', 'Ness')
SLOTS = {
    'Jab': ['Attack11', 'Attack12'],
    'Dash': ['AttackDash'],
    'F-tilt': ['AttackS3Hi', 'AttackS3HiS', 'AttackS3', 'AttackS3LwS', 'AttackS3Lw'],
    'U-tilt': ['AttackHi3F', 'AttackHi3', 'AttackHi3B'],
    'D-tilt': ['AttackLw3'],
    'F-smash': ['AttackS4Hi', 'AttackS4HiS', 'AttackS4', 'AttackS4LwS', 'AttackS4Lw'],
    'U-smash': ['AttackHi4'], 'D-smash': ['AttackLw4'],
    'N-air': ['AttackAirN'], 'F-air': ['AttackAirF'], 'B-air': ['AttackAirB'],
    'U-air': ['AttackAirHi'], 'D-air': ['AttackAirLw'],
}


def us_text(text):
    """Select the source's REGION_US/REGION_JP branches before counting."""
    active, stack, lines = True, [], []
    for line in text.splitlines():
        if line.lstrip().startswith('#if'):
            if 'REGION_' not in line:
                raise ValueError('Unrecognized conditional: ' + line)
            cond = 'REGION_US' in line
            if '!defined' in line:
                cond = not cond
            stack.append((active, cond))
            active = active and cond
        elif line.lstrip().startswith('#else'):
            parent, cond = stack[-1]
            active = parent and not cond
        elif line.lstrip().startswith('#endif'):
            active = stack.pop()[0]
        elif active:
            lines.append(line)
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', '\n'.join(lines), flags=re.S)


def arrays(text, typ):
    return dict(re.findall(typ + r'\s+(\w+)\[.*?\]\s*=\s*\{(.*?)\n\};', text, re.S))


def calls(body):
    # Motion commands in these sources have scalar or symbol arguments.
    return [(m.group(1), [x.strip() for x in m.group(2).split(',') if x.strip()])
            for m in re.finditer(r'(ftMotion\w+)\(([^()]*)\)', body)]


def enum_values(text, name):
    body = re.search(r'typedef enum ' + name + r'\s*\{(.*?)\}', text, re.S)[1]
    body = re.sub(r'//[^\n]*|/\*.*?\*/', '', body, flags=re.S)
    result, value = {}, -1
    for item in body.split(','):
        item = item.strip()
        if not item:
            continue
        parts = item.split('=')
        if len(parts) == 2:
            expr = parts[1].strip()
            value = result[expr] if expr in result else int(expr, 0)
        else:
            value += 1
        result[parts[0].strip()] = value
    return result


def trace(name, scripts):
    out, features = [], set()

    def expand(name, ancestors=()):
        offset = re.fullmatch(r'(\w+)\s*\+\s*(0x[0-9A-Fa-f]+|\d+)', name)
        start_word = 0
        if offset:
            name, byte_offset = offset.groups()
            start_word = int(byte_offset, 0) // 4
        if name not in scripts or name in ancestors:
            features.add('O')
            return []
        commands = calls(scripts[name])
        if start_word:
            # Offsets in ftdata are byte offsets into reloc blobs. For alias
            # tables, walk actual event lengths to find an event boundary.
            word = 0
            for index, (op, args) in enumerate(commands):
                if word == start_word:
                    commands = commands[index:]
                    break
                word += (5 if op in ('ftMotionCommandMakeAttackColl', 'ftMotionCommandMakeAttackCollScaled')
                         else 4 if op in ('ftMotionCommandEffect', 'ftMotionCommandEffectItemHold', 'ftMotionCommandSetDamageCollPartID')
                         else 2 if op in ('ftMotionCommandGoto', 'ftMotionCommandSubroutine', 'ftMotionCommandSetParallelScript',
                                         'ftMotionCommandSetAttackCollOffset', 'ftMotionCommandSetThrow') else 1)
            else:
                features.add('O')
                return []

        def block(start, stop_on_loop=False):
            result, i = [], start
            while i < len(commands):
                op, args = commands[i]
                i += 1
                if op == 'ftMotionCommandLoopEnd':
                    return result, i
                if op == 'ftMotionCommandLoopBegin':
                    nested, i = block(i, True)
                    if any('AttackColl' in op for op, _ in nested):
                        features.add('M')
                    result.extend(nested * min(int(args[0], 0), 100))
                elif op in ('ftMotionCommandSubroutine', 'ftMotionCommandGoto'):
                    result.extend(expand(args[0], ancestors + (name,)))
                    if op.endswith('Goto'):
                        break
                elif op in ('ftMotionCommandEnd', 'ftMotionCommandReturn'):
                    break
                else:
                    result.append((op, args))
            return result, i
        return block(0)[0]

    frame, boxes = 0, {}
    previous = {}
    had_hit = False
    for op, args in expand(name):
        if op == 'ftMotionCommandWaitAsync':
            frame = int(args[0], 0)
        elif op == 'ftMotionCommandWait':
            frame += int(args[0], 0)
        elif op in ('ftMotionCommandMakeAttackColl', 'ftMotionCommandMakeAttackCollScaled'):
            values = tuple(int(x, 0) for x in args)
            old = previous.get(values[0])
            if old and (old[0] != frame) and (old[1][2] != values[2] or old[1][7:10] != values[7:10]):
                features.add('V')
            previous[values[0]] = (frame, values)
            if boxes and any(old[1] != values[1] for old in boxes.values()):
                features.add('M')
            if had_hit and not boxes:
                features.add('M')
            boxes[values[0]] = values
            had_hit = True
            out.append((frame, 'make', values))
            if values[5] == 3:
                features.add('K')  # Weapon/slash geometry requires a separate mapping policy.
        elif op == 'ftMotionCommandClearAttackCollAll':
            if boxes:
                out.append((frame, 'clear', ()))
            boxes.clear()
        elif op == 'ftMotionCommandClearAttackCollID':
            boxes.pop(int(args[0], 0), None)
            out.append((frame, 'clear-one', tuple(args)))
        elif op == 'ftMotionCommandRefreshAttackCollID':
            features.add('M')
            out.append((frame, 'refresh', tuple(args)))
        elif op.startswith('ftMotionCommandSetAttackColl'):
            features.add('P')
            if op.endswith('Offset'):
                features.add('V')
            out.append((frame, 'mutate', tuple(args)))
        elif op.startswith('ftMotionCommandSetHitStatus') or op == 'ftMotionCommandSetDamageCollPartID':
            features.add('H')
    starts = {f for f, op, _ in out if op == 'make'}
    if len(starts) > 1:
        features.add('P')
    if not had_hit or boxes:
        features.add('O')  # No hit or cleanup depends on animation/status end.
    collision_simple = not features.intersection({'M', 'P', 'V', 'O'})
    if collision_simple:
        features.add('S')
    return features, collision_simple


def main():
    source = ROOT / 'src/relocData'
    scripts = {}
    for path in source.glob('*MainMotion.c'):
        scripts.update(arrays(us_text(path.read_text()), r'(?:ftMotionCommand|u32)'))
    scripts.update(arrays(us_text((source / '201_FTCommonMoveset.c').read_text()), r'(?:ftMotionCommand|u32)'))
    motion_ids = enum_values((ROOT / 'src/ft/ftdef.h').read_text(), 'FTCommonMotion')
    tables = arrays(us_text((ROOT / 'src/ft/ftdata.c').read_text()), 'FTMotionDesc')
    detail, summary, unique = [], [], {}
    for fighter in ROSTER:
        # A few tables mix braced entries and unbraced triples (legal C).
        fields = [x.strip() for x in re.sub(r'[{}]', '', tables['dFT' + fighter + 'MotionDescs']).split(',') if x.strip()]
        assert len(fields) % 3 == 0, fighter
        descs = [tuple(fields[i:i + 3]) for i in range(0, len(fields), 3)]
        cells = []
        for slot, ids in SLOTS.items():
            selected = []
            for motion in ids:
                desc = descs[motion_ids['nFTCommonMotion' + motion]]
                if desc[0] not in ('0x00000000', '0') and desc[1] != '0x80000000':
                    selected.append(desc[1])
            if slot == 'Jab':
                selected.extend(desc[1] for desc in descs
                                if desc[0] not in ('0x00000000', '0') and
                                re.search(r'MainMotion_Jab(?:3|Loop)', desc[1]) and
                                'End' not in desc[0] and 'End' not in desc[1])
            selected = list(dict.fromkeys(selected))
            assert selected, (fighter, slot)
            combined = set()
            for name in selected:
                flags, simple = trace(name, scripts)
                unique[fighter, name] = simple
                combined.update(flags)
                detail.append((fighter, slot, name, set(flags), simple))
            if slot == 'Jab':
                combined.add('C')
            if fighter == 'Link' and slot == 'D-air':
                combined.add('C')
            if fighter in ('Ness', 'Pikachu') and slot == 'F-smash':
                combined.add('C')
            if slot.endswith('air'):
                # Inspect the landing descriptor actually selected by the engine.
                landing = {'N-air': 'N', 'F-air': 'F', 'B-air': 'B', 'U-air': 'Hi', 'D-air': 'Lw'}[slot]
                landing_desc = descs[motion_ids['nFTCommonMotionLandingAir' + landing]]
                landing_scripts = [landing_desc[1] if landing_desc[0] not in ('0x00000000', '0')
                                   else descs[motion_ids['nFTCommonMotionLandingAirNull']][1]]
                if any('ftMotionCommandMakeAttackColl' in scripts.get(n, '') for n in landing_scripts):
                    combined.add('L')
            cells.append('/'.join(sorted(combined)))
        summary.append((fighter, cells))
    simple_count = sum(unique.values())
    counts = Counter(flag for _, _, _, flags, _ in detail for flag in flags)
    text = [
        '# Vanilla normal attack census (US)', '',
        'Generated by `python3 tools/auditNormalMoves.py`. No moves are implemented by this audit.', '',
        'The matrix groups angled variants and jab states into 13 families per fighter (156 families). '
        'Descriptors in `src/ft/ftdata.c`, indexed by `FTCommonMotion`, select the actual scripts; '
        'this avoids trusting array names (Link back-air includes a misleadingly named landing array). '
        'Jab3 and rapid-jab states, including setup states with no hit, are also included. US conditional branches are selected before counting.', '',
        '| Code | Category |', '|---|---|',
        '| S | Simple single hit: one bounded collision phase; multiple simultaneous boxes allowed |',
        '| M | Multihit / rehit: collision loops, refresh, new group, or a cleared second hit |',
        '| P | Multiple sequential phases: late-hit parameter changes or later creation |',
        '| V | Moving hitboxes: offset/joint changes during later creation or explicit offset mutation (ordinary animation motion is universal) |',
        '| L | Special landing hitboxes in the selected landing or fallback script |',
        '| C | Special callbacks / state behavior outside the definition |',
        '| K | Unusual skeleton dependency: slash/weapon geometry needs a mapping policy |',
        '| H | Hurtbox changes or invulnerability outside the definition |',
        '| O | Other: unresolved control flow, no hit, or cleanup at animation/status end |', '',
        'Codes overlap; S can coexist with C/K/L/H because collision parameters alone can be simple. '
        'Every aerial also has landing flags and animation-based recovery; those policies are not serialized by the definition.', '',
        '| Fighter | ' + ' | '.join(SLOTS) + ' |',
        '|---|' + '---|' * len(SLOTS),
    ]
    text.extend('| ' + f + ' | ' + ' | '.join(cells) + ' |' for f, cells in summary)
    text += ['', f'**Collision-only coverage: {simple_count}/{len(unique)} unique descriptor-selected script entries '
             f'({100 * simple_count / len(unique):.1f}%).** Angled variants and distinct byte-offset entries are separate; duplicate references are counted once per fighter. '
             'This is an upper bound for normalized numeric collision timelines after each source joint is identified. '
             'It is not the percentage of complete donor moves already portable, and only Mario has a runtime joint map.', '',
             'The current definition has no late-hit phases, rehit/group transitions over time, '
             'looping jab machine, moving-offset events, weapon semantic locations, hurtbox changes, '
             'donor recovery, or donor landing policies. Link down-air bounce/rehit, Ness forward-smash reflector, '
             'Pikachu forward-smash effects, Kirby rapid-jab accessory effects and jab chain transitions '
             'must remain explicit gaps. Kirby down-air can create landing hitboxes.', '',
             '## Per-script evidence', '',
             '| Fighter | Family | Source script | Codes | Collision phase representable |', '|---|---|---|---|---|']
    text.extend(f'| {fighter} | {slot} | `{name}` | {"/".join(sorted(flags))} | {"Yes" if simple else "No"} |'
                for fighter, slot, name, flags, simple in detail)
    target = ROOT / 'docs/custom-move-normal-audit.md'
    target.write_text('\n'.join(text) + '\n')
    print(f'{simple_count}/{len(unique)} collision timelines ({100 * simple_count / len(unique):.1f}%). Report: {target}')


if __name__ == '__main__':
    main()
