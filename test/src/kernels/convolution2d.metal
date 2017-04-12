#include <metal_stdlib>
using namespace metal;

struct Convolution2DDescriptor
{
    int kw;
    int kh;
    int sw;
    int sh;
    int pw;
    int ph;
    int n;
    int w1;
    int h1;
    int c1;
    int c2;
};

// kernel void
// im2col(const device Convolution2DDescriptor *desc[[buffer(0)]],
//        const device float *im[[buffer(1)]],
//        const device float *cols[[buffer(2)]],
//        uint gid[[thread_position_in_grid]])
// {
// const int KW = desc->kw;
// const int KH = desc->kh;
// const int SW = desc->sw;
// const int SH = desc->sh;
// const int PW = desc->pw;
// const int PH = desc->ph;
// const int N = desc->n;
// const int W1 = desc->w1;
// const int H1 = desc->h1;
// const int C1 = desc->c1;
// const int C2 = desc->c2;
// const int W2 = (W1 + 2 * PW - KW) / SW + 1;
// const int H2 = (H1 + 2 * PH - KH) / SH + 1;

//     if (gid >= N * H2 * W2 * C1 * KH * KW)
//         return;

//     const int kw = gid % KW;
//     const int kh = gid / KW % KH;
//     const int c1 = gid / KW / KH / C1;
//     const int w2 = gid / KW / KH / C1 / W2;
//     const int h2 = gid / KW / KH / C1 / W2 % H2;
//     const int n = gid / KW / KH / C1 / W2 / H2;

//     const int h1 = h2 * S - kh;
//     const int w1 = w2 * S - kw;

//     col[gid] = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n * C1 + c1) * H1 + h1) * W1 + w1];
// }

kernel void
convolution2d_naive(const device Convolution2DDescriptor *desc[[buffer(0)]],
                    const device float *X[[buffer(1)]],
                    const device float *W[[buffer(2)]],
                    device float *Y[[buffer(3)]],
                    uint gid[[thread_position_in_grid]])
{
    const int KW = desc->kw;
    const int KH = desc->kh;
    const int SW = desc->sw;
    const int SH = desc->sh;
    const int PW = desc->pw;
    const int PH = desc->ph;
    const int N = desc->n;
    const int W1 = desc->w1;
    const int H1 = desc->h1;
    const int C1 = desc->c1;
    const int C2 = desc->c2;
    const int W2 = (W1 + 2 * PW - KW) / SW + 1;
    const int H2 = (H1 + 2 * PH - KH) / SH + 1;

    if (gid >= N * C2 * H2 * W2)
        return;

    const int w2 = gid % W2;
    const int h2 = gid / W2 % H2;
    const int c2 = gid / W2 / H2 % C2;
    const int n = gid / W2 / H2 / C2;

    float result = 0;

    for (int c1 = 0; c1 < C1; c1++)
    {
        for (int kh = 0; kh < KH; kh++)
        {
            const int h1 = h2 * SH - PH + kh;
            if (h1 < 0 || h1 >= H1)
                continue;

            for (int kw = 0; kw < KW; kw++)
            {
                const int w1 = w2 * SW - PW + kw;
                if (w1 < 0 || w1 >= W1)
                    continue;

                result += W[((c1 * KH + kh) * KW + kw) * C2 + c2] * X[((n * H1 + h1) * W1 + w1) * C1 + c1];
            }
        }
    }

    Y[((n * H2 + h2) * W2 + w2) * C2 + c2] = result;
}

kernel void
im2col(const device Convolution2DDescriptor *desc[[buffer(0)]],
       const device float *im[[buffer(1)]],
       device float *col[[buffer(2)]],
       uint gid[[thread_position_in_grid]],
       uint num_threads[[threads_per_grid]])
{
    const int KW = desc->kw;
    const int KH = desc->kh;
    const int SW = desc->sw;
    const int SH = desc->sh;
    const int PW = desc->pw;
    const int PH = desc->ph;
    const int N = desc->n;
    const int W1 = desc->w1;
    const int H1 = desc->h1;
    const int C1 = desc->c1;
    const int C2 = desc->c2;
    const int W2 = (W1 + 2 * PW - KW) / SW + 1;
    const int H2 = (H1 + 2 * PH - KH) / SH + 1;

    for (int i = gid; i < N * H1 * W1 * C1; i += num_threads)
    {
        const int c1 = i % C1;
        const int w1 = i / C1 % W1;
        const int h1 = i / C1 / W1 % H1;
        const int n = i / C1 / W1 / H1;

        const float v = im[((n * H1 + h1) * W1 + w1) * C1 + c1];

        for (int kh = 0; kh < KH; kh++)
        {
            if ((h1 + kh) % SH != 0)
                continue;

            for (int kw = 0; kw < KW; kw++)
            {
                if ((w1 + kw) % SW != 0)
                    continue;

                col[((((n * H1 + h1) * W1 + w1) * C1 + c1) * KH + kh) * KW + kw] = v;
            }
        }
    }
}