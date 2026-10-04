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
typedef struct FTCustomAnimationPackedFrame
{
    s16 rotate[24][3], root_translate[3];
} FTCustomAnimationPackedFrame;

typedef struct FTCustomAnimationPackedClip
{
    const FTCustomAnimationPackedFrame *frames;
    s32 count;
} FTCustomAnimationPackedClip;

#include "ftcustomanimationpacked.generated.inc"
u32 gFTCustomAnimationValidationFailures;

static const FTCustomAnimationPackedFrame* ftCustomAnimationGetPackedFrame(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomAnimationPackedClip *clip;
    u32 offset, index;
    s32 frame;
    if ((clock == NULL) || (fp->fkind != nFTKindMario) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    /* Special and capture clocks must never index the normal pose registry. */
    offset = (u32)clock->move - (u32)sFTCustomMoves;
    if ((offset >= sizeof(sFTCustomMoves)) || (offset % sizeof(FTCustomMoveDefinition))) return NULL;
    index = offset / sizeof(FTCustomMoveDefinition);
    clip = &sFTCustomAnimationPackedClips[index / 33][index % 33];
    if ((clip->frames == NULL) || (clip->count <= 0)) return NULL;
    frame = (s32)clock->frame;
    if (frame < 0) frame = 0;
    if (frame >= clip->count) frame = clip->count - 1;
    return &clip->frames[frame];
}

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
    const FTCustomAnimationPackedFrame *packed = ftCustomAnimationGetPackedFrame(fp);
    DObj *joint;
    s32 i;
    if ((frame == NULL) && (packed == NULL)) return;
    /* Validate the entire mapped rig before changing any part of the pose. */
    for (i = 4; i < 28; i++)
    {
        if (fp->joints[i] == NULL)
        {
            gFTCustomAnimationValidationFailures++;
            return;
        }
    }
    if (packed != NULL)
    {
        /* Donor reserved rotations are already folded into the mapped pose.
           Remove the body's cosmetic channels to avoid applying them twice.
           TopN/facing and detached TransN/physics remain engine-owned. */
        for (i = nFTPartsJointXRotN; i <= nFTPartsJointYRotN; i++)
        {
            joint = fp->joints[i];
            if (joint == NULL) continue;
            joint->rotate.vec.f.x = joint->rotate.vec.f.y = joint->rotate.vec.f.z = 0.0F;
            joint->translate.vec.f.x = joint->translate.vec.f.y = joint->translate.vec.f.z = 0.0F;
            joint->scale.vec.f.x = joint->scale.vec.f.y = joint->scale.vec.f.z = 1.0F;
        }
    }
    for (i = 0; i < 24; i++)
    {
        joint = fp->joints[i + 4];
        if (frame != NULL)
        {
            joint->rotate.vec.f = frame->joints[i].rotate;
            joint->translate.vec.f = frame->joints[i].translate;
        }
        else
        {
            joint->rotate.vec.f.x = packed->rotate[i][0] * (1.0F / 4096.0F);
            joint->rotate.vec.f.y = packed->rotate[i][1] * (1.0F / 4096.0F);
            joint->rotate.vec.f.z = packed->rotate[i][2] * (1.0F / 4096.0F);
            joint->translate.vec.f = sFTCustomAnimationMarioBind[i];
            if (i == 0)
            {
                joint->translate.vec.f.x = packed->root_translate[0] * (1.0F / 16.0F);
                joint->translate.vec.f.y = packed->root_translate[1] * (1.0F / 16.0F);
                joint->translate.vec.f.z = packed->root_translate[2] * (1.0F / 16.0F);
            }
        }
        joint->scale.vec.f.x = joint->scale.vec.f.y = joint->scale.vec.f.z = 1.0F;
    }
}
