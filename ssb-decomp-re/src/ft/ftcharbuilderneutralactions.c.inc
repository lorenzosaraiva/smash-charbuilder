/* Sidecar state never aliases the borrowing body's native passive/status unions. */
typedef struct FTCharBuilderNeutralState
{
    FTStruct *owner;
    s32 body, row, dk_charge, samus_charge, release_charge, charge_wait, recoil;
    sb32 release, cancel, charging, fired, boost_used, is_smash;
    GObj *boomerang;
    f32 last_update;
} FTCharBuilderNeutralState;
static FTCharBuilderNeutralState sFTCharBuilderNeutralStates[4];
static const s32 sFTCharBuilderActionDonors[6] = { nFTKindCaptain, nFTKindPurin, nFTKindDonkey, nFTKindSamus, nFTKindLink, nFTKindYoshi };

void ftMainCharBuilderResetNeutralAll(void)
{
    s32 i;
    for (i = 0; i < 4; i++)
    { sFTCharBuilderNeutralStates[i].owner = NULL; sFTCharBuilderNeutralStates[i].boomerang = NULL; }
}

void ftMainCharBuilderResetNeutral(FTStruct *fp)
{
    FTCharBuilderNeutralState *s;
    if (fp->player >= 4) return;
    s = &sFTCharBuilderNeutralStates[fp->player];
    if (s->owner == fp && s->boomerang != NULL) wpMainDestroyWeapon(s->boomerang);
    s->owner = fp; s->body = fp->fkind; s->row = -1;
    s->dk_charge = s->samus_charge = s->release_charge = s->recoil = 0;
    s->boomerang = NULL;
}

static FTCharBuilderNeutralState* ftMainCharBuilderNeutralStorage(FTStruct *fp)
{
    FTCharBuilderNeutralState *s;
    if (fp->player >= 4) return NULL;
    s = &sFTCharBuilderNeutralStates[fp->player];
    if ((s->owner != fp) || (s->body != fp->fkind)) ftMainCharBuilderResetNeutral(fp);
    return s;
}

static FTCharBuilderNeutralState* ftMainCharBuilderNeutralState(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    FTCharBuilderNeutralState *s;
    if ((clock == NULL) || (fp->player >= 4) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    s = &sFTCharBuilderNeutralStates[fp->player];
    if ((s->owner != fp) || (s->body != fp->fkind) || (s->row < 0) || (s->row >= ARRAY_COUNT(sFTCharBuilderActions)) ||
        (clock->move != &sFTCharBuilderActions[s->row].move)) return NULL;
    return s;
}

static void ftMainCharBuilderYoshiCapture(GObj*, GObj*);
static void ftMainCharBuilderActionUpdate(GObj*);
static void ftMainCharBuilderActionInterrupt(GObj*);
static void ftMainCharBuilderActionPhysics(GObj*);
static void ftMainCharBuilderActionMap(GObj*);
static void ftMainCharBuilderActionCatch(GObj*);
static void ftMainCharBuilderActionDamage(GObj*);
static void ftMainCharBuilderActionAccessory(GObj*);

static void ftMainCharBuilderStartAction(GObj *g, s32 pair, f32 frame)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralStorage(fp);
    const FTCharBuilderNeutralActionDesc *action = &sFTCharBuilderActions[pair + (fp->ga == nMPKineticsAir)];
    FTCustomMoveClock *clock;
    s32 i;
    ftMainCharBuilderStartNeutral(g, &action->move, frame);
    clock = ftCustomMoveGetClock(fp);
    clock->trajectory = &action->trajectory;
    if (pair == 12) clock->speed = (-0.16000003F) * (s->samus_charge / (f32)FTSAMUS_CHARGE_MAX) + 1.0F;
    s->row = pair + (fp->ga == nMPKineticsAir);
    s->last_update = -1;
    fp->motion_vars.flags.flag2 = 0;
    fp->proc_update = ftMainCharBuilderActionUpdate;
    fp->proc_interrupt = ftMainCharBuilderActionInterrupt;
    fp->proc_physics = ftMainCharBuilderActionPhysics;
    fp->proc_map = ftMainCharBuilderActionMap;
    fp->proc_accessory = ftMainCharBuilderActionAccessory;
    fp->proc_damage = ftMainCharBuilderActionDamage;
    for (i = 0; i < 2; i++) fp->motion_scripts[i][2].script_wait = 1.0F - frame;
    /* Native interrupted Egg Lay release reads descriptor 1 before proc_damage. */
    if (pair >= 24) fp->throw_desc = sFTCharBuilderYoshiInterruptThrows;
    if (pair >= 26 && fp->catch_gobj != NULL) ftParamSetCaptureImmuneMask(fp, FTCATCHKIND_MASK_ALL);
    if (pair == 24) ftParamSetCatchParams(fp, FTCATCHKIND_MASK_YOSHISPECIALN, ftMainCharBuilderActionCatch, ftMainCharBuilderYoshiCapture);
    if (pair == 20) fp->is_special_interrupt = TRUE;
    if (fp->ga == nMPKineticsGround) s->recoil = 0;
    ftMainUpdateMotionEventsAll(g);
    ftMainCharBuilderActionAccessory(g);
}

