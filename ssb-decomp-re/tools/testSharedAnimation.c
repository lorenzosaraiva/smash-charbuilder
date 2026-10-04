/* Emit poses from the actual C retargeter, using original inverse-trig math. */
#define _start sharedHostTestsEntry
#include "testCustomMove.c"
#undef _start
static void output(void *data, u32 size)
{
    s32 written;
    __asm__ volatile("int $0x80":"=a"(written):"a"(4),"b"(1),"c"(data),"d"(size):"memory");
    if (written != size) __asm__ volatile("int $0x80"::"a"(1),"b"(100):"memory");
}
#include "../build/shared-animation-cases.inc"
void _start(void)
{
    FTStruct fp = { 0 };
    DObj joints[FTPARTS_JOINT_NUM_MAX] = { 0 };
    FTCustomAnimationQuat world[FTPARTS_JOINT_NUM_MAX], values[FTPARTS_JOINT_NUM_MAX];
    const FTCustomAnimationRig *rig;
    const FTCustomAnimationBone *bone;
    s32 c, body, frame, i;
    for (i = 0; i < FTPARTS_JOINT_NUM_MAX; i++) fp.joints[i] = &joints[i];
    for (c = 0; c < ARRAY_COUNT(sSharedOracleClips); c++) for (body = 0; body < 12; body++)
    {
        fp.fkind = body; rig = &sFTCustomAnimationRigs[body];
        for (frame = 0; frame < sSharedOracleClips[c]->count; frame++)
        {
            ftCustomAnimationSharedPose(&fp,sSharedOracleClips[c],frame);
            world[0] = (FTCustomAnimationQuat){0,0,0,1};
            for (i = 0; i < rig->count; i++)
            {
                Vec3f r;
                bone = &rig->bones[i]; r = joints[bone->joint].rotate.vec.f;
                world[bone->joint] = ftCustomAnimationMultiply(world[bone->parent],ftCustomAnimationFromEuler(r.x,r.y,r.z));
                values[i] = world[bone->joint];
            }
            output(values,rig->count*sizeof(*values));
            output(&joints[4].translate.vec.f,sizeof(Vec3f));
        }
    }
    __asm__ volatile("int $0x80"::"a"(1),"b"(0):"memory");
    __builtin_unreachable();
}
