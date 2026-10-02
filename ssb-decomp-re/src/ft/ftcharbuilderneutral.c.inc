/* Use only the body's animation. No foreign status functions or event pointers. */
static FTStruct *sFTCharBuilderNeutralStartingOwner;
static const s32 sFTCharBuilderNeutralStatuses[12][2] =
{
    { nFTMarioStatusSpecialN, nFTMarioStatusSpecialAirN },
    { nFTFoxStatusSpecialN, nFTFoxStatusSpecialAirN },
    { nFTDonkeyStatusSpecialNEnd, nFTDonkeyStatusSpecialAirNEnd },
    { nFTSamusStatusSpecialNEnd, nFTSamusStatusSpecialAirNEnd },
    { nFTMarioStatusSpecialN, nFTMarioStatusSpecialAirN },
    { nFTLinkStatusSpecialN, nFTLinkStatusSpecialAirN },
    { nFTYoshiStatusSpecialN, nFTYoshiStatusSpecialAirN },
    { nFTCaptainStatusSpecialN, nFTCaptainStatusSpecialAirN },
    { nFTKirbyStatusSpecialNStart, nFTKirbyStatusSpecialAirNStart },
    { nFTPikachuStatusSpecialN, nFTPikachuStatusSpecialAirN },
    { nFTPurinStatusSpecialN, nFTPurinStatusSpecialAirN },
    { nFTNessStatusSpecialN, nFTNessStatusSpecialAirN }
};

/* Fox's source firing/repeat frames and animation durations (US). */
static const ftMotionCommand sFTCharBuilderLaserGround[] =
{
    ftMotionCommandWaitAsync(25), ftMotionCommandSetFlag0(1),
    ftMotionCommandWaitAsync(29), ftMotionCommandSetFlag1(1), ftMotionCommandEnd()
};
static const ftMotionCommand sFTCharBuilderLaserAir[] =
{
    ftMotionCommandWaitAsync(15), ftMotionCommandSetFlag0(1),
    ftMotionCommandSetFlag1(1), ftMotionCommandEnd()
};
static const FTCustomMoveDefinition sFTCharBuilderLaserMoves[2] =
{
    { sFTCharBuilderLaserGround, ARRAY_COUNT(sFTCharBuilderLaserGround), 55, 0 },
    { sFTCharBuilderLaserAir, ARRAY_COUNT(sFTCharBuilderLaserAir), 45, 0 }
};

static void ftMainCharBuilderMakeLaser(GObj *fighter_gobj)
{
    FTStruct *fp = ftGetStruct(fighter_gobj);
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    Vec3f pos;
    if ((clock == NULL) ||
        ((clock->move != &sFTCharBuilderLaserMoves[0]) && (clock->move != &sFTCharBuilderLaserMoves[1])) ||
        (fp->motion_vars.flags.flag0 == 0)) return;
    fp->motion_vars.flags.flag0 = 0;
    pos = fp->joints[nFTPartsJointTopN]->translate.vec.f;
    pos.x += fp->lr * 60.0F;
    pos.y += 80.0F;
    wpFoxBlasterMakeWeapon(fighter_gobj, &pos);
    func_800269C0_275C0(nSYAudioFGMFoxSpecialN);
}

static void ftMainCharBuilderNeutralProcUpdate(GObj *fighter_gobj)
{
    if (fighter_gobj->anim_frame <= 0.0F) mpCommonSetFighterWaitOrFall(fighter_gobj);
}

static void ftMainCharBuilderNeutralProcInterrupt(GObj *fighter_gobj)
{
    FTStruct *fp = ftGetStruct(fighter_gobj);
    if ((fp->motion_vars.flags.flag1 != 0) && (fp->input.pl.button_tap & fp->input.button_mask_b))
    {
        ftMainCharBuilderTrySpecialN(fighter_gobj);
        ftParamSetMotionID(fp, nFTMotionAttackIDSpecialN);
        ftParamSetStatUpdate(fp, fp->stat_flags.halfword);
        ftParamUpdate1PGameAttackStats(fp, 0);
    }
}

sb32 ftMainCharBuilderTrySpecialN(GObj *fighter_gobj)
{
    FTStruct *fp = ftGetStruct(fighter_gobj);
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    const FTCustomMoveDefinition *move;
    s32 air, i;
    if (slot == NULL) return FALSE;
    ftMainCharBuilderClearSpecialDonor(fp);
    if ((slot->special_n != nSCCharBuilderNeutralFoxLaser) ||
        (fp->fkind == nFTKindFox)) return FALSE;
    air = (fp->ga == nMPKineticsAir);
    move = &sFTCharBuilderLaserMoves[air];
    sFTCharBuilderNeutralStartingOwner = fp;
    ftMainSetStatus(fighter_gobj, sFTCharBuilderNeutralStatuses[fp->fkind][air],
        0.0F, 1.0F, air ? FTSTATUS_PRESERVE_FASTFALL : FTSTATUS_PRESERVE_NONE);
    sFTCharBuilderNeutralStartingOwner = NULL;
    /* Frame zero of the body pose was already played by SetStatus. */
    ftCustomMoveStartClock(fp, move, 1.0F);
    for (i = 0; i < 2; i++)
    {
        fp->motion_scripts[i][2].p_script = (ftMotionCommand*)move->events;
        fp->motion_scripts[i][2].script_wait = 1.0F;
        fp->motion_scripts[i][2].script_id = 0;
    }
    fp->motion_vars.flags.flag0 = fp->motion_vars.flags.flag1 = 0;
    fp->proc_update = ftMainCharBuilderNeutralProcUpdate;
    fp->proc_interrupt = ftMainCharBuilderNeutralProcInterrupt;
    fp->proc_physics = air ? ftPhysicsApplyAirVelDrift : ftPhysicsApplyGroundVelFriction;
    fp->proc_map = air ? mpCommonProcFighterWaitOrLanding : mpCommonSetFighterFallOnEdgeBreak;
    fp->proc_accessory = ftMainCharBuilderMakeLaser;
    return TRUE;
}
