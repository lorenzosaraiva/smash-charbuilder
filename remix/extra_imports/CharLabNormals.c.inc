/* Donor normal semantics without installing donor identity or model parts. */
#include "../build/char_creator/runtime/normal-data.inc"
extern s32 ccSelectJabDonor(FTStruct*, s32);
extern void ccOriginalKirbyJabEffect(FTStruct*);

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
    if (donor!=ccBodyKind(fp)) ccSelectJabDonor(fp,donor);
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
