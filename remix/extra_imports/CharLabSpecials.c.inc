/* Foreign special state must not alias the actual body's passive/status union. */
#include <wp/weapon.h>
#include <ef/effect.h>
#include <gm/gmfunctions.h>
#include <it/item.h>
extern EFDesc dEFManagerNessPKThunderTrailEffectDesc;
extern EFDesc dEFManagerNessPKThunderWaveEffectDesc;
extern WPDesc dWPNessPKThunderHeadWeaponDesc;
extern WPDesc dWPNessPKThunderTrailWeaponDesc;
extern void ccOriginalDivePositions(GObj*, GObj*, Vec3f*);

/* Clang lowers large zero initializers even in a freestanding build. */
void* memset(void *dst, s32 value, u32 count)
{
    volatile u8 *p = dst;
    while (count--) *p++ = value;
    return dst;
}

typedef struct CCSpecialState {
    FTStruct *owner;
    u32 generation;
    f32 angle;
    sb32 tornado, thunder_destroy;
    FTNessPassiveVars ness;
    GObj *weapons[3];
    u32 resources;
    sb32 bomb_throw;
} CCSpecialState;
static CCSpecialState sCCSpecialStates[4];
static struct { FTStruct *owner; u32 generation; s32 donor; } sCCRecovery[4];

static CCSpecialState* ccSpecialState(FTStruct *fp)
{
    CCSpecialState *state;
    if (fp->player >= 4) return NULL;
    state = &sCCSpecialStates[fp->player];
    if (state->owner != fp || state->generation != fp->player_num)
    {
        *state = (CCSpecialState){0};
        state->owner = fp; state->generation = fp->player_num;
    }
    return state;
}

sb32 ccKeepSpecialContext(FTStruct *fp, s32 next)
{
    return fp->player < 4 && ccSpecialDonor(fp) == nFTKindLink &&
        sCCSpecialStates[fp->player].owner == fp && sCCSpecialStates[fp->player].generation == fp->player_num &&
        sCCSpecialStates[fp->player].bomb_throw &&
        (next == nFTCommonStatusLightThrowF4 || next == nFTCommonStatusLightThrowAirF4);
}

static FTAttributes* ccAttributes(FTStruct *fp, s32 donor)
{
    FTData *data;
    if ((u32)donor >= 12) return fp->attr;
    data = dFTManagerDataFiles[donor];
    if (!data || !data->p_file_main || !*data->p_file_main) return fp->attr;
    return (FTAttributes*)((uintptr_t)*data->p_file_main+(uintptr_t)data->o_attributes);
}

FTAttributes* ftMainCharBuilderGetSpecialAttributes(FTStruct *fp)
{ return ccSpecialDonor(fp)<0 ? ccNormalAttributes(fp) : ccAttributes(fp, ccSpecialDonor(fp)); }

static s32 ccRecoveryDonor(FTStruct *fp)
{
    if (fp->player >= 4 || sCCRecovery[fp->player].owner != fp ||
        sCCRecovery[fp->player].generation != fp->player_num ||
        (fp->status_id != nFTCommonStatusFallSpecial && fp->status_id != nFTCommonStatusLandingFallSpecial)) return -1;
    return sCCRecovery[fp->player].donor;
}

FTAttributes* ftMainCharBuilderGetSuperJumpAttributes(FTStruct *fp)
{
    s32 donor = ccRecoveryDonor(fp);
    if (donor == -1) donor = ccSpecialDonor(fp);
    return ccAttributes(fp, donor);
}

sb32 ftMainCharBuilderIsSpecialAdapter(GObj *g)
{ return (u32)ccSpecialDonor(ftGetStruct(g)) < 12; }
sb32 ftMainCharBuilderIsSpecialVisual(FTStruct *fp)
{ return (u32)ccSpecialDonor(fp) < 12; }

DObj* ftMainCharBuilderGetSpecialJoint(FTStruct *fp, s32 joint)
{ return fp->joints[(u32)ccSpecialDonor(fp) < 12 ? 0 : joint]; }

void ftMainCharBuilderSetSpecialTravelAngle(FTStruct *fp, f32 angle)
{
    CCSpecialState *state = ccSpecialState(fp);
    if (state && (u32)ccSpecialDonor(fp) < 12) state->angle = angle;
    else fp->joints[nFTPartsJointTransN]->rotate.vec.f.z = angle;
}
f32 ftMainCharBuilderGetSpecialTravelAngle(FTStruct *fp)
{
    CCSpecialState *state = ccSpecialState(fp);
    return (state && (u32)ccSpecialDonor(fp) < 12) ? state->angle : fp->joints[nFTPartsJointTransN]->rotate.vec.f.z;
}

