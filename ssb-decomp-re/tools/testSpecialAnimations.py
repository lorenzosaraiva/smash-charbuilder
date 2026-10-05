#!/usr/bin/env python3
"""Exercise the actual special pose selector, phase clocks and attachment maps."""
import subprocess
from customAnimation import ROOT
from sharedAnimation import catalog, special_rows, MAPS
from generateNeutralActions import catalog as actions
from generateNeutralProjectiles import catalog as projectiles
from generateSpecialTiming import path_catalog

def main():
    from prepareSharedAnimationTest import prepare_math
    prepare_math()
    rows=special_rows();cases,_=catalog()
    source=['struct DObj;void ftParamsUpdateFighterPartsTransform(struct DObj*);', 'struct GObj;static void ftMainCharBuilderUpdateSpecialAttachments(struct GObj *g) {}', '#define FTCHARBUILDER_SPECIAL_ANIMATIONS', '#define _start specialOldTestsEntry',
            '#include "../tools/testCustomMove.c"', '#undef _start',
            '#include <ef/efdef.h>', '#include <gm/gmsound.h>',
            'static s32 recoveryDonor=-1;',
            'static s32 ftMainCharBuilderGetSuperJumpRecoveryDonor(FTStruct *fp) { return (fp->status_id==nFTCommonStatusFallSpecial || fp->status_id==nFTCommonStatusLandingFallSpecial) ? recoveryDonor : -1; }',
            'static s32 ftParamGetJointID(FTStruct *fp,s32 joint) { return joint==127 ? -1 : joint; }']
    move=lambda d:'{ NULL, 0, '+str(d)+', 0 }'
    # Reuse the actual neutral and Up/Down B gameplay tables, including scripts.
    main=(ROOT/'src/ft/ftmain.c').read_text()
    source.append(main[main.index('typedef enum FTMainCharBuilderSpecialKind'):main.index('/* PK Thunder')].replace('"ftspecialtiming.generated.inc"','"ft/ftspecialtiming.generated.inc"'))
    runtime=(ROOT/'src/ft/ftspecialanimation.c.inc').read_text()
    runtime=runtime[:runtime.index('static void ftMainCharBuilderApplySpecialVisuals')]
    source.append(runtime.replace('"ftspecialanimations.generated.inc"','"ft/ftspecialanimations.generated.inc"'))
    source.append('static sb32 ftMainCharBuilderIsBorrowingMotion(FTStruct *fp) { return TRUE; }')
    source.append(main[main.index('static s32 ftMainCharBuilderGetMotionJointID('):main.index('static s32 ftMainCharBuilderGetSpecialMotionID(')])
    source.append(r'''
static s32 run(void)
{
    FTStruct fp={0};DObj joints[FTPARTS_JOINT_NUM_MAX]={0};
    s32 body,i,t,selected,expected,donor,phase; const FTCustomSpecialAnimation *definition;
    const FTCustomAnimationClip *clip;FTCustomMoveClock *clock;
    gSCManagerSceneData.scene_curr=nSCKind1PTrainingMode;
    fp.player=0;fp.player_num=123;fp.pkind=nFTPlayerKindMan;fp.status_id=220;fp.motion_id=221;
    for(i=0;i<FTPARTS_JOINT_NUM_MAX;i++)fp.joints[i]=&joints[i];
    for(body=0;body<12;body++)
    {
        fp.fkind=gSCManagerCharBuilderSlots[0].body=body;gSCManagerCharBuilderSlots[0].is_enabled=TRUE;
        for(i=0;i<ARRAY_COUNT(sFTCustomSpecialAnimations);i++)
        {
            definition=&sFTCustomSpecialAnimations[i];clip=definition->clip;
            ftCustomMoveStartClock(&fp,definition->move,1);clock=ftCustomMoveGetClock(&fp);
            for(t=0;t<clip->count+100;t++)
            {
                clock->frame=t+0.75F;expected=t;
                if(clip->loop_period && t>=clip->loop_start)expected=clip->loop_start+(t-clip->loop_start)%clip->loop_period;
                if(expected>=clip->count)expected=clip->count-1;
                CHECK(ftCustomAnimationGetClip(&fp,&selected)==clip && selected==expected);
            }
            ftMainCharBuilderStartSpecialVisualScript(&fp,7);
            CHECK(fp.motion_scripts[0][1].p_script==definition->visual && fp.motion_scripts[0][1].script_wait==-6);
            CHECK(ftCustomMoveEventFrame(&fp,&fp.motion_scripts[0][1],-9)==clock->frame);
            clock->speed=0.36F;CHECK(ftCustomMoveEventSpeed(&fp,&fp.motion_scripts[0][1],1)==0.36F);
            for(t=0;t<24;t++)
            {
                donor=sFTCustomAnimationSemanticJoints[definition->donor][t];
                CHECK(fp.joints[ftMainCharBuilderGetMotionJointID(&fp,donor,TRUE)]==ftMainCharBuilderGetSpecialVisualJoint(&fp,definition->donor,donor));
                CHECK(ftMainCharBuilderGetMotionJointID(&fp,donor,FALSE)==donor);
            }
            CHECK(ftCustomMoveEventFrame(&fp,&fp.motion_scripts[0][0],-9)==clock->native_frame);
            fp.player_num++;CHECK(ftCustomAnimationGetClip(&fp,&selected)==NULL);fp.player_num--;
            fp.status_id++;CHECK(ftCustomAnimationGetClip(&fp,&selected)==NULL);fp.status_id--;
            ftCustomMoveResetClock(&fp);CHECK(ftCustomAnimationGetClip(&fp,&selected)==NULL);
            CHECK(ftMainCharBuilderGetMotionJointID(&fp,127,TRUE)==-1);
            CHECK(ftMainCharBuilderGetMotionJointID(&fp,127,FALSE)==nFTPartsJointTopN);
            CHECK(ftMainCharBuilderGetMotionJointID(&fp,40,TRUE)==nFTPartsJointTopN);
        }
        for(donor=0;donor<12;donor++)for(i=0;i<24;i++)
        {
            DObj *joint=ftMainCharBuilderGetSpecialVisualJoint(&fp,donor,sFTCustomAnimationSemanticJoints[donor][i]);
            CHECK(joint!=NULL);
            if(donor==body)CHECK(joint==fp.joints[sFTCustomAnimationSemanticJoints[donor][i]]);
        }
        for(donor=0;donor<12;donor++)if(sFTCustomSpecialRecoveryClips[donor][0])
        {
            recoveryDonor=donor;
            fp.status_id=nFTCommonStatusFallSpecial;ftMainCharBuilderAdvanceRecoveryPose(&fp);
            CHECK(ftCustomAnimationGetClip(&fp,&selected)==sFTCustomSpecialRecoveryClips[donor][0] && selected==0);
            for(t=1;t<100;t++) { ftMainCharBuilderAdvanceRecoveryPose(&fp);CHECK(ftCustomAnimationGetClip(&fp,&selected)!=NULL); }
            fp.player_num++;ftMainCharBuilderAdvanceRecoveryPose(&fp);CHECK(sFTCustomRecoveryPoses[0].frame==0);
            fp.status_id=nFTCommonStatusLandingFallSpecial;ftMainCharBuilderAdvanceRecoveryPose(&fp);
            ftCustomMoveStartClock(&fp,&sFTCharBuilderLaserMoves[0],1);clock=ftCustomMoveGetClock(&fp);clock->duration=25;
            for(t=0;t<25;t++)
            {
                clock->frame=t;clip=sFTCustomSpecialRecoveryClips[donor][1];
                CHECK(ftCustomAnimationGetClip(&fp,&selected)==clip && selected==t*(clip->count-1)/25);
            }
            recoveryDonor=-1;fp.status_id=220;ftCustomMoveResetClock(&fp);ftMainCharBuilderAdvanceRecoveryPose(&fp);
            CHECK(sFTCustomRecoveryPoses[0].owner==NULL && ftCustomAnimationGetClip(&fp,&selected)==NULL);
        }
    }
    return 0;
}
void _start(void) { s32 result=run();__asm__ volatile("int $0x80"::"a"(1),"b"(result):"memory");__builtin_unreachable(); }
''')
    (ROOT/'build/testSpecialAnimations.c').write_text('\n'.join(source),encoding='utf-8',newline='\n')
    subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-O1','-Iinclude','-Isrc','-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US','build/testSpecialAnimations.c','-o','build/testSpecialAnimations'],cwd=ROOT,check=True)
    subprocess.run([str(ROOT/'build/testSpecialAnimations')],cwd=ROOT,check=True)
    print(f'PASS: {sum(p["binding"] is not None for p,i in rows)} special bindings across 12 bodies; startup/loop/release/recovery, fractional clocks, stale owners, visual-script clocks and semantic attachments.')

if __name__=='__main__':main()
