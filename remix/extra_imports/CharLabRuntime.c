/* Shared donor runtime compiled for Remix's original o32 fighter layout. */
#include <ft/fttypes.h>
#include <ft/ftcustommove.h>
#include <sc/scdef.h>
#include <sc/sctypes.h>
#include <sc/sccharbuilder.h>
#include <ft/ftmain.h>
#include <ft/ftparam.h>
#include <ft/ftphysics.h>
#include <mp/mpcommon.h>
#include <ft/fighter.h>
/* IDO headers erase attributes; the Remix Clang build needs real alignment
 * for DMA buffers and retained descriptors for the complete ROM catalog. */
#undef __attribute__
extern s32 ccBodyKind(FTStruct*);
extern void ccSuspendJoints(FTStruct*);
extern void ccResumeJoints(FTStruct*);
static void ccApplySpecialPose(FTStruct*);
static void ccVisualTick(GObj*);
static void ccVisualReset(void);
static void ccVisualStart(FTStruct*, f32);
static void ccVisualStatusChanging(GObj*, s32);
DObj* ftMainCharBuilderGetSpecialVisualJoint(FTStruct*, s32, s32);
static void ccVisualFalconEffect(GObj*, sb32);
static void ccVisualCutterEffect(GObj*);
u32 ccVisualPreserve(FTStruct*, const FTCustomMoveDefinition*);
static void ccPairTransition(GObj*, s32);
static sb32 ccPairPrepare(FTStruct*, f32);
static void ccPairTick(GObj*);
static void ccPairReset(void);
static void ccPairCollisionApply(FTStruct*);
static sb32 ccPairEffectLive(GObj*);
static void ccSyncCurrent(FTStruct*);
extern s32 sCCPairDonors[4];

/* Settings can enter Training CSS without the ordinary 1P menu setup. */
void ccSetupTraining(s32 body)
{
    SCCommonData *scene = (SCCommonData*)0x800A4AD0;
    scene->player = 0;
    scene->training_man_fkind = body;
    scene->training_man_costume = ftParamGetCostumeCommonID(body, 0);
    scene->training_com_fkind = nFTKindMario;
    scene->training_com_costume = ftParamGetCostumeCommonID(nFTKindMario, body == nFTKindMario ? 1 : 0);
}

SCCharBuilderSlot gSCManagerCharBuilderSlots[4];
s8 gSCManagerCharBuilderPlayerSlots[4] = { 0, 1, 2, 3 };
static struct { s32 scene_curr; } gSCManagerSceneData;
static FTStruct *sFTCharBuilderNeutralStartingOwner;
static FTMotionScript sCCMotionScripts[4];
#include "CharLabCollisionStorage.c.inc"
#include "../build/char_creator/runtime/move.c.inc"

void ccApplyAnimation(FTStruct *fp)
{
    /* Callback aliases for absent donor joints must never become visual
     * bones: cosmetic/optional pose writes would reset the world root. */
    ccSuspendJoints(fp);
    ftCustomAnimationApplyPose(fp);
    ccResumeJoints(fp);
}

#define ABI_CHECK(field, offset) _Static_assert(__builtin_offsetof(FTStruct, field) == offset, #field " Remix ABI")
ABI_CHECK(fkind, 0x8);
ABI_CHECK(player, 0xD);
ABI_CHECK(status_id, 0x24);
ABI_CHECK(motion_id, 0x28);
ABI_CHECK(attack_colls, 0x294);
ABI_CHECK(motion_scripts, 0x868);
ABI_CHECK(joints, 0x8E8);
ABI_CHECK(attr, 0x9C8);
ABI_CHECK(ga, 0x14C);
ABI_CHECK(motion_vars, 0x17C);
ABI_CHECK(motion_attack_id, 0x288);
ABI_CHECK(throw_desc, 0x848);
ABI_CHECK(proc_update, 0x9D4);
ABI_CHECK(proc_accessory, 0x9D8);
ABI_CHECK(proc_interrupt, 0x9DC);
_Static_assert(sizeof(FTAttackColl) == 0xC4, "Remix hitbox ABI");
_Static_assert(sizeof(FTMotionScript) == 0x20, "Remix motion-script ABI");
_Static_assert(__builtin_offsetof(GObj, user_data) == 0x84, "Remix GObj ABI");

