#!/usr/bin/env python3
"""Compare actual Mario Up B callbacks/physics with foreign-body donor playback."""
import re
import subprocess
from pathlib import Path
from hostFighterHeaders import prepare
from generateSpecialTiming import render, superjump_landing_duration, path_catalog

ROOT=Path(__file__).resolve().parents[1]
assert (ROOT/'src/ft/ftspecialtiming.generated.inc').read_text()==render()
assert superjump_landing_duration()==25
main=(ROOT/'src/ft/ftmain.c').read_text()
physics=(ROOT/'src/ft/ftphysics.c').read_text()
mario=(ROOT/'src/ft/ftchar/ftmario/ftmariospecialhi.c').read_text()
fall=(ROOT/'src/ft/ftcommon/ftcommonfallspecial.c').read_text()

def function(text,name):
    match=re.search(r'^[\w *]+\b'+name+r'\([^;]*?\)[^\n{;]*\s*\{',text,re.M)
    assert match,name
    start=match.start()
    brace=text.index('{',start);depth=1;end=brace+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]+'\n'

clock=(ROOT/'src/ft/ftcustommove.c.inc').read_text()
clock=clock[clock.index('typedef struct FTCustomMoveClock'):clock.index('static s32 ftCustomJointResolve')]
timing=main[main.index('typedef enum FTMainCharBuilderSpecialKind'):main.index('/* PK Thunder')]
timing=timing.replace('"ftspecialtiming.generated.inc"','"ft/ftspecialtiming.generated.inc"')
state=main[main.index('static s32 sFTMainCharBuilderSpecialDonors'):main.index('static ftMotionCommand sFTMainCharBuilderSamusSpecialLwScript')]
helpers=''.join(function(main,n) for n in (
    'ftMainCharBuilderGetActiveSpecialDonor','ftMainCharBuilderClearSpecialDonor',
    'ftMainCharBuilderGetSpecialAttributes','ftMainCharBuilderGetSuperJumpRecoveryDonor',
    'ftMainCharBuilderGetSuperJumpAttributes','ftMainCharBuilderStartSuperJumpLandingClock',
    'ftMainCharBuilderActivePath','ftMainCharBuilderGetSpecialTravel',
    'ftMainCharBuilderSetSpecialTravelAngle','ftMainCharBuilderGetSpecialTravelAngle',
    'ftMainCharBuilderCheckSpecialStatus'))
actual_physics=''.join(function(physics,n) for n in (
    'ftPhysicsSetGroundVelTransferAir','ftPhysicsApplyGroundVelTransN',
    'ftPhysicsApplyGravityClampTVel','ftPhysicsApplyGravityDefault','ftPhysicsApplyFastFall','ftPhysicsCheckSetFastFall',
    'ftPhysicsClampAirVelX','ftPhysicsCheckClampAirVelXDec','ftPhysicsCheckClampAirVelXDecMax',
    'ftPhysicsClampAirVelXStickRange','ftPhysicsApplyAirVelXFriction',
    'ftPhysicsGetAirVelTransN','ftPhysicsApplyAirVelTransNAll'))
flag_rows=[]
for case in path_catalog():
    if case['donor'] not in (0,4) or 'Hi' not in case['phase']:continue
    wall=0;events={};flag1=0;air=case['air'];row=[]
    for op,args in case['events']:
        if op=='ftMotionCommandWait':wall+=int(args[0],0)
        elif op=='ftMotionCommandWaitAsync':wall=max(wall,int(args[0],0))
        else:events.setdefault(wall,[]).append((op,args))
    for frame in range(case['duration']):
        flag2=0
        for op,args in events.get(frame,()):
            if op=='ftMotionCommandSetFlag1':flag1=int(args[0],0)
            elif op=='ftMotionCommandSetFlag2':flag2=int(args[0],0)
            elif op=='ftMotionCommandSetAirJumpMax':air=1
        row.append('{'+','.join(map(str,(flag1,flag2,air)))+'}')
    flag_rows.append('{'+','.join(row)+'}')
