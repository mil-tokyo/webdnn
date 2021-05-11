#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#define WEBDNN_KERNEL EMSCRIPTEN_KEEPALIVE
#else
#define WEBDNN_KERNEL
#endif
