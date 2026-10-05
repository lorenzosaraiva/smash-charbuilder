#!/usr/bin/env python3
"""Production paired phase/ownership/release checks with real fighter layouts."""
import subprocess
from pathlib import Path
from hostFighterHeaders import prepare
from pairedMoves import catalog
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=r'''
#include <ft/fighter.h>
#include <sc/scene.h>
#include <ef/efdef.h>
#include <gm/gmsound.h>
#define FTCHARBUILDER_NEUTRAL_EXTENDED
#define FTCHARBUILDER_PAIRED_MOVES
void bzero(void *p,int n) { unsigned char *q=p;while(n--)*q++=0; }
f32 __cosf(f32 a) { f32 r;__asm__("flds %1; fcos; fstps %0":"=m"(r):"m"(a));return r; }
f32 __sinf(f32 a) { f32 r;__asm__("flds %1; fsin; fstps %0":"=m"(r):"m"(a));return r; }
f32 sqrtf(f32 a) { f32 r;__asm__("flds %1; fsqrt; fstps %0":"=m"(r):"m"(a));return r; }
f32 syUtilsArcTan2(f32 y,f32 x) { f32 r;__asm__("flds %1; flds %2; fpatan; fstps %0":"=m"(r):"m"(y),"m"(x));return r; }
f32 syUtilsArcSin(f32 a) { return syUtilsArcTan2(a,sqrtf(1-a*a)); }
#include "ft/ftcustommove.c.inc"
typedef struct FTCustomSpecialAttachmentFrame { Vec3f rotate,translate,scale; sb32 active; } FTCustomSpecialAttachmentFrame;
typedef struct FTCustomSpecialAttachment { const FTCustomSpecialAttachmentFrame *frames; s32 joint,part; sb32 hide_body; } FTCustomSpecialAttachment;
static GObj* ftCustomAnimationFindLiveEffect(GObj *g,GObj *owner) { return NULL; }
static void ftCustomAnimationStopProp(GObj **g) { *g=NULL; }
static GObj* ftCustomAnimationMakeProp(GObj *g,Gfx *dl) { return NULL; }
DObj* ftMainCharBuilderGetSpecialVisualJoint(FTStruct *fp,s32 donor,s32 joint) { return fp->joints[0]; }
#include "ft/ftpairedmoves.c.inc"
SCCommonData gSCManagerSceneData;
SCCharBuilderSlot gSCManagerCharBuilderSlots[SCCHARBUILDER_SLOTS_COUNT];
s8 gSCManagerCharBuilderPlayerSlots[4]={0,1,2,3};
FTData *dFTManagerDataFiles[32];
static FTAttributes attributes[12];static FTData files[12];static void *main_files[12];
static FTStruct a,v;static GObj ag,vg;static DObj ar,vr,child,model;
static int release_count,released_lr,released_script,returned,queued_start,queued_end;
static int catch_calls,guard_calls,catch_result;
sb32 ftCommonCatchCheckInterruptCommon(GObj *g) { catch_calls++;return catch_result; }
sb32 ftCommonGuardOnCheckInterruptCommon(GObj *g) { guard_calls++;return TRUE; }
void ftKirbySpecialNLoseCopy(GObj *g) {}
#include "ft/ftcommon/ftcommonappeal.c"
void ftMainPlayAnimEventsAll(GObj *g) { g->anim_frame=ftCustomMoveAdvanceClock(ftGetStruct(g),g->anim_frame); }
void ftMainSetStatus(GObj *g,s32 status,f32 begin,f32 speed,u32 flags) {
 FTStruct *fp=ftGetStruct(g);const FTCustomPairPhase *phase=ftMainCharBuilderPairTransition(fp,status);
 ftCustomMoveResetClock(fp);fp->status_id=status;fp->motion_id=nFTCommonMotionWait;
 if(phase)ftMainCharBuilderInstallPairPhase(fp,phase,begin,speed);
 ftMainPlayAnimEventsAll(g);
}
void ftParamSetCaptureImmuneMask(FTStruct *fp,u8 mask) { fp->capture_immune_mask=mask; }
void mpCommonSetFighterAir(FTStruct *fp) { fp->ga=nMPKineticsAir; }
void mpCommonSetFighterWaitOrFall(GObj *g) { returned++;ftMainSetStatus(g,nFTCommonStatusWait,0,1,0); }
void ftCommonThrownSetStatusQueue(GObj *g,s32 first,s32 second) { queued_start=first;queued_end=second; }
void ftCommonThrownSetStatusImmediate(GObj *g,s32 status) { queued_start=-1;queued_end=status; }
void ftCommonThrownProcPhysics(GObj *g) { ftMainCharBuilderPairCaptureTransform(g,&DObjGetStruct(g)->translate.vec.f,&DObjGetStruct(g)->rotate.vec.f); }
void ftCommonThrownReleaseThrownUpdateStats(GObj *g,s32 lr,s32 script,sb32 proc) {
 release_count++;released_lr=lr;released_script=script;ftGetStruct(g)->capture_gobj=NULL;
}
void ftCommonCaptureShoulderedSetStatus(GObj *g) { v.status_id=nFTCommonStatusShouldered; }
void ftDonkeyThrowFWaitSetStatus(GObj *g) { ftMainSetStatus(g,nFTDonkeyStatusThrowFWait,0,1,0); }
void ftPhysicsApplyAirVelTransNAll(GObj *g) {}
void ftPhysicsApplyGroundFrictionOrTransN(GObj *g) {}
void ftKirbyThrowFLandingProcPhysics(GObj *g) {}
void ftPhysicsApplyGroundVelFriction(GObj *g) {}
void ftPhysicsSetGroundVelTransferAir(GObj *g) {}
void ftCommonThrowProcUpdate(GObj *g) {}
#define CHECK(x) do { if(!(x))return __LINE__; }while(0)
static int run(void) {
 int body,donor,player,kind,victim,i,j,t,flags,k,facing;s32 frame;Mtx44f matrix;Vec3f expected,rotation;const FTCustomPairAnchor *anchor;f32 sn,cs,scale;FTCustomMoveClock *clock;
 const FTCustomPairPhase *phase;const FTThrownStatus *pair;Vec3f pos,angles;
 gSCManagerSceneData.scene_curr=nSCKind1PTrainingMode;
 ag.user_data.p=&a;vg.user_data.p=&v;ag.obj=&ar;vg.obj=&vr;vr.child=&child;
 ar.scale.vec.f=(Vec3f){1,1,1};vr.scale.vec.f=(Vec3f){1,1,1};
 for(i=0;i<12;i++){main_files[i]=&attributes[i];files[i].p_file_main=&main_files[i];files[i].o_attributes=0;dFTManagerDataFiles[i]=&files[i];}
 for(body=0;body<12;body++)for(player=0;player<4;player++)for(donor=0;donor<12;donor++)for(kind=1;kind<=2;kind++)for(victim=0;victim<12;victim++) {
  ftMainCharBuilderResetPairedMoves();bzero(&a,sizeof(a));bzero(&v,sizeof(v));
  a.fkind=body;a.pkind=nFTPlayerKindMan;a.player=player;a.player_num=44;a.fighter_gobj=&ag;a.lr=kind==1?1:-1;a.attr=&attributes[body];
  v.fkind=victim;v.player=(player+1)%4;v.player_num=66;v.capture_gobj=&ag;v.attr=&attributes[victim];a.catch_gobj=&vg;
  a.input.pl.stick_range.x=kind==1?0:80;
  gSCManagerCharBuilderSlots[player].is_enabled=TRUE;gSCManagerCharBuilderSlots[player].body=body;
  for(i=13;i<16;i++)gSCManagerCharBuilderSlots[player].attacks[i]=donor;
  CHECK(ftMainCharBuilderTryPairedThrow(&ag,kind==1)==(body!=donor));if(body==donor)continue;
  CHECK(ftCustomPairState(&a)!=NULL);phase=ftCustomPairState(&a)->phase;clock=ftCustomMoveGetClock(&a);
  CHECK(clock && clock->move==&phase->move && clock->frame==1);
  pair=&sFTCustomPairVictimStatuses[donor][victim][kind-1];CHECK(queued_start==pair->status1 && queued_end==pair->status2);
  CHECK(ftMainCharBuilderGetCaptureKind(&v)==donor && a.attr==&attributes[body]);
  CHECK(ftMainCharBuilderPairCaptureTransform(&vg,&pos,&angles));
  v.player_num++;CHECK(!ftMainCharBuilderPairCaptureTransform(&vg,&pos,&angles));v.player_num--;
  a.player_num++;CHECK(ftCustomPairState(&a)==NULL && ftCustomMoveGetClock(&a)==NULL);a.player_num--;
  release_count=returned=0;flags=0;
  for(t=0;t<=phase->move.duration;t++) {
   clock->frame=t;ag.anim_frame=t>=phase->move.duration?-1:t+0.001F;
   /* Execute the generated event stream at its donor wait boundaries. */
   for(i=0;i<phase->move.word_count;i++) {
    u32 word=phase->move.events[i],op=word>>26;
    if(op==nFTMotionEventAsyncWait){flags=word&65535;continue;}
    if(flags!=t) { if(op==nFTMotionEventMakeAttackColl || op==nFTMotionEventMakeAttackCollScaled)i+=4;else if(op==nFTMotionEventSetAttackCollOffset)i++;continue; }
    if(op==nFTMotionEventSetFlag1)a.motion_vars.flags.flag1=word&0x03ffffff;
    if(op==nFTMotionEventSetFlag2)a.motion_vars.flags.flag2=word&0x03ffffff;
    if(op==nFTMotionEventMakeAttackColl || op==nFTMotionEventMakeAttackCollScaled)i+=4;
    else if(op==nFTMotionEventSetAttackCollOffset)i++;
   }
   if(donor==8 && kind==1)break; /* Landing mechanics exercised by live ROM checks. */
   ftMainCharBuilderPairThrowUpdate(&ag);
   if(!ftCustomPairState(&a) || ftCustomPairState(&a)->phase!=phase)break;
  }
  if(donor==2 && kind==1)CHECK(v.status_id==nFTCommonStatusShouldered && a.status_id==nFTDonkeyStatusThrowFWait && release_count==0);
  else if(donor!=8 || kind!=1)CHECK(release_count==1 && a.catch_gobj==NULL && v.capture_gobj==NULL && returned==1 && released_script==(kind==2));
  ftMainCharBuilderResetPairedMoves();CHECK(ftCustomPairState(&a)==NULL);
 }
 for(body=0;body<12;body++)for(player=0;player<4;player++)for(donor=0;donor<12;donor++) {
  ftMainCharBuilderResetPairedMoves();bzero(&a,sizeof(a));
  a.fkind=body;a.pkind=nFTPlayerKindMan;a.player=player;a.player_num=100;a.fighter_gobj=&ag;a.attr=&attributes[body];
  a.passive_vars.kirby.copy_id=nFTKindKirby;
  a.joints[4]=&model;model.scale.vec.f=sFTCustomAnimationRigs[body].bones[0].scale;
  gSCManagerCharBuilderSlots[player].is_enabled=TRUE;gSCManagerCharBuilderSlots[player].body=body;
  gSCManagerCharBuilderSlots[player].taunt=donor;
  a.motion_vars.flags.flag1=1;ftCommonAppealSetStatus(&ag);
  CHECK(a.status_id==nFTCommonStatusAppeal && a.motion_vars.flags.flag1==0);
  CHECK((ftCustomPairState(&a)!=NULL)==(body!=donor));
  if(body!=donor) {
   phase=ftCustomPairState(&a)->phase;clock=ftCustomMoveGetClock(&a);
   CHECK(phase->donor==donor && phase->status==nFTCommonStatusAppeal && clock->frame==0);
   CHECK(clock->move->duration==phase->move.duration && a.attr==&attributes[body]);
   if(donor==nFTKindMario) {
    Vec3f base=sFTCustomAnimationRigs[body].bones[0].scale;
    for(t=0;t<phase->count;t++) {
     clock->frame=t;ftMainCharBuilderApplyPairScale(&a);
     CHECK(model.scale.vec.f.x==base.x*sFTCustomPairMarioTauntScales[t].x);
     CHECK(model.scale.vec.f.y==base.y*sFTCustomPairMarioTauntScales[t].y);
     CHECK(model.scale.vec.f.z==base.z*sFTCustomPairMarioTauntScales[t].z);
     CHECK(ar.scale.vec.f.x==1 && a.attr==&attributes[body]);
    }
    /* Interrupt at full growth; stale identities cannot apply a pose. */
    clock->frame=60;ftMainCharBuilderApplyPairScale(&a);
    a.player_num++;model.scale.vec.f=base;ftMainCharBuilderApplyPairScale(&a);
    CHECK(model.scale.vec.f.x==base.x);a.player_num--;
    ftMainCharBuilderApplyPairScale(&a);CHECK(model.scale.vec.f.x>base.x*2);
   }
  }
  catch_calls=guard_calls=catch_result=0;ftCommonAppealProcInterrupt(&ag);CHECK(catch_calls==0 && guard_calls==0);
  a.motion_vars.flags.flag1=1;ftCommonAppealProcInterrupt(&ag);CHECK(catch_calls==1 && guard_calls==1);
  catch_result=TRUE;ftCommonAppealProcInterrupt(&ag);CHECK(catch_calls==2 && guard_calls==1);
  ftMainSetStatus(&ag,nFTCommonStatusWait,0,1,0);CHECK(ftCustomPairState(&a)==NULL && ftCustomMoveGetClock(&a)==NULL);
  CHECK(model.scale.vec.f.x==sFTCustomAnimationRigs[body].bones[0].scale.x);
  CHECK(model.scale.vec.f.y==sFTCustomAnimationRigs[body].bones[0].scale.y);
  CHECK(model.scale.vec.f.z==sFTCustomAnimationRigs[body].bones[0].scale.z);
 }
 for(body=0;body<12;body++)for(i=0;i<ARRAY_COUNT(sFTCustomPairPhases);i++) {
  const FTCustomAnimationClip *clip;
  phase=&sFTCustomPairPhases[i];a.fkind=gSCManagerCharBuilderSlots[0].body=body;a.player=0;a.player_num=100;a.pkind=nFTPlayerKindMan;
  a.status_id=phase->status;a.motion_id=nFTCommonMotionWait;sFTCustomPairStates[0].owner=&a;sFTCustomPairStates[0].player_num=100;
  sFTCustomPairStates[0].phase=phase;sFTCustomPairStates[0].donor=phase->donor;sFTCustomPairStates[0].status=phase->status;
  ftMainCharBuilderInstallPairPhase(&a,phase,0,1);clock=ftCustomMoveGetClock(&a);
  for(t=0;t<phase->count+100;t++) {
   clock->frame=t;clip=ftCustomAnimationGetPairClip(&a,&frame);j=t;
   if(phase->trajectory.loop_period && j>=phase->trajectory.loop_start)j=phase->trajectory.loop_start+(j-phase->trajectory.loop_start)%phase->trajectory.loop_period;
   if(j>=phase->count)j=phase->count-1;CHECK(clip==phase->clips[j/128] && frame==j%128);
   CHECK(ftCustomCollisionGetFrame(&a)==ftCustomCollisionSample(&phase->trajectory,t));
   a.catch_gobj=&vg;v.capture_gobj=&ag;sFTCustomPairStates[0].victim=NULL;v.player_num=77;
   child.translate.vec.f=(Vec3f){10,-150,30};scale=0.8F+body*0.05F;vr.scale.vec.f=(Vec3f){scale,scale,scale};
   ar.translate.vec.f=(Vec3f){1234,-56,78};anchor=&phase->anchors[j];
   for(facing=-1;facing<=1;facing+=2) {
    ar.rotate.vec.f.y=facing*1.57079632679F;sn=__sinf(ar.rotate.vec.f.y);cs=__cosf(ar.rotate.vec.f.y);
    CHECK(ftMainCharBuilderPairCaptureTransform(&vg,&pos,&angles));
    for(k=0;k<3;k++) {
     const f32 *r=(const f32*)anchor->basis;
     matrix[k][0]=cs*r[k]+sn*r[6+k];matrix[k][1]=r[3+k];matrix[k][2]=-sn*r[k]+cs*r[6+k];
    }
    matrix[3][0]=1234+cs*anchor->translate.x+sn*anchor->translate.z;
    matrix[3][1]=-56+anchor->translate.y;matrix[3][2]=78-sn*anchor->translate.x+cs*anchor->translate.z;
    expected=(Vec3f){-10*scale,150*scale,-30*scale};gmCollisionGetWorldPosition(matrix,&expected);func_ovl2_800EDA0C(matrix,&rotation);
    CHECK(ABS(expected.x-pos.x)<0.001F && ABS(expected.y-pos.y)<0.001F && ABS(expected.z-pos.z)<0.001F);
    CHECK(ABS(rotation.x-angles.x)<0.001F && ABS(rotation.y-angles.y)<0.001F && ABS(rotation.z-angles.z)<0.001F);
   }

  }
  a.player_num++;CHECK(ftCustomAnimationGetPairClip(&a,&frame)==NULL);a.player_num--;
 }
 return 0;
}
void _start(void) { int result=run();__asm__ volatile("int $0x80"::"a"(1),"b"(result):"memory");__builtin_unreachable(); }
'''
    # Use the original engine's matrix-to-Euler routine, including gimbal cases.
    text=(ROOT/'src/gm/gmcollision.c').read_text();first=text.index('void func_ovl2_800EDA0C(');last=text.index('// 0x800EDB88',first)
    world_first=text.index('void gmCollisionGetWorldPosition(');world_last=text.index('// 0x800ED490',world_first)
    source=source.replace('#include "ft/ftcustommove.c.inc"',text[first:last]+'\n'+text[world_first:world_last]+'\n#include "ft/ftcustommove.c.inc"')
    headers=prepare(ROOT,ROOT/'build/paired-host-headers')
    (ROOT/'build/testPairedMoves.c').write_text(source,encoding='utf-8',newline='\n')
    subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-O1','-I'+str(headers),'-Iinclude','-Isrc','-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US','build/testPairedMoves.c','-o','build/testPairedMoves'],cwd=ROOT,check=True)
    subprocess.run([str(ROOT/'build/testPairedMoves')],cwd=ROOT,check=True)
    print('PASS:',len(catalog()),'paired/taunt phases, twelve attacker/victim bodies/four slots, taunt selection/native cancel policy, donor release/facing/cargo, capture ownership and long-clip/loop boundaries.')
if __name__=='__main__':main()
