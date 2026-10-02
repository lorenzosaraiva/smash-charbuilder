/* Collision lookup never reads or changes the target body's animated limbs. */
typedef struct FTCustomCollisionTrajectory
{
    const FTCustomMoveDefinition *move;
    const FTCustomCollisionFrame *frames;
    s32 count, stride;
} FTCustomCollisionTrajectory;

#include "ftcustomcollisions.generated.inc"
#include "ftcustomcollisionregistry.generated.inc"

static const FTCustomCollisionFrame* ftCustomCollisionGetFrame(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomCollisionTrajectory *trajectory;
    s32 frame, i;
    if ((clock == NULL) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    frame = (s32)clock->frame;
    if (frame < 0) frame = 0;
    for (i = 0; i < ARRAY_COUNT(sFTCustomCollisionTrajectories); i++)
    {
        trajectory = &sFTCustomCollisionTrajectories[i];
        if (clock->move != trajectory->move) continue;
        if (frame >= trajectory->count) frame = trajectory->count - 1;
        return (const FTCustomCollisionFrame*)((const u8*)trajectory->frames + frame * trajectory->stride);
    }
    return NULL;
}

static void ftCustomCollisionApply(FTStruct *fp)
{
    const FTCustomCollisionFrame *frame = ftCustomCollisionGetFrame(fp);
    FTAttackColl *attack;
    f32 inverse_size;
    s32 i;
    if ((frame == NULL) || (fp->joints[nFTPartsJointTopN] == NULL) ||
        (fp->attr == NULL) || (fp->attr->size <= 0.0F)) return;
    inverse_size = 1.0F / fp->attr->size;
    for (i = 0; i < ARRAY_COUNT(fp->attack_colls); i++)
    {
        attack = &fp->attack_colls[i];
        if ((attack->attack_state == nGMAttackStateOff) || !(frame->active_mask & (1 << i))) continue;
        attack->joint_id = nFTPartsJointTopN;
        attack->joint = fp->joints[nFTPartsJointTopN];
        attack->offset.x = frame->centers[i].x * inverse_size;
        attack->offset.y = frame->centers[i].y * inverse_size;
        attack->offset.z = frame->centers[i].z * inverse_size;
        attack->is_scale_pos = FALSE;
        /* The engine owns radius, hit records, damage, state and swept history. */
    }
}
