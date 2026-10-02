#include <mn/menu.h>
#include <gm/gmsound.h>
#include <sc/scene.h>
#include <sys/video.h>
#include <sys/rdp.h>
#include <sys/controller.h>
#include <reloc_data.h>

extern void* func_800269C0_275C0(u16);

// // // // // // // // // // // //
//                               //
//             MACROS            //
//                               //
// // // // // // // // // // // //

#define mnOptionCheckGetOptionButtonInput(is_button, mask) \
mnCommonCheckGetOptionButtonInput(sMNOptionOptionChangeWait, is_button, mask)

#define mnOptionCheckGetOptionStickInputUD(stick_range, min, b) \
mnCommonCheckGetOptionStickInputUD(sMNOptionOptionChangeWait, stick_range, min, b)

#define mnOptionCheckGetOptionStickInputLR(stick_range, min, b) \
mnCommonCheckGetOptionStickInputLR(sMNOptionOptionChangeWait, stick_range, min, b)

#define mnOptionSetOptionChangeWaitP(is_button, stick_range, div) \
mnCommonSetOptionChangeWaitP(sMNOptionOptionChangeWait, is_button, stick_range, div)

#define mnOptionSetOptionChangeWaitN(is_button, stick_range, div) \
mnCommonSetOptionChangeWaitN(sMNOptionOptionChangeWait, is_button, stick_range, div)

#define MNOPTION_BUILDER_MODE_NONE 0
#define MNOPTION_BUILDER_MODE_SLOTS 1
#define MNOPTION_BUILDER_MODE_EDIT 2
#define MNOPTION_BUILDER_SLOT_ROWS 9
#define MNOPTION_BUILDER_TEXT_SCALE 2.0F

#define MNOPTION_BUILDER_ENTRY_COUNT 24
#define MNOPTION_BUILDER_VISIBLE_COUNT 12

#define MNOPTION_BUILDER_ROW_X 38
#define MNOPTION_BUILDER_VALUE_X 286
#define MNOPTION_BUILDER_ROW_Y 50
#define MNOPTION_BUILDER_ROW_HEIGHT 14

// // // // // // // // // // // //
//                               //
//       EXTERNAL VARIABLES      //
//                               //
// // // // // // // // // // // //

extern sb32 dSYAudioSoundQuality;

// // // // // // // // // // // //
//                               //
//       INITIALIZED DATA        //
//                               //
// // // // // // // // // // // //

// 0x80133620
u32 dMNOptionFileIDs[/* */] = { &llMNCommonFileID, &llMNOptionFileID, &llMNCommonFontsFileID };

// 0x80133628
Lights1 dMNOptionLights1 = gdSPDefLights1(0x20, 0x20, 0x20, 0xFF, 0xFF, 0xFF, 0x3C, 0x3C, 0x3C);

// 0x80133640
Gfx dMNOptionDisplayList[/* */] =
{
    gsSPSetGeometryMode(G_LIGHTING),
    gsSPSetLights1(dMNOptionLights1),
    gsSPEndDisplayList()
};

// // // // // // // // // // // //
//                               //
//   GLOBAL / STATIC VARIABLES   //
//                               //
// // // // // // // // // // // //

// 0x801337A0
GObj *sMNOptionOptionSoundGObj;

// 0x801337A4
GObj *sMNOptionOptionScreenAdjustGObj;

// 0x801337A8
GObj *sMNOptionOptionBackupClearGObj;

GObj *sMNOptionOptionCharBuilderGObj;

GObj *sMNOptionBuilderBackdropGObj;

GObj *sMNOptionBuilderTextGObj;

intptr_t dMNOptionBuilderLetterOffsets[/* */] =
{
    &llMNCommonFontsLetterASprite, &llMNCommonFontsLetterBSprite,
    &llMNCommonFontsLetterCSprite, &llMNCommonFontsLetterDSprite,
    &llMNCommonFontsLetterESprite, &llMNCommonFontsLetterFSprite,
    &llMNCommonFontsLetterGSprite, &llMNCommonFontsLetterHSprite,
    &llMNCommonFontsLetterISprite, &llMNCommonFontsLetterJSprite,
    &llMNCommonFontsLetterKSprite, &llMNCommonFontsLetterLSprite,
    &llMNCommonFontsLetterMSprite, &llMNCommonFontsLetterNSprite,
    &llMNCommonFontsLetterOSprite, &llMNCommonFontsLetterPSprite,
    &llMNCommonFontsLetterQSprite, &llMNCommonFontsLetterRSprite,
    &llMNCommonFontsLetterSSprite, &llMNCommonFontsLetterTSprite,
    &llMNCommonFontsLetterUSprite, &llMNCommonFontsLetterVSprite,
    &llMNCommonFontsLetterWSprite, &llMNCommonFontsLetterXSprite,
    &llMNCommonFontsLetterYSprite, &llMNCommonFontsLetterZSprite
};

// 0x801337B0
s32 sMNOptionPad0x801337B0[2];

// 0x801337B8
s32 sMNOptionOption;

// 0x801337BC - 0 = mono, 1 = stereo
sb32 sMNOptionSoundMonoOrStereo;

// 0x801337C0
sb32 sMNOptionIsScreenFlash;

// 0x801337C4
s32 sMNOptionPad0x801337C4;

// 0x801337C8
GObj *sMNOptionSoundOptionGObj;

// 0x801337CC
s32 sMNOptionPad0x801337CC;

// 0x801337D0
GObj *sMNOptionMenuGObj;

// 0x801337D4
GObj *D_ovl60_801337D4;

// 0x801337D8
s32 D_ovl60_801337D8;

// 0x801337DC
sb32 sMNOptionIsProceedScene;

// 0x801337E0
s32 sMNOptionOptionChangeWait;

// 0x801337E4
s32 sMNOptionTotalTimeTics;

// 0x801337E8
s32 sMNOptionReturnTic;

s32 sMNOptionBuilderMode;

s32 sMNOptionBuilderSlot;

s32 sMNOptionBuilderEntry;

// 0x801337EC - Padding?
// s32 sMNOptionPad0x801337EC;

// 0x801337F0
LBFileNode sMNOptionStatusBuffer[24];

// 0x801338B0
void *sMNOptionFiles[ARRAY_COUNT(dMNOptionFileIDs)];

// // // // // // // // // // // //
//                               //
//           FUNCTIONS           //
//                               //
// // // // // // // // // // // //

// 0x80131B00
void mnOptionFuncLights(Gfx **dls)
{
    gSPDisplayList(dls[0]++, dMNOptionDisplayList);
}

// 0x80131B24
void mnOptionSetOptionSpriteColors(GObj *gobj, s32 status)
{
    // 0x80133668
    SYColorRGBPair selcolors = { { 0x00, 0x00, 0x00 }, { 0xFF, 0xFF, 0xFF } };

    // 0x80133670
    SYColorRGBPair hicolors  = { { 0x82, 0x00, 0x28 }, { 0xFF, 0x00, 0x28 } };

    // 0x80133678
    SYColorRGBPair notcolors = { { 0x00, 0x00, 0x00 }, { 0x82, 0x82, 0xAA } };

    SYColorRGBPair *colors;
    SObj *sobj;
    s32 i;

    switch (status)
    {
    case nMNOptionTabStatusHighlight:
        colors = &hicolors;
        break;

    case nMNOptionTabStatusNot:
        colors = &notcolors;
        break;

    case nMNOptionTabStatusSelected:
        colors = &selcolors;
        break;

    default:
        break; // WARNING: Undefined behavior. This will assign sp 0xC to colors which is uninitialized.
    }
    sobj = SObjGetStruct(gobj);

    for (i = 0; i < 3; i++)
    {
        sobj->envcolor.r = colors->prim.r;
        sobj->envcolor.g = colors->prim.g;
        sobj->envcolor.b = colors->prim.b;

        sobj->sprite.red   = colors->env.r;
        sobj->sprite.green = colors->env.g;
        sobj->sprite.blue  = colors->env.b;

        sobj = sobj->next;
    }
}

