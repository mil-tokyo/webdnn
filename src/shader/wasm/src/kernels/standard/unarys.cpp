#include <algorithm>
#include <cmath>
#include "../../common/kernel.hpp"
#include "../../common/unary.hpp"

extern "C"
{
  
#define DEFINE_UNARY(name, func) \
void WEBDNN_KERNEL kernel_##name(const float *src, float *dst, int length) { webdnn_unary(src, dst, length, func); }
  DEFINE_UNARY(ceil, [](float s) { return std::ceil(s); });
  DEFINE_UNARY(exp, [](float s) { return std::exp(s); });
  DEFINE_UNARY(floor, [](float s) { return std::floor(s); });
  DEFINE_UNARY(relu, [](float s) { return std::max(s, 0.0f); });
  DEFINE_UNARY(sigmoid, [](float s) { return (std::tanh(s * 0.5f) + 1.0f) * 0.5f; });
  DEFINE_UNARY(sqrt, [](float s) { return std::sqrt(s); });
  DEFINE_UNARY(tanh, [](float s) { return std::tanh(s); });
}
