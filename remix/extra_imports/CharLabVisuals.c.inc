extern void gcParseMObjMatAnimJoint(MObj*);
/* Original material setup for independent EF props. Remix costume hooks
 * require a fighter GObj and cannot accept these owned effect objects. */
void ccPropMaterials
(
    DObj *dobj,
    MObjSub **mobjsubs,
    AObjEvent32 **costume_matanim_joints,
    AObjEvent32 **main_matanim_joints,
    f32 anim_frame
)
{
    if (mobjsubs != NULL)
    {
        MObjSub *mobjsub = *mobjsubs;

        while (mobjsub != NULL)
        {
            MObj *mobj = gcAddMObjForDObj(dobj, mobjsub);

            if (costume_matanim_joints != NULL)
            {
                AObjEvent32 *costume_matanim_joint = *costume_matanim_joints;

                if (costume_matanim_joint != NULL)
                {
                    gcAddMObjMatAnimJoint(mobj, costume_matanim_joint, anim_frame);
                    gcParseMObjMatAnimJoint(mobj);
                    gcPlayMObjMatAnim(mobj);
                    gcRemoveAObjFromMObj(mobj);
                }
                costume_matanim_joints++;
            }
            if (main_matanim_joints != NULL)
            {
                AObjEvent32 *main_matanim_joint = *main_matanim_joints;

                if (main_matanim_joint != NULL)
                {
                    gcAddMObjMatAnimJoint(mobj, main_matanim_joint, 0.0F);
                    gcParseMObjMatAnimJoint(mobj);
                    gcPlayMObjMatAnim(mobj);
                }
                main_matanim_joints++;
            }
            mobjsubs++;
            mobjsub = *mobjsubs;
        }
    }
}

/* Borrowed visuals own their objects, never the body's model-part tables. */
typedef struct FTCustomSpecialAttachmentFrame { Vec3f rotate, translate, scale; sb32 active; } FTCustomSpecialAttachmentFrame;
typedef struct FTCustomSpecialAttachment { const FTCustomSpecialAttachmentFrame *frames; s32 joint, part; sb32 hide_body; } FTCustomSpecialAttachment;
typedef struct CCVisualDefinition {
    const FTCustomMoveDefinition *move;
    const CCAnimationRecord *clip;
    const ftMotionCommand *visual;
    s32 donor;
    const FTCustomSpecialAttachment *attachment;
    s32 family; /* 1 Up B, 2 Down B, 3 Neutral B */
} CCVisualDefinition;
static const CCVisualDefinition* ccPairVisual(FTStruct*);
#include "../build/char_creator/runtime/visual-data.inc"

typedef struct CCVisualState {
    FTStruct *owner;
    GObj *fighter, *model, *charge, *effect;
    u32 generation;
    const CCVisualDefinition *definition;
    const FTCustomSpecialAttachment *prop;
    const ftMotionCommand *script;
    f32 frame, wait;
    sb32 hidden;
    u8 flags[FTPARTS_JOINT_NUM_MAX];
    alSoundEffect *loop, *voice;
    sb32 held_charge;
    sb32 charge_flash;
    s32 model_part;
    u16 ball_palette[16] __attribute__((aligned(8)));
    void *ball_palettes[1];
} CCVisualState;
static CCVisualState sCCVisualStates[4];
static FTStruct *sCCVisualContinuingOwner;
u32 gCCVisualModels, gCCVisualEffects, gCCVisualSounds, gCCVisualStops;

static const CCVisualDefinition* ccVisualDefinition(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    CCSpecialClock *special = ccSpecialClock(fp);
    const FTCustomMoveDefinition *move = clock ? clock->move : NULL;
    s32 i;
    if (fp->player >= 4 || ftCustomMoveGetSlot(fp) == NULL) return NULL;
    if (sCCPairDonors[fp->player] >= 0) return ccPairVisual(fp);
    if (special != NULL && special->path == NULL)
        for (i = 0; i < ARRAY_COUNT(sFTCharBuilderSpecialTimings); i++)
            if (sFTCharBuilderSpecialTimings[i].donor == special->donor && sFTCharBuilderSpecialTimings[i].motion == special->motion)
                move = &sFTCharBuilderSpecialTimings[i].move;
    for (i = 0; i < ARRAY_COUNT(sFTCustomSpecialAnimations); i++)
        if (move == sFTCustomSpecialAnimations[i].move && sFTCustomSpecialAnimations[i].donor != ccBodyKind(fp))
            return &sFTCustomSpecialAnimations[i];
    return NULL;
}

