#!/usr/bin/env python3
"""Compile the actual special clock/accessor with real 32-bit fighter layouts."""
import subprocess
from pathlib import Path
from generateSpecialTiming import catalog, render
from hostFighterHeaders import prepare

ROOT = Path(__file__).resolve().parents[1]
assert (ROOT/'src/ft/ftspecialtiming.generated.inc').read_text() == render()
clock = (ROOT/'src/ft/ftcustommove.c.inc').read_text()
clock = clock[clock.index('typedef struct FTCustomMoveClock'):clock.index('static s32 ftCustomJointResolve')]
main = (ROOT/'src/ft/ftmain.c').read_text()
timing = main[main.index('typedef struct FTCharBuilderSpecialTiming'):main.index('static s32 sFTMainCharBuilderSpecialDonors')]
timing = timing.replace('"ftspecialtiming.generated.inc"', '"ft/ftspecialtiming.generated.inc"')
source = r'''
#include <ft/fighter.h>
#include <ft/ftcustommove.h>
#define FTCHARBUILDER_NEUTRAL_EXTENDED
typedef struct FTCustomCollisionTrajectory {
    const FTCustomCollisionFrame *frames; s32 first, count, loop_start, loop_period;
} FTCustomCollisionTrajectory;
void bzero(void *p, int n) { unsigned char *q=p; while(n--) *q++=0; }
''' + clock + timing + r'''
static FTStruct fighters[4], replacement;
#define CHECK(c) do { if (!(c)) return __LINE__; } while(0)
static int test(void) {
    int row,body,port,frame;
    for (row=0;row<ARRAY_COUNT(sFTCharBuilderSpecialTimings);row++) {
        const FTCharBuilderSpecialTiming *s=&sFTCharBuilderSpecialTimings[row];
        CHECK(ftMainCharBuilderSpecialTiming(s->donor,s->motion)==&s->move);
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
            /* PK Thunder must never alter another body's native passive union. */
            fp->player_num=11;
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
    replacement.player=0;replacement.fkind=nFTKindCaptain;replacement.player_num=77;
    CHECK(ftMainCharBuilderGetNessPassive(&replacement)->is_thunder_destroy==0);
    replacement.fkind=nFTKindNNess;
    CHECK(ftMainCharBuilderGetNessPassive(&replacement)==&replacement.passive_vars.ness);
    return 0;
}
void _start(void) {
    int result=test();
    if(result) {
        char message[]="Special timing CHECK line 0000\n";int i,v=result;
        for(i=28;i>=25;i--) {message[i]='0'+v%10;v/=10;}
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
print(f'PASS: {len(catalog())} source special clocks, 12 bodies/four slots, loop/transition progress and isolated Ness trail state.')
