extern void gcParseMObjMatAnimJoint(MObj *mobj);

/* Donor gameplay and capture transforms; each fighter keeps its own rig. */
typedef struct FTCustomPairAnchor { Vec3f basis[3], translate; } FTCustomPairAnchor;
typedef struct FTCustomPairPhase {
    s32 donor, status, motion;
    FTCustomMoveDefinition move;
    FTCustomCollisionTrajectory trajectory;
    const FTCustomPairAnchor *anchors;
    const Vec3f *travel;
    const FTCustomAnimationClip *const *clips;
    s32 count;
    const ftMotionCommand *visual;
    FTThrowHitDesc *throws;
    const FTCustomSpecialAttachment *props;
    s32 prop_count;
} FTCustomPairPhase;
#include "ftpairedmoves.generated.inc"
#include "ftpairedgeometry.generated.inc"
static struct FTCustomPairState {
    FTStruct *owner, *victim; u32 player_num, victim_num;
    const FTCustomPairPhase *phase;
    s32 donor, kind, status;
    void (*physics)(GObj*);
} sFTCustomPairStates[4];
static FTStruct *sFTCustomPairStarting;
static struct FTCustomPairProps {
    FTStruct *owner; u32 player_num;
    GObj *models[6];
    const FTCustomPairPhase *phase;
} sFTCustomPairProps[4];
void ftMainCharBuilderResetPairedMoves(void)
{
    bzero(sFTCustomPairStates, sizeof(sFTCustomPairStates)); sFTCustomPairStarting = NULL;
    bzero(sFTCustomPairProps, sizeof(sFTCustomPairProps));
}

static const FTCustomPairPhase* ftCustomPairFind(s32 donor, s32 status)
{
    s32 i;
    if (status == nFTCommonStatusCatchWait) status = nFTCommonStatusCatchPull;
    for (i = 0; i < ARRAY_COUNT(sFTCustomPairPhases); i++)
        if ((sFTCustomPairPhases[i].donor == donor) && (sFTCustomPairPhases[i].status == status)) return &sFTCustomPairPhases[i];
    return NULL;
}

static struct FTCustomPairState* ftCustomPairState(FTStruct *fp)
{
    struct FTCustomPairState *s;
    if ((fp == NULL) || (fp->player >= 4)) return NULL;
    s = &sFTCustomPairStates[fp->player];
    if ((s->owner != fp) || (s->player_num != fp->player_num) ||
        (s->status != fp->status_id) || (s->phase == NULL) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    return s;
}

static const FTCustomPairPhase* ftMainCharBuilderPairTransition(FTStruct *fp, s32 status)
{
    struct FTCustomPairState *s;
    const FTCustomPairPhase *phase = NULL;
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    s32 donor;
    if (fp->player >= 4) return NULL;
    s = &sFTCustomPairStates[fp->player];
    if (slot != NULL)
    {
        if (status == nFTCommonStatusAppeal)
        {
            donor = slot->taunt;
            if ((donor >= 0) && (donor < 12) && (donor != fp->fkind)) phase = ftCustomPairFind(donor, status);
        }
        else if ((status >= nFTCommonStatusCatch) && (status <= nFTCommonStatusCatchWait))
        {
            donor = slot->attacks[nSCCharBuilderAttackGrab];
            if ((donor >= 0) && (donor < 12) && (donor != fp->fkind)) phase = ftCustomPairFind(donor, status);
        }
        else if ((status == nFTCommonStatusThrowF || status == nFTCommonStatusThrowB) && sFTCustomPairStarting != fp)
            phase = NULL; /* Matching body/donor throws retain their native policy. */
        else if ((sFTCustomPairStarting == fp) || (ftCustomPairState(fp) != NULL))
            phase = ftCustomPairFind(s->donor, status);
    }
    if (phase == NULL) { s->owner = NULL; return NULL; }
    if ((s->owner != fp) || (s->player_num != fp->player_num))
    { s->victim = NULL; s->owner = fp; s->player_num = fp->player_num; }
    s->phase = phase; s->donor = phase->donor; s->status = status;
    return phase;
}

static const FTCustomMoveDefinition* ftMainCharBuilderGetPairMove(FTStruct *fp)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    return s ? &s->phase->move : NULL;
}