void ccSync(FTStruct *fp, s32 **entries, s32 scene)
{
    SCCharBuilderSlot *slot;
    s32 i;
    s32 body = ccBodyKind(fp);
    gSCManagerSceneData.scene_curr = scene;
    if (fp->player >= 4) return;
    slot = &gSCManagerCharBuilderSlots[fp->player];
    slot->is_enabled = FALSE;
    if ((entries == NULL) || (body < 0) || (body >= 12) ||
        (*entries[1] != body) || !*entries[0]) return;
    slot->body = body;
    for (i = 0; i < 13; i++) slot->attacks[i] = (u32)*entries[i + 2] < 12 ? *entries[i + 2] : body;
    for (i = 0; i < 3; i++) slot->attacks[13 + i] = (u32)*entries[18 + i] < 12 ? *entries[18 + i] : body;
    slot->special_n = *entries[15];
    slot->special_hi = *entries[16]; slot->special_lw = *entries[17];
    slot->taunt = (u32)*entries[21] < 12 ? *entries[21] : body;
    slot->is_enabled = TRUE;
}

#include "../build/char_creator/runtime/special-timings.inc"
extern s32 ccSpecialDonor(FTStruct*);
typedef struct FTCharBuilderSpecialPath FTCharBuilderSpecialPath;
typedef struct CCSpecialClock
{
    FTStruct *owner;
    s32 status, motion, donor;
    u32 timing;
    f32 frame;
    u32 player_num;
    const FTCharBuilderSpecialPath *path;
    void (*physics)(GObj*);
} CCSpecialClock;
static CCSpecialClock sCCSpecialClocks[4];

static CCSpecialClock* ccSpecialClock(FTStruct *fp)
{
    CCSpecialClock *clock;
    if (fp->player >= 4) return NULL;
    clock = &sCCSpecialClocks[fp->player];
    if (clock->owner != fp || clock->player_num != fp->player_num || clock->status != fp->status_id ||
        clock->motion != fp->motion_id || clock->donor != ccSpecialDonor(fp)) return NULL;
    return clock;
}
#include "CharLabMovement.c.inc"
#include "CharLabNormals.c.inc"
#include "CharLabSpecials.c.inc"
extern s32 **ccGetEntries(s32 player);
extern void ccOriginalParse(GObj*, FTStruct*, FTMotionScript*, u32);
extern void ccRestoreBody(FTStruct*);

void ccReset(void)
{
    s32 i;
    ccVisualReset();
    ccPairReset();
    ftMainCharBuilderResetNeutralAll();
    for (i = 0; i < 4; i++)
    {
        sFTCustomMoveClocks[i].owner = NULL;
        sFTCustomLastAirAttack[i] = -1;
        gSCManagerCharBuilderSlots[i].is_enabled = FALSE;
        sCCMotionScripts[i].p_script = NULL;
        sCCCollisionSource[i] = 0;
        sCCSpecialClocks[i].owner = NULL;
        sCCSpecialStates[i].owner = NULL;
        sCCRecovery[i].owner = NULL;
    }
}

void ccStart(FTStruct *fp, f32 frame_begin)
{
    const FTCustomMoveDefinition *move;
    FTMotionScript *script;
    if (fp->player >= 4) return;
    script = &sCCMotionScripts[fp->player];
    script->p_script = NULL;
    ftCustomMoveResetClock(fp);
    if (sFTCharBuilderNeutralStartingOwner == fp)
    {
        s32 i, j;
        for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) fp->motion_scripts[i][j].p_script = NULL;
        return;
    }
    move = ftCustomMoveGetDefinition(fp);
    if (move == NULL) return;
    script->p_script = ftCustomMoveBuildScript(fp, move);
    script->script_wait = 1.0F - frame_begin;
    script->script_id = 0;
    ftCustomMoveStartClock(fp, move, frame_begin);
}

