/* Included in ftmain; normal identity never changes the body's fighter kind. */
typedef struct FTCustomNormalMechanics
{
    const Vec3f *travel, *socket;
    s32 count;
    u32 flags;
} FTCustomNormalMechanics;
#include "ftnormalmechanics.generated.inc"

s32 ftMainCharBuilderGetNormalKind(FTStruct *fp, s32 attack)
{
    SCCharBuilderSlot *slot = ftCustomMoveGetSlot(fp);
    s32 donor;
    if ((slot == NULL) || (attack < 0) || (attack >= nSCCharBuilderAttackGrab)) return fp->fkind;
    donor = slot->attacks[attack];
    return ((donor >= 0) && (donor < 12)) ? donor : fp->fkind;
}

FTAttributes* ftMainCharBuilderGetAttackAttributes(FTStruct *fp, s32 attack)
{
    s32 donor = ftMainCharBuilderGetNormalKind(fp, attack);
    FTData *data;
    if (donor == fp->fkind) return fp->attr;
    data = dFTManagerDataFiles[donor];
    if ((data->p_file_main == NULL) || (*data->p_file_main == NULL)) return fp->attr;
    return lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);
}

s32 ftMainCharBuilderGetJabStatus(FTStruct *fp, s32 native_status, s32 phase)
{
    if (ftMainCharBuilderGetNormalKind(fp, nSCCharBuilderAttackJab) == fp->fkind) return native_status;
    return FTCUSTOMMOVE_JAB_STATUS_START + phase;
}

sb32 ftMainCharBuilderHasNormalMotion(FTStruct *fp, s32 attack, s32 motion)
{
    s32 donor = ftMainCharBuilderGetNormalKind(fp, attack);
    return dFTManagerDataFiles[donor]->mainmotion->motion_desc[motion].anim_file_id != 0;
}

static s32 ftCustomNormalIndex(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    u32 offset;
    if ((clock == NULL) || (ftCustomMoveGetSlot(fp) == NULL)) return -1;
    offset = (u32)clock->move - (u32)sFTCustomMoves;
    if ((offset >= sizeof(sFTCustomMoves)) || (offset % sizeof(FTCustomMoveDefinition))) return -1;
    return offset / sizeof(FTCustomMoveDefinition);
}

static FTAttributes* ftCustomNormalGetAttributes(FTStruct *fp)
{
    s32 index = ftCustomNormalIndex(fp);
    FTData *data;
    if (index < 0) return fp->attr;
    data = dFTManagerDataFiles[index / 33];
    if ((data->p_file_main == NULL) || (*data->p_file_main == NULL)) return fp->attr;
    return lbRelocGetFileData(FTAttributes*, *data->p_file_main, data->o_attributes);
}

static sb32 ftCustomNormalGetTravel(FTStruct *fp, Vec3f *out, sb32 ground)
{
    s32 index = ftCustomNormalIndex(fp), frame;
    const FTCustomNormalMechanics *data;
    if (index < 0) return FALSE;
    data = &sFTCustomNormalMechanics[index / 33][index % 33];
    /* A donor without TransN owns zero travel, even if the body's pose has it. */
    if (data->travel == NULL) { out->x = out->y = out->z = 0.0F; return TRUE; }
    frame = (s32)ftCustomMoveGetClock(fp)->frame;
    if (frame < 0) frame = 0;
    if (frame >= data->count) frame = (ftCustomMoveGetClock(fp)->flags & FTCUSTOMMOVE_FLAG_LOOP) ? frame % (data->count - 1) : data->count - 1;
    *out = data->travel[frame];
    if (ground == FALSE) { out->x *= fp->lr; out->z *= fp->lr; }
    return TRUE;
}

sb32 ftMainCharBuilderUsesNormalTransN(FTStruct *fp)
{
    s32 index = ftCustomNormalIndex(fp);
    if (index < 0) return fp->anim_desc.flags.is_use_transn_joint;
    return (sFTCustomNormalMechanics[index / 33][index % 33].flags & FTANIM_FLAG_TRANSN_JOINT) != 0;
}

sb32 ftMainCharBuilderGetNormalSphere(FTStruct *fp, Mtx44f matrix, Vec3f *size)
{
    s32 index = ftCustomNormalIndex(fp), frame, i, j;
    const FTCustomNormalMechanics *data;
    Vec3f center, root;
    f32 donor_size;
    if ((index < 0) || (index / 33 != nFTKindNess) || (fp->special_coll == NULL)) return FALSE;
    data = &sFTCustomNormalMechanics[index / 33][index % 33];
    if (data->socket == NULL) return FALSE;
    frame = (s32)ftCustomMoveGetClock(fp)->frame;
    if (frame < 0) frame = 0;
    if (frame >= data->count) frame = data->count - 1;
    center = data->socket[frame]; root = DObjGetStruct(fp->fighter_gobj)->translate.vec.f;
    center.x = root.x + center.x * fp->lr; center.y += root.y; center.z = root.z + center.z * fp->lr;
    donor_size = ftCustomNormalGetAttributes(fp)->size;
    *size = fp->special_coll->size;
    size->x *= donor_size; size->y *= donor_size; size->z *= donor_size;
    for (i = 0; i < 4; i++) for (j = 0; j < 4; j++) matrix[i][j] = (i == j) ? 1.0F : 0.0F;
    matrix[3][0] = -center.x; matrix[3][1] = -center.y; matrix[3][2] = -center.z;
    return TRUE;
}
