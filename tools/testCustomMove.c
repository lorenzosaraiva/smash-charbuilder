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
    FTMotionScript motion_scripts[2][2];
};
#include "../src/ft/ftcustommove.c.inc"

#define CHECK(expr) do { if (!(expr)) return __LINE__; } while (0)

static s32 testCustomMove(void)
{
    FTStruct fp = { 0 }, other = { 0 };
    DObj joint;
    FTCustomMoveDefinition move = sFTCustomMarioAttackAirLw;
    ftMotionCommand *script, *second;
    ftMotionCommand native[8];
    u32 saved;
    s32 i;

    fp.fkind = nFTKindMario;
    fp.pkind = nFTPlayerKindMan;
    fp.status_id = nFTCommonStatusAttackAirLw;
    fp.motion_id = nFTCommonMotionAttackAirLw;
    for (i = 0; i < ARRAY_COUNT(fp.joints); i++) fp.joints[i] = &joint;
    CHECK(ftCustomMoveGetDefinition(&fp) != NULL);
    CHECK(ftCustomJointResolve(&fp, nFTCustomJointKneeR) == 25);
    CHECK(ftCustomJointResolve(&fp, nFTCustomJointFootR) == 27);
    CHECK(ftCustomJointResolve(&fp, -1) == -1);
    CHECK(ftCustomJointResolve(&fp, nFTCustomJointEnumCount) == -1);
    CHECK(ftCustomJointResolve(NULL, nFTCustomJointRoot) == -1);
    script = ftCustomMoveBuildScript(&fp, &move);
    CHECK((script[0] >> 26) == nFTMotionEventAsyncWait);
    CHECK((script[0] & 0x03FFFFFF) == 7);
    CHECK(((script[1] >> 13) & 0x7F) == 25);
    CHECK(((script[1] >> 5) & 255) == 14);
    CHECK((script[2] >> 16) == 330);
    CHECK((script[3] >> 16) == 45);
    CHECK(((script[4] >> 22) & 1023) == ((u32)-80 & 1023));
    CHECK(((script[4] >> 12) & 1023) == 100);
    CHECK(((script[6] >> 13) & 0x7F) == 5);
    CHECK((script[7] >> 16) == 190);
    CHECK((script[11] >> 26) == nFTMotionEventSyncWait);
    CHECK((script[11] & 0x03FFFFFF) == 18);
    CHECK((script[12] >> 26) == nFTMotionEventClearAttackCollAll);
    CHECK((script[13] >> 26) == nFTMotionEventEnd);
    move.hitbox_count = 4;
    move.hitboxes[2] = move.hitboxes[0];
    move.hitboxes[3] = move.hitboxes[1];
    script = ftCustomMoveBuildScript(&fp, &move);
    CHECK(((script[16] >> 23) & 7) == 3);
    CHECK((script[23] >> 26) == nFTMotionEventEnd);
    move = sFTCustomMarioAttackAirLw;
    script = ftCustomMoveBuildScript(&fp, &move);
    /* Separate fighter storage; rebuilding one cannot corrupt another. */
    other = fp;
    other.player = 1;
    saved = script[1];
    second = ftCustomMoveBuildScript(&other, &move);
    CHECK(second != script);
    move.hitboxes[0].damage = 19;
    ftCustomMoveBuildScript(&other, &move);
    CHECK(script[1] == saved);
    /* Invalid skeleton joint skips only its box. */
    fp.joints[25] = NULL;
    script = ftCustomMoveBuildScript(&fp, &move);
    CHECK(((script[1] >> 23) & 7) == 1);
    CHECK(((script[1] >> 13) & 0x7F) == 5);
    CHECK((script[6] >> 26) == nFTMotionEventSyncWait);
    fp.joints[25] = &joint;
    move.hitboxes[0].damage = 256;
    script = ftCustomMoveBuildScript(&fp, &move);
    CHECK(((script[1] >> 23) & 7) == 1);
    move = sFTCustomMarioAttackAirLw;
    move.hitbox_count = 5;
    CHECK(ftCustomMoveBuildScript(&fp, &move)[0] == ftMotionCommandEnd());
    move.hitbox_count = -1;
    CHECK(ftCustomMoveBuildScript(&fp, &move)[0] == ftMotionCommandEnd());
    move = sFTCustomMarioAttackAirLw;
    move.active_frames = 0;
    CHECK(ftCustomMoveBuildScript(&fp, &move)[0] == ftMotionCommandEnd());
    CHECK(ftCustomMoveBuildScript(&fp, NULL)[0] == ftMotionCommandEnd());
    fp.player = GMCOMMON_PLAYERS_MAX;
    CHECK(ftCustomMoveBuildScript(&fp, &move) == NULL);
    CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    fp.player = 0;
    /* Mario's native refresh/clear cannot make the new move multihit. */
    fp.motion_scripts[0][0].p_script = native;
    CHECK(ftCustomMoveSkipNativeCollision(&fp, &fp.motion_scripts[0][0], nFTMotionEventMakeAttackColl));
    CHECK(fp.motion_scripts[0][0].p_script == native + 5);
    fp.motion_scripts[1][0].p_script = native;
    CHECK(ftCustomMoveSkipNativeCollision(&fp, &fp.motion_scripts[1][0], nFTMotionEventRefreshAttackCollID));
    CHECK(fp.motion_scripts[1][0].p_script == native + 1);
    CHECK(!ftCustomMoveSkipNativeCollision(&fp, &fp.motion_scripts[0][0], nFTMotionEventSetFlag1));
    CHECK(!ftCustomMoveSkipNativeCollision(&fp, &fp.motion_scripts[0][1], nFTMotionEventClearAttackCollAll));
    fp.status_id = nFTCommonStatusAttackAirF;
    CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    CHECK(!ftCustomMoveSkipNativeCollision(&fp, &fp.motion_scripts[0][0], nFTMotionEventClearAttackCollAll));
    fp.status_id = nFTCommonStatusAttackAirLw;
    fp.pkind = nFTPlayerKindDemo;
    CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    fp.pkind = nFTPlayerKindMan;
    fp.fkind = nFTKindFox;
    CHECK(ftCustomMoveGetDefinition(&fp) == NULL);
    CHECK(ftCustomJointResolve(&fp, nFTCustomJointKneeR) == -1);
    CHECK(gFTCustomMoveValidationFailures == 8);
    return 0;
}

void _start(void)
{
    s32 result = testCustomMove();
    __asm__ volatile("int $0x80" : : "a"(1), "b"(result) : "memory");
    __builtin_unreachable();
}
