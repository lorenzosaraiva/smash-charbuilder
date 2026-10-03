/* Actual body enums and actual neutral adapter, with engine services stubbed. */
struct FTStatusDesc { u32 unused; };
struct FTMotionDesc { u32 unused; };
#define _WPVARS_H_
#define WPPKTHUNDER_PARTS_COUNT 5
#include <mp/mpdef.h>
#include <gm/gmsound.h>
#include <ft/ftchar/ftmario/ftmario.h>
#include <ft/ftchar/ftfox/ftfox.h>
#include <ft/ftchar/ftdonkey/ftdonkey.h>
#include <ft/ftchar/ftsamus/ftsamus.h>
#include <ft/ftchar/ftlink/ftlink.h>
#include <ft/ftchar/ftyoshi/ftyoshi.h>
#include <ft/ftchar/ftcaptain/ftcaptain.h>
#include <ft/ftchar/ftkirby/ftkirby.h>
#include <ft/ftchar/ftpikachu/ftpikachu.h>
#include <ft/ftchar/ftpurin/ftpurin.h>
#include <ft/ftchar/ftness/ftness.h>
struct GObj { f32 anim_frame; FTStruct *fp; DObj *root; };
#define ftGetStruct(gobj) ((gobj)->fp)
static s32 sTestNeutralStatusCalls, sTestNeutralShots, sTestNeutralEnds;
static sb32 sTestThrowMode;
static Vec3f sTestNeutralShotPosition;
static void ftMainSetStatus(GObj*, s32, f32, f32, u32);
static void mpCommonSetFighterWaitOrFall(GObj *gobj) { sTestNeutralEnds++; ftCustomMoveResetClock(gobj->fp); }
static void ftPhysicsApplyAirVelDrift(GObj *gobj) {}
static void ftPhysicsApplyGroundVelFriction(GObj *gobj) {}
static void mpCommonProcFighterWaitOrLanding(GObj *gobj) {}
static void mpCommonSetFighterFallOnEdgeBreak(GObj *gobj) {}
static GObj* wpFoxBlasterMakeWeapon(GObj *gobj, Vec3f *pos)
{ sTestNeutralShots++; sTestNeutralShotPosition = *pos; return gobj; }
static void func_800269C0_275C0(u16 id) {}
static void ftParamSetMotionID(FTStruct *fp, s32 id) {}
static void ftParamSetStatUpdate(FTStruct *fp, u16 flags) {}
static void ftParamUpdate1PGameAttackStats(FTStruct *fp, s32 unused) {}
static void ftMainCharBuilderClearSpecialDonor(FTStruct *fp) {}
static s32 sTestProjectileShots, sTestProjectileKind;
static sb32 sTestProjectileFailure, sTestNeutralLanding, sTestNeutralEdge;
static Vec3f sTestProjectilePosition, sTestProjectileVelocity;
static f32 sTestProjectileAngle;
static f32 __sinf(f32 v) { f32 r; __asm__("fsin" : "=t"(r) : "0"(v)); return r; }
static f32 __cosf(f32 v) { f32 r; __asm__("fcos" : "=t"(r) : "0"(v)); return r; }
static void ftPhysicsClampAirVelXMax(FTStruct *fp) {}
static void mpCommonSetFighterAir(FTStruct*);
static void mpCommonSetFighterGround(FTStruct*);
static sb32 mpCommonProcFighterLanding(GObj*, void (*)(GObj*));
static sb32 mpCommonProcFighterOnEdge(GObj *g, void (*callback)(GObj*))
{ if (sTestNeutralEdge) callback(g); return !sTestNeutralEdge; }
static GObj *wpMarioFireballMakeWeapon(GObj *g, Vec3f *p, s32 kind)
{ sTestProjectileShots++; sTestProjectileKind = kind; sTestProjectilePosition = *p; return sTestProjectileFailure ? NULL : g; }
static GObj *wpPikachuThunderJoltAirMakeWeapon(GObj *g, Vec3f *p, Vec3f *v)
{ sTestProjectileVelocity = *v; return wpMarioFireballMakeWeapon(g, p, 2); }
static GObj *wpNessPKFireMakeWeapon(GObj *g, Vec3f *p, Vec3f *v, f32 a)
{ sTestProjectileVelocity = *v; sTestProjectileAngle = a; return wpMarioFireballMakeWeapon(g, p, 3); }
#define FTCHARBUILDER_NEUTRAL_EXTENDED
sb32 ftMainCharBuilderTrySpecialN(GObj*);
#include "../src/ft/ftcharbuilderneutral.c.inc"
static void ftMainSetStatus(GObj *gobj, s32 status, f32 frame, f32 speed, u32 flags)
{
    FTStruct *fp = gobj->fp;
    sTestNeutralStatusCalls++;
    if (!sTestThrowMode && sFTCharBuilderNeutralStartingOwner != fp) sTestNeutralStatusCalls += 10000;
    ftCustomMoveResetClock(fp);
    fp->status_id = status; fp->motion_id = status;
    fp->motion_scripts[0][0].p_script = fp->motion_scripts[1][0].p_script = NULL;
    fp->motion_scripts[0][1].p_script = fp->motion_scripts[1][1].p_script = NULL;
    gobj->anim_frame = 0;
}