// 0x80131BFC
void mnOptionMakeOptionTabs(GObj *gobj, f32 pos_x, f32 pos_y, s32 lrs)
{
    SObj *sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonOptionTabLeftSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->pos.x = pos_x;
    sobj->pos.y = pos_y;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonOptionTabMiddleSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->pos.x = pos_x + 16.0F;
    sobj->pos.y = pos_y;

    sobj->cms = 0;
    sobj->cmt = 0;

    sobj->masks = 4;
    sobj->maskt = 0;

    sobj->lrs = lrs * 8;
    sobj->lrt = 29;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonOptionTabRightSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->pos.x = pos_x + 16.0F + (lrs * 8);
    sobj->pos.y = pos_y;
}

// 0x80131D2C
void mnOptionSetSoundToggleSpriteColors(GObj *gobj, sb32 mono_or_stereo)
{
    SObj *sobj = SObjGetStruct(gobj);

    if (mono_or_stereo != 0)
    {
        sobj->sprite.red   = 0xFF;
        sobj->sprite.green = 0xFF;
        sobj->sprite.blue  = 0xFF;

        sobj->next->sprite.red   = 0x32;
        sobj->next->sprite.green = 0x32;
        sobj->next->sprite.blue  = 0x32;
    }
    else
    {
        sobj->sprite.red   = 0x32;
        sobj->sprite.green = 0x32;
        sobj->sprite.blue  = 0x32;

        sobj->next->sprite.red   = 0xFF;
        sobj->next->sprite.green = 0xFF;
        sobj->next->sprite.blue  = 0xFF;
    }
}

// 0x80131D98
void mnOptionMakeSoundToggle(void)
{
    GObj *gobj;
    SObj *sobj;

    sMNOptionSoundOptionGObj = gobj = gcMakeGObjSPAfter(0, NULL, 4, GOBJ_PRIORITY_DEFAULT);
    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 2, GOBJ_PRIORITY_DEFAULT, ~0);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionStereoTextSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->pos.x = 179.0F;
    sobj->pos.y = 48.0F;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionMonoTextSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->pos.x = 236.0F;
    sobj->pos.y = 48.0F;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonSlashSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x32;
    sobj->sprite.green = 0x32;
    sobj->sprite.blue  = 0x32;

    sobj->pos.x = 229.0F;
    sobj->pos.y = 48.0F;

    mnOptionSetSoundToggleSpriteColors(gobj, sMNOptionSoundMonoOrStereo);
}

// 0x80131EF0
void mnOptionMakeSound(void)
{
    GObj *gobj;
    SObj *sobj;

    sMNOptionOptionSoundGObj = gobj = gcMakeGObjSPAfter(0, NULL, 4, GOBJ_PRIORITY_DEFAULT);
    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 2, GOBJ_PRIORITY_DEFAULT, ~0);

    mnOptionMakeOptionTabs(gobj, 113.0F, 42.0F, 17);
    mnOptionSetOptionSpriteColors(gobj, sMNOptionOption == nMNOptionOptionSound);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionSoundTextSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x00;
    sobj->sprite.green = 0x00;
    sobj->sprite.blue  = 0x00;

    sobj->pos.x = 116.0F;
    sobj->pos.y = 46.0F;
}

// 0x80131FC4
void mnOptionMakeScreenAdjust(void)
{
    GObj *gobj;
    SObj *sobj;

    sMNOptionOptionScreenAdjustGObj = gobj = gcMakeGObjSPAfter(0, NULL, 4, GOBJ_PRIORITY_DEFAULT);

    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 2, GOBJ_PRIORITY_DEFAULT, ~0);

    mnOptionMakeOptionTabs(gobj, 91.0F, 89.0F, 17);

    mnOptionSetOptionSpriteColors(gobj, sMNOptionOption == nMNOptionOptionScreenAdjust);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionScreenAdjustTextSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x00;
    sobj->sprite.green = 0x00;
    sobj->sprite.blue  = 0x00;

    sobj->pos.x = 103.0F;
    sobj->pos.y = 92.0F;
}

// 0x8013209C
void mnOptionMakeBackupClear(void)
{
    GObj *gobj;
    SObj *sobj;

    sMNOptionOptionBackupClearGObj = gobj = gcMakeGObjSPAfter(0, NULL, 4, GOBJ_PRIORITY_DEFAULT);

    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 2, GOBJ_PRIORITY_DEFAULT, ~0);
    mnOptionMakeOptionTabs(gobj, 69.0F, 136.0F, 17);
    mnOptionSetOptionSpriteColors(gobj, sMNOptionOption == nMNOptionOptionBackupClear);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionBackupClearTextSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x00;
    sobj->sprite.green = 0x00;
    sobj->sprite.blue  = 0x00;

    sobj->pos.x = 86.0F;
    sobj->pos.y = 140.0F;
}

f32 mnOptionGetStringWidth(const char *str)
{
    Sprite *sprite;
    f32 width = 0.0F;
    s32 i;

    for (i = 0; str[i] != '\0'; i++)
    {
        if (str[i] == ' ')
        {
            width += 4.0F;
        }
        else
        {
            sprite = lbRelocGetFileData(Sprite*, sMNOptionFiles[2], dMNOptionBuilderLetterOffsets[str[i] - 'A']);
            width += sprite->width + 1.0F;
        }
    }
    return ((width == 0.0F) ? 0.0F : width - 1.0F) * MNOPTION_BUILDER_TEXT_SCALE;
}

void mnOptionMakeString(GObj *gobj, const char *str, f32 x, f32 y, u32 *color, sb32 is_right)
{
    SObj *sobj;
    f32 pos_x = is_right ? x - mnOptionGetStringWidth(str) : x;
    s32 i;

    for (i = 0; str[i] != '\0'; i++)
    {
        if (str[i] == ' ')
        {
            pos_x += 4.0F * MNOPTION_BUILDER_TEXT_SCALE;
        }
        else
        {
            sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[2], dMNOptionBuilderLetterOffsets[str[i] - 'A']));
            sobj->sprite.attr &= ~SP_FASTCOPY;
            sobj->sprite.attr |= SP_TRANSPARENT;
            sobj->sprite.red = color[0];
            sobj->sprite.green = color[1];
            sobj->sprite.blue = color[2];
            sobj->sprite.scalex = sobj->sprite.scaley = MNOPTION_BUILDER_TEXT_SCALE;
            sobj->pos.x = pos_x;
            sobj->pos.y = y;
            pos_x += (sobj->sprite.width + 1.0F) * MNOPTION_BUILDER_TEXT_SCALE;
        }
    }
}