void ccAdvance(GObj *gobj)
{
    FTStruct *fp = gobj->user_data.p;
    CCSpecialClock *special = ccSpecialClock(fp);
    if (special != NULL)
    {
        f32 duration = special->timing & 0x7FFFFFFF;
        special->frame += ((DObj*)gobj->obj)->anim_speed;
        if ((special->timing & 0x80000000) && special->frame >= duration)
            special->frame -= duration;
        gobj->anim_frame = (!(special->timing & 0x80000000) && special->frame >= duration) ?
            -1.0F : (special->frame > 0.0F ? special->frame : 0.001F);
        if (ftCustomMoveGetClock(fp) != NULL)
        {
            ftCustomMoveGetClock(fp)->frame = special->frame;
            ftCustomMoveGetClock(fp)->native_frame = gobj->anim_frame;
        }
        ccApplyAnimation(fp);
        ccApplySpecialPose(fp);
        ccVisualTick(gobj);
        return;
    }
    gobj->anim_frame = ftCustomMoveAdvanceClock(fp, gobj->anim_frame);
    ccApplyAnimation(fp);
    ccPairTick(gobj);
    ccVisualTick(gobj);
}

void ccParse(GObj *gobj, FTStruct *fp, FTMotionScript *script, u32 opcode)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    f32 frame = gobj->anim_frame;
    s32 normal = ccNormalIndex(fp);
    if (normal >= 0 && normal / 33 != ccBodyKind(fp))
    {
        /* Native donor streams also contain cosmetic bone/mesh commands.
         * A borrowed smash must never index them through the body skeleton. */
        switch (opcode)
        {
        case nFTMotionEventSetModelPartID: case nFTMotionEventResetModelPartAll:
        case nFTMotionEventHideModelPartAll: case nFTMotionEventSetTexturePartID:
        case nFTMotionEventSetHitStatusPartID: case nFTMotionEventResetDamageCollPartAll:
        case nFTMotionEventSetHitStatusPartAll:
            ftMotionEventAdvance(script, FTMotionEventDefault); return;
        case nFTMotionEventSetDamageCollPartID:
            ftMotionEventAdvance(script, FTMotionEventSetDamageCollPartID); return;
        case nFTMotionEventEffect: case nFTMotionEventEffectItemHold:
        {
            const FTMotionEventMakeEffect *event = (const FTMotionEventMakeEffect*)script->p_script;
            Vec3f offset = { event->s2.off_x, event->s2.off_y, event->s3.off_z };
            Vec3f scatter = { event->s3.rng_x, event->s4.rng_y, event->s4.rng_z };
            DObj *part;
            s32 i, joint = -1;
            if (event->s1.joint_id != -1 && event->s1.joint_id != 127)
            {
                part = ftMainCharBuilderGetSpecialVisualJoint(fp, normal / 33, event->s1.joint_id);
                for (i = 0; i < FTPARTS_JOINT_NUM_MAX; i++)
                    if (fp->joints[i] == part) { joint = i; break; }
            }
            if (!fp->is_effect_skip)
                ftParamMakeEffect(gobj, event->s1.effect_id, joint, &offset, &scatter, fp->lr,
                    opcode == nFTMotionEventEffectItemHold, event->s1.flag);
            ftMotionEventAdvance(script, FTMotionEventMakeEffect); return;
        }
        }
    }
    if ((u32)ccSpecialDonor(fp) < 12)
    {
        /* Donor mesh/hurtbox IDs and attached effects cannot address a
         * foreign body's parts. Preserve body hurtboxes and whole-fighter
         * invulnerability while leaving source flags/weapon timing intact. */
        switch (opcode)
        {
        case nFTMotionEventSetModelPartID: case nFTMotionEventResetModelPartAll:
        case nFTMotionEventHideModelPartAll: case nFTMotionEventSetTexturePartID:
        case nFTMotionEventSetHitStatusPartID: case nFTMotionEventResetDamageCollPartAll:
            ftMotionEventAdvance(script, FTMotionEventDefault); return;
        case nFTMotionEventSetDamageCollPartID:
            ftMotionEventAdvance(script, FTMotionEventSetDamageCollPartID); return;
        case nFTMotionEventEffect: case nFTMotionEventEffectItemHold:
            ftMotionEventAdvance(script, FTMotionEventMakeEffect); return;
        case nFTMotionEventPlayFGM: case nFTMotionEventPlayFGMStoreInfo:
        case nFTMotionEventPlayLoopSFXStoreInfo: case nFTMotionEventStopLoopSFX:
        case nFTMotionEventPlayVoiceStoreInfo: case nFTMotionEventPlayLoopVoiceStoreInfo:
            if (ccSpecialClock(fp) != NULL) { ftMotionEventAdvance(script, FTMotionEventDefault); return; }
            break;
        }
    }
    /* Retargeted body animation flags must not overwrite source jab/landing
     * flags. The external normal event stream supplies their original waits. */
    if (script != &sCCMotionScripts[fp->player] && ccNormalIndex(fp)>=0 &&
        opcode>=nFTMotionEventSetFlag0 && opcode<=nFTMotionEventSetFlag3)
    { ftMotionEventAdvance(script, FTMotionEventDefault); return; }
    if (script != &sCCMotionScripts[fp->player] && ccSpecialClock(fp) != NULL && ccSpecialClock(fp)->path != NULL)
    {
        /* The phase is outside the normal definition table, so skip native
         * collision commands explicitly. Numeric flags still run natively. */
        switch(opcode)
        {
        case nFTMotionEventMakeAttackColl: case nFTMotionEventMakeAttackCollScaled:
            ftMotionEventAdvance(script,FTMotionEventMakeAttack);return;
        case nFTMotionEventSetAttackCollOffset:
            ftMotionEventAdvance(script,FTMotionEventSetAttackOffset);return;
        case nFTMotionEventClearAttackCollID: case nFTMotionEventClearAttackCollAll:
        case nFTMotionEventRefreshAttackCollID: case nFTMotionEventSetAttackCollDamage:
        case nFTMotionEventSetAttackCollSize: case nFTMotionEventSetAttackCollSoundLevel:
            ftMotionEventAdvance(script,FTMotionEventDefault);return;
        }
    }
    else if (ftCustomMoveSkipNativeCollision(fp, script, opcode)) return;
    if (clock != NULL)
        gobj->anim_frame = script == &sCCMotionScripts[fp->player] ? clock->frame : clock->native_frame;
    ccOriginalParse(gobj, fp, script, opcode);
    gobj->anim_frame = frame;
    if (opcode == nFTMotionEventSetThrow) ftCustomMoveApplyThrow(fp);
}

