#ifndef _SCCHARBUILDERTRAINING_H_
#define _SCCHARBUILDERTRAINING_H_

#include <sc/sccharbuilder.h>

/* Survives scene overlay loads; -1 means training was not launched by the lab.
 * Options consumes this preset when reopening the editor. Training resets and
 * stage/character selection retain it until return or cancellation. */
extern s8 gSCManagerCharBuilderTrainingSlot;

#endif