void mnOptionMakeCharBuilder(void)
{
    u32 text_color[3] = { 0x00, 0x00, 0x00 };
    GObj *gobj;

    sMNOptionOptionCharBuilderGObj = gobj = gcMakeGObjSPAfter(0, NULL, 4, GOBJ_PRIORITY_DEFAULT);
    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 2, GOBJ_PRIORITY_DEFAULT, ~0);
    mnOptionMakeOptionTabs(gobj, 47.0F, 178.0F, 17);
    mnOptionSetOptionSpriteColors(gobj, sMNOptionOption == nMNOptionOptionCharBuilder);
    mnOptionMakeString(gobj, "CHARACTER LAB", 62.0F, 181.0F, text_color, FALSE);
}

// 0x80132174 - Unused?
void mnOptionSetSubtitleSpriteColors(SObj *sobj)
{
    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->envcolor.r = 0x00;
    sobj->envcolor.g = 0x00;
    sobj->envcolor.b = 0x00;

    sobj->sprite.red   = 0xFF;
    sobj->sprite.green = 0xFF;
    sobj->sprite.blue  = 0xFF;
}

// 0x801321A8
void mnOptionMakeMenuGObj(void)
{
    GObj *gobj;
    SObj *sobj;

    // 0x80133680
    intptr_t sp1C[/* */] = { 0x6A8, 0x1580, 0x1CF0 };

    // 0x8013368C
    Vec2f sp3C[/* */] = 
    {
        { 132.0F, 195.0F },
        { 104.0F, 195.0F },
        { 119.0F, 195.0F },
        { 103.0F, 195.0F }
    };

    sMNOptionMenuGObj = gobj = gcMakeGObjSPAfter(0, NULL, 5, GOBJ_PRIORITY_DEFAULT);

#if defined(REGION_JP)
    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 3, GOBJ_PRIORITY_DEFAULT, ~0);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonFrameSprite));

    sobj->pos.x = 93.0F;
    sobj->pos.y = 189.0F;
    
    mnOptionSetSubtitleSpriteColors(sobj);
    
    switch (sMNOptionOption)
    {
        case nMNOptionOptionSound:
            sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionSoundTextJapSprite));
            
            sobj->pos.x = 105.0F;
            sobj->pos.y = 195.0F;
            
            mnOptionSetSubtitleSpriteColors(sobj);

            if (sMNOptionSoundMonoOrStereo == 1) 
            {
                sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionStereoTextJapSprite));
            }
            else
            {
                sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionMonoTextJapSprite));
            }

            sobj->pos.x = 169.0F;
            sobj->pos.y = 196.0F;

            mnOptionSetSubtitleSpriteColors(sobj);
            return;

        case nMNOptionOptionScreenAdjust:
            sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionScreenAdjustTextJapSprite));
            
            sobj->pos.x = 120.0F;
            sobj->pos.y = 195.0F;
            
            mnOptionSetSubtitleSpriteColors(sobj);
            return;

        case nMNOptionOptionBackupClear:
            sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionBackupClearTextJapSprite));
            
            sobj->pos.x = 104.0F;
            sobj->pos.y = 195.0F;
            
            mnOptionSetSubtitleSpriteColors(sobj);
            return;
    }
#endif
}

// 0x80132248
void mnOptionLabelsProcDisplay(GObj *gobj)
{
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);
    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 160, 120, 20, 230);
    gDPSetCombineMode(gSYTaskmanDLHeads[0]++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_XLU_SURF, G_RM_AA_XLU_SURF2);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 225, 143, 310, 230);
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_ZB_OPA_SURF, G_RM_AA_ZB_OPA_SURF2);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);

    lbCommonClearExternSpriteParams();
    lbCommonDrawSObjAttr(gobj);
}

// 0x8013238C
void mnOptionMakeLabels(void)
{
    GObj *gobj;
    SObj *sobj;

    gobj = gcMakeGObjSPAfter(0, NULL, 3, GOBJ_PRIORITY_DEFAULT);

    gcAddGObjDisplay(gobj, mnOptionLabelsProcDisplay, 1, GOBJ_PRIORITY_DEFAULT, ~0);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonSmashLogoSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x00;
    sobj->sprite.green = 0x00;
    sobj->sprite.blue  = 0x00;

    sobj->pos.x = 235.0F;
    sobj->pos.y = 158.0F;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionOptionTextSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x00;
    sobj->sprite.green = 0x00;
    sobj->sprite.blue  = 0x00;

    sobj->pos.x = 201.0F;
    sobj->pos.y = 120.0F;
}

// 0x80132484
void mnOptionMakeDecals(void)
{
    GObj *gobj;
    SObj *sobj;

    gobj = gcMakeGObjSPAfter(0, NULL, 2, GOBJ_PRIORITY_DEFAULT);
    gcAddGObjDisplay(gobj, lbCommonDrawSObjAttr, 0, GOBJ_PRIORITY_DEFAULT, ~0);

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonSmashBrosCollageSprite));

    sobj->pos.x = 10.0F;
    sobj->pos.y = 10.0F;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonDecalPaperSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0xA0;
    sobj->sprite.green = 0x78;
    sobj->sprite.blue  = 0x14;

    sobj->pos.x = 140.0F;
    sobj->pos.y = 143.0F;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[0], &llMNCommonDecalPaperSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0xA0;
    sobj->sprite.green = 0x78;
    sobj->sprite.blue  = 0x14;

    sobj->pos.x = 225.0F;
    sobj->pos.y = 56.0F;

    sobj = lbCommonMakeSObjForGObj(gobj, lbRelocGetFileData(Sprite*, sMNOptionFiles[1], &llMNOptionSettingsIconDarkSprite));

    sobj->sprite.attr &= ~SP_FASTCOPY;
    sobj->sprite.attr |= SP_TRANSPARENT;

    sobj->sprite.red   = 0x99;
    sobj->sprite.green = 0x99;
    sobj->sprite.blue  = 0x99;

    sobj->pos.x = 10.0F;
    sobj->pos.y = 10.0F;
}

// 0x80132618 - Unused?
void func_ovl60_80132618(GObj *gobj)
{
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);
    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0x66, 0x4C, 0x0C, 0x66);
    gDPSetCombineMode(gSYTaskmanDLHeads[0]++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_XLU_SURF, G_RM_AA_XLU_SURF2);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 27, 25, 185, 122);
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_ZB_OPA_SURF, G_RM_AA_ZB_OPA_SURF2);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);

    lbCommonClearExternSpriteParams();
    lbCommonDrawSObjAttr(gobj);
}

// 0x8013275C
void func_ovl60_8013275C(void)
{
    if (D_ovl60_801337D4 != NULL)
    {
        gcEjectGObj(D_ovl60_801337D4);

        D_ovl60_801337D4 = NULL;
    }
}

// 0x80132794 - Unused?
void func_ovl60_80132794(GObj *gobj)
{
    if (sMNOptionTotalTimeTics == D_ovl60_801337D8)
    {
        func_ovl60_8013275C();
    }
}

// 0x801327CC - Unused?
void func_ovl60_801327CC(void)
{
    return;
}