void ccEvents(GObj *gobj)
{
    FTStruct *fp = gobj->user_data.p;
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    FTMotionScript *script;
    s32 limit = FTCUSTOMMOVE_SCRIPT_WORDS * 2;
    if (clock == NULL) return;
    script = &sCCMotionScripts[fp->player];
    if (script->script_wait == F32_MAX)
    {
        if (((DObj*)gobj->obj)->anim_speed <= gobj->anim_frame) return;
        script->script_wait = -gobj->anim_frame;
    }
    else script->script_wait -= ccSpecialClock(fp) ? ((DObj*)gobj->obj)->anim_speed : clock->speed;
    while (script->p_script != NULL && script->script_wait <= 0.0F && limit-- > 0)
        ccParse(gobj, fp, script, *script->p_script >> 26);
    if (limit <= 0) { script->p_script = NULL; gFTCustomMoveValidationFailures++; }
}

void ccCollision(FTStruct *fp) { ccPairCollisionApply(fp); ccSpecialCollision(fp); }

static void ccSyncCurrent(FTStruct *fp)
{
    if (fp->player < 4)
        ccSync(fp, ccGetEntries(fp->player), *(volatile u8*)0x800A4AD0);
}

void ccPrepare(GObj *gobj, f32 frame_begin)
{
    FTStruct *fp = gobj->user_data.p;
    s32 donor;
    CCSpecialClock *clock;
    ccSyncCurrent(fp);
    if (ccPairPrepare(fp, frame_begin)) return;
    ccStart(fp, frame_begin);
    ccStartRecovery(fp, frame_begin);
    if (fp->player >= 4) return;
    clock = &sCCSpecialClocks[fp->player];
    if (clock->owner != fp || clock->player_num != fp->player_num || clock->donor != ccSpecialDonor(fp) || fp->status_id < 0xDC)
        ccSpecialState(fp)->angle = 0.0F;
    clock->owner = NULL;
    donor = ccSpecialDonor(fp);
    if ((u32)donor >= 12 || (u32)fp->motion_id >= 276 ||
        (fp->status_id < 0xDC && !ccKeepSpecialContext(fp, fp->status_id)) || !sCCSpecialTimings[donor][fp->motion_id]) return;
    clock->owner = fp;
    clock->status = fp->status_id;
    clock->motion = fp->motion_id;
    clock->donor = donor;
    clock->timing = sCCSpecialTimings[donor][fp->motion_id];
    clock->frame = frame_begin - ((DObj*)gobj->obj)->anim_speed;
    clock->player_num = fp->player_num;
    clock->path = ccFindSpecialPath(donor, fp->motion_id);
    clock->physics = fp->proc_physics;
    if (clock->path != NULL)
    {
        FTMotionScript *script=&sCCMotionScripts[fp->player];
        ftCustomMoveStartClock(fp,&clock->path->move,frame_begin);
        sFTCustomMoveClocks[fp->player].frame=clock->frame;
        script->p_script=(ftMotionCommand*)clock->path->move.events;
        script->script_wait=1.0F-frame_begin;script->script_id=0;
        if (clock->physics != NULL) fp->proc_physics=ccDonorPhysics;
    }
    ccVisualStart(fp, frame_begin);
}