DObj* ftMainCharBuilderGetSpecialVisualJoint(FTStruct *fp, s32 donor, s32 joint)
{
    s32 body = ccBodyKind(fp), role, i;
    const FTCustomAnimationRig *rig;
    if ((u32)body >= 12 || (u32)donor >= 12) return fp->joints[0];
    if (body == donor && (u32)joint < FTPARTS_JOINT_NUM_MAX && fp->joints[joint]) return fp->joints[joint];
    rig = &sFTCustomAnimationRigs[body];
    for (role = 0; role < 24; role++) if (sFTCustomAnimationSemanticJoints[donor][role] == joint)
        for (i = 0; i < rig->count; i++)
            if (rig->bones[i].role == role && fp->joints[rig->bones[i].joint]) return fp->joints[rig->bones[i].joint];
    return fp->joints[0];
}

#include "../build/char_creator/runtime/visual-effects.inc"
extern void *ccVisualMainFile(s32);
static void ccVisualEffectUpdate(GObj*);

static GObj* ccVisualLive(GObj *wanted, GObj *fighter)
{
    GObj *g;
    if (wanted == NULL) return NULL;
    for (g = gGCCommonLinks[nGCCommonLinkIDEffect]; g != NULL; g = g->link_next)
        if (g == wanted && efGetStruct(g) && efGetStruct(g)->fighter_gobj == fighter &&
            efGetStruct(g)->proc_update == ccVisualEffectUpdate) return g;
    return NULL;
}

static sb32 ccVisualOwnerLive(CCVisualState *s)
{
    GObj *g;
    if (s->fighter == NULL) return FALSE;
    for (g = gGCCommonLinks[nGCCommonLinkIDFighter]; g != NULL; g = g->link_next)
        if (g == s->fighter) return ftGetStruct(g) == s->owner && s->owner->player_num == s->generation;
    return FALSE;
}

static void ccVisualRestore(CCVisualState *s)
{
    s32 i;
    if (s->hidden && ccVisualOwnerLive(s))
    {
        ccSuspendJoints(s->owner);
        for (i = 4; i < FTPARTS_JOINT_NUM_MAX; i++)
            if (s->owner->joints[i]) s->owner->joints[i]->flags = s->flags[i];
        ccResumeJoints(s->owner);
    }
    s->hidden = FALSE;
}

static void ccVisualEject(CCVisualState *s, GObj **object)
{
    GObj *g = ccVisualLive(*object, s->fighter);
    if (g) { ftParamStopEffect(g, efGetStruct(g)); gCCVisualStops++; }
    *object = NULL;
}

static void ccVisualClear(CCVisualState *s)
{
    ccVisualRestore(s);
    ccVisualEject(s, &s->model); ccVisualEject(s, &s->charge); ccVisualEject(s, &s->effect);
    if (ccVisualOwnerLive(s))
    {
        if (s->loop && s->owner->p_loop_sfx == s->loop) ftParamStopLoopSFX(s->owner);
        if (s->voice && s->owner->p_voice == s->voice) ftParamStopVoice(s->owner);
    }
    s->loop = s->voice = NULL; s->prop = NULL; s->definition = NULL; s->script = NULL;
    s->held_charge = FALSE;
}

static CCVisualState* ccVisualState(FTStruct *fp)
{
    CCVisualState *s;
    if (fp->player >= 4) return NULL;
    s = &sCCVisualStates[fp->player];
    if (s->owner != fp || s->generation != fp->player_num)
    {
        ccVisualClear(s); memset(s, 0, sizeof(*s));
        s->owner = fp; s->fighter = fp->fighter_gobj; s->generation = fp->player_num;
    }
    return s;
}

static void ccVisualReset(void)
{
    s32 i;
    sCCVisualContinuingOwner = NULL;
    for (i = 0; i < 4; i++) { ccVisualClear(&sCCVisualStates[i]); memset(&sCCVisualStates[i], 0, sizeof(CCVisualState)); }
}

