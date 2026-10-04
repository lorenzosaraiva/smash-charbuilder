#include "m64p_plugin.h"
static _Atomic unsigned keys[4];
EXPORT void LabKeys(unsigned v){keys[0]=v;}
EXPORT void LabKeysPort(unsigned c,unsigned v){if(c<4)keys[c]=v;}
EXPORT m64p_error PluginStartup(m64p_dynlib_handle h,void*c,void(*d)(void*,int,const char*)){return M64ERR_SUCCESS;}
EXPORT m64p_error PluginShutdown(void){return M64ERR_SUCCESS;}
EXPORT m64p_error PluginGetVersion(m64p_plugin_type*t,int*v,int*a,const char**n,int*c){if(t)*t=M64PLUGIN_INPUT;if(v)*v=0x10000;if(a)*a=0x20000;if(n)*n="Lab test input";if(c)*c=0;return 0;}
EXPORT void InitiateControllers(CONTROL_INFO i){for(int c=0;c<4;c++){i.Controls[c].Present=1;i.Controls[c].RawData=0;i.Controls[c].Plugin=PLUGIN_NONE;}}
EXPORT int RomOpen(void){return 1;}
EXPORT void RomClosed(void){}
EXPORT void GetKeys(int c,BUTTONS*k){k->Value=(c>=0&&c<4)?keys[c]:0;}
EXPORT void ControllerCommand(int c,unsigned char*p){}
EXPORT void ReadController(int c,unsigned char*p){}
EXPORT void SDL_KeyDown(int m,int s){}
EXPORT void SDL_KeyUp(int m,int s){}