extern GObj *wpFoxBlasterMakeWeapon(GObj*, Vec3f*);
extern alSoundEffect *func_800269C0_275C0(u16);
static void ftMainCharBuilderClearSpecialDonor(FTStruct *fp) { ccRestoreBody(fp); }
#include "../build/char_creator/runtime/neutral-weapons.inc"
#include "../build/char_creator/runtime/neutral.c.inc"

static sb32 ccNeutralBoomerangOwner(GObj *owner, GObj *weapon)
{
    FTStruct *fp = ftGetStruct(owner);
    FTCharBuilderNeutralState *s;
    if (fp == NULL || fp->player >= 4) return FALSE;
    s = &sFTCharBuilderNeutralStates[fp->player];
    return s->owner == fp && s->generation == fp->player_num && s->body == ccBodyKind(fp) && s->boomerang == weapon;
}
#include "CharLabAnimations.c.inc"
#include "CharLabVisuals.c.inc"
#include "CharLabPairs.c.inc"

sb32 ccNeutral(GObj *gobj)
{
    ccSyncCurrent(ftGetStruct(gobj));
    if (ftGetStruct(gobj)->player < 4 && gSCManagerCharBuilderSlots[ftGetStruct(gobj)->player].special_n == nSCCharBuilderNeutralPikachuJolt)
        gFTDataPikachuParticleBankID = sCCNeutralParticleBanks[0];
    if (ftGetStruct(gobj)->player < 4 && gSCManagerCharBuilderSlots[ftGetStruct(gobj)->player].special_n == nSCCharBuilderNeutralEggLay)
        gFTDataYoshiSpecial3 = sCCNeutralFiles[6];
    return ftMainCharBuilderTrySpecialN(gobj);
}

/* Retain the body's capture/victim machinery and donor numeric parameters. */
extern s32 ccMappedThrownKind(s32 fkind, s32 direction);
#include "../build/char_creator/runtime/throw.c"
sb32 ccThrow(GObj *gobj, sb32 forward)
{
    FTStruct *fp = ftGetStruct(gobj);
    ccSyncCurrent(fp);
    if (ftCustomMoveGetSlot(fp) == NULL) return FALSE;
    ftCommonThrowSetStatus(gobj, forward);
    return TRUE;
}