static void ccVisualStatusChanging(GObj *g, s32 next)
{
    FTStruct *fp = ftGetStruct(g);
    CCVisualState *s;
    if (fp->player >= 4) return;
    s = &sCCVisualStates[fp->player];
    if (s->owner != fp || s->generation != fp->player_num) return;
    if (sFTCharBuilderNeutralStartingOwner == fp && sCCVisualContinuingOwner == fp) return;
    /* Common statuses include damage, capture, death, cliff and recovery.
     * Same-family unique phase changes can preserve native attached effects. */
    ccVisualRestore(s);
    if (next < 0xDC) ccVisualClear(s);
}

static void ccVisualStart(FTStruct *fp, f32 frame)
{
    CCVisualState *s = ccVisualState(fp);
    const CCVisualDefinition *def = ccVisualDefinition(fp);
    if (!s) return;
    sCCVisualContinuingOwner = NULL;
    if (s->definition && (!def || s->definition->donor != def->donor || s->definition->family != def->family)) ccVisualClear(s);
    s->definition = def; s->script = def ? def->visual : NULL;
    s->wait = 0; s->frame = frame - 1.0F;
}

u32 ccVisualPreserve(FTStruct *fp, const FTCustomMoveDefinition *move)
{
    const CCVisualDefinition *current = ccVisualDefinition(fp), *next;
    CCVisualState *s;
    s32 i;
    sCCVisualContinuingOwner = NULL;
    if (!current || current->family != 3 || fp->player >= 4) return 0;
    s = &sCCVisualStates[fp->player];
    if (s->owner != fp || s->generation != fp->player_num || s->definition != current) return 0;
    for (i = 0; i < ARRAY_COUNT(sFTCustomSpecialAnimations); i++)
    {
        next = &sFTCustomSpecialAnimations[i];
        if (next->move == move && next->donor == current->donor && next->family == current->family)
        {
            sCCVisualContinuingOwner = fp;
            return FTSTATUS_PRESERVE_EFFECT | FTSTATUS_PRESERVE_LOOPSFX;
        }
    }
    return 0;
}

static GObj* ccVisualOwn(GObj *g, GObj *fighter)
{
    if (g)
    {
        efGetStruct(g)->fighter_gobj = fighter;
        efGetStruct(g)->proc_update = ccVisualEffectUpdate;
        ftGetStruct(fighter)->is_effect_attach = TRUE;
    }
    return g;
}

static void ccVisualEffectUpdate(GObj *g)
{
    s32 i;
    if (ccPairEffectLive(g)) { efManagerNoEjectProcUpdate(g); return; }
    for (i = 0; i < 4; i++)
    {
        CCVisualState *s = &sCCVisualStates[i];
        if (s->model == g || s->charge == g || s->effect == g)
        {
            if (ccVisualOwnerLive(s) && ccVisualDefinition(s->owner)) { efManagerNoEjectProcUpdate(g); return; }
            ccVisualRestore(s); break;
        }
    }
    ftParamStopEffect(g, efGetStruct(g)); gCCVisualStops++;
}

