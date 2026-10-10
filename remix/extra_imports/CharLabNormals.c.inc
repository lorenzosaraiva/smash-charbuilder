/* Donor normal semantics without installing donor identity or model parts. */
#include "../build/char_creator/runtime/normal-data.inc"
extern s32 ccSelectJabDonor(FTStruct*, s32);
extern void ccOriginalKirbyJabEffect(FTStruct*);
extern s32 sCCNormalDonors[4];

/* Unique motion/status numbers are local to each fighter. Appear, charge
 * loops and jabs can share them; only an explicit jab transition owns a phase. */
typedef struct CCJabState {
    FTStruct *owner;
    u32 generation;
    s32 status, phase;
    sb32 pending;
} CCJabState;
static CCJabState sCCJabs[4];
const u32 ccJabNativeCases[][2] = {
    { nFTKindSamus, nFTSamusStatusAppearR }, { nFTKindSamus, nFTSamusStatusAppearL },
    { nFTKindSamus, nFTSamusStatusSpecialNLoop },
    { nFTKindNess, nFTNessStatusAppearRStart }, { nFTKindNess, nFTNessStatusAppearLStart },
    { nFTKindNess, nFTNessStatusAppearWait }, { nFTKindNess, nFTNessStatusAppearREnd },
    { nFTKindNess, nFTNessStatusAppearLEnd }, { nFTKindNess, nFTNessStatusSpecialN },
    { nFTKindCaptain, nFTCaptainStatusAppearRStart }, { nFTKindCaptain, nFTCaptainStatusAppearLStart },
    { nFTKindCaptain, nFTCaptainStatusAppearREnd }, { nFTKindCaptain, nFTCaptainStatusAppearLEnd },
    { nFTKindCaptain, nFTCaptainStatusSpecialN }, { nFTKindCaptain, nFTCaptainStatusSpecialLw }
};
const u32 ccJabOwnershipLayout[] = { nFTCommonMotionSpecialStart, ARRAY_COUNT(ccJabNativeCases) };

static s32 ccJabPhase(FTStruct *fp)
{
    CCJabState *state;
    if (fp->player >= 4) return -1;
    state = &sCCJabs[fp->player];
    return state->owner == fp && state->generation == fp->player_num &&
        state->status == fp->status_id ? state->phase : -1;
}

void ccJabStatusChanging(FTStruct *fp, s32 next)
{
    CCJabState *state;
    /* Expanded bodies use Remix's legacy/native normal callbacks. */
    if (fp->player >= 4 || (u32)ccBodyKind(fp) >= 12) return;
    state = &sCCJabs[fp->player];
    if (state->owner == fp && state->generation == fp->player_num &&
        state->pending && state->status == next)
    {
        state->pending = FALSE;
        return;
    }
    state->owner = NULL;
    /* Shared normal setup selects its own donor later. Native unique actions
     * must not inherit an unrelated jab/tilt/aerial action array or FTData. */
    sCCNormalDonors[fp->player] = -1;
}

s32 ftMainCharBuilderGetNormalKind(FTStruct *fp, s32 attack)
{
    SCCharBuilderSlot *slot=ftCustomMoveGetSlot(fp);
    if (!slot || (u32)attack>=nSCCharBuilderAttackGrab) return ccBodyKind(fp);
    return slot->attacks[attack];
}
FTAttributes* ftMainCharBuilderGetAttackAttributes(FTStruct *fp,s32 attack)
{
    s32 donor=ftMainCharBuilderGetNormalKind(fp,attack);
    return donor==ccBodyKind(fp) || (u32)donor>=12 ? fp->attr : &sCCNormalAttributes[donor];
}
s32 ftMainCharBuilderGetJabStatus(FTStruct *fp,s32 native_status,s32 phase)
{
    s32 donor=ftMainCharBuilderGetNormalKind(fp,nSCCharBuilderAttackJab);
    if (donor!=ccBodyKind(fp) && fp->player < 4)
    {
        CCJabState *state = &sCCJabs[fp->player];
        state->owner = fp; state->generation = fp->player_num;
        state->status = native_status; state->phase = phase; state->pending = TRUE;
        ccSelectJabDonor(fp,donor);
    }
    return native_status;
}
sb32 ftMainCharBuilderHasNormalMotion(FTStruct *fp,s32 attack,s32 motion)
{
    s32 donor=ftMainCharBuilderGetNormalKind(fp,attack);
    return (u32)donor<12 && (u32)motion<276 && sCCNormalMotionAvailable[donor][motion];
}
static FTAttributes* ccNormalAttributes(FTStruct *fp)
{
    s32 index=ccNormalIndex(fp);
    return index<0 ? fp->attr : &sCCNormalAttributes[index/33];
}
sb32 ccUseNormalCallback(void *object,s32 kind)
{
    FTStruct *fp=kind ? object : ftGetStruct((GObj*)object);
    return (u32)ccBodyKind(fp)<12 && ccSpecialDonor(fp)<0 && ftCustomMoveGetSlot(fp)!=NULL;
}

sb32 ftMainCharBuilderGetNormalSphere(FTStruct *fp,Mtx44f matrix,Vec3f *size)
{
    s32 index=ccNormalIndex(fp),frame,i,j;
    const FTCustomNormalMechanics *data;
    Vec3f center,root;
    f32 scale;
    if (index<0 || index/33!=nFTKindNess || !fp->special_coll) return FALSE;
    data=&sFTCustomNormalMechanics[index/33][index%33];
    if (!data->socket) return FALSE;
    frame=(s32)ftCustomMoveGetClock(fp)->frame;
    if(frame<0)frame=0;if(frame>=data->count)frame=data->count-1;
    center=data->socket[frame];root=DObjGetStruct(fp->fighter_gobj)->translate.vec.f;
    center.x=root.x+center.x*fp->lr;center.y+=root.y;center.z=root.z+center.z*fp->lr;
    scale=sCCNormalAttributes[nFTKindNess].size;*size=fp->special_coll->size;
    size->x*=scale;size->y*=scale;size->z*=scale;
    for(i=0;i<4;i++)for(j=0;j<4;j++)matrix[i][j]=i==j?1.0F:0.0F;
    matrix[3][0]=-center.x;matrix[3][1]=-center.y;matrix[3][2]=-center.z;
    return TRUE;
}
#include "../build/char_creator/runtime/normal-callbacks.inc"
