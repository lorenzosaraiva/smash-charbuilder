/* Specials share the normal retargeter, never foreign fighter DObjs. */
typedef struct FTCustomSpecialAttachmentFrame { Vec3f rotate, translate, scale; sb32 active; } FTCustomSpecialAttachmentFrame;
typedef struct FTCustomSpecialAttachment { const FTCustomSpecialAttachmentFrame *frames; s32 joint, part; sb32 hide_body; } FTCustomSpecialAttachment;
typedef struct FTCustomSpecialAnimation
{
    const FTCustomMoveDefinition *move;
    const FTCustomAnimationClip *clip;
    const ftMotionCommand *visual;
    s32 donor;
    const FTCustomSpecialAttachment *attachment;
} FTCustomSpecialAnimation;
#include "ftspecialanimations.generated.inc"

static const FTCustomSpecialAnimation* ftCustomAnimationSpecialDefinition(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    s32 i;
    if ((clock == NULL) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    for (i = 0; i < ARRAY_COUNT(sFTCustomSpecialAnimations); i++)
        if (clock->move == sFTCustomSpecialAnimations[i].move) return &sFTCustomSpecialAnimations[i];
    return NULL;
}

static void ftMainCharBuilderStartSpecialVisualScript(FTStruct *fp, f32 frame)
{
    const FTCustomSpecialAnimation *definition = ftCustomAnimationSpecialDefinition(fp);
    s32 i;
    if (definition == NULL) return;
    for (i = 0; i < 2; i++)
    {
        fp->motion_scripts[i][1].p_script = (ftMotionCommand*)definition->visual;
        fp->motion_scripts[i][1].script_wait = 1.0F - frame;
        fp->motion_scripts[i][1].script_id = 0;
    }
}

static struct FTCustomRecoveryPose
{
    FTStruct *owner;
    u32 player_num;
    s32 status, donor, frame;
} sFTCustomRecoveryPoses[4];

static s32 ftCustomAnimationSpecialFrame(const FTCustomAnimationClip *clip, f32 frame)
{
    s32 index = (s32)frame;
    if (index < 0) index = 0;
    if ((clip->loop_period > 0) && (index >= clip->loop_start))
        index = clip->loop_start + (index - clip->loop_start) % clip->loop_period;
    if (index >= clip->count) index = clip->count - 1;
    return index;
}

static const FTCustomAnimationClip* ftCustomAnimationGetSpecialClip(FTStruct *fp, s32 *frame)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomAnimationClip *clip;
    s32 i, donor = ftMainCharBuilderGetSuperJumpRecoveryDonor(fp);
    if (donor >= 0)
    {
        clip = sFTCustomSpecialRecoveryClips[donor][fp->status_id == nFTCommonStatusLandingFallSpecial];
        if (clip == NULL) return NULL;
        if (fp->status_id == nFTCommonStatusLandingFallSpecial)
        {
            if (clock == NULL) return NULL;
            /* Landing lag is gameplay time; playback uses the donor clip rate. */
            *frame = ftCustomAnimationSpecialFrame(clip, clock->frame * (clip->count - 1) / clock->duration);
        }
        else *frame = ftCustomAnimationSpecialFrame(clip, sFTCustomRecoveryPoses[fp->player].frame);
        return clip;
    }
    if (clock == NULL) return NULL;
    for (i = 0; i < ARRAY_COUNT(sFTCustomSpecialAnimations); i++)
        if (clock->move == sFTCustomSpecialAnimations[i].move)
        {
            clip = sFTCustomSpecialAnimations[i].clip;
            *frame = ftCustomAnimationSpecialFrame(clip, clock->frame);
            return clip;
        }
    return NULL;
}

static void ftMainCharBuilderAdvanceRecoveryPose(FTStruct *fp)
{
    struct FTCustomRecoveryPose *pose;
    s32 donor = ftMainCharBuilderGetSuperJumpRecoveryDonor(fp);
    if (fp->player >= 4) return;
    pose = &sFTCustomRecoveryPoses[fp->player];
    if ((donor < 0) || (ftCustomMoveGetSlot(fp) == NULL)) { pose->owner = NULL; return; }
    if ((pose->owner != fp) || (pose->player_num != fp->player_num) ||
        (pose->status != fp->status_id) || (pose->donor != donor))
    {
        pose->owner = fp; pose->player_num = fp->player_num;
        pose->status = fp->status_id; pose->donor = donor; pose->frame = 0;
    }
    else pose->frame++;
}

/* Visual attachments use semantic roles. Gameplay sockets keep donor paths. */
DObj* ftMainCharBuilderGetSpecialVisualJoint(FTStruct *fp, s32 donor, s32 source_joint)
{
    const FTCustomAnimationRig *body;
    const FTCustomAnimationBone *bone;
    s32 role, i;
    if ((fp->fkind < 0) || (fp->fkind >= 12) || (donor < 0) || (donor >= 12)) return fp->joints[0];
    if (donor == fp->fkind) return (source_joint >= 0 && source_joint < FTPARTS_JOINT_NUM_MAX && fp->joints[source_joint]) ? fp->joints[source_joint] : fp->joints[0];
    body = &sFTCustomAnimationRigs[fp->fkind];
    for (role = 0; role < 24; role++) if (sFTCustomAnimationSemanticJoints[donor][role] == source_joint)
        for (i = 0; i < body->count; i++)
        {
            bone = &body->bones[i];
            if ((bone->role == role) && (fp->joints[bone->joint] != NULL)) return fp->joints[bone->joint];
        }
    return fp->joints[nFTPartsJointTopN];
}

sb32 ftMainCharBuilderIsSpecialVisual(FTStruct *fp)
{
    return ftCustomAnimationSpecialDefinition(fp) != NULL;
}

static s32 ftMainCharBuilderVisualMotionJoint(FTStruct *fp, s32 source_joint)
{
    const FTCustomSpecialAnimation *definition = ftCustomAnimationSpecialDefinition(fp);
    DObj *joint;
    s32 i;
    if (source_joint == 127) return -1;
    if (definition == NULL) return ftParamGetJointID(fp, source_joint);
    joint = ftMainCharBuilderGetSpecialVisualJoint(fp, definition->donor, source_joint);
    for (i = 0; i < FTPARTS_JOINT_NUM_MAX; i++) if (joint == fp->joints[i]) return i;
    return nFTPartsJointTopN;
}

static void ftMainCharBuilderApplySpecialVisuals(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    const FTCharBuilderSpecialPath *path = ftMainCharBuilderActivePath(fp);
    DObj *root = fp->joints[4];
    if ((path == NULL) || (root == NULL)) return;
    if (((path->donor == nFTKindFox) && ((path->motion == nFTFoxMotionSpecialHi) || (path->motion == nFTFoxMotionSpecialAirHi))) ||
        ((path->donor == nFTKindPikachu) && ((path->motion == nFTPikachuMotionSpecialHi) || (path->motion == nFTPikachuMotionSpecialAirHi))))
        root->rotate.vec.f.x = (syUtilsArcTan2(fp->physics.vel_air.x, fp->physics.vel_air.y) * fp->lr) - F_CST_DTOR32(90.0F);
    else if (((path->donor == nFTKindMario) || (path->donor == nFTKindLuigi)) &&
             ((path->motion == nFTMarioMotionSpecialHi) || (path->motion == nFTMarioMotionSpecialAirHi)))
        root->rotate.vec.f.x -= sFTMainCharBuilderSpecialTravelAngles[fp->player] * fp->lr;
}
