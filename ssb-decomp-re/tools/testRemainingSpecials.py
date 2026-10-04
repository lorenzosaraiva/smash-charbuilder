#!/usr/bin/env python3
"""Exercise production special mechanics with actual 32-bit fighter layouts."""
import re, subprocess
from pathlib import Path
from hostFighterHeaders import prepare
from generateSpecialTiming import path_catalog, render
ROOT=Path(__file__).resolve().parents[1]
def function(text,name):
    m=re.search(r'^[\w *]+\b'+name+r'\([^;]*?\)[^\n{;]*\s*\{',text,re.M)
    assert m,name
    start=m.start();brace=text.index('{',start);depth=1;end=brace+1
    while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]+'\n'
def functions(file,names):
    text=(ROOT/file).read_text()
    return ''.join(function(text,n) for n in names.split())
assert (ROOT/'src/ft/ftspecialtiming.generated.inc').read_text()==render()
main=(ROOT/'src/ft/ftmain.c').read_text()
clock=(ROOT/'src/ft/ftcustommove.c.inc').read_text()
clock=clock[clock.index('typedef struct FTCustomMoveClock'):clock.index('static s32 ftCustomJointResolve')]
timing=main[main.index('typedef enum FTMainCharBuilderSpecialKind'):main.index('/* PK Thunder')].replace('"ftspecialtiming.generated.inc"','"ft/ftspecialtiming.generated.inc"')
state=main[main.index('static s32 sFTMainCharBuilderSpecialDonors'):main.index('static ftMotionCommand sFTMainCharBuilderSamusSpecialLwScript')]
helpers=''.join(function(main,n) for n in ('ftMainCharBuilderGetActiveSpecialDonor','ftMainCharBuilderClearSpecialDonor',
    'ftMainCharBuilderGetSpecialAttributes','ftMainCharBuilderGetSuperJumpRecoveryDonor','ftMainCharBuilderGetSuperJumpAttributes',
    'ftMainCharBuilderStartSuperJumpLandingClock','ftMainCharBuilderActivePath','ftMainCharBuilderGetSpecialTravel',
    'ftMainCharBuilderGetSpecialSpawn','ftMainCharBuilderGetSpecialSphere','ftMainCharBuilderAdjustSpecialCollision',
    'ftMainCharBuilderIsSpecialAdapter','ftMainCharBuilderGetSpecialJoint','ftMainCharBuilderCheckSpecialStatus','ftMainCharBuilderGetSpecialMotionID',
    'ftMainCheckGetUpdateDamage','ftMainUpdateAbsorbStatWeapon','ftMainUpdateReflectorStatWeapon'))
