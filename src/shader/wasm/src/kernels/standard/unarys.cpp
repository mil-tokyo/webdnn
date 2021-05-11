#include <algorithm>
#include <cmath>
#include "../../common/kernel.hpp"
#include "../../common/unary.hpp"

extern "C"
{
  void WEBDNN_KERNEL kernel_ceil(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return std::ceil(s); });
  }

  void WEBDNN_KERNEL kernel_exp(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return std::exp(s); });
  }

  void WEBDNN_KERNEL kernel_floor(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return std::floor(s); });
  }

  void WEBDNN_KERNEL kernel_relu(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return std::max(s, 0.0f); });
  }

  void WEBDNN_KERNEL kernel_sigmoid(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return (std::tanh(s * 0.5f) + 1.0f) * 0.5f; });
  }

  void WEBDNN_KERNEL kernel_sqrt(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return std::sqrt(s); });
  }

  void WEBDNN_KERNEL kernel_tanh(const float *src, float *dst, int length)
  {
    webdnn_unary(src, dst, length, [](float s) { return std::tanh(s); });
  }
}
