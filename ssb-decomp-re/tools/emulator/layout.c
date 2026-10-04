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

#include <wp/weapon.h>
#include <it/item.h>
const u32 sSceneSmokeMechanicLayout[] = {
    __builtin_offsetof(GObj, link_next), __builtin_offsetof(WPStruct, owner_gobj),
    __builtin_offsetof(FTStruct, item_gobj), __builtin_offsetof(ITStruct, kind),
    __builtin_offsetof(ITStruct, owner_gobj), nITKindLinkBomb,
    __builtin_offsetof(FTStruct, status_vars.fox.specialhi.angle),
    __builtin_offsetof(FTStruct, percent_damage), __builtin_offsetof(FTStruct, ga), nMPKineticsAir
};
const u32 sSceneSmokeAnimationLayout[] = {
    __builtin_offsetof(DObj, rotate.vec.f), __builtin_offsetof(DObj, scale.vec.f)
};
const u32 sSceneSmokeSpecialLayout[] = {
    __builtin_offsetof(FTStruct, joints), __builtin_offsetof(FTStruct, lr),
    __builtin_offsetof(FTStruct, status_vars.ness.specialhi.pkthunder_gobj),
    __builtin_offsetof(FTStruct, status_vars.ness.specialhi.pkjibaku_delay),
    __builtin_offsetof(GObj, obj), __builtin_offsetof(GObj, user_data),
    __builtin_offsetof(DObj, translate.vec.f),
    __builtin_offsetof(WPStruct, physics.vel_air), __builtin_offsetof(SCBattleState, game_status)
};
const u32 sSceneSmokeSuperJumpLayout[] = {
    __builtin_offsetof(FTStruct, hitstatus), __builtin_offsetof(FTStruct, jumps_used),
    __builtin_offsetof(FTStruct, attr), __builtin_offsetof(FTAttributes, jumps_max),
    __builtin_offsetof(FTAttackColl, damage), __builtin_offsetof(FTAttackColl, size),
    __builtin_offsetof(FTAttackColl, angle), __builtin_offsetof(FTAttackColl, knockback_scale),
    __builtin_offsetof(FTAttackColl, knockback_weight), __builtin_offsetof(FTAttackColl, knockback_base),
    __builtin_offsetof(FTAttackColl, pos_curr)
};
const u32 sSceneSmokeSpinLayout[] = {
    __builtin_offsetof(FTStruct, status_vars.link.specialhi.spin_attack_gobj),
    __builtin_offsetof(WPStruct, kind), __builtin_offsetof(WPStruct, attack_coll.attack_state),
    __builtin_offsetof(WPStruct, attack_coll.size), __builtin_offsetof(WPStruct, lifetime),
    __builtin_offsetof(WPStruct, attack_coll.damage)
};
