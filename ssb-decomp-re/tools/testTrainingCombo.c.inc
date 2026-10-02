/* Exercise the production counter update for native and creator fighters. */
static struct
{
    struct { s32 combo_damage_foe, combo_count_foe; } players[4];
} sTestComboBattleState;
static __typeof__(sTestComboBattleState) *gSCManagerBattleState = &sTestComboBattleState;
#include "../src/ft/fttrainingcombo.c.inc"

static s32 testTrainingCombo(void)
{
    FTStruct fp = {0};
    GObj captor = {0};
    s32 body, player, status, frame, enabled;
    const s32 captures[] = { nFTCommonStatusCapturePulled, nFTCommonStatusCaptureWait,
        nFTCommonStatusCaptureKirby, nFTCommonStatusCaptureWaitKirby,
        nFTCommonStatusCaptureYoshi, nFTCommonStatusYoshiEgg, nFTCommonStatusCaptureCaptain };
    const s32 scenes[] = { nSCKindVSBattle, nSCKind1PGame, nSCKindTitle };
    gSCManagerSceneData.scene_curr = nSCKind1PTrainingMode;
    for (body = 0; body < 12; body++)
    for (enabled = 0; enabled < 2; enabled++)
    for (player = 0; player < 4; player++)
    {
        fp.fkind = body; fp.player = player;
        fp.pkind = player == 0 ? nFTPlayerKindMan : nFTPlayerKindCom;
        gSCManagerCharBuilderSlots[player].is_enabled = enabled;
        /* A two-hit attack leads directly into a grab. */
        sTestComboBattleState.players[player].combo_damage_foe = 21;
        sTestComboBattleState.players[player].combo_count_foe = 2;
        fp.status_id = nFTCommonStatusDamageAir1; fp.is_hitstun = TRUE;
        fp.capture_gobj = NULL;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 2);
        fp.is_hitstun = FALSE; fp.capture_gobj = &captor;
        for (status = 0; status < ARRAY_COUNT(captures); status++)
        {
            fp.status_id = captures[status];
            for (frame = 0; frame < 120; frame++) ftMainUpdateComboStats(&fp);
            CHECK(sTestComboBattleState.players[player].combo_count_foe == 2);
            CHECK(sTestComboBattleState.players[player].combo_damage_foe == 21);
            CHECK(!fp.is_hitstun && fp.capture_gobj == &captor);
        }
        /* Cover every native cargo/throw phase, even between capture links. */
        fp.capture_gobj = NULL;
        for (status = nFTCommonStatusThrownDonkeyUnk; status <= nFTCommonStatusThrownEnd; status++)
        {
            fp.status_id = status; ftMainUpdateComboStats(&fp);
            CHECK(sTestComboBattleState.players[player].combo_count_foe == 2);
            CHECK(sTestComboBattleState.players[player].combo_damage_foe == 21);
        }
        /* Throw damage is added by the native stats path before release. */
        sTestComboBattleState.players[player].combo_damage_foe += 12;
        sTestComboBattleState.players[player].combo_count_foe++;
        fp.status_id = nFTCommonStatusDamageAir1; fp.is_hitstun = TRUE;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 3);
        CHECK(sTestComboBattleState.players[player].combo_damage_foe == 33);
        /* Recovery, or escape without further hitstun, ends the combo. */
        fp.is_hitstun = FALSE; fp.status_id = nFTCommonStatusFall;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 0);
        CHECK(sTestComboBattleState.players[player].combo_damage_foe == 0);
        /* An escaped grab clears its capture link without a damaging throw. */
        fp.capture_gobj = &captor; fp.status_id = nFTCommonStatusCaptureWait;
        sTestComboBattleState.players[player].combo_count_foe = 2;
        sTestComboBattleState.players[player].combo_damage_foe = 21;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 2);
        fp.capture_gobj = NULL; fp.status_id = nFTCommonStatusDamageAir1;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 0);
        CHECK(sTestComboBattleState.players[player].combo_damage_foe == 0);
        /* A bare grab does not invent a hit or damage. */
        fp.capture_gobj = &captor; fp.status_id = nFTCommonStatusCaptureWait;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 0);
        CHECK(sTestComboBattleState.players[player].combo_damage_foe == 0);
        /* Catching someone must not preserve the attacker's own victim stats. */
        fp.capture_gobj = NULL; fp.catch_gobj = &captor; fp.status_id = nFTCommonStatusCatchWait;
        sTestComboBattleState.players[player].combo_count_foe = 2;
        sTestComboBattleState.players[player].combo_damage_foe = 21;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[player].combo_count_foe == 0);
        CHECK(sTestComboBattleState.players[player].combo_damage_foe == 0);
        fp.catch_gobj = NULL;
    }
    /* Updating one victim leaves the other three counters alone. */
    for (player = 0; player < 4; player++)
    {
        sTestComboBattleState.players[player].combo_count_foe = player + 1;
        sTestComboBattleState.players[player].combo_damage_foe = 10 + player;
    }
    fp.player = 2; fp.status_id = nFTCommonStatusWait;
    ftMainUpdateComboStats(&fp);
    for (player = 0; player < 4; player++)
    {
        CHECK(sTestComboBattleState.players[player].combo_count_foe == (player == 2 ? 0 : player + 1));
        CHECK(sTestComboBattleState.players[player].combo_damage_foe == (player == 2 ? 0 : 10 + player));
    }
    /* Other scenes keep vanilla reset behavior, including during capture. */
    fp.capture_gobj = &captor; fp.status_id = nFTCommonStatusShouldered;
    for (status = 0; status < ARRAY_COUNT(scenes); status++)
    {
        gSCManagerSceneData.scene_curr = scenes[status];
        sTestComboBattleState.players[2].combo_count_foe = 3;
        sTestComboBattleState.players[2].combo_damage_foe = 33;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[2].combo_count_foe == 0);
        CHECK(sTestComboBattleState.players[2].combo_damage_foe == 0);
        fp.is_hitstun = TRUE;
        sTestComboBattleState.players[2].combo_count_foe = 3;
        sTestComboBattleState.players[2].combo_damage_foe = 33;
        ftMainUpdateComboStats(&fp);
        CHECK(sTestComboBattleState.players[2].combo_count_foe == 3);
        CHECK(sTestComboBattleState.players[2].combo_damage_foe == 33);
        fp.is_hitstun = FALSE;
    }
    return 0;
}
