/* Borrowed Kirby copy gameplay. The recipe remains Inhale; copied choices are
 * match-owned and never occupy a body's passive union or persisted recipe. */
enum { CC_NEUTRAL_INHALE = 12 };
typedef struct CCInhaleState {
    FTStruct *owner;
    u32 generation;
    s32 choice;
    GObj *wind, *fighter;
} CCInhaleState;
static CCInhaleState sCCInhaleStates[4];
static const s32 sCCInhaleBodyChoices[12] = {2,1,8,9,3,10,11,6,12,4,7,5};

static CCInhaleState* ccInhaleState(FTStruct *fp)
{
    CCInhaleState *s;
    if (!fp || fp->player >= 4) return NULL;
    s = &sCCInhaleStates[fp->player];
    return s->owner == fp && s->generation == fp->player_num ? s : NULL;
}

s32 ccInhaleChoice(FTStruct *fp, s32 selected)
{
    CCInhaleState *s;
    if (!fp || fp->player >= 4 || (u32)ccBodyKind(fp) >= 12) return selected;
    s = &sCCInhaleStates[fp->player];
    if (selected != CC_NEUTRAL_INHALE)
    { ccInhaleVisualClear(fp); s->owner = NULL; return selected; }
    if (ccBodyKind(fp) == nFTKindKirby) return selected;
    if (s->owner != fp || s->generation != fp->player_num)
    { s->owner = fp; s->generation = fp->player_num; s->choice = CC_NEUTRAL_INHALE; s->wind = NULL; s->fighter = fp->fighter_gobj; }
    s->fighter = fp->fighter_gobj;
    return s->choice;
}

static void ccInhaleReset(void)
{
    s32 i;
    for (i=0;i<4;i++)
    { if (sCCInhaleStates[i].owner) ccInhaleVisualClear(sCCInhaleStates[i].owner); sCCInhaleStates[i].owner = NULL; }
}

static void ccInhaleLoseCopy(FTStruct *fp)
{
    CCInhaleState *s = ccInhaleState(fp);
    if (!s || s->choice == CC_NEUTRAL_INHALE) return;
    s->choice = CC_NEUTRAL_INHALE;
    if (efManagerLoseKirbyStarMakeEffect(fp->fighter_gobj)) gCCVisualEffects++;
    ftMainCharBuilderResetNeutral(fp);
    func_800269C0_275C0(nSYAudioFGMKirbySpecialNLoseCopy);
}

static sb32 ccInhaleUseCallback(FTStruct *fp)
{
    /* A foreign Kirby execution context must not fall through to native
     * copy-loss code, even when it belongs to Stone/Cutter rather than Inhale. */
    return (u32)ccBodyKind(fp) < 12 && ccBodyKind(fp) != nFTKindKirby &&
        (ccSpecialDonor(fp) == nFTKindKirby || ccInhaleState(fp) != NULL);
}

static void ccInhaleDamageCheck(FTStruct *fp)
{
    CCInhaleState *s = ccInhaleState(fp);
    if (s && s->choice != CC_NEUTRAL_INHALE &&
        syUtilsRandFloat() < FTKIRBY_COPYDAMAGE_LOSECOPY_RANDOM) ccInhaleLoseCopy(fp);
}

static __attribute__((noinline)) void ccInhaleStatusChanging(FTStruct *fp, s32 next)
{
    CCInhaleState *s = ccInhaleState(fp);
    if (!s) return;
    if (!((next >= nFTKirbyStatusSpecialNStart && next <= nFTKirbyStatusSpecialNCopy) ||
          (next >= nFTKirbyStatusSpecialAirNStart && next <= nFTKirbyStatusSpecialAirNCopy)))
        ccInhaleVisualClear(fp);
    /* Status setup may preserve native attachments between inhale phases.
     * Our wind lifetime follows the next actual phase on its visual tick. */
    if (next <= nFTCommonStatusRebirthWait)
    { ccInhaleVisualClear(fp); s->choice = CC_NEUTRAL_INHALE; s->owner = NULL; }
    else if (next == nFTCommonStatusAppeal) ccInhaleLoseCopy(fp);
}

static s32 ccInhaleCaptureChoice(FTStruct *victim)
{
    SCCharBuilderSlot *slot;
    s32 body = ccBodyKind(victim), choice;
    if ((u32)body >= 12) return CC_NEUTRAL_INHALE;
    ccSyncCurrent(victim);
    slot = ftCustomMoveGetSlot(victim);
    if (slot && slot->special_n != 0 &&
        !(body == nFTKindKirby && slot->special_n == CC_NEUTRAL_INHALE))
    { choice = slot->special_n; return (u32)(choice-1) < 12 ? choice : CC_NEUTRAL_INHALE; }
    if (body == nFTKindKirby)
    {
        body = victim->passive_vars.kirby.copy_id;
        if ((u32)body >= 12) return CC_NEUTRAL_INHALE;
    }
    return sCCInhaleBodyChoices[body];
}

static void ccInhaleCopy(FTStruct *fp)
{
    CCInhaleState *s = ccInhaleState(fp);
    if (!s || !fp->motion_vars.flags.flag1) return;
    fp->motion_vars.flags.flag1 = 0;
    s->choice = (u32)(fp->status_vars.kirby.specialn.copy_id-1) < 12 ?
        fp->status_vars.kirby.specialn.copy_id : CC_NEUTRAL_INHALE;
    ftMainCharBuilderResetNeutral(fp);
    if (fp->catch_gobj) ccInhaleLoseCopy(ftGetStruct(fp->catch_gobj));
    func_800269C0_275C0(nSYAudioFGMKirbySpecialNCopyThrow);
}

const u32 ccInhaleLayout[] = {
    sizeof(CCInhaleState), __builtin_offsetof(CCInhaleState,choice),
    __builtin_offsetof(FTStruct,status_vars.kirby.specialn.copy_id),
    __builtin_offsetof(FTStruct,passive_vars.kirby.copy_id),
    nFTKirbyStatusSpecialNStart,nFTKirbyStatusSpecialNLoop,nFTKirbyStatusSpecialNWait,
    nFTKirbyStatusSpecialNCatch,nFTKirbyStatusSpecialNEat,nFTKirbyStatusSpecialNThrow,nFTKirbyStatusSpecialNCopy,
    nFTKirbyStatusSpecialAirNStart,nFTKirbyStatusSpecialAirNLoop,nFTKirbyStatusSpecialAirNWait,
    nFTCommonStatusCaptureKirby,nFTCommonStatusCaptureWaitKirby,nFTCommonStatusThrownKirbyStar,nFTCommonStatusThrownCopyStar,
    __builtin_offsetof(FTStruct,input.pl.button_hold),__builtin_offsetof(FTStruct,input.button_mask_a)
};
const u32 ccInhaleReleaseLayout[] = {
    __builtin_offsetof(FTStruct,input.pl.button_tap),
    __builtin_offsetof(FTStruct,input.button_mask_l),
    nFTKirbyStatusSpecialNThrow,nFTKirbyStatusSpecialAirNThrow
};
