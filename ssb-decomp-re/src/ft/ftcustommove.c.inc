/* Compiled in ftmain's overlay; no runtime donor file/script is needed. */
#include <ft/ftcustommove.h>
#include "ftcustommoves.generated.inc"
#include "ftcustomgrabs.generated.inc"

static ftMotionCommand sFTCustomMoveScripts[GMCOMMON_PLAYERS_MAX][FTCUSTOMMOVE_SCRIPT_WORDS];
u32 gFTCustomMoveValidationFailures;
static s8 sFTCustomLastAirAttack[4] = { -1, -1, -1, -1 };
static FTThrowHitDesc sFTCustomThrowDescs[GMCOMMON_PLAYERS_MAX][2];

typedef struct FTCustomMoveClock
{
    FTStruct *owner;
    u32 player_num;
    const FTCustomMoveDefinition *move;
    s32 status_id, motion_id, duration;
    f32 frame, native_frame;
    u32 flags;
#ifdef FTCHARBUILDER_NEUTRAL_EXTENDED
    const struct FTCustomCollisionTrajectory *trajectory;
    f32 speed;
#endif
} FTCustomMoveClock;

static FTCustomMoveClock sFTCustomMoveClocks[GMCOMMON_PLAYERS_MAX];

static FTCustomMoveClock* ftCustomMoveGetClock(FTStruct *fp)
{
    FTCustomMoveClock *clock;
    if ((fp == NULL) || (fp->player >= GMCOMMON_PLAYERS_MAX)) return NULL;
    clock = &sFTCustomMoveClocks[fp->player];
    if ((clock->owner != fp) || (clock->player_num != fp->player_num) ||
        (clock->status_id != fp->status_id) || (clock->motion_id != fp->motion_id)) return NULL;
    return clock;
}

static void ftCustomMoveResetClock(FTStruct *fp)
{
    if ((fp->player < GMCOMMON_PLAYERS_MAX) && (sFTCustomMoveClocks[fp->player].owner == fp))
        sFTCustomMoveClocks[fp->player].owner = NULL;
}

static void ftCustomMoveStartClock(FTStruct *fp, const FTCustomMoveDefinition *move, f32 frame_begin)
{
    FTCustomMoveClock *clock;
    ftCustomMoveResetClock(fp);
    if ((move == NULL) || (move->duration <= 0) || (fp->player >= GMCOMMON_PLAYERS_MAX)) return;
    clock = &sFTCustomMoveClocks[fp->player];
    clock->owner = fp;
    clock->player_num = fp->player_num;
    clock->move = move;
    clock->status_id = fp->status_id;
    clock->motion_id = fp->motion_id;
    clock->duration = move->duration;
    clock->flags = move->flags;
#ifdef FTCHARBUILDER_NEUTRAL_EXTENDED
    clock->trajectory = NULL;
    clock->speed = 1.0F;
#endif
    clock->frame = frame_begin - 1.0F;
    clock->native_frame = frame_begin;
}

/* Called when animation advances, so hitlag and pauses stop both clocks. */
static f32 ftCustomMoveAdvanceClock(FTStruct *fp, f32 native_frame)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    if (clock == NULL) return native_frame;
    clock->native_frame = native_frame;
#ifdef FTCHARBUILDER_NEUTRAL_EXTENDED
    clock->frame += clock->speed;
#else
    clock->frame += 1.0F;
#endif
    if (clock->flags & FTCUSTOMMOVE_FLAG_LOOP) return native_frame;
    if (clock->flags & FTCUSTOMMOVE_FLAG_SPECIAL_CYCLE)
    {
        if (clock->frame >= clock->duration) clock->frame = 0.0F;
        return clock->frame;
    }
    if (clock->frame >= clock->duration) return -1.0F;
    return (clock->frame > 0.0F) ? clock->frame : 0.001F;
}

