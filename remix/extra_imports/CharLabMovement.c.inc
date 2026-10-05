/* Original donor geometry/travel, retaining Remix's native contact engine. */
typedef struct FTCharBuilderSpecialTravel { Vec3f delta; f32 angle; } FTCharBuilderSpecialTravel;
struct FTCharBuilderSpecialPath {
    s32 donor, motion;
    FTCustomMoveDefinition move;
    FTCustomCollisionTrajectory trajectory;
    const FTCharBuilderSpecialTravel *travel;
    const Vec3f *spawn;
};
typedef struct FTCharBuilderSpecialTiming { s32 donor, motion; FTCustomMoveDefinition move; } FTCharBuilderSpecialTiming;
#include "ft/ftspecialtiming.generated.inc"
typedef struct FTCustomNormalMechanics { const Vec3f *travel, *socket; s32 count; u32 flags; } FTCustomNormalMechanics;
#include "ft/ftnormalmechanics.generated.inc"
extern FTData *dFTManagerDataFiles[];
extern void ccOriginalGroundTravel(GObj*);
extern void ccOriginalAirTravel(FTStruct*, f32*, f32*, f32*);
extern void ccOriginalGroundPhysics(GObj*);

static const FTCharBuilderSpecialPath* ccFindSpecialPath(s32 donor,s32 motion)
{
    s32 i;
    for(i=0;i<ARRAY_COUNT(sFTCharBuilderSpecialPaths);i++)
        if(sFTCharBuilderSpecialPaths[i].donor==donor && sFTCharBuilderSpecialPaths[i].motion==motion)
            return &sFTCharBuilderSpecialPaths[i];
    return NULL;
}

static s32 ccNormalIndex(FTStruct *fp)
{
    FTCustomMoveClock *clock=ftCustomMoveGetClock(fp);u32 offset;
    if(clock==NULL || ftCustomMoveGetSlot(fp)==NULL)return -1;
    offset=(u32)clock->move-(u32)sFTCustomMoves;
    if(offset>=sizeof(sFTCustomMoves) || offset%sizeof(FTCustomMoveDefinition))return -1;
    return offset/sizeof(FTCustomMoveDefinition);
}

static sb32 ccSourceTravel(FTStruct *fp,Vec3f *out,sb32 ground)
{
    CCSpecialClock *special=ccSpecialClock(fp);s32 frame,index;
    if(special && special->path && special->path->travel)
    {
        const FTCharBuilderSpecialPath *path=special->path;
        f32 x,y,angle;
        frame=(s32)special->frame;if(frame<0)frame=0;
        if(frame>=path->trajectory.count)frame=path->trajectory.count-1;
        *out=path->travel[frame].delta;
        if(ground)return TRUE;
        x=out->x*fp->lr;y=out->y;angle=path->travel[frame].angle;
        /* Falcon's ground-to-air kick pitches TransN by the ground slope. */
        if(path->donor==nFTKindCaptain && path->motion==nFTCaptainMotionSpecialLwAir)
            angle+=fp->joints[nFTPartsJointTransN]->rotate.vec.f.z;
        out->x=x*__cosf(angle)-y*__sinf(angle);
        out->y=x*__sinf(angle)+y*__cosf(angle);out->z*=fp->lr;
        return TRUE;
    }
    index=ccNormalIndex(fp);
    if(index>=0)
    {
        const FTCustomNormalMechanics *data=&sFTCustomNormalMechanics[index/33][index%33];
        if(data->travel==NULL){out->x=out->y=out->z=0;return TRUE;}
        frame=(s32)ftCustomMoveGetClock(fp)->frame;if(frame<0)frame=0;
        if(frame>=data->count)frame=(ftCustomMoveGetClock(fp)->flags&FTCUSTOMMOVE_FLAG_LOOP)?1+(frame-1)%(data->count-1):data->count-1;
        *out=data->travel[frame];if(!ground){out->x*=fp->lr;out->z*=fp->lr;}return TRUE;
    }
    return FALSE;
}

void ccGroundTravel(GObj *g)
{
    FTStruct *fp=ftGetStruct(g);Vec3f travel;
    if(!ccSourceTravel(fp,&travel,TRUE)){ccOriginalGroundTravel(g);return;}
    fp->physics.vel_ground.x=travel.x;fp->physics.vel_ground.z=travel.z*fp->lr;
    if(fp->lr*DObjGetStruct(g)->rotate.vec.f.y<0)
    {fp->physics.vel_ground.x=-fp->physics.vel_ground.x;fp->physics.vel_ground.z=-fp->physics.vel_ground.z;}
    ftPhysicsSetGroundVelTransferAir(g);
}

void ccAirTravel(FTStruct *fp,f32 *z,f32 *y,f32 *x)
{
    Vec3f travel;
    if(!ccSourceTravel(fp,&travel,FALSE)){ccOriginalAirTravel(fp,z,y,x);return;}
    if(z)*z=travel.x;if(y)*y=travel.y;if(x)*x=travel.z;
}

void ccGroundPhysics(GObj *g)
{
    FTStruct *fp=ftGetStruct(g);s32 index=ccNormalIndex(fp);
    if(index<0){ccOriginalGroundPhysics(g);return;}
    if(sFTCustomNormalMechanics[index/33][index%33].flags&0x40000000)ccGroundTravel(g);
    else ftPhysicsApplyGroundVelFriction(g);
}

static void ccDonorPhysics(GObj *g)
{
    FTStruct *fp=ftGetStruct(g);CCSpecialClock *special=ccSpecialClock(fp);
    FTAttributes *body=fp->attr;FTData *data;
    if(!special || !special->physics)return;
    data=dFTManagerDataFiles[special->donor];
    if(data && data->p_file_main && *data->p_file_main)
        fp->attr=(FTAttributes*)((uintptr_t)*data->p_file_main+(uintptr_t)data->o_attributes);
    special->physics(g);
    fp->attr=body;
}

static void ccSpecialCollision(FTStruct *fp)
{
    CCSpecialClock *special=ccSpecialClock(fp);const FTCustomCollisionFrame *frame;
    s32 i;
    if(!special || !special->path){ftCustomCollisionApply(fp);return;}
    if(fp->attr==NULL || fp->attr->size<=0 || fp->joints[0]==NULL)return;
    frame=ftCustomCollisionSample(&special->path->trajectory,(s32)special->frame);
    if(frame==NULL)return;
    for(i=0;i<4;i++)
    {
        FTAttackColl *hit=&fp->attack_colls[i];Vec3f center;
        if(hit->attack_state==nGMAttackStateOff || !(frame->active_mask&(1<<i)))continue;
        center=frame->centers[i];hit->joint_id=0;hit->joint=fp->joints[0];
        hit->offset.x=center.x/fp->attr->size;hit->offset.y=center.y/fp->attr->size;hit->offset.z=center.z/fp->attr->size;
        hit->is_scale_pos=FALSE;
    }
}
