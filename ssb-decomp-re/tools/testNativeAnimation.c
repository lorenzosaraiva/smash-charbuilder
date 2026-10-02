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
typedef struct OracleEvent { s32 kind,value,aid,joint; Vec3f offset; sb32 scaled; } OracleEvent;
typedef struct OracleHidden { s32 joint,parent,partindex,kind; } OracleHidden;
static AObj pool[640]; static s32 allocated;
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
/* Independently construct the donor tree using native setup/hidden-part rules.
   Binding precedes TransN detachment, as in ftMainSetStatus. */
static void append(DObj *parent,DObj *child)
{
    DObj *last=parent->child;
    if (last==NULL) parent->child=child;
    else { while(last->sib_next!=NULL)last=last->sib_next;last->sib_next=child; }
    child->parent=parent;
}
static s32 bindTree(DObj *joint,AObjEvent32 **table,s32 count,s32 slot)
{
    while(joint!=NULL)
    {
        joint->anim_joint.event16=(slot<count)?(void*)table[slot]:NULL;slot++;
        joint->anim_wait=joint->anim_joint.event16?AOBJ_ANIM_CHANGED:AOBJ_ANIM_NULL;
        if (joint->child!=NULL)slot=bindTree(joint->child,table,count,slot);
        joint=joint->sib_next;
    }
    return slot;
}
static void dump(DObjDesc *bind,AObjEvent32 **table,s32 table_count,u32 setup0,u32 setup1,
                 OracleHidden *hidden,s32 hidden_count,u32 flags,Vec3f *scales,
                 s32 frames,const OracleEvent *events,f32 size)
{
    DObj joints[40]={0},*ancestors[18]={0},*joint,*parent;
    sb32 enabled[40]={0};
    GObj gobj={0};Mtx44f matrix;Vec3f centers[4];f32 values[9];
    s32 i,j,depth,frame,aid,wait=0,guard;
    u32 mask;
    OracleHit hits[4]={{-1},{-1},{-1},{-1}};
    const OracleEvent *event=events;
    allocated=0;
    for (i=0;i<40;i++)
    {
        joints[i].parent_gobj=&gobj;joints[i].anim_speed=1;
        joints[i].scale.vec.f=(Vec3f){1,1,1};joints[i].anim_wait=AOBJ_ANIM_NULL;
    }
    for (i=0;bind[i].id!=18;i++)
    {
        if (i>=36)quit(103);
        if (!((i<32?setup0:setup1)&(1U<<(31-i%32))))continue;
        depth=bind[i].id&0xfff;j=i+4;joint=&joints[j];enabled[j]=TRUE;
        if (depth && ancestors[depth-1]==NULL)quit(104);
        append(depth?ancestors[depth-1]:&joints[0],joint);ancestors[depth]=joint;
    }
    for (i=0;i<hidden_count;i++)
    {
        if (!(flags&(1U<<(31-i))))continue;
        j=hidden[i].joint;joint=&joints[j];parent=&joints[hidden[i].parent];
        if (enabled[j])quit(105);
        enabled[j]=TRUE;joint->parent=parent;
        switch(hidden[i].kind)
        {
        case 0:append(parent,joint);break;
        case 1:joint->sib_next=parent->child;parent->child=joint;break;
        case 2:joint->sib_next=parent->child->sib_next;parent->child->sib_next=joint;break;
        case 3:
            joint->child=parent->child;parent->child=joint;
            for(parent=joint->child;parent!=NULL;parent=parent->sib_next)parent->parent=joint;
            break;
        default:quit(106);
        }
    }
    for (j=4;j<40;j++)if(enabled[j])
    {
        joints[j].rotate.vec.f=bind[j-4].rotate;joints[j].translate.vec.f=bind[j-4].translate;joints[j].scale.vec.f=bind[j-4].scale;
    }
    bindTree(joints[0].child,table,table_count,0);
    if (enabled[1])
    {
        joint=&joints[1];parent=joint->parent;parent->child=joint->child;
        for (parent=joint->child;parent!=NULL;parent=parent->sib_next)parent->parent=joint->parent;
        joint->child=NULL;
    }
    for (frame=0;frame<frames;frame++)
    {
        if(frame)wait--;
        guard=0;
        /* The native sync wait adds to script_wait; async wait replaces it
           with target - current frame. A negative wait executes immediately. */
        while(event!=NULL && wait<=0)
        {
            if(++guard>10000)quit(108);
            switch(event->kind)
            {
            case 0:event=NULL;continue;
            case 1:wait+=event->value;break;
            case 2:wait=event->value-frame;break;
            case 3:hits[event->aid]=(OracleHit){event->joint,event->offset,event->scaled};break;
            case 4:for(aid=0;aid<4;aid++)hits[aid].joint=-1;break;
            case 5:hits[event->aid].joint=-1;break;
            case 6:if(hits[event->aid].joint>=0)hits[event->aid].offset=event->offset;break;
            case 7:event=events;continue;
            default:quit(109);
            }
            event++;
        }
        for (j=1;j<40;j++)if(enabled[j])
        {
            joint=&joints[j];ftAnimParseDObjFigatree(joint);
            if (scales!=NULL)lbCommonPlayTranslateScaledDObjAnim(joint,&scales[j]);
            else gcPlayDObjAnimJoint(joint);
            values[0]=joint->rotate.vec.f.x;values[1]=joint->rotate.vec.f.y;values[2]=joint->rotate.vec.f.z;
            values[3]=joint->translate.vec.f.x;values[4]=joint->translate.vec.f.y;values[5]=joint->translate.vec.f.z;
            values[6]=joint->scale.vec.f.x;values[7]=joint->scale.vec.f.y;values[8]=joint->scale.vec.f.z;
            output(values,sizeof(values));
        }
        mask=0;
        for (aid=0;aid<4;aid++)
        {
            OracleHit *hit=&hits[aid];centers[aid]=(Vec3f){0};
            if (hit->joint<0)continue;
            mask|=1U<<aid;
            if (hit->joint && !enabled[hit->joint])quit(107);
            centers[aid]=hit->offset;
            if (hit->scaled){centers[aid].x/=size;centers[aid].y/=size;centers[aid].z/=size;}
            parent=hit->joint?&joints[hit->joint]:NULL;
            while(parent!=NULL && parent!=&joints[0])
            {
                gmCollisionTransformMatrixAll(parent,NULL,matrix);gmCollisionGetWorldPosition(matrix,&centers[aid]);parent=parent->parent;
            }
            centers[aid].x*=size;centers[aid].y*=size;centers[aid].z*=size;
        }
        output(centers,sizeof(centers));output(&mask,sizeof(mask));
    }
}
/* Compare donor reach with compensated target TopN using original matrices. */
typedef struct FTCustomCollisionFrame { Vec3f centers[4]; u32 active_mask; } FTCustomCollisionFrame;
#include "../src/ft/ftcustomcollisions.generated.inc"
static void dumpRootPlacement(const FTCustomCollisionFrame *frames,s32 count)
{
    DObj root={0}; Mtx44f matrix; Vec3f donor,custom;
    s32 body,facing,frame,aid;
    for (body=0;body<ARRAY_COUNT(sOracleBodySizes);body++)
    {
        for (facing=-1;facing<=1;facing+=2)
        {
            root.rotate.vec.f.y=facing*1.5707963267948966F;
            root.translate.vec.f=(Vec3f){1234,-56,78};
            for (frame=0;frame<count;frame++)
            {
                const FTCustomCollisionFrame *hit=&frames[frame];
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
#include "../build/nativeAnimationCalls.inc"
    quit(0);
}
