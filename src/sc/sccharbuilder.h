#ifndef _SCCHARBUILDER_H_
#define _SCCHARBUILDER_H_

#include <ssb_types.h>

#define SCCHARBUILDER_SLOTS_COUNT 4
#define SCCHARBUILDER_ATTACKS_COUNT 13

typedef enum SCCharBuilderAttack
{
    nSCCharBuilderAttackJab,
    nSCCharBuilderAttackDash,
    nSCCharBuilderAttackFTilt,
    nSCCharBuilderAttackUTilt,
    nSCCharBuilderAttackDTilt,
    nSCCharBuilderAttackFSmash,
    nSCCharBuilderAttackUSmash,
    nSCCharBuilderAttackDSmash,
    nSCCharBuilderAttackNAir,
    nSCCharBuilderAttackFAir,
    nSCCharBuilderAttackBAir,
    nSCCharBuilderAttackUAir,
    nSCCharBuilderAttackDAir

} SCCharBuilderAttack;

typedef struct SCCharBuilderSlot
{
    u8 is_enabled;
    u8 body;
    u8 attacks[SCCHARBUILDER_ATTACKS_COUNT];
    u8 special_hi;
    u8 special_lw;

} SCCharBuilderSlot;

extern SCCharBuilderSlot gSCManagerCharBuilderSlots[SCCHARBUILDER_SLOTS_COUNT];
/* -1 is vanilla; 0..3 selects a preset independently for each controller/CPU. */
extern s8 gSCManagerCharBuilderPlayerSlots[4];

#endif
