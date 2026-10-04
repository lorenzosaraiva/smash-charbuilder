"""Extract original inverse-trig helpers for the freestanding runtime checks."""
from customAnimation import ROOT

def prepare_math():
 text=(ROOT/'src/sys/utils.c').read_text(encoding='utf-8')
 first=text.index('f32 syUtilsArcTan(');last=text.index('f32 syUtilsArcSin(',first)
 (ROOT/'build/shared-animation-math.inc').write_text('#define M_PI 3.14159265358979323846\n#define M_DTOR (M_PI/180.0)\n#ifndef M_PI_F\n#define M_PI_F 3.14159265358979323846F\n#endif\n#ifndef M_DTOR_F\n#define M_DTOR_F(x) ((x)*0.0174532925199433F)\n#endif\n'+text[first:last],encoding='utf-8')

if __name__=='__main__':prepare_math()
