/* Standalone native props: no donor rig or model-part event touches the body. */
static void *sFTCustomPropFileBase;
extern wpSamusChargeShotAttributes dWPSamusChargeShotWeaponAttributes[];
extern WPDesc dWPSamusChargeShotWeaponDesc;
static void ftCustomAnimationDrawProp(GObj *g)
{
    Gfx *prefix = DObjGetStruct(g)->user_data.p;
    if (prefix != NULL) gSPDisplayList(gSYTaskmanDLHeads[1]++, prefix);
    gcDrawDObjDLHead1(g);
}
static EFDesc sFTCustomPropEffect = {
    EFFECT_FLAG_USERDATA, 15, &sFTCustomPropFileBase,
    { nGCMatrixKindTraRotRpyRSca, nGCMatrixKindNull, 0 },
    { nGCMatrixKindNull, nGCMatrixKindNull, 0 },
    efManagerNoEjectProcUpdate, ftCustomAnimationDrawProp, 0, 0, 0, 0
};
static struct FTCustomPropState {
    FTStruct *owner; u32 player_num;
    GObj *model, *charge;
    const FTCustomSpecialAttachment *definition;
    sb32 hidden;
    u8 flags[FTPARTS_JOINT_NUM_MAX];
} sFTCustomPropStates[4];

/* Scene arenas reuse fighter addresses and restart player_num. Do not carry
 * old hidden flags or effect identities into the new allocation pool. */
void ftMainCharBuilderResetSpecialVisualsAll(void)
{
    bzero(sFTCustomPropStates, sizeof(sFTCustomPropStates));
    bzero(sFTCustomRecoveryPoses, sizeof(sFTCustomRecoveryPoses));
}

static GObj* ftCustomAnimationFindLiveEffect(GObj *wanted, GObj *owner)
{
    GObj *g;
    if (wanted == NULL) return NULL;
    for (g = gGCCommonLinks[nGCCommonLinkIDEffect]; g != NULL; g = g->link_next)
        if ((g == wanted) && (g->proc_display == ftCustomAnimationDrawProp) &&
            (efGetStruct(g) != NULL) && (efGetStruct(g)->fighter_gobj == owner)) return g;
    return NULL;
}

static void ftCustomAnimationStopProp(GObj **g)
{
    if (*g != NULL) { ftParamStopEffect(*g, efGetStruct(*g)); *g = NULL; }
}

static void ftCustomAnimationRestoreBody(FTStruct *fp, struct FTCustomPropState *state)
{
    s32 i;
    if (state->hidden)
        for (i = 4; i < FTPARTS_JOINT_NUM_MAX; i++)
            if (fp->joints[i] != NULL) fp->joints[i]->flags = state->flags[i];
    state->hidden = FALSE;
}

static GObj* ftCustomAnimationMakeProp(GObj *owner, Gfx *dl)
{
    GObj *g;
    if (dl == NULL) return NULL;
    sFTCustomPropEffect.o_dobjsetup = (intptr_t)dl;
    g = efManagerMakeEffectNoForce(&sFTCustomPropEffect);
    if (g != NULL)
    {
        efGetStruct(g)->fighter_gobj = owner;
        ftGetStruct(owner)->is_effect_attach = TRUE;
    }
    return g;
}

