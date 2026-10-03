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