static f32 ftCustomMoveEventFrame(FTStruct *fp, FTMotionScript *ms, f32 native_frame)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    if (clock == NULL) return native_frame;
    return ((ms == &fp->motion_scripts[0][2]) || (ms == &fp->motion_scripts[1][2])) ? clock->frame : clock->native_frame;
}

static f32 ftCustomMoveEventSpeed(FTStruct *fp, FTMotionScript *ms, f32 anim_speed)
{
    if ((ftCustomMoveGetClock(fp) != NULL) &&
        ((ms == &fp->motion_scripts[0][2]) || (ms == &fp->motion_scripts[1][2])))
    {
#ifdef FTCHARBUILDER_NEUTRAL_EXTENDED
        return ftCustomMoveGetClock(fp)->speed;
#else
        return 1.0F;
#endif
    }
    return anim_speed;
}

static s32 ftCustomJointResolve(FTStruct *fp, FTCustomJointKind kind)
{
    s32 joint_id;
    if ((fp == NULL) || (fp->fkind < nFTKindPlayableStart) ||
        (fp->fkind > nFTKindPlayableEnd) || (kind < 0) || (kind >= nFTCustomJointEnumCount)) return -1;
    joint_id = (kind == nFTCustomJointGrabPoint) ? sFTCustomGrabJointMap[fp->fkind] : sFTCustomJointMaps[fp->fkind][kind];
    if ((joint_id < 0) || (joint_id >= ARRAY_COUNT(fp->joints)) || (fp->joints[joint_id] == NULL)) return -1;
    return joint_id;
}

static SCCharBuilderSlot* ftCustomMoveGetSlot(FTStruct *fp)
{
    SCCharBuilderSlot *slot;
    s32 slot_id;
    if ((fp == NULL) || (fp->pkind == nFTPlayerKindDemo) ||
        (fp->player >= GMCOMMON_PLAYERS_MAX) || (fp->fkind < nFTKindPlayableStart) || (fp->fkind > nFTKindPlayableEnd) ||
        ((gSCManagerSceneData.scene_curr != nSCKindVSBattle) &&
         (gSCManagerSceneData.scene_curr != nSCKind1PTrainingMode))) return NULL;
    slot_id = gSCManagerCharBuilderPlayerSlots[fp->player];
    if ((slot_id < 0) || (slot_id >= SCCHARBUILDER_SLOTS_COUNT)) return NULL;
    slot = &gSCManagerCharBuilderSlots[slot_id];
    if ((slot->is_enabled == FALSE) || (slot->body != fp->fkind)) return NULL;
    return slot;
}

/* A foreign forward throw must release, rather than enter DK's carry loop. */
sb32 ftMainCharBuilderIsImmediateDonkeyThrow(FTStruct *fp)
{
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    s32 donor;
    if ((slot == NULL) || (fp->fkind != nFTKindDonkey)) return FALSE;
    donor = slot->attacks[nSCCharBuilderAttackThrowF];
    return (donor >= nFTKindPlayableStart) && (donor <= nFTKindPlayableEnd) && (donor != nFTKindDonkey);
}