static void ftMainCharBuilderReleaseCharge(GObj *g, FTCharBuilderNeutralState *s, sb32 donkey)
{
    FTStruct *fp = ftGetStruct(g);
    s->release_charge = donkey ? s->dk_charge : s->samus_charge;
    s->fired = FALSE;
    ftMainCharBuilderStartAction(g, donkey ? (s->dk_charge == FTDONKEY_GIANTPUNCH_CHARGE_MAX ? 10 : 8) : 16, 0);
    if (donkey)
    {
        if (fp->ga == nMPKineticsGround) fp->physics.vel_ground.x = s->dk_charge * FTDONKEY_GIANTPUNCH_VEL_MUL;
        s->dk_charge = 0;
    }
}

static void ftMainCharBuilderActionDamage(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    if (s == NULL) return;
    if ((s->row >= 4) && (s->row < 12)) s->dk_charge = 0;
    if ((s->row >= 12) && (s->row < 18) && !s->fired) s->samus_charge = 0;
    if ((s->row >= 24) && (fp->catch_gobj != NULL))
    {
        GObj *victim = fp->catch_gobj;
        ftCommonThrownDecideFighterLoseGrip(g, victim);
        mpCommonSetFighterWaitOrFall(victim);
        fp->catch_gobj = NULL;
        ftParamSetCaptureImmuneMask(fp, FTCATCHKIND_MASK_NONE);
    }
}

static void ftMainCharBuilderActionUpdate(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    s32 pair, i;
    f32 frame;
    if (s == NULL) return;
    pair = s->row & ~1; frame = ftCustomMoveGetClock(fp)->frame;
    if ((pair == 14) && (s->last_update != frame))
    {
        if (--s->charge_wait <= 0)
        {
            s->charge_wait = FTSAMUS_CHARGE_INT;
            if (++s->samus_charge >= FTSAMUS_CHARGE_MAX)
            { s->samus_charge = FTSAMUS_CHARGE_MAX; mpCommonSetFighterWaitOrFall(g); return; }
        }
    }
    s->last_update = frame;
    if ((pair == 8) && (s->release_charge < FTDONKEY_GIANTPUNCH_CHARGE_MAX))
        for (i = 0; i < ARRAY_COUNT(fp->attack_colls); i++)
            if (fp->attack_colls[i].attack_state == nGMAttackStateNew)
                fp->attack_colls[i].damage += s->release_charge * FTDONKEY_GIANTPUNCH_CHARGE_DAMAGE_MUL;
    if (pair == 26)
    {
        if ((fp->motion_vars.flags.flag1 != 0) || (g->anim_frame <= 0))
        { ftMainCharBuilderStartAction(g, 28, 0); return; }
    }
    if ((pair == 28) && (fp->catch_gobj != NULL))
    {
        FTStruct *victim = ftGetStruct(fp->catch_gobj);
        if (fp->motion_vars.flags.flag2) { victim->status_vars.common.captureyoshi.stage = 1; fp->motion_vars.flags.flag2 = 0; }
        if (fp->motion_vars.flags.flag1)
        {
            victim->status_vars.common.captureyoshi.stage = 3;
            fp->catch_gobj = NULL; fp->motion_vars.flags.flag1 = 0;
            ftParamSetCaptureImmuneMask(fp, FTCATCHKIND_MASK_NONE);
        }
    }
    if (g->anim_frame > 0) return;
    switch (pair)
    {
    case 4: ftMainCharBuilderStartAction(g, 6, 0); return;
    case 6:
        if (s->charging && s->dk_charge < FTDONKEY_GIANTPUNCH_CHARGE_MAX) s->dk_charge++;
        if (s->cancel || s->dk_charge == FTDONKEY_GIANTPUNCH_CHARGE_MAX) break;
        if (s->release) { ftMainCharBuilderReleaseCharge(g, s, TRUE); return; }
        s->charging = TRUE; ftMainCharBuilderStartAction(g, 6, 0); return;
    case 12:
        if (fp->ga == nMPKineticsAir || s->release) ftMainCharBuilderReleaseCharge(g, s, FALSE);
        else { s->charge_wait = FTSAMUS_CHARGE_INT; ftMainCharBuilderStartAction(g, 14, 0); }
        return;
    case 14: ftMainCharBuilderStartAction(g, 14, 0); return;
    }
    mpCommonSetFighterWaitOrFall(g);
}