source=r'''
#include <ft/fighter.h>
#include <wp/weapon.h>
#include <it/item.h>
#include <ft/ftcustommove.h>
static FTAttributes* ftCustomNormalGetAttributes(FTStruct *fp) { return fp->attr; }
static sb32 ftCustomNormalGetTravel(FTStruct *fp,Vec3f *v,sb32 ground) { return FALSE; }

#include <sc/scene.h>
static SCBattleState battle;SCBattleState *gSCManagerBattleState=&battle;
MPGroundData *gMPCollisionGroundData;
extern int llCaptainMainMotionSpecialHiVec2h;
#define FTCHARBUILDER_NEUTRAL_EXTENDED
typedef struct FTCustomCollisionTrajectory { const FTCustomCollisionFrame *frames; s32 first,count,loop_start,loop_period; } FTCustomCollisionTrajectory;
void bzero(void *p,int n) { unsigned char *q=p;while(n--) *q++=0; }
f32 __cosf(f32 a) { f32 r;__asm__("flds %1; fcos; fstps %0":"=m"(r):"m"(a));return r; }
f32 __sinf(f32 a) { f32 r;__asm__("flds %1; fsin; fstps %0":"=m"(r):"m"(a));return r; }
f32 cosf(f32 a) { return __cosf(a); }
f32 sqrtf(f32 a) { f32 r;__asm__("flds %1; fsqrt; fstps %0":"=m"(r):"m"(a));return r; }
f32 syUtilsArcTan2(f32 y,f32 x) { f32 r;__asm__("flds %1; flds %2; fpatan; fstps %0":"=m"(r):"m"(y),"m"(x));return r; }
f32 syVectorAngleDiff3D(Vec3f *a,Vec3f *b) { f32 d=syUtilsArcTan2(a->y,a->x)-syUtilsArcTan2(b->y,b->x);if(d<0)d=-d;if(d>PI32)d=2*PI32-d;return d; }
FTData *dFTManagerDataFiles[32];static FTData files[12];static FTAttributes attrs[12],body_attrs;static void *main_files[12];
f32 dMPCollisionMaterialFrictions[16]={1};
'''+clock+timing+state+helpers+functions('src/ft/ftphysics.c',
    'ftPhysicsSetGroundVelTransferAir ftPhysicsSetGroundVelFriction ftPhysicsApplyGroundVelFriction ftPhysicsApplyGravityClampTVel ftPhysicsApplyGravityDefault ftPhysicsApplyFastFall ftPhysicsClampAirVelX ftPhysicsClampAirVelXMax ftPhysicsCheckClampAirVelXDec ftPhysicsCheckClampAirVelXDecMax ftPhysicsClampAirVelXStickRange ftPhysicsApplyAirVelXFriction ftPhysicsGetAirVelTransN ftPhysicsApplyAirVelTransNYZ ftPhysicsApplyAirVelTransNAll ftPhysicsApplyAirVelFriction')+r'''
static WPStruct weapon;static GObj weapon_gobj;static DObj weapon_top;static int spawned,destroyed,absorbed,reflected,thrown;
static Vec3f spawn_position;static int last_status;
FTItemThrow dFTCommonDataItemThrowDescs[nFTCommonStatusLightThrowEnd-nFTCommonStatusLightThrowStart+1];
static f32 bomb_throw_damage;
void itMainSetFighterThrow(GObj *g,Vec3f *v,f32 damage,sb32 smash) { spawn_position=*v;bomb_throw_damage=damage; }
void itMainSetFighterDrop(GObj *g,Vec3f *v,f32 damage) { itMainSetFighterThrow(g,v,damage,FALSE); }
void mpCommonSetFighterWaitOrFall(GObj *g) {}
static FTSpecialColl special_coll;static FTStruct victim;static GObj victim_gobj;static DObj victim_top;
static Vec2h capture_offsets[32];void *gFTDataCaptainMainMotion=capture_offsets;
__asm__(".global llCaptainMainMotionSpecialHiVec2h\n.set llCaptainMainMotionSpecialHiVec2h,0");
void ftMainSetStatus(GObj *g,s32 status,f32 begin,f32 speed,u32 flags) {
    FTStruct *fp=ftGetStruct(g);int donor=ftMainCharBuilderGetActiveSpecialDonor(fp),i;
    ftCustomMoveResetClock(fp);fp->status_id=status;last_status=status;
    ftMainCharBuilderCheckSpecialStatus(fp,status>=nFTCommonStatusSpecialStart);
    if(donor>=0 && status>=nFTCommonStatusSpecialStart) {
        for(i=0;i<ARRAY_COUNT(sFTCharBuilderSpecialPaths);i++) {
            const FTCharBuilderSpecialPath *p=&sFTCharBuilderSpecialPaths[i];
            if(p->donor!=donor)continue;
            /* For host movement tests, corresponding native status/motion IDs
               are assigned by the fixture; real dispatch is tested in ROM. */
            if(p->motion==sFTMainCharBuilderSpecialMotionIDs[fp->player]) {
                ftCustomMoveStartClock(fp,&p->move,begin);break;
            }
        }
    } else ftMainCharBuilderStartSuperJumpLandingClock(fp,begin);
}
void ftMainPlayAnimEventsAll(GObj *g) {}
void mpCommonSetFighterAir(FTStruct *fp) { fp->ga=nMPKineticsAir; }
void mpCommonSetFighterGround(FTStruct *fp) { fp->ga=nMPKineticsGround;fp->jumps_used=0; }
void ftParamsUpdateFighterPartsTransformAll(DObj *d) {}
sb32 ftParamCheckSetFighterColAnimID(GObj *g,s32 id,s32 ticks) { return FALSE; }
void ftParamSetCaptureImmuneMask(FTStruct *fp,u8 mask) { fp->capture_immune_mask=mask; }
void ftPhysicsStopVelAll(GObj *g) { FTStruct *fp=ftGetStruct(g);fp->physics.vel_air=(Vec3f){0};fp->physics.vel_ground=(Vec3f){0}; }
void ftCommonWaitSetStatus(GObj *g) { ftMainSetStatus(g,nFTCommonStatusWait,0,1,0); }
void ftCommonFallSetStatus(GObj *g) { ftMainSetStatus(g,nFTCommonStatusFall,0,1,0); }
sb32 ftAnimEndCheckSetStatus(GObj *g,void (*callback)(GObj*)) { if(g->anim_frame<=0){callback(g);return TRUE;}return FALSE; }
void ftAnimEndSetWait(GObj *g) { ftAnimEndCheckSetStatus(g,ftCommonWaitSetStatus); }
void ftAnimEndSetFall(GObj *g) { ftAnimEndCheckSetStatus(g,ftCommonFallSetStatus); }
void ftCommonFallSpecialSetStatus(GObj *g,f32 drift,sb32 unk,sb32 accel,sb32 landing,f32 lag,sb32 interrupt) { ftMainSetStatus(g,nFTCommonStatusFallSpecial,0,1,0); }
void ftMainRunUpdateColAnim(GObj *g) {}
void ftKirbySpecialHiUpdateEffect(GObj *g) {}
GObj* efManagerPurinSingMakeEffect(GObj *g) { return NULL; }
GObj* efManagerQuakeMakeEffect(s32 kind) { return NULL; }
void wpMainDestroyWeapon(GObj *g) { destroyed++; }
GObj* wpPikachuThunderHeadMakeWeapon(GObj *g,Vec3f *pos,Vec3f *vel) {
    spawned++;spawn_position=*pos;weapon.physics.vel_air=*vel;weapon.weapon_vars.thunder.thunder_state=0;return &weapon_gobj;
}
GObj* wpYoshiEggThrowMakeWeapon(GObj *g,Vec3f *pos) { spawned++;spawn_position=*pos;return &weapon_gobj; }
void mpCommonRunWeaponCollisionDefault(GObj *g,Vec3f *p,MPCollData *c) {}
void gmCollisionGetFighterPartsWorldPosition(DObj *d,Vec3f *v) { *v=d->translate.vec.f; }
s32 wpMainGetStaledDamage(WPStruct *w) { return w->attack_coll.damage; }
void wpProcessUpdateHitInteractStats(WPStruct *w,WPAttackColl *c,GObj *g,s32 kind,u32 dmg) { absorbed+=kind==nGMHitTypeAbsorb;reflected+=kind==nGMHitTypeReflect; }
void ftParamUpdateDamage(FTStruct *fp,s32 damage) {}
void ftCommonThrownReleaseFighterLoseGrip(GObj *g) { thrown++; }
void ftCommonThrownReleaseThrownUpdateStats(GObj *g,s32 lr,s32 script,s32 index) { thrown++; }
Vec3f* syVectorSub3D(Vec3f *a,Vec3f *b) { a->x-=b->x;a->y-=b->y;a->z-=b->z;return a; }
Vec3f* syVectorAdd3D(Vec3f *a,Vec3f *b) { a->x+=b->x;a->y+=b->y;a->z+=b->z;return a; }
f32 syVectorMag3D(Vec3f *a) { return sqrtf(a->x*a->x+a->y*a->y+a->z*a->z); }
f32 syVectorNorm3D(Vec3f *a) { f32 n=syVectorMag3D(a);a->x/=n;a->y/=n;a->z/=n;return n; }
Vec3f* syVectorScale3D(Vec3f *a,f32 s) { a->x*=s;a->y*=s;a->z*=s;return a; }
'''+functions('src/ft/ftparam.c','ftParamSetStickLR')
selection={
 'ftfox/ftfoxspecialhi.c':'ftFoxSpecialHiUpdateModelPitch ftFoxSpecialHiInitStatusVars ftFoxSpecialAirHiSetStatusFromGround ftFoxSpecialAirHiProcPhysics ftFoxSpecialHiProcPhysics ftFoxSpecialHiHoldInitStatusVars',
 'ftpikachu/ftpikachuspecialhi.c':'ftPikachuSpecialHiStartInitStatusVars ftPikachuSpecialHiInitStatusVarsZip ftPikachuSpecialAirHiSetStatus ftPikachuSpecialHiCheckGotoSubZip ftPikachuSpecialHiEndBackupVel ftPikachuSpecialAirHiEndSetStatus ftPikachuSpecialAirHiEndProcUpdate',
 'ftfox/ftfoxspeciallw.c':'ftFoxSpecialLwCheckSetRelease ftFoxSpecialLwDecReleaseLag ftFoxSpecialLwLoopSetReflectFlag',
 'ftness/ftnessspeciallw.c':'ftNessSpecialLwCheckRelease ftNessSpecialLwDecReleaseLag ftNessSpecialLw_InitStatusVars ftNessSpecialLwHitSetAbsorbTrue',
 'ftkirby/ftkirbyspeciallw.c':'ftKirbySpecialLwUpdateColAnim ftKirbySpecialLwSetDamageResist ftKirbySpecialLwSetDropFallVel ftKirbySpecialLwCheckRelease',
 'ftkirby/ftkirbyspecialhi.c':'ftKirbySpecialAirHiProcPhysics',
 'ftpikachu/ftpikachuspeciallw.c':'ftPikachuSpecialLwGetWeapon ftPikachuSpecialLwMakeThunder ftPikachuSpecialLwCheckCollideThunder ftPikachuSpecialLwProcDamage ftPikachuSpecialLwStartInitStatusVars',
 'ftyoshi/ftyoshispecialhi.c':'ftYoshiSpecialHiGetWeapon ftYoshiSpecialHiGetEggPosition ftYoshiSpecialHiUpdateEggVars ftYoshiSpecialHiUpdateEggThrowForce ftYoshiSpecialHiProcDamage',
 'ftcaptain/ftcaptainspecialhi.c':'ftCaptainSpecialHiProcCatch ftCaptainSpecialHiThrowSetStatus ftCaptainSpecialHiCatchProcUpdate ftCaptainSpecialHiCatchProcPhysics',
 'ftpurin/ftpurinspecialhi.c':'ftPurinSpecialHiProcUpdate',
}
for file,names in selection.items():source+=functions('src/ft/ftchar/'+file,names)
source+=functions('src/ft/ftcommon/ftcommoncapturecaptain.c','ftCommonCaptureCaptainUpdatePositions ftCommonCaptureCaptainRelease')
source+=functions('src/ft/ftcommon/ftcommonitemthrow.c','ftCommonItemThrowUpdateModelYaw ftCommonItemThrowProcUpdate ftCommonItemThrowInitStatusVars')
source+=r'''
static FTStruct fp;static GObj g;static DObj top,trans,base;static MPGroundData ground;
#define CHECK(c) do { if(!(c)) return __LINE__; } while(0)
#define NEAR(a,b) ((a)-(b)<0.003F && (a)-(b)>-0.003F)
static const FTCharBuilderSpecialPath* start(s32 donor,s32 motion,s32 kind) {
    const FTCharBuilderSpecialPath *p=ftMainCharBuilderSpecialPath(donor,motion);
    sFTMainCharBuilderSpecialDonors[fp.player]=donor;sFTMainCharBuilderSpecialKinds[fp.player]=kind;
    sFTMainCharBuilderSpecialMotionIDs[fp.player]=motion;
    fp.motion_id=nFTCommonMotionWait;fp.status_id=230;
    ftCustomMoveStartClock(&fp,&p->move,0);ftCustomMoveAdvanceClock(&fp,0);return p;
}
static int test(void) {
    int b,p,i,dx,dy,f;s32 damage;Vec3f pos,center,expect;Mtx44f matrix;const FTCharBuilderSpecialPath *path;
    for(i=0;i<12;i++) {
        attrs[i].size=1+i*.01F;attrs[i].gravity=.8F;attrs[i].tvel_base=80;
        attrs[i].air_speed_max_x=30;attrs[i].air_friction=.8F;attrs[i].air_accel=.4F;
        main_files[i]=&attrs[i];files[i].p_file_main=&main_files[i];dFTManagerDataFiles[i]=&files[i];
    }
    body_attrs=attrs[2];body_attrs.size=9;body_attrs.jumps_max=6;
    g.user_data.p=&fp;g.obj=&top;weapon_gobj.user_data.p=&weapon;weapon_gobj.obj=&weapon_top;weapon.weapon_gobj=&weapon_gobj;
    victim_gobj.user_data.p=&victim;victim_gobj.obj=&victim_top;victim.joints[0]=&victim_top;
    gMPCollisionGroundData=&ground;ground.map_bound_top=5000;
    for(b=0;b<12;b++) for(p=0;p<4;p++) {
        bzero(&fp,sizeof(fp));fp.fighter_gobj=&g;fp.fkind=b;fp.player=p;fp.player_num=100;fp.attr=&body_attrs;fp.lr=1;
        fp.joints[0]=&top;fp.joints[1]=&trans;fp.joints[4]=&base;fp.input.button_mask_b=0x40;
        top.scale.vec.f=(Vec3f){1,1,1};top.translate.vec.f=(Vec3f){100,500,0};
        CHECK(ftMainCharBuilderGetSpecialMotionID(8,nFTMainCharBuilderSpecialKindLw,nMPKineticsGround)==nFTKirbyMotionSpecialLwStart);
        CHECK(ftMainCharBuilderGetSpecialMotionID(8,nFTMainCharBuilderSpecialKindLw,nMPKineticsAir)==nFTKirbyMotionSpecialAirLwStart);
        /* Fire Fox has a 35-tick charge and 30-tick directional travel. */
        for(dx=-80;dx<=80;dx+=40) for(dy=-80;dy<=80;dy+=40) {
            start(1,nFTFoxMotionSpecialAirHi,1);fp.status_id=nFTFoxStatusSpecialAirHi;
            fp.input.pl.stick_range.x=dx;fp.input.pl.stick_range.y=dy;
            ftFoxSpecialAirHiSetStatusFromGround(&g);CHECK(fp.status_vars.fox.specialhi.anim_frames==30 && fp.jumps_used==6);
            CHECK(NEAR(sqrtf(SQUARE(fp.physics.vel_air.x)+SQUARE(fp.physics.vel_air.y)),115));
            for(f=0;f<30;f++)ftFoxSpecialAirHiProcPhysics(&g);
            CHECK(NEAR(sqrtf(SQUARE(fp.physics.vel_air.x)+SQUARE(fp.physics.vel_air.y)),115-29*FTFOX_FIREFOX_DECELERATE_VEL));
        }
        ftFoxSpecialHiHoldInitStatusVars(&g);CHECK(fp.status_vars.fox.specialhi.launch_delay==35);
        /* Casted native SetThrow pointers must survive script extraction. */
        path=ftMainCharBuilderSpecialPath(7,nFTCaptainMotionSpecialHi);
        for(i=0;(path->move.events[i]>>26)!=nFTMotionEventSetThrow;i++)CHECK(i<10);
        CHECK(((FTThrowHitDesc*)path->move.events[i+1])->damage==20);
        CHECK(((FTThrowHitDesc*)path->move.events[i+1])[1].damage==8);
        /* Final Cutter's native 0.8 travel factor must not resize foreign bodies. */
        path=start(8,nFTKirbyMotionSpecialAirHi,1);fp.ga=nMPKineticsAir;
        ftCustomMoveGetClock(&fp)->frame=20;top.scale.vec.f=(Vec3f){9,9,9};
        CHECK(ftMainCharBuilderGetSpecialTravel(&fp,&expect,FALSE));ftKirbySpecialAirHiProcPhysics(&g);
        CHECK(top.scale.vec.f.x==9 && top.scale.vec.f.y==9 && top.scale.vec.f.z==9);
        CHECK(NEAR(fp.physics.vel_air.y,expect.y*.8F) && NEAR(fp.physics.vel_air.z,expect.z*.8F));
        top.scale.vec.f=(Vec3f){1,1,1};
        /* Link Down B's common toss keeps Link's velocity/damage scales. */
        path=start(5,nFTCommonMotionLightThrowF4,2);fp.status_id=nFTCommonStatusLightThrowF4;
        ftCustomMoveStartClock(&fp,&path->move,0);fp.item_gobj=&weapon_gobj;fp.lr=1;
        attrs[5].itemthrow_vel_scale=100;attrs[5].itemthrow_damage_scale=100;
        body_attrs.itemthrow_vel_scale=900;body_attrs.itemthrow_damage_scale=900;
        dFTCommonDataItemThrowDescs[nFTCommonStatusLightThrowF4-nFTCommonStatusLightThrowStart]=(FTItemThrow){TRUE,80,0,120};
        ftCommonItemThrowInitStatusVars(&fp);fp.motion_vars.flags.flag0=1;
        g.anim_frame=10;ftCommonItemThrowProcUpdate(&g);
        CHECK(NEAR(spawn_position.x,80) && NEAR(spawn_position.y,0) && NEAR(bomb_throw_damage,1.2F));
        fp.item_gobj=NULL;
        /* Quick Attack: source velocity, five-tick zip, second-direction gate and 0.9 multiplier. */
        start(9,nFTPikachuMotionSpecialAirHi,1);fp.input.pl.stick_range.x=80;fp.input.pl.stick_range.y=0;
        ftPikachuSpecialHiStartInitStatusVars(&g);CHECK(fp.status_vars.pikachu.specialhi.anim_frames==20);
        ftPikachuSpecialAirHiSetStatus(&g);CHECK(fp.status_vars.pikachu.specialhi.anim_frames==5 && NEAR(fp.physics.vel_air.x,330));
        CHECK(!ftPikachuSpecialHiCheckGotoSubZip(&g));fp.input.pl.stick_range.y=80;fp.input.pl.stick_range.x=0;
        CHECK(ftPikachuSpecialHiCheckGotoSubZip(&g));fp.status_vars.pikachu.specialhi.is_subsequent_zip=TRUE;
        ftPikachuSpecialAirHiSetStatus(&g);CHECK(NEAR(fp.physics.vel_air.y,297) && !ftPikachuSpecialHiCheckGotoSubZip(&g));
        /* Reflector/PSI hold controls and native projectile ownership/healing. */
        start(1,nFTFoxMotionSpecialLwLoop,2);fp.special_coll=&special_coll;special_coll.size=(Vec3f){350,350,350};special_coll.damage_resist=50;
        ftFoxSpecialLwLoopSetReflectFlag(&g);CHECK(fp.is_reflect);CHECK(ftMainCharBuilderGetSpecialSphere(&fp,matrix,&pos));CHECK(NEAR(pos.x,350*attrs[1].size));
        weapon.attack_coll.damage=10;ftMainUpdateReflectorStatWeapon(&weapon,&weapon.attack_coll,&fp,&g);CHECK(weapon.reflect_gobj==&g);
        fp.status_vars.fox.speciallw.release_lag=18;fp.input.pl.button_hold=0;ftFoxSpecialLwCheckSetRelease(&fp);
        for(i=0;i<18;i++)ftFoxSpecialLwDecReleaseLag(&fp);CHECK(!fp.status_vars.fox.speciallw.release_lag && fp.status_vars.fox.speciallw.is_release);
        start(11,nFTNessMotionSpecialLwHold,2);special_coll.size=(Vec3f){430,430,430};ftNessSpecialLwHitSetAbsorbTrue(&g);CHECK(fp.is_absorb);
        CHECK(ftMainCharBuilderGetSpecialSphere(&fp,matrix,&pos) && NEAR(pos.x,430*attrs[11].size));
        fp.percent_damage=45;weapon.attack_coll.damage=10;weapon.attack_coll.can_not_heal=FALSE;
        ftMainUpdateAbsorbStatWeapon(&weapon,&weapon.attack_coll,&fp,&g);CHECK(fp.percent_damage==25 && weapon.absorb_gobj==&g);
        fp.percent_damage=5;ftMainUpdateAbsorbStatWeapon(&weapon,&weapon.attack_coll,&fp,&g);CHECK(!fp.percent_damage);
        /* Held egg create/charge/release/interrupt, using a source socket. */
        path=start(6,nFTYoshiMotionSpecialHi,1);spawned=destroyed=0;fp.motion_vars.flags.flag2=1;
        ftYoshiSpecialHiUpdateEggVars(&g);CHECK(spawned==1 && *ftYoshiSpecialHiGetWeapon(&fp)==&weapon_gobj);
        CHECK(ftMainCharBuilderGetSpecialSpawn(&g,&pos) && NEAR(pos.x,spawn_position.x) && NEAR(pos.y,spawn_position.y));
        fp.input.pl.button_hold=0x40;fp.status_vars.yoshi.specialhi.throw_force=0;
        for(i=0;i<19;i++)ftYoshiSpecialHiUpdateEggThrowForce(&g);
        fp.motion_vars.flags.flag2=2;ftYoshiSpecialHiUpdateEggVars(&g);
        CHECK(!*ftYoshiSpecialHiGetWeapon(&fp) && weapon.weapon_vars.egg_throw.is_throw && weapon.weapon_vars.egg_throw.throw_force==19);
        fp.motion_vars.flags.flag2=1;ftYoshiSpecialHiUpdateEggVars(&g);
        if(b!=6)fp.status_vars.yoshi.specialhi.egg_gobj=(GObj*)0x3f;
        ftYoshiSpecialHiProcDamage(&g);CHECK(destroyed==1 && !*ftYoshiSpecialHiGetWeapon(&fp));
        /* Thunder spawn from stage ceiling and native owner-contact dimensions. */
        start(9,nFTPikachuMotionSpecialLwLoop,2);ftPikachuSpecialLwStartInitStatusVars(&g);ftPikachuSpecialLwMakeThunder(&g);
        CHECK(NEAR(spawn_position.y,4500) && weapon.physics.vel_air.y==-450);
        weapon_top.translate.vec.f=(Vec3f){100,275,0};CHECK(ftPikachuSpecialLwCheckCollideThunder(&g));
        CHECK(weapon.weapon_vars.thunder.thunder_state==nWPPikachuThunderStatusCollide);
        CHECK(!*ftPikachuSpecialLwGetWeapon(&fp));
        weapon_gobj.user_data.p=NULL;ftPikachuSpecialLwProcDamage(&g);
        CHECK(*ftMainCharBuilderGetPikachuThunderDestroy(&fp));
        weapon_gobj.user_data.p=&weapon;*ftPikachuSpecialLwGetWeapon(&fp)=&weapon_gobj;
        *ftMainCharBuilderGetPikachuThunderDestroy(&fp)=FALSE;
        weapon.weapon_vars.thunder.thunder_state=nWPPikachuThunderStatusActive;
        if(b!=9)fp.status_vars.pikachu.speciallw.thunder_gobj=(GObj*)0x3f;
        ftPikachuSpecialLwProcDamage(&g);CHECK(!*ftPikachuSpecialLwGetWeapon(&fp) && *ftMainCharBuilderGetPikachuThunderDestroy(&fp));
        CHECK(weapon.weapon_vars.thunder.thunder_state==nWPPikachuThunderStatusDestroy);
        /* Stone: US armor, minimum release, timeout and armor-break spill damage. */
        start(8,nFTKirbyMotionSpecialAirLwHold,2);ftKirbySpecialLwSetDamageResist(&g);CHECK(fp.is_damage_resist && fp.damage_resist==38);
        ftKirbySpecialLwSetDropFallVel(&fp);CHECK(fp.physics.vel_air.y==FTKIRBY_STONE_FALL_VEL);
        fp.input.pl.button_tap=0x40;CHECK(!ftKirbySpecialLwCheckRelease(&g,FALSE));
        fp.input.pl.button_tap=0;for(i=0;i<FTKIRBY_STONE_DURATION_MIN;i++)CHECK(!ftKirbySpecialLwCheckRelease(&g,FALSE));
        fp.input.pl.button_tap=0x40;CHECK(ftKirbySpecialLwCheckRelease(&g,FALSE));
        damage=20;CHECK(!ftMainCheckGetUpdateDamage(&fp,&damage) && fp.damage_resist==18);
        damage=35;CHECK(ftMainCheckGetUpdateDamage(&fp,&damage) && damage==17 && !fp.is_damage_resist);
        fp.input.pl.button_tap=0;fp.status_vars.kirby.speciallw.duration=1;CHECK(!ftKirbySpecialLwCheckRelease(&g,FALSE));CHECK(ftKirbySpecialLwCheckRelease(&g,FALSE));
        /* Falcon Dive uses the source catch anchor and original throw descriptor. */
        path=start(7,nFTCaptainMotionSpecialHiCatch,1);fp.search_gobj=&victim_gobj;victim.ga=nMPKineticsAir;
        ftCaptainSpecialHiProcCatch(&g);CHECK(fp.catch_gobj==&victim_gobj && fp.capture_immune_mask==FTCATCHKIND_MASK_ALL);
        victim.fkind=0;capture_offsets[0]=(Vec2h){12,34};victim_top.translate.vec.f=(Vec3f){0,0,0};
        ftCommonCaptureCaptainUpdatePositions(&g,&victim_gobj,&pos);CHECK(ftMainCharBuilderGetSpecialSpawn(&g,&expect));
        CHECK(NEAR(pos.x,expect.x-12) && NEAR(pos.y,expect.y-34));
        g.anim_frame=-1;fp.motion_vars.flags.flag0=0;ftCaptainSpecialHiCatchProcUpdate(&g);
        CHECK(victim.status_vars.common.capturecaptain.capture_flag&FTCOMMON_CAPTURECAPTAIN_MASK_THROW);
        CHECK(fp.status_id==nFTCaptainStatusSpecialHiThrow && !fp.catch_gobj && !fp.capture_immune_mask);
        /* The independent weapon/passive stores invalidate on fighter generation. */
        *ftMainCharBuilderGetSpecialWeapon(&fp,6)=&weapon_gobj;fp.player_num++;
        CHECK(!*ftMainCharBuilderGetSpecialWeapon(&fp,6));
    }
    CHECK(reflected && absorbed);return 0;
}
void _start(void) { int code=test();__asm__ volatile("int $0x80"::"a"(1),"b"(code):"memory"); }
'''
headers=prepare(ROOT,ROOT/'build/remaining-host-headers')
path=ROOT/'build/testRemainingSpecials.c';path.write_text(source)
subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-O1',
    '-I'+str(headers),'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',str(path),'-o',str(ROOT/'build/testRemainingSpecials')],check=True)
result=subprocess.run([str(ROOT/'build/testRemainingSpecials')])
if result.returncode:
    candidates=[(i,l.strip()) for i,l in enumerate(source.splitlines(),1) if i%256==result.returncode and 'CHECK' in l]
    raise AssertionError(('Production special mechanic check failed',result.returncode,candidates))
print('PASS: production Fire Fox/Quick Attack movement and second-zip gate, Reflector ownership, PSI healing, held egg lifecycle, Thunder contact/cleanup, Stone armor/release and Falcon Dive capture/release on 12 bodies/four slots.')