// 0x801327D4
void mnOptionSoundUnderlineProcDisplay(GObj *gobj)
{
    // 0x801336AC
    SYRectangle rect[/* */] =
    {
        { 233,  64, 273,  64 },
        { 179,  64, 225,  64 }
    };

    // 0x801336CC
    SYRectangle unused[/* */] =
    {
        {  0xE9,  0x5E, 0x106,  0x5E },
        {  0xC8,  0x5E,  0xE2,  0x5E }
    };

    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_FILL);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_NOOP, G_RM_NOOP2);
    gDPSetFillColor(gSYTaskmanDLHeads[0]++, syVideoGetFillColor(GPACK_RGBA8888(0xFF, 0xFF, 0xFF, 0xFF)));

    if (sMNOptionOption == nMNOptionOptionSound)
    {
        gDPFillRectangle
        (
            gSYTaskmanDLHeads[0]++,
            rect[sMNOptionSoundMonoOrStereo].ulx,
            rect[sMNOptionSoundMonoOrStereo].uly,
            rect[sMNOptionSoundMonoOrStereo].lrx,
            rect[sMNOptionSoundMonoOrStereo].lry
        );
    }
    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_ZB_OPA_SURF, G_RM_AA_ZB_OPA_SURF2);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);

    lbCommonClearExternSpriteParams();
}

// 0x801329F4
void mnOptionMakeSoundUnderline(void)
{
    gcAddGObjDisplay
    (
        gcMakeGObjSPAfter
        (
            0,
            NULL,
            5,
            GOBJ_PRIORITY_DEFAULT
        ),
        mnOptionSoundUnderlineProcDisplay,
        3,
        GOBJ_PRIORITY_DEFAULT,
        ~0
    );
}

// 0x80132A40
void mnOptionMakeSoundUnderlineCamera(void)
{
    CObj *cobj = CObjGetStruct
    (
        gcMakeCameraGObj
        (
            1,
            NULL,
            1,
            GOBJ_PRIORITY_DEFAULT,
            lbCommonDrawSprite,
            20,
            COBJ_MASK_DLLINK(3),
            ~0,
            FALSE,
            nGCProcessKindFunc,
            NULL,
            1,
            FALSE
        )
    );
    syRdpSetViewport(&cobj->viewport, 10.0F, 10.0F, 310.0F, 230.0F);
}

// 0x80132AE0
void mnOptionMakeLink4Camera(void)
{
    CObj *cobj = CObjGetStruct
    (
        gcMakeCameraGObj
        (
            1,
            NULL,
            1,
            GOBJ_PRIORITY_DEFAULT,
            lbCommonDrawSprite,
            10,
            COBJ_MASK_DLLINK(4),
            ~0,
            FALSE,
            nGCProcessKindFunc,
            NULL,
            1,
            FALSE
        )
    );
    syRdpSetViewport(&cobj->viewport, 10.0F, 10.0F, 310.0F, 230.0F);
}

// 0x80132B80
void mnOptionMakeOptionsCamera(void)
{
    CObj *cobj = CObjGetStruct
    (
        gcMakeCameraGObj
        (
            1,
            NULL,
            1,
            GOBJ_PRIORITY_DEFAULT,
            lbCommonDrawSprite,
            40,
            COBJ_MASK_DLLINK(2),
            ~0,
            FALSE,
            nGCProcessKindFunc,
            NULL,
            1,
            FALSE
        )
    );
    syRdpSetViewport(&cobj->viewport, 10.0F, 10.0F, 310.0F, 230.0F);
}

// 0x80132C20
void mnOptionMakeLabelsCamera(void)
{
    CObj *cobj = CObjGetStruct
    (
        gcMakeCameraGObj
        (
            1,
            NULL,
            1,
            GOBJ_PRIORITY_DEFAULT,
            lbCommonDrawSprite,
            60,
            COBJ_MASK_DLLINK(1),
            ~0,
            FALSE,
            nGCProcessKindFunc,
            NULL,
            1,
            FALSE
        )
    );
    syRdpSetViewport(&cobj->viewport, 10.0F, 10.0F, 310.0F, 230.0F);
}

// 0x80132CC0
void mnOptionMakeDecalsCamera(void)
{
    CObj *cobj = CObjGetStruct
    (
        gcMakeCameraGObj
        (
            1,
            NULL,
            1,
            GOBJ_PRIORITY_DEFAULT,
            lbCommonDrawSprite,
            80,
            COBJ_MASK_DLLINK(0),
            ~0,
            FALSE,
            nGCProcessKindFunc,
            NULL,
            1,
            FALSE
        )
    );
    syRdpSetViewport(&cobj->viewport, 10.0F, 10.0F, 310.0F, 230.0F);
}

void mnOptionBuilderBackdropProcDisplay(GObj *gobj)
{
    s32 cursor_row;
    s32 start;
    s32 cursor_y;

    if (sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_SLOTS)
    {
        cursor_row = sMNOptionBuilderSlot;
    }
    else
    {
        start = sMNOptionBuilderEntry - 5;

        if (start < 0)
        {
            start = 0;
        }
        if (start > (MNOPTION_BUILDER_ENTRY_COUNT - MNOPTION_BUILDER_VISIBLE_COUNT))
        {
            start = MNOPTION_BUILDER_ENTRY_COUNT - MNOPTION_BUILDER_VISIBLE_COUNT;
        }
        cursor_row = sMNOptionBuilderEntry - start;
    }
    cursor_y = MNOPTION_BUILDER_ROW_Y + (cursor_row * MNOPTION_BUILDER_ROW_HEIGHT);

    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetCycleType(gSYTaskmanDLHeads[0]++, G_CYC_1CYCLE);
    gDPSetCombineMode(gSYTaskmanDLHeads[0]++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_XLU_SURF, G_RM_AA_XLU_SURF2);

    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0x22, 0x1C, 0x30, 0xF0);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 10, 10, 310, 230);

    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0x00, 0x00, 0x00, 0xFF);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 24, 18, 296, 40);

    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0x5F, 0x58, 0x46, 0xFF);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 24, 18, 28, 40);

    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0xF2, 0xC7, 0x0D, 0xFF);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 30, 44, 290, 44);
    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0x9C, 0x20, 0x30, 0xFF);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 30, cursor_y - 2, 290, cursor_y + 10);
    gDPSetPrimColor(gSYTaskmanDLHeads[0]++, 0, 0, 0xFF, 0xD8, 0x4A, 0xFF);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 32, cursor_y + 2, 35, cursor_y + 8);
    gDPFillRectangle(gSYTaskmanDLHeads[0]++, 32, cursor_y + 11, 288, cursor_y + 11);

    gDPPipeSync(gSYTaskmanDLHeads[0]++);
    gDPSetRenderMode(gSYTaskmanDLHeads[0]++, G_RM_AA_ZB_OPA_SURF, G_RM_AA_ZB_OPA_SURF2);
    lbCommonClearExternSpriteParams();
}

void mnOptionBuilderMakeBackdrop(void)
{
    sMNOptionBuilderBackdropGObj = gcMakeGObjSPAfter(0, NULL, 6, GOBJ_PRIORITY_DEFAULT);
    gcAddGObjDisplay(sMNOptionBuilderBackdropGObj, mnOptionBuilderBackdropProcDisplay, 4, GOBJ_PRIORITY_DEFAULT, ~0);
}

const char* mnOptionBuilderGetFighterName(s32 fkind)
{
    // These names deliberately fit the narrow value column in the editor.
    const char *names[/* */] =
    {
        "MARIO", "FOX", "DONKEY", "SAMUS", "LUIGI", "LINK",
        "YOSHI", "CAPTAIN", "KIRBY", "PIKACHU", "JIGGLY", "NESS"
    };

    return names[fkind];
}

