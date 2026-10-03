/* Run the actual adapter and its bounded event stream across bodies/ports. */
static void testProjectileTick(GObj *g)
{
    FTStruct *fp = g->fp;
    FTMotionScript *s = &fp->motion_scripts[0][2];
    u32 op;
    g->anim_frame = ftCustomMoveAdvanceClock(fp, -1);
    s->script_wait -= 1;
    while (s->p_script && s->script_wait <= 0)
    {
        op = *s->p_script++;
        switch (op >> 26)
        {
        case nFTMotionEventAsyncWait:
            s->script_wait = (op & 0x3FFFFFF) - ftCustomMoveGetClock(fp)->frame;
            break;
        case nFTMotionEventSetFlag0: fp->motion_vars.flags.flag0 = op & 0x3FFFFFF; break;
        default: s->p_script = NULL; break;
        }
    }
    fp->proc_accessory(g);
}

static sb32 testNear(f32 a, f32 b) { return a - b < 0.002F && b - a < 0.002F; }
static s32 testCharBuilderProjectiles(void)
{
    FTStruct players[4] = {0};
    FTTestAttributes attrs[4] = {0};
    GObj objects[4];
    DObj roots[4];
    const s32 fire[] = {16,16,21,20};
    FTStruct *fp;
    SCCharBuilderSlot *slot;
    const FTCustomMoveDefinition *move;
    const Vec3f *offset;
    s32 index, body, air, player, frame, before, calls, transition;
    sTestThrowMode = FALSE;
    gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    for (player = 0; player < 4; player++)
    {
        fp = &players[player]; objects[player].fp = fp; fp->player = player;
        fp->pkind = player & 1 ? nFTPlayerKindCom : nFTPlayerKindMan;
        fp->attr = &attrs[player]; attrs[player].size = 0.5F + player;
        fp->joints[0] = &roots[player]; fp->lr = player & 1 ? -1 : 1;
        roots[player].translate.vec.f.x = 123;
        roots[player].translate.vec.f.y = 456;
        roots[player].translate.vec.f.z = 7;
        gSCManagerCharBuilderPlayerSlots[player] = player;
    }
    for (index = 0; index < 4; index++) for (body = 0; body < 12; body++) for (air = 0; air < 2; air++)
    {
        move = &sFTCharBuilderProjectileMoves[index][air]; offset = &sFTCharBuilderProjectileOffsets[index][air];
        for (player = 0; player < 4; player++)
        {
            fp = &players[player]; slot = &gSCManagerCharBuilderSlots[player];
            fp->fkind = slot->body = body; fp->ga = air; slot->is_enabled = TRUE;
            slot->special_n = nSCCharBuilderNeutralMarioFireball + index;
            calls = sTestNeutralStatusCalls;
            if (body == sFTCharBuilderProjectileDonors[index])
            {
                CHECK(!ftMainCharBuilderTrySpecialN(&objects[player]));
                CHECK(sTestNeutralStatusCalls == calls); continue;
            }
            CHECK(ftMainCharBuilderTrySpecialN(&objects[player]));
            CHECK(sTestNeutralStatusCalls == calls + 1 && fp->fkind == body && fp->pkind == (player & 1 ? nFTPlayerKindCom : nFTPlayerKindMan));
            CHECK(fp->status_id == sFTCharBuilderNeutralStatuses[body][air]);
            CHECK(ftCustomMoveGetClock(fp)->move == move && ftCustomMoveGetClock(fp)->frame == 0);
            CHECK(fp->proc_interrupt == NULL && fp->proc_accessory == ftMainCharBuilderMakeProjectile);
        }
        if (body == sFTCharBuilderProjectileDonors[index]) continue;
        for (frame = 1; frame <= move->duration; frame++) for (player = 0; player < 4; player++)
        {
            fp = &players[player]; before = sTestProjectileShots;
            testProjectileTick(&objects[player]);
            CHECK(sTestProjectileShots == before + (frame == fire[index]));
            if (frame == fire[index])
            {
                CHECK(sTestProjectileKind == index);
                CHECK(testNear(sTestProjectilePosition.x, 123 + fp->lr * offset->x));
                CHECK(testNear(sTestProjectilePosition.y, 456 + offset->y));
                CHECK(testNear(sTestProjectilePosition.z, index == 3 ? 0 : 7 + fp->lr * offset->z));
                if (index == 2) CHECK(testNear(sTestProjectileVelocity.x, __cosf(FTPIKACHU_THUNDERJOLT_SPAWN_ANGLE) * FTPIKACHU_THUNDERJOLTVEL * fp->lr));
                if (index == 3)
                {
                    CHECK(sTestProjectileAngle == (air ? FTNESS_PKFIRE_SPARK_ANGLE_AIR : FTNESS_PKFIRE_SPARK_ANGLE_GROUND));
                    CHECK(testNear(sTestProjectileVelocity.y, __sinf(sTestProjectileAngle) * (air ? FTNESS_PKFIRE_SPARK_VEL_AIR : FTNESS_PKFIRE_SPARK_VEL_GROUND)));
                }
                fp->motion_vars.flags.flag0 = 1; fp->proc_accessory(&objects[player]);
                CHECK(sTestProjectileShots == before + 1 && fp->motion_vars.flags.flag0 == 0);
            }
            calls = sTestNeutralEnds; fp->proc_update(&objects[player]);
            CHECK(sTestNeutralEnds == calls + (frame == move->duration));
        }
    }
    fp = &players[0]; slot = &gSCManagerCharBuilderSlots[0];
    fp->fkind = slot->body = nFTKindDonkey;
    for (index = 0; index < 4; index++) for (air = 0; air < 2; air++) for (transition = 0; transition < 2; transition++)
    {
        fp->ga = air; slot->special_n = nSCCharBuilderNeutralMarioFireball + index;
        CHECK(ftMainCharBuilderTrySpecialN(&objects[0])); before = sTestProjectileShots;
        calls = transition ? fire[index] + 2 : 5;
        for (frame = 0; frame < calls; frame++) testProjectileTick(&objects[0]);
        sTestNeutralLanding = air; sTestNeutralEdge = !air;
        fp->proc_map(&objects[0]); sTestNeutralLanding = sTestNeutralEdge = FALSE;
        CHECK(fp->ga == !air && ftCustomMoveGetClock(fp)->frame == calls);
        CHECK(ftCustomMoveGetClock(fp)->move == &sFTCharBuilderProjectileMoves[index][!air]);
        for (frame = calls; frame < sFTCharBuilderProjectileMoves[index][!air].duration; frame++) testProjectileTick(&objects[0]);
        CHECK(sTestProjectileShots == before + 1);
    }
    CHECK(ftMainCharBuilderTrySpecialN(&objects[0])); before = sTestProjectileShots;
    ftCustomMoveResetClock(fp); fp->motion_vars.flags.flag0 = 1; fp->proc_accessory(&objects[0]);
    CHECK(sTestProjectileShots == before);
    sTestProjectileFailure = TRUE; CHECK(ftMainCharBuilderTrySpecialN(&objects[0]));
    for (frame = 0; frame < 30; frame++) testProjectileTick(&objects[0]);
    CHECK(sTestProjectileShots == before + 1); sTestProjectileFailure = FALSE;
    CHECK(ftMainCharBuilderTrySpecialN(&objects[0]));
    for (frame = 0; frame < 30; frame++) testProjectileTick(&objects[0]);
    CHECK(sTestProjectileShots == before + 2);
    fp->pkind = nFTPlayerKindDemo; CHECK(!ftMainCharBuilderTrySpecialN(&objects[0])); fp->pkind = nFTPlayerKindMan;
    slot->is_enabled = FALSE; CHECK(!ftMainCharBuilderTrySpecialN(&objects[0])); slot->is_enabled = TRUE;
    gSCManagerCharBuilderPlayerSlots[0] = -1; CHECK(!ftMainCharBuilderTrySpecialN(&objects[0])); gSCManagerCharBuilderPlayerSlots[0] = 0;
    slot->special_n = 255; CHECK(!ftMainCharBuilderTrySpecialN(&objects[0]));
    return 0;
}
