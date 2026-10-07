/* Eight source frames per port bound DMA and RAM independently of long cargo
 * loops. Geometry is not rescaled to the selected body's limbs. */
typedef struct CCPairFrame {
    FTCustomPairAnchor anchor;
    Vec3f travel;
    FTCustomCollisionFrame collision;
    FTCustomSpecialAttachmentFrame props[6];
} CCPairFrame;
_Static_assert(sizeof(CCPairFrame) == 352, "paired ROM geometry ABI");
static CCPairFrame sCCPairFrames[4][8] __attribute__((aligned(16)));
static const FTCustomPairPhase *sCCPairLoaded[4];
static s32 sCCPairFirst[4];
static FTCustomCollisionTrajectory sCCPairCollision[4];

static CCPairFrame* ccPairSample(FTStruct *fp, s32 frame)
{
    const FTCustomPairPhase *phase = sFTCustomPairStates[fp->player].phase;
    s32 first = frame & ~7, count;
    if (sCCPairLoaded[fp->player] != phase || sCCPairFirst[fp->player] != first)
    {
        count = phase->count-first; if (count > 8) count = 8;
        syDmaReadRom(0x5400000+phase->offset+first*sizeof(CCPairFrame), sCCPairFrames[fp->player], count*sizeof(CCPairFrame));
        sCCPairLoaded[fp->player] = phase; sCCPairFirst[fp->player] = first;
    }
    return &sCCPairFrames[fp->player][frame-first];
}

static void ccPairStopProp(GObj **object)
{
    GObj *g;
    for (g = gGCCommonLinks[nGCCommonLinkIDEffect]; g; g = g->link_next)
        if (g == *object && efGetStruct(g) && efGetStruct(g)->proc_update == ccVisualEffectUpdate)
        { ftParamStopEffect(g, efGetStruct(g)); gCCVisualStops++; break; }
    *object = NULL;
}
