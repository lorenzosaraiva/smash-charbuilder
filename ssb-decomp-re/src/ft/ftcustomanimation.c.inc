/* Pilot poses own no DObjs, scripts, animation heaps or fighter callbacks. */
typedef struct FTCustomAnimationJoint
{
    Vec3f rotate, translate;
} FTCustomAnimationJoint;

typedef struct FTCustomAnimationFrame
{
    FTCustomAnimationJoint joints[24]; /* Mario native IDs 4..27. */
    FTCustomCollisionFrame collision;
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