static s32 ftMainCharBuilderPairedVisualJoint(FTStruct *fp, s32 joint)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    DObj *part;
    s32 i;
    if (joint == 127 || joint == -1) return -1;
    if (s == NULL) return ftParamGetJointID(fp, joint);
    part = ftMainCharBuilderGetSpecialVisualJoint(fp, s->donor, joint);
    for (i = 0; i < FTPARTS_JOINT_NUM_MAX; i++) if (part == fp->joints[i]) return i;
    return nFTPartsJointTopN;
}

static const FTCustomAnimationClip* ftCustomAnimationGetPairClip(FTStruct *fp, s32 *frame)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    s32 index;
    if ((s == NULL) || (clock == NULL) || (clock->move != &s->phase->move)) return NULL;
    index = (s32)clock->frame;
    if (index < 0) index = 0;
    if (s->phase->trajectory.loop_period && (index >= s->phase->trajectory.loop_start))
        index = s->phase->trajectory.loop_start + (index - s->phase->trajectory.loop_start) % s->phase->trajectory.loop_period;
    if (index >= s->phase->count) index = s->phase->count - 1;
    *frame = index % 128;
    return s->phase->clips[index / 128];
}

static void ftMainCharBuilderInstallPairPhase(FTStruct *fp, const FTCustomPairPhase *phase, f32 begin, f32 speed)
{
    FTCustomMoveClock *clock;
    s32 i;
    if (fp->status_id == nFTCommonStatusCatchWait) { begin = phase->move.duration; speed = 0; }
    ftCustomMoveStartClock(fp, &phase->move, begin); clock = ftCustomMoveGetClock(fp);
    clock->trajectory = &phase->trajectory; clock->speed = speed; clock->frame = begin - speed;
    for (i = 0; i < 2; i++)
    {
        fp->motion_scripts[i][0].p_script = NULL;
        fp->motion_scripts[i][2].p_script = (ftMotionCommand*)phase->move.events;
        fp->motion_scripts[i][1].p_script = (ftMotionCommand*)phase->visual;
        fp->motion_scripts[i][1].script_wait = fp->motion_scripts[i][2].script_wait = 1.0F - begin;
        fp->motion_scripts[i][1].script_id = fp->motion_scripts[i][2].script_id = 0;
    }
    if (phase->throws != NULL) fp->throw_desc = phase->throws;
}

/* Native captured-body pose/status queues remain native to the victim. */
s32 ftMainCharBuilderGetCaptureKind(FTStruct *victim)
{
    FTStruct *owner;
    struct FTCustomPairState *s;
    if (victim->capture_gobj == NULL) return -1;
    owner = ftGetStruct(victim->capture_gobj); s = ftCustomPairState(owner);
    return s ? s->donor : owner->fkind;
}

s32 ftMainCharBuilderGetGrabKind(FTStruct *fp)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    return s ? s->donor : fp->fkind;
}

sb32 ftMainCharBuilderPairSocket(FTStruct *fp, Vec3f *pos)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomPairAnchor *anchor;
    DObj *root;
    s32 frame;
    f32 sn, cs;
    if (s == NULL || clock == NULL) return FALSE;
    frame = (s32)clock->frame; if (frame < 0) frame = 0;
    if (s->phase->trajectory.loop_period && frame >= s->phase->trajectory.loop_start)
        frame = s->phase->trajectory.loop_start + (frame-s->phase->trajectory.loop_start)%s->phase->trajectory.loop_period;
    if (frame >= s->phase->count) frame = s->phase->count-1;
    anchor = &s->phase->anchors[frame]; root = DObjGetStruct(fp->fighter_gobj);
    sn = __sinf(root->rotate.vec.f.y); cs = __cosf(root->rotate.vec.f.y);
    pos->x = root->translate.vec.f.x + cs*anchor->translate.x + sn*anchor->translate.z;
    pos->y = root->translate.vec.f.y + anchor->translate.y;
    pos->z = root->translate.vec.f.z - sn*anchor->translate.x + cs*anchor->translate.z;
    return TRUE;
}

