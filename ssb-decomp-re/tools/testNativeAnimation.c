/* Freestanding 32-bit native-animation oracle. No N64 renderer/emulator. */
#include <ssb_types.h>
#include <macros.h>
#include <sys/objdef.h>
#define _FIGHTER_H_
#define _RELOCDATA_TYPES_H_
#define AOBJ_ANIM_NULL F32_MIN
#define AOBJ_ANIM_CHANGED (F32_MIN / 2.0F)
#define AOBJ_ANIM_END (F32_MIN / 3.0F)
#define GOBJ_FLAG_NOANIM (1 << 1)
#define DOBJ_PARENT_NULL ((DObj*)1)
#define AObjAnimAdvance(script) ((script)++)
#define DObjGetStruct(gobj) ((gobj)->dobj)
typedef union AObjEvent16
{
    struct { u16 toggle:1, flags:10, opcode:5; } command;
    s16 s; u16 u;
} AObjEvent16;
union AObjEvent32 { u32 u; };
typedef struct AObj
{
    struct AObj *next;
    s32 track,kind;
    f32 value_base,value_target,rate_base,rate_target,length_invert,length;
    void *interpolate;
} AObj;
typedef struct DObj DObj;
typedef struct MObj { struct MObj *next; } MObj;
typedef struct GObj { f32 anim_frame; u32 flags; void (*func_anim)(DObj*,s32,s32); DObj *dobj; } GObj;
typedef struct { union { Vec3f f; } vec; } Transform;
struct DObj
{
    f32 anim_wait,anim_frame,anim_speed;
    union { AObjEvent16 *event16; AObjEvent32 *event32; } anim_joint;
    AObj *aobj; GObj *parent_gobj; u32 flags; sb32 is_anim_root;
    Transform rotate,translate,scale;
    MObj *mobj; DObj *child,*sib_next,*parent;
};
typedef struct { s32 unused; } FTParts;
struct DObjDesc { s32 id; void *dl; Vec3f translate,rotate,scale; };
typedef struct OracleHit { s32 joint; Vec3f offset; sb32 scaled; } OracleHit;
static AObj pool[320]; static s32 allocated;
static void quit(s32 result) { __asm__ volatile("int $0x80" : : "a"(1),"b"(result):"memory"); __builtin_unreachable(); }
AObj* gcAddAObjForDObj(DObj *dobj,s32 track)
{
    AObj *aobj;
    if (allocated >= ARRAY_COUNT(pool)) quit(100);
    aobj=&pool[allocated++];*aobj=(AObj){0};aobj->track=track;aobj->next=dobj->aobj;dobj->aobj=aobj;return aobj;
}
void syInterpCubic(Vec3f *vec,void *unused,f32 value) { quit(101); }
void gcParseMObjMatAnimJoint(MObj *mobj) {}
void gcPlayMObjMatAnim(MObj *mobj) {}
void gcPlayDObjAnimJoint(DObj *dobj);
static f32 lbCommonSin(f32 value) { f32 result; __asm__("fsin":"=t"(result):"0"(value)); return result; }
static f32 lbCommonCos(f32 value) { f32 result; __asm__("fcos":"=t"(result):"0"(value)); return result; }
#include "../src/ft/ftanim.c"
#include "../build/nativeAnimationOracle.inc"
static void output(void *data,u32 size)
{
    s32 written;
    __asm__ volatile("int $0x80":"=a"(written):"a"(4),"b"(1),"c"(data),"d"(size):"memory");
    if (written != size) quit(102);
}
static void dump(DObjDesc *bind,AObjEvent32 **table,s32 joints,s32 frames,s32 table_count)
{
    DObj joint={0}; GObj gobj={0}; f32 values[9]; s32 i,frame;
    for (i=0;i<joints;i++)
    {
        allocated=0;joint=(DObj){0};joint.parent_gobj=&gobj;
        joint.anim_speed=1;joint.anim_wait=AOBJ_ANIM_CHANGED;
        joint.anim_joint.event16=(i<table_count)?(void*)table[i]:NULL;
        if (joint.anim_joint.event16==NULL) joint.anim_wait=AOBJ_ANIM_NULL;
        joint.rotate.vec.f=bind[i].rotate;joint.translate.vec.f=bind[i].translate;joint.scale.vec.f=bind[i].scale;
        for (frame=0;frame<frames;frame++)
        {
            ftAnimParseDObjFigatree(&joint);gcPlayDObjAnimJoint(&joint);
            values[0]=joint.rotate.vec.f.x;values[1]=joint.rotate.vec.f.y;values[2]=joint.rotate.vec.f.z;
            values[3]=joint.translate.vec.f.x;values[4]=joint.translate.vec.f.y;values[5]=joint.translate.vec.f.z;
            values[6]=joint.scale.vec.f.x;values[7]=joint.scale.vec.f.y;values[8]=joint.scale.vec.f.z;
            output(values,sizeof(values));
        }
    }
}
static void dumpGeometry(DObjDesc *bind,AObjEvent32 **table,s32 joints_count,s32 frames,s32 table_count,OracleHit (*hits)[4],f32 size)
{
    DObj joints[32],*ancestors[18],*parent;
    GObj gobj={0}; Mtx44f matrix; Vec3f centers[4];
    s32 i,frame,aid,depth;
    allocated=0;
    for (i=0;i<joints_count;i++)
    {
        DObj *joint=&joints[i];*joint=(DObj){0};joint->parent_gobj=&gobj;
        joint->anim_speed=1;joint->anim_wait=AOBJ_ANIM_CHANGED;
        joint->anim_joint.event16=(i<table_count)?(void*)table[i]:NULL;
        if (joint->anim_joint.event16==NULL) joint->anim_wait=AOBJ_ANIM_NULL;
        joint->rotate.vec.f=bind[i].rotate;joint->translate.vec.f=bind[i].translate;joint->scale.vec.f=bind[i].scale;
        depth=bind[i].id; joint->parent=depth?ancestors[depth-1]:NULL;ancestors[depth]=joint;
    }
    for (frame=0;frame<frames;frame++)
    {
        for (i=0;i<joints_count;i++) { ftAnimParseDObjFigatree(&joints[i]);gcPlayDObjAnimJoint(&joints[i]); }
        for (aid=0;aid<4;aid++)
        {
            OracleHit *hit=&hits[frame][aid]; centers[aid]=(Vec3f){0};
            if (hit->joint<0) continue;
            centers[aid]=hit->offset;
            if (hit->scaled) { centers[aid].x/=size;centers[aid].y/=size;centers[aid].z/=size; }
            parent=hit->joint?&joints[hit->joint-4]:NULL;
            while (parent!=NULL)
            {
                gmCollisionTransformMatrixAll(parent,NULL,matrix);
                gmCollisionGetWorldPosition(matrix,&centers[aid]);parent=parent->parent;
            }
            centers[aid].x*=size;centers[aid].y*=size;centers[aid].z*=size;
        }
        output(centers,sizeof(centers));
    }
}
/* Compare donor reach with compensated target TopN using original matrices. */
typedef struct FTCustomCollisionFrame { Vec3f centers[4]; u32 active_mask; } FTCustomCollisionFrame;
#include "../src/ft/ftcustomcollisions.generated.inc"
static void dumpRootPlacement(void)
{
    DObj root={0}; Mtx44f matrix; Vec3f donor,custom;
    s32 body,facing,frame,aid;
    for (body=0;body<ARRAY_COUNT(sOracleBodySizes);body++)
    {
        for (facing=-1;facing<=1;facing+=2)
        {
            root.rotate.vec.f.y=facing*1.5707963267948966F;
            root.translate.vec.f=(Vec3f){1234,-56,78};
            for (frame=0;frame<ARRAY_COUNT(sFTCustomCollisionKirbyUTilt);frame++)
            {
                const FTCustomCollisionFrame *hit=&sFTCustomCollisionKirbyUTilt[frame];
                for (aid=0;aid<4;aid++)
                {
                    if (!(hit->active_mask&(1<<aid))) continue;
                    donor=hit->centers[aid];custom=donor;
                    custom.x/=sOracleBodySizes[body];custom.y/=sOracleBodySizes[body];custom.z/=sOracleBodySizes[body];
                    root.scale.vec.f.x=root.scale.vec.f.y=root.scale.vec.f.z=sOracleBodySizes[body];
                    gmCollisionTransformMatrixAll(&root,NULL,matrix);gmCollisionGetWorldPosition(matrix,&custom);
                    root.scale.vec.f=(Vec3f){1,1,1};
                    gmCollisionTransformMatrixAll(&root,NULL,matrix);gmCollisionGetWorldPosition(matrix,&donor);
                    output(&custom,sizeof(custom));output(&donor,sizeof(donor));
                }
            }
        }
    }
}
void _start(void)
{
    dump(sOracleCaptainBind,dFTCaptainAnimAttackAirD_joints,ARRAY_COUNT(sOracleCaptainBind)-1,41,ARRAY_COUNT(dFTCaptainAnimAttackAirD_joints));
    dump(sOracleFoxBind,dFTFoxAnimFTilt_joints,ARRAY_COUNT(sOracleFoxBind)-1,28,ARRAY_COUNT(dFTFoxAnimFTilt_joints));
    dump(sOracleDonkeyBind,dFTDonkeyAnimFSmash_joints,ARRAY_COUNT(sOracleDonkeyBind)-1,61,ARRAY_COUNT(dFTDonkeyAnimFSmash_joints));
    dump(sOracleKirbyBind,dFTKirbyAnimUTilt_joints,ARRAY_COUNT(sOracleKirbyBind)-1,19,ARRAY_COUNT(dFTKirbyAnimUTilt_joints));
    dumpGeometry(sOracleCaptainBind,dFTCaptainAnimAttackAirD_joints,ARRAY_COUNT(sOracleCaptainBind)-1,41,ARRAY_COUNT(dFTCaptainAnimAttackAirD_joints),sOracleCaptainHits,1.05F);
    dumpGeometry(sOracleFoxBind,dFTFoxAnimFTilt_joints,ARRAY_COUNT(sOracleFoxBind)-1,28,ARRAY_COUNT(dFTFoxAnimFTilt_joints),sOracleFoxHits,1.0F);
    dumpGeometry(sOracleDonkeyBind,dFTDonkeyAnimFSmash_joints,ARRAY_COUNT(sOracleDonkeyBind)-1,61,ARRAY_COUNT(dFTDonkeyAnimFSmash_joints),sOracleDonkeyHits,1.25F);
    dumpGeometry(sOracleKirbyBind,dFTKirbyAnimUTilt_joints,ARRAY_COUNT(sOracleKirbyBind)-1,19,ARRAY_COUNT(dFTKirbyAnimUTilt_joints),sOracleKirbyHits,0.91F);
    dumpRootPlacement();
    quit(0);
}
