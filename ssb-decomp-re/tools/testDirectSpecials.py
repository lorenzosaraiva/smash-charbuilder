#!/usr/bin/env python3
"""Compare production Link/Samus/Rest callbacks and physics with native donors."""
import re
import subprocess
from pathlib import Path
from hostFighterHeaders import prepare
from generateSpecialTiming import render, path_catalog, direct_landing_duration

ROOT=Path(__file__).resolve().parents[1]
def function(text,name):
    match=re.search(r'^[\w *]+\b'+name+r'\([^;]*?\)[^\n{;]*\s*\{',text,re.M)
    assert match,name
    start=match.start();brace=text.index('{',start);depth=1;end=brace+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]+'\n'
assert (ROOT/'src/ft/ftspecialtiming.generated.inc').read_text()==render()
assert (direct_landing_duration('Link'),direct_landing_duration('Samus'))==(13,20)
main=(ROOT/'src/ft/ftmain.c').read_text();physics=(ROOT/'src/ft/ftphysics.c').read_text()
clock=(ROOT/'src/ft/ftcustommove.c.inc').read_text()
clock=clock[clock.index('typedef struct FTCustomMoveClock'):clock.index('static s32 ftCustomJointResolve')]
timing=main[main.index('typedef enum FTMainCharBuilderSpecialKind'):main.index('/* PK Thunder')].replace('"ftspecialtiming.generated.inc"','"ft/ftspecialtiming.generated.inc"')
state=main[main.index('static s32 sFTMainCharBuilderSpecialDonors'):main.index('static ftMotionCommand sFTMainCharBuilderSamusSpecialLwScript')]
helpers=''.join(function(main,n) for n in (
    'ftMainCharBuilderGetActiveSpecialDonor','ftMainCharBuilderClearSpecialDonor',
    'ftMainCharBuilderGetSpecialAttributes','ftMainCharBuilderGetSuperJumpRecoveryDonor',
    'ftMainCharBuilderGetSuperJumpAttributes','ftMainCharBuilderStartSuperJumpLandingClock',
    'ftMainCharBuilderActivePath','ftMainCharBuilderGetSpecialTravel',
    'ftMainCharBuilderGetSpecialJoint','ftMainCharBuilderCheckSpecialStatus'))
actual_physics=''.join(function(physics,n) for n in (
    'ftPhysicsSetGroundVelTransferAir','ftPhysicsSetGroundVelFriction','ftPhysicsApplyGroundVelFriction',
    'ftPhysicsApplyGravityClampTVel','ftPhysicsApplyGravityDefault','ftPhysicsApplyFastFall',
    'ftPhysicsClampAirVelX','ftPhysicsClampAirVelXMax','ftPhysicsCheckClampAirVelXDec',
    'ftPhysicsCheckClampAirVelXDecMax','ftPhysicsClampAirVelXStickRange','ftPhysicsApplyAirVelXFriction',
    'ftPhysicsGetAirVelTransN','ftPhysicsApplyAirVelTransNYZ','ftPhysicsApplyAirVelFriction'))
flags=[];indices={}
for case in path_catalog():
    if not ((case['donor'] in (3,5) and 'Hi' in case['phase']) or (case['donor']==10 and 'Lw' in case['phase'])):continue
    wall=0;events={};flag1=0;row=[];air=case['air']
    for op,args in case['events']:
        if op=='ftMotionCommandWait':wall+=int(args[0],0)
        elif op=='ftMotionCommandWaitAsync':wall=max(wall,int(args[0],0))
        else:events.setdefault(wall,[]).append((op,args))
    for frame in range(case['duration']):
        f0=f2=0
        for op,a in events.get(frame,()):
            if op=='ftMotionCommandSetFlag0':f0=int(a[0],0)
            elif op=='ftMotionCommandSetFlag1':flag1=int(a[0],0)
            elif op=='ftMotionCommandSetFlag2':f2=int(a[0],0)
            elif op=='ftMotionCommandSetAirJumpMax':air=1
        row.append('{'+','.join(map(str,(f0,flag1,f2,air)))+'}')
    indices[case['phase']]=len(flags);flags.append('{'+','.join(row)+'}')
