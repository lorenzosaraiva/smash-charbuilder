/* Borrowed inhale cosmetics use owned effects and a receiving-body face socket.
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

static const Vtx sCCInhaleMouthVertices[32] = {
    { { { 0, 0, 4 }, 0, {0,0}, {8,0,8,255} } },
    { { { 100, 0, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 87, 50, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 50, 87, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 0, 100, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { -50, 87, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { -87, 50, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { -100, 0, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { -87, -50, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { -50, -87, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 0, -100, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 50, -87, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 87, -50, 7 }, 0, {0,0}, {8,0,8,255} } },
    { { { 110, 0, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { 95, 55, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { 55, 95, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { 0, 110, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { -55, 95, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { -95, 55, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { -110, 0, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { -95, -55, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { -55, -95, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { 0, -110, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { 55, -95, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { 95, -55, 0 }, 0, {0,0}, {92,36,36,255} } },
    { { { -50, -60, 10 }, 0, {0,0}, {230,80,110,255} } },
    { { { 50, -60, 10 }, 0, {0,0}, {230,80,110,255} } },
    { { { 0, -22, 10 }, 0, {0,0}, {230,80,110,255} } },
    { { { -68, 56, 11 }, 0, {0,0}, {250,240,220,255} } },
    { { { 68, 56, 11 }, 0, {0,0}, {250,240,220,255} } },
    { { { 50, 26, 11 }, 0, {0,0}, {250,240,220,255} } },
    { { { -50, 26, 11 }, 0, {0,0}, {250,240,220,255} } },
};
static const Gfx sCCInhaleMouthDL[] = {
    gsDPPipeSync(),
    gsSPClearGeometryMode(G_LIGHTING | G_CULL_BOTH | G_TEXTURE_GEN | G_TEXTURE_GEN_LINEAR),
    gsSPTexture(0,0,0,0,G_OFF),
    gsDPSetCombineMode(G_CC_SHADE, G_CC_SHADE),
    gsSPVertex(sCCInhaleMouthVertices,32,0),
    gsSP1Triangle(0, 1, 2, 0),
    gsSP2Triangles(1, 13, 14, 0, 1, 14, 2, 0),
    gsSP1Triangle(0, 2, 3, 0),
    gsSP2Triangles(2, 14, 15, 0, 2, 15, 3, 0),
    gsSP1Triangle(0, 3, 4, 0),
    gsSP2Triangles(3, 15, 16, 0, 3, 16, 4, 0),
    gsSP1Triangle(0, 4, 5, 0),
    gsSP2Triangles(4, 16, 17, 0, 4, 17, 5, 0),
    gsSP1Triangle(0, 5, 6, 0),
    gsSP2Triangles(5, 17, 18, 0, 5, 18, 6, 0),
    gsSP1Triangle(0, 6, 7, 0),
    gsSP2Triangles(6, 18, 19, 0, 6, 19, 7, 0),
    gsSP1Triangle(0, 7, 8, 0),
    gsSP2Triangles(7, 19, 20, 0, 7, 20, 8, 0),
    gsSP1Triangle(0, 8, 9, 0),
    gsSP2Triangles(8, 20, 21, 0, 8, 21, 9, 0),
    gsSP1Triangle(0, 9, 10, 0),
    gsSP2Triangles(9, 21, 22, 0, 9, 22, 10, 0),
    gsSP1Triangle(0, 10, 11, 0),
    gsSP2Triangles(10, 22, 23, 0, 10, 23, 11, 0),
    gsSP1Triangle(0, 11, 12, 0),
    gsSP2Triangles(11, 23, 24, 0, 11, 24, 12, 0),
    gsSP1Triangle(0, 12, 1, 0),
    gsSP2Triangles(12, 24, 13, 0, 12, 13, 1, 0),
    gsSP1Triangle(25,26,27,0),
    gsSP2Triangles(28,29,30,0,28,30,31,0),
    gsSPSetGeometryMode(G_LIGHTING | G_CULL_BACK),
    gsSPEndDisplayList()
};
/* width/height and local mouth-center Y/Z; one face calibration per body,
 * shared by every inhale phase/facing, rather than per donor/body combination. */
