#include <algorithm>
#include <cmath>
#include "../../common/kernel.hpp"
#include "../../common/unary.hpp"

extern "C"
{
  void WEBDNN_KERNEL kernel_leakyrelu(const float *src, float *dst, int length, float alpha)
  {
    webdnn_unary(src, dst, length, [alpha](float s) { return s < 0.0f ? s * alpha : s; });
  }

}