sb32 ftMainCharBuilderPairCaptureTransform(GObj *g, Vec3f *pos, Vec3f *rotate)
{
    FTStruct *victim = ftGetStruct(g), *owner;
    struct FTCustomPairState *s;
    FTCustomMoveClock *clock;
    const FTCustomPairAnchor *anchor;
    DObj *root, *child;
    Vec3f v, local;
    Mtx44f matrix;
    const f32 *basis;
    f32 sn, cs, y;
    s32 index, axis;
    if (victim->capture_gobj == NULL) return FALSE;
    owner = ftGetStruct(victim->capture_gobj); s = ftCustomPairState(owner);
    if ((s == NULL) || (owner->catch_gobj != g)) return FALSE;
    if (s->victim == NULL) { s->victim = victim; s->victim_num = victim->player_num; }
    if ((s->victim != victim) || (s->victim_num != victim->player_num)) return FALSE;
    clock = ftCustomMoveGetClock(owner);
    if ((clock == NULL) || (clock->move != &s->phase->move)) return FALSE;
    index = (s32)clock->frame; if (index < 0) index = 0;
    if (s->phase->trajectory.loop_period && index >= s->phase->trajectory.loop_start)
        index = s->phase->trajectory.loop_start + (index-s->phase->trajectory.loop_start) % s->phase->trajectory.loop_period;
    if (index >= s->phase->count) index = s->phase->count - 1;
    anchor = &s->phase->anchors[index]; root = DObjGetStruct(victim->capture_gobj); child = DObjGetStruct(g)->child;
    if (child == NULL) return FALSE;
    v.x = -child->translate.vec.f.x * DObjGetStruct(g)->scale.vec.f.x;
    v.y = -child->translate.vec.f.y * DObjGetStruct(g)->scale.vec.f.y;
    v.z = -child->translate.vec.f.z * DObjGetStruct(g)->scale.vec.f.z;
    local.x = anchor->translate.x + anchor->basis[0].x*v.x + anchor->basis[0].y*v.y + anchor->basis[0].z*v.z;
    local.y = anchor->translate.y + anchor->basis[1].x*v.x + anchor->basis[1].y*v.y + anchor->basis[1].z*v.z;
    local.z = anchor->translate.z + anchor->basis[2].x*v.x + anchor->basis[2].y*v.y + anchor->basis[2].z*v.z;
    y = root->rotate.vec.f.y; sn = __sinf(y); cs = __cosf(y);
    pos->x = root->translate.vec.f.x + cs*local.x + sn*local.z;
    pos->y = root->translate.vec.f.y + local.y;
    pos->z = root->translate.vec.f.z - sn*local.x + cs*local.z;
    basis = (const f32*)anchor->basis;
    for (axis = 0; axis < 3; axis++)
    {
        matrix[axis][0] = cs*basis[axis] + sn*basis[6+axis];
        matrix[axis][1] = basis[3+axis];
        matrix[axis][2] = -sn*basis[axis] + cs*basis[6+axis];
    }
    func_ovl2_800EDA0C(matrix, rotate);
    return TRUE;
}

static void ftMainCharBuilderPairThrowUpdate(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    struct FTCustomPairState *s = ftCustomPairState(fp);
    if (s == NULL) { mpCommonSetFighterWaitOrFall(g); return; }
    if (fp->motion_vars.flags.flag1)
    { fp->motion_vars.flags.flag1 = 0; fp->lr = -fp->lr; fp->physics.vel_ground.x = -fp->physics.vel_ground.x; }
    if (fp->motion_vars.flags.flag2 && fp->catch_gobj != NULL)
    {
        ftCommonThrownProcPhysics(fp->catch_gobj);
        ftCommonThrownReleaseThrownUpdateStats(fp->catch_gobj, fp->motion_vars.flags.flag2 == 1 ? -fp->lr : fp->lr, s->kind == 2, TRUE);
        fp->motion_vars.flags.flag2 = 0; fp->catch_gobj = NULL;
        ftParamSetCaptureImmuneMask(fp, FTCATCHKIND_MASK_NONE);
    }
    if (g->anim_frame <= 0)
    {
        if (s->donor == nFTKindDonkey && fp->status_id == nFTCommonStatusThrowF && fp->catch_gobj != NULL)
        { ftCommonCaptureShoulderedSetStatus(fp->catch_gobj); ftDonkeyThrowFWaitSetStatus(g); return; }
        mpCommonSetFighterWaitOrFall(g);
    }
}