static void ftMainCharBuilderActionInterrupt(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    s32 pair, escape;
    if (s == NULL) return;
    pair = s->row & ~1;
    if (pair != 4 && pair != 6 && pair != 12 && pair != 14) return;
    if (fp->input.pl.button_tap & (fp->input.button_mask_a | fp->input.button_mask_b))
    {
        if (pair == 14) { ftMainCharBuilderReleaseCharge(g, s, FALSE); return; }
        s->release = TRUE;
    }
    if (pair == 6 || pair == 14)
    {
        escape = fp->ga == nMPKineticsGround ? ftCommonEscapeGetStatus(fp) : -1;
        if (escape != -1) { ftCommonEscapeSetStatus(g, escape, 0); return; }
        if (fp->input.pl.button_tap & fp->input.button_mask_z)
        {
            if (pair == 6) s->cancel = TRUE;
            else mpCommonSetFighterWaitOrFall(g);
        }
    }
}

static void ftMainCharBuilderActionPhysics(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    const FTCharBuilderNeutralActionDesc *a;
    s32 pair, frame, stick;
    f32 angle;
    if (s == NULL) return;
    pair = s->row & ~1; a = &sFTCharBuilderActions[s->row];
    if (pair == 0 || pair == 2)
    {
        if (fp->ga == nMPKineticsGround)
        {
            frame = (s32)ftCustomMoveGetClock(fp)->frame;
            if (frame > a->move.duration) frame = a->move.duration;
            fp->physics.vel_ground.x = a->travel[frame].x;
            fp->physics.vel_ground.z = -fp->lr * a->travel[frame].z;
            ftPhysicsSetGroundVelTransferAir(g);
        }
        else
        {
            if (fp->motion_vars.flags.flag1)
            {
                fp->motion_vars.flags.flag1 = 0;
                if (!s->boost_used)
                {
                    s->boost_used = TRUE; stick = ABS(fp->input.pl.stick_range.y);
                    if (stick > 50) stick = 50;
                    stick -= 10; if (stick < 0) stick = 0;
                    if (fp->input.pl.stick_range.y < 0) stick = -stick;
                    angle = F_CLC_DTOR32((stick * (pair == 0 ? 30 : 20)) / 40.0F);
                    fp->physics.vel_air.y = __sinf(angle) * 65.0F;
                    fp->physics.vel_air.x = __cosf(angle) * fp->lr * 65.0F;
                }
            }
            switch (fp->motion_vars.flags.flag2)
            {
            case 0: ftPhysicsApplyAirVelFriction(g); break;
            case 1: fp->physics.vel_air.x *= 0.92F; fp->physics.vel_air.y *= 0.92F; break;
            case 2: ftPhysicsApplyAirVelDriftFastFall(g); break;
            }
        }
    }
    else if (fp->ga == nMPKineticsAir) ftPhysicsApplyAirVelDrift(g);
    else ftPhysicsApplyGroundVelFriction(g);
}

