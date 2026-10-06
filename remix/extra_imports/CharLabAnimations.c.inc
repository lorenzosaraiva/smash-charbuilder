/* Shared donor curves are copied only at clip transitions, never per joint. */
extern void syDmaReadRom(uintptr_t, void*, size_t);
static u8 sCCAnimationCache[4][CC_ANIMATION_CACHE_BYTES] __attribute__((aligned(16)));
static const CCAnimationRecord *sCCAnimationLoaded[4];
static FTCustomAnimationClip sCCAnimationClips[4];
static u16 sCCAnimationChannels[FTPARTS_JOINT_NUM_MAX*3];
static struct { FTStruct *owner; u32 generation; s32 donor, status; f32 frame; } sCCAnimationRecovery[4];
u32 gCCAnimationLoads;

static const FTCustomAnimationClip* ccLoadAnimation(FTStruct *fp, const CCAnimationRecord *record, f32 time, s32 *frame)
{
    FTCustomAnimationClip *clip;
    u8 *cache;
    s32 i;
    if (record == NULL || fp->player >= 4 || (u32)ccBodyKind(fp) >= 12) return NULL;
    clip = &sCCAnimationClips[fp->player]; cache = sCCAnimationCache[fp->player];
    if (sCCAnimationLoaded[fp->player] != record)
    {
        if (record->size > CC_ANIMATION_CACHE_BYTES) { gFTCustomAnimationValidationFailures++; return NULL; }
        syDmaReadRom(CC_ANIMATION_ROM_START + record->offset, cache, record->size);
        for (i = 0; i < FTPARTS_JOINT_NUM_MAX*3; i++) sCCAnimationChannels[i] = i;
        clip->rig = record->rig; clip->channels = sCCAnimationChannels;
        clip->curves = (FTCustomAnimationCurve*)cache;
        clip->keys = (FTCustomAnimationKey*)(cache + record->keys);
        clip->root = (Vec3h*)(cache + record->root);
        clip->count = record->count; clip->loop_start = record->loop_start; clip->loop_period = record->loop_period;
        sCCAnimationLoaded[fp->player] = record;
        gCCAnimationLoads++;
    }
    *frame = (s32)time;
    if (*frame < 0) *frame = 0;
    if (clip->loop_period > 0 && *frame >= clip->loop_start)
        *frame = clip->loop_start + (*frame - clip->loop_start) % clip->loop_period;
    if (*frame >= clip->count) *frame = clip->count - 1;
    return clip;
}

static const FTCustomAnimationClip* ccSelectAnimation(FTStruct *fp, s32 *frame)
{
    CCSpecialClock *special = ccSpecialClock(fp);
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    s32 i, index, donor = ccRecoveryDonor(fp), motion = fp->motion_id;
    f32 time;
    if (fp->player >= 4 || (u32)ccBodyKind(fp) >= 12 || ftCustomMoveGetSlot(fp) == NULL) return NULL;
    if (donor < 0) sCCAnimationRecovery[fp->player].owner = NULL;
    if (special != NULL) { donor = special->donor; time = special->frame; }
    else if (donor >= 0)
    {
        if (sCCAnimationRecovery[fp->player].owner != fp || sCCAnimationRecovery[fp->player].generation != fp->player_num ||
            sCCAnimationRecovery[fp->player].donor != donor || sCCAnimationRecovery[fp->player].status != fp->status_id)
        {
            sCCAnimationRecovery[fp->player].owner = fp; sCCAnimationRecovery[fp->player].generation = fp->player_num;
            sCCAnimationRecovery[fp->player].donor = donor; sCCAnimationRecovery[fp->player].status = fp->status_id;
            sCCAnimationRecovery[fp->player].frame = 0.0F;
        }
        time = sCCAnimationRecovery[fp->player].frame++;
    }
    else if (clock != NULL && clock->move == &sFTCharBuilderLaserMoves[fp->ga == nMPKineticsAir])
    {
        donor = nFTKindFox; motion = fp->ga == nMPKineticsAir ? nFTFoxMotionSpecialAirN : nFTFoxMotionSpecialN;
        time = clock->frame;
    }
    else
    {
        index = ccNormalIndex(fp);
        if (index < 0) return NULL;
        return ccLoadAnimation(fp, sCCNormalAnimations[index/33][index%33], clock->frame, frame);
    }
    for (i = 0; i < ARRAY_COUNT(sCCSpecialAnimations); i++)
        if (sCCSpecialAnimations[i].donor == donor && sCCSpecialAnimations[i].motion == motion)
        {
            const CCAnimationRecord *record = sCCSpecialAnimations[i].clip;
            if (special == NULL && donor >= 0 && fp->status_id == nFTCommonStatusLandingFallSpecial && clock != NULL)
                time = clock->frame * (record->count - 1) / clock->duration;
            return ccLoadAnimation(fp, record, time, frame);
        }
    return NULL;
}

static void ccApplySpecialPose(FTStruct *fp)
{
    CCSpecialClock *special = ccSpecialClock(fp);
    DObj *root = fp->joints[4];
    if (special == NULL || root == NULL) return;
    if ((special->donor == nFTKindFox && (special->motion == nFTFoxMotionSpecialHi || special->motion == nFTFoxMotionSpecialAirHi)) ||
        (special->donor == nFTKindPikachu && (special->motion == nFTPikachuMotionSpecialHi || special->motion == nFTPikachuMotionSpecialAirHi)))
        root->rotate.vec.f.x = syUtilsArcTan2(fp->physics.vel_air.x, fp->physics.vel_air.y) * fp->lr - F_CST_DTOR32(90.0F);
    else if ((special->donor == nFTKindMario || special->donor == nFTKindLuigi) &&
             (special->motion == nFTMarioMotionSpecialHi || special->motion == nFTMarioMotionSpecialAirHi))
        root->rotate.vec.f.x -= ftMainCharBuilderGetSpecialTravelAngle(fp) * fp->lr;
}
