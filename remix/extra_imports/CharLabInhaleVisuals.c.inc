/* Borrowed inhale wind uses an owned effect and a receiving-body face socket.
 * They never change gameplay joints, native hurtboxes or capture geometry. */
/* Native fighter loading rebuilds these tables after the donor preload walk.
 * Retain resolved pointers while their source bank is live, then bind the spare
 * eighth particle slot after native scene setup. No files load on B input. */
extern s32 sLBParticleScriptBanksNum[8], sLBParticleTextureBanksNum[8];
extern LBScript **sLBParticleScriptBanks[8];
extern LBTexture **sLBParticleTextureBanks[8];
extern s32 sEFParticleBanksNum;
u32 sCCInhaleParticleData[4];
void ccInhaleCaptureParticleBank(s32 bank)
{
    if ((u32)bank>=8) return;
    sCCInhaleParticleData[0]=sLBParticleScriptBanksNum[bank];
    sCCInhaleParticleData[1]=(u32)sLBParticleScriptBanks[bank];
    sCCInhaleParticleData[2]=sLBParticleTextureBanksNum[bank];
    sCCInhaleParticleData[3]=(u32)sLBParticleTextureBanks[bank];
}
static sb32 ccInhaleInstallParticleBank(void)
{
    if (sCCInhaleParticleData[0]<=12 || !sCCInhaleParticleData[1] ||
        !sCCInhaleParticleData[2] || !sCCInhaleParticleData[3] || sEFParticleBanksNum>=8) return FALSE;
    sLBParticleScriptBanksNum[7]=sCCInhaleParticleData[0];
    sLBParticleScriptBanks[7]=(LBScript**)sCCInhaleParticleData[1];
    sLBParticleTextureBanksNum[7]=sCCInhaleParticleData[2];
    sLBParticleTextureBanks[7]=(LBTexture**)sCCInhaleParticleData[3];
    sCCNeutralParticleBanks[2]=7;
    return TRUE;
}

/* Local head Y/Z for the native wind funnel on each receiving body. */
static const f32 sCCInhaleFaces[12][2] = {
    {-55,110}, {-35,140}, {-40,150}, {-35,130}, {-55,110}, {-50,110},
    {-20,250}, {-50,115}, {-25,160}, {-45,135}, {-25,165}, {-55,110}
};

static GObj* ccInhaleLive(CCInhaleState *s, GObj *wanted)
{
    GObj *g;
    if (!wanted) return NULL;
    for (g=gGCCommonLinks[nGCCommonLinkIDEffect]; g; g=g->link_next)
        if (g==wanted && efGetStruct(g) && efGetStruct(g)->fighter_gobj==s->fighter) return g;
    return NULL;
}
static void ccInhaleStop(CCInhaleState *s, GObj **handle)
{
    GObj *g=ccInhaleLive(s,*handle);
    if (g) { ftParamStopEffect(g,efGetStruct(g)); gCCVisualStops++; }
    *handle=NULL;
}
static void ccInhaleVisualClear(FTStruct *fp)
{
    CCInhaleState *s;
    if (!fp) return;
    /* Reset can run after native objects were removed. List membership and the
     * captured fighter pointer validate effects before any owner dereference. */
    for (s=sCCInhaleStates;s<sCCInhaleStates+4;s++)
        if (s->owner==fp) { ccInhaleStop(s,&s->wind);return; }
}
static sb32 ccInhaleWindPhase(FTStruct *fp)
{
    CCSpecialClock *clock=ccSpecialClock(fp);
    CCInhaleState *s=ccInhaleState(fp);
    return clock && clock->donor==nFTKindKirby && s && s->choice==CC_NEUTRAL_INHALE &&
        (clock->motion==nFTKirbyMotionSpecialNLoop || clock->motion==nFTKirbyMotionSpecialAirNLoop);
}
static void ccInhaleFace(FTStruct *fp, Vec3f *pos, Vec3f *rotate)
{
    s32 body=ccBodyKind(fp),j=sFTCustomAnimationSemanticJoints[body][8],limit=0;
    DObj *head=fp->joints[j],*part;
    FTCustomAnimationQuat q={0,0,0,1};
    *pos=(Vec3f){0,sCCInhaleFaces[body][0],sCCInhaleFaces[body][1]};
    ccSuspendJoints(fp);
    if (head)
    {
        gmCollisionGetFighterPartsWorldPosition(head,pos);
        /* Follow the real body's head orientation, including animated parents. */
        for (part=head;part && part!=DOBJ_PARENT_NULL && limit++<64;part=part->parent)
            q=ftCustomAnimationMultiply(ftCustomAnimationFromEuler(part->rotate.vec.f.x,
                part->rotate.vec.f.y,part->rotate.vec.f.z),q);
    }
    else { *pos=DObjGetStruct(fp->fighter_gobj)->translate.vec.f;pos->y+=230;q=ftCustomAnimationFromEuler(0,fp->lr*F_CST_DTOR32(90),0); }
    *rotate=ftCustomAnimationToEuler(q);
    ccResumeJoints(fp);
}
static void ccInhaleWindBind(GObj *fighter, GObj *wind)
{
    CCInhaleState *s=ccInhaleState(ftGetStruct(fighter));
    if (!s) return;
    s->wind=wind;ftGetStruct(fighter)->is_effect_attach=TRUE;gCCVisualEffects++;
    ccInhaleWindPosition(wind);
}
static void ccInhaleWindPosition(GObj *g)
{
    EFStruct *ep=efGetStruct(g);
    FTStruct *fp=ftGetStruct(ep->fighter_gobj);
    CCInhaleState *s=ccInhaleState(fp);
    Vec3f pos,rotate;
    if (!s || s->wind!=g || !ccInhaleWindPhase(fp))
    {
        if (s && s->wind==g) s->wind=NULL;
        ftParamStopEffect(g,ep);gCCVisualStops++;return;
    }
    ccInhaleFace(fp,&pos,&rotate);
    /* Native particle script travels from +800 toward the donor mouth at +160. */
    pos.x+=fp->lr*640;
    ep->xf->translate=pos;
    ep->xf->rotate.z=fp->lr<0 ? F_CST_DTOR32(90) : F_CST_DTOR32(-90);
}
static __attribute__((noinline)) void ccInhaleWindStart(GObj *g)
{
    FTStruct *fp=ftGetStruct(g);
    CCInhaleState *s=ccInhaleState(fp);
    if (!s) return;
    s->wind=ccInhaleLive(s,s->wind);
    if (fp->motion_vars.flags.flag0==1 && !s->wind && ccInhaleInstallParticleBank())
    {
        if (ccfxKirbyInhaleWind(g)) fp->motion_vars.flags.flag0=0;
    }
}
static __attribute__((noinline)) void ccInhaleVisualTick(GObj *g)
{
    FTStruct *fp=ftGetStruct(g);
    CCInhaleState *s=ccInhaleState(fp);
    if (!s) return;
    s->wind=ccInhaleLive(s,s->wind);
    if (!ccInhaleWindPhase(fp)) ccInhaleVisualClear(fp);
}
const u32 ccInhaleVisualLayout[]={
    __builtin_offsetof(CCInhaleState,wind),
    __builtin_offsetof(CCInhaleState,fighter),__builtin_offsetof(EFStruct,xf),
    __builtin_offsetof(LBTransform,translate),__builtin_offsetof(LBTransform,rotate),
    nFTKirbyMotionSpecialNLoop,nFTKirbyMotionSpecialAirNLoop
};