static void ccVisualDrawProp(GObj *g)
{
    Gfx *prefix = DObjGetStruct(g)->user_data.p;
    /* These are fighter part DLs, not particle DLs. Native Samus draws the
     * palettized beam on head 0 inside a two-cycle fighter pass. Sharing head
     * 1 with its glow/particles changes their texture combiner and subsequent
     * translucent stage layers. Match the native pass AND its exit state. */
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_2CYCLE);
    gDPSetTextureLUT(gSYTaskmanDLHeads[0]++, G_TT_NONE);
    gDPSetAlphaCompare(gSYTaskmanDLHeads[0]++, G_AC_NONE);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_PASS, G_RM_AA_ZB_OPA_SURF2);
    gSPGeometryMode(gSYTaskmanDLHeads[0]++, G_CULL_BOTH | G_FOG | G_TEXTURE_GEN | G_TEXTURE_GEN_LINEAR | G_LOD,
        G_ZBUFFER | G_SHADE | G_CULL_BACK | G_LIGHTING | G_SHADING_SMOOTH);
    /* Stone supplies its own diffuse/ambient colors, but assumes the native
     * fighter pass has selected one light and installed the stage direction.
     * Effects can leave another light count/direction behind. Install the
     * direction before the mesh's light-color commands, not only on exit. */
    ftDisplayLightsDrawReflect(&gSYTaskmanDLHeads[0], gMPCollisionLightAngleX, gMPCollisionLightAngleY);
    mpCollisionSetLightColorGetAlpha(&gSYTaskmanDLHeads[0]);
    gDPSetFogColor(gSYTaskmanDLHeads[0]++, 0, 0, 0, 0);
    if (prefix) gSPDisplayList(gSYTaskmanDLHeads[0]++, prefix);
    gcDrawDObjDLHead0(g);
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);
    gDPSetTextureLUT(gSYTaskmanDLHeads[0]++, G_TT_NONE);
    gDPSetAlphaCompare(gSYTaskmanDLHeads[0]++, G_AC_NONE);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_ZB_OPA_SURF, G_RM_AA_ZB_OPA_SURF2);
    ftDisplayLightsDrawReflect(&gSYTaskmanDLHeads[0], gMPCollisionLightAngleX, gMPCollisionLightAngleY);
}
static void *sCCPropBase;
static EFDesc sCCPropDesc = { EFFECT_FLAG_USERDATA, 15, &sCCPropBase,
    { nGCMatrixKindTraRotRpyRSca, nGCMatrixKindNull, 0 }, { nGCMatrixKindNull, nGCMatrixKindNull, 0 },
    efManagerNoEjectProcUpdate, ccVisualDrawProp, 0, 0, 0, 0 };

static GObj* ccVisualMakeProp(GObj *fighter, Gfx *dl)
{
    GObj *g;
    if (!dl) return NULL;
    sCCPropDesc.o_dobjsetup = (intptr_t)dl;
    g = ccVisualOwn(efManagerMakeEffectNoForce(&sCCPropDesc), fighter);
    if (g) gCCVisualModels++;
    return g;
}

/* Private CI4 palette: preserve the source ball's shading and silhouette,
 * with the receiving body's color. Never edit shared donor texture data. */
void ccVisualBallColor(CCVisualState *s, DObj *dobj, s32 body)
{
    static const u8 colors[12][3] = {
        {255,64,48}, {224,160,96}, {144,88,48}, {240,160,48},
        {64,192,64}, {64,176,72}, {64,200,80}, {96,112,224},
        {255,144,192}, {255,224,48}, {255,176,208}, {224,64,64}
    };
    MObj *m = dobj->mobj;
    const u16 *source;
    s32 i, r, g, b, shade;
    if ((u32)body >= 12 || !m || !m->sub.palettes) return;
    source = m->sub.palettes[(s32)m->palette_id];
    if (!source) return;
    for (i = 0; i < 16; i++)
    {
        r = (source[i] >> 11) & 31; g = (source[i] >> 6) & 31; b = (source[i] >> 1) & 31;
        shade = r > g ? r : g; if (b > shade) shade = b;
        s->ball_palette[i] = ((shade*colors[body][0]/255) << 11) |
            ((shade*colors[body][1]/255) << 6) | ((shade*colors[body][2]/255) << 1) | (source[i] & 1);
    }
    s->ball_palettes[0] = s->ball_palette;
    m->sub.palettes = s->ball_palettes; m->palette_id = 0;
}

static void ccVisualFalconEffect(GObj *g, sb32 kick)
{
    FTStruct *fp = ftGetStruct(g);
    CCVisualState *s = ccVisualState(fp);
    u32 *flag = kick ? &fp->motion_vars.flags.flag2 : &fp->motion_vars.flags.flag0;
    if (!s || !ccVisualDefinition(fp)) return;
    s->effect = ccVisualLive(s->effect, g);
    if (!s->effect && *flag == 1)
    {
        if (sCCVisualFiles[kick ? 1 : 2]) s->effect = ccVisualOwn(kick ? ccfxCaptainFalconKick(g) : ccfxCaptainFalconPunch(g), g);
        if (s->effect) gCCVisualEffects++;
        *flag = 0;
    }
    else if (s->effect && *flag == (kick ? 2 : 1))
    { ccVisualEject(s, &s->effect); *flag = kick ? 0 : 2; }
}

