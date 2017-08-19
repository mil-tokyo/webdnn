
#include <stdlib.h>
#include <math.h>

float static_buffer[29];
float* dynamic_buffer = nullptr;

int meta_buf_0[] = {8,0,24,16,5};
int* meta_buffers[] = {meta_buf_0};

extern "C" void init() {
    //static_buffer = (float*)malloc(29 * sizeof(float));
}

extern "C" float* get_static_buffer(void) {
    return static_buffer;
}

extern "C" float* allocate_dynamic_buffer(int count) {
    if (dynamic_buffer) {
        free(dynamic_buffer);
        dynamic_buffer = nullptr;
    }
    dynamic_buffer = (float*)malloc(count * sizeof(float));
    return dynamic_buffer;
}

extern "C" float* get_dynamic_buffer(void) {
    return dynamic_buffer;
}
extern "C" void set_placeholder_value(int kernel_order, int offset, int value) {
    meta_buffers[kernel_order][offset] = value;
}

void mergedelementwise_5eb3431de5e2461142568d810920cf4320b1b4207ab1619a235d7ed5(const int * meta_buffer)
{
    const float * v1 = (static_buffer + meta_buffer[0]);
    const float * v2 = (static_buffer + meta_buffer[1]);
    const float * v3 = (static_buffer + meta_buffer[2]);
    float * v4 = (static_buffer + meta_buffer[3]);
    const int D0 = meta_buffer[4];
    int d0;
    for (d0 = 0; d0 < D0; d0 += 1) {
        const float v5 = v1[d0];
        const float v6 = v3[d0];
        float v7;
        {
            v7 = v6 * v5;
        }
        const float v8 = v2[d0];
        float v9;
        {
            v9 = v7 + v8;
        }
        v4[d0] = v9;
    }
}

extern "C" void run() {
mergedelementwise_5eb3431de5e2461142568d810920cf4320b1b4207ab1619a235d7ed5(meta_buf_0);

}

