/* Only the Training display treats capture/throw windup as combo continuity.
 * Keep the real hitstun flag intact: it also controls gameplay and physics. */
void ftMainUpdateComboStats(FTStruct *fp)
{
    if (fp->is_hitstun)
    {
        return;
    }
    if (gSCManagerSceneData.scene_curr == nSCKind1PTrainingMode)
    {
        if ((fp->capture_gobj != NULL) ||
            ((fp->status_id >= nFTCommonStatusThrownDonkeyUnk) &&
             (fp->status_id <= nFTCommonStatusThrownEnd)))
        {
            return;
        }
    }
    gSCManagerBattleState->players[fp->player].combo_damage_foe = 0;
    gSCManagerBattleState->players[fp->player].combo_count_foe = 0;
}