sb32* ftMainCharBuilderGetTornadoExpend(FTStruct *fp)
{
    s32 body = ccBodyKind(fp);
    if (body == nFTKindMario || body == nFTKindLuigi || fp->player >= 4)
        return &fp->passive_vars.mario.is_expend_tornado;
    return &ccSpecialState(fp)->tornado;
}
FTNessPassiveVars* ftMainCharBuilderGetNessPassive(FTStruct *fp)
{
    if (ccBodyKind(fp) == nFTKindNess || fp->player >= 4) return &fp->passive_vars.ness;
    ccSpecialState(fp)->resources |= 1U << nFTKindNess;
    return &ccSpecialState(fp)->ness;
}
GObj** ftMainCharBuilderGetSpecialWeapon(FTStruct *fp, s32 donor)
{ return &ccSpecialState(fp)->weapons[donor == nFTKindYoshi ? 0 : 1]; }
static GObj** ccNessWeapon(FTStruct *fp)
{
    if (ccBodyKind(fp) == nFTKindNess || fp->player >= 4) return &fp->status_vars.ness.specialhi.pkthunder_gobj;
    return &ccSpecialState(fp)->weapons[2];
}
sb32* ftMainCharBuilderGetPikachuThunderDestroy(FTStruct *fp)
{
    if (ccBodyKind(fp) == nFTKindPikachu || fp->player >= 4) return &fp->passive_vars.pikachu.is_thunder_destroy;
    ccSpecialState(fp)->resources |= 1U << nFTKindPikachu;
    return &ccSpecialState(fp)->thunder_destroy;
}

sb32 ftMainCharBuilderGetSpecialSpawn(GObj *g, Vec3f *out)
{
    FTStruct *fp = ftGetStruct(g); CCSpecialClock *clock = ccSpecialClock(fp);
    const FTCharBuilderSpecialPath *path; s32 frame;
    if (!clock || !(path = clock->path) || !path->spawn) return FALSE;
    frame = (s32)clock->frame;
    if (frame < 0) frame = 0;
    if (frame >= path->trajectory.count) frame = path->trajectory.count-1;
    *out = DObjGetStruct(g)->translate.vec.f;
    out->x += path->spawn[frame].x * fp->lr;
    out->y += path->spawn[frame].y;
    out->z += path->spawn[frame].z * fp->lr;
    return TRUE;
}

sb32 ftMainCharBuilderGetSpecialSphere(FTStruct *fp, Mtx44f matrix, Vec3f *size)
{
    CCSpecialClock *clock = ccSpecialClock(fp); Vec3f center; f32 scale; s32 i,j;
    if (!clock || !fp->special_coll || (clock->donor != nFTKindFox && clock->donor != nFTKindNess) ||
        fp->motion_attack_id != nFTMotionAttackIDSpecialLw || !ftMainCharBuilderGetSpecialSpawn(fp->fighter_gobj, &center)) return FALSE;
    scale = ccAttributes(fp, clock->donor)->size;
    *size = fp->special_coll->size;
    size->x *= scale; size->y *= scale; size->z *= scale;
    for (i=0;i<4;i++) for(j=0;j<4;j++) matrix[i][j] = i==j ? 1.0F : 0.0F;
    matrix[3][0] = -center.x; matrix[3][1] = -center.y; matrix[3][2] = -center.z;
    return TRUE;
}

/* Dispatch native entry points only while the corresponding foreign donor is
 * active. Weapon/effect ownership remains valid after leaving the special. */
sb32 ccUseSpecialCallback(void *object, FTStruct *third, s32 donor, s32 kind)
{
    FTStruct *fp;
    if (kind == 1) fp = object;
    else if (kind == 2) {
        Mtx44f matrix; Vec3f size;
        return ftMainCharBuilderGetSpecialSphere(third, matrix, &size) || ftMainCharBuilderGetNormalSphere(third, matrix, &size);
    }
    else if (kind == 3) {
        WPStruct *wp = wpGetStruct((GObj*)object);
        if (!wp->owner_gobj) return FALSE;
        fp = ftGetStruct(wp->owner_gobj);
        return fp->player < 4 && wp->player_num == fp->player_num && ccBodyKind(fp) != donor &&
            sCCSpecialStates[fp->player].owner == fp && sCCSpecialStates[fp->player].generation == fp->player_num &&
            (sCCSpecialStates[fp->player].resources & (1U << donor));
    }
    else if (kind == 4) {
        EFStruct *ep = efGetStruct((GObj*)object);
        if (!ep->effect_vars.pkthunder.owner_gobj) return FALSE;
        fp = ftGetStruct(ep->effect_vars.pkthunder.owner_gobj);
        return fp->player < 4 && ccBodyKind(fp) != nFTKindNess &&
            sCCSpecialStates[fp->player].owner == fp && sCCSpecialStates[fp->player].generation == fp->player_num &&
            (sCCSpecialStates[fp->player].resources & (1U << nFTKindNess));
    }
    else if (kind == 5) {
        ITStruct *ip = itGetStruct((GObj*)object);
        if (!ip->owner_gobj || ip->kind != nITKindLinkBomb) return FALSE;
        fp = ftGetStruct(ip->owner_gobj);
        return ccKeepSpecialContext(fp, fp->status_id);
    }
    else fp = ftGetStruct((GObj*)object);
    if (donor == -1) return ccRecoveryDonor(fp) != -1 || (u32)ccSpecialDonor(fp) < 12;
    return ccSpecialDonor(fp) == donor || (donor == nFTKindMario && ccSpecialDonor(fp) == nFTKindLuigi);
}

