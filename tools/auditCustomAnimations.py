#!/usr/bin/env python3
"""Read-only skeleton and figatree audit for the three-move pilot."""
from customAnimation import model, animation, PILOTS, sample, source_size
from customMoveTiming import animation_duration

for fighter in ('Mario','Captain','Fox','Donkey'):
    print('\n'+fighter+' skeleton (native IDs; anim table slot = ID - 4), size '+str(source_size(fighter)))
    for joint,bone in model(fighter).items():
        print(joint,'parent',bone.parent,'mesh' if bone.display else 'pivot','translation',tuple(round(v,2) for v in bone.translate),'rotation',tuple(round(v,3) for v in bone.rotate))
for fighter,motion,name,index in PILOTS:
    path,scripts=animation(name);frames=animation_duration('&ll'+name+'FileID')+1
    poses=sample(fighter,name,frames)
    print('\n'+name+': '+str(len(scripts))+' animated joints; '+str(frames)+' samples; '+str(sum(len(s) for s in scripts.values())*2)+' source script bytes')
    print('First pelvis pose:',poses[0][4],'Last:',poses[-1][4])