sb32 ftMainCharBuilderTryPairedThrow(GObj *g, sb32 is_throwf)
{
    FTStruct *fp = ftGetStruct(g), *victim;
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    struct FTCustomPairState *s;
    const FTThrownStatus *queued;
    s32 kind, donor, status;
    if ((slot == NULL) || (fp->catch_gobj == NULL)) return FALSE;
    kind = (is_throwf || fp->input.pl.stick_range.x * fp->lr >= 0) ? 1 : 2;
    donor = slot->attacks[nSCCharBuilderAttackGrab + kind];
    if ((donor < 0) || (donor >= 12)) return FALSE;
    if (donor == fp->fkind)
    {
        /* Native DK windup inherits its grab interrupt descriptor. A separately
         * selected grab must not change the carry donor's release values. */
        if (donor == nFTKindDonkey && kind == 1) fp->throw_desc = ftCustomPairFind(donor, nFTCommonStatusCatch)->throws;
        return FALSE;
    }
    victim = ftGetStruct(fp->catch_gobj);
    if ((victim->fkind < 0) || (victim->fkind >= 12)) return FALSE;
    s = &sFTCustomPairStates[fp->player];
    s->owner = fp; s->player_num = fp->player_num; s->donor = donor; s->kind = kind;
    s->victim = victim; s->victim_num = victim->player_num;
    status = (kind == 1 && donor == nFTKindKirby) ? nFTKirbyStatusThrowF : kind == 1 ? nFTCommonStatusThrowF : nFTCommonStatusThrowB;
    if (donor == nFTKindKirby && kind == 1) mpCommonSetFighterAir(fp);
    sFTCustomPairStarting = fp; ftMainSetStatus(g, status, 0, 1, FTSTATUS_PRESERVE_NONE); sFTCustomPairStarting = NULL;
    if (donor == nFTKindDonkey && kind == 1) fp->throw_desc = ftCustomPairFind(donor, nFTCommonStatusCatch)->throws;
    ftMainPlayAnimEventsAll(g);
    ftParamSetCaptureImmuneMask(fp, FTCATCHKIND_MASK_ALL);
    fp->motion_vars.flags.flag1 = fp->motion_vars.flags.flag2 = 0;
    queued = &sFTCustomPairVictimStatuses[donor][victim->fkind][kind - 1];
    if (queued->status1 != -1) ftCommonThrownSetStatusQueue(fp->catch_gobj, queued->status1, queued->status2);
    else ftCommonThrownSetStatusImmediate(fp->catch_gobj, queued->status2);
    if (donor == nFTKindKirby && kind == 1) { fp->is_ignore_dead = victim->is_ignore_dead = TRUE; }
    return TRUE;
}

FTAttributes* ftMainCharBuilderPairAttributes(FTStruct *fp)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    FTData *data;
    if (s == NULL) return fp->attr;
    data = dFTManagerDataFiles[s->donor];
    if ((data->p_file_main == NULL) || (*data->p_file_main == NULL)) return fp->attr;
    return lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);
}

static void ftMainCharBuilderPairPhysics(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    struct FTCustomPairState *s = ftCustomPairState(fp);
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    Vec3f travel;
    FTAttributes *saved;
    s32 index;
    if ((s == NULL) || (clock == NULL)) return;
    index = (s32)clock->frame; if (index < 0) index = 0;
    if (index >= s->phase->count) index = s->phase->count - 1;
    if (s->phase->travel != NULL) travel = s->phase->travel[index];
    else travel.x = travel.y = travel.z = 0.0F;
    if (s->physics == ftPhysicsApplyAirVelTransNAll || s->physics == ftPhysicsApplyGroundFrictionOrTransN ||
        (s->physics == ftKirbyThrowFLandingProcPhysics && fp->ga == nMPKineticsAir))
    {
        if (fp->ga == nMPKineticsGround)
        {
            /* None of these phases flags native ground TransN movement. */
            saved = fp->attr; fp->attr = ftMainCharBuilderPairAttributes(fp);
            ftPhysicsApplyGroundVelFriction(g); fp->attr = saved;
        }
        else { fp->physics.vel_air.x = fp->lr * travel.x; fp->physics.vel_air.y = travel.y; fp->physics.vel_air.z = fp->lr * travel.z; }
    }
    else if (s->physics != NULL)
    {
        /* Pure physics callbacks only: restore native attributes before map,
         * status changes, collisions or hurtbox queries can run. */
        saved = fp->attr; fp->attr = ftMainCharBuilderPairAttributes(fp); s->physics(g); fp->attr = saved;
    }
}

static void ftMainCharBuilderFinishPairStatus(FTStruct *fp)
{
    struct FTCustomPairState *s = ftCustomPairState(fp);
    if (s == NULL) return;
    s->physics = fp->proc_physics; fp->proc_physics = ftMainCharBuilderPairPhysics;
    if (fp->proc_update == ftCommonThrowProcUpdate) fp->proc_update = ftMainCharBuilderPairThrowUpdate;
}

