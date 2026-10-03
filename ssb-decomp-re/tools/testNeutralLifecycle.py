#!/usr/bin/env python3
"""Exercise actual boomerang return/cleanup C, including native fallbacks."""
import subprocess
from pathlib import Path
from testNativeAnimation import function

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'src/wp/wplink/wplinkboomerang.c').read_text()
fixture=r'''
#define _start unused_host_start
#include "../tools/testCustomMove.c"
#undef _start
struct WPStruct { struct { struct { GObj *parent_gobj; u32 flags; } boomerang; } weapon_vars; };
static WPStruct weapon;
#define wpGetStruct(g) (&weapon)
#define WPLINK_BOOMERANG_FLAG_RETURN 1
static s32 native_link, native_kirby;
void ftLinkSpecialNGetSetStatus(GObj *g) { native_link++; }
void ftKirbyCopyLinkSpecialNGetSetStatus(GObj *g) { native_kirby++; }
'''+function(source,'wpLinkBoomerangClearGObjs')+'\n'+function(source,'wpLinkBoomerangCheckOwnerCatch')+r'''
static s32 testLifecycle(void)
{
    FTStruct fp={0}; GObj owner={0}, old={0}, newer={0}; DObj root={0};
    SCCharBuilderSlot *slot=&gSCManagerCharBuilderSlots[0];
    s32 body, before;
    owner.fp=&fp;owner.root=&root;fp.player=0;fp.joints[0]=&root;fp.pkind=nFTPlayerKindMan;
    gSCManagerSceneData.scene_curr=nSCKind1PTrainingMode;gSCManagerCharBuilderPlayerSlots[0]=0;
    slot->is_enabled=TRUE;slot->special_n=nSCCharBuilderNeutralBoomerang;
    for(body=0;body<12;body++)if(body!=nFTKindLink)
    {
        fp.fkind=slot->body=body;ftMainCharBuilderResetNeutralAll();
        fp.passive_vars.link.boomerang_gobj=&newer;fp.passive_vars.kirby.copylink_boomerang_gobj=&newer;
        CHECK(ftMainCharBuilderTrySpecialN(&owner));sFTCharBuilderNeutralStates[0].boomerang=&old;
        ftCustomMoveResetClock(&fp);fp.is_special_interrupt=FALSE;
        weapon.weapon_vars.boomerang.parent_gobj=&owner;weapon.weapon_vars.boomerang.flags=1;
        before=sTestWeaponDestroys;wpLinkBoomerangCheckOwnerCatch(&old,179);
        CHECK(sTestWeaponDestroys==before+1 && sFTCharBuilderNeutralStates[0].boomerang==NULL);
        CHECK(fp.passive_vars.link.boomerang_gobj==&newer && fp.passive_vars.kirby.copylink_boomerang_gobj==&newer);
        CHECK(weapon.weapon_vars.boomerang.parent_gobj==NULL && native_link==0 && native_kirby==0);
        CHECK(ftMainCharBuilderTrySpecialN(&owner));sFTCharBuilderNeutralStates[0].boomerang=&old;
        fp.is_special_interrupt=TRUE;weapon.weapon_vars.boomerang.parent_gobj=&owner;
        wpLinkBoomerangCheckOwnerCatch(&old,179);CHECK(sFTCharBuilderNeutralStates[0].row==22);
        CHECK(sFTCharBuilderNeutralStates[0].boomerang==NULL && native_link==0 && native_kirby==0);
        sFTCharBuilderNeutralStates[0].boomerang=&newer;
        CHECK(!ftMainCharBuilderBoomerangClear(&fp,&old));CHECK(sFTCharBuilderNeutralStates[0].boomerang==&newer);
        before=sTestWeaponDestroys;ftMainCharBuilderResetNeutral(&fp);
        CHECK(sTestWeaponDestroys==before+1 && sFTCharBuilderNeutralStates[0].boomerang==NULL);
        ftMainCharBuilderResetNeutral(&fp);CHECK(sTestWeaponDestroys==before+1);
        sFTCharBuilderNeutralStates[0].boomerang=&old;ftMainCharBuilderResetNeutralAll();
        ftMainCharBuilderResetNeutral(&fp);CHECK(sTestWeaponDestroys==before+1);
    }
    ftMainCharBuilderResetNeutralAll();gSCManagerCharBuilderPlayerSlots[0]=-1;
    fp.fkind=nFTKindLink;fp.passive_vars.link.boomerang_gobj=&old;
    weapon.weapon_vars.boomerang.parent_gobj=&owner;wpLinkBoomerangCheckOwnerCatch(&old,180);
    CHECK(native_link==0 && weapon.weapon_vars.boomerang.parent_gobj==&owner);
    wpLinkBoomerangCheckOwnerCatch(&old,179);CHECK(native_link==1 && fp.passive_vars.link.boomerang_gobj==NULL);
    fp.fkind=nFTKindKirby;fp.passive_vars.kirby.copylink_boomerang_gobj=&old;
    weapon.weapon_vars.boomerang.parent_gobj=&owner;wpLinkBoomerangCheckOwnerCatch(&old,179);
    CHECK(native_kirby==1 && fp.passive_vars.kirby.copylink_boomerang_gobj==NULL);
    fp.fkind=nFTKindMario;fp.passive_vars.link.boomerang_gobj=&newer;
    weapon.weapon_vars.boomerang.parent_gobj=&owner;wpLinkBoomerangCheckOwnerCatch(&old,179);
    CHECK(native_link==1 && native_kirby==1 && fp.passive_vars.link.boomerang_gobj==&newer);
    return 0;
}
void _start(void)
{
    s32 result=testLifecycle();
    if(result){char msg[]="Lifecycle CHECK 0000\n";s32 v=result,i;for(i=18;i>=15;i--){msg[i]='0'+v%10;v/=10;}
        __asm__ volatile("int $0x80"::"a"(4),"b"(2),"c"(msg),"d"(sizeof(msg)-1):"memory");}
    __asm__ volatile("int $0x80"::"a"(1),"b"(result):"memory");__builtin_unreachable();
}
'''
(ROOT/'build/testNeutralLifecycle.c').write_text(fixture)
subprocess.run(['gcc','-m32','-nostdlib','-static','-fno-pie','-fno-stack-protector','-O1',
                '-Iinclude','-Isrc','-D__sgi','-D_LANGUAGE_C','-D_MIPS_SZLONG=32','-DREGION_US',
                'build/testNeutralLifecycle.c','-o','build/testNeutralLifecycle'],cwd=ROOT,check=True)
subprocess.run([str(ROOT/'build/testNeutralLifecycle')],check=True)
print('PASS: native boomerang cleanup/return helpers, foreign body unions, native fallbacks, weapon identity and stock/scene reset.')
