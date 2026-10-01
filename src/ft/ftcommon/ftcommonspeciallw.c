#include <ft/fighter.h>

// // // // // // // // // // // //
//                               //
//       INITIALIZED DATA        //
//                               //
// // // // // // // // // // // //

// 0x80188D50
void (*dFTCommonSpecialLwStatusList[/* */])(GObj*) = 
{
    ftMarioSpecialLwSetStatus,
    ftFoxSpecialLwStartSetStatus,
    ftDonkeySpecialLwStartSetStatus,
    ftSamusSpecialLwSetStatus,
    ftMarioSpecialLwSetStatus,
    ftLinkSpecialLwSetStatus,
    ftYoshiSpecialLwStartSetStatus,
    ftCaptainSpecialLwSetStatus,
    ftKirbySpecialLwStartSetStatus,
    ftPikachuSpecialLwStartSetStatus,
    ftPurinSpecialLwSetStatus,
    ftNessSpecialLwStartSetStatus,
    ftMarioSpecialLwSetStatus,
    ftMarioSpecialLwSetStatus,
    ftMarioSpecialLwSetStatus,
    ftFoxSpecialLwStartSetStatus,
    ftDonkeySpecialLwStartSetStatus,
    ftSamusSpecialLwSetStatus,
    ftMarioSpecialLwSetStatus,
    ftLinkSpecialLwSetStatus,
    ftYoshiSpecialLwStartSetStatus,
    ftCaptainSpecialLwSetStatus,
    ftKirbySpecialLwStartSetStatus,
    ftPikachuSpecialLwStartSetStatus,
    ftPurinSpecialLwSetStatus,
    ftNessSpecialLwStartSetStatus,
    ftDonkeySpecialLwStartSetStatus
};

// // // // // // // // // // // //
//                               //
//           FUNCTIONS           //
//                               //
// // // // // // // // // // // //

// 0x801511E0
sb32 ftCommonSpecialLwCheckInterruptCommon(GObj *fighter_gobj)
{
    FTStruct *fp = ftGetStruct(fighter_gobj);
    FTAttributes *attr = fp->attr;
    s32 donor = ftMainCharBuilderGetSpecialLwKind(fighter_gobj);

    if ((fp->input.pl.button_tap & fp->input.button_mask_b) && ((attr->is_have_speciallw) || (donor != fp->fkind)) && (fp->input.pl.stick_range.y <= FTCOMMON_SPECIALLW_STICK_RANGE_MIN))
    {
        donor = ftMainCharBuilderSetSpecialLwDonor(fighter_gobj, donor);
        dFTCommonSpecialLwStatusList[donor](fighter_gobj);

        return TRUE;
    }
    else return FALSE;
}