/* Export the compiled layout for the ROM verifier, alongside native ABI asserts. */
#define OFF(type, field) __builtin_offsetof(type, field)
const u32 ccLayout[] = {
    sizeof(FTStruct), OFF(FTStruct, pkind), OFF(FTStruct, ga),
    OFF(FTStruct, motion_vars), OFF(FTStruct, motion_attack_id),
    OFF(FTStruct, throw_desc), OFF(FTStruct, proc_update),
    OFF(FTStruct, proc_interrupt), OFF(FTStruct, proc_accessory),
    OFF(FTAttributes, size), OFF(GObj, obj), OFF(GObj, anim_frame),
    OFF(DObj, translate.vec.f), OFF(DObj, rotate.vec.f),
    OFF(DObj, scale.vec.f), OFF(DObj, anim_speed), sizeof(DObj),
    OFF(FTStruct, catch_gobj), OFF(FTStruct, capture_gobj),
    nFTCommonStatusCatch, nFTCommonMotionCatch,
    nFTCommonStatusThrowF, nFTMotionAttackIDThrowF, nFTMotionAttackIDThrowB,
    nFTDonkeyStatusThrowFF, nFTCommonStatusShouldered, nFTCommonStatusThrownCommon,
    nSCKindVSBattle, nSCKind1PTrainingMode, nMPKineticsAir,
    OFF(FTAttributes, thrown_status), OFF(FTStruct, input.pl.stick_range),
    OFF(FTStruct, input.pl.button_tap), OFF(FTStruct, input.button_mask_b)
};

const u32 ccSpecialLayout[] = {
    OFF(FTStruct, status_vars), OFF(FTStruct, physics.vel_air),
    OFF(FTStruct, physics.vel_ground), OFF(FTStruct, joints),
    nFTPikachuStatusSpecialHi, nFTPikachuStatusSpecialHiEnd,
    nFTPikachuStatusSpecialAirHi, nFTPikachuStatusSpecialAirHiEnd
};
const u32 ccClockLayout[] = {
    sizeof(FTCustomMoveClock), OFF(FTCustomMoveClock, move), OFF(FTCustomMoveClock, frame),
    OFF(FTStruct, player_num), OFF(FTStruct, physics.vel_ground), OFF(FTStruct, proc_physics)
};
const u32 ccMovementLayout[] = {
    sizeof(CCSpecialClock), OFF(CCSpecialClock, frame),
    sizeof(FTCharBuilderSpecialPath), ARRAY_COUNT(sFTCharBuilderSpecialPaths),
    OFF(FTCharBuilderSpecialPath, trajectory), OFF(FTCharBuilderSpecialPath, travel),
    sizeof(FTCustomNormalMechanics), OFF(FTCustomNormalMechanics, count),
    OFF(FTStruct, coll_data.floor_angle), OFF(FTAttributes, traction)
};
const u32 ccAdapterLayout[] = {
    sizeof(CCSpecialState), OFF(CCSpecialState, angle), OFF(CCSpecialState, tornado),
    OFF(CCSpecialState, ness), OFF(CCSpecialState, weapons), OFF(FTStruct, fighter_gobj),
    OFF(FTStruct, motion_attack_id), OFF(FTStruct, special_coll),
    OFF(FTStruct, passive_vars), sizeof(((FTStruct*)0)->passive_vars),
    OFF(FTStruct, status_vars.common.fallspecial.is_fall_accelerate),
    OFF(FTStruct, status_vars.fox.specialhi.angle), OFF(FTStruct, damage_resist),
    OFF(FTAttributes, gravity), OFF(FTAttributes, tvel_base),
    OFF(FTAttributes, air_speed_max_x), OFF(FTAttributes, air_accel),
    nFTCommonStatusFallSpecial, nFTCommonStatusLandingFallSpecial,
    nFTMotionAttackIDSpecialHi, nFTMotionAttackIDSpecialLw,
    nFTMarioMotionSpecialHi, nFTMarioMotionSpecialAirHi, nFTMarioStatusSpecialHi,
    nFTMarioStatusSpecialAirHi, nFTFoxStatusSpecialHi, nFTFoxStatusSpecialAirHi,
    nFTFoxMotionSpecialHi, nFTFoxMotionSpecialAirHi,
    nFTYoshiMotionSpecialHi, nFTPikachuMotionSpecialLwStart,
    nFTNessMotionSpecialHiHold, nFTFoxMotionSpecialLwLoop, nFTNessMotionSpecialLwHold,
    OFF(FTStruct, status_vars.ness.specialhi.pkjibaku_delay),
    OFF(FTStruct, status_vars.kirby.speciallw.duration),
    nFTKirbyMotionSpecialLwHold, nFTYoshiStatusSpecialHi,
    OFF(WPStruct, weapon_vars), OFF(WPStruct, player_num), OFF(WPStruct, weapon_gobj)
};
const u32 ccPairedSpecialLayout[] = {
    OFF(FTStruct, item_gobj), OFF(ITStruct, kind), OFF(ITStruct, owner_gobj), nITKindLinkBomb,
    nFTCommonStatusLightThrowF4, nFTCommonStatusLightThrowAirF4,
    nFTCommonMotionLightThrowF4, nFTCommonMotionLightThrowAirF4,
    nFTCaptainMotionSpecialHiCatch, nFTCaptainStatusSpecialHiCatch,
    OFF(ITStruct, physics.vel_air), OFF(ITStruct, vel_scale),
    OFF(FTStruct, status_vars.common.capturecaptain.capture_flag)
};
const u32 ccVisualCommandLayout[] = {
    nFTMotionEventSetModelPartID, nFTMotionEventResetModelPartAll,
    nFTMotionEventHideModelPartAll, nFTMotionEventSetTexturePartID,
    nFTMotionEventSetHitStatusPartID, nFTMotionEventResetDamageCollPartAll,
    nFTMotionEventSetDamageCollPartID, nFTMotionEventEffect, nFTMotionEventEffectItemHold
};
const u32 ccTrainingSetupLayout[] = {
    OFF(SCCommonData, player), OFF(SCCommonData, training_man_fkind),
    OFF(SCCommonData, training_man_costume), OFF(SCCommonData, training_com_fkind),
    OFF(SCCommonData, training_com_costume)
};

