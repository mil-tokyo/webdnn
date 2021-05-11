#include <cstdlib>
#include <emscripten.h>

extern "C"
{
  void* EMSCRIPTEN_KEEPALIVE webdnn_malloc(int byte_length)
  {
    return malloc((size_t)byte_length);
  }

  void EMSCRIPTEN_KEEPALIVE webdnn_free(void *buf)
  {
    free(buf);
  }
}
