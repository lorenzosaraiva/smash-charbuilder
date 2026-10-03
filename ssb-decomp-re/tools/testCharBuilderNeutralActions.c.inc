static void testActionTick(GObj *g)
{
    s32 i;
    g->anim_frame = ftCustomMoveAdvanceClock(g->fp, -1);
    ftMainUpdateMotionEventsAll(g);
    g->fp->proc_accessory(g);
    g->fp->proc_update(g);
    if (ftCustomMoveGetClock(g->fp) != NULL) g->fp->proc_physics(g);
    ftCustomCollisionApply(g->fp);
    for (i = 0; i < 4; i++) if (g->fp->attack_colls[i].attack_state == nGMAttackStateNew)
        g->fp->attack_colls[i].attack_state = nGMAttackStateInterpolate;
}
static s32 testCharBuilderNeutralActions(void)
{
    FTStruct fp = {0}, victim = {0};
    FTTestAttributes attr = {0};
    DObj root = {0}, victim_root = {0};
    GObj g = {0, &fp, &root}, v = {0, &victim, &victim_root};
    FTCharBuilderNeutralState *s;
    SCCharBuilderSlot *slot;
    const FTCustomCollisionFrame *frame;
    s32 body, air, player, index, tick, aid, count, before;
    fp.attr = &attr; fp.joints[0] = &root; fp.lr = 1;
    fp.input.button_mask_b = 2; fp.input.button_mask_a = 1; fp.input.button_mask_z = 4;
    gSCManagerSceneData.scene_curr = nSCKindVSBattle; sTestThrowMode = FALSE;
    for (index = 0; index < 6; index++) for (body = 0; body < 12; body++) for (air = 0; air < 2; air++) for (player = 0; player < 4; player++)
    {
        slot = &gSCManagerCharBuilderSlots[player]; fp.player = player;
        fp.fkind = slot->body = body; fp.pkind = player & 1 ? nFTPlayerKindCom : nFTPlayerKindMan;
        fp.ga = air; fp.input.pl.button_tap = 0; attr.size = 0.5F + player;
        slot->is_enabled = TRUE; slot->special_n = nSCCharBuilderNeutralFalconPunch + index;
        gSCManagerCharBuilderPlayerSlots[player] = player;
        ftMainCharBuilderResetNeutralAll(); ftCustomMoveResetClock(&fp);
        if (body == sFTCharBuilderActionDonors[index]) { CHECK(!ftMainCharBuilderTrySpecialN(&g)); continue; }
        CHECK(ftMainCharBuilderTrySpecialN(&g)); s = ftMainCharBuilderNeutralState(&fp);
        CHECK(s != NULL && fp.fkind == body && fp.status_id == sFTCharBuilderNeutralStatuses[body][air]);
        CHECK(fp.motion_scripts[0][0].p_script == NULL && fp.motion_scripts[0][1].p_script == NULL);
        CHECK(fp.proc_physics == ftMainCharBuilderActionPhysics && fp.proc_map == ftMainCharBuilderActionMap);
        count = index == 2 ? 150 : index == 3 && !air ? 175 : 95;
        for (tick = 1; tick <= count && ftCustomMoveGetClock(&fp); tick++)
        {
            testActionTick(&g);
            if (ftCustomMoveGetClock(&fp) == NULL) break;
            frame = ftCustomCollisionGetFrame(&fp);
            CHECK(frame != NULL || sFTCharBuilderActions[s->row].trajectory.frames == NULL);
            if (index < 2)
            {
                CHECK(frame->active_mask == (index == 0 ? (tick >= 42 && tick < 47 ? 7 : 0) : (tick >= 12 && tick < 28 ? 3 : 0)));
                for (aid = 0; aid < 4; aid++) if (frame->active_mask & (1 << aid))
                {
                    CHECK(fp.attack_colls[aid].joint == &root);
                    CHECK(testNear(fp.attack_colls[aid].offset.z * attr.size, frame->centers[aid].z));
                    CHECK(fp.attack_colls[aid].damage == (index == 0 ? 24 + aid : 13));
                }
                if (air && tick == (index == 0 ? 40 : 12)) CHECK(testNear(fp.physics.vel_air.x, 65 * 0.92F));
                if (!air) CHECK(testNear(fp.physics.vel_ground.x, sFTCharBuilderActions[s->row].travel[tick].x));
            }
        }
        CHECK(ftCustomMoveGetClock(&fp) == NULL);
        if (index == 2) CHECK(s->dk_charge == FTDONKEY_GIANTPUNCH_CHARGE_MAX);
        if (index == 3 && !air) CHECK(s->samus_charge == FTSAMUS_CHARGE_MAX);
        if (index == 4)
        {
            CHECK(s->boomerang == &g && ftMainCharBuilderBoomerangClear(&fp, &g));
            CHECK(s->boomerang == NULL && !ftMainCharBuilderBoomerangClear(&fp, &g));
        }
    }
    /* Charge/store/release, damage reset and zero-frame native shot. */
    fp.player = 0; fp.fkind = nFTKindMario; fp.pkind = nFTPlayerKindMan;
    slot = &gSCManagerCharBuilderSlots[0]; slot->body = fp.fkind;
    for (index = 2; index <= 3; index++)
    {
        ftMainCharBuilderResetNeutral(&fp); fp.ga = nMPKineticsGround;
        slot->special_n = nSCCharBuilderNeutralFalconPunch + index;
        CHECK(ftMainCharBuilderTrySpecialN(&g)); s = ftMainCharBuilderNeutralState(&fp);
        for (tick = 0; tick < 65; tick++) testActionTick(&g);
        CHECK(index == 2 ? s->dk_charge > 0 : s->samus_charge > 0);
        fp.input.pl.button_tap = fp.input.button_mask_z; fp.proc_interrupt(&g); fp.input.pl.button_tap = 0;
        for (tick = 0; tick < 15 && ftCustomMoveGetClock(&fp); tick++) testActionTick(&g);
        CHECK(ftCustomMoveGetClock(&fp) == NULL);
        count = index == 2 ? s->dk_charge : s->samus_charge;
        CHECK(count > 0 && ftMainCharBuilderTrySpecialN(&g));
        if (index == 2) s->release = TRUE;
        else { s->release = TRUE; }
        before = sTestChargeShots;
        for (tick = 0; tick < 30; tick++) testActionTick(&g);
        if (index == 2)
        {
            CHECK(s->release_charge == count && s->dk_charge == 0);
            CHECK(fp.attack_colls[0].damage == 14 + count*2);
        }
        else CHECK(sTestChargeShots == before + 1 && sTestChargeLevel == count && s->samus_charge == 0);
        CHECK(ftMainCharBuilderTrySpecialN(&g));
        if (index == 2) s->dk_charge = 3; else s->samus_charge = 3;
        fp.proc_damage(&g); CHECK(index == 2 ? s->dk_charge == 0 : s->samus_charge == 0);
    }
    /* Boomerang empty/return never accesses a foreign passive union. */
    slot->special_n = nSCCharBuilderNeutralBoomerang; fp.ga = nMPKineticsGround;
    ftMainCharBuilderResetNeutral(&fp); CHECK(ftMainCharBuilderTrySpecialN(&g));
    for (tick = 0; tick < 27; tick++) testActionTick(&g);
    s = ftMainCharBuilderNeutralState(&fp); CHECK(s->boomerang == &g);
    CHECK(ftMainCharBuilderTrySpecialN(&g)); CHECK(s->row == 20 && fp.is_special_interrupt);
    CHECK(ftMainCharBuilderBoomerangCatch(&g, &g)); CHECK(s->row == 22);
    CHECK(ftMainCharBuilderBoomerangClear(&fp, &g));
    /* Yoshi capture at any body/slot, native egg handoff, damage and interruption. */
    for (body = 0; body < 12; body++) if (body != nFTKindYoshi) for (air = 0; air < 2; air++) for (player = 0; player < 4; player++)
    {
        fp.player = player; fp.fkind = body; fp.ga = air; slot = &gSCManagerCharBuilderSlots[player];
        slot->body = body; slot->special_n = nSCCharBuilderNeutralEggLay;
        ftMainCharBuilderResetNeutralAll(); CHECK(ftMainCharBuilderTrySpecialN(&g));
        for (tick = 0; tick < 18; tick++) testActionTick(&g);
        CHECK(fp.is_catchstatus && fp.proc_capture == ftMainCharBuilderYoshiCapture);
        fp.search_gobj = &v; fp.proc_catch(&g); fp.proc_capture(&v, &g);
        CHECK(fp.catch_gobj == &v && victim.capture_gobj == &g && fp.capture_immune_mask == FTCATCHKIND_MASK_ALL);
        before = sTestEggs;
        for (tick = 0; tick < 30; tick++)
        {
            testActionTick(&g);
            if (victim.capture_gobj != NULL) victim.proc_physics(&v);
        }
        CHECK(sTestEggs == before + 1 && fp.catch_gobj == NULL && victim.capture_gobj == NULL);
        CHECK(ftMainCharBuilderTrySpecialN(&g));
        for (tick = 0; tick < 18; tick++) testActionTick(&g);
        fp.search_gobj = &v; fp.proc_catch(&g); fp.proc_capture(&v, &g); fp.proc_damage(&g);
        CHECK(fp.catch_gobj == NULL && victim.capture_gobj == NULL);
    }
    ftMainCharBuilderResetNeutralAll();
    return 0;
}
