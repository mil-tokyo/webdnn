#include <algorithm>
#include <cmath>
#include "../../common/kernel.hpp"
#include "../../common/binary7.hpp"


extern "C"
{
#define DEFINE_BINARY7(name, func) \
void WEBDNN_KERNEL kernel_##name##_d0(const float *srcl, const float *srcr, float *dst) { webdnn_binary7_d0(func, srcl, srcr, dst); } \
void WEBDNN_KERNEL kernel_##name##_d1(const float *srcl, const float *srcr, float *dst, int o0, int isl0, int isr0) { webdnn_binary7_d1(func, srcl, srcr, dst, o0, isl0, isr0); } \
void WEBDNN_KERNEL kernel_##name##_d2(const float *srcl, const float *srcr, float *dst, int o0, int o1, int isl0, int isl1, int isr0, int isr1) { webdnn_binary7_d2(func, srcl, srcr, dst, o0, o1, isl0, isl1, isr0, isr1); } \
void WEBDNN_KERNEL kernel_##name##_d3(const float *srcl, const float *srcr, float *dst, int o0, int o1, int o2, int isl0, int isl1, int isl2, int isr0, int isr1, int isr2) { webdnn_binary7_d3(func, srcl, srcr, dst, o0, o1, o2, isl0, isl1, isl2, isr0, isr1, isr2); } \
void WEBDNN_KERNEL kernel_##name##_d4(const float *srcl, const float *srcr, float *dst, int o0, int o1, int o2, int o3, int isl0, int isl1, int isl2, int isl3, int isr0, int isr1, int isr2, int isr3) { webdnn_binary7_d4(func, srcl, srcr, dst, o0, o1, o2, o3, isl0, isl1, isl2, isl3, isr0, isr1, isr2, isr3); } \
void WEBDNN_KERNEL kernel_##name##_d5(const float *srcl, const float *srcr, float *dst, int o0, int o1, int o2, int o3, int o4, int isl0, int isl1, int isl2, int isl3, int isl4, int isr0, int isr1, int isr2, int isr3, int isr4) { webdnn_binary7_d5(func, srcl, srcr, dst, o0, o1, o2, o3, o4, isl0, isl1, isl2, isl3, isl4, isr0, isr1, isr2, isr3, isr4); } \
void WEBDNN_KERNEL kernel_##name##_d6(const float *srcl, const float *srcr, float *dst, int o0, int o1, int o2, int o3, int o4, int o5, int isl0, int isl1, int isl2, int isl3, int isl4, int isl5, int isr0, int isr1, int isr2, int isr3, int isr4, int isr5) { webdnn_binary7_d6(func, srcl, srcr, dst, o0, o1, o2, o3, o4, o5, isl0, isl1, isl2, isl3, isl4, isl5, isr0, isr1, isr2, isr3, isr4, isr5); }

  DEFINE_BINARY7(add, [](float lhs, float rhs) { return lhs + rhs; });
  DEFINE_BINARY7(sub, [](float lhs, float rhs) { return lhs - rhs; });
  DEFINE_BINARY7(mul, [](float lhs, float rhs) { return lhs * rhs; });
  DEFINE_BINARY7(div, [](float lhs, float rhs) { return lhs / rhs; });
  DEFINE_BINARY7(pow, [](float lhs, float rhs) { return pow(lhs, rhs); });
}