static const FTCustomMoveDefinition* ftCustomMoveGetDefinition(FTStruct *fp)
{
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    s32 attack, i, donor;
    if (slot == NULL) return NULL;
    if ((fp->status_id == nFTCommonStatusCatch) && (fp->motion_id == nFTCommonMotionCatch))
    {
        donor = slot->attacks[nSCCharBuilderAttackGrab];
        if ((donor >= nFTKindPlayableStart) && (donor <= nFTKindPlayableEnd) && (donor != fp->fkind))
            return &sFTCustomGrabMoves[donor];
        return NULL;
    }
    for (i = 0; i < 33; i++)
    {
        if (i < ARRAY_COUNT(sFTCustomMotionIDs))
        {
            if (fp->motion_id != sFTCustomMotionIDs[i]) continue;
        }
        else if ((sFTCustomBodyExtraMotionIDs[fp->fkind][i - 29] < 0) ||
                 (fp->motion_id != sFTCustomBodyExtraMotionIDs[fp->fkind][i - 29])) continue;
        if (i < 2) attack = nSCCharBuilderAttackJab;
        else if (i == 2) attack = nSCCharBuilderAttackDash;
        else if (i < 8) attack = nSCCharBuilderAttackFTilt;
        else if (i < 11) attack = nSCCharBuilderAttackUTilt;
        else if (i == 11) attack = nSCCharBuilderAttackDTilt;
        else if (i < 17) attack = nSCCharBuilderAttackFSmash;
        else if (i < 24) attack = nSCCharBuilderAttackUSmash + (i - 17);
        else if (i < 29) attack = nSCCharBuilderAttackNAir + (i - 24);
        else attack = nSCCharBuilderAttackJab;
        if ((i >= 19) && (i < 24)) sFTCustomLastAirAttack[fp->player] = attack;
        donor = slot->attacks[attack];
        if ((donor < nFTKindPlayableStart) || (donor > nFTKindPlayableEnd) || (donor == fp->fkind)) return NULL;
        return &sFTCustomMoves[donor][i];
    }
    if ((fp->motion_id == nFTCommonMotionLandingAirNull) && (sFTCustomLastAirAttack[fp->player] >= nSCCharBuilderAttackNAir))
    {
        attack = sFTCustomLastAirAttack[fp->player];
        donor = slot->attacks[attack];
        if ((donor >= nFTKindPlayableStart) && (donor <= nFTKindPlayableEnd) && (donor != fp->fkind))
            return &sFTCustomMoves[donor][24 + attack - nSCCharBuilderAttackNAir];
    }
    else sFTCustomLastAirAttack[fp->player] = -1;
    return NULL;
}

/* Retain native victim status, capture choreography and release flag timing. */
static void ftCustomMoveApplyThrow(FTStruct *fp)
{
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    const FTCustomThrowDefinition *data;
    FTThrowHitDesc *desc;
    s32 kind, donor, i;
    if ((slot == NULL) || (fp->throw_desc == NULL)) return;
    if ((fp->status_id == nFTCommonStatusCatch) || (fp->status_id == nFTCommonStatusCatchPull) ||
        (fp->status_id == nFTCommonStatusCatchWait)) kind = 0;
    else if (fp->motion_attack_id == nFTMotionAttackIDThrowF) kind = 1;
    else if (fp->motion_attack_id == nFTMotionAttackIDThrowB) kind = 2;
    else return;
    donor = slot->attacks[nSCCharBuilderAttackGrab + kind];
    if ((donor < nFTKindPlayableStart) || (donor > nFTKindPlayableEnd) || (donor == fp->fkind)) return;
    for (i = 0; i < 2; i++)
    {
        data = &sFTCustomThrowProperties[donor][kind][i];
        desc = &sFTCustomThrowDescs[fp->player][i];
        *desc = fp->throw_desc[i];
        desc->damage = data->damage;
        desc->angle = data->angle;
        desc->knockback_scale = data->knockback_scale;
        desc->knockback_weight = data->knockback_weight;
        desc->knockback_base = data->knockback_base;
        desc->element = data->element;
    }
    fp->throw_desc = sFTCustomThrowDescs[fp->player];
}