static void ccVisualCutterEffect(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    CCVisualState *s = ccVisualState(fp);
    s32 flag;
    if (!s || !ccVisualDefinition(fp)) return;
    s->effect = ccVisualLive(s->effect, g);
    if (fp->motion_vars.flags.flag1) { ccVisualEject(s, &s->effect); fp->motion_vars.flags.flag1 = 0; }
    flag = fp->motion_vars.flags.flag2;
    if (flag) ccVisualEject(s, &s->effect);
    if (sCCVisualFiles[0]) switch (flag)
    {
    case 2: s->effect = ccfxKirbyCutterDraw(g); break;
    case 3: s->effect = ccfxKirbyCutterUp(g); break;
    case 4: s->effect = ccfxKirbyCutterDown(g); break;
    case 5: s->effect = ccfxKirbyCutterTrail(g); break;
    }
    if (s->effect && flag >= 2 && flag <= 5) { ccVisualOwn(s->effect, g); gCCVisualEffects++; }
    fp->motion_vars.flags.flag2 = 0;
}

static s32 ccVisualFrame(const CCAnimationRecord *clip, f32 time)
{
    s32 frame = time < 0 ? 0 : (s32)time;
    if (clip->loop_period > 0 && frame >= clip->loop_start) frame = clip->loop_start + (frame-clip->loop_start)%clip->loop_period;
    if (frame >= clip->count) frame = clip->count-1;
    return frame;
}

static void ccVisualScript(GObj *g, CCVisualState *s, f32 time)
{
    FTStruct *fp = ftGetStruct(g);
    s32 limit = 512, op, joint, i;
    u32 value;
    Vec3f offset, scatter;
    const FTMotionEventMakeEffect *effect;
    DObj *part;
    while (s->script && limit-- > 0)
    {
        value = *s->script; op = value >> 26;
        if (op == nFTMotionEventAsyncWait)
        { s->wait = value & 0x3FFFFFF; if (time < s->wait) break; s->script++; continue; }
        if (op == nFTMotionEventEnd) { s->script = NULL; break; }
        value &= 0x3FFFFFF;
        switch (op)
        {
        case nFTMotionEventPlayFGMStoreInfo:
            if (!fp->is_muted)
            {
                fp->p_sfx = func_800269C0_275C0(value);
                fp->sfx_id = fp->p_sfx ? fp->p_sfx->sfx_id : 0;
                gCCVisualSounds++;
            }
            break;
        case nFTMotionEventPlayFGM:
            if (!fp->is_muted) { func_800269C0_275C0(value); gCCVisualSounds++; } break;
        case nFTMotionEventPlayVoiceStoreInfo:
            if (!fp->is_muted) { ftParamPlayVoice(fp, value); s->voice = fp->p_voice; gCCVisualSounds++; } break;
        case nFTMotionEventPlayLoopSFXStoreInfo: case nFTMotionEventPlayLoopVoiceStoreInfo:
            if (!fp->is_muted) { ftParamPlayLoopSFX(fp, value); s->loop = fp->p_loop_sfx; gCCVisualSounds++; } break;
        case nFTMotionEventStopLoopSFX: ftParamStopLoopSFX(fp); s->loop = NULL; break;
        case nFTMotionEventMakeRumble:
            ftParamMakeRumble(fp, value & 0x1FFF, value >> 13); break;
        case nFTMotionEventEffect:
            effect = (const FTMotionEventMakeEffect*)s->script;
            offset.x = effect->s2.off_x; offset.y = effect->s2.off_y; offset.z = effect->s3.off_z;
            scatter.x = effect->s3.rng_x; scatter.y = effect->s4.rng_y; scatter.z = effect->s4.rng_z;
            joint = -1;
            if (effect->s1.joint_id != 127 && effect->s1.joint_id != -1)
            {
                part = ftMainCharBuilderGetSpecialVisualJoint(fp, s->definition->donor, effect->s1.joint_id);
                for (i = 0; i < FTPARTS_JOINT_NUM_MAX; i++) if (fp->joints[i] == part) { joint = i; break; }
            }
            if (!fp->is_effect_skip) ftParamMakeEffect(g, effect->s1.effect_id, joint, &offset, &scatter, fp->lr, FALSE, effect->s1.flag);
            s->script += sizeof(FTMotionEventMakeEffect)/sizeof(ftMotionCommand); continue;
        default: s->script = NULL; gFTCustomMoveValidationFailures++; continue;
        }
        s->script++;
    }
    if (limit <= 0) { s->script = NULL; gFTCustomMoveValidationFailures++; }
}

