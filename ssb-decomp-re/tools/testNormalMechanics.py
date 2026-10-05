#!/usr/bin/env python3
"""Production normal callbacks, donor identity and clocks on actual 32-bit layouts."""
import re, struct, subprocess
from pathlib import Path
from hostFighterHeaders import prepare
from generateNormalMechanics import render, catalog
from customAnimation import source_size
from elfData import read_elf
ROOT=Path(__file__).resolve().parents[1]

def function(text,name):
    m=re.search(r'^[\w *]+\b'+name+r'\([^;]*?\)[^\n{;]*\s*\{',text,re.M);assert m,name
    start=m.start();brace=text.index('{',start);depth=1;end=brace+1
    while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]+'\n'
def functions(file,names):
    text=(ROOT/file).read_text();return ''.join(function(text,n) for n in names.split())
assert (ROOT/'src/ft/ftnormalmechanics.generated.inc').read_text()==render()
# Ask the target compiler which bit the native runtime actually reads. Host
# bitfield packing differs, so reading the union's word on x86 is not an oracle.
headers=prepare(ROOT,ROOT/'build/normal-host-headers')
mask_source=ROOT/'build/normal-transn-mask.c'
mask_source.write_text('#include <ft/fighter.h>\nconst FTAnimDesc sNativeTransNMask = { .flags = { .is_use_transn_joint = TRUE } };\n')
mask_object=ROOT/'build/normal-transn-mask.o'
subprocess.run(['clang','--target=mips-unknown-none','-c','-EB','-mabi=32','-march=mips2','-ffreestanding',
    '-I'+str(headers),'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',str(mask_source),'-o',str(mask_object)],check=True)
