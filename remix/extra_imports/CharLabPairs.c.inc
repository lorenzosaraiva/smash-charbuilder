extern s32 ccMappedThrownKind(s32, s32);
/* Remix parent mapping may resolve to an original polygon or boss variant. */
static s32 ccPairVictimKind(s32 kind, s32 direction)
{
    s32 mapped = ccMappedThrownKind(kind, direction);
    if (mapped == 13) return 0;
    if (mapped >= 14 && mapped <= 25) return mapped - 14;
    if (mapped == 26) return 2;
    return mapped;
}
extern void syDmaReadRom(uintptr_t, void*, size_t);
extern FTThrowReleaseDesc dFTCommonCaptureKnockbackCatch, dFTCommonCaptureKnockbackCapture;
static void ccPairSetStatus(GObj*, s32, f32, f32, u32);
s32 sCCPairDonors[4] = { -1, -1, -1, -1 };
#include "../build/char_creator/runtime/paired.c.inc"

static sb32 ccPairEffectLive(GObj *g)
{
    s32 p, i;
    for (p = 0; p < 4; p++)
        for (i = 0; i < 6; i++)
            if (sFTCustomPairProps[p].models[i] == g)
            {
                struct FTCustomPairState *s = &sFTCustomPairStates[p];
                GObj *fighter;
                for (fighter = gGCCommonLinks[nGCCommonLinkIDFighter]; fighter; fighter = fighter->link_next)
                    if (fighter == efGetStruct(g)->fighter_gobj)
                        return s->owner && ftGetStruct(fighter) == s->owner &&
                            s->owner == sFTCustomPairProps[p].owner && s->player_num == sFTCustomPairProps[p].player_num &&
                            ftCustomPairState(s->owner) != NULL;
                return FALSE;
            }
    return FALSE;
}

static const CCVisualDefinition* ccPairVisual(FTStruct *fp)
{
    static CCVisualDefinition definitions[4];
    struct FTCustomPairState *s = ftCustomPairState(fp);
    CCVisualDefinition *def;
    if (!s || !ftCustomMoveGetClock(fp)) return NULL;
    def = &definitions[fp->player];
    def->move = &s->phase->move; def->donor = s->donor;
    def->clip = s->phase->clips[0]; def->attachment = NULL;
    def->visual = s->phase->visual;
    def->family = s->status == nFTCommonStatusAppeal ? 6 : s->status <= nFTCommonStatusCatchWait ? 4 : 5;
    return def;
}

static void ccPairSetStatus(GObj *g, s32 status, f32 begin, f32 speed, u32 preserve)
{
    FTStruct *fp;
    struct FTCustomPairState *s;
    FTCustomMoveClock *clock;
    ftMainSetStatus(g, status, begin, speed, preserve);
    fp = ftGetStruct(g); s = ftCustomPairState(fp); clock = ftCustomMoveGetClock(fp);
    /* CatchWait has a null native motion. It skips the engine's animation
     * setup (and ccPrepare), but must retain the donor's frozen pull socket. */
    if (s && (!clock || clock->move != &s->phase->move)) ccPairPrepare(fp, begin);
    ftMainCharBuilderFinishPairStatus(fp);
}

static void ccPairTransition(GObj *g, s32 next)
{
    FTStruct *fp = ftGetStruct(g);
    ccSyncCurrent(fp);
    ftMainCharBuilderPairTransition(fp, next);
    if (fp->player < 4 && sFTCustomPairProps[fp->player].owner == fp)
    {
        s32 i;
        for (i = 0; i < 6; i++) ccPairStopProp(&sFTCustomPairProps[fp->player].models[i]);
    }
}

static sb32 ccPairPrepare(FTStruct *fp, f32 begin)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    if (!s) return FALSE;
    fp->motion_id = s->phase->motion;
    ftMainCharBuilderInstallPairPhase(fp, s->phase, begin, DObjGetStruct(fp->fighter_gobj)->anim_speed);
    return TRUE;
}