static void ccVisualTick(GObj *g)
{
    FTStruct *fp = ftGetStruct(g);
    /* SetStatus advances a safe body pose before installing the next donor
     * clock. That bootstrap is not an interruption or a donor visual frame. */
    if (sFTCharBuilderNeutralStartingOwner == fp) return;
    CCVisualState *s = ccVisualState(fp);
    const CCVisualDefinition *def = ccVisualDefinition(fp);
    const FTCustomSpecialAttachment *prop;
    const FTCustomSpecialAttachmentFrame *sample;
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    CCSpecialClock *special = ccSpecialClock(fp);
    FTCharBuilderNeutralState *neutral = ftMainCharBuilderNeutralState(fp);
    FTAttributes *attr; FTData *data; FTModelPart *part = NULL;
    DObj *dobj; Gfx *dl, *prefix = NULL;
    f32 time = special ? special->frame : clock ? clock->frame : 0;
    s32 frame, i, level, model_part;
    sb32 ball;
    Vec3f pos;
    if (!s) return;
    /* Stored Giant Punch belongs to the neutral sidecar, including while
     * walking/attacking. Native color reset only reads the body's union.
     * Keep the source script running; restarting it each tick prevents blink. */
    {
        SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
        FTCharBuilderNeutralState *stored = &sFTCharBuilderNeutralStates[fp->player];
        sb32 full = slot && slot->special_n == nSCCharBuilderNeutralGiantPunch &&
            ccBodyKind(fp) != nFTKindDonkey && stored->owner == fp &&
            stored->generation == fp->player_num && stored->body == ccBodyKind(fp) &&
            stored->dk_charge == FTDONKEY_GIANTPUNCH_CHARGE_MAX;
        if (full)
        {
            if (fp->colanim.colanim_id != nGMColAnimFighterCommonSpecialNCharge)
                ftParamCheckSetFighterColAnimID(g, nGMColAnimFighterCommonSpecialNCharge, 0);
            s->charge_flash = TRUE;
        }
        else if (s->charge_flash)
        {
            s->charge_flash = FALSE;
            if (fp->colanim.colanim_id == nGMColAnimFighterCommonSpecialNCharge)
                ftParamResetStatUpdateColAnim(g);
        }
    }
    if (!def) { ccVisualClear(s); return; }
    if (s->definition != def || time < s->frame) ccVisualStart(fp, time);
    s->frame = time;
    ccSuspendJoints(fp);
    ccVisualScript(g, s, time);
    s->model = ccVisualLive(s->model, g); s->charge = ccVisualLive(s->charge, g);
    ccVisualRestore(s);
    ccSuspendJoints(fp);
    prop = def->attachment;
    frame = ccVisualFrame(def->clip, time);
    sample = prop ? &prop->frames[frame] : NULL;
    ball = def->donor == nFTKindSamus && def->family == 2 && prop && prop->hide_body;
    model_part = prop ? prop->part : -1;
    if (ball && (frame < 10 || frame >= 43)) model_part = 1;
    if (def->donor == nFTKindSamus && def->family == 4 && fp->status_id == nFTCommonStatusCatch && sCCVisualFiles[3])
    {
        /* Preserve the native glow tree/materials with a source joint-23
         * root rather than attaching it to the receiving body's joint 23. */
        const FTCustomSpecialAttachmentFrame *beam;
        s->effect = ccVisualLive(s->effect, g);
        if (!s->effect)
        {
            s->effect = ccVisualOwn(efManagerMakeEffectNoForce(&sCCSamusGrappleBeamEffectDesc), g);
            if (s->effect) gCCVisualEffects++;
        }
        i = time < 0 ? 0 : (s32)time;
        if (i >= ARRAY_COUNT(sCCSamusTetherGlow)) i = ARRAY_COUNT(sCCSamusTetherGlow)-1;
        beam = &sCCSamusTetherGlow[i];
        if (s->effect)
        {
            dobj = DObjGetStruct(s->effect); pos = DObjGetStruct(g)->translate.vec.f;
            pos.x += beam->translate.z*fp->lr; pos.y += beam->translate.y; pos.z -= beam->translate.x*fp->lr;
            dobj->translate.vec.f = pos; dobj->scale.vec.f = beam->scale;
            dobj->rotate.vec.f = ftCustomAnimationToEuler(ftCustomAnimationMultiply(
                ftCustomAnimationFromEuler(0, fp->lr*F_CST_DTOR32(90.0F), 0),
                ftCustomAnimationFromEuler(beam->rotate.x, beam->rotate.y, beam->rotate.z)));
        }
    }
    if (sample && !sample->active) prop = NULL;
    if (s->prop != prop || (prop && s->model_part != model_part))
    { ccVisualEject(s, &s->model); s->prop = prop; s->model_part = model_part; }
    if (prop && ccVisualMainFile(def->donor))
    {
        data = dFTManagerDataFiles[def->donor];
        attr = (FTAttributes*)((uintptr_t)ccVisualMainFile(def->donor)+(uintptr_t)data->o_attributes);
        if (prop->part >= 0)
        {
            part = &attr->modelparts_container->modelparts_desc[prop->joint-4]->modelparts[model_part][0];
            dl = (part->flags & 15) == 1 ? ((Gfx**)part->dl)[1] : part->dl;
            if ((part->flags & 15) == 1) prefix = ((Gfx**)part->dl)[0];
        }
        else
        {
            dl = attr->commonparts_container->commonparts[0].dobjdesc[prop->joint-4].dl;
            if ((attr->commonparts_container->commonparts[0].flags & 15) == 1) { prefix = ((Gfx**)dl)[0]; dl = ((Gfx**)dl)[1]; }
        }
        if (!s->model)
        {
            s->model = ccVisualMakeProp(g, dl);
            if (s->model)
            {
                DObjGetStruct(s->model)->user_data.p = prefix;
                ccPropMaterials(DObjGetStruct(s->model),
                    part ? part->mobjsubs : attr->commonparts_container->commonparts[0].p_mobjsubs ? attr->commonparts_container->commonparts[0].p_mobjsubs[prop->joint-4] : NULL,
                    part ? part->costume_matanim_joints : attr->commonparts_container->commonparts[0].p_costume_matanim_joints ? attr->commonparts_container->commonparts[0].p_costume_matanim_joints[prop->joint-4] : NULL,
                    part ? part->main_matanim_joints : NULL, 0);
                if (ball) ccVisualBallColor(s, DObjGetStruct(s->model), ccBodyKind(fp));
            }
        }
        if (s->model)
        {
            dobj = DObjGetStruct(s->model); pos = DObjGetStruct(g)->translate.vec.f;
            pos.x += sample->translate.z*fp->lr; pos.y += sample->translate.y; pos.z -= sample->translate.x*fp->lr;
            dobj->translate.vec.f = pos;
            dobj->rotate.vec.f = ftCustomAnimationToEuler(ftCustomAnimationMultiply(
                ftCustomAnimationFromEuler(0, fp->lr*F_CST_DTOR32(90.0F), 0),
                ftCustomAnimationFromEuler(sample->rotate.x, sample->rotate.y, sample->rotate.z)));
            dobj->scale.vec.f = sample->scale;
            if (prop->hide_body)
            {
                s->hidden = TRUE;
                for (i = 4; i < FTPARTS_JOINT_NUM_MAX; i++) if (fp->joints[i])
                { s->flags[i] = fp->joints[i]->flags; fp->joints[i]->flags |= DOBJ_FLAG_HIDDEN; }
            }
        }
    }
    /* A cosmetic orb has no WPStruct and never acquires a damaging hitbox. */
    if (neutral && neutral->row >= 14 && neutral->row < 16) s->held_charge = TRUE;
    if (!neutral || neutral->row < 14 || neutral->row >= 18 || neutral->fired || !s->held_charge)
    {
        ccVisualEject(s, &s->charge);
        if (s->held_charge && s->loop && fp->p_loop_sfx == s->loop) { ftParamStopLoopSFX(fp); s->loop = NULL; }
        s->held_charge = FALSE;
    }
    else if (sCCNeutralFiles[4])
    {
        if (!s->charge)
        {
            WPAttributes *shot = (WPAttributes*)((uintptr_t)sCCNeutralFiles[4]+(uintptr_t)ccwp_dWPSamusChargeShotWeaponDesc.o_attributes);
            s->charge = ccVisualMakeProp(g, shot->data);
            if (s->charge) gcAddMObjAll(s->charge, shot->p_mobjsubs);
        }
        if (s->charge)
        {
            frame = time < 0 ? 0 : (s32)time;
            if (frame > clock->move->duration) frame = clock->move->duration;
            pos = DObjGetStruct(g)->translate.vec.f;
            pos.x += fp->lr*sFTCharBuilderActions[neutral->row].spawn[frame].x;
            pos.y += sFTCharBuilderActions[neutral->row].spawn[frame].y;
            pos.z += fp->lr*sFTCharBuilderActions[neutral->row].spawn[frame].z;
            dobj = DObjGetStruct(s->charge); dobj->translate.vec.f = pos;
            level = neutral->row >= 16 ? neutral->release_charge : neutral->samus_charge;
            if (level < 0) level = 0; if (level > 7) level = 7;
            if (!fp->is_muted && !fp->p_loop_sfx)
            {
                ftParamPlayLoopSFX(fp, ccwp_dWPSamusChargeShotWeaponAttributes[level].charge_fgm_id);
                s->loop = fp->p_loop_sfx; gCCVisualSounds++;
            }
            dobj->scale.vec.f.x = dobj->scale.vec.f.y = dobj->scale.vec.f.z = ccwp_dWPSamusChargeShotWeaponAttributes[level].gfx_size/WPCHARGESHOT_GFX_SIZE_DIV;
            dobj->rotate.vec.f.z -= 0.2F*fp->lr;
        }
    }
    ccResumeJoints(fp);
}

