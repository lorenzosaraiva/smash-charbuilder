/* Pilot poses own no DObjs, scripts, animation heaps or fighter callbacks. */
typedef struct FTCustomAnimationJoint
{
    Vec3f rotate, translate;
} FTCustomAnimationJoint;

typedef struct FTCustomAnimationFrame
{
    FTCustomAnimationJoint joints[24]; /* Mario native IDs 4..27. */
    FTCustomCollisionFrame collision;
} FTCustomAnimationFrame;

#include "ftcustomanimations.generated.inc"
typedef struct FTCustomAnimationQuat { f32 x, y, z, w; } FTCustomAnimationQuat;
typedef struct FTCustomAnimationKey { u8 frame, hi, lo; } FTCustomAnimationKey;
typedef struct FTCustomAnimationCurve { u32 first; u16 count, reserved; } FTCustomAnimationCurve;
typedef struct FTCustomAnimationSourceBone { u8 joint, parent; u16 reserved; FTCustomAnimationQuat inverse; } FTCustomAnimationSourceBone;
typedef struct FTCustomAnimationSourceRig { const FTCustomAnimationSourceBone *bones; s32 count; u8 roles[24]; } FTCustomAnimationSourceRig;
typedef struct FTCustomAnimationClip
{
    const FTCustomAnimationSourceRig *rig;
    const u16 *channels;
    const Vec3h *root;
    s32 count, loop_start, loop_period;
} FTCustomAnimationClip;
typedef struct FTCustomAnimationBone
{
    u8 joint, parent; s8 role; u8 required;
    Vec3f translate, scale;
    FTCustomAnimationQuat local, world;
} FTCustomAnimationBone;
typedef struct FTCustomAnimationRig { const FTCustomAnimationBone *bones; s32 count; } FTCustomAnimationRig;
#include "ftcustomanimationshared.generated.inc"
u32 gFTCustomAnimationValidationFailures;
#ifdef FTCHARBUILDER_PAIRED_MOVES
static const FTCustomAnimationClip* ftCustomAnimationGetPairClip(FTStruct*, s32*);
#endif
#ifdef FTCHARBUILDER_SPECIAL_ANIMATIONS
static const FTCustomAnimationClip* ftCustomAnimationGetSpecialClip(FTStruct*, s32*);
static void ftMainCharBuilderStartSpecialVisualScript(FTStruct*, f32);
#endif

static FTCustomAnimationQuat ftCustomAnimationMultiply(FTCustomAnimationQuat a, FTCustomAnimationQuat b)
{
    FTCustomAnimationQuat q;
    q.x = a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y;
    q.y = a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x;
    q.z = a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w;
    q.w = a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z;
    return q;
}

static FTCustomAnimationQuat ftCustomAnimationInverse(FTCustomAnimationQuat q)
{
    q.x = -q.x; q.y = -q.y; q.z = -q.z;
    return q;
}

static f32 ftCustomAnimationReadCurve(const FTCustomAnimationCurve *curve, s32 frame)
{
    const FTCustomAnimationKey *keys = &sFTCustomAnimationKeys[curve->first];
    s32 low = 0, high = curve->count - 1, middle;
    f32 value;
    if (frame <= keys[0].frame) return (s16)((keys[0].hi << 8) | keys[0].lo) * (1.0F / 4096.0F);
    if (frame >= keys[high].frame) return (s16)((keys[high].hi << 8) | keys[high].lo) * (1.0F / 4096.0F);
    while (high - low > 1)
    {
        middle = (high + low) / 2;
        if (frame < keys[middle].frame) high = middle;
        else low = middle;
    }
    value = (s16)((keys[low].hi << 8) | keys[low].lo) + ((s16)((keys[high].hi << 8) | keys[high].lo) - (s16)((keys[low].hi << 8) | keys[low].lo)) *
        ((f32)(frame - keys[low].frame) / (keys[high].frame - keys[low].frame));
    return value * (1.0F / 4096.0F);
}

static FTCustomAnimationQuat ftCustomAnimationFromEuler(f32 x, f32 y, f32 z)
{
    f32 sx = __sinf(x * 0.5F), cx = __cosf(x * 0.5F);
    f32 sy = __sinf(y * 0.5F), cy = __cosf(y * 0.5F);
    f32 sz = __sinf(z * 0.5F), cz = __cosf(z * 0.5F);
    FTCustomAnimationQuat q;
    q.x = sx*cy*cz - cx*sy*sz; q.y = cx*sy*cz + sx*cy*sz;
    q.z = cx*cy*sz - sx*sy*cz; q.w = cx*cy*cz + sx*sy*sz;
    return q;
}