const u32 ccNormalLayout[] = {
    sizeof(FTAttributes), OFF(FTAttributes, attack1_followup_frames),
    OFF(FTAttributes, traction), OFF(FTAttributes, gravity),
    OFF(FTAttributes, tvel_base), OFF(FTAttributes, tvel_fast),
    OFF(FTAttributes, air_speed_max_x), OFF(FTAttributes, air_accel), OFF(FTAttributes, air_friction),
    OFF(FTStruct, attack1_followup_frames), OFF(FTStruct, attack1_input_count), OFF(FTStruct, attack1_status_id),
    OFF(FTStruct, status_vars.common.attack1.is_goto_followup),
    OFF(FTStruct, status_vars.common.attackair.rehit_timer),
    OFF(FTStruct, input.pl.button_release), OFF(FTStruct, input.button_mask_a),
    OFF(FTStruct, fighter_gobj), OFF(FTStruct, special_coll), OFF(FTStruct, proc_hit),
    OFF(FTStruct, proc_map), OFF(FTStruct, tics_since_last_z),
    nFTCommonStatusAttack11, nFTCommonStatusAttack12,
    nFTCommonStatusAttackAirN, nFTCommonStatusAttackAirLw, nFTCommonStatusAttackS4,
    nFTCommonStatusLandingAirNull,
    nFTCommonStatusLandingAirStart, nFTCommonStatusLandingAirEnd,
    FTCOMMON_ATTACKAIRLW_LINK_REHIT_FRAME_BEGIN, FTCOMMON_ATTACKAIRLW_LINK_REHIT_FRAME_END,
    FTCOMMON_ATTACKAIRLW_LINK_REHIT_TIMER,
    nFTMotionEventSetFlag0,nFTMotionEventSetFlag1,nFTMotionEventSetFlag2,nFTMotionEventSetFlag3
};

const u32 ccNeutralWeaponLayout[] = {
    sizeof(WPStruct), OFF(WPStruct, lifetime), OFF(WPStruct, physics.vel_air),
    OFF(WPStruct, weapon_vars.boomerang.parent_gobj), OFF(WPStruct, owner_gobj),
    OFF(WPStruct, attack_coll.damage), OFF(WPStruct, attack_coll.size),
    OFF(WPStruct, weapon_vars.charge_shot.owner_gobj), OFF(DObj, mobj),
    WPBOOMERANG_LIFETIME_TILT, WPBOOMERANG_LIFETIME_SMASH, WPBOOMERANG_VEL_TILT,
    WPBOOMERANG_VEL_SMASH, WPPIKACHUJOLT_LIFETIME, WPPKFIRE_LIFETIME
};
