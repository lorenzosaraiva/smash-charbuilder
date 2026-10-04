/* Collision lookup never reads or changes the target body's animated limbs. */
typedef struct FTCustomCollisionTrajectory
{
    const FTCustomCollisionFrame *frames;
    s32 first, count, loop_start, loop_period;
} FTCustomCollisionTrajectory;

#ifdef FTCHARBUILDER_NEUTRAL_EXTENDED
typedef struct FTCharBuilderNeutralActionDesc
{
    FTCustomMoveDefinition move;
    FTCustomCollisionTrajectory trajectory;
    const Vec3f *travel, *spawn, *anchor;
} FTCharBuilderNeutralActionDesc;
#include "ftneutralactions.generated.inc"
#endif
#include "ftcustomcollisions.generated.inc"
#include "ftcustomcollisionregistry.generated.inc"
static const FTCustomCollisionFrame sFTCustomCollisionInactive = { { { 0 } }, 0 };

static const FTCustomCollisionFrame* ftCustomCollisionSample(const FTCustomCollisionTrajectory *trajectory, s32 frame)
{
    if (trajectory->frames == NULL) return NULL;
    if (frame < 0) frame = 0;
    if ((trajectory->loop_period > 0) && (frame >= trajectory->loop_start))
        frame = trajectory->loop_start + (frame - trajectory->loop_start) % trajectory->loop_period;
    frame -= trajectory->first;
    if ((frame < 0) || (frame >= trajectory->count)) return &sFTCustomCollisionInactive;
    return &trajectory->frames[frame];
}

static const FTCustomCollisionFrame* ftCustomCollisionGetFrame(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    u32 offset, index;
    if ((clock == NULL) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
#ifdef FTCHARBUILDER_NEUTRAL_EXTENDED
    if (clock->trajectory != NULL) return ftCustomCollisionSample(clock->trajectory, (s32)clock->frame);
#endif
    /* Integer bounds avoid subtracting pointers from different objects: grab
       and special definitions share the clock but are outside the normal table. */
    offset = (u32)clock->move - (u32)sFTCustomMoves;
    if ((offset >= sizeof(sFTCustomMoves)) || (offset % sizeof(FTCustomMoveDefinition))) return NULL;
    index = offset / sizeof(FTCustomMoveDefinition);
    return ftCustomCollisionSample(&sFTCustomCollisionTrajectories[index / 33][index % 33], (s32)clock->frame);
}

static void ftCustomCollisionApply(FTStruct *fp)
{
    const FTCustomCollisionFrame *frame = ftCustomCollisionGetFrame(fp);
    FTAttackColl *attack;
    f32 inverse_size;
    s32 i;
    Vec3f center;
    if ((frame == NULL) || (fp->joints[nFTPartsJointTopN] == NULL) ||
        (fp->attr == NULL) || (fp->attr->size <= 0.0F)) return;
    inverse_size = 1.0F / fp->attr->size;
    for (i = 0; i < ARRAY_COUNT(fp->attack_colls); i++)
    {
        attack = &fp->attack_colls[i];
        if ((attack->attack_state == nGMAttackStateOff) || !(frame->active_mask & (1 << i))) continue;
        attack->joint_id = nFTPartsJointTopN;
        attack->joint = fp->joints[nFTPartsJointTopN];
        center = frame->centers[i];
#ifdef FTCHARBUILDER_SPECIAL_MECHANICS
        ftMainCharBuilderAdjustSpecialCollision(fp, &center);
#endif
        attack->offset.x = center.x * inverse_size;
        attack->offset.y = center.y * inverse_size;
        attack->offset.z = center.z * inverse_size;
        attack->is_scale_pos = FALSE;
        /* The engine owns radius, hit records, damage, state and swept history. */
    }
}