static ftMotionCommand* ftCustomMoveBuildScript(FTStruct *fp, const FTCustomMoveDefinition *move)
{
    ftMotionCommand *script;
    u32 word, op, previous_op = nFTMotionEventEnd;
    s32 i = 0, j, count, joint_id;
    if ((fp == NULL) || (fp->player >= GMCOMMON_PLAYERS_MAX)) return NULL;
    script = sFTCustomMoveScripts[fp->player];
    script[0] = ftMotionCommandEnd();
    if ((move == NULL) || (move->events == NULL) || (move->word_count <= 0) ||
        (move->word_count > FTCUSTOMMOVE_SCRIPT_WORDS)) goto invalid;
    while (i < move->word_count)
    {
        word = move->events[i];
        op = word >> 26;
        count = 1;
        switch (op)
        {
        case nFTMotionEventMakeAttackColl:
        case nFTMotionEventMakeAttackCollScaled:
            count = 5;
            if (((word >> 23) & 7) >= ARRAY_COUNT(fp->attack_colls)) goto invalid;
            joint_id = ftCustomJointResolve(fp, (word >> 13) & 127);
            if (joint_id == -1) goto invalid;
            word = (word & ~(127 << 13)) | (joint_id << 13);
            break;
        case nFTMotionEventSetAttackCollOffset:
            count = 2;
            /* fallthrough */
        case nFTMotionEventClearAttackCollID:
        case nFTMotionEventRefreshAttackCollID:
        case nFTMotionEventSetAttackCollDamage:
        case nFTMotionEventSetAttackCollSize:
        case nFTMotionEventSetAttackCollSoundLevel:
            if (((word >> 23) & 7) >= ARRAY_COUNT(fp->attack_colls)) goto invalid;
            break;
        case nFTMotionEventClearAttackCollAll:
        case nFTMotionEventSyncWait:
        case nFTMotionEventAsyncWait:
        case nFTMotionEventPauseScript:
        case nFTMotionEventEnd:
            break;
        case nFTMotionEventSetFlag1:
            if (!(move->flags & FTCUSTOMMOVE_FLAG_FLAG1)) goto invalid;
            break;
        case nFTMotionEventGoto:
            count = 2;
            if ((i != move->word_count - 3) || (previous_op != nFTMotionEventSyncWait) ||
                !(move->flags & FTCUSTOMMOVE_FLAG_LOOP) ||
                (move->events[i + 1] != 0)) goto invalid;
            break;
        default: goto invalid;
        }
        if ((i + count) > move->word_count) goto invalid;
        script[i] = word;
        for (j = 1; j < count; j++) script[i + j] = move->events[i + j];
        if (op == nFTMotionEventGoto) script[i + 1] = (uintptr_t)script;
        i += count;
        previous_op = op;
    }
    if ((script[i - 1] >> 26) != nFTMotionEventEnd) goto invalid;
    return script;
invalid:
    gFTCustomMoveValidationFailures++;
    script[0] = ftMotionCommandEnd();
    return script;
}

static sb32 ftCustomMoveSkipNativeCollision(FTStruct *fp, FTMotionScript *ms, u32 ev_kind)
{
    const FTCustomMoveDefinition *move = ftCustomMoveGetDefinition(fp);
    if ((move == NULL) ||
        ((ms != &fp->motion_scripts[0][0]) && (ms != &fp->motion_scripts[1][0]) &&
         (ms != &fp->motion_scripts[0][1]) && (ms != &fp->motion_scripts[1][1]))) return FALSE;
    switch (ev_kind)
    {
    case nFTMotionEventSetFlag1:
        if (!(move->flags & FTCUSTOMMOVE_FLAG_FLAG1)) return FALSE;
        ftMotionEventAdvance(ms, FTMotionEventDefault);
        return TRUE;
    case nFTMotionEventMakeAttackColl:
    case nFTMotionEventMakeAttackCollScaled:
        ftMotionEventAdvance(ms, FTMotionEventMakeAttack);
        return TRUE;
    case nFTMotionEventSetAttackCollOffset:
        ftMotionEventAdvance(ms, FTMotionEventSetAttackOffset);
        return TRUE;
    case nFTMotionEventClearAttackCollID:
    case nFTMotionEventClearAttackCollAll:
    case nFTMotionEventRefreshAttackCollID:
    case nFTMotionEventSetAttackCollDamage:
    case nFTMotionEventSetAttackCollSize:
    case nFTMotionEventSetAttackCollSoundLevel:
        ftMotionEventAdvance(ms, FTMotionEventDefault);
        return TRUE;
    }
    return FALSE;
}

#include "ftcustomanimation.c.inc"
#include "ftcustomcollision.c.inc"
