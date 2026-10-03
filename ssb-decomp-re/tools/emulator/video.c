#include "m64p_plugin.h"
static GFX_INFO info;
static void (*render)(int);
EXPORT m64p_error PluginStartup(m64p_dynlib_handle h,void*c,void(*d)(void*,int,const char*)){return 0;}
EXPORT m64p_error PluginShutdown(void){return 0;}
EXPORT m64p_error PluginGetVersion(m64p_plugin_type*t,int*v,int*a,const char**n,int*c){if(t)*t=M64PLUGIN_GFX;if(v)*v=0x10000;if(a)*a=0x20100;if(n)*n="Lab null video with DP completion";if(c)*c=0;return 0;}
EXPORT int InitiateGFX(GFX_INFO i){info=i;return 1;}
EXPORT int RomOpen(void){return 1;}
EXPORT void RomClosed(void){}
EXPORT void ProcessDList(void){*info.MI_INTR_REG|=0x20;info.CheckInterrupts();}
EXPORT void ProcessRDPList(void){ProcessDList();}
EXPORT void UpdateScreen(void){if(render)render(1);}
EXPORT void SetRenderingCallback(void(*cb)(int)){render=cb;}
EXPORT void ChangeWindow(void){}
EXPORT void MoveScreen(int x,int y){}
EXPORT void ShowCFB(void){}
EXPORT void ViStatusChanged(void){}
EXPORT void ViWidthChanged(void){}
EXPORT void ReadScreen2(void*d,int*w,int*h,int f){*w=0;*h=0;}
EXPORT void ResizeVideoOutput(int w,int h){}
EXPORT void FBRead(unsigned a){}
EXPORT void FBWrite(unsigned a,unsigned s){}
EXPORT void FBGetFrameBufferInfo(void*p){FrameBufferInfo*i=p;for(int c=0;c<6;c++)i[c].addr=0;}
