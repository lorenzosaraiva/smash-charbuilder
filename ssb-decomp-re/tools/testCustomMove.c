/* Host-only, freestanding 32-bit test of the actual custom layer.
 * Minimal engine objects avoid IDO-only incomplete extern-array declarations.
 * Does not exercise N64 animation, collision detection, or emulation. */
#include <ssb_types.h>
#include <macros.h>
#include <ft/ftdef.h>
#include <gm/gmdef.h>

#define _FTTYPES_H_
typedef struct GObj GObj;
struct DObj { struct { union { Vec3f f; } vec; } rotate,translate,scale; };
typedef struct DObj DObj;
typedef struct FTAttackColl {
    s32 attack_state, joint_id, damage, group_id;
    DObj *joint;
    Vec3f offset, pos_curr, pos_prev;
    f32 size;
    sb32 is_scale_pos;
} FTAttackColl;
struct FTMotionScript { ftMotionCommand *p_script; f32 script_wait; s32 script_id; };
struct FTMotionEventDefault { u32 words[1]; };
struct FTMotionEventMakeAttack { u32 words[5]; };
struct FTMotionEventSetAttackOffset { u32 words[2]; };
struct FTThrowHitDesc
{
    s32 status_id, damage, angle, knockback_scale, knockback_weight, knockback_base, element;
};
struct FTThrownStatus { s32 status1, status2; };
typedef struct FTTestAttributes
{
    f32 size;
    struct { FTThrownStatus ft_thrown[2]; } thrown_status[27];
} FTTestAttributes;
struct FTStruct
{
    s32 fkind, pkind;
    u32 player;
    s32 status_id, motion_id;
    s32 motion_attack_id;
    FTThrowHitDesc *throw_desc;
    DObj *joints[FTPARTS_JOINT_NUM_MAX];
    FTAttackColl attack_colls[4];
    FTTestAttributes *attr;
    FTMotionScript motion_scripts[2][3];
    s32 ga;
    f32 lr;
    struct { struct { s32 flag0, flag1, flag2; } flags; } motion_vars;
    struct { struct { u32 button_tap; Vec2b stick_range, stick_prev; } pl; u32 button_mask_b, button_mask_a; } input;
    struct { struct { f32 x; } vel_ground; } physics;
    struct { struct { struct { sb32 is_turn; s32 turn_tics; } throwff;
        struct { s32 throw_wait; } catchwait; } common; } status_vars;
    GObj *catch_gobj;
    GObj *capture_gobj;
    sb32 is_hitstun;
    sb32 is_ignore_dead;
    sb32 is_effect_attach;
    u8 capture_immune_mask;
    struct { u16 halfword; } stat_flags;
    void (*proc_update)(GObj*), (*proc_interrupt)(GObj*), (*proc_physics)(GObj*),
        (*proc_map)(GObj*), (*proc_accessory)(GObj*);
};
#include <sc/scdef.h>
#include <sc/sccharbuilder.h>
SCCharBuilderSlot gSCManagerCharBuilderSlots[4];
s8 gSCManagerCharBuilderPlayerSlots[4] = { 0, 1, 2, 3 };
static struct { s32 scene_curr; } gSCManagerSceneData;
#include "../src/ft/ftcustommove.c.inc"

