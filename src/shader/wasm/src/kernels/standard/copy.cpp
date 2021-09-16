#include <cstring>
#include "../../common/kernel.hpp"

extern "C"
{
  void WEBDNN_KERNEL kernel_copy(const float *src, float *dst, int length) {
    memcpy(dst, src, length * sizeof(float));
  }
}