void mnOptionBuilderMakeSlotList(GObj *gobj)
{
    const char *names[] = { "BUILD ONE", "BUILD TWO", "BUILD THREE", "BUILD FOUR",
        "PLAYER ONE", "PLAYER TWO", "PLAYER THREE", "PLAYER FOUR", "PLAY VS" };
    u32 gold[3] = { 0xFF, 0xD8, 0x4A };
    u32 white[3] = { 0xFF, 0xFF, 0xFF };
    const char *value;
    s32 i, preset;
    mnOptionMakeString(gobj, "OPTIONS", 36.0F, 25.0F, white, FALSE);
    mnOptionMakeString(gobj, "CHARACTER LAB", 288.0F, 25.0F, gold, TRUE);
    for (i = 0; i < MNOPTION_BUILDER_SLOT_ROWS; i++)
    {
        mnOptionMakeString(gobj, names[i], MNOPTION_BUILDER_ROW_X, MNOPTION_BUILDER_ROW_Y + i * MNOPTION_BUILDER_ROW_HEIGHT, white, FALSE);
        value = NULL;
        if (i < 4) value = mnOptionBuilderGetFighterName(gSCManagerCharBuilderSlots[i].body);
        else if (i < 8)
        {
            preset = gSCManagerCharBuilderPlayerSlots[i - 4];
            value = (preset < 0) ? "VANILLA" : names[preset];
        }
        if (value != NULL) mnOptionMakeString(gobj, value, MNOPTION_BUILDER_VALUE_X, MNOPTION_BUILDER_ROW_Y + i * MNOPTION_BUILDER_ROW_HEIGHT, gold, TRUE);
    }
    mnOptionMakeString(gobj, "A EDIT   B BACK", 38.0F, 198.0F, gold, FALSE);
    mnOptionMakeString(gobj, "LR ASSIGN   HUMAN OR CPU", 38.0F, 212.0F, white, FALSE);
}

void mnOptionBuilderAssignPlayer(s32 add)
{
    s32 player = sMNOptionBuilderSlot - 4;
    s32 preset = gSCManagerCharBuilderPlayerSlots[player] + add;
    if (preset >= SCCHARBUILDER_SLOTS_COUNT) preset = -1;
    if (preset < -1) preset = SCCHARBUILDER_SLOTS_COUNT - 1;
    gSCManagerCharBuilderPlayerSlots[player] = preset;
    if (preset >= 0)
    {
        gSCManagerCharBuilderSlots[preset].is_enabled = TRUE;
        gSCManagerTransferBattleState.players[player].fkind = gSCManagerCharBuilderSlots[preset].body;
        gSCManagerTransferBattleState.players[player].costume = 0;
    }
}

void mnOptionBuilderMakeEditor(GObj *gobj)
{
    const char *slot_names[/* */] = { "BUILD ONE", "BUILD TWO", "BUILD THREE", "BUILD FOUR" };
    const char *entry_names[/* */] =
    {
        "ENABLED", "BODY", "USE BODY FOR ALL", "JAB", "DASH ATTACK", "FORWARD TILT", "UP TILT",
        "DOWN TILT", "FORWARD SMASH", "UP SMASH", "DOWN SMASH", "NEUTRAL AIR", "FORWARD AIR",
        "BACK AIR", "UP AIR", "DOWN AIR", "GRAB", "FORWARD THROW", "BACK THROW", "NEUTRAL B", "UP B", "DOWN B", "RANDOMIZE ATTACKS", "TEST IN TRAINING"
    };
    SCCharBuilderSlot *slot = &gSCManagerCharBuilderSlots[sMNOptionBuilderSlot];
    u32 title_color[3] = { 0xFF, 0xD8, 0x4A };
    u32 header_color[3] = { 0x5F, 0x58, 0x46 };
    u32 normal_color[3] = { 0xFF, 0xFF, 0xFF };
    const char *value;
    s32 start;
    s32 end;
    s32 i;

    start = sMNOptionBuilderEntry - 5;

    if (start < 0)
    {
        start = 0;
    }
    if (start > (MNOPTION_BUILDER_ENTRY_COUNT - MNOPTION_BUILDER_VISIBLE_COUNT))
    {
        start = MNOPTION_BUILDER_ENTRY_COUNT - MNOPTION_BUILDER_VISIBLE_COUNT;
    }
    end = start + MNOPTION_BUILDER_VISIBLE_COUNT;
    mnOptionMakeString(gobj, "OPTIONS", 36.0F, 25.0F, header_color, FALSE);
    mnOptionMakeString(gobj, slot_names[sMNOptionBuilderSlot], 288.0F, 24.0F, title_color, TRUE);

    for (i = start; i < end; i++)
    {
        mnOptionMakeString(gobj, entry_names[i], MNOPTION_BUILDER_ROW_X, MNOPTION_BUILDER_ROW_Y + ((i - start) * MNOPTION_BUILDER_ROW_HEIGHT), normal_color, FALSE);

        value = NULL;

        if (i == 0)
        {
            value = slot->is_enabled ? "ON" : "OFF";
        }
        else if (i == 1)
        {
            value = mnOptionBuilderGetFighterName(slot->body);
        }
        else if ((i >= 3) && (i <= 18))
        {
            value = mnOptionBuilderGetFighterName(slot->attacks[i - 3]);
        }
        else if (i == 19)
        {
            value = (slot->special_n == nSCCharBuilderNeutralFoxLaser) ? "FOX LASER" : "BODY MOVE";
        }
        else if (i == 20)
        {
            value = mnOptionBuilderGetFighterName(slot->special_hi);
        }
        else if (i == 21)
        {
            value = mnOptionBuilderGetFighterName(slot->special_lw);
        }
        if (value != NULL)
        {
            mnOptionMakeString(gobj, value, MNOPTION_BUILDER_VALUE_X, MNOPTION_BUILDER_ROW_Y + ((i - start) * MNOPTION_BUILDER_ROW_HEIGHT), normal_color, TRUE);
        }
    }
    mnOptionMakeString(gobj, "LR CHANGE   A OK   B BACK", 38.0F, 220.0F, title_color, FALSE);
}

void mnOptionBuilderRedraw(void)
{
    if (sMNOptionBuilderTextGObj != NULL)
    {
        gcEjectGObj(sMNOptionBuilderTextGObj);
    }
    sMNOptionBuilderTextGObj = gcMakeGObjSPAfter(0, NULL, 7, GOBJ_PRIORITY_DEFAULT);
    gcAddGObjDisplay(sMNOptionBuilderTextGObj, lbCommonDrawSObjAttr, 4, GOBJ_PRIORITY_DEFAULT, ~0);

    if (sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_SLOTS)
    {
        mnOptionBuilderMakeSlotList(sMNOptionBuilderTextGObj);
    }
    else mnOptionBuilderMakeEditor(sMNOptionBuilderTextGObj);
}

void mnOptionBuilderRandomize(void)
{
    SCCharBuilderSlot *slot = &gSCManagerCharBuilderSlots[sMNOptionBuilderSlot];
    u32 seed = sMNOptionTotalTimeTics + (sMNOptionBuilderSlot * 7919);
    s32 i;

    for (i = 0; i < SCCHARBUILDER_ATTACKS_COUNT; i++)
    {
        seed = (seed * 1103515245) + 12345;
        slot->attacks[i] = (seed >> 16) % (nFTKindPlayableEnd + 1);
    }
    seed = (seed * 1103515245) + 12345;
    slot->special_hi = (seed >> 16) % (nFTKindPlayableEnd + 1);
    slot->special_n = (seed >> 15) & 1;
    seed = (seed * 1103515245) + 12345;
    slot->special_lw = (seed >> 16) % (nFTKindPlayableEnd + 1);

    if (slot->special_lw == nFTKindKirby)
    {
        slot->special_lw = nFTKindSamus;
    }
}

