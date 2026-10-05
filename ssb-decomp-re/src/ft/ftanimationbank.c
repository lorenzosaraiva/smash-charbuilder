/* Compressed pose keys have their own Expansion Pak region. They must not
 * enlarge lower-bank overlays into the original framebuffer addresses. */
#include <ssb_types.h>
typedef struct FTCustomAnimationKey { u8 frame, hi, lo; } FTCustomAnimationKey;
#include "ftcustomanimationkeys.generated.inc"
