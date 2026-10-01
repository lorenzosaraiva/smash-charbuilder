/* Host-only, freestanding 32-bit test of the actual custom layer.
 * Minimal engine objects avoid IDO-only incomplete extern-array declarations.
 * Does not exercise N64 animation, collision detection, or emulation. */
#include <ssb_types.h>
#include <macros.h>
#include <ft/ftdef.h>
#include <gm/gmdef.h>

#define _FTTYPES_H_
struct DObj { s32 unused; };
typedef struct DObj DObj;
struct FTMotionScript { ftMotionCommand *p_script; };
struct FTMotionEventDefault { u32 words[1]; };
struct FTMotionEventMakeAttack { u32 words[5]; };
struct FTMotionEventSetAttackOffset { u32 words[2]; };
struct FTStruct
{
    s32 fkind, pkind;
    u32 player;
    s32 status_id, motion_id;
    DObj *joints[FTPARTS_JOINT_NUM_MAX];
    s32 attack_colls[4];
    FTMotionScript motion_scripts[2][3];
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
    FTCustomMoveDefinition bad;
    const FTCustomMoveDefinition *move;
    s32 body, donor, i, j, cursor, count;
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
            for (j = 0; j < 13; j++) gSCManagerCharBuilderSlots[0].attacks[j] = donor;
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
                    else CHECK(opcode == nFTMotionEventEnd || opcode == nFTMotionEventSyncWait || opcode == nFTMotionEventAsyncWait || opcode == nFTMotionEventPauseScript || opcode == nFTMotionEventClearAttackCollAll || opcode == nFTMotionEventClearAttackCollID || opcode == nFTMotionEventRefreshAttackCollID || opcode == nFTMotionEventSetAttackCollDamage || opcode == nFTMotionEventSetAttackCollSize || opcode == nFTMotionEventSetAttackCollSoundLevel);
                    cursor += count;
                }
                CHECK(cursor == sFTCustomMoves[donor][i].word_count);
                CHECK((script[cursor - 1] >> 26) == nFTMotionEventEnd);
            }
        }
    }
    fp.fkind = nFTKindMario; fp.motion_id = nFTCommonMotionAttackAirLw;
    gSCManagerCharBuilderSlots[0].body = nFTKindMario;
    gSCManagerCharBuilderSlots[0].attacks[nSCCharBuilderAttackDAir] = nFTKindCaptain;
    CHECK(ftCustomJointResolve(&fp,nFTCustomJointKneeR) == 25);
    script = ftCustomMoveBuildScript(&fp,ftCustomMoveGetDefinition(&fp));
    CHECK((script[0] & 0x03FFFFFF) == 7);
    CHECK(((script[1] >> 13) & 127) == 25);
    CHECK(((script[1] >> 5) & 255) == 14);
    CHECK((script[3] >> 16) == 45);
    CHECK((script[8] >> 16) == 0);
    saved = script[1]; other = fp; other.player = 1;
    second = ftCustomMoveBuildScript(&other,&sFTCustomMoves[nFTKindFox][23]);
    CHECK(second != script && script[1] == saved);
    fp.pkind = nFTPlayerKindCom; CHECK(ftCustomMoveGetDefinition(&fp) != NULL);
    fp.pkind = nFTPlayerKindDemo; CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    fp.pkind = nFTPlayerKindMan;
    fp.motion_scripts[0][0].p_script = native;
    CHECK(ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][0],nFTMotionEventMakeAttackColl));
    CHECK(fp.motion_scripts[0][0].p_script == native + 5);
    fp.motion_scripts[0][1].p_script = native;
    CHECK(ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][1],nFTMotionEventClearAttackCollAll));
    CHECK(!ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][2],nFTMotionEventClearAttackCollAll));
    CHECK(!ftCustomMoveSkipNativeCollision(&fp,&fp.motion_scripts[0][0],nFTMotionEventSetFlag1));
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
void _start(void)
{
    s32 result = testCustomMove();
    __asm__ volatile("int $0x80" : : "a"(1), "b"(result) : "memory");
    __builtin_unreachable();
}
