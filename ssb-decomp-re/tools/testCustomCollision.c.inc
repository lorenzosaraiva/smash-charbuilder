/* Exercise the actual runtime collision layer independently of body posing. */
static sb32 collisionNear(f32 a, f32 b)
{
    return ((a - b) < 0.001F) && ((a - b) > -0.001F);
}

static s32 testFalconUAirCollision(void)
{
    FTStruct fp = { 0 };
    DObj root = { 0 }, limb = { 0 };
    FTTestAttributes attr = { 0 };
    const FTCustomMoveDefinition *move;
    const FTCustomCollisionFrame *frame;
    s32 body, tick, aid;
    gSCManagerSceneData.scene_curr = nSCKind1PTrainingMode;
    fp.player = 0; fp.pkind = nFTPlayerKindCom; fp.attr = &attr;
    fp.motion_id = nFTCommonMotionAttackAirHi;
    for (aid = 0; aid < ARRAY_COUNT(fp.joints); aid++) fp.joints[aid] = &limb;
    fp.joints[nFTPartsJointTopN] = &root;
    gSCManagerCharBuilderPlayerSlots[0] = 0;
    gSCManagerCharBuilderSlots[0].is_enabled = TRUE;
    gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackUAir] = nFTKindCaptain;
    for (body = 0; body < 12; body++)
    {
        fp.fkind = body; gSCManagerCharBuilderSlots[0].body = body;
        /* The requested Kirby case uses its real size; others exercise scale independence. */
        attr.size = (body == nFTKindKirby) ? 0.91F : 1.25F;
        move = ftCustomMoveGetDefinition(&fp);
        ftCustomMoveStartClock(&fp, move, 0);
        if (body == nFTKindCaptain)
        {
            CHECK(move == NULL && ftCustomCollisionGetFrame(&fp) == NULL); continue;
        }
        CHECK(move == &sFTCustomMoves[nFTKindCaptain][22] && move->duration == 34);
        for (tick = 0; tick <= move->duration; tick++)
        {
            ftCustomMoveAdvanceClock(&fp, -1);
            frame = ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindCaptain][22], tick);
            CHECK(ftCustomCollisionGetFrame(&fp) == frame);
            CHECK(frame->active_mask == ((tick >= 5 && tick < 14) ? 3 : 0));
            CHECK(ftCustomAnimationGetFrame(&fp) == NULL);
            limb.translate.vec.f.y = 1000 + tick * 50;
            for (aid = 0; aid < 4; aid++)
            {
                fp.attack_colls[aid] = (FTAttackColl){ 0 };
                fp.attack_colls[aid].attack_state = (frame->active_mask & (1 << aid)) ? nGMAttackStateInterpolate : nGMAttackStateOff;
                fp.attack_colls[aid].joint = &limb;
                fp.attack_colls[aid].size = aid == 0 ? 110 : 130;
                fp.attack_colls[aid].damage = 16;
                fp.attack_colls[aid].group_id = 0;
                fp.attack_colls[aid].pos_prev.x = 42;
            }
            ftCustomCollisionApply(&fp);
            ftCustomCollisionApply(&fp); /* Hitlag/paused processing keeps the same sample. */
            CHECK(ftCustomCollisionGetFrame(&fp) == frame);
            for (aid = 0; aid < 2; aid++)
            {
                CHECK(fp.attack_colls[aid].size == (aid == 0 ? 110 : 130));
                CHECK(fp.attack_colls[aid].damage == 16 && fp.attack_colls[aid].group_id == 0);
                CHECK(fp.attack_colls[aid].pos_prev.x == 42);
                if (frame->active_mask & (1 << aid))
                {
                    CHECK(fp.attack_colls[aid].joint == &root && !fp.attack_colls[aid].is_scale_pos);
                    CHECK(collisionNear(fp.attack_colls[aid].offset.x * attr.size, frame->centers[aid].x));
                    CHECK(collisionNear(fp.attack_colls[aid].offset.y * attr.size, frame->centers[aid].y));
                    CHECK(collisionNear(fp.attack_colls[aid].offset.z * attr.size, frame->centers[aid].z));
                }
                else CHECK(fp.attack_colls[aid].joint == &limb);
            }
        }
        ftCustomMoveStartClock(&fp, move, 10);
        ftCustomMoveAdvanceClock(&fp, -1);
        CHECK(ftCustomCollisionGetFrame(&fp) == ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindCaptain][22], 10));
        /* Landing switches to donor landing duration, without aerial trajectory leakage. */
        fp.motion_id = nFTCommonMotionLandingAirNull;
        CHECK(ftCustomCollisionGetFrame(&fp) == NULL);
        move = ftCustomMoveGetDefinition(&fp);
        CHECK(move == &sFTCustomMoves[nFTKindCaptain][27]);
        ftCustomMoveStartClock(&fp, move, 0);
        CHECK(ftCustomCollisionGetFrame(&fp) == NULL);
        fp.motion_id = nFTCommonMotionAttackAirHi;
    }
    return 0;
}