#define CHECK(expr) do { if (!(expr)) return __LINE__; } while (0)
static s32 testCustomMove(void)
{
    FTStruct fp = { 0 }, other = { 0 };
    DObj joint;
    ftMotionCommand *script, *second;
    ftMotionCommand native[8], invalid[6];
    FTCustomMoveDefinition bad = { 0 };
    const FTCustomMoveDefinition *move;
    FTThrowHitDesc native_throw[2] = { { 52, 12, 45, 70, 0, 80, 0 }, { 55, 6, 45, 70, 0, 80, 0 } };
    s32 body, donor, i, j, cursor, count, kind;
    u32 word, opcode, saved, failures;
    gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    fp.pkind = nFTPlayerKindMan;
    for (i = 0; i < ARRAY_COUNT(fp.joints); i++) fp.joints[i] = &joint;
    for (body = 0; body < 12; body++)
    {
        fp.fkind = body;
        gSCManagerCharBuilderSlots[0].is_enabled = TRUE;
        gSCManagerCharBuilderSlots[0].body = body;
        for (donor = 0; donor < 12; donor++)
        {
            for (j = 0; j < SCCHARBUILDER_ATTACKS_COUNT; j++) gSCManagerCharBuilderSlots[0].attacks[j] = donor;
            for (i = 0; i < 33; i++)
            {
                fp.motion_id = (i < 29) ? sFTCustomMotionIDs[i] : sFTCustomBodyExtraMotionIDs[body][i - 29];
                move = ftCustomMoveGetDefinition(&fp);
                if ((body == donor) || (fp.motion_id < 0)) CHECK(move == NULL);
                else CHECK(move == &sFTCustomMoves[donor][i]);
                failures = gFTCustomMoveValidationFailures;
                script = ftCustomMoveBuildScript(&fp, &sFTCustomMoves[donor][i]);
                CHECK(script != NULL);
                CHECK(gFTCustomMoveValidationFailures == failures);
                cursor = 0;
                while (cursor < sFTCustomMoves[donor][i].word_count)
                {
                    word = script[cursor]; opcode = word >> 26;
                    count = 1;
                    if ((opcode == nFTMotionEventMakeAttackColl) || (opcode == nFTMotionEventMakeAttackCollScaled))
                    {
                        count = 5;
                        CHECK(((word >> 23) & 7) < 4);
                        CHECK(((word >> 13) & 127) < FTPARTS_JOINT_NUM_MAX);
                        CHECK(fp.joints[(word >> 13) & 127] != NULL);
                    }
                    else if (opcode == nFTMotionEventSetAttackCollOffset) count = 2;
                    else if (opcode == nFTMotionEventGoto)
                    {
                        count = 2; CHECK(script[cursor + 1] == (uintptr_t)script);
                    }
                    else CHECK(opcode == nFTMotionEventEnd || opcode == nFTMotionEventSyncWait || opcode == nFTMotionEventAsyncWait || opcode == nFTMotionEventPauseScript || opcode == nFTMotionEventClearAttackCollAll || opcode == nFTMotionEventClearAttackCollID || opcode == nFTMotionEventRefreshAttackCollID || opcode == nFTMotionEventSetAttackCollDamage || opcode == nFTMotionEventSetAttackCollSize || opcode == nFTMotionEventSetAttackCollSoundLevel || opcode == nFTMotionEventSetFlag1);
                    cursor += count;
                }
                CHECK(cursor == sFTCustomMoves[donor][i].word_count);
                CHECK((script[cursor - 1] >> 26) == nFTMotionEventEnd);
                ftCustomMoveStartClock(&fp,move,0.0F);
                if (move != NULL && move->duration > 0)
                {
                    for (cursor = 0; cursor < move->duration; cursor++)
                    {
                        /* Body animation has already ended. Donor still runs. */
                        if (!(move->flags & FTCUSTOMMOVE_FLAG_LOOP)) CHECK(ftCustomMoveAdvanceClock(&fp,-1.0F) > 0.0F);
                        else CHECK(ftCustomMoveAdvanceClock(&fp,5.0F) == 5.0F);
                        CHECK(ftCustomMoveEventFrame(&fp,&fp.motion_scripts[0][2],0.0F) == cursor);
                        CHECK(ftCustomMoveEventSpeed(&fp,&fp.motion_scripts[0][2],2.0F) == 1.0F);
                        CHECK(ftCustomMoveEventSpeed(&fp,&fp.motion_scripts[0][0],2.0F) == 2.0F);
                    }
                    if (!(move->flags & FTCUSTOMMOVE_FLAG_LOOP)) CHECK(ftCustomMoveAdvanceClock(&fp,100.0F) <= 0.0F);
                    ftCustomMoveResetClock(&fp);
                    CHECK(ftCustomMoveAdvanceClock(&fp,17.0F) == 17.0F);
                }
            }
        }
    }
    for (body = 0; body < 12; body++)
    {
        fp.fkind = body;
        gSCManagerCharBuilderSlots[0].body = body;
        for (donor = 0; donor < 12; donor++)
        {
            fp.status_id = nFTCommonStatusCatch;
            fp.motion_id = nFTCommonMotionCatch;
            gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackGrab] = donor;
            move = ftCustomMoveGetDefinition(&fp);
            CHECK(move == ((body == donor) ? NULL : &sFTCustomGrabMoves[donor]));
            failures = gFTCustomMoveValidationFailures;
            script = ftCustomMoveBuildScript(&fp, &sFTCustomGrabMoves[donor]);
            CHECK(script != NULL && gFTCustomMoveValidationFailures == failures);
            CHECK((script[0] & 0x03FFFFFF) == sFTCustomGrabTimings[donor][0]);
            CHECK(((script[1] >> 13) & 127) == sFTCustomGrabJointMap[body]);
            CHECK((script[sFTCustomGrabMoves[donor].word_count - 3] & 0x03FFFFFF) == sFTCustomGrabTimings[donor][1]);
            CHECK((script[sFTCustomGrabMoves[donor].word_count - 2] >> 26) == nFTMotionEventClearAttackCollAll);
            ftCustomMoveStartClock(&fp,move,0.0F);
            if (move != NULL)
            {
                for (cursor = 0; cursor < move->duration; cursor++) CHECK(ftCustomMoveAdvanceClock(&fp,-1.0F) > 0.0F);
                CHECK(ftCustomMoveAdvanceClock(&fp,100.0F) <= 0.0F);
            }
            ftCustomMoveResetClock(&fp);
            for (kind = 0; kind < 3; kind++)
            {
                gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackGrab + kind] = donor;
                fp.status_id = (kind == 0) ? nFTCommonStatusCatch : nFTCommonStatusThrowF;
                fp.motion_attack_id = (kind == 2) ? nFTMotionAttackIDThrowB : nFTMotionAttackIDThrowF;
                fp.throw_desc = native_throw;
                ftCustomMoveApplyThrow(&fp);
                if (body == donor) CHECK(fp.throw_desc == native_throw);
                else
                {
                    CHECK(fp.throw_desc != native_throw);
                    for (j = 0; j < 2; j++)
                    {
                        CHECK(fp.throw_desc[j].status_id == native_throw[j].status_id);
                        CHECK(fp.throw_desc[j].damage == sFTCustomThrowProperties[donor][kind][j].damage);
                        CHECK(fp.throw_desc[j].angle == sFTCustomThrowProperties[donor][kind][j].angle);
                        CHECK(fp.throw_desc[j].knockback_scale == sFTCustomThrowProperties[donor][kind][j].knockback_scale);
                        CHECK(fp.throw_desc[j].knockback_weight == sFTCustomThrowProperties[donor][kind][j].knockback_weight);
                        CHECK(fp.throw_desc[j].knockback_base == sFTCustomThrowProperties[donor][kind][j].knockback_base);
                        CHECK(fp.throw_desc[j].element == sFTCustomThrowProperties[donor][kind][j].element);
                    }
                }
            }
        }
    }
    /* Known source values, two independent players, and eligibility guards. */
    fp.fkind = nFTKindMario; gSCManagerCharBuilderSlots[0].body = nFTKindMario;
    fp.status_id = nFTCommonStatusThrowF; fp.motion_attack_id = nFTMotionAttackIDThrowF;
    gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackThrowF] = nFTKindSamus;
    fp.throw_desc = native_throw; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc[0].damage == 16 && fp.throw_desc[0].angle == 40);
    CHECK(fp.throw_desc[0].knockback_base == 90 && fp.throw_desc[0].element == 2);
    CHECK(fp.throw_desc[1].damage == 8 && native_throw[0].damage == 12);
    other = fp; other.player = 1;
    gSCManagerCharBuilderSlots[1] = gSCManagerCharBuilderSlots[0];
    gSCManagerCharBuilderSlots[1].attacks[nSCCharBuilderAttackThrowF] = nFTKindDonkey;
    other.throw_desc = native_throw; ftCustomMoveApplyThrow(&other);
    CHECK(other.throw_desc != fp.throw_desc && other.throw_desc[0].damage == 8);
    CHECK(fp.throw_desc[0].damage == 16);
    fp.pkind = nFTPlayerKindCom; fp.throw_desc = native_throw; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc != native_throw);
    fp.pkind = nFTPlayerKindDemo; fp.throw_desc = native_throw; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc == native_throw); fp.pkind = nFTPlayerKindMan;
    gSCManagerCharBuilderPlayerSlots[0] = -1; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc == native_throw); gSCManagerCharBuilderPlayerSlots[0] = 0;
    gSCManagerSceneData.scene_curr = nSCKindTitle; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc == native_throw); gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackThrowF] = 12; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc == native_throw);
    fp.status_id = nFTCommonStatusWait; fp.motion_attack_id = 0;
    gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackThrowF] = nFTKindSamus; ftCustomMoveApplyThrow(&fp);
    CHECK(fp.throw_desc == native_throw);
    fp.fkind = nFTKindMario; fp.motion_id = nFTCommonMotionAttackAirLw;
    gSCManagerCharBuilderSlots[0].body = nFTKindMario;
    gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackDAir] = nFTKindCaptain;
    CHECK(ftCustomJointResolve(&fp,nFTCustomJointKneeR) == 25);
    script = ftCustomMoveBuildScript(&fp,ftCustomMoveGetDefinition(&fp));
    CHECK((script[0] & 0x03FFFFFF) == 7);
    CHECK((script[1] >> 26) == nFTMotionEventSetFlag1 && (script[1] & 0x03FFFFFF) == 40);
    CHECK(((script[2] >> 13) & 127) == 25);
    CHECK(((script[2] >> 5) & 255) == 14);
    CHECK((script[4] >> 16) == 120);
    CHECK((script[9] >> 16) == 30);
    CHECK(sFTCustomMoves[nFTKindKirby][5].duration == 28);
    ftCustomMoveStartClock(&fp,ftCustomMoveGetDefinition(&fp),0.0F);
    CHECK(ftCustomMoveAdvanceClock(&fp,-1.0F) > 0.0F);
    other = fp;
    CHECK(ftCustomMoveGetClock(&other) == NULL);
    ftCustomMoveResetClock(&other); /* A preview sharing the player ID. */
    CHECK(ftCustomMoveGetClock(&fp) != NULL);
    CHECK(ftCustomMoveEventFrame(&fp,&fp.motion_scripts[0][2],0.0F) == 0.0F);
    /* No advance during hitlag; a shorter body pose cannot finish the move. */
    CHECK(ftCustomMoveAdvanceClock(&fp,-1.0F) == 1.0F);
    ftCustomMoveResetClock(&fp);
    saved = script[2]; other = fp; other.player = 1;
    second = ftCustomMoveBuildScript(&other,&sFTCustomMoves[nFTKindFox][23]);
    CHECK(second != script && script[2] == saved);
    fp.pkind = nFTPlayerKindCom; CHECK(ftCustomMoveGetDefinition(&fp) != NULL);
    fp.pkind = nFTPlayerKindDemo; CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    fp.pkind = nFTPlayerKindMan;
    fp.motion_scripts[0][0].p_script = native;
    CHECK(ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][0],nFTMotionEventMakeAttackColl));
    CHECK(fp.motion_scripts[0][0].p_script == native + 5);
    fp.motion_scripts[0][1].p_script = native;
    CHECK(ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][1],nFTMotionEventClearAttackCollAll));
    CHECK(!ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][2],nFTMotionEventClearAttackCollAll));
    CHECK(ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][0],nFTMotionEventSetFlag1));
    CHECK(!ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][0],nFTMotionEventSetFlag2));
    gSCManagerCharBuilderPlayerSlots[0] = -1; CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    gSCManagerCharBuilderPlayerSlots[0] = 0;
    gSCManagerSceneData.scene_curr = nSCKindTitle; CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    gSCManagerSceneData.scene_curr = nSCKind1PTrainingMode;
    CHECK(ftCustomMoveGetDefinition(&fp) != NULL);
    invalid[0] = ftMotionCommandMakeAttackCollS1(4,0,nFTCustomJointTorso,1,1,0);
    bad.events = invalid; bad.word_count = 6;
    CHECK(ftCustomMoveBuildScript(&fp,&bad)[0] == ftMotionCommandEnd());
    bad.word_count = FTCUSTOMMOVE_SCRIPT_WORDS + 1;
    CHECK(ftCustomMoveBuildScript(&fp,&bad)[0] == ftMotionCommandEnd());
    bad.events = NULL; bad.word_count = 1;
    CHECK(ftCustomMoveBuildScript(&fp,&bad)[0] == ftMotionCommandEnd());
    CHECK(ftCustomJointResolve(NULL,nFTCustomJointRoot) == -1);
    fp.joints[25] = NULL;
    CHECK(ftCustomMoveBuildScript(&fp,&sFTCustomMoves[nFTKindCaptain][23])[0] == ftMotionCommandEnd());
    fp.player = 4; CHECK(ftCustomMoveBuildScript(&fp,&bad) == NULL);
    CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    return 0;
}
static s32 testCustomAnimation(void)
{
    FTStruct players[4] = { 0 }, preview;
    DObj joints[4][28] = { 0 };
    struct { f32 size; } attr = { 1.12F };
    const FTCustomMoveDefinition *moves[3] = { &sFTCustomMoves[nFTKindCaptain][23], &sFTCustomMoves[nFTKindFox][5], &sFTCustomMoves[nFTKindDonkey][14] };
    const FTCustomAnimationFrame *tables[3] = { sFTCustomAnimationCaptain, sFTCustomAnimationFox, sFTCustomAnimationDonkey };
    const FTCustomAnimationFrame *pose;
    s32 player, pilot, frame, i, aid, state;
    u32 failures;
    f32 saved;
    CHECK(sizeof(FTCustomAnimationFrame) == 628);
    gSCManagerSceneData.scene_curr = nSCKind1PTrainingMode;
    for (player = 0; player < 4; player++)
    {
        FTStruct *fp = &players[player];
        fp->player = player; fp->fkind = nFTKindMario; fp->pkind = nFTPlayerKindCom;
        fp->attr = (void*)&attr;
        gSCManagerCharBuilderPlayerSlots[player] = 0;
        gSCManagerCharBuilderSlots[0].body = nFTKindMario;
        gSCManagerCharBuilderSlots[0].is_enabled = TRUE;
        for (i = 0; i < 28; i++) fp->joints[i] = &joints[player][i];
        ftCustomMoveStartClock(fp, moves[player % 3], player * 2.0F);
        ftCustomMoveAdvanceClock(fp, 0);
    }
    for (player = 0; player < 4; player++) CHECK(ftCustomAnimationGetFrame(&players[player]) == &tables[player % 3][player * 2]);
    preview = players[0]; ftCustomMoveResetClock(&preview);
    CHECK(ftCustomAnimationGetFrame(&players[0]) == &tables[0][0]);
    for (pilot = 0; pilot < 3; pilot++)
    {
        FTStruct *fp = &players[0];
        ftCustomMoveStartClock(fp, moves[pilot], 0);
        for (frame = 0; frame <= moves[pilot]->duration; frame++)
        {
            ftCustomMoveAdvanceClock(fp, -1); pose = &tables[pilot][frame];
            CHECK(ftCustomAnimationGetFrame(fp) == pose);
            ftCustomAnimationApplyPose(fp);
            for (i = 0; i < 24; i++)
            {
                CHECK(joints[0][i + 4].rotate.vec.f.x == pose->joints[i].rotate.x);
                CHECK(joints[0][i + 4].rotate.vec.f.y == pose->joints[i].rotate.y);
                CHECK(joints[0][i + 4].rotate.vec.f.z == pose->joints[i].rotate.z);
                CHECK(joints[0][i + 4].translate.vec.f.y == pose->joints[i].translate.y);
                CHECK(joints[0][i + 4].scale.vec.f.x == 1.0F);
            }
            /* Reading/applying a frozen frame never advances the clock. */
            ftCustomAnimationApplyPose(fp); CHECK(ftCustomAnimationGetFrame(fp) == pose);
            for (state = nGMAttackStateNew; state <= nGMAttackStateInterpolate; state++)
            {
                for (aid = 0; aid < 4; aid++)
                {
                    fp->attack_colls[aid].attack_state = state;
                    fp->attack_colls[aid].joint = &joints[0][5];
                    fp->attack_colls[aid].offset.x = 123.0F;
                }
                ftCustomCollisionApply(fp);
                for (aid = 0; aid < 4; aid++)
                {
                    CHECK(fp->attack_colls[aid].attack_state == state);
                    if (pose->collision.active_mask & (1 << aid))
                    {
                        CHECK(fp->attack_colls[aid].joint == fp->joints[0]);
                        saved = fp->attack_colls[aid].offset.x * attr.size - pose->collision.centers[aid].x;
                        CHECK(saved < 0.001F && saved > -0.001F);
                        saved = fp->attack_colls[aid].offset.y * attr.size - pose->collision.centers[aid].y;
                        CHECK(saved < 0.001F && saved > -0.001F);
                        saved = fp->attack_colls[aid].offset.z * attr.size - pose->collision.centers[aid].z;
                        CHECK(saved < 0.001F && saved > -0.001F);
                        CHECK(!fp->attack_colls[aid].is_scale_pos);
                    }
                    else CHECK(fp->attack_colls[aid].offset.x == 123.0F);
                }
            }
        }
    }
    players[0].status_id++; CHECK(ftCustomAnimationGetFrame(&players[0]) == NULL); players[0].status_id--;
    players[0].motion_id++; CHECK(ftCustomAnimationGetFrame(&players[0]) == NULL); players[0].motion_id--;
    players[0].fkind = nFTKindFox; CHECK(ftCustomAnimationGetFrame(&players[0]) == NULL); players[0].fkind = nFTKindMario;
    players[0].pkind = nFTPlayerKindDemo; CHECK(ftCustomAnimationGetFrame(&players[0]) == NULL); players[0].pkind = nFTPlayerKindMan;
    gSCManagerSceneData.scene_curr = nSCKindTitle; CHECK(ftCustomAnimationGetFrame(&players[0]) == NULL);
    gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    ftCustomMoveStartClock(&players[0],moves[0],0); ftCustomMoveAdvanceClock(&players[0],0);
    saved = joints[0][4].rotate.vec.f.x; failures = gFTCustomAnimationValidationFailures;
    players[0].joints[27] = NULL; ftCustomAnimationApplyPose(&players[0]);
    CHECK(gFTCustomAnimationValidationFailures == failures + 1 && joints[0][4].rotate.vec.f.x == saved);
    ftCustomMoveResetClock(&players[0]); CHECK(ftCustomAnimationGetFrame(&players[0]) == NULL);
    CHECK(ftCustomAnimationGetFrame(&players[1]) == &tables[1][2]);
    ftCustomMoveStartClock(&players[1],&sFTCustomMoves[nFTKindFox][4],0);
    CHECK(ftCustomAnimationGetFrame(&players[1]) == NULL); /* Angled variants stay native. */
    return 0;
}
#include "testCharBuilderNeutral.c.inc"
#include "testCharBuilderThrow.c.inc"
#include "testCustomCollision.c.inc"
#include "testTrainingCombo.c.inc"
void _start(void)
{
    s32 result = testCustomMove();
    if (result == 0) result = testCustomAnimation();
    if (result == 0) result = testCustomCollision();
    if (result == 0) result = testFullCollisionRoster();
    if (result == 0) result = testCharBuilderNeutral();
    if (result == 0) result = testCharBuilderThrow();
    if (result == 0) result = testTrainingCombo();
    if (result != 0)
    {
        char message[] = "Failed CHECK at line 0000\n";
        s32 value = result, i;
        for (i = 24; i >= 21; i--) { message[i] = '0' + value % 10; value /= 10; }
        __asm__ volatile("int $0x80" : : "a"(4), "b"(2), "c"(message), "d"(sizeof(message) - 1) : "memory");
    }
    __asm__ volatile("int $0x80" : : "a"(1), "b"(result) : "memory");
    __builtin_unreachable();
}
