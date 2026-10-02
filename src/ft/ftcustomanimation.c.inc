/* Pilot poses own no DObjs, scripts, animation heaps or fighter callbacks. */
typedef struct FTCustomAnimationJoint
{
    Vec3f rotate, translate;
} FTCustomAnimationJoint;

typedef struct FTCustomAnimationFrame
{
    FTCustomAnimationJoint joints[24]; /* Mario native IDs 4..27. */
    Vec3f centers[FTCUSTOMMOVE_HITBOX_COUNT_MAX]; /* Scaled donor TopN coordinates. */
    u32 active_mask;
} FTCustomAnimationFrame;

#include "ftcustomanimations.generated.inc"
u32 gFTCustomAnimationValidationFailures;

static const FTCustomAnimationFrame* ftCustomAnimationGetFrame(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomAnimationFrame *frames;
    s32 frame, count;
    if ((clock == NULL) || (fp->fkind != nFTKindMario) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    if (clock->move == &sFTCustomMoves[nFTKindCaptain][23])
    {
        frames = sFTCustomAnimationCaptain; count = ARRAY_COUNT(sFTCustomAnimationCaptain);
    }
    else if (clock->move == &sFTCustomMoves[nFTKindFox][5])
    {
        frames = sFTCustomAnimationFox; count = ARRAY_COUNT(sFTCustomAnimationFox);
    }
    else if (clock->move == &sFTCustomMoves[nFTKindDonkey][14])
    {
        frames = sFTCustomAnimationDonkey; count = ARRAY_COUNT(sFTCustomAnimationDonkey);
    }
    else return NULL;
    frame = (s32)clock->frame;
    if (frame < 0) frame = 0;
    if (frame >= count) frame = count - 1;
    return &frames[frame];
}

static void ftCustomAnimationApplyPose(FTStruct *fp)
{
    const FTCustomAnimationFrame *frame = ftCustomAnimationGetFrame(fp);
    DObj *joint;
    s32 i;
    if (frame == NULL) return;
    /* Validate the entire mapped rig before changing any part of the pose. */
    for (i = 4; i < 28; i++)
    {
        if (fp->joints[i] == NULL)
        {
            gFTCustomAnimationValidationFailures++;
            return;
        }
    }
    for (i = 0; i < 24; i++)
    {
        joint = fp->joints[i + 4];
        joint->rotate.vec.f = frame->joints[i].rotate;
        joint->translate.vec.f = frame->joints[i].translate;
        joint->scale.vec.f.x = joint->scale.vec.f.y = joint->scale.vec.f.z = 1.0F;
    }
}

static void ftCustomAnimationApplyCollision(FTStruct *fp)
{
    const FTCustomAnimationFrame *frame = ftCustomAnimationGetFrame(fp);
    FTAttackColl *attack;
    f32 inverse_size;
    s32 i;
    if ((frame == NULL) || (fp->joints[nFTPartsJointTopN] == NULL) || (fp->attr->size <= 0.0F)) return;
    inverse_size = 1.0F / fp->attr->size;
    for (i = 0; i < ARRAY_COUNT(fp->attack_colls); i++)
    {
        attack = &fp->attack_colls[i];
        if ((attack->attack_state == nGMAttackStateOff) || !(frame->active_mask & (1 << i))) continue;
        attack->joint = fp->joints[nFTPartsJointTopN];
        attack->offset.x = frame->centers[i].x * inverse_size;
        attack->offset.y = frame->centers[i].y * inverse_size;
        attack->offset.z = frame->centers[i].z * inverse_size;
        attack->is_scale_pos = FALSE;
    }
}