static void ftMainCharBuilderUpdatePairProps(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    struct FTCustomPairState *pair = ftCustomPairState(fp);
    struct FTCustomPairProps *state;
    const FTCustomPairPhase *phase = pair ? pair->phase : NULL;
    const FTCustomSpecialAttachment *prop;
    const FTCustomSpecialAttachmentFrame *sample;
    FTData *data;
    FTAttributes *attr;
    FTModelPart *part;
    Gfx *dl, *prefix;
    DObj *dobj;
    Vec3f pos;
    MObj *mobj;
    s32 i, frame;
    if (fp->player >= 4) return;
    state = &sFTCustomPairProps[fp->player];
    if (state->owner != fp || state->player_num != fp->player_num)
    { bzero(state, sizeof(*state)); state->owner = fp; state->player_num = fp->player_num; }
    for (i = 0; i < 6; i++)
    {
        state->models[i] = ftCustomAnimationFindLiveEffect(state->models[i], g);
        if (phase != state->phase || phase == NULL || i >= phase->prop_count) ftCustomAnimationStopProp(&state->models[i]);
    }
    state->phase = phase;
    if (phase == NULL || phase->prop_count == 0) return;
    frame = (s32)ftCustomMoveGetClock(fp)->frame;
    if (frame < 0) frame = 0;
    if (phase->trajectory.loop_period && frame >= phase->trajectory.loop_start)
        frame = phase->trajectory.loop_start + (frame-phase->trajectory.loop_start) % phase->trajectory.loop_period;
    if (frame >= phase->count) frame = phase->count-1;
    data = dFTManagerDataFiles[phase->donor];
    if (!data->p_file_main || !*data->p_file_main) return;
    attr = lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);
    for (i = 0; i < phase->prop_count; i++)
    {
        prop = &phase->props[i]; sample = &prop->frames[frame];
        if (!sample->active) { ftCustomAnimationStopProp(&state->models[i]); continue; }
        part = NULL; prefix = NULL;
        if (prop->part >= 0)
        {
            part = &attr->modelparts_container->modelparts_desc[prop->joint-4]->modelparts[prop->part][0];
            dl = part->dl;
            if ((part->flags & 15) == 1) { prefix = ((Gfx**)dl)[0]; dl = ((Gfx**)dl)[1]; }
        }
        else
        {
            dl = attr->commonparts_container->commonparts[0].dobjdesc[prop->joint-4].dl;
            if ((attr->commonparts_container->commonparts[0].flags & 15) == 1) { prefix = ((Gfx**)dl)[0]; dl = ((Gfx**)dl)[1]; }
        }
        if (state->models[i] == NULL)
        {
            state->models[i] = ftCustomAnimationMakeProp(g, dl);
            if (state->models[i] == NULL) continue;
            dobj = DObjGetStruct(state->models[i]); dobj->user_data.p = prefix;
            if (part != NULL) lbCommonAddMObjForFighterPartsDObj(dobj, part->mobjsubs, part->costume_matanim_joints, part->main_matanim_joints, 0);
            else lbCommonAddMObjForFighterPartsDObj(dobj,
                attr->commonparts_container->commonparts[0].p_mobjsubs ? attr->commonparts_container->commonparts[0].p_mobjsubs[prop->joint-4] : NULL,
                attr->commonparts_container->commonparts[0].p_costume_matanim_joints ? attr->commonparts_container->commonparts[0].p_costume_matanim_joints[prop->joint-4] : NULL, NULL, 0);
        }
        dobj = DObjGetStruct(state->models[i]); pos = DObjGetStruct(g)->translate.vec.f;
        pos.x += sample->translate.z * fp->lr; pos.y += sample->translate.y; pos.z -= sample->translate.x * fp->lr;
        dobj->translate.vec.f = pos; dobj->scale.vec.f = sample->scale;
        dobj->rotate.vec.f = ftCustomAnimationToEuler(ftCustomAnimationMultiply(
            ftCustomAnimationFromEuler(0, fp->lr * F_CST_DTOR32(90.0F), 0),
            ftCustomAnimationFromEuler(sample->rotate.x, sample->rotate.y, sample->rotate.z)));
        for (mobj = dobj->mobj; mobj != NULL; mobj = mobj->next)
        { gcParseMObjMatAnimJoint(mobj); gcPlayMObjMatAnim(mobj); }
    }
}