static void ccPairCollisionApply(FTStruct *fp)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    s32 frame;
    FTCustomCollisionTrajectory *trajectory;
    if (!s || !clock) return;
    frame = (s32)clock->frame; if (frame < 0) frame = 0;
    if (s->phase->trajectory.loop_period && frame >= s->phase->trajectory.loop_start)
        frame = s->phase->trajectory.loop_start+(frame-s->phase->trajectory.loop_start)%s->phase->trajectory.loop_period;
    if (frame >= s->phase->count) frame = s->phase->count-1;
    trajectory = &sCCPairCollision[fp->player];
    trajectory->frames = &ccPairSample(fp, frame)->collision;
    trajectory->first = (s32)clock->frame < 0 ? 0 : (s32)clock->frame;
    trajectory->count = 1; trajectory->loop_start = trajectory->loop_period = 0;
    clock->trajectory = trajectory;
}

static const FTCustomAnimationClip* ccPairAnimation(FTStruct *fp, s32 *frame)
{
    const CCAnimationRecord *record = ftCustomAnimationGetPairClip(fp, frame);
    s32 time = *frame;
    return record ? ccLoadAnimation(fp, record, time, frame) : NULL;
}

static void ccPairTick(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    ftMainCharBuilderApplyPairScale(fp);
    ftMainCharBuilderUpdatePairProps(g);
}

static void ccPairReset(void)
{
    s32 p, i;
    for (p = 0; p < 4; p++)
    {
        GObj *fighter;
        struct FTCustomPairState *s = &sFTCustomPairStates[p];
        for (fighter = gGCCommonLinks[nGCCommonLinkIDFighter]; fighter; fighter = fighter->link_next)
            if (s->owner && s->is_taunt_scaled && ftGetStruct(fighter) == s->owner && s->owner->player_num == s->player_num &&
                (u32)ccBodyKind(s->owner) < 12 && s->owner->joints[4])
                s->owner->joints[4]->scale.vec.f = sFTCustomAnimationRigs[ccBodyKind(s->owner)].bones[0].scale;
        for (i = 0; i < 6; i++) ccPairStopProp(&sFTCustomPairProps[p].models[i]);
        sCCPairDonors[p] = -1; sCCPairLoaded[p] = NULL;
    }
    ftMainCharBuilderResetPairedMoves();
}

sb32 ccUsePairCallback(GObj *g, s32 mode)
{
    FTStruct *fp;
    SCCharBuilderSlot *slot;
    if (!g) return FALSE;
    fp = mode & 128 ? (FTStruct*)g : ftGetStruct(g); mode &= 127;
    if (!fp) return FALSE;
    if (mode == 2)
    {
        if (!fp->capture_gobj) return FALSE;
        return ftCustomPairState(ftGetStruct(fp->capture_gobj)) != NULL;
    }
    if (ftCustomPairState(fp)) return TRUE;
    slot = ftCustomMoveGetSlot(fp);
    if (!slot) return FALSE;
    if (mode == 1) return (u32)slot->taunt < 12 && slot->taunt != ccBodyKind(fp);
    if (mode == 3) return FALSE;
    return (u32)slot->attacks[nSCCharBuilderAttackGrab] < 12 && slot->attacks[nSCCharBuilderAttackGrab] != ccBodyKind(fp);
}
#include "../build/char_creator/runtime/paired-callbacks.inc"

const u32 ccPairLayout[] = {
    sizeof(struct FTCustomPairState), sizeof(FTCustomPairPhase), sizeof(CCPairFrame),
    __builtin_offsetof(struct FTCustomPairState, phase), __builtin_offsetof(FTCustomPairPhase, offset),
    __builtin_offsetof(FTCustomPairPhase, move), __builtin_offsetof(FTCustomPairPhase, trajectory),
    __builtin_offsetof(FTCustomPairPhase, clips), __builtin_offsetof(FTCustomPairPhase, count),
    __builtin_offsetof(FTCustomPairPhase, props), __builtin_offsetof(FTCustomPairPhase, prop_count),
    __builtin_offsetof(SCCharBuilderSlot, taunt),
    nFTCommonStatusAppeal, nFTCommonStatusCatchPull, nFTCommonStatusCatchWait
};