static Vec3f ftCustomAnimationToEuler(FTCustomAnimationQuat q)
{
    f32 inverse = 1.0F / sqrtf(q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w);
    f32 m00, m10, m20, m21, m22, m12, m11, cosine;
    Vec3f result;
    q.x *= inverse; q.y *= inverse; q.z *= inverse; q.w *= inverse;
    m00 = 1.0F - 2.0F*(q.y*q.y + q.z*q.z); m10 = 2.0F*(q.x*q.y + q.w*q.z);
    m20 = 2.0F*(q.x*q.z - q.w*q.y); m21 = 2.0F*(q.y*q.z + q.w*q.x);
    m22 = 1.0F - 2.0F*(q.x*q.x + q.y*q.y);
    cosine = sqrtf(m00*m00 + m10*m10);
    result.y = syUtilsArcTan2(-m20, cosine);
    if (cosine > 0.00001F)
    {
        result.x = syUtilsArcTan2(m21, m22); result.z = syUtilsArcTan2(m10, m00);
    }
    else
    {
        m12 = 2.0F*(q.y*q.z - q.w*q.x); m11 = 1.0F - 2.0F*(q.x*q.x + q.z*q.z);
        result.x = syUtilsArcTan2(-m12, m11); result.z = 0.0F;
    }
    return result;
}

static const FTCustomAnimationClip* ftCustomAnimationGetClip(FTStruct *fp, s32 *frame)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomAnimationClip *clip;
    u32 offset, index;
    if ((fp->fkind < 0) || (fp->fkind >= 12) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
#ifdef FTCHARBUILDER_PAIRED_MOVES
    clip = ftCustomAnimationGetPairClip(fp, frame);
    if (clip != NULL) return clip;
#endif
#ifdef FTCHARBUILDER_SPECIAL_ANIMATIONS
    clip = ftCustomAnimationGetSpecialClip(fp, frame);
    if (clip != NULL) return clip;
#endif
    if (clock == NULL) return NULL;
    offset = (u32)clock->move - (u32)sFTCustomMoves;
    if ((offset >= sizeof(sFTCustomMoves)) || (offset % sizeof(FTCustomMoveDefinition))) return NULL;
    index = offset / sizeof(FTCustomMoveDefinition);
    clip = sFTCustomAnimationClips[index / 33][index % 33];
    if (clip == NULL) return NULL;
    *frame = (s32)clock->frame;
    if (*frame < 0) *frame = 0;
    if ((clip->loop_period > 0) && (*frame >= clip->loop_start))
        *frame = clip->loop_start + (*frame - clip->loop_start) % clip->loop_period;
    if (*frame >= clip->count) *frame = clip->count - 1;
    return clip;
}