void mnOptionBuilderChangeValue(s32 add)
{
    SCCharBuilderSlot *slot = &gSCManagerCharBuilderSlots[sMNOptionBuilderSlot];
    u8 *value;

    if (sMNOptionBuilderEntry == 0)
    {
        slot->is_enabled = (slot->is_enabled == FALSE) ? TRUE : FALSE;
        return;
    }
    if (sMNOptionBuilderEntry == 1)
    {
        value = &slot->body;
    }
    else if ((sMNOptionBuilderEntry >= 3) && (sMNOptionBuilderEntry <= 18))
    {
        value = &slot->attacks[sMNOptionBuilderEntry - 3];
    }
    else if (sMNOptionBuilderEntry == 19)
    {
        slot->special_n = (slot->special_n == nSCCharBuilderNeutralFoxLaser) ?
            nSCCharBuilderNeutralBody : nSCCharBuilderNeutralFoxLaser;
        return;
    }
    else if (sMNOptionBuilderEntry == 20)
    {
        value = &slot->special_hi;
    }
    else if (sMNOptionBuilderEntry == 21)
    {
        value = &slot->special_lw;
    }
    else return;

    do
    {
        if (add > 0)
        {
            *value = (*value == nFTKindPlayableEnd) ? nFTKindMario : *value + 1;
        }
        else *value = (*value == nFTKindMario) ? nFTKindPlayableEnd : *value - 1;
    }
    while ((sMNOptionBuilderEntry == 21) && (*value == nFTKindKirby));
}

void mnOptionBuilderUseBodyForAll(void)
{
    SCCharBuilderSlot *slot = &gSCManagerCharBuilderSlots[sMNOptionBuilderSlot];
    s32 i;

    for (i = 0; i < SCCHARBUILDER_ATTACKS_COUNT; i++)
    {
        slot->attacks[i] = slot->body;
    }
    slot->special_hi = slot->body;
    slot->special_lw = slot->body;
    slot->special_n = nSCCharBuilderNeutralBody;
}

void mnOptionBuilderTestInTraining(void)
{
    SCCharBuilderSlot *slot = &gSCManagerCharBuilderSlots[sMNOptionBuilderSlot];

    slot->is_enabled = TRUE;
    gSCManagerCharBuilderPlayerSlots[0] = sMNOptionBuilderSlot;
    gSCManagerSceneData.player = 0;
    gSCManagerSceneData.training_man_fkind = slot->body;
    gSCManagerSceneData.training_man_costume = 0;
    gSCManagerSceneData.training_com_fkind = nFTKindNull;
    gSCManagerSceneData.training_com_costume = 0;
    gSCManagerSceneData.scene_prev = gSCManagerSceneData.scene_curr;
    gSCManagerSceneData.scene_curr = nSCKindPlayers1PTraining;
    sMNOptionIsProceedScene = TRUE;
}

void mnOptionBuilderExit(void)
{
    gcEjectGObj(sMNOptionBuilderTextGObj);
    gcEjectGObj(sMNOptionBuilderBackdropGObj);
    sMNOptionBuilderTextGObj = NULL;
    sMNOptionBuilderBackdropGObj = NULL;
    sMNOptionBuilderMode = MNOPTION_BUILDER_MODE_NONE;
}

void mnOptionBuilderRun(void)
{
    sb32 stick_range;
    s32 is_button;
    sb32 is_up;
    sb32 is_down;
    sb32 is_left;
    sb32 is_right;

    is_up = mnOptionCheckGetOptionButtonInput(is_button, U_JPAD | U_CBUTTONS) || mnOptionCheckGetOptionStickInputUD(stick_range, 20, 1);
    is_down = mnOptionCheckGetOptionButtonInput(is_button, D_JPAD | D_CBUTTONS) || mnOptionCheckGetOptionStickInputUD(stick_range, -20, 0);
    is_left = mnOptionCheckGetOptionButtonInput(is_button, L_JPAD | L_CBUTTONS) || mnOptionCheckGetOptionStickInputLR(stick_range, -20, 0);
    is_right = mnOptionCheckGetOptionButtonInput(is_button, R_JPAD | R_CBUTTONS) || mnOptionCheckGetOptionStickInputLR(stick_range, 20, 1);

    if (is_up || is_down)
    {
        func_800269C0_275C0(nSYAudioFGMMenuScroll2);
        sMNOptionOptionChangeWait = 10;

        if (sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_SLOTS)
        {
            sMNOptionBuilderSlot = is_up ? ((sMNOptionBuilderSlot == 0) ? MNOPTION_BUILDER_SLOT_ROWS - 1 : sMNOptionBuilderSlot - 1) : ((sMNOptionBuilderSlot + 1) % MNOPTION_BUILDER_SLOT_ROWS);
        }
        else
        {
            sMNOptionBuilderEntry = is_up ? ((sMNOptionBuilderEntry == 0) ? MNOPTION_BUILDER_ENTRY_COUNT - 1 : sMNOptionBuilderEntry - 1) : ((sMNOptionBuilderEntry + 1) % MNOPTION_BUILDER_ENTRY_COUNT);
        }
        mnOptionBuilderRedraw();
        return;
    }
    if ((sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_SLOTS) &&
        (sMNOptionBuilderSlot >= 4) && (sMNOptionBuilderSlot < 8) && (is_left || is_right))
    {
        mnOptionBuilderAssignPlayer(is_right ? 1 : -1);
        func_800269C0_275C0(nSYAudioFGMMenuScroll1);
        sMNOptionOptionChangeWait = 10;
        mnOptionBuilderRedraw();
        return;
    }
    if ((sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_EDIT) && (is_left || is_right))
    {
        mnOptionBuilderChangeValue(is_right ? 1 : -1);
        func_800269C0_275C0(nSYAudioFGMMenuScroll1);
        sMNOptionOptionChangeWait = 10;
        mnOptionBuilderRedraw();
        return;
    }
    if (scSubsysControllerGetPlayerTapButtons(B_BUTTON) != FALSE)
    {
        func_800269C0_275C0(nSYAudioFGMMenuSelect);

        if (sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_EDIT)
        {
            sMNOptionBuilderMode = MNOPTION_BUILDER_MODE_SLOTS;
            mnOptionBuilderRedraw();
        }
        else mnOptionBuilderExit();
        return;
    }
    if (scSubsysControllerGetPlayerTapButtons(A_BUTTON | START_BUTTON) != FALSE)
    {
        func_800269C0_275C0(nSYAudioFGMMenuSelect);

        if (sMNOptionBuilderMode == MNOPTION_BUILDER_MODE_SLOTS)
        {
            if (sMNOptionBuilderSlot == 8)
            {
                mnOptionWriteBackup();
                gSCManagerSceneData.scene_prev = gSCManagerSceneData.scene_curr;
                gSCManagerSceneData.scene_curr = nSCKindPlayersVS;
                sMNOptionIsProceedScene = TRUE;
                return;
            }
            if (sMNOptionBuilderSlot >= 4)
            {
                mnOptionBuilderAssignPlayer(1);
                mnOptionBuilderRedraw();
                return;
            }
            sMNOptionBuilderMode = MNOPTION_BUILDER_MODE_EDIT;
            sMNOptionBuilderEntry = 0;
            mnOptionBuilderRedraw();
            return;
        }
        switch (sMNOptionBuilderEntry)
        {
        case 2:
            mnOptionBuilderUseBodyForAll();
            break;

        case 22:
            mnOptionBuilderRandomize();
            break;

        case 23:
            mnOptionBuilderTestInTraining();
            return;

        default:
            mnOptionBuilderChangeValue(1);
            break;
        }
        mnOptionBuilderRedraw();
    }
}