static s32 testCustomCollision(void)
{
    FTStruct players[4] = { 0 }, preview;
    DObj roots[4] = { 0 }, feet[4] = { 0 };
    FTTestAttributes attributes[4] = { 0 };
    const FTCustomCollisionFrame *frame;
    const FTCustomMoveDefinition *move;
    FTAttackColl before;
    s32 player, body, variant, tick, aid, state, pilot;
    const s32 donors[4] = { nFTKindKirby, nFTKindCaptain, nFTKindFox, nFTKindDonkey };
    const s32 indices[4] = { 9, 23, 5, 14 };
    const f32 sizes[4] = { 0.91F, 1.25F, 0.5F, 2.0F };

    CHECK(sizeof(FTCustomCollisionFrame) == 52);
    gSCManagerSceneData.scene_curr = nSCKind1PTrainingMode;
    for (player = 0; player < 4; player++)
    {
        FTStruct *fp = &players[player];
        fp->player = player; fp->pkind = nFTPlayerKindCom;
        fp->attr = &attributes[player]; fp->attr->size = sizes[player];
        for (aid = 0; aid < ARRAY_COUNT(fp->joints); aid++) fp->joints[aid] = &feet[player];
        fp->joints[nFTPartsJointTopN] = &roots[player];
        gSCManagerCharBuilderPlayerSlots[player] = player;
        gSCManagerCharBuilderSlots[player].is_enabled = TRUE;
    }
    for (body = 0; body < 12; body++)
    {
        FTStruct *fp = &players[0];
        fp->fkind = body; gSCManagerCharBuilderSlots[0].body = body;
        for (variant = 8; variant <= 10; variant++)
        {
            fp->motion_id = sFTCustomMotionIDs[variant];
            gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackUTilt] = nFTKindKirby;
            move = ftCustomMoveGetDefinition(fp);
            if (body == nFTKindKirby)
            {
                CHECK(move == NULL); ftCustomMoveStartClock(fp, move, 0);
                CHECK(ftCustomCollisionGetFrame(fp) == NULL); continue;
            }
            CHECK(move == &sFTCustomMoves[nFTKindKirby][variant] && move->duration == 18);
            ftCustomMoveStartClock(fp, move, 0);
            for (tick = 0; tick <= move->duration; tick++)
            {
                ftCustomMoveAdvanceClock(fp, -1);
                frame = ftCustomCollisionGetFrame(fp);
                CHECK(frame == ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindKirby][9], tick));
                CHECK(frame->active_mask == ((tick >= 4 && tick < 12) ? 3 : 0));
                /* Repeated reads model paused/hitlag frames; none advances time. */
                CHECK(ftCustomCollisionGetFrame(fp) == frame);
                CHECK(ftCustomAnimationGetFrame(fp) == NULL);
                for (state = nGMAttackStateOff; state <= nGMAttackStateInterpolate; state++)
                {
                    for (aid = 0; aid < 4; aid++)
                    {
                        fp->attack_colls[aid] = (FTAttackColl){ 0 };
                        fp->attack_colls[aid].attack_state = state;
                        fp->attack_colls[aid].joint = &feet[0];
                        fp->attack_colls[aid].joint_id = 28;
                        fp->attack_colls[aid].offset = (Vec3f){ 123, 456, 789 };
                        fp->attack_colls[aid].size = 150;
                        fp->attack_colls[aid].damage = 14;
                        fp->attack_colls[aid].group_id = 1;
                        fp->attack_colls[aid].pos_curr = (Vec3f){ 7, 8, 9 };
                        fp->attack_colls[aid].pos_prev = (Vec3f){ 4, 5, 6 };
                    }
                    /* Deliberately move DK's foot; donor centers must not change. */
                    feet[0].translate.vec.f.y = tick * 1000;
                    feet[0].rotate.vec.f.z = tick;
                    before = fp->attack_colls[0]; ftCustomCollisionApply(fp);
                    for (aid = 0; aid < 4; aid++)
                    {
                        FTAttackColl *attack = &fp->attack_colls[aid];
                        CHECK(attack->attack_state == state && attack->size == 150);
                        CHECK(attack->damage == 14 && attack->group_id == 1);
                        CHECK(attack->pos_curr.x == 7 && attack->pos_curr.y == 8 && attack->pos_curr.z == 9);
                        CHECK(attack->pos_prev.x == 4 && attack->pos_prev.y == 5 && attack->pos_prev.z == 6);
                        if (state != nGMAttackStateOff && (frame->active_mask & (1 << aid)))
                        {
                            CHECK(attack->joint == &roots[0] && attack->joint_id == nFTPartsJointTopN);
                            CHECK(collisionNear(attack->offset.x * fp->attr->size, frame->centers[aid].x));
                            CHECK(collisionNear(attack->offset.y * fp->attr->size, frame->centers[aid].y));
                            CHECK(collisionNear(attack->offset.z * fp->attr->size, frame->centers[aid].z));
                            CHECK(!attack->is_scale_pos);
                        }
                        else CHECK(attack->joint == &feet[0] && attack->offset.x == before.offset.x);
                    }
                    CHECK(ftCustomCollisionGetFrame(fp) == frame);
                }
            }
        }
        /* The three earlier pilot trajectories now work on every foreign body. */
        for (pilot = 1; pilot < 4; pilot++)
        {
            for (aid = 0; aid < SCCHARBUILDER_ATTACKS_COUNT; aid++)
                gSCManagerCharBuilderSlots[0].attacks[aid] = donors[pilot];
            fp->motion_id = sFTCustomMotionIDs[indices[pilot]];
            move = ftCustomMoveGetDefinition(fp); ftCustomMoveStartClock(fp, move, 4);
            ftCustomMoveAdvanceClock(fp, 0);
            if (body == donors[pilot]) CHECK(ftCustomCollisionGetFrame(fp) == NULL);
            else CHECK(ftCustomCollisionGetFrame(fp) != NULL);
        }
    }
    /* Four independent players, sizes and nonzero starts. */
    for (player = 0; player < 4; player++)
    {
        FTStruct *fp = &players[player];
        fp->fkind = nFTKindDonkey; fp->motion_id = nFTCommonMotionAttackHi3;
        gSCManagerCharBuilderSlots[player].body = fp->fkind;
        gSCManagerCharBuilderSlots[player].attacks[nSCCharBuilderAttackUTilt] = nFTKindKirby;
        ftCustomMoveStartClock(fp, ftCustomMoveGetDefinition(fp), 4 + player);
        ftCustomMoveAdvanceClock(fp, 0);
        fp->attack_colls[0].attack_state = nGMAttackStateNew;
        ftCustomCollisionApply(fp);
        frame = ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindKirby][9], 4 + player);
        CHECK(ftCustomCollisionGetFrame(fp) == frame);
        CHECK(collisionNear(fp->attack_colls[0].offset.y * fp->attr->size, frame->centers[0].y));
    }
    preview = players[0]; ftCustomMoveResetClock(&preview);
    CHECK(ftCustomCollisionGetFrame(&preview) == NULL);
    CHECK(ftCustomCollisionGetFrame(&players[0]) == ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindKirby][9], 4));
    /* Shared preset, independent clock. */
    gSCManagerCharBuilderPlayerSlots[1] = 0;
    CHECK(ftCustomCollisionGetFrame(&players[1]) == ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindKirby][9], 5));
    players[0].status_id++; CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL); players[0].status_id--;
    players[0].motion_id++; CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL); players[0].motion_id--;
    players[0].pkind = nFTPlayerKindDemo; CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL);
    players[0].pkind = nFTPlayerKindMan;
    gSCManagerSceneData.scene_curr = nSCKindTitle; CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL);
    gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    gSCManagerCharBuilderPlayerSlots[0] = -1; CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL);
    gSCManagerCharBuilderPlayerSlots[0] = 0;
    players[0].fkind = nFTKindFox; CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL);
    players[0].fkind = nFTKindDonkey;
    before = players[0].attack_colls[0]; players[0].attr->size = 0;
    ftCustomCollisionApply(&players[0]); CHECK(players[0].attack_colls[0].offset.y == before.offset.y);
    players[0].attr->size = 1.25F; players[0].joints[0] = NULL;
    ftCustomCollisionApply(&players[0]); CHECK(players[0].attack_colls[0].offset.y == before.offset.y);
    ftCustomMoveResetClock(&players[0]); CHECK(ftCustomCollisionGetFrame(&players[0]) == NULL);
    CHECK(ftCustomCollisionGetFrame(&players[1]) == ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindKirby][9], 5));
    return testFalconUAirCollision();
}

