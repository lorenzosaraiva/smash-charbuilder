#!/usr/bin/env python3
"""Compile donor curves once and small bind/semantic maps for each body."""
import json
from sharedAnimation import *
from generateCustomAnimations import number,vec

def render():
 cases,rows=catalog();pool=[];shared={};global_curves=[];curve_rows=[];report=[]
 for i,case in enumerate(cases):
  curves,roots=clip_data(i);row=[]
  for keys in curves:
   if keys not in shared:
    shared[keys]=len(global_curves);global_curves.append((len(pool),len(keys)));pool.extend(keys)
   row.append(shared[keys])
  curve_rows.append(row)
  report.append(dict(**case,keys=sum(len(k) for k in curves),root_frames=len(roots)))
 key_out=['/* Generated compressed pose keys, shared by host tests and the ROM bank. */',
      'const FTCustomAnimationKey sFTCustomAnimationKeys[] = {']
 assert all(frame<256 for frame,value in pool), 'key frame overflow'
 assert len(global_curves)<65536, 'curve index overflow'
 key_out.extend('    { '+str(frame)+', '+str((value>>8)&255)+', '+str(value&255)+' },' for frame,value in pool)
 key_out.append('};')
 (ROOT/'src/ft/ftcustomanimationkeys.generated.inc').write_text('\n'.join(key_out)+'\n',encoding='utf-8',newline='\n')
 out=['/* Generated shared donor orientations. Never attach donor assets to a body. */',
      '#ifdef FTCHARBUILDER_ANIMATION_BANK',
      'extern const FTCustomAnimationKey sFTCustomAnimationKeys[];',
      '#else', '#include "ftcustomanimationkeys.generated.inc"', '#endif']
 out.append('const FTCustomAnimationCurve sFTCustomAnimationCurves[] = { '+', '.join('{ '+str(first)+', '+str(count)+', 0 }' for first,count in global_curves)+' };')
 for fighter,flags in sorted({(c['fighter'],c['flags']) for c in cases}):
  symbol='sFTCustomAnimationSourceRig'+fighter+str(flags)
  bones,roles=source_rig(fighter,flags)
  out.append('const FTCustomAnimationSourceBone '+symbol+'Bones[] = {')
  out.extend('    { '+str(b['joint'])+', '+str(b['parent'])+', 0, '+vec(b['inverse'])+' },' for b in bones)
  out.append('};')
  out.append('const FTCustomAnimationSourceRig '+symbol+' = { '+symbol+'Bones, '+str(len(bones))+', { '+', '.join(map(str,roles))+' } };')
 for i,c in enumerate(cases):
  symbol=c['symbol'];curves,roots=clip_data(i)
  out.append('const u16 '+symbol+'Curves[] = { '+', '.join(map(str,curve_rows[i]))+' };')
  out.append('const Vec3h '+symbol+'Root[] = { '+', '.join('{ '+', '.join(map(str,r))+' }' for r in roots)+' };')
  out.append('const FTCustomAnimationClip '+symbol+' = { &sFTCustomAnimationSourceRig'+c['fighter']+str(c['flags'])+', '+symbol+'Curves, '+symbol+'Root, '+', '.join(map(str,(c['frames'],c['loop_start'],c['loop_period'])))+' };')
 for f in ROSTER:
  out.append('const FTCustomAnimationBone sFTCustomAnimationRig'+f+'[] = {')
  for b in body_rig(f):
   out.append('    { '+', '.join(map(str,(b['joint'],b['parent'],b['role'],int(b['required']))))+', '+vec(b['translate'])+', '+vec(b['scale'])+', '+vec(b['local'])+', '+vec(b['world'])+' },')
  out.append('};')
 out.append('const FTCustomAnimationRig sFTCustomAnimationRigs[12] = {')
 out.extend('    { sFTCustomAnimationRig'+f+', '+str(len(body_rig(f)))+' },' for f in ROSTER);out.append('};')
 out.append('const FTCustomAnimationClip *const sFTCustomAnimationClips[12][33] = {')
 for f,row in zip(ROSTER,rows):
  out.append('    { /* '+f+' */ '+', '.join('NULL' if i is None else '&'+cases[i]['symbol'] for i in row)+' },')
 out.append('};')
 out.append('const u8 sFTCustomAnimationSemanticJoints[12][24] = { '+', '.join('{ '+', '.join(map(str,MAPS[f]))+' }' for f in ROSTER)+' };')
 bindings=['/* Generated visual bindings; gameplay definitions stay unchanged. */']
 from specialAnimationAttachments import attachment,frames as attachment_frames
 for i,(phase,index) in enumerate(special_rows()):
  if attachment(phase):
   bindings.append('const FTCustomSpecialAttachmentFrame sFTCustomSpecialAttachment'+str(i)+'[] = {')
   bindings.extend('    { '+vec(r)+', '+vec(t)+', '+vec(s)+', '+str(active)+' },' for r,t,s,active in attachment_frames(phase))
   bindings.append('};')
   joint,part,hide,_=attachment(phase)
   bindings.append('const FTCustomSpecialAttachment sFTCustomSpecialProp'+str(i)+' = { sFTCustomSpecialAttachment'+str(i)+', '+str(joint)+', '+str(part)+', '+str(hide)+' };')
 for i,(phase,index) in enumerate(special_rows()):
  if phase['binding'] is not None:
   bindings.append('const ftMotionCommand sFTCustomSpecialVisual'+str(i)+'[] = { '+', '.join(phase['visual'])+' };')
 bindings.append('const FTCustomSpecialAnimation sFTCustomSpecialAnimations[] = {')
 for i,(phase,index) in enumerate(special_rows()):
  if phase['binding'] is not None:
   prop='&sFTCustomSpecialProp'+str(i) if attachment(phase) else 'NULL'
   bindings.append('    { '+phase['binding']+', &'+cases[index]['symbol']+', sFTCustomSpecialVisual'+str(i)+', '+str(phase['donor'])+', '+prop+' }, /* '+phase['fighter']+' '+phase['phase']+' */')
 bindings.append('};')
 bindings.append('const FTCustomAnimationClip *const sFTCustomSpecialRecoveryClips[12][2] = {')
 for fighter in ROSTER:
  refs=[]
  for label in ('FallSpecial','LandingFallSpecial'):
   matches=[index for phase,index in special_rows() if phase['fighter']==fighter and phase['phase']==label]
   refs.append('&'+cases[matches[0]]['symbol'] if matches else 'NULL')
  bindings.append('    { '+', '.join(refs)+' },')
 bindings.append('};')
 (ROOT/'src/ft/ftspecialanimations.generated.inc').write_text('\n'.join(bindings)+'\n',encoding='utf-8',newline='\n')
 footprint=len(pool)*3+len(global_curves)*8+sum(c['frames']*6+len(curve_rows[i])*2+24 for i,c in enumerate(cases))+sum(len(body_rig(f))*60 for f in ROSTER)+96+1584+sum(len(source_rig(f,flags)[0])*20+32 for f,flags in {(c['fighter'],c['flags']) for c in cases})
 return '\n'.join(out)+'\n',dict(clips=report,rows=rows,shared_keys=len(pool),bytes=footprint)

def main():
 output,report=render()
 from prepareSharedAnimationTest import prepare_math
 prepare_math()
 (ROOT/'src/ft/ftcustomanimationshared.generated.inc').write_bytes(output.encode('utf-8'))
 (ROOT/'build/animation-shared-manifest.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
 print('Generated',len(report['clips']),'shared clips for all twelve bodies;',report['shared_keys'],'keys;',report['bytes'],'data bytes.')
if __name__=='__main__':main()