// 0x80132D60
void mnOptionInitVars(void)
{
    switch (gSCManagerSceneData.scene_prev)
    {
    case nSCKindScreenAdjust:
        sMNOptionOption = nMNOptionOptionScreenAdjust;
        break;

    case nSCKindBackupClear:
        sMNOptionOption = nMNOptionOptionBackupClear;
        break;

    default:
        sMNOptionOption = nMNOptionOptionSound;
        break;
    }
    sMNOptionOptionChangeWait = 0;

    sMNOptionSoundMonoOrStereo = (dSYAudioSoundQuality == 1) ? 1 : 0;

    sMNOptionIsScreenFlash = gSCManagerBackupData.is_allow_screenflash;
    sMNOptionTotalTimeTics = 0;
    D_ovl60_801337D4 = NULL;
    sMNOptionIsProceedScene = FALSE;
    sMNOptionReturnTic = sMNOptionTotalTimeTics + I_MIN_TO_TICS(5);
    sMNOptionBuilderMode = MNOPTION_BUILDER_MODE_NONE;
    sMNOptionBuilderSlot = 0;
    sMNOptionBuilderEntry = 0;
    sMNOptionBuilderBackdropGObj = NULL;
    sMNOptionBuilderTextGObj = NULL;
}

// 0x80132E10
void mnOptionWriteBackup(void)
{
    gSCManagerBackupData.is_allow_screenflash = sMNOptionIsScreenFlash;
    gSCManagerBackupData.sound_mono_or_stereo = sMNOptionSoundMonoOrStereo;

    lbBackupWrite();
}

// 0x80132E4C
void mnOptionFuncRun(GObj *gobj)
{
    GObj *select_gobj;
    sb32 stick_range;

    // 0x801336EC
    GObj **option_gobjs[/* */] = { &sMNOptionOptionSoundGObj, &sMNOptionOptionScreenAdjustGObj, &sMNOptionOptionBackupClearGObj, &sMNOptionOptionCharBuilderGObj };

    s32 is_button;

    sMNOptionTotalTimeTics++;

    if (sMNOptionTotalTimeTics >= 10)
    {
        if (sMNOptionTotalTimeTics == sMNOptionReturnTic)
        {
            gSCManagerSceneData.scene_prev = gSCManagerSceneData.scene_curr;
            gSCManagerSceneData.scene_curr = nSCKindTitle;

            mnOptionWriteBackup();
            syTaskmanSetLoadScene();

            return;
        }
        if (scSubsysControllerCheckNoInputAll() == FALSE)
        {
            sMNOptionReturnTic = sMNOptionTotalTimeTics + I_MIN_TO_TICS(5);
        }
        if (sMNOptionIsProceedScene != FALSE)
        {
            syTaskmanSetLoadScene();
        }
        if (sMNOptionOptionChangeWait != 0)
        {
            sMNOptionOptionChangeWait--;
        }
        if
        (
            (scSubsysControllerGetPlayerStickInRangeLR(-20, 20) != FALSE)           &&
            (scSubsysControllerGetPlayerStickInRangeUD(-20, 20) != FALSE)           &&
            (scSubsysControllerGetPlayerHoldButtons(U_JPAD | U_CBUTTONS) == FALSE)  &&
            (scSubsysControllerGetPlayerHoldButtons(D_JPAD | D_CBUTTONS) == FALSE)
        )
        {
            sMNOptionOptionChangeWait = 0;
        }
        if (sMNOptionBuilderMode != MNOPTION_BUILDER_MODE_NONE)
        {
            mnOptionBuilderRun();
            return;
        }
        if (scSubsysControllerGetPlayerTapButtons(A_BUTTON | START_BUTTON) != FALSE)
        {
            switch (sMNOptionOption)
            {
            case nMNOptionOptionScreenAdjust:
                mnOptionWriteBackup();

                func_800269C0_275C0(nSYAudioFGMMenuSelect);

                mnOptionSetOptionSpriteColors(*option_gobjs[sMNOptionOption], nMNOptionTabStatusSelected);

                gSCManagerSceneData.scene_prev = gSCManagerSceneData.scene_curr;
                gSCManagerSceneData.scene_curr = nSCKindScreenAdjust;

                sMNOptionIsProceedScene = TRUE;
                return;

            case nMNOptionOptionBackupClear:
                mnOptionWriteBackup();

                func_800269C0_275C0(nSYAudioFGMMenuSelect);

                mnOptionSetOptionSpriteColors(*option_gobjs[sMNOptionOption], nMNOptionTabStatusSelected);

                gSCManagerSceneData.scene_prev = gSCManagerSceneData.scene_curr;
                gSCManagerSceneData.scene_curr = nSCKindBackupClear;

                sMNOptionIsProceedScene = TRUE;
                return;

            case nMNOptionOptionCharBuilder:
                func_800269C0_275C0(nSYAudioFGMMenuSelect);
                sMNOptionBuilderMode = MNOPTION_BUILDER_MODE_SLOTS;
                mnOptionBuilderMakeBackdrop();
                mnOptionBuilderRedraw();
                return;
            }
        }
        if (scSubsysControllerGetPlayerTapButtons(B_BUTTON) != FALSE)
        {
            mnOptionWriteBackup();

            gSCManagerSceneData.scene_prev = gSCManagerSceneData.scene_curr;
            gSCManagerSceneData.scene_curr = nSCKindModeSelect;

            syTaskmanSetLoadScene();
        }
        if
        (
            mnOptionCheckGetOptionButtonInput(is_button, U_JPAD | U_CBUTTONS) ||
            mnOptionCheckGetOptionStickInputUD(stick_range, 20, 1)
        )
        {
            func_800269C0_275C0(nSYAudioFGMMenuScroll2);

            mnOptionSetOptionChangeWaitP(is_button, stick_range, 7);

            mnOptionSetOptionSpriteColors(*option_gobjs[sMNOptionOption], nMNOptionTabStatusNot);

            if (sMNOptionOption == nMNOptionOptionStart)
            {
                sMNOptionOption = nMNOptionOptionEnd;
            }
            else sMNOptionOption--;

            mnOptionSetOptionSpriteColors(*option_gobjs[sMNOptionOption], nMNOptionTabStatusHighlight);
            gcEjectGObj(sMNOptionMenuGObj);
            mnOptionMakeMenuGObj();
        }
        if
        (
            mnOptionCheckGetOptionButtonInput(is_button, D_JPAD | D_CBUTTONS) ||
            mnOptionCheckGetOptionStickInputUD(stick_range, -20, 0)
        )
        {
            func_800269C0_275C0(nSYAudioFGMMenuScroll2);

            mnOptionSetOptionChangeWaitN(is_button, stick_range, 7);

            if (sMNOptionOption == nMNOptionOptionScreenAdjust)
            {
                sMNOptionOptionChangeWait += 8;
            }
            mnOptionSetOptionSpriteColors(*option_gobjs[sMNOptionOption], nMNOptionTabStatusNot);

            if (sMNOptionOption == nMNOptionOptionEnd)
            {
                sMNOptionOption = nMNOptionOptionStart;
            }
            else sMNOptionOption++;

            mnOptionSetOptionSpriteColors(*option_gobjs[sMNOptionOption], nMNOptionTabStatusHighlight);
            gcEjectGObj(sMNOptionMenuGObj);
            mnOptionMakeMenuGObj();
        }
        if (sMNOptionOption == nMNOptionOptionSound)
        {
            if
            (
                (scSubsysControllerGetPlayerTapButtons(L_JPAD | L_TRIG | L_CBUTTONS) != FALSE) ||
                (mnOptionCheckGetOptionStickInputLR(stick_range, -20, 0))
            )
            {
                if (sMNOptionSoundMonoOrStereo == 0)
                {
                    func_800269C0_275C0(nSYAudioFGMMenuScroll1);

                    sMNOptionSoundMonoOrStereo = 1;

                    gcEjectGObj(sMNOptionSoundOptionGObj);
                    mnOptionMakeSoundToggle();

                    sMNOptionOptionChangeWait = mnCommonGetOptionChangeWaitN(stick_range, 7);

                    gcEjectGObj(sMNOptionMenuGObj);
                    mnOptionMakeMenuGObj();
                    syAudioSetQuality(sMNOptionSoundMonoOrStereo);
                }
            }
            if
            (
                (scSubsysControllerGetPlayerTapButtons(R_JPAD | R_TRIG | R_CBUTTONS) != FALSE) ||
                (mnOptionCheckGetOptionStickInputLR(stick_range, 20, 1))
            )
            {
                if (sMNOptionSoundMonoOrStereo == 1)
                {
                    func_800269C0_275C0(nSYAudioFGMMenuScroll1);

                    sMNOptionSoundMonoOrStereo = 0;

                    gcEjectGObj(sMNOptionSoundOptionGObj);
                    mnOptionMakeSoundToggle();

                    sMNOptionOptionChangeWait = mnCommonGetOptionChangeWaitP(stick_range, 7);

                    gcEjectGObj(sMNOptionMenuGObj);
                    mnOptionMakeMenuGObj();
                    syAudioSetQuality(sMNOptionSoundMonoOrStereo);
                }
            }
            if (scSubsysControllerGetPlayerTapButtons(A_BUTTON) != FALSE)
            {
                func_800269C0_275C0(nSYAudioFGMMenuScroll1);

                if (sMNOptionSoundMonoOrStereo == 1)
                {
                    sMNOptionSoundMonoOrStereo = 0;
                }
                else sMNOptionSoundMonoOrStereo = 1;

                gcEjectGObj(sMNOptionSoundOptionGObj);
                mnOptionMakeSoundToggle();
                gcEjectGObj(sMNOptionMenuGObj);
                mnOptionMakeMenuGObj();
                syAudioSetQuality(sMNOptionSoundMonoOrStereo);
            }
        }
    }
}

