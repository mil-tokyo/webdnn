template <typename T, class tFunction>
static void webdnn_unary(const T *src, T *dst, int length, tFunction f)
{
  for (int i = 0; i < length; i++)
  {
    dst[i] = f(src[i]);
  }
}