flag_data='static const unsigned char sDirectFlags[6][250][4]={'+','.join(flags)+'};\n'
link=(ROOT/'src/ft/ftchar/ftlink/ftlinkspecialhi.c').read_text()
samus=(ROOT/'src/ft/ftchar/ftsamus/ftsamusspecialhi.c').read_text()
rest=(ROOT/'src/ft/ftchar/ftpurin/ftpurinspeciallw.c').read_text()
wp=(ROOT/'src/wp/wplink/wplinkspinattack.c').read_text()
cleanup=main[main.index('    /* Reset, damage'):main.index('    if ((ftMainCharBuilderActivePath(fp) != NULL)',main.index('    /* Reset, damage'))].replace('fighter_gobj','g').replace('(status_id','(status')
source=r'''
#include <ft/fighter.h>
#include <wp/weapon.h>
#include <ft/ftcustommove.h>
#define FTCHARBUILDER_NEUTRAL_EXTENDED
#define FTPURIN_SPECIALLW_STATUS_FLAGS (FTSTATUS_PRESERVE_TEXTUREPART | FTSTATUS_PRESERVE_HITSTATUS | FTSTATUS_PRESERVE_COLANIM)
typedef struct FTCustomCollisionTrajectory { const FTCustomCollisionFrame *frames; s32 first,count,loop_start,loop_period; } FTCustomCollisionTrajectory;
void bzero(void *p,int n) { unsigned char *q=p;while(n--) *q++=0; }
f32 __cosf(f32 a) { f32 r;__asm__("flds %1; fcos; fstps %0":"=m"(r):"m"(a));return r; }
f32 __sinf(f32 a) { f32 r;__asm__("flds %1; fsin; fstps %0":"=m"(r):"m"(a));return r; }
f32 cosf(f32 a) { return __cosf(a); }
f32 sqrtf(f32 a) { f32 r;__asm__("flds %1; fsqrt; fstps %0":"=m"(r):"m"(a));return r; }
FTData *dFTManagerDataFiles[32];
static FTData files[12];static FTAttributes attrs[12],body_attrs;static void *main_files[12];
f32 dMPCollisionMaterialFrictions[16]={1};
'''+clock+timing+state+helpers+actual_physics+flag_data+r'''
static WPStruct weapons[2];static GObj weapon_gobjs[2],effect;static DObj weapon_tops[2];
static int destroyed[2],updates[2];WPDesc dWPLinkSpinAttackWeaponDesc;
GObj* wpManagerMakeWeapon(GObj *parent,WPDesc *desc,Vec3f *pos,u32 flags) {
    int i=ftGetStruct(parent)->player==4;GObj *g=&weapon_gobjs[i];WPStruct *w=&weapons[i];
    bzero(w,sizeof(*w));g->user_data.p=w;g->obj=&weapon_tops[i];w->weapon_gobj=g;
    weapon_tops[i].translate.vec.f=*pos;return g;
}
void wpProcessUpdateHitPositions(GObj *g) { int i=g==&weapon_gobjs[1];updates[i]++; }
void wpMainDestroyWeapon(GObj *g) { destroyed[g==&weapon_gobjs[1]]++; }
sb32 wpMainDecLifeCheckExpire(WPStruct *w) { return --w->lifetime==0; }
GObj* efManagerLinkSpinAttackMakeEffect(GObj *g) { return &effect; }
void gmCollisionGetFighterPartsWorldPosition(DObj *d,Vec3f *v) { *v=d->translate.vec.f; }
static sb32 map_contact=FALSE;
void ftMainSetStatus(GObj *g,s32 status,f32 begin,f32 speed,u32 flags) {
    FTStruct *fp=ftGetStruct(g);
''' + cleanup + r'''
    ftCustomMoveResetClock(fp);fp->status_id=status;
    ftMainCharBuilderCheckSpecialStatus(fp,status>=nFTCommonStatusSpecialStart);
    if(status>=nFTCommonStatusSpecialStart && ftMainCharBuilderGetActiveSpecialDonor(fp)>=0) {
        s32 donor=sFTMainCharBuilderSpecialDonors[fp->player];
        s32 motion=donor==10 ? nFTPurinMotionSpecialLw : donor==3 ? (status==nFTSamusStatusSpecialAirHi ? nFTSamusMotionSpecialAirHi : nFTSamusMotionSpecialHi) : status==nFTLinkStatusSpecialHiEnd ? nFTLinkMotionSpecialHiEnd : status==nFTLinkStatusSpecialAirHi ? nFTLinkMotionSpecialAirHi : nFTLinkMotionSpecialHi;
        sFTMainCharBuilderSpecialMotionIDs[fp->player]=motion;
        ftCustomMoveStartClock(fp,ftMainCharBuilderSpecialTiming(sFTMainCharBuilderSpecialDonors[fp->player],motion),begin);
    } else ftMainCharBuilderStartSuperJumpLandingClock(fp,begin);
}
void ftMainPlayAnimEventsAll(GObj *g) {}
void mpCommonSetFighterAir(FTStruct *fp) { fp->ga=nMPKineticsAir; }
void mpCommonSetFighterGround(FTStruct *fp) { fp->ga=nMPKineticsGround;fp->jumps_used=0; }
sb32 ftParamCheckSetFighterColAnimID(GObj *g,s32 id,s32 ticks) { return FALSE; }
void ftPublicTryPlayFallSpecialReact(GObj *g) {}
void ftMainRunUpdateColAnim(GObj *g) {}
sb32 mpCommonCheckFighterProject(GObj *g) { return FALSE; }
sb32 mpCommonCheckFighterPassCliff(GObj *g,sb32 (*pass)(GObj*)) { return map_contact; }
void mpCommonSetFighterFallOnEdgeBreak(GObj *g) {}
sb32 mpCommonCheckFighterOnFloor(GObj *g) { return !map_contact; }
sb32 mpCommonCheckFighterCeilHeavyCliff(GObj *g) { return map_contact; }
sb32 mpCommonProcFighterOnFloor(GObj *g,void (*callback)(GObj*)) { if(map_contact) callback(g);return !map_contact; }
sb32 mpCommonProcFighterLanding(GObj *g,void (*callback)(GObj*)) { if(map_contact) callback(g);return map_contact; }
void ftCommonCliffCatchSetStatus(GObj *g) { ftMainSetStatus(g,nFTCommonStatusCliffCatch,0,1,0); }
void ftCommonWaitSetStatus(GObj *g) { ftMainSetStatus(g,nFTCommonStatusWait,0,1,0); }
void ftCommonFallSetStatus(GObj *g) { ftMainSetStatus(g,nFTCommonStatusFall,0,1,0); }
void ftCommonLandingFallSpecialSetStatus(GObj *g,sb32 interrupt,f32 speed) {
    FTStruct *fp=ftGetStruct(g);mpCommonSetFighterGround(fp);
    ftMainSetStatus(g,nFTCommonStatusLandingFallSpecial,0,speed,0);
}
sb32 ftAnimEndCheckSetStatus(GObj *g,void (*callback)(GObj*)) { if(g->anim_frame<=0) { callback(g);return TRUE; } return FALSE; }
'''+function((ROOT/'src/ft/ftcommon/ftcommonfallspecial.c').read_text(),'ftCommonFallSpecialSetStatus')+''.join(function(wp,n) for n in (
    'wpLinkSpinAttackProcDead','wpLinkSpinAttackProcUpdate','wpLinkSpinAttackProcMap','wpLinkSpinAttackMakeWeapon'))+link[link.index('struct FTLinkCharBuilderSpinWeapon'):link.index('// // // //')] + ''.join(function(link,n) for n in re.findall(r'^(?:void|sb32) (\w+)\(',link,re.M))+''.join(function(samus,n) for n in re.findall(r'^(?:void|sb32) (\w+)\(',samus,re.M))+''.join(function(rest,n) for n in re.findall(r'^void (\w+)\(',rest,re.M))+r'''
static FTStruct native_fp,body_fp;static GObj native_g,body_g;static DObj native_top,native_trans,body_top;
#define CHECK(c) do { if(!(c)) return __LINE__; } while(0)
#define NEAR(a,b) ((a)-(b)<0.003F && (a)-(b)>-0.003F)
static int test(void) {
    int d,b,p,air,lr,stick,f,i,k;const FTCharBuilderSpecialPath *path;
    for(i=0;i<12;i++) {
        attrs[i].gravity=0.7F+i*0.03F;attrs[i].tvel_base=12+i;attrs[i].tvel_fast=20+i;
        attrs[i].air_speed_max_x=8+i;attrs[i].air_accel=0.15F+i*0.01F;attrs[i].traction=.5F+i*.02F;
        attrs[i].air_friction=0.3F+i*0.01F;attrs[i].jumps_max=2;
        main_files[i]=&attrs[i];files[i].p_file_main=&main_files[i];dFTManagerDataFiles[i]=&files[i];
    }
    body_attrs=attrs[9];body_attrs.jumps_max=6;
    for(k=0;k<3;k++) { d=k==0 ? 3 : k==1 ? 5 : 10;
    for(b=0;b<12;b++) for(p=0;p<4;p++) for(air=0;air<2;air++) for(lr=-1;lr<=1;lr+=2) for(stick=-80;stick<=80;stick+=40) {
        bzero(&body_fp,sizeof(body_fp));bzero(&native_fp,sizeof(native_fp));bzero(&native_trans,sizeof(native_trans));
        body_fp.player=p;body_fp.player_num=11;body_fp.fkind=b;body_fp.attr=&body_attrs;
        native_fp.player=4;native_fp.fkind=d;native_fp.attr=&attrs[d];
        native_fp.joints[0]=&native_top;native_fp.joints[1]=&native_trans;
        body_fp.joints[0]=&body_top;body_fp.joints[1]=NULL;
        native_top.scale.vec.f=(Vec3f){1,1,1};native_top.rotate.vec.f.y=lr*F_CST_DTOR32(90.0F);
        body_top=native_top;body_fp.lr=native_fp.lr=lr;
        body_fp.ga=native_fp.ga=air ? nMPKineticsAir : nMPKineticsGround;
        body_fp.coll_data.floor_angle=native_fp.coll_data.floor_angle=(Vec3f){0,1,0};
        body_g.user_data.p=&body_fp;body_g.obj=&body_top;native_g.user_data.p=&native_fp;native_g.obj=&native_top;
        body_fp.physics.vel_air=(Vec3f){9,3,0};native_fp.physics.vel_air=body_fp.physics.vel_air;
        body_fp.physics.vel_ground.x=native_fp.physics.vel_ground.x=7;
        sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]= d==10 ? nFTMainCharBuilderSpecialKindLw : nFTMainCharBuilderSpecialKindHi;
        sFTMainCharBuilderSpecialMotionIDs[p]= d==3 ? (air ? nFTSamusMotionSpecialAirHi : nFTSamusMotionSpecialHi) : d==5 ? (air ? nFTLinkMotionSpecialAirHi : nFTLinkMotionSpecialHi) : nFTPurinMotionSpecialLw;
        if(d==3) { if(air) { ftSamusSpecialAirHiSetStatus(&body_g);ftSamusSpecialAirHiSetStatus(&native_g); } else { ftSamusSpecialHiSetStatus(&body_g);ftSamusSpecialHiSetStatus(&native_g); } }
        else if(d==5) { if(air) { ftLinkSpecialAirHiSetStatus(&body_g);ftLinkSpecialAirHiSetStatus(&native_g); } else { ftLinkSpecialHiSetStatus(&body_g);ftLinkSpecialHiSetStatus(&native_g); } ftLinkSpecialHiProcStatus(&body_g);ftLinkSpecialHiProcStatus(&native_g); }
        else { if(air) { ftPurinSpecialAirLwSetStatus(&body_g);ftPurinSpecialAirLwSetStatus(&native_g); } else { ftPurinSpecialLwSetStatus(&body_g);ftPurinSpecialLwSetStatus(&native_g); } }
        CHECK(NEAR(body_fp.physics.vel_air.y,native_fp.physics.vel_air.y));
        path=ftMainCharBuilderSpecialPath(d,sFTMainCharBuilderSpecialMotionIDs[p]);CHECK(path);
        i=d==3 ? air : d==5 ? 2+air*2 : 5;
        for(f=0;f<path->move.duration;f++) {
            ftCustomMoveAdvanceClock(&body_fp,0);
            body_fp.motion_vars.flags.flag0=native_fp.motion_vars.flags.flag0=sDirectFlags[i][f][0];
            body_fp.motion_vars.flags.flag1=native_fp.motion_vars.flags.flag1=sDirectFlags[i][f][1];
            body_fp.motion_vars.flags.flag2=native_fp.motion_vars.flags.flag2=sDirectFlags[i][f][2];
            body_fp.ga=native_fp.ga=sDirectFlags[i][f][3] ? nMPKineticsAir : nMPKineticsGround;
            body_fp.input.pl.stick_range.x=native_fp.input.pl.stick_range.x=stick;
            if(path->travel) { native_fp.anim_vel=(Vec3f){0,0,0};native_trans.translate.vec.f=(Vec3f){-path->travel[f].delta.z,path->travel[f].delta.y,path->travel[f].delta.x};native_trans.rotate.vec.f.z=path->travel[f].angle; }
            if(d==3) { if(air) { ftSamusSpecialAirHiProcPhysics(&body_g);ftSamusSpecialAirHiProcPhysics(&native_g); } else { ftSamusSpecialHiProcPhysics(&body_g);ftSamusSpecialHiProcPhysics(&native_g); } }
            else if(d==5) { if(air) { ftLinkSpecialAirHiProcPhysics(&body_g);ftLinkSpecialAirHiProcPhysics(&native_g); } else { ftLinkSpecialHiProcPhysics(&body_g);ftLinkSpecialHiProcPhysics(&native_g); } }
            else { if(air) { ftPhysicsApplyAirVelFriction(&body_g);ftPhysicsApplyAirVelFriction(&native_g); } else { ftPhysicsApplyGroundVelFriction(&body_g);ftPhysicsApplyGroundVelFriction(&native_g); } }
            CHECK(NEAR(body_fp.physics.vel_air.x,native_fp.physics.vel_air.x));CHECK(NEAR(body_fp.physics.vel_air.y,native_fp.physics.vel_air.y));
            CHECK(NEAR(body_fp.physics.vel_ground.x,native_fp.physics.vel_ground.x));
            if(d==5 && !air && (*ftLinkSpecialHiGetWeapon(&body_fp))) {
                CHECK((*ftLinkSpecialHiGetWeapon(&native_fp)));
                CHECK(weapons[0].attack_coll.attack_state==weapons[1].attack_coll.attack_state);
                CHECK(weapons[0].attack_coll.size==weapons[1].attack_coll.size);
                CHECK(weapons[0].lifetime==weapons[1].lifetime);
                CHECK(wpLinkSpinAttackProcUpdate(&weapon_gobjs[0])==wpLinkSpinAttackProcUpdate(&weapon_gobjs[1]));
                wpLinkSpinAttackProcMap(&weapon_gobjs[0]);wpLinkSpinAttackProcMap(&weapon_gobjs[1]);
                CHECK(NEAR(weapons[0].attack_coll.offsets[0].x,weapons[1].attack_coll.offsets[0].x));
                CHECK(NEAR(weapons[0].physics.vel_air.y,weapons[1].physics.vel_air.y));
                body_fp.hitlag_tics=1;ftLinkSpecialHiProcEffect(&body_g);CHECK(weapons[0].is_hitlag_weapon);
                body_fp.hitlag_tics=0;ftLinkSpecialHiProcEffect(&body_g);CHECK(!weapons[0].is_hitlag_weapon);
            }
        }
        if(d==5) { ftLinkSpecialHiProcDamage(&body_g);ftLinkSpecialHiProcDamage(&native_g);CHECK(!(*ftLinkSpecialHiGetWeapon(&body_fp))); }
        if(d==10) {
            /* Sleep continues at the current donor frame across both ground/air transitions. */
            body_g.anim_frame=47;ftPurinSpecialLwSwitchStatusAir(&body_g);
            CHECK(ftCustomMoveGetClock(&body_fp)->duration==250 && ftCustomMoveAdvanceClock(&body_fp,0)==47);
            CHECK(body_fp.physics.vel_air.x<=attrs[d].air_speed_max_x && body_fp.physics.vel_air.x>=-attrs[d].air_speed_max_x);
            body_g.anim_frame=73;ftPurinSpecialAirLwSwitchStatusGround(&body_g);
            CHECK(ftCustomMoveAdvanceClock(&body_fp,0)==73);
        } else {
            body_g.anim_frame=-1;
            if(d==3) ftSamusSpecialHiProcUpdate(&body_g);else ftLinkSpecialAirHiProcUpdate(&body_g);
            CHECK(body_fp.status_id==nFTCommonStatusFallSpecial);
            CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&attrs[d]);
            ftCommonLandingFallSpecialSetStatus(&body_g,FALSE,1);
            CHECK(ftCustomMoveGetClock(&body_fp)->duration==(d==3 ? 20 : 13));
        }
        /* Damage/reset exits execute the production owned-weapon cleanup guard. */
        if(d==5) {
            sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
            ftLinkSpecialHiProcStatus(&body_g);ftLinkSpecialHiProcStatus(&native_g);
            ftMainSetStatus(&body_g,nFTLinkStatusSpecialHi,0,1,0);
            body_fp.motion_vars.flags.flag0=1;native_fp.motion_vars.flags.flag0=1;
            ftLinkSpecialHiMakeWeapon(&body_g,FALSE);ftLinkSpecialHiMakeWeapon(&native_g,FALSE);
            CHECK((*ftLinkSpecialHiGetWeapon(&body_fp)));
            ftLinkSpecialHiProcDamage(&native_g);
            /* Native common setters may overwrite status_vars before SetStatus. */
            if(b!=5) body_fp.status_vars.link.specialhi.spin_attack_gobj=(GObj*)0x3f;
        }
        ftMainSetStatus(&body_g,nFTCommonStatusDamageAir1,0,1,0);
        CHECK(ftMainCharBuilderGetActiveSpecialDonor(&body_fp)==-1 && !ftCustomMoveGetClock(&body_fp));
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&body_attrs);
        if(d==5) {
            CHECK(!(*ftLinkSpecialHiGetWeapon(&body_fp)));
            sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
            ftMainSetStatus(&body_g,nFTLinkStatusSpecialHi,0,1,0);
            ftLinkSpecialHiProcStatus(&body_g);ftLinkSpecialHiProcStatus(&native_g);
            body_fp.motion_vars.flags.flag0=1;native_fp.motion_vars.flags.flag0=1;
            ftLinkSpecialHiMakeWeapon(&body_g,FALSE);ftLinkSpecialHiMakeWeapon(&native_g,FALSE);
            body_g.anim_frame=31;map_contact=TRUE;ftLinkSpecialHiProcMap(&body_g);
            CHECK((*ftLinkSpecialHiGetWeapon(&body_fp))==&weapon_gobjs[0]);
            CHECK(body_fp.status_id==nFTLinkStatusSpecialAirHi && ftCustomMoveAdvanceClock(&body_fp,0)==31);
            CHECK(body_fp.proc_passive==ftLinkSpecialHiProcEffect);
            body_fp.coll_data.mask_stat=MAP_FLAG_FLOOR;ftLinkSpecialAirHiProcMap(&body_g);
            CHECK(body_fp.status_id==nFTLinkStatusSpecialHiEnd && ftCustomMoveGetClock(&body_fp)->duration==40);
            CHECK(!(*ftLinkSpecialHiGetWeapon(&body_fp)));ftLinkSpecialHiProcDamage(&native_g);
            body_g.anim_frame=-1;ftLinkSpecialHiEndProcUpdate(&body_g);
            CHECK(body_fp.status_id==nFTCommonStatusWait);
            sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
            body_fp.coll_data.mask_stat=MAP_FLAG_CLIFF_MASK;ftLinkSpecialAirHiProcMap(&body_g);
            CHECK(body_fp.status_id==nFTCommonStatusCliffCatch && !ftCustomMoveGetClock(&body_fp));
        } else if(d==3) {
            body_fp.coll_data.floor_flags=MAP_VERTEX_COLL_PASS;body_fp.input.pl.stick_range.y=-80;
            CHECK(!ftSamusSpecialHiProcPass(&body_g));body_fp.input.pl.stick_range.y=80;CHECK(ftSamusSpecialHiProcPass(&body_g));
            sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
            body_fp.ga=nMPKineticsAir;body_fp.physics.vel_air.y=-3;body_fp.coll_data.mask_stat=MAP_FLAG_FLOOR;map_contact=TRUE;
            ftSamusSpecialHiProcMap(&body_g);
            CHECK(body_fp.status_id==nFTCommonStatusLandingFallSpecial && ftCustomMoveGetClock(&body_fp)->duration==20);
            sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
            body_fp.ga=nMPKineticsAir;body_fp.coll_data.mask_stat=MAP_FLAG_CLIFF_MASK;
            ftSamusSpecialHiProcMap(&body_g);CHECK(body_fp.status_id==nFTCommonStatusCliffCatch && !ftCustomMoveGetClock(&body_fp));
        }
        map_contact=FALSE;
    }}
    /* A recycled fighter must never read a stale status union as a weapon. */
    body_fp.player=0;body_fp.player_num=77;body_fp.status_id=nFTLinkStatusSpecialHi;
    sFTMainCharBuilderSpecialDonors[0]=5;sFTMainCharBuilderSpecialKinds[0]=nFTMainCharBuilderSpecialKindHi;
    sFTMainCharBuilderSpecialMotionIDs[0]=nFTLinkMotionSpecialHi;
    ftCustomMoveStartClock(&body_fp,ftMainCharBuilderSpecialTiming(5,nFTLinkMotionSpecialHi),0);
    (*ftLinkSpecialHiGetWeapon(&body_fp))=(GObj*)0x3f;
    body_fp.player_num++;
    CHECK(!ftCustomMoveGetClock(&body_fp));
    ftMainSetStatus(&body_g,nFTCommonStatusWait,0,1,0);
    CHECK(ftMainCharBuilderGetActiveSpecialDonor(&body_fp)==-1);
    CHECK(destroyed[0]==destroyed[1] && destroyed[0]>0 && updates[0]==updates[1]);
    return 0;
}
void _start(void) {
    int r=test();if(r) { char msg[]="Direct special CHECK line 0000\n";int i,v=r;
        for(i=28;i>=25;i--) {msg[i]='0'+v%10;v/=10;}
        __asm__ volatile("int $0x80"::"a"(4),"b"(2),"c"(msg),"d"(sizeof(msg)-1):"memory"); }
    __asm__ volatile("int $0x80"::"a"(1),"b"(r):"memory");__builtin_unreachable();
}
'''
build=ROOT/'build';headers=prepare(ROOT,build/'direct-host-headers')
(build/'testDirectSpecials.c').write_text(source)
subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-O1',
    '-I'+str(headers),'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C',
    '-D_MIPS_SZLONG=32','-DREGION_US',str(build/'testDirectSpecials.c'),'-o',str(build/'testDirectSpecials')],check=True)
subprocess.run([str(build/'testDirectSpecials')],check=True)
print('PASS: production Link/Samus/Rest movement on 12 bodies/four slots/both facings, grounded spin weapon flags/lifetime/expansion/hitlag/cleanup, donor recovery and continuing Rest sleep across ground/air changes.')