static void ftMainCharBuilderUpdateSpecialAttachments(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    const FTCustomSpecialAnimation *visual = ftCustomAnimationSpecialDefinition(fp);
    const FTCustomSpecialAttachment *prop = visual ? visual->attachment : NULL;
    const FTCustomSpecialAttachmentFrame *sample;
    FTCharBuilderNeutralState *neutral = ftMainCharBuilderNeutralState(fp);
    struct FTCustomPropState *state;
    FTData *data;
    FTAttributes *attr;
    FTModelPart *part;
    DObj *dobj;
    Gfx *dl, *prefix;
    s32 i, frame, level;
    Vec3f pos;
    if (fp->player >= 4) return;
    state = &sFTCustomPropStates[fp->player];
    if ((state->owner != fp) || (state->player_num != fp->player_num))
    {
        bzero(state, sizeof(*state)); state->owner = fp; state->player_num = fp->player_num;
    }
    state->model = ftCustomAnimationFindLiveEffect(state->model, g);
    state->charge = ftCustomAnimationFindLiveEffect(state->charge, g);
    ftCustomAnimationRestoreBody(fp, state);
    if ((prop != NULL) && (visual->donor != fp->fkind))
    {
        frame = ftCustomAnimationSpecialFrame(visual->clip, ftCustomMoveGetClock(fp)->frame);
        sample = &prop->frames[frame];
        if (!sample->active) prop = NULL;
    }
    else prop = NULL;
    if (prop != state->definition) { ftCustomAnimationStopProp(&state->model); state->definition = prop; }
    if (prop != NULL)
    {
        data = dFTManagerDataFiles[visual->donor];
        if ((data->p_file_main == NULL) || (*data->p_file_main == NULL)) return;
        attr = lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);
        part = NULL;
        prefix = NULL;
        if (prop->part >= 0)
        {
            part = &attr->modelparts_container->modelparts_desc[prop->joint - 4]->modelparts[prop->part][0];
            dl = ((part->flags & 15) == 1) ? ((Gfx**)part->dl)[1] : part->dl;
            if ((part->flags & 15) == 1) prefix = ((Gfx**)part->dl)[0];
        }
        else
        {
            dl = attr->commonparts_container->commonparts[0].dobjdesc[prop->joint - 4].dl;
            if ((attr->commonparts_container->commonparts[0].flags & 15) == 1) { prefix = ((Gfx**)dl)[0]; dl = ((Gfx**)dl)[1]; }
        }
        if (state->model == NULL)
        {
            state->model = ftCustomAnimationMakeProp(g, dl);
            if (state->model != NULL) DObjGetStruct(state->model)->user_data.p = prefix;
            if ((state->model != NULL) && (part != NULL))
                lbCommonAddMObjForFighterPartsDObj(DObjGetStruct(state->model), part->mobjsubs, part->costume_matanim_joints, part->main_matanim_joints, 0);
            else if (state->model != NULL)
                lbCommonAddMObjForFighterPartsDObj(DObjGetStruct(state->model),
                    attr->commonparts_container->commonparts[0].p_mobjsubs ? attr->commonparts_container->commonparts[0].p_mobjsubs[prop->joint - 4] : NULL,
                    attr->commonparts_container->commonparts[0].p_costume_matanim_joints ? attr->commonparts_container->commonparts[0].p_costume_matanim_joints[prop->joint - 4] : NULL,
                    NULL, 0);
        }
        if (state->model != NULL)
        {
            dobj = DObjGetStruct(state->model);
            pos = DObjGetStruct(g)->translate.vec.f;
            pos.x += sample->translate.z * fp->lr; pos.y += sample->translate.y; pos.z -= sample->translate.x * fp->lr;
            dobj->translate.vec.f = pos;
            dobj->rotate.vec.f = ftCustomAnimationToEuler(ftCustomAnimationMultiply(
                ftCustomAnimationFromEuler(0, fp->lr * F_CST_DTOR32(90.0F), 0),
                ftCustomAnimationFromEuler(sample->rotate.x, sample->rotate.y, sample->rotate.z)));
            dobj->scale.vec.f = sample->scale;
            if (prop->hide_body)
            {
                state->hidden = TRUE;
                for (i = 4; i < FTPARTS_JOINT_NUM_MAX; i++) if (fp->joints[i] != NULL)
                { state->flags[i] = fp->joints[i]->flags; fp->joints[i]->flags |= DOBJ_FLAG_HIDDEN; }
            }
        }
    }
    /* The held charge orb is an effect, with no weapon state or collisions. */
    if ((neutral == NULL) || (neutral->row < 14) || (neutral->row >= 16)) ftCustomAnimationStopProp(&state->charge);
    else
    {
        if (state->charge == NULL)
        {
            WPAttributes *shot = lbRelocGetFileData(WPAttributes*, *dWPSamusChargeShotWeaponDesc.p_weapon, dWPSamusChargeShotWeaponDesc.o_attributes);
            state->charge = ftCustomAnimationMakeProp(g, shot->data);
            if (state->charge != NULL) gcAddMObjAll(state->charge, shot->p_mobjsubs);
        }
        if (state->charge != NULL)
        {
            frame = (s32)ftCustomMoveGetClock(fp)->frame;
            if (frame > sFTCharBuilderActions[neutral->row].move.duration) frame = sFTCharBuilderActions[neutral->row].move.duration;
            if (frame < 0) frame = 0;
            pos = DObjGetStruct(g)->translate.vec.f;
            pos.x += fp->lr * sFTCharBuilderActions[neutral->row].spawn[frame].x;
            pos.y += sFTCharBuilderActions[neutral->row].spawn[frame].y;
            pos.z += fp->lr * sFTCharBuilderActions[neutral->row].spawn[frame].z;
            dobj = DObjGetStruct(state->charge); dobj->translate.vec.f = pos;
            level = neutral->samus_charge;
            if (level < 0) level = 0; if (level > FTSAMUS_CHARGE_MAX) level = FTSAMUS_CHARGE_MAX;
            dobj->scale.vec.f.x = dobj->scale.vec.f.y = dobj->scale.vec.f.z = dWPSamusChargeShotWeaponAttributes[level].gfx_size / WPCHARGESHOT_GFX_SIZE_DIV;
            dobj->rotate.vec.f.z -= 0.2F * fp->lr;
        }
    }
}

static void ftMainCharBuilderRestoreSpecialBody(FTStruct *fp)
{
    struct FTCustomPropState *state;
    if (fp->player >= 4) return;
    state = &sFTCustomPropStates[fp->player];
    if ((state->owner == fp) && (state->player_num == fp->player_num)) ftCustomAnimationRestoreBody(fp, state);
}
