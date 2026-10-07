/* ROM tags are resolved before any collision sample is dereferenced. Each
 * player owns its cache, so simultaneous attacks cannot evict another sample. */
extern void syDmaReadRom(uintptr_t, void*, size_t);
static u8 sCCCollisionCache[4][80] __attribute__((aligned(16)));
static u32 sCCCollisionSource[4];

static const FTCustomCollisionFrame* ccCollisionSourceFrame(
    FTStruct *fp, const FTCustomCollisionFrame *frame)
{
    u32 source = (u32)frame, aligned;
    if (source < 0x05800000 || source >= 0x05900000) return frame;
    if (fp->player >= 4) return NULL;
    aligned = source & ~15U;
    if (sCCCollisionSource[fp->player] != aligned)
    {
        syDmaReadRom(aligned, sCCCollisionCache[fp->player], 80);
        sCCCollisionSource[fp->player] = aligned;
    }
    return (const FTCustomCollisionFrame*)
        &sCCCollisionCache[fp->player][source & 15];
}
