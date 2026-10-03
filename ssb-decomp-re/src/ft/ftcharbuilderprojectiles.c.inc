/* Native projectile behavior, donor spawn geometry, body-owned poses/state. */
#include "ftneutralprojectiles.generated.inc"
typedef struct FTCharBuilderProjectileState
{
    FTStruct *owner;
    sb32 fired;
} FTCharBuilderProjectileState;
static FTCharBuilderProjectileState sFTCharBuilderProjectileStates[4];

static s32 ftMainCharBuilderGetProjectileIndex(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    u32 offset;
    if ((clock == NULL) || (fp->player >= 4) ||
        (sFTCharBuilderProjectileStates[fp->player].owner != fp)) return -1;
    offset = (u32)clock->move - (u32)sFTCharBuilderProjectileMoves;
    if ((offset >= sizeof(sFTCharBuilderProjectileMoves)) || (offset % sizeof(FTCustomMoveDefinition))) return -1;
    return offset / (2 * sizeof(FTCustomMoveDefinition));
}

static void ftMainCharBuilderMakeProjectile(GObj *fighter_gobj)
{
    FTStruct *fp = ftGetStruct(fighter_gobj);
    s32 index = ftMainCharBuilderGetProjectileIndex(fp);
    s32 air;
    f32 angle, speed;
    Vec3f pos, vel;
    const Vec3f *offset;
    if ((index < 0) || (fp->motion_vars.flags.flag0 == 0)) return;
    fp->motion_vars.flags.flag0 = 0;
    if (sFTCharBuilderProjectileStates[fp->player].fired != FALSE) return;
    sFTCharBuilderProjectileStates[fp->player].fired = TRUE;
    air = fp->ga == nMPKineticsAir;
    offset = &sFTCharBuilderProjectileOffsets[index][air];
    pos = fp->joints[nFTPartsJointTopN]->translate.vec.f;
    pos.x += fp->lr * offset->x;
    pos.y += offset->y;
    pos.z += fp->lr * offset->z;
    switch (index)
    {
    case 0:
    case 1:
        wpMarioFireballMakeWeapon(fighter_gobj, &pos, index);
        func_800269C0_275C0(nSYAudioFGMMarioSpecialN);
        break;
    case 2:
        vel.x = __cosf(FTPIKACHU_THUNDERJOLT_SPAWN_ANGLE) * FTPIKACHU_THUNDERJOLTVEL * fp->lr;
        vel.y = __sinf(FTPIKACHU_THUNDERJOLT_SPAWN_ANGLE) * FTPIKACHU_THUNDERJOLTVEL;
        vel.z = 0.0F;
        wpPikachuThunderJoltAirMakeWeapon(fighter_gobj, &pos, &vel);
        break;
    case 3:
        angle = air ? FTNESS_PKFIRE_SPARK_ANGLE_AIR : FTNESS_PKFIRE_SPARK_ANGLE_GROUND;
        speed = air ? FTNESS_PKFIRE_SPARK_VEL_AIR : FTNESS_PKFIRE_SPARK_VEL_GROUND;
        vel.x = __cosf(angle) * speed * fp->lr;
        vel.y = __sinf(angle) * speed;
        vel.z = pos.z = 0.0F;
        wpNessPKFireMakeWeapon(fighter_gobj, &pos, &vel, angle);
        break;
    }
}

static void ftMainCharBuilderProjectileProcMapGround(GObj*);
static void ftMainCharBuilderProjectileProcMapAir(GObj*);

static void ftMainCharBuilderStartProjectile(GObj *gobj, s32 index, f32 frame_begin, sb32 fired)
{
    FTStruct *fp = ftGetStruct(gobj);
    s32 air = fp->ga == nMPKineticsAir;
    s32 i;
    ftMainCharBuilderStartNeutral(gobj, &sFTCharBuilderProjectileMoves[index][air], frame_begin);
    sFTCharBuilderProjectileStates[fp->player].owner = fp;
    sFTCharBuilderProjectileStates[fp->player].fired = fired;
    fp->proc_accessory = ftMainCharBuilderMakeProjectile;
    fp->proc_interrupt = NULL;
    fp->proc_map = air ? ftMainCharBuilderProjectileProcMapAir : ftMainCharBuilderProjectileProcMapGround;
    /* Continue an unfired script at the donor clock; a spent projectile must
       never replay its firing event on landing or an edge transition. */
    for (i = 0; i < 2; i++)
    {
        if (fired != FALSE) fp->motion_scripts[i][2].p_script = NULL;
        fp->motion_scripts[i][2].script_wait = 1.0F - frame_begin;
    }
}

static void ftMainCharBuilderProjectileSwitchGround(GObj *gobj)
{
    FTStruct *fp = ftGetStruct(gobj);
    s32 index = ftMainCharBuilderGetProjectileIndex(fp);
    f32 frame;
    if (index < 0) return;
    frame = ftCustomMoveGetClock(fp)->frame;
    mpCommonSetFighterGround(fp);
    ftMainCharBuilderStartProjectile(gobj, index, frame, sFTCharBuilderProjectileStates[fp->player].fired);
}

static void ftMainCharBuilderProjectileSwitchAir(GObj *gobj)
{
    FTStruct *fp = ftGetStruct(gobj);
    s32 index = ftMainCharBuilderGetProjectileIndex(fp);
    f32 frame;
    if (index < 0) return;
    frame = ftCustomMoveGetClock(fp)->frame;
    mpCommonSetFighterAir(fp);
    ftPhysicsClampAirVelXMax(fp);
    ftMainCharBuilderStartProjectile(gobj, index, frame, sFTCharBuilderProjectileStates[fp->player].fired);
}

static void ftMainCharBuilderProjectileProcMapGround(GObj *gobj)
{
    mpCommonProcFighterOnEdge(gobj, ftMainCharBuilderProjectileSwitchAir);
}

static void ftMainCharBuilderProjectileProcMapAir(GObj *gobj)
{
    mpCommonProcFighterLanding(gobj, ftMainCharBuilderProjectileSwitchGround);
}

static sb32 ftMainCharBuilderTryProjectileNeutral(GObj *gobj, s32 choice)
{
    FTStruct *fp = ftGetStruct(gobj);
    s32 index = choice - nSCCharBuilderNeutralMarioFireball;
    if ((index < 0) || (index >= 4) || (fp->fkind == sFTCharBuilderProjectileDonors[index])) return FALSE;
    ftMainCharBuilderStartProjectile(gobj, index, 0.0F, FALSE);
    return TRUE;
}