static void ftCustomAnimationSharedPose(FTStruct *fp, const FTCustomAnimationClip *clip, s32 frame)
{
    FTCustomAnimationQuat source[FTPARTS_JOINT_NUM_MAX], target[FTPARTS_JOINT_NUM_MAX], delta[24], local, desired;
    const FTCustomAnimationRig *body = &sFTCustomAnimationRigs[fp->fkind];
    const FTCustomAnimationSourceBone *src;
    const FTCustomAnimationBone *bone;
    const u16 *curves;
    DObj *joint;
    s32 i;
    f32 height;
    /* Validate the entire required native rig before changing any DObj. */
    for (i = 0; i < body->count; i++)
        if (body->bones[i].required && (fp->joints[body->bones[i].joint] == NULL))
        { gFTCustomAnimationValidationFailures++; return; }
    source[0].x = source[0].y = source[0].z = 0.0F; source[0].w = 1.0F;
    target[0] = source[0];
    for (i = 0; i < clip->rig->count; i++)
    {
        src = &clip->rig->bones[i]; curves = &clip->channels[i*3];
        local = ftCustomAnimationFromEuler(ftCustomAnimationReadCurve(&sFTCustomAnimationCurves[curves[0]], frame),
            ftCustomAnimationReadCurve(&sFTCustomAnimationCurves[curves[1]], frame), ftCustomAnimationReadCurve(&sFTCustomAnimationCurves[curves[2]], frame));
        source[src->joint] = ftCustomAnimationMultiply(source[src->parent], local);
    }
    for (i = 0; i < 24; i++)
    {
        src = &clip->rig->bones[clip->rig->roles[i]];
        delta[i] = ftCustomAnimationMultiply(source[src->joint], src->inverse);
    }
    /* Reserved cosmetic rotations are already included in the donor FK. */
    for (i = nFTPartsJointXRotN; i <= nFTPartsJointYRotN; i++)
    {
        joint = fp->joints[i]; if (joint == NULL) continue;
        joint->rotate.vec.f.x = joint->rotate.vec.f.y = joint->rotate.vec.f.z = 0.0F;
        joint->translate.vec.f.x = joint->translate.vec.f.y = joint->translate.vec.f.z = 0.0F;
        joint->scale.vec.f.x = joint->scale.vec.f.y = joint->scale.vec.f.z = 1.0F;
    }
    height = body->bones[0].translate.y;
    for (i = 0; i < body->count; i++)
    {
        bone = &body->bones[i];
        desired = (bone->role >= 0) ? ftCustomAnimationMultiply(delta[bone->role], bone->world) :
            ftCustomAnimationMultiply(target[bone->parent], bone->local);
        target[bone->joint] = desired;
        joint = fp->joints[bone->joint]; if (joint == NULL) continue;
        local = ftCustomAnimationMultiply(ftCustomAnimationInverse(target[bone->parent]), desired);
        joint->rotate.vec.f = ftCustomAnimationToEuler(local);
        joint->translate.vec.f = bone->translate; joint->scale.vec.f = bone->scale;
        if (bone->joint == 4)
        {
            joint->translate.vec.f.x += clip->root[frame].x * (height / 4096.0F);
            joint->translate.vec.f.y += clip->root[frame].y * (height / 4096.0F);
            joint->translate.vec.f.z += clip->root[frame].z * (height / 4096.0F);
        }
    }
}

static const FTCustomAnimationFrame* ftCustomAnimationGetFrame(FTStruct *fp)
{
    FTCustomMoveClock *clock = ftCustomMoveGetClock(fp);
    const FTCustomAnimationFrame *frames;
    s32 frame, count;
    if ((clock == NULL) || (fp->fkind != nFTKindMario) || (ftCustomMoveGetSlot(fp) == NULL)) return NULL;
    if (clock->move == &sFTCustomMoves[nFTKindCaptain][23])
    {
        frames = sFTCustomAnimationCaptain; count = ARRAY_COUNT(sFTCustomAnimationCaptain);
    }
    else if (clock->move == &sFTCustomMoves[nFTKindFox][5])
    {
        frames = sFTCustomAnimationFox; count = ARRAY_COUNT(sFTCustomAnimationFox);
    }
    else if (clock->move == &sFTCustomMoves[nFTKindDonkey][14])
    {
        frames = sFTCustomAnimationDonkey; count = ARRAY_COUNT(sFTCustomAnimationDonkey);
    }
    else return NULL;
    frame = (s32)clock->frame;
    if (frame < 0) frame = 0;
    if (frame >= count) frame = count - 1;
    return &frames[frame];
}

static void ftCustomAnimationApplyPose(FTStruct *fp)
{
    const FTCustomAnimationFrame *pilot = ftCustomAnimationGetFrame(fp);
    const FTCustomAnimationClip *clip;
    DObj *joint;
    s32 i, frame;
    if (pilot == NULL)
    {
        clip = ftCustomAnimationGetClip(fp, &frame);
        if (clip != NULL) ftCustomAnimationSharedPose(fp, clip, frame);
        return;
    }
    /* Keep the three visually accepted Mario pilots byte-for-byte unchanged. */
    for (i = 4; i < 28; i++) if (fp->joints[i] == NULL)
    { gFTCustomAnimationValidationFailures++; return; }
    for (i = 0; i < 24; i++)
    {
        joint = fp->joints[i + 4];
        joint->rotate.vec.f = pilot->joints[i].rotate;
        joint->translate.vec.f = pilot->joints[i].translate;
        joint->scale.vec.f.x = joint->scale.vec.f.y = joint->scale.vec.f.z = 1.0F;
    }
}
