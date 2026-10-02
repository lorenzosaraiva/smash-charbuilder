"""Read a fighter animation's frame duration without loading foreign models."""
import math
import re
from functools import lru_cache
from auditNormalMoves import ROOT, arrays, us_text

@lru_cache(None)
def animation_duration(file_id):
    match = re.fullmatch(r'&ll(\w+)FileID', file_id)
    assert match, file_id
    paths = list((ROOT/'src/relocData').glob('*_'+match[1]+'.c'))
    assert len(paths) == 1, file_id
    text = us_text(paths[0].read_text())
    joints = arrays(text, 'u16')
    durations = []
    for script in joints.values():
        if not re.search(r'ftAnim\w+\(', script): continue
        duration = 0
        for op, arguments in re.findall(r'(ftAnim\w+)\(([^()]*)\)', script):
            args = [arg.strip() for arg in arguments.split(',')]
            if op in ('ftAnimEnd', 'ftAnimLoop'): break
            if op in ('ftAnimBlock','ftAnimSetFlagsT') or ('Block' in op and op.endswith('T') and 'SetTargetRate' not in op):
                duration += int(args[-1], 0)
        durations.append(duration)
    assert durations and max(durations) > 0, file_id
    # All active joints run each frame; the last ending track ends the move.
    return max(durations)

def landing_duration(file_id, aerial_commands):
    rate = next((int(args[0], 0)/100 for op,args in aerial_commands
                 if op == 'ftMotionCommandSetFlag1' and int(args[0], 0) > 0), 1)
    return math.ceil(animation_duration(file_id)/rate)
