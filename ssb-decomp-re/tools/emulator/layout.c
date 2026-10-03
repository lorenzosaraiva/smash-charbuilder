/* Read actual MIPS struct offsets; keep smoke-test writes out of guessed fields. */
#include <sc/sctypes.h>
#include <sc/sccharbuilder.h>
const u32 sSceneSmokeLayout[] = {
    sizeof(SCCharBuilderSlot), __builtin_offsetof(SCCharBuilderSlot, special_n),
    __builtin_offsetof(SCBattleState, players), sizeof(SCPlayerData),
    __builtin_offsetof(SCPlayerData, pkind), __builtin_offsetof(SCPlayerData, fkind),
    __builtin_offsetof(SCBattleState, pl_count), __builtin_offsetof(SCBattleState, cp_count),
    __builtin_offsetof(SCBattleState, is_reset_players), __builtin_offsetof(SCBattleState, is_stage_select)
};

#include <ft/fighter.h>
const u32 sSceneSmokeFighterLayout[] = {
    sizeof(FTStruct), __builtin_offsetof(FTStruct, fkind), __builtin_offsetof(FTStruct, player),
    __builtin_offsetof(FTStruct, fighter_gobj), __builtin_offsetof(FTStruct, status_id),
    __builtin_offsetof(FTStruct, motion_id), __builtin_offsetof(FTStruct, attack_colls),
    sizeof(FTAttackColl), __builtin_offsetof(FTAttackColl, attack_state),
    __builtin_offsetof(FTStruct, passive_vars), sizeof(((FTStruct*)0)->passive_vars),
    __builtin_offsetof(FTStruct, player_num), __builtin_offsetof(FTStruct, physics),
    __builtin_offsetof(struct FTPhysics, vel_air), __builtin_offsetof(FTStruct, hitlag_tics), __builtin_offsetof(GObj, anim_frame)
};