static const f32 sCCInhaleFaces[12][4] = {
    {75,85,-55,110}, {90,75,-35,140}, {130,120,-40,150},
    {105,85,-35,130}, {75,85,-55,110}, {75,80,-50,110},
    {135,125,-20,250}, {80,85,-50,115}, {120,120,-25,160},
    {85,75,-45,135}, {120,110,-25,165}, {75,80,-55,110}
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
        if (s->owner==fp) { ccInhaleStop(s,&s->mouth);ccInhaleStop(s,&s->wind);return; }
}
static s32 ccInhaleMouthPhase(FTStruct *fp)
{
    CCSpecialClock *clock=ccSpecialClock(fp);
    if (!clock || clock->donor!=nFTKindKirby || !ccInhaleState(fp) ||
        ccInhaleState(fp)->choice!=CC_NEUTRAL_INHALE) return 0;
    switch(clock->motion)
    {
    case nFTKirbyMotionSpecialNStart: case nFTKirbyMotionSpecialAirNStart:return 1;
    case nFTKirbyMotionSpecialNLoop: case nFTKirbyMotionSpecialAirNLoop:return 2;
    case nFTKirbyMotionSpecialNEnd: case nFTKirbyMotionSpecialAirNEnd:return 3;
    case nFTKirbyMotionSpecialNEat: case nFTKirbyMotionSpecialAirNEat:return 4;
    case nFTKirbyMotionSpecialNThrow: case nFTKirbyMotionSpecialAirNThrow:return 5;
    default:return 0;
    }
}
static __attribute__((noinline)) sb32 ccInhaleEffectLive(GObj *g)
{
    s32 i;
    for (i=0;i<4;i++)
    {
        CCInhaleState *s=&sCCInhaleStates[i];
        if (s->mouth==g && s->owner && ccInhaleState(s->owner)==s && ccInhaleMouthPhase(s->owner))
            return ccInhaleLive(s,g)!=NULL;
    }
    return FALSE;
}
static void ccInhaleFace(FTStruct *fp, Vec3f *pos, Vec3f *rotate)
{
    s32 body=ccBodyKind(fp),j=sFTCustomAnimationSemanticJoints[body][8],limit=0;
    DObj *head=fp->joints[j],*part;
    FTCustomAnimationQuat q={0,0,0,1};
    *pos=(Vec3f){0,sCCInhaleFaces[body][2],sCCInhaleFaces[body][3]};
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
    if (!s || s->wind!=g || ccInhaleMouthPhase(fp)!=2)
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
    CCSpecialClock *clock;
    DObj *dobj;
    Vec3f pos,rotate;
    f32 amount=1,size;
    s32 phase,body;
    if (!s) return;
    phase=ccInhaleMouthPhase(fp);
    if (!phase) { ccInhaleVisualClear(fp);return; }
    s->mouth=ccInhaleLive(s,s->mouth);s->wind=ccInhaleLive(s,s->wind);
    if (phase!=2) ccInhaleStop(s,&s->wind);
    clock=ccSpecialClock(fp);body=ccBodyKind(fp);
    if (phase==1) amount=clock->frame/16;
    else if (phase==3) amount=1-clock->frame/(clock->timing&0x7FFFFFFF);
    else if (phase==5) amount=clock->frame<7 ? 1 : 1-(clock->frame-7)/13;
    if (amount<0) amount=0;if (amount>1) amount=1;
    if (amount<0.01F) { ccInhaleStop(s,&s->mouth);return; }
    if (!s->mouth) s->mouth=ccVisualMakeProp(g,(Gfx*)sCCInhaleMouthDL);
    if (!s->mouth) return;
    ccInhaleFace(fp,&pos,&rotate);dobj=DObjGetStruct(s->mouth);
    dobj->translate.vec.f=pos;dobj->rotate.vec.f=rotate;
    size=fp->attr->size;
    dobj->scale.vec.f=(Vec3f){sCCInhaleFaces[body][0]*size/100,
        sCCInhaleFaces[body][1]*size*amount/100,size};
}
const u32 ccInhaleVisualLayout[]={
    __builtin_offsetof(CCInhaleState,mouth),__builtin_offsetof(CCInhaleState,wind),
    __builtin_offsetof(CCInhaleState,fighter),__builtin_offsetof(EFStruct,xf),
    __builtin_offsetof(LBTransform,translate),__builtin_offsetof(LBTransform,rotate),
    nFTKirbyMotionSpecialNLoop,nFTKirbyMotionSpecialAirNLoop
};

