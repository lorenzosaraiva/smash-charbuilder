"""Compare compiled hitboxes and their frame windows with original US scripts."""
import re
import struct
from generateCustomMoves import ROOT, ROSTER, SLOTS, arrays, us_text, enum_values, expand

def verify_sources(host, sections, symbols):
    scripts = {}
    for path in (ROOT/'src/relocData').glob('*MainMotion.c'):
        scripts.update(arrays(us_text(path.read_text()),r'(?:ftMotionCommand|u32)'))
    scripts.update(arrays(us_text((ROOT/'src/relocData/201_FTCommonMoveset.c').read_text()),r'(?:ftMotionCommand|u32)'))
    tables = arrays(us_text((ROOT/'src/ft/ftdata.c').read_text()),'FTMotionDesc')
    header = (ROOT/'src/ft/ftdef.h').read_text()
    ids = enum_values(header,'FTCommonMotion')
    ops = enum_values(header,'FTMotionEvent')
    motions = [m for family in SLOTS.values() for m in family]
    comparisons = tilt_smash = 0
    for fighter in ROSTER:
        fields = [v.strip() for v in re.sub(r'[{}]','',tables['dFT'+fighter+'MotionDescs']).split(',') if v.strip()]
        descs = [fields[i:i+3] for i in range(0,len(fields),3)]
        for motion in motions:
            desc = descs[ids['nFTCommonMotion'+motion]]
            if desc[0] in ('0','0x00000000') or desc[1]=='0x80000000':
                family = next(f for f in SLOTS.values() if motion in f)
                fallback = next(m for m in family if descs[ids['nFTCommonMotion'+m]][0] not in ('0','0x00000000') and descs[ids['nFTCommonMotion'+m]][1]!='0x80000000')
                desc = descs[ids['nFTCommonMotion'+fallback]]
            expected = []
            frame = 0
            for op,args in expand(desc[1],scripts):
                if op=='ftMotionCommandWaitAsync': frame=int(args[0],0)
                elif op=='ftMotionCommandWait': frame+=int(args[0],0)
                elif op in ('ftMotionCommandMakeAttackColl','ftMotionCommandMakeAttackCollScaled'):
                    values = list(map(lambda x:int(x,0),args))
                    # Keep every source field except its foreign skeleton ID.
                    aid,gid,jid,dmg,reb,element,size,x,y,z,angle,kbs,kbw,ga,sd,fl,fk,kbb = values
                    opcode = ops['nFTMotionEvent'+op.removeprefix('ftMotionCommand')]
                    words = [opcode<<26 | aid<<23 | gid<<20 | dmg<<5 | reb<<4 | element,
                             (size&65535)<<16 | (x&65535), (y&65535)<<16 | (z&65535),
                             (angle&1023)<<22 | kbs<<12 | kbw<<2 | ga,
                             (sd&255)<<24 | fl<<21 | fk<<17 | kbb<<7]
                    expected.append((frame,words))
                elif op.startswith('ftMotionCommandClearAttackColl'):
                    expected.append((frame,(op,tuple(args))))
            name = 'sFTCustom'+fighter+motion
            address,length,index = symbols[name]
            start = sections[index][4]+address-sections[index][3]
            words = struct.unpack_from('<'+str(length//4)+'I',host,start)
            actual = []
            frame = cursor = 0
            while cursor < len(words):
                word = words[cursor]; opcode = word>>26; count = 1
                if opcode==ops['nFTMotionEventAsyncWait']: frame=word&0x3FFFFFF
                elif opcode==ops['nFTMotionEventSyncWait']: frame+=word&0x3FFFFFF
                elif opcode in (ops['nFTMotionEventMakeAttackColl'],ops['nFTMotionEventMakeAttackCollScaled']):
                    count=5
                    actual.append((frame,[word&~(127<<13),*words[cursor+1:cursor+5]]))
                elif opcode in (ops['nFTMotionEventClearAttackCollAll'],ops['nFTMotionEventClearAttackCollID']):
                    op = 'ftMotionCommandClearAttackCollAll' if opcode==ops['nFTMotionEventClearAttackCollAll'] else 'ftMotionCommandClearAttackCollID'
                    args = () if op.endswith('All') else (str((word>>23)&7),)
                    actual.append((frame,(op,args)))
                elif opcode==ops['nFTMotionEventSetAttackCollOffset']: count=2
                cursor += count
            assert actual==expected, 'Source hitbox or timing mismatch: '+name
            comparisons += len([e for e in actual if isinstance(e[1],list)])
            if motion in [m for family in list(SLOTS.values())[2:8] for m in family]:
                tilt_smash += len([e for e in actual if isinstance(e[1],list)])
    print(f'PASS: {comparisons} original hitbox definitions and their creation/clear frames, including {tilt_smash} tilt/smash hitboxes; damage, size, offsets, angle and all knockback fields match the donor.')
