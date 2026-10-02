/* Collision lookup never reads or changes the target body's animated limbs. */
#include "ftcustomcollisions.generated.inc"

static const FTCustomCollisionFrame* ftCustomCollisionGetFrame(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    s32 frame, count;
    if ((clock == NULL) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    frame = (s32)clock->frame;
    if (frame < 0) frame = 0;
    /* Reuse pilot trajectories on every body without duplicating their data. */
    if (clock->move == &sFTCustomMoves[nFTKindCaptain][23])
    {
        count = ARRAY_COUNT(sFTCustomAnimationCaptain);
        if (frame >= count) frame = count - 1;
        return &sFTCustomAnimationCaptain[frame].collision;
    }
    if (clock->move == &sFTCustomMoves[nFTKindFox][5])
    {
        count = ARRAY_COUNT(sFTCustomAnimationFox);
        if (frame >= count) frame = count - 1;
        return &sFTCustomAnimationFox[frame].collision;
    }
    if (clock->move == &sFTCustomMoves[nFTKindDonkey][14])
    {
        count = ARRAY_COUNT(sFTCustomAnimationDonkey);
        if (frame >= count) frame = count - 1;
        return &sFTCustomAnimationDonkey[frame].collision;
    }
    /* Kirby has one up-tilt; the three selected-body variants share it. */
    if ((clock->move == &sFTCustomMoves[nFTKindKirby][8]) ||
        (clock->move == &sFTCustomMoves[nFTKindKirby][9]) ||
        (clock->move == &sFTCustomMoves[nFTKindKirby][10]))
    {
        count = ARRAY_COUNT(sFTCustomCollisionKirbyUTilt);
        if (frame >= count) frame = count - 1;
        return &sFTCustomCollisionKirbyUTilt[frame];
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
