/* Exercise actual forward-throw dispatch and actual DK release callbacks. */
#define _FIGHTER_H_
#include <ft/ftcommon.h>
#define DObjGetStruct(gobj) ((gobj)->root)
static s32 sTestThrowQueue, sTestThrowRelease, sTestThrowCargo;
static FTThrowHitDesc sTestNativeThrow[2] = { {52,8,45,80,0,70,0}, {-1,2,361,100,0,0,0} };
static void ftMainPlayAnimEventsAll(GObj *gobj)
{
    gobj->fp->motion_attack_id = gobj->fp->status_id == nFTCommonStatusThrowB ?
        nFTMotionAttackIDThrowB : nFTMotionAttackIDThrowF;
    gobj->fp->throw_desc = sTestNativeThrow;
    ftCustomMoveApplyThrow(gobj->fp);
}
void ftParamSetCaptureImmuneMask(FTStruct *fp, u8 mask) { fp->capture_immune_mask = mask; }
void ftCommonThrownProcPhysics(GObj *gobj) {}
void ftCommonThrownReleaseThrownUpdateStats(GObj *gobj, s32 lr, s32 script, sb32 stale)
{ sTestThrowRelease++; }
void ftCommonCaptureShoulderedSetStatus(GObj *gobj) { sTestThrowCargo++; }
void ftDonkeyThrowFWaitSetStatus(GObj *gobj) { sTestThrowCargo++; }
static void mpCommonSetFighterAir(FTStruct *fp) { fp->ga = nMPKineticsAir; }
static void mpCommonSetFighterGround(FTStruct *fp) { fp->ga = nMPKineticsGround; }
static GObj* efManagerSamusGrappleBeamGlowMakeEffect(GObj *gobj) { return NULL; }
void ftCommonThrownSetStatusQueue(GObj *gobj, s32 first, s32 second) { sTestThrowQueue = second; }
void ftCommonThrownSetStatusImmediate(GObj *gobj, s32 status) { sTestThrowQueue = status; }
static sb32 mpCommonProcFighterOnFloor(GObj *gobj, void (*callback)(GObj*)) { return TRUE; }
static sb32 mpCommonProcFighterLanding(GObj *gobj, void (*callback)(GObj*))
{ if (sTestNeutralLanding) callback(gobj); return sTestNeutralLanding; }
#include "../src/ft/ftcommon/ftcommonthrow.c"
#include "../src/ft/ftchar/ftdonkey/ftdonkeythrowff.c"

static s32 testCharBuilderThrow(void)
{
    FTStruct attacker = {0}, victim = {0};
    FTTestAttributes attr = {0};
    DObj root;
    GObj a = {30, &attacker, &root}, v = {30, &victim, &root};
    SCCharBuilderSlot *slot = &gSCManagerCharBuilderSlots[0];
    s32 donor, released, cargo, i;
    sTestThrowMode = TRUE;
    attacker.fkind = slot->body = nFTKindDonkey; attacker.pkind = nFTPlayerKindMan;
    attacker.attr = &attr; attacker.lr = 1; attacker.ga = nMPKineticsGround;
    victim.fkind = nFTKindMario;
    attr.thrown_status[nFTKindMario].ft_thrown[0].status1 = nFTCommonStatusThrownStart;
    attr.thrown_status[nFTKindMario].ft_thrown[0].status2 = nFTCommonStatusShouldered;
    attr.thrown_status[nFTKindMario].ft_thrown[1].status1 = -1;
    attr.thrown_status[nFTKindMario].ft_thrown[1].status2 = nFTCommonStatusThrownCommon;
    slot->is_enabled = TRUE; gSCManagerCharBuilderPlayerSlots[0] = 0;
    gSCManagerSceneData.scene_curr = nSCKindVSBattle;
    for (donor = 0; donor < 12; donor++)
    {
        slot->attacks[nSCCharBuilderAttackThrowF] = donor;
        attacker.catch_gobj = &v; attacker.status_vars.common.throwff.is_turn = TRUE;
        ftCommonThrowSetStatus(&a, TRUE);
        CHECK(attacker.capture_immune_mask == FTCATCHKIND_MASK_ALL);
        CHECK(attacker.motion_vars.flags.flag2 == 0);
        CHECK(attacker.status_id == (donor == nFTKindDonkey ? nFTCommonStatusThrowF : nFTDonkeyStatusThrowFF));
        CHECK(sTestThrowQueue == (donor == nFTKindDonkey ? nFTCommonStatusShouldered : nFTCommonStatusThrownCommon));
        cargo = sTestThrowCargo; released = sTestThrowRelease;
        if (donor == nFTKindDonkey)
        {
            a.anim_frame = -1; ftCommonThrowProcUpdate(&a);
            CHECK(sTestThrowCargo == cargo + 2 && sTestThrowRelease == released);
            continue;
        }
        CHECK(!attacker.status_vars.common.throwff.is_turn);
        CHECK(attacker.throw_desc[0].damage == sFTCustomThrowProperties[donor][1][0].damage);
        CHECK(attacker.throw_desc[0].knockback_base == sFTCustomThrowProperties[donor][1][0].knockback_base);
        CHECK(attacker.throw_desc[0].status_id == 52);
        for (i = 1; i <= 22; i++)
        {
            a.anim_frame = i == 22 ? -1 : i;
            if (i == 18) attacker.motion_vars.flags.flag2 = 1;
            ftDonkeyThrowFFProcUpdate(&a);
            CHECK(sTestThrowRelease == released + (i >= 18));
            CHECK(sTestThrowCargo == cargo);
            if (i >= 18) CHECK(attacker.catch_gobj == NULL && attacker.capture_immune_mask == FTCATCHKIND_MASK_NONE);
        }
    }
    /* Back throw and vanilla DK retain their original dispatch. */
    attacker.catch_gobj = &v; attacker.input.pl.stick_range.x = -50;
    ftCommonThrowSetStatus(&a, FALSE); CHECK(attacker.status_id == nFTCommonStatusThrowB);
    attacker.catch_gobj = &v; gSCManagerCharBuilderPlayerSlots[0] = -1;
    ftCommonThrowSetStatus(&a, TRUE);
    CHECK(attacker.status_id == nFTCommonStatusThrowF && sTestThrowQueue == nFTCommonStatusShouldered);
    sTestThrowMode = FALSE;
    return 0;
}