/* Exposed ABI facts let linked-MIPS checks avoid guessed private offsets. */
const u32 ccVisualDrawLayout[] = { __builtin_offsetof(DObj,dl), __builtin_offsetof(DObj,user_data), G_RM_PASS | G_RM_AA_ZB_OPA_SURF2 };
const u32 ccChargeVisualLayout[] = {
    __builtin_offsetof(FTStruct,colanim.colanim_id), nGMColAnimFighterCommonSpecialNCharge,
    FTDONKEY_GIANTPUNCH_CHARGE_MAX, __builtin_offsetof(CCVisualState,charge_flash),
    __builtin_offsetof(CCVisualState,ball_palette), __builtin_offsetof(CCVisualState,ball_palettes),
    __builtin_offsetof(MObj,palette_id), __builtin_offsetof(MObj,sub.palettes), sizeof(FTCharBuilderNeutralState)
};
const u32 ccVisualMaterialLayout[] = {
    __builtin_offsetof(SYMallocRegion,ptr), __builtin_offsetof(DObj,mobj), sizeof(MObj),
    __builtin_offsetof(MObj,sub), __builtin_offsetof(MObjSub,sprites), __builtin_offsetof(MObjSub,flags)
};
const u32 ccVisualLayout[] = {
    sizeof(CCVisualState), __builtin_offsetof(CCVisualState,model), __builtin_offsetof(CCVisualState,charge),
    __builtin_offsetof(CCVisualState,effect), __builtin_offsetof(CCVisualState,hidden),
    __builtin_offsetof(DObj,flags), DOBJ_FLAG_HIDDEN, __builtin_offsetof(GObj,link_next),
    __builtin_offsetof(FTStruct,fighter_gobj), __builtin_offsetof(FTAttributes,modelparts_container),
    __builtin_offsetof(FTAttributes,commonparts_container), sizeof(FTModelPart), sizeof(DObjDesc),
    __builtin_offsetof(DObjDesc,dl), __builtin_offsetof(WPAttributes,data), __builtin_offsetof(WPAttributes,p_mobjsubs),
    __builtin_offsetof(FTStruct,p_loop_sfx), __builtin_offsetof(FTStruct,p_voice),
    nFTMotionEventAsyncWait, nFTMotionEventEnd, nFTMotionEventPlayLoopSFXStoreInfo,
    nFTMotionEventStopLoopSFX, nFTMotionEventPlayVoiceStoreInfo, nFTMotionEventPlayFGM,
    sizeof(CCVisualDefinition), ARRAY_COUNT(sFTCustomSpecialAnimations),
    __builtin_offsetof(EFStruct,proc_update), nFTMotionEventEffect
};