static void ftMainCharBuilderActionSwitch(GObj *g, sb32 air)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    s32 pair;
    f32 frame;
    if (s == NULL) return;
    pair = s->row & ~1; frame = ftCustomMoveGetClock(fp)->frame;
    if (air) { mpCommonSetFighterAir(fp); ftPhysicsClampAirVelXMax(fp); }
    else mpCommonSetFighterGround(fp);
    if (pair == 14 && air) { ftMainCharBuilderReleaseCharge(g, s, FALSE); return; }
    ftMainCharBuilderStartAction(g, pair, frame);
    if (s->fired && (pair == 16 || pair == 18)) fp->motion_vars.flags.flag0 = 0;
}
static void ftMainCharBuilderActionGround(GObj *g) { ftMainCharBuilderActionSwitch(g, FALSE); }
static void ftMainCharBuilderActionAir(GObj *g) { ftMainCharBuilderActionSwitch(g, TRUE); }
static void ftMainCharBuilderActionMap(GObj *g)
{
    if (ftGetStruct(g)->ga == nMPKineticsAir) mpCommonProcFighterLanding(g, ftMainCharBuilderActionGround);
    else mpCommonProcFighterOnEdge(g, ftMainCharBuilderActionAir);
}

static void ftMainCharBuilderActionAccessory(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    const FTCharBuilderNeutralActionDesc *a;
    Vec3f pos;
    s32 pair, frame, charge;
    f32 vx, vy;
    if (s == NULL) return;
    pair = s->row & ~1;
    if (pair != 16 && pair != 18) return;
    if (!fp->motion_vars.flags.flag0) return;
    fp->motion_vars.flags.flag0 = 0;
    if (s->fired) return;
    s->fired = TRUE;
    a = &sFTCharBuilderActions[s->row]; frame = (s32)ftCustomMoveGetClock(fp)->frame;
    if (frame > a->move.duration) frame = a->move.duration;
    pos = fp->joints[nFTPartsJointTopN]->translate.vec.f;
    pos.x += fp->lr * a->spawn[frame].x; pos.y += a->spawn[frame].y; pos.z += fp->lr * a->spawn[frame].z;
    if (pair == 18)
    { if (s->boomerang == NULL) s->boomerang = wpLinkBoomerangMakeWeapon(g, &pos); }
    else
    {
        charge = s->release_charge;
        wpSamusChargeShotMakeWeapon(g, &pos, charge, TRUE);
        vx = FTSAMUS_CHARGE_RECOIL_MUL * (charge + 1) + FTSAMUS_CHARGE_RECOIL_BASE;
        if (fp->ga == nMPKineticsAir)
        {
            fp->physics.vel_air.x = -fp->lr * vx;
            vy = charge + 1 + FTSAMUS_CHARGE_RECOIL_ADD + s->recoil * -FTSAMUS_CHARGE_RECOIL_BASE;
            if (fp->physics.vel_air.y < vy) fp->physics.vel_air.y = vy;
            s->recoil++;
        }
        else fp->physics.vel_ground.x = -vx;
        s->samus_charge = 0;
    }
}

/* Weapon lifecycle hooks work after the attack clock has ended. */
sb32 ftMainCharBuilderBoomerangIsSmash(FTStruct *fp)
{
    FTCharBuilderNeutralState *s = ftMainCharBuilderNeutralState(fp);
    return s != NULL && (s->row == 18 || s->row == 19) ? s->is_smash : fp->status_vars.link.specialn.is_smash;
}
sb32 ftMainCharBuilderBoomerangClear(FTStruct *fp, GObj *weapon)
{
    FTCharBuilderNeutralState *s;
    if (fp->player >= 4) return FALSE;
    s = &sFTCharBuilderNeutralStates[fp->player];
    if (s->owner != fp || s->body != fp->fkind || s->boomerang != weapon) return FALSE;
    s->boomerang = NULL; return TRUE;
}
sb32 ftMainCharBuilderBoomerangCatch(GObj *g, GObj *weapon)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s;
    if (fp->player >= 4) return FALSE;
    s = &sFTCharBuilderNeutralStates[fp->player];
    if (s->owner != fp || s->body != fp->fkind || s->boomerang != weapon) return FALSE;
    if (fp->is_special_interrupt && ftCustomMoveGetSlot(fp) != NULL) ftMainCharBuilderStartAction(g, 22, 0);
    return TRUE;
}

