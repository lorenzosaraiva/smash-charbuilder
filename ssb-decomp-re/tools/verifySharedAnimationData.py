"""Compare every real C retargeted frame/body with native donor poses."""
import struct,subprocess
from sharedAnimation import *
from elfData import read_elf
from prepareSharedAnimationTest import prepare_math

def verify_shared_poses(native_poses):
 cases,_=catalog();prepare_math()
 (ROOT/'build/shared-animation-cases.inc').write_text('static const FTCustomAnimationClip *const sSharedOracleClips[] = { '+', '.join('&'+c['symbol'] for c in cases)+' };\n',encoding='utf-8')
 subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-O1','-Iinclude','-Isrc','-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US','tools/testSharedAnimation.c','-o','build/testSharedAnimation'],cwd=ROOT,check=True)
 raw=subprocess.check_output([str(ROOT/'build/testSharedAnimation')],cwd=ROOT)
 (ROOT/'build/shared-animation-poses.bin').write_bytes(raw)
 cursor=0;maximum=0;root_error=0;checks=0;scalar_error=0
 host,sections,symbols=read_elf(ROOT/'build/testCustomMove','<')
 address,length,index=symbols['sFTCustomAnimationKeys'];start=sections[index][4]+address-sections[index][3]
 pool=[]
 for at in range(start,start+length,3):
  frame,hi,lo=host[at:at+3];value=(hi<<8)|lo
  pool.append((frame,value-65536 if value&32768 else value))
 address,length,index=symbols['sFTCustomAnimationCurves'];start=sections[index][4]+address-sections[index][3]
 global_curves=[struct.unpack_from('<IHH',host,at)[:2] for at in range(start,start+length,8)]
 def evaluate_scalar(keys,frame):
  if frame<=keys[0][0]:return keys[0][1]/ANGLE_QUANT
  if frame>=keys[-1][0]:return keys[-1][1]/ANGLE_QUANT
  for (a,x),(b,y) in zip(keys,keys[1:]):
   if a<=frame<=b:return (x+(y-x)*(frame-a)/(b-a))/ANGLE_QUANT
  raise AssertionError(frame)
 for c in cases:
  if c['loop_start'] and c['loop_period']:
   # Original C playback includes three rapid-jab cycles. Validate that the
   # retained steady cycle can repeat every joint, not only active hitboxes.
   all_poses=native_poses[(c['fighter'],c['name'],c['flags'])]
   d=c['loop_period'];assert len(all_poses)>=3*d+1,c['symbol']
   for first,second in zip(all_poses[d:2*d],all_poses[2*d:3*d]):
    for joint in first:
     assert max(abs((a-b+math.pi)%(2*math.pi)-math.pi) for a,b in zip(first[joint][:3],second[joint][:3]))<0.0001,(c['symbol'],'nonperiodic rotation',joint)
     assert max(abs(a-b) for a,b in zip(first[joint][4:7],second[joint][4:7]))<0.001,(c['symbol'],'nonperiodic translation',joint)
  poses=native_poses[(c['fighter'],c['name'],c['flags'])][:c['frames']]
  assert len(poses)==c['frames'],c['symbol']
  source,roles=source_rig(c['fighter'],c['flags']);ids=tuple(b['joint'] for b in source)
  address,length,index=symbols[c['symbol']+'Curves'];start=sections[index][4]+address-sections[index][3]
  channels=struct.unpack_from('<'+str(len(source)*3)+'H',host,start)
  deltas=[];roots=[]
  bones,_=rig(c['fighter'],c['flags'])
  bind=world(bones,{j:(*b.rotate,0,*b.translate,1,1,1) for j,b in bones.items()})
  for frame,pose in enumerate(poses):
   actual_source=world(bones,{j:(*v[:7],1,1,1) for j,v in pose.items()})
   deltas.append(tuple(qmul(quaternion(actual_source[ids[i]][0]),source[i]['inverse']) for i in roles))
   roots.append(tuple((a-b)/bones[4].translate[1] for a,b in zip(actual_source[4][1],bind[4][1])))
   for i,joint in enumerate(ids):
    for axis in range(3):
     first,count=global_curves[channels[i*3+axis]]
     value=evaluate_scalar(pool[first:first+count],frame)
     expected=(pose[joint][axis]+math.pi)%(2*math.pi)-math.pi
     error=abs((value-expected+math.pi)%(2*math.pi)-math.pi)
     scalar_error=max(scalar_error,error)
     assert error<0.00033,(c['symbol'],frame,joint,axis,error)
  for body in ROSTER:
   target=body_rig(body)
   for frame in range(c['frames']):
    expected_world={0:(0,0,0,1)}
    for bone in target:
     observed=struct.unpack_from('<4f',raw,cursor);cursor+=16
     desired=qmul(deltas[frame][bone['role']],bone['world']) if bone['role']>=0 else qmul(expected_world[bone['parent']],bone['local'])
     expected_world[bone['joint']]=desired
     # Rotation matrices avoid quaternion sign and Euler-wrap ambiguities.
     a,b=qmatrix(observed),qmatrix(desired)
     error=max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(3))
     maximum=max(maximum,error);checks+=1
     assert error<0.008,(c['symbol'],body,frame,bone['joint'],error)
    observed=struct.unpack_from('<3f',raw,cursor);cursor+=12
    expected=tuple(t+d*target[0]['translate'][1] for t,d in zip(target[0]['translate'],roots[frame]))
    error=max(abs(a-b) for a,b in zip(observed,expected));root_error=max(root_error,error)
    assert error<0.055,(c['symbol'],body,frame,'root translation',error)
 from specialAnimationAttachments import attachment,frames as prop_frames
 prop_checks=0
 for phase,index in special_rows():
  spec=attachment(phase)
  if spec is None:continue
  joint=spec[0];bones,_=rig(phase['fighter'],phase['flags'])
  poses=native_poses[(phase['fighter'],phase['name'],phase['flags'])]
  for frame,(r,t,s,active) in enumerate(prop_frames(phase)):
   pose=poses[frame]
   unit={j:(*v[:7],1,1,1) for j,v in pose.items()}
   native_r,_=world(bones,unit)[joint];_,native_t=world(bones,pose)[joint]
   size=source_size(phase['fighter'])
   assert max(abs(a-b*size) for a,b in zip(t,native_t))<0.003,(phase['phase'],'prop translation',frame)
   assert max(abs(a-b*size) for a,b in zip(s,pose[joint][7:10]))<0.003,(phase['phase'],'prop scale',frame)
   observed_r=rotation(r)
   assert max(abs(observed_r[i][j]-native_r[i][j]) for i in range(3) for j in range(3))<0.0001,(phase['phase'],'prop rotation',frame)
   prop_checks+=1
 print(f'PASS: {prop_checks} native blaster/tongue/Stone attachment transforms, including tongue extension scales, match original C poses.')
 assert cursor==len(raw),(cursor,len(raw))
 print(f'PASS: {len(cases)} shared clips on all 12 bodies, {checks} runtime joint-world orientations, original C inverse-trig and native donor poses; max matrix error {maximum:.7f}, root error {root_error:.7f}, scalar compression error {scalar_error:.7f}.')
