/* Compiled in ftmain's overlay; no runtime donor file/script is needed. */
#include <ft/ftcustommove.h>
#include "ftcustommoves.generated.inc"

static ftMotionCommand sFTCustomMoveScripts[GMCOMMON_PLAYERS_MAX][FTCUSTOMMOVE_SCRIPT_WORDS];
u32 gFTCustomMoveValidationFailures;
static s8 sFTCustomLastAirAttack[4] = { -1, -1, -1, -1 };

static s32 ftCustomJointResolve(FTStruct *fp, FTCustomJointKind kind)
{
    s32 joint_id;
    if ((fp == NULL) || (fp->fkind < nFTKindPlayableStart) ||
        (fp->fkind > nFTKindPlayableEnd) || (kind < 0) || (kind >= nFTCustomJointEnumCount)) return -1;
    joint_id = sFTCustomJointMaps[fp->fkind][kind];
    if ((joint_id < 0) || (joint_id >= ARRAY_COUNT(fp->joints)) || (fp->joints[joint_id] == NULL)) return -1;
    return joint_id;
}

static const FTCustomMoveDefinition* ftCustomMoveGetDefinition(FTStruct *fp)
{
    SCCharBuilderSlot *slot;
    s32 slot_id, attack, i, donor;
    if ((fp == NULL) || (fp->pkind == nFTPlayerKindDemo) ||
        (fp->player >= GMCOMMON_PLAYERS_MAX) || (fp->fkind < nFTKindPlayableStart) || (fp->fkind > nFTKindPlayableEnd) ||
        ((gSCManagerSceneData.scene_curr != nSCKindVSBattle) &&
         (gSCManagerSceneData.scene_curr != nSCKind1PTrainingMode))) return NULL;
    slot_id = gSCManagerCharBuilderPlayerSlots[fp->player];
    if ((slot_id < 0) || (slot_id >= SCCHARBUILDER_SLOTS_COUNT)) return NULL;
    slot = &gSCManagerCharBuilderSlots[slot_id];
    if ((slot->is_enabled == FALSE) || (slot->body != fp->fkind)) return NULL;
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
        case nFTMotionEventGoto:
            count = 2;
            if ((i != move->word_count - 3) || (previous_op != nFTMotionEventPauseScript) ||
                (move->events[i + 1] != 0)) goto invalid;
            break;
        default: goto invalid;
        }
        if ((i + count) > move->word_count) goto invalid;
        script[i] = word;
        for (j = 1; j < count; j++) script[i + j] = move->events[i + j];
        if (op == nFTMotionEventGoto) script[i + 1] = (uintptr_t)script;
        /* Retain the shorter-limb offsets from the tested Mario aerial. */
        if ((fp->fkind == nFTKindMario) && (move == &sFTCustomMoves[nFTKindCaptain][23]) && (count == 5))
        {
            script[i + 2] = ftMotionCommandMakeAttackCollS3((joint_id == 25) ? 45 : 0, 0);
        }
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
    if ((ftCustomMoveGetDefinition(fp) == NULL) ||
        ((ms != &fp->motion_scripts[0][0]) && (ms != &fp->motion_scripts[1][0]) &&
         (ms != &fp->motion_scripts[0][1]) && (ms != &fp->motion_scripts[1][1]))) return FALSE;
    switch (ev_kind)
    {
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