// 0x8013346C
void mnOptionFuncStart(void)
{
    LBRelocSetup rl_setup;

    rl_setup.table_addr = (uintptr_t)&lLBRelocTableAddr;
    rl_setup.table_files_num = (u32)&llRelocFileCount;
    rl_setup.file_heap = NULL;
    rl_setup.file_heap_size = 0;
    rl_setup.status_buffer = sMNOptionStatusBuffer;
    rl_setup.status_buffer_size = ARRAY_COUNT(sMNOptionStatusBuffer);
    rl_setup.force_status_buffer = NULL;
    rl_setup.force_status_buffer_size = 0;

    lbRelocInitSetup(&rl_setup);
    lbRelocLoadFilesListed(dMNOptionFileIDs, sMNOptionFiles);
    gcMakeGObjSPAfter(0, mnOptionFuncRun, 0, GOBJ_PRIORITY_DEFAULT);
    gcMakeDefaultCameraGObj(0, GOBJ_PRIORITY_DEFAULT, 100, 0, GPACK_RGBA8888(0x00, 0x00, 0x00, 0x00));
    
    mnOptionInitVars();
    mnOptionMakeDecalsCamera();
    mnOptionMakeLabelsCamera();
    mnOptionMakeOptionsCamera();
    mnOptionMakeSoundUnderlineCamera();
    mnOptionMakeLink4Camera();
    mnOptionMakeDecals();
    mnOptionMakeLabels();
    mnOptionMakeSound();
    mnOptionMakeSoundToggle();
    mnOptionMakeScreenAdjust();
    mnOptionMakeBackupClear();
    mnOptionMakeCharBuilder();
    mnOptionMakeSoundUnderline();
    mnOptionMakeMenuGObj();

    if (gSCManagerSceneData.scene_prev == nSCKindScreenAdjust)
    {
        syAudioPlayBGM(0, nSYAudioBGMModeSelect);
    }
}

// 0x801336F8
SYVideoSetup dMNOptionVideoSetup = SYVIDEO_SETUP_DEFAULT();

// 0x80133714
SYTaskmanSetup dMNOptionTaskmanSetup =
{
    // Task Manager Buffer Setup
    {
        0,                          // ???
        gcRunAll,              		// Update function
        gcDrawAll,                  // Frame draw function
        &ovl60_BSS_END,             // Allocatable memory pool start
        0,                          // Allocatable memory pool size
        1,                          // ???
        2,                          // Number of contexts?
        sizeof(Gfx) * 7500,         // Display List Buffer 0 Size
        0,                          // Display List Buffer 1 Size
        0,                          // Display List Buffer 2 Size
        0,                          // Display List Buffer 3 Size
        0x8000,                     // Graphics Heap Size
        2,                          // ???
        0xC000,                     // RDP Output Buffer Size
        mnOptionFuncLights,         // Pre-render function
        syControllerFuncRead,       // Controller I/O function
    },

    0,                              // Number of GObjThreads
    sizeof(u64) * 192,              // Thread stack size
    0,                              // Number of thread stacks
    0,                              // ???
    0,                              // Number of GObjProcesses
    0,                              // Number of GObjs
    sizeof(GObj),                   // GObj size
    0,                              // Number of XObjs
    NULL,                           // Matrix function list
    NULL,                           // DObjVec eject function
    0,                              // Number of AObjs
    0,                              // Number of MObjs
    0,                              // Number of DObjs
    sizeof(DObj),                   // DObj size
    0,                              // Number of SObjs
    sizeof(SObj),                   // SObj size
    0,                              // Number of CObjs
    sizeof(CObj),                 	// CObj size
    
    mnOptionFuncStart               // Task start function
};

// 0x801335C0
void mnOptionStartScene(void)
{
    dMNOptionVideoSetup.zbuffer = SYVIDEO_ZBUFFER_START(320, 240, 0, 10, u16);
    syVideoInit(&dMNOptionVideoSetup);

    dMNOptionTaskmanSetup.scene_setup.arena_size = (size_t) ((uintptr_t)&ovl1_VRAM - (uintptr_t)&ovl60_BSS_END);
    syTaskmanStartTask(&dMNOptionTaskmanSetup);
}
