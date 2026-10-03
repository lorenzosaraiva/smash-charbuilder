/* Shared donor runtime compiled for Remix's original o32 fighter layout. */
#include <ft/fttypes.h>
#include <sc/scdef.h>
#include <sc/sccharbuilder.h>
#include <ft/ftmain.h>
#include <ft/ftparam.h>
#include <ft/ftphysics.h>
#include <mp/mpcommon.h>

SCCharBuilderSlot gSCManagerCharBuilderSlots[4];
s8 gSCManagerCharBuilderPlayerSlots[4] = { 0, 1, 2, 3 };
static struct { s32 scene_curr; } gSCManagerSceneData;
static FTStruct *sFTCharBuilderNeutralStartingOwner;
#include "../../ssb-decomp-re/src/ft/ftcustommove.c.inc"

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
    gSCManagerSceneData.scene_curr = scene;
    if (fp->player >= 4) return;
    slot = &gSCManagerCharBuilderSlots[fp->player];
    slot->is_enabled = FALSE;
    if ((entries == NULL) || (fp->fkind < 0) || (fp->fkind >= 12) ||
        (*entries[1] != fp->fkind) || !*entries[0]) return;
    slot->body = fp->fkind;
    for (i = 0; i < 13; i++) slot->attacks[i] = (u32)*entries[i + 2] < 12 ? *entries[i + 2] : fp->fkind;
    for (i = 0; i < 3; i++) slot->attacks[13 + i] = (u32)*entries[18 + i] < 12 ? *entries[18 + i] : fp->fkind;
    slot->special_n = *entries[15];
    slot->is_enabled = TRUE;
}

static FTMotionScript sCCMotionScripts[4];
#include "../build/char_creator/runtime/special-timings.inc"
extern s32 ccSpecialDonor(FTStruct*);
typedef struct CCSpecialClock
{
    FTStruct *owner;
    s32 status, motion, donor;
    u32 timing;
    f32 frame;
} CCSpecialClock;
static CCSpecialClock sCCSpecialClocks[4];

static CCSpecialClock* ccSpecialClock(FTStruct *fp)
{
    CCSpecialClock *clock;
    if (fp->player >= 4) return NULL;
    clock = &sCCSpecialClocks[fp->player];
    if (clock->owner != fp || clock->status != fp->status_id ||
        clock->motion != fp->motion_id || clock->donor != ccSpecialDonor(fp)) return NULL;
    return clock;
}
extern s32 **ccGetEntries(s32 player);
extern void ccOriginalParse(GObj*, FTStruct*, FTMotionScript*, u32);
extern void ccRestoreBody(FTStruct*);

void ccReset(void)
{
    s32 i;
    for (i = 0; i < 4; i++)
    {
        sFTCustomMoveClocks[i].owner = NULL;
        sFTCustomLastAirAttack[i] = -1;
        gSCManagerCharBuilderSlots[i].is_enabled = FALSE;
        sCCMotionScripts[i].p_script = NULL;
        sCCSpecialClocks[i].owner = NULL;
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
        return;
    }
    gobj->anim_frame = ftCustomMoveAdvanceClock(fp, gobj->anim_frame);
    ftCustomAnimationApplyPose(fp);
}

void ccParse(GObj *gobj, FTStruct *fp, FTMotionScript *script, u32 opcode)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    f32 frame = gobj->anim_frame;
    if (ftCustomMoveSkipNativeCollision(fp, script, opcode)) return;
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
    else script->script_wait -= 1.0F;
    while (script->p_script != NULL && script->script_wait <= 0.0F && limit-- > 0)
        ccParse(gobj, fp, script, *script->p_script >> 26);
    if (limit <= 0) { script->p_script = NULL; gFTCustomMoveValidationFailures++; }
}

void ccCollision(FTStruct *fp) { ftCustomCollisionApply(fp); }

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
    ccStart(fp, frame_begin);
    if (fp->player >= 4) return;
    clock = &sCCSpecialClocks[fp->player];
    clock->owner = NULL;
    donor = ccSpecialDonor(fp);
    if ((u32)donor >= 12 || (u32)fp->motion_id >= 276 ||
        fp->status_id < 0xDC || !sCCSpecialTimings[donor][fp->motion_id]) return;
    clock->owner = fp;
    clock->status = fp->status_id;
    clock->motion = fp->motion_id;
    clock->donor = donor;
    clock->timing = sCCSpecialTimings[donor][fp->motion_id];
    clock->frame = frame_begin - ((DObj*)gobj->obj)->anim_speed;
}

#define ftGetStruct(gobj) ((FTStruct*)(gobj)->user_data.p)
extern GObj *wpFoxBlasterMakeWeapon(GObj*, Vec3f*);
extern alSoundEffect *func_800269C0_275C0(u16);
static void ftMainCharBuilderClearSpecialDonor(FTStruct *fp) { ccRestoreBody(fp); }
#include "../build/char_creator/runtime/neutral.c.inc"

sb32 ccNeutral(GObj *gobj)
{
    ccSyncCurrent(ftGetStruct(gobj));
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