flag_data='static const unsigned char sSuperJumpSourceFlags[4][40][3] = {'+','.join(flag_rows)+'};\n'
source=r'''
#include <ft/fighter.h>
#include <ft/ftcustommove.h>
#define FTCHARBUILDER_NEUTRAL_EXTENDED
typedef struct FTCustomCollisionTrajectory { const FTCustomCollisionFrame *frames; s32 first,count,loop_start,loop_period; } FTCustomCollisionTrajectory;
void bzero(void *p,int n) { unsigned char *q=p;while(n--) *q++=0; }
f32 __cosf(f32 a) { f32 r;__asm__("flds %1; fcos; fstps %0":"=m"(r):"m"(a));return r; }
f32 __sinf(f32 a) { f32 r;__asm__("flds %1; fsin; fstps %0":"=m"(r):"m"(a));return r; }
f32 cosf(f32 a) { return __cosf(a); }
FTData *dFTManagerDataFiles[32];
static FTData files[12];static FTAttributes attrs[12],body_attrs;static void *main_files[12];
''' + clock+timing+state+helpers+actual_physics+flag_data+r'''
void ftMainSetStatus(GObj *g,s32 status,f32 begin,f32 speed,u32 flags) {
    FTStruct *fp=ftGetStruct(g);ftCustomMoveResetClock(fp);fp->status_id=status;
    ftMainCharBuilderCheckSpecialStatus(fp,status>=nFTCommonStatusSpecialStart);
    ftMainCharBuilderStartSuperJumpLandingClock(fp,begin);
}
void ftMainPlayAnimEventsAll(GObj *g) {}
void mpCommonSetFighterAir(FTStruct *fp) { fp->ga=nMPKineticsAir; }
sb32 ftParamCheckSetFighterColAnimID(GObj *g,s32 id,s32 ticks) { return FALSE; }
void ftPublicTryPlayFallSpecialReact(GObj *g) {}
void ftMainRunUpdateColAnim(GObj *g) {}
void ftParamSetStickLR(FTStruct *fp) { fp->lr=fp->input.pl.stick_range.x<0 ? -1 : 1; }
static sb32 map_contact;
sb32 mpCommonCheckFighterProject(GObj *g) { return FALSE; }
sb32 mpCommonCheckFighterPassCliff(GObj *g,sb32 (*pass)(GObj*)) { return map_contact; }
void mpCommonSetFighterFallOnEdgeBreak(GObj *g) {}
void ftCommonCliffCatchSetStatus(GObj *g) { ftMainSetStatus(g,nFTCommonStatusCliffCatch,0,1,0); }
void ftCommonLandingFallSpecialSetStatus(GObj *g,sb32 interrupt,f32 speed) {
    FTStruct *fp=ftGetStruct(g);fp->ga=nMPKineticsGround;fp->jumps_used=0;
    ftMainSetStatus(g,nFTCommonStatusLandingFallSpecial,0,speed,0);
    fp->status_vars.common.landing.is_allow_interrupt=interrupt;
}
''' + function(fall,'ftCommonFallSpecialSetStatus')+function(fall,'ftCommonFallSpecialProcPhysics')+''.join(function(mario,n) for n in (
    'ftMarioSpecialHiProcUpdate','ftMarioSpecialHiProcInterrupt','ftMarioSpecialHiProcPhysics',
    'ftMarioSpecialHiProcPass','ftMarioSpecialHiProcMap',
    'ftMarioSpecialHiInitStatusVars','ftMarioSpecialHiSetStatus','ftMarioSpecialAirHiSetStatus'))+r'''
static FTStruct donor_fp,body_fp,replacement;static GObj donor_g,body_g;
static DObj donor_top,donor_trans,body_top;
#define CHECK(c) do { if(!(c)) return __LINE__; } while(0)
#define NEAR(a,b) ((a)-(b)<0.003F && (a)-(b)>-0.003F)
static int test(void) {
    int d,b,p,air,lr,stick,f,i;const FTCharBuilderSpecialPath *path;
    for(i=0;i<12;i++) {
        attrs[i].gravity=0.7F+i*0.03F;attrs[i].tvel_base=12+i;attrs[i].tvel_fast=20+i;
        attrs[i].air_speed_max_x=8+i;attrs[i].air_accel=0.15F+i*0.01F;
        attrs[i].air_friction=0.3F+i*0.01F;attrs[i].jumps_max=2;
        main_files[i]=&attrs[i];files[i].p_file_main=&main_files[i];dFTManagerDataFiles[i]=&files[i];
    }
    body_attrs=attrs[9];body_attrs.jumps_max=6;
    for(d=0;d<=4;d+=4) for(b=0;b<12;b++) for(p=0;p<4;p++) for(air=0;air<2;air++)
    for(lr=-1;lr<=1;lr+=2) for(stick=-80;stick<=80;stick+=40) {
        bzero(&body_fp,sizeof(body_fp));bzero(&donor_fp,sizeof(donor_fp));
        bzero(&donor_trans,sizeof(donor_trans));
        body_fp.player=p;body_fp.player_num=11;body_fp.fkind=b;body_fp.attr=&body_attrs;
        donor_fp.player=4;donor_fp.fkind=d;donor_fp.attr=&attrs[d];
        donor_fp.joints[0]=&donor_top;donor_fp.joints[1]=&donor_trans;
        body_fp.joints[0]=&body_top;body_fp.joints[1]=NULL; /* Missing/foreign TransN must be safe. */
        donor_top.scale.vec.f=(Vec3f){1,1,1};donor_top.rotate.vec.f.y=lr*F_CST_DTOR32(90.0F);
        body_top=donor_top;body_fp.lr=donor_fp.lr=lr;
        body_fp.ga=donor_fp.ga=air ? nMPKineticsAir : nMPKineticsGround;
        body_fp.coll_data.floor_angle=donor_fp.coll_data.floor_angle=(Vec3f){0,1,0};
        body_g.user_data.p=&body_fp;body_g.obj=&body_top;
        donor_g.user_data.p=&donor_fp;donor_g.obj=&donor_top;
        body_fp.physics.vel_air=(Vec3f){9,3,0};donor_fp.physics.vel_air=body_fp.physics.vel_air;
        sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
        sFTMainCharBuilderSpecialTravelAngles[p]=0;
        if(air) { ftMarioSpecialAirHiSetStatus(&body_g);ftMarioSpecialAirHiSetStatus(&donor_g); }
        else { ftMarioSpecialHiSetStatus(&body_g);ftMarioSpecialHiSetStatus(&donor_g); }
        CHECK(body_fp.physics.vel_air.x==donor_fp.physics.vel_air.x);
        CHECK(body_fp.physics.vel_air.y==donor_fp.physics.vel_air.y);
        body_fp.motion_id=nFTCommonMotionWait;
        sFTMainCharBuilderSpecialMotionIDs[p]=air ? nFTMarioMotionSpecialAirHi : nFTMarioMotionSpecialHi;
        path=ftMainCharBuilderSpecialPath(d,sFTMainCharBuilderSpecialMotionIDs[p]);CHECK(path && path->travel);
        ftCustomMoveStartClock(&body_fp,&path->move,0);
        for(f=0;f<40;f++) {
            ftCustomMoveAdvanceClock(&body_fp,0);
            i=(d==4 ? 2 : 0)+air;
            body_fp.motion_vars.flags.flag1=donor_fp.motion_vars.flags.flag1=sSuperJumpSourceFlags[i][f][0];
            body_fp.motion_vars.flags.flag2=donor_fp.motion_vars.flags.flag2=sSuperJumpSourceFlags[i][f][1];
            body_fp.ga=donor_fp.ga=sSuperJumpSourceFlags[i][f][2] ? nMPKineticsAir : nMPKineticsGround;
            body_fp.input.pl.stick_range.x=donor_fp.input.pl.stick_range.x=stick;
            donor_fp.anim_vel=(Vec3f){0,0,0};donor_trans.translate.vec.f=(Vec3f){-path->travel[f].delta.z,path->travel[f].delta.y,path->travel[f].delta.x};
            ftMarioSpecialHiProcInterrupt(&body_g);ftMarioSpecialHiProcInterrupt(&donor_g);
            CHECK(NEAR(ftMainCharBuilderGetSpecialTravelAngle(&body_fp),donor_trans.rotate.vec.f.z));
            CHECK(body_fp.lr==donor_fp.lr);
            ftMarioSpecialHiProcPhysics(&body_g);ftMarioSpecialHiProcPhysics(&donor_g);
            CHECK(NEAR(body_fp.physics.vel_air.x,donor_fp.physics.vel_air.x));
            CHECK(NEAR(body_fp.physics.vel_air.y,donor_fp.physics.vel_air.y));
            CHECK(NEAR(body_fp.physics.vel_air.z,donor_fp.physics.vel_air.z));
            /* No animation advance during hitlag: travel and clock do not change. */
            { Vec3f v,w;ftMainCharBuilderGetSpecialTravel(&body_fp,&v,FALSE);
              ftMainCharBuilderGetSpecialTravel(&body_fp,&w,FALSE);CHECK(v.x==w.x && v.y==w.y); }
        }
        body_g.anim_frame=-1;donor_g.anim_frame=-1;
        ftMarioSpecialHiProcUpdate(&body_g);ftMarioSpecialHiProcUpdate(&donor_g);
        CHECK(body_fp.status_id==nFTCommonStatusFallSpecial);
        CHECK(ftMainCharBuilderGetActiveSpecialDonor(&body_fp)==-1);
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&attrs[d]);
        CHECK(body_fp.jumps_used==6 && donor_fp.jumps_used==2);
        CHECK(body_fp.status_vars.common.fallspecial.drift==donor_fp.status_vars.common.fallspecial.drift);
        for(f=0;f<30;f++) {
            body_fp.input.pl.stick_range.y=donor_fp.input.pl.stick_range.y=(f>=15 ? -80 : 0);
            body_fp.tap_stick_y=donor_fp.tap_stick_y=0;
            ftCommonFallSpecialProcPhysics(&body_g);ftCommonFallSpecialProcPhysics(&donor_g);
            CHECK(NEAR(body_fp.physics.vel_air.x,donor_fp.physics.vel_air.x));
            CHECK(NEAR(body_fp.physics.vel_air.y,donor_fp.physics.vel_air.y));
            CHECK(body_fp.is_fastfall==donor_fp.is_fastfall);
        }
        ftMainSetStatus(&body_g,nFTCommonStatusLandingFallSpecial,0,0.28F,0);
        CHECK(ftCustomMoveGetClock(&body_fp) && ftCustomMoveGetClock(&body_fp)->duration==25);
        for(f=0;f<25;f++) CHECK(ftCustomMoveAdvanceClock(&body_fp,-1)>0 || f==0);
        CHECK(ftCustomMoveAdvanceClock(&body_fp,-1)<0);
        ftMainSetStatus(&body_g,nFTCommonStatusWait,0,1,0);
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&body_attrs);
        CHECK(!ftCustomMoveGetClock(&body_fp));
        /* Native map callbacks retain platform-pass, direct landing and cliff branches. */
        body_fp.coll_data.floor_flags=MAP_VERTEX_COLL_PASS;body_fp.input.pl.stick_range.y=-80;
        CHECK(!ftMarioSpecialHiProcPass(&body_g));body_fp.input.pl.stick_range.y=80;
        CHECK(ftMarioSpecialHiProcPass(&body_g));
        body_fp.status_id=nFTMarioStatusSpecialHi;body_fp.ga=nMPKineticsAir;
        body_fp.motion_vars.flags.flag1=1;body_fp.physics.vel_air.y=-3;map_contact=TRUE;
        sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
        body_fp.coll_data.mask_stat=0;ftMarioSpecialHiProcMap(&body_g);
        CHECK(body_fp.status_id==nFTCommonStatusLandingFallSpecial && ftCustomMoveGetClock(&body_fp)->duration==25);
        CHECK(!body_fp.status_vars.common.landing.is_allow_interrupt);
        body_fp.status_id=nFTMarioStatusSpecialHi;body_fp.ga=nMPKineticsAir;
        sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
        body_fp.coll_data.mask_stat=MAP_FLAG_CLIFF_MASK;ftMarioSpecialHiProcMap(&body_g);
        CHECK(body_fp.status_id==nFTCommonStatusCliffCatch && !ftCustomMoveGetClock(&body_fp));
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&body_attrs);
        /* A damaging interruption must never retain donor travel/recovery physics. */
        sFTMainCharBuilderSpecialDonors[p]=d;sFTMainCharBuilderSpecialKinds[p]=nFTMainCharBuilderSpecialKindHi;
        ftMainSetStatus(&body_g,nFTCommonStatusDamageAir1,0,1,0);
        CHECK(ftMainCharBuilderGetActiveSpecialDonor(&body_fp)==-1);
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&body_attrs);
        { Vec3f v;CHECK(!ftMainCharBuilderGetSpecialTravel(&body_fp,&v,FALSE)); }
        /* Same slot/address reused after respawn and other owners cannot inherit recovery. */
        sFTCharBuilderSuperJumpRecovery[p].owner=&body_fp;sFTCharBuilderSuperJumpRecovery[p].player_num=11;sFTCharBuilderSuperJumpRecovery[p].donor=d;
        body_fp.status_id=nFTCommonStatusFallSpecial;body_fp.player_num++;
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&body_fp)==&body_attrs);
        replacement=body_fp;replacement.player_num=11;
        CHECK(ftMainCharBuilderGetSuperJumpAttributes(&replacement)==replacement.attr);
    }
    return 0;
}
void _start(void) {
    int r=test();if(r) {
        char msg[]="Super Jump CHECK line 0000\n";int i,v=r;
        for(i=24;i>=21;i--) {msg[i]='0'+v%10;v/=10;}
        __asm__ volatile("int $0x80"::"a"(4),"b"(2),"c"(msg),"d"(sizeof(msg)-1):"memory");
    }
    __asm__ volatile("int $0x80"::"a"(1),"b"(r):"memory");__builtin_unreachable();
}
'''
build=ROOT/'build';headers=prepare(ROOT,build/'superjump-host-headers')
(build/'testSuperJump.c').write_text(source)
subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-O1',
                '-I'+str(headers),'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C',
                '-D_MIPS_SZLONG=32','-DREGION_US',str(build/'testSuperJump.c'),'-o',str(build/'testSuperJump')],check=True)
subprocess.run([str(build/'testSuperJump')],check=True)
print('PASS: Mario/Luigi Up B native versus donor movement, steering/facing, ground/air physics, helpless recovery, 25-tick landing and interruption/respawn guards on 12 bodies/four slots/both facings.')
