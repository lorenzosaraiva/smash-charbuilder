/* Compiled in ftmain's existing overlay: no new segment or linker layout.
 * No donor file, animation, status, or raw donor joint is used at runtime. */
#include <ft/ftcustommove.h>

#define FTCUSTOMMOVE_SCRIPT_WORDS (5 * FTCUSTOMMOVE_HITBOX_COUNT_MAX + 4)

/* MarioModel JointTree ordinal + nFTPartsJointCommonStart (4).
 * Left/right branches are anchored by MarioMain's slope leg roots (18/23)
 * and right item socket (17). Feet here are shoe joints, not slope roots.
 * Torso is the central body pivot used by vanilla body hitboxes. */
static const s32 sFTCustomMarioJointMap[nFTCustomJointEnumCount] =
{
    nFTPartsJointTopN, 5, 12, 10, 16, 9, 15, 20, 25, 22, 27
};

/* Normalized from CaptainMainMotion_AttackAirD; source 26 is right knee,
 * source 5 is torso. Smaller local Y offsets suit Mario's shorter limbs. */
static const FTCustomMoveDefinition sFTCustomMarioAttackAirLw =
{
    7, 18, 2,
    {
        { nFTCustomJointKneeR, 0, 14, -80, 100, 0, 0, 330,
          { 0, 45, 0 }, nGMHitElementNormal, TRUE, 3, 0, nGMHitLevelStrong, nGMHitSoundKick, FALSE },
        { nFTCustomJointTorso, 0, 14, -80, 100, 0, 0, 190,
          { 0, 0, 0 }, nGMHitElementNormal, TRUE, 3, 0, nGMHitLevelStrong, nGMHitSoundKick, FALSE }
    }
};

/* Independent storage: simultaneous Mario fighters cannot overwrite scripts. */
static ftMotionCommand sFTCustomMoveScripts[GMCOMMON_PLAYERS_MAX][FTCUSTOMMOVE_SCRIPT_WORDS];
/* Inspectable in the ELF/debugger, including release builds. */
u32 gFTCustomMoveValidationFailures;

static s32 ftCustomJointResolve(FTStruct *fp, FTCustomJointKind kind)
{
    s32 joint_id;

    if ((fp == NULL) || (fp->fkind != nFTKindMario) ||
        (kind < 0) || (kind >= nFTCustomJointEnumCount))
    {
        return -1;
    }
    joint_id = sFTCustomMarioJointMap[kind];
    if ((joint_id < 0) || (joint_id >= ARRAY_COUNT(fp->joints)) ||
        (fp->joints[joint_id] == NULL))
    {
        return -1;
    }
    return joint_id;
}

static const FTCustomMoveDefinition* ftCustomMoveGetDefinition(FTStruct *fp)
{
    if ((fp->fkind == nFTKindMario) && (fp->pkind != nFTPlayerKindDemo) &&
        (fp->player < GMCOMMON_PLAYERS_MAX) &&
        (fp->status_id == nFTCommonStatusAttackAirLw) &&
        (fp->motion_id == nFTCommonMotionAttackAirLw))
    {
        return &sFTCustomMarioAttackAirLw;
    }
    return NULL;
}

static sb32 ftCustomMoveValidateHitbox(const FTCustomHitboxDefinition *hit)
{
    return (hit->group_id >= 0) && (hit->group_id < 7) &&
        (hit->damage >= 0) && (hit->damage <= 255) &&
        (hit->angle >= -512) && (hit->angle <= 511) &&
        (hit->knockback_scale >= 0) && (hit->knockback_scale <= 1023) &&
        (hit->knockback_weight >= 0) && (hit->knockback_weight <= 1023) &&
        (hit->knockback_base >= 0) && (hit->knockback_base <= 1023) &&
        (hit->diameter > 0) && (hit->diameter <= 65535) &&
        (hit->element >= nGMHitElementNormal) && (hit->element <= nGMHitElementSleep) &&
        ((hit->can_rebound == FALSE) || (hit->can_rebound == TRUE)) &&
        (hit->hit_ground_air > 0) && (hit->hit_ground_air <= 3) &&
        (hit->shield_damage >= -128) && (hit->shield_damage <= 127) &&
        (hit->fgm_level >= 0) && (hit->fgm_level < nGMHitLevelEnumCount) &&
        (hit->fgm_kind >= 0) && (hit->fgm_kind < nGMHitSoundEnumCount) &&
        ((hit->is_scale_pos == FALSE) || (hit->is_scale_pos == TRUE));
}

static ftMotionCommand* ftCustomMoveBuildScript(FTStruct *fp, const FTCustomMoveDefinition *move)
{
    ftMotionCommand *script;
    const FTCustomHitboxDefinition *hit;
    s32 i, joint_id, cursor = 0;

    if ((fp == NULL) || (fp->player >= GMCOMMON_PLAYERS_MAX))
    {
        gFTCustomMoveValidationFailures++;
        return NULL;
    }
    script = sFTCustomMoveScripts[fp->player];
    /* Invalid definitions yield a harmless empty script, never native hitboxes. */
    script[0] = ftMotionCommandEnd();
    if ((move == NULL) || (move->hitbox_count <= 0) ||
        (move->hitbox_count > ARRAY_COUNT(fp->attack_colls)) ||
        (move->hitbox_count > FTCUSTOMMOVE_HITBOX_COUNT_MAX) ||
        (move->startup_frames < 0) || (move->startup_frames > 65535) ||
        (move->active_frames <= 0) || (move->active_frames > 65535))
    {
        gFTCustomMoveValidationFailures++;
        return script;
    }
    script[cursor++] = ftMotionCommandWaitAsync(move->startup_frames);
    for (i = 0; i < move->hitbox_count; i++)
    {
        hit = &move->hitboxes[i];
        joint_id = ftCustomJointResolve(fp, hit->joint);
        if ((joint_id == -1) || (ftCustomMoveValidateHitbox(hit) == FALSE))
        {
            gFTCustomMoveValidationFailures++;
            continue;
        }
        script[cursor++] = (hit->is_scale_pos != FALSE) ?
            ftMotionCommandMakeAttackCollScaledS1(i, hit->group_id, joint_id, hit->damage, hit->can_rebound, hit->element) :
            ftMotionCommandMakeAttackCollS1(i, hit->group_id, joint_id, hit->damage, hit->can_rebound, hit->element);
        script[cursor++] = ftMotionCommandMakeAttackCollS2(hit->diameter, hit->offset.x);
        script[cursor++] = ftMotionCommandMakeAttackCollS3(hit->offset.y, hit->offset.z);
        script[cursor++] = ftMotionCommandMakeAttackCollS4(hit->angle, hit->knockback_scale, hit->knockback_weight, hit->hit_ground_air);
        script[cursor++] = ftMotionCommandMakeAttackCollS5(hit->shield_damage, hit->fgm_level, hit->fgm_kind, hit->knockback_base);
    }
    script[cursor++] = ftMotionCommandWait(move->active_frames);
    script[cursor++] = ftMotionCommandClearAttackCollAll();
    script[cursor] = ftMotionCommandEnd();
    return script;
}

/* Keep Mario's flags, sounds and landing policy in his original script.
 * Only its hitbox events are replaced by our collision-only parallel script. */
static sb32 ftCustomMoveSkipNativeCollision(FTStruct *fp, FTMotionScript *ms, u32 ev_kind)
{
    if ((ftCustomMoveGetDefinition(fp) == NULL) ||
        ((ms != &fp->motion_scripts[0][0]) && (ms != &fp->motion_scripts[1][0])))
    {
        return FALSE;
    }
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