static void ftMainCharBuilderYoshiVictimPhysics(GObj *g)
{
    FTStruct *victim = ftGetStruct(g), *captor;
    FTCharBuilderNeutralState *s;
    const FTCharBuilderNeutralActionDesc *a;
    Vec3f pos;
    s32 frame;
    if (victim->capture_gobj == NULL) return;
    captor = ftGetStruct(victim->capture_gobj); s = ftMainCharBuilderNeutralState(captor);
    if (s == NULL || s->row < 26)
    { ftCommonThrownDecideFighterLoseGrip(victim->capture_gobj, g); mpCommonSetFighterWaitOrFall(g); return; }
    a = &sFTCharBuilderActions[s->row]; frame = (s32)ftCustomMoveGetClock(captor)->frame;
    if (frame > a->move.duration) frame = a->move.duration;
    pos = captor->joints[nFTPartsJointTopN]->translate.vec.f;
    pos.x += captor->lr * a->anchor[frame].x; pos.y += a->anchor[frame].y; pos.z += captor->lr * a->anchor[frame].z;
    DObjGetStruct(g)->translate.vec.f = pos;
    if (victim->status_vars.common.captureyoshi.stage == 3) ftCommonYoshiEggSetStatus(g);
    else if (victim->status_vars.common.captureyoshi.stage == 1)
    {
        victim->status_vars.common.captureyoshi.stage = 2;
        victim->is_invisible = victim->is_shadow_hide = TRUE;
        ftParamSetHitStatusAll(g, nGMHitStatusIntangible);
    }
}

static void ftMainCharBuilderYoshiCapture(GObj *victim, GObj *captor)
{
    ftCommonCaptureYoshiProcCaptureWithPhysics(victim, captor, ftMainCharBuilderYoshiVictimPhysics);
    ftGetStruct(victim)->proc_map = mpCommonUpdateFighterProjectFloor;
    ftMainCharBuilderYoshiVictimPhysics(victim);
}
static void ftMainCharBuilderActionCatch(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    f32 frame;
    if (ftMainCharBuilderNeutralState(fp) == NULL) return;
    frame = ftCustomMoveGetClock(fp)->frame;
    ftMainCharBuilderStartAction(g, 26, frame);
    ftParamSetCaptureImmuneMask(fp, FTCATCHKIND_MASK_ALL);
    ftPhysicsStopVelAll(g); fp->catch_gobj = fp->search_gobj;
}

static sb32 ftMainCharBuilderTryNeutralAction(GObj *g, s32 choice)
{
    FTStruct *fp = ftGetStruct(g);
    FTCharBuilderNeutralState *s;
    s32 index = choice - nSCCharBuilderNeutralFalconPunch, pair;
    if (index < 0 || index >= 6 || fp->fkind == sFTCharBuilderActionDonors[index]) return FALSE;
    s = ftMainCharBuilderNeutralStorage(fp);
    s->release = s->cancel = s->charging = s->fired = s->boost_used = FALSE;
    switch (index)
    {
    case 0: pair = 0; break;
    case 1: pair = 2; break;
    case 2: pair = 4; s->release = s->dk_charge == FTDONKEY_GIANTPUNCH_CHARGE_MAX; break;
    case 3: pair = 12; s->release = s->samus_charge == FTSAMUS_CHARGE_MAX || fp->ga == nMPKineticsAir; break;
    case 4:
        pair = s->boomerang != NULL ? 20 : 18;
        s->is_smash = ABS(fp->input.pl.stick_range.x) >= FTLINK_BOOMERANG_SMASH_STICK_MIN && fp->hold_stick_x < FTLINK_BOOMERANG_SMASH_BUFFER;
        break;
    default: pair = 24; break;
    }
    ftMainCharBuilderStartAction(g, pair, 0);
    if (index == 5) ftParamSetCatchParams(fp, FTCATCHKIND_MASK_YOSHISPECIALN, ftMainCharBuilderActionCatch, ftMainCharBuilderYoshiCapture);
    return TRUE;
}
