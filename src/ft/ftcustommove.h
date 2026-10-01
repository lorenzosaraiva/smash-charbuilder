#ifndef _FTCUSTOMMOVE_H_
#define _FTCUSTOMMOVE_H_

#include <ft/fttypes.h>

/* Body locations, never a donor's skeleton indices. */
typedef enum FTCustomJointKind
{
    nFTCustomJointRoot,
    nFTCustomJointTorso,
    nFTCustomJointHead,
    nFTCustomJointHandL,
    nFTCustomJointHandR,
    nFTCustomJointElbowL,
    nFTCustomJointElbowR,
    nFTCustomJointKneeL,
    nFTCustomJointKneeR,
    nFTCustomJointFootL,
    nFTCustomJointFootR,
    nFTCustomJointGrabPoint,
    nFTCustomJointEnumCount
} FTCustomJointKind;

/* Matches FTStruct.attack_colls, not the event's wider 3-bit attack ID. */
#define FTCUSTOMMOVE_HITBOX_COUNT_MAX 4

typedef struct FTCustomHitboxDefinition
{
    FTCustomJointKind joint;
    s32 group_id;
    s32 damage;
    s32 angle;
    s32 knockback_scale;
    s32 knockback_weight;
    s32 knockback_base;
    s32 diameter;               /* Motion-event size; FTAttackColl.size is half this. */
    Vec3h offset;               /* Signed local joint coordinates in engine units. */
    GMHitElement element;
    sb32 can_rebound;
    s32 hit_ground_air;         /* Existing event mask: bit 0 air, bit 1 ground. */
    s32 shield_damage;
    GMAttackLevel fgm_level;
    GMAttackSound fgm_kind;
    sb32 is_scale_pos;
} FTCustomHitboxDefinition;

typedef struct FTCustomMoveDefinition
{
    const ftMotionCommand *events; /* Collision-only events with semantic joints. */
    s32 word_count;
} FTCustomMoveDefinition;

/* Numeric gameplay only: the victim's status remains the body's native one. */
typedef struct FTCustomThrowDefinition
{
    s32 damage;
    s32 angle;
    s32 knockback_scale;
    s32 knockback_weight;
    s32 knockback_base;
    s32 element;
} FTCustomThrowDefinition;

#endif