#include "../build/char_creator/runtime/special-callbacks.inc"

/* Runs at the start of native SetStatus, before status_vars and body context
 * change. Retained weapons are external, so damage/capture writes are safe. */
void ccStatusChanging(GObj *g, s32 next)
{
    FTStruct *fp = ftGetStruct(g); CCSpecialClock *clock = ccSpecialClock(fp);
    s32 donor = ccSpecialDonor(fp); CCSpecialState *state;
    if (fp->player >= 4) return;
    state = ccSpecialState(fp);
    state->bomb_throw = donor == nFTKindLink &&
        (next == nFTCommonStatusLightThrowF4 || next == nFTCommonStatusLightThrowAirF4) &&
        ((fp->item_gobj && itGetStruct(fp->item_gobj)->kind == nITKindLinkBomb) || state->bomb_throw);
    if ((next == nFTCommonStatusFallSpecial || next == nFTCommonStatusLandingFallSpecial) &&
        fp->motion_attack_id == nFTMotionAttackIDSpecialHi &&
        (donor == nFTKindMario || donor == nFTKindLuigi || donor == nFTKindLink || donor == nFTKindSamus ||
         donor == nFTKindFox || donor == nFTKindPikachu || donor == nFTKindCaptain || donor == nFTKindNess))
    {
        sCCRecovery[fp->player].owner = fp; sCCRecovery[fp->player].generation = fp->player_num;
        sCCRecovery[fp->player].donor = donor;
    }
    else if (next != nFTCommonStatusFallSpecial && next != nFTCommonStatusLandingFallSpecial)
        sCCRecovery[fp->player].owner = NULL;
    if (fp->ga == nMPKineticsGround) state->tornado = FALSE;
    if (!clock || !clock->path) return;
    if (donor == nFTKindYoshi && fp->motion_attack_id == nFTMotionAttackIDSpecialHi &&
        next != nFTYoshiStatusSpecialHi && next != nFTYoshiStatusSpecialAirHi) cc_ftYoshiSpecialHiProcDamage(g);
    if (donor == nFTKindLink && fp->motion_attack_id == nFTMotionAttackIDSpecialHi &&
        next != nFTLinkStatusSpecialHi && next != nFTLinkStatusSpecialHiEnd && next != nFTLinkStatusSpecialAirHi) cc_ftLinkSpecialHiProcDamage(g);
    if (donor == nFTKindPikachu && fp->motion_attack_id == nFTMotionAttackIDSpecialLw &&
        (next < nFTPikachuStatusSpecialLwStart || next > nFTPikachuStatusSpecialAirLwEnd)) cc_ftPikachuSpecialLwProcDamage(g);
    if (donor == nFTKindNess && fp->motion_attack_id == nFTMotionAttackIDSpecialHi && next < 0xDC)
    {
        cc_ftNessSpecialHiSetPKThunderDestroy(g);
        *ccNessWeapon(fp) = NULL;
        state->ness.is_thunder_destroy |= TRUE;
    }
}

static void ccStartRecovery(FTStruct *fp, f32 frame)
{
    s32 donor = ccRecoveryDonor(fp);
    const FTCustomMoveDefinition *move;
    if (donor == -1 || fp->status_id != nFTCommonStatusLandingFallSpecial) return;
    move = donor == nFTKindLink ? &sFTCharBuilderLinkSpecialLanding :
        donor == nFTKindSamus ? &sFTCharBuilderSamusSpecialLanding :
        donor == nFTKindFox ? &sFTCharBuilderFoxSpecialLanding :
        donor == nFTKindPikachu ? &sFTCharBuilderPikachuSpecialLanding :
        donor == nFTKindCaptain ? &sFTCharBuilderCaptainSpecialLanding :
        donor == nFTKindNess ? &sFTCharBuilderNessSpecialLanding : &sFTCharBuilderSuperJumpLanding;
    ftCustomMoveStartClock(fp, move, frame);
}
