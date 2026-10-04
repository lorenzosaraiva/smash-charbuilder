#!/usr/bin/env python3
"""Compile the actual special clock/accessor with real 32-bit fighter layouts."""
import subprocess
from pathlib import Path
from generateSpecialTiming import catalog, render, path_catalog
from hostFighterHeaders import prepare

ROOT = Path(__file__).resolve().parents[1]
assert (ROOT/'src/ft/ftspecialtiming.generated.inc').read_text() == render()
clock = (ROOT/'src/ft/ftcustommove.c.inc').read_text()
clock = clock[clock.index('typedef struct FTCustomMoveClock'):clock.index('static s32 ftCustomJointResolve')]
main = (ROOT/'src/ft/ftmain.c').read_text()
timing = main[main.index('typedef enum FTMainCharBuilderSpecialKind'):main.index('static s32 sFTMainCharBuilderSpecialDonors')]
timing = timing.replace('"ftspecialtiming.generated.inc"', '"ft/ftspecialtiming.generated.inc"')
recovery = next(line for line in main.splitlines() if line.startswith('static struct FTCharBuilderSuperJumpRecovery'))
attrs = main[main.index('FTAttributes* ftMainCharBuilderGetSpecialAttributes'):main.index('static const FTCharBuilderSpecialPath* ftMainCharBuilderActivePath')]
mp = (ROOT/'src/mp/mpcommon.c').read_text()
ground = mp[mp.index('void mpCommonSetFighterGround('):mp.index('// 0x800DEEC8')]
helpers = main[main.index('static const FTCharBuilderSpecialPath* ftMainCharBuilderActivePath'):main.index('static sb32 ftMainCharBuilderIsBorrowingMotion')]
physics = (ROOT/'src/ft/ftphysics.c').read_text()
friction = physics[physics.index('void ftPhysicsApplyAirVelFriction('):physics.index('// 0x800D9260')]
air = physics[physics.index('void ftPhysicsGetAirVelTransN('):physics.index('// 0x800D938C')]
source = r'''
#include <ft/fighter.h>
#include <ft/ftcustommove.h>
#define FTCHARBUILDER_NEUTRAL_EXTENDED
typedef struct FTCustomCollisionTrajectory {
    const FTCustomCollisionFrame *frames; s32 first, count, loop_start, loop_period;
} FTCustomCollisionTrajectory;
void bzero(void *p, int n) { unsigned char *q=p; while(n--) *q++=0; }
''' + clock + timing + r'''
static s32 sFTMainCharBuilderSpecialMotionIDs[4], active_donors[4];
static u8 sFTMainCharBuilderSpecialKinds[4];
static f32 sFTMainCharBuilderSpecialTravelAngles[4];
FTData *dFTManagerDataFiles[32];
static FTData donor_data[12];static FTAttributes donor_attrs[12],body_attrs;static void *donor_files[12];
static s32 ftMainCharBuilderGetActiveSpecialDonor(FTStruct *fp) { return active_donors[fp->player]; }
f32 __cosf(f32 a) { f32 result; __asm__("flds %1; fcos; fstps %0":"=m"(result):"m"(a));return result; }
f32 __sinf(f32 a) { f32 result; __asm__("flds %1; fsin; fstps %0":"=m"(result):"m"(a));return result; }
''' + recovery + '\n' + attrs + helpers + ground + r'''
f32 cosf(f32 a) { return __cosf(a); }
''' + air + r'''
static FTAttributes *last_physics_attrs;
void ftPhysicsApplyFastFall(FTStruct *fp,FTAttributes *attr) { last_physics_attrs=attr; }
void ftPhysicsApplyGravityDefault(FTStruct *fp,FTAttributes *attr) { last_physics_attrs=attr; }
sb32 ftPhysicsCheckClampAirVelXDecMax(FTStruct *fp,FTAttributes *attr) { last_physics_attrs=attr;return FALSE; }
void ftPhysicsApplyAirVelXFriction(FTStruct *fp,FTAttributes *attr) { last_physics_attrs=attr; }
''' + friction + r'''
static FTStruct fighters[4], replacement;
#define CHECK(c) do { if (!(c)) return __LINE__; } while(0)
#define NEAR(a,b) ((a)-(b)<0.001F && (a)-(b)>-0.001F)
static int test(void) {
    int row,body,port,frame,facing;
    GObj gobj;DObj top,trans;Vec3f actual;
    for(row=0;row<12;row++) {
        donor_files[row]=&donor_attrs[row];donor_data[row].p_file_main=&donor_files[row];
        dFTManagerDataFiles[row]=&donor_data[row];
    }
    for (row=0;row<ARRAY_COUNT(sFTCharBuilderSpecialTimings);row++) {
        const FTCharBuilderSpecialTiming *s=&sFTCharBuilderSpecialTimings[row];
        CHECK(ftMainCharBuilderSpecialTiming(s->donor,s->motion)->duration==s->move.duration);
        CHECK(ftMainCharBuilderSpecialTiming(s->donor,s->motion)->flags==s->move.flags);
        for (body=0;body<12;body++) for(port=0;port<4;port++) {
            FTStruct *fp=&fighters[port];
            fp->player=port;fp->fkind=body;fp->status_id=232;fp->motion_id=nFTCommonMotionWait;
            ftCustomMoveStartClock(fp,&s->move,0);
            for(frame=0;frame<s->move.duration*2+2;frame++) {
                float result=ftCustomMoveAdvanceClock(fp,-1);
                if(s->move.flags & FTCUSTOMMOVE_FLAG_SPECIAL_CYCLE)
                    CHECK(result==frame%s->move.duration);
                else CHECK((frame<s->move.duration && (result==frame || (frame==0 && result>0))) ||
                           (frame>=s->move.duration && result<0));
                CHECK(ftCustomMoveEventSpeed(fp,&fp->motion_scripts[0][2],0.125F)==1);
                CHECK(ftCustomMoveEventFrame(fp,&fp->motion_scripts[0][2],999)==ftCustomMoveGetClock(fp)->frame);
            }
            ftCustomMoveStartClock(fp,&s->move,5);
            CHECK(ftCustomMoveAdvanceClock(fp,100)==(s->move.duration<=5 ?
                  (s->move.flags & FTCUSTOMMOVE_FLAG_SPECIAL_CYCLE ? 0 : -1) : 5));
            ftCustomMoveResetClock(fp);CHECK(ftCustomMoveAdvanceClock(fp,17)==17);
            *ftMainCharBuilderGetTornadoExpend(fp)=TRUE;fp->jumps_used=5;
            mpCommonSetFighterGround(fp);
            CHECK(!*ftMainCharBuilderGetTornadoExpend(fp) && fp->jumps_used==0);
            /* PK Thunder must never alter another body's native passive union. */
            fp->player_num=11;
            /* A foreign Tornado must not use another body's passive union. */
            fp->passive_vars.mario.is_expend_tornado=123;
            *ftMainCharBuilderGetTornadoExpend(fp)=456;
            CHECK(fp->passive_vars.mario.is_expend_tornado==
                  ((body==nFTKindMario || body==nFTKindLuigi) ? 456 : 123));
            if(body!=nFTKindMario && body!=nFTKindLuigi) {
                fp->player_num++;
                CHECK(*ftMainCharBuilderGetTornadoExpend(fp)==0);
                CHECK(fp->passive_vars.mario.is_expend_tornado==123);
            }
            fp->passive_vars.ness.is_thunder_destroy=123;
            ftMainCharBuilderGetNessPassive(fp)->is_thunder_destroy=456;
            CHECK(fp->passive_vars.ness.is_thunder_destroy==(body==nFTKindNess ? 456 : 123));
            if(body!=nFTKindNess) {
                fp->player_num++;
                CHECK(ftMainCharBuilderGetNessPassive(fp)->is_thunder_destroy==0);
                CHECK(fp->passive_vars.ness.is_thunder_destroy==123);
            }
        }
    }
    for(row=0;row<ARRAY_COUNT(sFTCharBuilderSpecialPaths);row++) {
        const FTCharBuilderSpecialPath *p=&sFTCharBuilderSpecialPaths[row];
        CHECK(ftMainCharBuilderSpecialTiming(p->donor,p->motion)==&p->move);
        CHECK(p->trajectory.count==p->move.duration+1);
        for(body=0;body<12;body++) for(port=0;port<4;port++) for(facing=-1;facing<=1;facing+=2) {
            FTStruct *fp=&fighters[port];
            fp->player=port;fp->fkind=body;fp->lr=facing;fp->status_id=232;
            fp->motion_id=nFTCommonMotionWait;fp->joints[0]=&top;fp->joints[1]=&trans;
            gobj.user_data.p=fp;gobj.obj=&top;top.translate.vec.f=(Vec3f){-1200,730,50};
            trans.rotate.vec.f.z=0;active_donors[port]=p->donor;
            sFTMainCharBuilderSpecialMotionIDs[port]=p->motion;
            fp->attr=&body_attrs;
            CHECK(ftMainCharBuilderGetSpecialAttributes(fp)==&donor_attrs[p->donor]);
            ftCustomMoveStartClock(fp,&p->move,0);
            for(frame=0;frame<p->move.duration;frame++) {
                ftCustomMoveAdvanceClock(fp,0);
                CHECK(ftMainCharBuilderActivePath(fp)==p);
                ftPhysicsApplyAirVelFriction(&gobj);
                CHECK(last_physics_attrs==(p->travel ? &donor_attrs[p->donor] : &body_attrs));
                CHECK(ftMainCharBuilderGetSpecialTravel(fp,&actual,TRUE)==(p->travel!=NULL));
                if(p->travel) {
                    Vec3f d=p->travel[frame].delta;f32 a=p->travel[frame].angle;
                    CHECK(actual.x==d.x && actual.y==d.y && actual.z==d.z);
                    CHECK(ftMainCharBuilderGetSpecialTravel(fp,&actual,FALSE));
                    fp->joints[1]=NULL;
                    ftPhysicsGetAirVelTransN(fp,&actual.x,&actual.y,&actual.z);
                    fp->joints[1]=&trans;
                    CHECK(NEAR(actual.x,d.x*facing*__cosf(a)-d.y*__sinf(a)));
                    CHECK(NEAR(actual.y,d.x*facing*__sinf(a)+d.y*__cosf(a)));
                    CHECK(actual.z==d.z*facing);
                    if(p->motion==nFTCaptainMotionSpecialLwAir) {
                        f32 slope=0.35F;
                        fp->joints[1]=NULL;ftMainCharBuilderSetSpecialTravelAngle(fp,slope);
                        CHECK(ftMainCharBuilderGetSpecialTravel(fp,&actual,FALSE));
                        CHECK(NEAR(actual.x,d.x*facing*__cosf(a+slope)-d.y*__sinf(a+slope)));
                        CHECK(NEAR(actual.y,d.x*facing*__sinf(a+slope)+d.y*__cosf(a+slope)));
                        ftMainCharBuilderSetSpecialTravelAngle(fp,0);fp->joints[1]=&trans;
                    }
                }
                CHECK(ftMainCharBuilderGetSpecialSpawn(&gobj,&actual)==(p->spawn!=NULL));
                if(p->spawn) {
                    CHECK(NEAR(actual.x,-1200+p->spawn[frame].x*facing));
                    CHECK(NEAR(actual.y,730+p->spawn[frame].y));
                    CHECK(NEAR(actual.z,50+p->spawn[frame].z*facing));
                }
            }
            ftCustomMoveResetClock(fp);
            active_donors[port]=-1;
            CHECK(ftMainCharBuilderGetSpecialAttributes(fp)==&body_attrs);
            ftPhysicsApplyAirVelFriction(&gobj);CHECK(last_physics_attrs==&body_attrs);
            CHECK(!ftMainCharBuilderGetSpecialTravel(fp,&actual,TRUE));
            CHECK(!ftMainCharBuilderGetSpecialSpawn(&gobj,&actual));
        }
    }
    ftCustomMoveStartClock(&fighters[0],&sFTCharBuilderSuperJumpLanding,0);
    CHECK(ftCustomMoveGetClock(&fighters[0])->duration==25);
    for(frame=0;frame<25;frame++) CHECK(ftCustomMoveAdvanceClock(&fighters[0],-1)>=0);
    CHECK(ftCustomMoveAdvanceClock(&fighters[0],-1)<0);
    replacement.player=0;replacement.fkind=nFTKindCaptain;replacement.player_num=77;
    CHECK(ftMainCharBuilderGetNessPassive(&replacement)->is_thunder_destroy==0);
    replacement.player=4;replacement.fkind=nFTKindNess;
    replacement.passive_vars.mario.is_expend_tornado=987;
    *ftMainCharBuilderGetTornadoExpend(&replacement)=TRUE;
    mpCommonSetFighterGround(&replacement);
    CHECK(replacement.passive_vars.mario.is_expend_tornado==987);
    replacement.player=0;replacement.fkind=nFTKindNNess;
    CHECK(ftMainCharBuilderGetNessPassive(&replacement)==&replacement.passive_vars.ness);
    return 0;
}
void _start(void) {
    int result=test();
    if(result) {
        char message[]="Special timing CHECK line 0000\n";int i,v=result;
        for(i=29;i>=26;i--) {message[i]='0'+v%10;v/=10;}
        __asm__ volatile("int $0x80" : : "a"(4),"b"(2),"c"(message),"d"(sizeof(message)-1) : "memory");
    }
    __asm__ volatile("int $0x80" : : "a"(1),"b"(result) : "memory");
    __builtin_unreachable();
}
'''
build=ROOT/'build';build.mkdir(exist_ok=True)
# IDO accepts extern arrays of not-yet-defined structs; GCC does not. Remove
# only those unused declarations in a fixture include tree, retaining layouts.
headers=prepare(ROOT,build/'special-host-headers')
(build/'testSpecialTiming.c').write_text(source)
subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-O1',
                '-I'+str(headers),'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C',
                '-D_MIPS_SZLONG=32','-DREGION_US',str(build/'testSpecialTiming.c'),
                '-o',str(build/'testSpecialTiming')],check=True)
subprocess.run([str(build/'testSpecialTiming')],check=True)
print(f'PASS: {len(catalog())} source special clocks, 12 bodies/four slots, loop/transition progress, {len(path_catalog())} collision/travel/socket phases and isolated Ness/Tornado state.')