data,sections,symbols=read_elf(mask_object,'>')
value,length,index=symbols['sNativeTransNMask']
native_transn_mask=struct.unpack_from('>I',data,sections[index][4]+value-sections[index][3])[0]
source=r'''
#include <ft/fighter.h>
#include <it/item.h>
#include <ft/ftcustommove.h>
#include <sc/scene.h>
#define FTCHARBUILDER_NEUTRAL_EXTENDED
#define FTCHARBUILDER_NORMAL_MECHANICS
SCCommonData gSCManagerSceneData;
SCCharBuilderSlot gSCManagerCharBuilderSlots[4];s8 gSCManagerCharBuilderPlayerSlots[4];
FTData *dFTManagerDataFiles[32];static FTData files[12];static FTAttributes attrs[12];static void *main_files[12];
void bzero(void *p,int n) { unsigned char *q=p;while(n--)*q++=0; }
#include "ft/ftcustommove.c.inc"
#include "ft/ftnormalmechanics.c.inc"
FTAttributes* ftMainCharBuilderGetSpecialAttributes(FTStruct *fp) { return ftCustomNormalGetAttributes(fp); }
FTAttributes* ftMainCharBuilderGetSuperJumpAttributes(FTStruct *fp) { return fp->attr; }
sb32 ftMainCharBuilderGetSpecialTravel(FTStruct *fp,Vec3f *v,sb32 g) { return ftCustomNormalGetTravel(fp,v,g); }
static FTStruct fp;static GObj g;static DObj joints[FTPARTS_JOINT_NUM_MAX];static int set_status,clears,refreshes;
static s32 attack_for_motion(s32 m) {
    int i;for(i=0;i<29;i++)if(sFTCustomMotionIDs[i]==m)return i;
    return -1;
}
void ftMainSetStatus(GObj *g,s32 status,f32 begin,f32 speed,u32 flags) {
    FTStruct *f=ftGetStruct(g);int donor=ftMainCharBuilderGetNormalKind(f,nSCCharBuilderAttackJab);
    ftCustomMoveResetClock(f);f->status_id=status;set_status=status;
    if(status>=FTCUSTOMMOVE_JAB_STATUS_START && status<=FTCUSTOMMOVE_JAB_STATUS_END)
        f->motion_id=sFTCustomBodyExtraMotionIDs[donor][status-FTCUSTOMMOVE_JAB_STATUS_START];
    else if(status==nFTCommonStatusAttack11)f->motion_id=nFTCommonMotionAttack11;
    else if(status==nFTCommonStatusAttack12)f->motion_id=nFTCommonMotionAttack12;
    else if(status==nFTCommonStatusAttackAirLw)f->motion_id=nFTCommonMotionAttackAirLw;
    else f->motion_id=nFTCommonMotionWait;
    ftCustomMoveStartClock(f,ftCustomMoveGetDefinition(f),begin);
    f->is_reflect=FALSE;g->anim_frame=begin;
}
void ftMainPlayAnimEventsAll(GObj *g) {}
sb32 ftCommonGetCheckInterruptCommon(GObj *g) { return FALSE; }
sb32 ftCommonCatchCheckInterruptAttack11(GObj *g) { return FALSE; }
void ftAnimEndSetWait(GObj *g) { if(g->anim_frame<=0)ftMainSetStatus(g,nFTCommonStatusWait,0,1,0); }
void ftAnimEndSetFall(GObj *g) { if(g->anim_frame<=0)ftMainSetStatus(g,nFTCommonStatusFall,0,1,0); }
sb32 ftAnimEndCheckSetStatus(GObj *g,void (*f)(GObj*)) { if(g->anim_frame<=0){f(g);return TRUE;}return FALSE; }
void ftParamClearAttackCollAll(GObj *g) { clears++; }
void ftParamRefreshAttackCollID(GObj *g,s32 id) { refreshes++; }
void ftParamSetMotionID(FTStruct *f,s32 id) {}
void ftParamSetStatUpdate(FTStruct *f,u16 flags) {}
void ftParamUpdate1PGameAttackStats(FTStruct *f,u16 flags) {}
void ftCommonItemThrowSetStatus(GObj *g,s32 status) {}
void ftCommonItemSwingSetStatus(GObj *g,s32 status) {}
void ftCommonItemShootSetStatus(GObj *g) {}
void gmCollisionGetFighterPartsWorldPosition(DObj *d,Vec3f *v) {}
GObj* efManagerKirbyVulcanJabMakeEffect(Vec3f *p,s32 lr,f32 r,f32 v,f32 a) { return NULL; }
extern int llKirbyMainMotionftKirbyAttack100Effect;
void *gFTDataKirbyMainMotion;__asm__(".global llKirbyMainMotionftKirbyAttack100Effect\n.set llKirbyMainMotionftKirbyAttack100Effect,0");
f32 dMPCollisionMaterialFrictions[16]={1};
sb32 ftParamCheckSetFighterColAnimID(GObj *g,s32 id,s32 tics) { return FALSE; }
void ftMainRunUpdateColAnim(GObj *g) {}
'''
for file in ('ftcommonattack1.c','ftcommonattack100.c'):
    text=(ROOT/'src/ft/ftcommon'/file).read_text()
    source+=text[text.index('#define ftCommonAttack'):]