static s32 testCharBuilderNeutral(void)
{
    FTStruct players[4] = { 0 };
    GObj objects[4];
    DObj roots[4];
    FTStruct *fp;
    SCCharBuilderSlot *slot;
    const FTCustomMoveDefinition *move;
    s32 body, air, player, frame, shots, calls;
    gSCManagerSceneData.scene_curr = nSCKind1PTrainingMode;
    for (player = 0; player < 4; player++)
    {
        objects[player].fp = &players[player];
        fp = &players[player]; fp->player = player; fp->pkind = nFTPlayerKindMan;
        fp->joints[0] = &roots[player]; fp->lr = player & 1 ? -1 : 1;
        roots[player].translate.vec.f.x = 100; roots[player].translate.vec.f.y = 200;
        roots[player].translate.vec.f.z = 0;
        fp->input.button_mask_b = 2;
        gSCManagerCharBuilderPlayerSlots[player] = player;
    }
    for (body = 0; body < 12; body++) for (air = 0; air < 2; air++)
    {
        for (player = 0; player < 4; player++)
        {
            fp = &players[player]; slot = &gSCManagerCharBuilderSlots[player];
            fp->fkind = slot->body = body; fp->ga = air; slot->is_enabled = TRUE;
            fp->pkind = player == 3 ? nFTPlayerKindCom : nFTPlayerKindMan;
            slot->special_n = nSCCharBuilderNeutralBody; calls = sTestNeutralStatusCalls;
            CHECK(!ftMainCharBuilderTrySpecialN(&objects[player]));
            CHECK(sTestNeutralStatusCalls == calls);
            slot->special_n = nSCCharBuilderNeutralFoxLaser;
            if (body == nFTKindFox)
            {
                CHECK(!ftMainCharBuilderTrySpecialN(&objects[player]));
                CHECK(sTestNeutralStatusCalls == calls);
                continue;
            }
            CHECK(ftMainCharBuilderTrySpecialN(&objects[player]));
            CHECK(sTestNeutralStatusCalls == calls + 1 && sFTCharBuilderNeutralStartingOwner == NULL);
            CHECK(fp->status_id == sFTCharBuilderNeutralStatuses[body][air]);
            CHECK(body != nFTKindDonkey || fp->status_id != nFTDonkeyStatusSpecialNStart);
            CHECK(fp->motion_scripts[0][0].p_script == NULL && fp->motion_scripts[0][1].p_script == NULL);
            CHECK(fp->proc_update == ftMainCharBuilderNeutralProcUpdate);
            CHECK(fp->proc_interrupt == ftMainCharBuilderNeutralProcInterrupt);
            CHECK(fp->proc_physics == (air ? ftPhysicsApplyAirVelDrift : ftPhysicsApplyGroundVelFriction));
            CHECK(fp->proc_map == (air ? mpCommonProcFighterWaitOrLanding : mpCommonSetFighterFallOnEdgeBreak));
            CHECK(fp->proc_accessory == ftMainCharBuilderMakeLaser);
        }
        if (body == nFTKindFox) continue;
        move = &sFTCharBuilderLaserMoves[air]; shots = sTestNeutralShots;
        for (frame = 1; frame <= move->duration; frame++) for (player = 0; player < 4; player++)
        {
            fp = &players[player];
            fp->proc_accessory(&objects[player]); CHECK(sTestNeutralShots == shots);
            objects[player].anim_frame = ftCustomMoveAdvanceClock(fp, -1);
            CHECK(ftCustomMoveGetClock(fp)->frame == frame);
            if (frame == (air ? 15 : 25))
            {
                fp->motion_vars.flags.flag0 = 1;
                fp->proc_accessory(&objects[player]); shots++;
                CHECK(sTestNeutralShots == shots && fp->motion_vars.flags.flag0 == 0);
                CHECK(sTestNeutralShotPosition.x == 100 + fp->lr * 60);
                CHECK(sTestNeutralShotPosition.y == 280 && sTestNeutralShotPosition.z == 0);
                fp->proc_accessory(&objects[player]); CHECK(sTestNeutralShots == shots);
            }
            calls = sTestNeutralEnds; fp->proc_update(&objects[player]);
            CHECK(sTestNeutralEnds == calls + (frame == move->duration));
        }
    }
    fp = &players[0]; slot = &gSCManagerCharBuilderSlots[0];
    fp->fkind = slot->body = nFTKindDonkey; fp->ga = nMPKineticsGround;
    CHECK(ftMainCharBuilderTrySpecialN(&objects[0]));
    fp->input.pl.button_tap = 2; calls = sTestNeutralStatusCalls;
    fp->proc_interrupt(&objects[0]); CHECK(sTestNeutralStatusCalls == calls);
    fp->motion_vars.flags.flag1 = 1;
    fp->proc_interrupt(&objects[0]); CHECK(sTestNeutralStatusCalls == calls + 1);
    CHECK(ftCustomMoveGetClock(fp)->frame == 0 && fp->motion_vars.flags.flag1 == 0);
    fp->motion_vars.flags.flag0 = 1; ftCustomMoveResetClock(fp); shots = sTestNeutralShots;
    fp->proc_accessory(&objects[0]); CHECK(sTestNeutralShots == shots);
    fp->pkind = nFTPlayerKindDemo; CHECK(!ftMainCharBuilderTrySpecialN(&objects[0]));
    fp->pkind = nFTPlayerKindMan; slot->is_enabled = FALSE; CHECK(!ftMainCharBuilderTrySpecialN(&objects[0]));
    slot->is_enabled = TRUE; gSCManagerCharBuilderPlayerSlots[0] = -1;
    CHECK(!ftMainCharBuilderTrySpecialN(&objects[0]));
    gSCManagerCharBuilderPlayerSlots[0] = 0; gSCManagerSceneData.scene_curr = nSCKindTitle;
    CHECK(!ftMainCharBuilderTrySpecialN(&objects[0]));
    gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    for (body = 0; body < 12; body++) for (player = 0; player < 12; player++)
    {
        fp->fkind = slot->body = body; slot->attacks[nSCCharBuilderAttackThrowF] = player;
        CHECK(ftMainCharBuilderIsImmediateDonkeyThrow(fp) == (body == nFTKindDonkey && player != nFTKindDonkey));
    }
    fp->fkind = slot->body = nFTKindDonkey; slot->attacks[nSCCharBuilderAttackThrowF] = 255;
    CHECK(!ftMainCharBuilderIsImmediateDonkeyThrow(fp));
    slot->attacks[nSCCharBuilderAttackThrowF] = nFTKindMario;
    gSCManagerCharBuilderPlayerSlots[0] = -1; CHECK(!ftMainCharBuilderIsImmediateDonkeyThrow(fp));
    return 0;
}