/* All donor definitions, every foreign body, all samples and repeated loops. */
static s32 testFullCollisionRoster(void)
{
    FTStruct fp={0};DObj root={0},limb={0};FTTestAttributes attr={0};
    const FTCustomMoveDefinition *move;const FTCustomCollisionTrajectory *trajectory;
    const FTCustomCollisionFrame *frame;FTAttackColl before;
    s32 body,donor,variant,tick,aid,end,i;
    gSCManagerSceneData.scene_curr=nSCKindVSBattle;
    fp.player=0;fp.pkind=nFTPlayerKindCom;fp.attr=&attr;
    fp.motion_id=nFTCommonMotionAttack11;
    for(i=0;i<ARRAY_COUNT(fp.joints);i++)fp.joints[i]=&limb;
    fp.joints[0]=&root;gSCManagerCharBuilderPlayerSlots[0]=0;
    gSCManagerCharBuilderSlots[0].is_enabled=TRUE;
    for(body=0;body<12;body++)
    {
        fp.fkind=body;attr.size=(body%2)?0.5F:2.0F;
        gSCManagerCharBuilderSlots[0].body=body;
        for(donor=0;donor<12;donor++)
        {
            if(body==donor)continue;
            for(i=0;i<SCCHARBUILDER_ATTACKS_COUNT;i++)gSCManagerCharBuilderSlots[0].attacks[i]=donor;
            for(variant=0;variant<33;variant++)
            {
                move=&sFTCustomMoves[donor][variant];trajectory=&sFTCustomCollisionTrajectories[donor][variant];
                ftCustomMoveStartClock(&fp,move,0);
                end=(trajectory->loop_period?trajectory->loop_start+trajectory->loop_period*3:move->duration)+2;
                for(tick=0;tick<end;tick++)
                {
                    ftCustomMoveAdvanceClock(&fp,0);
                    frame=ftCustomCollisionGetFrame(&fp);
                    if(move->duration<=0){CHECK(frame==NULL);continue;}
                    CHECK(frame==ftCustomCollisionSample(trajectory,tick));
                    for(aid=0;aid<4;aid++)
                    {
                        fp.attack_colls[aid]=(FTAttackColl){0};
                        fp.attack_colls[aid].attack_state=nGMAttackStateInterpolate;
                        fp.attack_colls[aid].joint=&limb;fp.attack_colls[aid].joint_id=23;
                        fp.attack_colls[aid].offset=(Vec3f){123,456,789};
                        fp.attack_colls[aid].size=137;fp.attack_colls[aid].damage=11;fp.attack_colls[aid].group_id=3;
                        fp.attack_colls[aid].pos_prev=(Vec3f){4,5,6};fp.attack_colls[aid].pos_curr=(Vec3f){7,8,9};
                    }
                    limb.translate.vec.f.x=tick*1000;before=fp.attack_colls[0];
                    ftCustomCollisionApply(&fp);ftCustomCollisionApply(&fp);
                    CHECK(ftCustomCollisionGetFrame(&fp)==frame);
                    for(aid=0;aid<4;aid++)
                    {
                        FTAttackColl *attack=&fp.attack_colls[aid];
                        CHECK(attack->size==137 && attack->damage==11 && attack->group_id==3);
                        CHECK(attack->attack_state==nGMAttackStateInterpolate);
                        CHECK(attack->pos_prev.x==4 && attack->pos_curr.x==7);
                        if(frame && (frame->active_mask&(1<<aid)))
                        {
                            CHECK(attack->joint==&root && attack->joint_id==0 && !attack->is_scale_pos);
                            CHECK(collisionNear(attack->offset.x*attr.size,frame->centers[aid].x));
                            CHECK(collisionNear(attack->offset.y*attr.size,frame->centers[aid].y));
                            CHECK(collisionNear(attack->offset.z*attr.size,frame->centers[aid].z));
                        }
                        else CHECK(attack->joint==&limb && attack->offset.x==before.offset.x);
                    }
                    if(!trajectory->loop_period && tick>=move->duration)CHECK(!frame || !frame->active_mask);
                }
                fp.status_id++;CHECK(ftCustomCollisionGetFrame(&fp)==NULL);fp.status_id--;
                ftCustomMoveResetClock(&fp);
            }
        }
    }
    /* Luigi's source ends with a backward absolute wait: the head hit and
       clear execute together at 44. It must not leave a head hit through 60. */
    CHECK(ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindLuigi][2],3)->active_mask==1);
    CHECK(ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindLuigi][2],4)->active_mask==1);
    CHECK(ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindLuigi][2],44)->active_mask==0);
    CHECK(ftCustomCollisionSample(&sFTCustomCollisionTrajectories[nFTKindLuigi][2],59)->active_mask==0);
    /* Other clock users must not index the normal registry. */
    ftCustomMoveStartClock(&fp,&sFTCustomGrabMoves[0],0);CHECK(ftCustomCollisionGetFrame(&fp)==NULL);
    return 0;
}