source+=functions('src/ft/ftcommon/ftcommonattackair.c','ftCommonAttackAirLwProcHit ftCommonAttackAirLwProcUpdate')
# Only the bat flag branch needs resources here; actual native field geometry is
# tested below. Live ROM tests cover preload and real projectile ownership.
smash=function((ROOT/'src/ft/ftcommon/ftcommonattacks4.c').read_text(),'ftCommonAttackS4ProcUpdate')
begin=smash.index('    case nFTKindPikachu:');end=smash.index('    case nFTKindNess:',begin)
source+=smash[:begin]+smash[end:]
source+=functions('src/ft/ftphysics.c','ftPhysicsSetGroundVelTransferAir ftPhysicsSetGroundVelFriction ftPhysicsApplyGroundVelFriction ftPhysicsApplyGroundVelTransN ftPhysicsApplyGroundFrictionOrTransN ftPhysicsApplyGravityClampTVel ftPhysicsApplyGravityDefault ftPhysicsApplyFastFall ftPhysicsCheckClampAirVelXDec ftPhysicsCheckClampAirVelXDecMax ftPhysicsClampAirVelXStickRange ftPhysicsClampAirVelXStickDefault ftPhysicsApplyAirVelXFriction ftPhysicsApplyAirVelDrift')
source+='static const f32 source_sizes[12]={'+','.join(str(source_size(f))+'F' for f in ('Mario','Fox','Donkey','Samus','Luigi','Link','Yoshi','Captain','Kirby','Pikachu','Purin','Ness'))+'};\n'
source+='static const u32 native_transn_mask='+str(native_transn_mask)+'U;\n'
source+=r'''
#define CHECK(x) do { if(!(x))return __LINE__; } while(0)
#define NEAR(a,b) (ABSF((a)-(b))<0.001F)
int test(void) {
    int b,d,p,i,j,phase,has3,rapid;FTCustomMoveClock *clock;Vec3f v,size;Mtx44f matrix;
    static FTSpecialColl bat={nFTSpecialCollKindNessReflector,0,{0,150,0},{300,300,300},1000};
    gSCManagerSceneData.scene_curr=nSCKind1PTrainingMode;
    for(d=0;d<12;d++){files[d].p_file_main=&main_files[d];main_files[d]=&attrs[d];dFTManagerDataFiles[d]=&files[d];attrs[d].size=source_sizes[d];attrs[d].traction=d+1;attrs[d].attack1_followup_frames=20+d;attrs[d].is_have_attack11=TRUE;attrs[d].is_have_attack12=d!=9;attrs[d].gravity=d+1;attrs[d].tvel_base=1000;attrs[d].air_speed_max_x=1000;}
    for(b=0;b<12;b++)for(d=0;d<12;d++)for(p=0;p<4;p++) {
        bzero(&fp,sizeof(fp));bzero(&g,sizeof(g));g.user_data.p=&fp;fp.fighter_gobj=&g;g.obj=&joints[0];
        for(i=0;i<FTPARTS_JOINT_NUM_MAX;i++)fp.joints[i]=&joints[i];
        if(b==3)fp.joints[17]=NULL; /* Native cannon skeleton has no right hand. */
        for(i=0;i<12;i++){files[i].o_attributes=0;}
        fp.fkind=b;fp.player=p;fp.player_num=42;fp.pkind=nFTPlayerKindMan;fp.attr=&attrs[b];fp.lr=1;
        fp.input.button_mask_a=0x80;gSCManagerCharBuilderPlayerSlots[p]=p;
        gSCManagerCharBuilderSlots[p].is_enabled=TRUE;gSCManagerCharBuilderSlots[p].body=b;
        for(i=0;i<13;i++)gSCManagerCharBuilderSlots[p].attacks[i]=d;
        CHECK(!ftCustomMoveIsNormalDefinition(&sFTCustomGrabMoves[d]));
        for(i=0;i<33;i++){
            CHECK((sFTCustomNormalMechanics[d][i].travel!=NULL)==((sFTCustomNormalMechanics[d][i].flags&native_transn_mask)!=0));
            CHECK(ftCustomMoveIsNormalDefinition(&sFTCustomMoves[d][i]));
            u32 failures=gFTCustomMoveValidationFailures;
            CHECK(ftCustomMoveBuildScript(&fp,&sFTCustomMoves[d][i])!=NULL);
            CHECK(gFTCustomMoveValidationFailures==failures);
        }
        CHECK(ftMainCharBuilderGetNormalKind(&fp,nSCCharBuilderAttackJab)==d);
        CHECK(ftMainCharBuilderGetAttackAttributes(&fp,nSCCharBuilderAttackJab)==&attrs[d]);
        ftCommonAttack11SetStatus(&g);CHECK(fp.attack1_followup_frames==20+d);
        /* Pikachu repeats jab one; other donors queue jab two. */
        fp.motion_vars.flags.flag1=1;fp.status_vars.common.attack1.is_goto_followup=TRUE;g.anim_frame=1;
        ftCommonAttack11ProcUpdate(&g);CHECK(set_status==(d==9?nFTCommonStatusAttack11:nFTCommonStatusAttack12));
        if(d!=9){
        has3=d==0||d==4||d==5||d==7||d==11;rapid=d==1||d==5||d==7||d==8||d==10;
        fp.input.pl.button_tap=0x80;fp.attack1_followup_frames=15;fp.motion_vars.flags.flag1=1;
        CHECK(ftCommonAttack13CheckGoto(&g)==has3);
        if(has3 && b!=d)CHECK(fp.status_id==FTCUSTOMMOVE_JAB_STATUS_START);
        if(rapid){
            fp.attack1_input_count=0;fp.is_goto_attack100=FALSE;
            fp.status_id=d==7?ftMainCharBuilderGetJabStatus(&fp,nFTCaptainStatusAttack13,0):nFTCommonStatusAttack12;
            fp.motion_vars.flags.flag1=0;
            for(i=0;i<(d==5?5:d==7?6:4)-1;i++){CHECK(!ftCommonAttack100StartCheckInterruptCommon(&g));CHECK(!fp.is_goto_attack100);}
            CHECK(!ftCommonAttack100StartCheckInterruptCommon(&g));CHECK(fp.is_goto_attack100);
            if(b!=d){
                ftCommonAttack100StartSetStatus(&g);CHECK(fp.status_id==FTCUSTOMMOVE_JAB_STATUS_START+1);
                g.anim_frame=-1;ftCommonAttack100StartProcUpdate(&g);CHECK(fp.status_id==FTCUSTOMMOVE_JAB_STATUS_START+2);
                clock=ftCustomMoveGetClock(&fp);CHECK(clock && clock->move==&sFTCustomMoves[d][31]);
                for(i=0;i<clock->duration*3;i++){f32 f=ftCustomMoveAdvanceClock(&fp,123);CHECK(f>=0 && f<clock->duration);}
                if(d==7){
                    clock->frame=0;CHECK(ftCustomNormalGetTravel(&fp,&v,TRUE));CHECK(NEAR(v.x,0));
                    for(i=1;i<=3;i++){
                        clock->frame=clock->duration*i;CHECK(ftCustomNormalGetTravel(&fp,&v,TRUE));
                        CHECK(NEAR(v.x,sFTCustomNormalMechanics[d][31].travel[clock->duration].x));CHECK(ABSF(v.x)>0.1F);
                    }
                }
                fp.motion_vars.flags.flag1=1;fp.status_vars.common.attack100.is_anim_end=TRUE;fp.status_vars.common.attack100.is_goto_loop=FALSE;
                ftCommonAttack100LoopProcUpdate(&g);CHECK(fp.status_id==FTCUSTOMMOVE_JAB_STATUS_START+3);
            }
        }else CHECK(!ftCommonAttack100StartCheckInterruptCommon(&g));
        }
        if(b==d)continue;
        /* Root travel uses donor scale, not retargeted body proportions. */
        fp.status_id=nFTCommonStatusAttackDash;fp.motion_id=nFTCommonMotionAttackDash;
        ftCustomMoveStartClock(&fp,&sFTCustomMoves[d][2],0);clock=ftCustomMoveGetClock(&fp);clock->frame=10;
        CHECK(ftMainCharBuilderGetSpecialAttributes(&fp)==&attrs[d]);
        CHECK(ftMainCharBuilderUsesNormalTransN(&fp)==((sFTCustomNormalMechanics[d][2].flags&native_transn_mask)!=0));
        CHECK(ftCustomNormalGetTravel(&fp,&v,TRUE));ftPhysicsApplyGroundVelTransN(&g);CHECK(NEAR(fp.physics.vel_ground.x,v.x));
        fp.physics.vel_ground.x=100;fp.coll_data.floor_flags=0;ftPhysicsApplyGroundVelFriction(&g);CHECK(NEAR(fp.physics.vel_ground.x,100-(d+1)));
        fp.physics.vel_air.y=100;fp.physics.vel_air.x=0;ftPhysicsApplyAirVelDrift(&g);CHECK(fp.physics.vel_air.y==100-(d+1));
        /* Link bounce and delayed rehit run only for Link's selected down-air. */
        fp.status_id=nFTCommonStatusAttackAirLw;fp.motion_id=nFTCommonMotionAttackAirLw;
        ftCustomMoveStartClock(&fp,&sFTCustomMoves[d][23],0);g.anim_frame=40;fp.is_fastfall=TRUE;clears=refreshes=0;
        ftCommonAttackAirLwProcHit(&g);
        if(d==5){CHECK(clears==1 && !fp.is_fastfall && fp.physics.vel_air.y==FTCOMMON_ATTACKAIRLW_LINK_REHIT_BOUNCE_VEL_Y);CHECK(g.anim_frame==FTCOMMON_ATTACKAIRLW_LINK_REHIT_FRAME_BEGIN);for(i=0;i<FTCOMMON_ATTACKAIRLW_LINK_REHIT_TIMER;i++)ftCommonAttackAirLwProcUpdate(&g);CHECK(refreshes==2);}
        else CHECK(!clears && fp.is_fastfall);
        /* Ness reflection uses source flag window, radius and socket. */
        fp.status_id=nFTCommonStatusAttackS4;fp.motion_id=nFTCommonMotionAttackS4;g.anim_frame=19;
        ftCustomMoveStartClock(&fp,&sFTCustomMoves[d][14],0);fp.special_coll=&bat;fp.motion_vars.flags.flag1=1;
        CHECK(ftMainCharBuilderUsesNormalTransN(&fp)==((sFTCustomNormalMechanics[d][14].flags&native_transn_mask)!=0));
        clock=ftCustomMoveGetClock(&fp);clock->frame=12;
        fp.physics.vel_ground.x=100;ftPhysicsApplyGroundFrictionOrTransN(&g);
        CHECK(ftCustomNormalGetTravel(&fp,&v,TRUE));
        CHECK(NEAR(fp.physics.vel_ground.x,ftMainCharBuilderUsesNormalTransN(&fp)?v.x:100-(d+1)));
        ftCommonAttackS4ProcUpdate(&g);CHECK(fp.is_reflect==(d==11));
        CHECK(ftMainCharBuilderGetNormalSphere(&fp,matrix,&size)==(d==11));
        if(d==11){CHECK(NEAR(size.x,300*attrs[d].size) && NEAR(size.y,300*attrs[d].size));CHECK(NEAR(matrix[3][1],-150*attrs[d].size));}
        fp.motion_vars.flags.flag1=0;ftCommonAttackS4ProcUpdate(&g);CHECK(!fp.is_reflect);
        fp.player_num++;CHECK(!ftCustomMoveGetClock(&fp));CHECK(ftMainCharBuilderGetSpecialAttributes(&fp)==fp.attr);
        gSCManagerCharBuilderPlayerSlots[p]=-1;CHECK(ftMainCharBuilderGetNormalKind(&fp,nSCCharBuilderAttackJab)==b);
    }
    return 0;
}
void _start(void){int code=test();__asm__ volatile("int $0x80"::"a"(1),"b"(code):"memory");}
'''
headers=prepare(ROOT,ROOT/'build/normal-host-headers');path=ROOT/'build/testNormalMechanics.c';path.write_text(source)
subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-O1',
    '-I'+str(headers),'-I'+str(ROOT/'include'),'-I'+str(ROOT/'src'),'-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',str(path),'-o',str(ROOT/'build/testNormalMechanics')],check=True)
result=subprocess.run([str(ROOT/'build/testNormalMechanics')])
if result.returncode:
    raise AssertionError(('Normal callback check failed',result.returncode,[(i,l.strip()) for i,l in enumerate(source.splitlines(),1) if i%256==result.returncode and 'CHECK' in l]))
print('PASS: donor jab buffering/availability/rapid thresholds, loop/end clocks, Link bounce/rehit, Ness bat field, normal root travel/physics and lifecycle on twelve bodies/donors/four slots.')
