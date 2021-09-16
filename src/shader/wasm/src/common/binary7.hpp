template <typename T, class tFunction>
static void webdnn_binary7_d6(tFunction f, const T *srcl, const T *srcr, T *dst,
                              int o0, int o1, int o2, int o3, int o4, int o5,
                              int isl0, int isl1, int isl2, int isl3, int isl4, int isl5,
                              int isr0, int isr1, int isr2, int isr3, int isr4, int isr5)
{
  int dstidx = 0;
  for (int d0 = 0; d0 < o0; d0++)
  {
    for (int d1 = 0; d1 < o1; d1++)
    {
      for (int d2 = 0; d2 < o2; d2++)
      {
        for (int d3 = 0; d3 < o3; d3++)
        {
          for (int d4 = 0; d4 < o4; d4++)
          {
            for (int d5 = 0; d5 < o5; d5++)
            {
              dst[dstidx++] = f(srcl[d0 * isl0 + d1 * isl1 + d2 * isl2 + d3 * isl3 + d4 * isl4 + d5 * isl5],
                                srcr[d0 * isr0 + d1 * isr1 + d2 * isr2 + d3 * isr3 + d4 * isr4 + d5 * isr5]);
            }
          }
        }
      }
    }
  }
}

template <typename T, class tFunction>
static void webdnn_binary7_d5(tFunction f, const T *srcl, const T *srcr, T *dst,
                              int o0, int o1, int o2, int o3, int o4,
                              int isl0, int isl1, int isl2, int isl3, int isl4,
                              int isr0, int isr1, int isr2, int isr3, int isr4)
{
  int dstidx = 0;
  for (int d0 = 0; d0 < o0; d0++)
  {
    for (int d1 = 0; d1 < o1; d1++)
    {
      for (int d2 = 0; d2 < o2; d2++)
      {
        for (int d3 = 0; d3 < o3; d3++)
        {
          for (int d4 = 0; d4 < o4; d4++)
          {
            dst[dstidx++] = f(srcl[d0 * isl0 + d1 * isl1 + d2 * isl2 + d3 * isl3 + d4 * isl4],
                              srcr[d0 * isr0 + d1 * isr1 + d2 * isr2 + d3 * isr3 + d4 * isr4]);
          }
        }
      }
    }
  }
}

template <typename T, class tFunction>
static void webdnn_binary7_d4(tFunction f, const T *srcl, const T *srcr, T *dst,
                              int o0, int o1, int o2, int o3,
                              int isl0, int isl1, int isl2, int isl3,
                              int isr0, int isr1, int isr2, int isr3)
{
  int dstidx = 0;
  for (int d0 = 0; d0 < o0; d0++)
  {
    for (int d1 = 0; d1 < o1; d1++)
    {
      for (int d2 = 0; d2 < o2; d2++)
      {
        for (int d3 = 0; d3 < o3; d3++)
        {
          dst[dstidx++] = f(srcl[d0 * isl0 + d1 * isl1 + d2 * isl2 + d3 * isl3],
                            srcr[d0 * isr0 + d1 * isr1 + d2 * isr2 + d3 * isr3]);
        }
      }
    }
  }
}

template <typename T, class tFunction>
static void webdnn_binary7_d3(tFunction f, const T *srcl, const T *srcr, T *dst,
                              int o0, int o1, int o2,
                              int isl0, int isl1, int isl2,
                              int isr0, int isr1, int isr2)
{
  int dstidx = 0;
  for (int d0 = 0; d0 < o0; d0++)
  {
    for (int d1 = 0; d1 < o1; d1++)
    {
      for (int d2 = 0; d2 < o2; d2++)
      {
        dst[dstidx++] = f(srcl[d0 * isl0 + d1 * isl1 + d2 * isl2],
                          srcr[d0 * isr0 + d1 * isr1 + d2 * isr2]);
      }
    }
  }
}

template <typename T, class tFunction>
static void webdnn_binary7_d2(tFunction f, const T *srcl, const T *srcr, T *dst,
                              int o0, int o1,
                              int isl0, int isl1,
                              int isr0, int isr1)
{
  int dstidx = 0;
  for (int d0 = 0; d0 < o0; d0++)
  {
    for (int d1 = 0; d1 < o1; d1++)
    {
      dst[dstidx++] = f(srcl[d0 * isl0 + d1 * isl1],
                        srcr[d0 * isr0 + d1 * isr1]);
    }
  }
}

template <typename T, class tFunction>
static void webdnn_binary7_d1(tFunction f, const T *srcl, const T *srcr, T *dst,
                              int o0,
                              int isl0,
                              int isr0)
{
  int dstidx = 0;
  for (int d0 = 0; d0 < o0; d0++)
  {
    dst[dstidx++] = f(srcl[d0 * isl0],
                      srcr[d0 * isr0]);
  }
}

template <typename T, class tFunction>
static void webdnn_binary7_d0(tFunction f, const T *srcl, const T *srcr, T *dst)
{
  dst[0] = f(srcl[0],
             srcr[0]);
}
