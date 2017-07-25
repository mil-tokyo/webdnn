
#include <stdlib.h>
#include <math.h>

float static_buffer[9506180];
float* dynamic_buffer = nullptr;

int meta_buf_0[] = {1820036,2787716,1,3,144,192,144,192,9,9,1,1,4,4};
int meta_buf_1[] = {2787716,1810016,1902980,27648,32,243};
int meta_buf_2[] = {1902980,1902980,1819968,27648,32};
int meta_buf_3[] = {1902980,1902980,884736};
int meta_buf_4[] = {1902980,1902980,1819936,884736,32};
int meta_buf_5[] = {1902980,1902980,1820000,27648,32};
int meta_buf_6[] = {1902980,2787716,1,32,144,192,72,96,4,4,2,2,1,1};
int meta_buf_7[] = {2787716,1736704,1902980,6912,64,512};
int meta_buf_8[] = {1902980,1902980,1819584,6912,64};
int meta_buf_9[] = {1902980,1902980,442368};
int meta_buf_10[] = {1902980,1902980,1819456,442368,64};
int meta_buf_11[] = {1902980,1902980,1819648,6912,64};
int meta_buf_12[] = {1902980,2345348,1,64,72,96,36,48,4,4,2,2,1,1};
int meta_buf_13[] = {2345348,1474560,1902980,1728,128,1024};
int meta_buf_14[] = {1902980,1902980,1818816,1728,128};
int meta_buf_15[] = {1902980,1902980,221184};
int meta_buf_16[] = {1902980,1902980,1818432,221184,128};
int meta_buf_17[] = {1902980,1902980,1818944,1728,128};
int meta_buf_18[] = {1902980,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_19[] = {2345348,294912,2124164,1728,128,1152};
int meta_buf_20[] = {2124164,2124164,1818048,1728,128};
int meta_buf_21[] = {2124164,2124164,221184};
int meta_buf_22[] = {2124164,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_23[] = {2345348,1032192,2124164,1728,128,1152};
int meta_buf_24[] = {2124164,2124164,1819328,1728,128};
int meta_buf_25[] = {2124164,1902980,2124164,221184};
int meta_buf_26[] = {2124164,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_27[] = {2345348,1179648,1902980,1728,128,1152};
int meta_buf_28[] = {1902980,1902980,1818688,1728,128};
int meta_buf_29[] = {1902980,1902980,221184};
int meta_buf_30[] = {1902980,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_31[] = {2345348,1327104,1902980,1728,128,1152};
int meta_buf_32[] = {1902980,1902980,1817792,1728,128};
int meta_buf_33[] = {1902980,2124164,1902980,221184};
int meta_buf_34[] = {1902980,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_35[] = {2345348,884736,2124164,1728,128,1152};
int meta_buf_36[] = {2124164,2124164,1819072,1728,128};
int meta_buf_37[] = {2124164,2124164,221184};
int meta_buf_38[] = {2124164,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_39[] = {2345348,442368,2124164,1728,128,1152};
int meta_buf_40[] = {2124164,2124164,1819200,1728,128};
int meta_buf_41[] = {2124164,1902980,2124164,221184};
int meta_buf_42[] = {2124164,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_43[] = {2345348,737280,1902980,1728,128,1152};
int meta_buf_44[] = {1902980,1902980,1818304,1728,128};
int meta_buf_45[] = {1902980,1902980,221184};
int meta_buf_46[] = {1902980,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_47[] = {2345348,147456,1902980,1728,128,1152};
int meta_buf_48[] = {1902980,1902980,1817920,1728,128};
int meta_buf_49[] = {1902980,2124164,1902980,221184};
int meta_buf_50[] = {1902980,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_51[] = {2345348,589824,2124164,1728,128,1152};
int meta_buf_52[] = {2124164,2124164,1818176,1728,128};
int meta_buf_53[] = {2124164,2124164,221184};
int meta_buf_54[] = {2124164,2345348,1,128,36,48,36,48,3,3,1,1,1,1};
int meta_buf_55[] = {2345348,0,2124164,1728,128,1152};
int meta_buf_56[] = {2124164,2124164,1818560,1728,128};
int meta_buf_57[] = {2124164,1902980,2124164,221184};
int meta_buf_58[] = {2124164,1605632,2345348,1728,1024,128};
int meta_buf_59[] = {1902980,2345348,1,36,48,64,72,96,4,4,2,2,1,1};
int meta_buf_60[] = {1902980,1902980,1819712,6912,64};
int meta_buf_61[] = {1902980,1902980,442368};
int meta_buf_62[] = {1902980,1902980,1819776,442368,64};
int meta_buf_63[] = {1902980,1902980,1819520,6912,64};
int meta_buf_64[] = {1902980,1769472,2787716,6912,512,64};
int meta_buf_65[] = {1902980,2787716,1,72,96,32,144,192,4,4,2,2,1,1};
int meta_buf_66[] = {1902980,1902980,1819872,27648,32};
int meta_buf_67[] = {1902980,1902980,884736};
int meta_buf_68[] = {1902980,1902980,1819840,884736,32};
int meta_buf_69[] = {1902980,1902980,1819904,27648,32};
int meta_buf_70[] = {1902980,1802240,2787716,27648,243,32};
int meta_buf_71[] = {1902980,2787716,1,144,192,3,144,192,9,9,1,1,4,4};
int meta_buf_72[] = {1902980,1902980,1820032,27648,3};
int meta_buf_73[] = {1902980,1902980,82944};
int meta_buf_74[] = {1902980,1902980,82944,1124007936,1124007936};
int* meta_buffers[] = {meta_buf_0,meta_buf_1,meta_buf_2,meta_buf_3,meta_buf_4,meta_buf_5,meta_buf_6,meta_buf_7,meta_buf_8,meta_buf_9,meta_buf_10,meta_buf_11,meta_buf_12,meta_buf_13,meta_buf_14,meta_buf_15,meta_buf_16,meta_buf_17,meta_buf_18,meta_buf_19,meta_buf_20,meta_buf_21,meta_buf_22,meta_buf_23,meta_buf_24,meta_buf_25,meta_buf_26,meta_buf_27,meta_buf_28,meta_buf_29,meta_buf_30,meta_buf_31,meta_buf_32,meta_buf_33,meta_buf_34,meta_buf_35,meta_buf_36,meta_buf_37,meta_buf_38,meta_buf_39,meta_buf_40,meta_buf_41,meta_buf_42,meta_buf_43,meta_buf_44,meta_buf_45,meta_buf_46,meta_buf_47,meta_buf_48,meta_buf_49,meta_buf_50,meta_buf_51,meta_buf_52,meta_buf_53,meta_buf_54,meta_buf_55,meta_buf_56,meta_buf_57,meta_buf_58,meta_buf_59,meta_buf_60,meta_buf_61,meta_buf_62,meta_buf_63,meta_buf_64,meta_buf_65,meta_buf_66,meta_buf_67,meta_buf_68,meta_buf_69,meta_buf_70,meta_buf_71,meta_buf_72,meta_buf_73,meta_buf_74};

extern "C" void init() {
    //static_buffer = (float*)malloc(9506180 * sizeof(float));
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

void im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(const int * meta_buffer)
{
    const float *im = (static_buffer + meta_buffer[0]);
    float *col = (static_buffer + meta_buffer[1]);

    const int N = meta_buffer[2];
    const int C1 = meta_buffer[3];
    const int H1 = meta_buffer[4];
    const int W1 = meta_buffer[5];
    const int H2 = meta_buffer[6];
    const int W2 = meta_buffer[7];
    const int KH = meta_buffer[8];
    const int KW = meta_buffer[9];
    const int SH = meta_buffer[10];
    const int SW = meta_buffer[11];
    const int PH = meta_buffer[12];
    const int PW = meta_buffer[13];

    for (int gid = 0; gid < N*H2*W2*KH*KW*C1; gid += 1) {
        const int c1 = gid % C1;
        const int kw = gid / C1 % KW;
        const int kh = gid / C1 / KW % KH;
        const int w2 = gid / C1 / KW / KH % W2;
        const int h2 = gid / C1 / KW / KH / W2 % H2;
        const int  n = gid / C1 / KW / KH / W2 / H2;
        
        const int h1 = h2 * SH - PH + kh;
        const int w1 = w2 * SW - PW + kw;

        col[gid] = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n*H1+h1)*W1+w1)*C1+c1];
    }
}


#ifndef INCLUDE_EIGEN
#define INCLUDE_EIGEN
#include <Eigen/Dense>
#endif

void sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(const int * meta_buffer)
{
    float *A = (static_buffer + meta_buffer[0]);
    float *B = (static_buffer + meta_buffer[1]);
    float *C = (static_buffer + meta_buffer[2]);

    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(A, meta_buffer[3], meta_buffer[5]);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(B, meta_buffer[5], meta_buffer[4]);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(C, meta_buffer[3], meta_buffer[4]);

    c_mat.noalias() = a_mat * b_mat;
}


void axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(const int * meta_buffer)
{
    const float *X = (static_buffer + meta_buffer[0]);
    float *Y = (static_buffer + meta_buffer[1]);
    const float *B = (static_buffer + meta_buffer[2]);
    const int N = meta_buffer[3];
    const int C = meta_buffer[4];
  
    for (int gid = 0; gid < N * C; gid += 1) {
        int c = gid % C;
        int n = gid / C;
        float result = X[gid] + B[c];

        Y[n * C + c] = result;
    }
}


void elu_1cb70152ce229367364539c8ddd7e909cd792fb676f59e3b872f8f31(const int * meta_buffer)
{
    const float *X = (static_buffer + meta_buffer[0]);
    float *Y = (static_buffer + meta_buffer[1]);

    const int N = meta_buffer[2];
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result < 0.0 ? (expf(result)-1) : result;      
        Y[gid] = result;
    }
}


void axiswisescale_3290c9beef6a91aef28301eaa1a14f62189981e6c1fc09f50855293f(const int * meta_buffer)
{
    const float *X = (static_buffer + meta_buffer[0]);
    float *Y = (static_buffer + meta_buffer[1]);
    const float *S = (static_buffer + meta_buffer[2]);
    const int N = meta_buffer[3];
    const int C = meta_buffer[4];
  
    for (int gid = 0; gid < N; gid += 1) {
        int c = gid % C;
        float result = X[gid] * S[c];

        Y[gid] = result;
    }
}


void relu_c19b7d5b2914f4d152413c95fd9de9d1ece00c3dcdacc64359d232a5(const int * meta_buffer)
{
    const float *X = (static_buffer + meta_buffer[0]);
    float *Y = (static_buffer + meta_buffer[1]);

    const int N = meta_buffer[2];
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result < 0.0 ? 0.0 : result;
        
        Y[gid] = result;
    }
}


void elementwisesum_df5df6a7c03c4feba54096a75ef74812e9bc18377631c4b39521a80d(const int * meta_buffer)
{
    const float *X0 = (static_buffer + meta_buffer[0]);
    const float *X1 = (static_buffer + meta_buffer[1]);
    float *Y = (static_buffer + meta_buffer[2]);
    const int N = meta_buffer[3];
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X0[gid] + X1[gid];

        Y[gid] = result;
    }
}


void col2im_c27ba017d8daabdc8a3c3b2e9bf5f029051ad380aed0be391c790d0e(const int * meta_buffer)
{
    const float *col = (static_buffer + meta_buffer[1]);
    float *im = (static_buffer + meta_buffer[0]);

    const int N = meta_buffer[2];
    const int C1 = meta_buffer[5];
    const int H1 = meta_buffer[6];
    const int W1 = meta_buffer[7];
    const int H2 = meta_buffer[3];
    const int W2 = meta_buffer[4];
    const int KH = meta_buffer[8];
    const int KW = meta_buffer[9];
    const int SH = meta_buffer[10];
    const int SW = meta_buffer[11];
    const int PH = meta_buffer[12];
    const int PW = meta_buffer[13];

    for (int gid = 0; gid < N*H1*W1*C1; gid += 1) {
        const int c1 = gid % C1;
        const int w1 = gid / C1 % W1;
        const int h1 = gid / C1 / W1 % H1;
        const int n = gid / C1 / W1 / H1;

        float sum = 0;
        for (int kh = 0; kh < KH; kh++) {
            const int h2 = (h1 + PH - kh) / SH;
            if ((h1 + PH - kh) % SH != 0 || h2 < 0 || h2 >= H2) continue;

            for (int kw = 0; kw < KW; kw++) {
                const int w2 = (w1 + PW - kw) / SW;
                if ((w1 + PW - kw) % SW != 0 || w2 < 0 || w2 >= W2) continue;
                
                sum += col[((((n * H2 + h2) * W2 + w2) * KH + kh) * KW + kw) * C1 + c1];
            }
        }
        
        im[gid] = sum; 
    }
}


void tanh_e8350db56083f84548b6a0abcb9432fa6464feeff5b46abf8592ad3b(const int * meta_buffer)
{
    const float *X = (static_buffer + meta_buffer[0]);
    float *Y = (static_buffer + meta_buffer[1]);

    const int N = meta_buffer[2];
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = tanhf(result);      
        Y[gid] = result;
    }
}


void scalaraffine_1551cfcbbf2312e6600c448733bf61e346c535051d0b4e719dccb7bc(const int * meta_buffer)
{
    const float *X = (static_buffer + meta_buffer[0]);
    float *Y = (static_buffer + meta_buffer[1]);

    const float scale = *((const float *)(& meta_buffer[3]));
    const float bias = *((const float *)(& meta_buffer[4]));
    const int N = meta_buffer[2];

    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result * scale + bias;

        Y[gid] = result;
    }
}

extern "C" void run() {
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_0);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_1);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_2);
elu_1cb70152ce229367364539c8ddd7e909cd792fb676f59e3b872f8f31(meta_buf_3);
axiswisescale_3290c9beef6a91aef28301eaa1a14f62189981e6c1fc09f50855293f(meta_buf_4);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_5);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_6);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_7);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_8);
elu_1cb70152ce229367364539c8ddd7e909cd792fb676f59e3b872f8f31(meta_buf_9);
axiswisescale_3290c9beef6a91aef28301eaa1a14f62189981e6c1fc09f50855293f(meta_buf_10);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_11);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_12);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_13);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_14);
elu_1cb70152ce229367364539c8ddd7e909cd792fb676f59e3b872f8f31(meta_buf_15);
axiswisescale_3290c9beef6a91aef28301eaa1a14f62189981e6c1fc09f50855293f(meta_buf_16);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_17);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_18);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_19);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_20);
relu_c19b7d5b2914f4d152413c95fd9de9d1ece00c3dcdacc64359d232a5(meta_buf_21);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_22);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_23);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_24);
elementwisesum_df5df6a7c03c4feba54096a75ef74812e9bc18377631c4b39521a80d(meta_buf_25);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_26);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_27);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_28);
relu_c19b7d5b2914f4d152413c95fd9de9d1ece00c3dcdacc64359d232a5(meta_buf_29);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_30);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_31);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_32);
elementwisesum_df5df6a7c03c4feba54096a75ef74812e9bc18377631c4b39521a80d(meta_buf_33);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_34);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_35);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_36);
relu_c19b7d5b2914f4d152413c95fd9de9d1ece00c3dcdacc64359d232a5(meta_buf_37);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_38);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_39);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_40);
elementwisesum_df5df6a7c03c4feba54096a75ef74812e9bc18377631c4b39521a80d(meta_buf_41);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_42);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_43);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_44);
relu_c19b7d5b2914f4d152413c95fd9de9d1ece00c3dcdacc64359d232a5(meta_buf_45);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_46);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_47);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_48);
elementwisesum_df5df6a7c03c4feba54096a75ef74812e9bc18377631c4b39521a80d(meta_buf_49);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_50);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_51);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_52);
relu_c19b7d5b2914f4d152413c95fd9de9d1ece00c3dcdacc64359d232a5(meta_buf_53);
im2col_407cc021db7d212d82c586be6dc289add9f37525deaf40c0b265f34f(meta_buf_54);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_55);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_56);
elementwisesum_df5df6a7c03c4feba54096a75ef74812e9bc18377631c4b39521a80d(meta_buf_57);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_58);
col2im_c27ba017d8daabdc8a3c3b2e9bf5f029051ad380aed0be391c790d0e(meta_buf_59);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_60);
elu_1cb70152ce229367364539c8ddd7e909cd792fb676f59e3b872f8f31(meta_buf_61);
axiswisescale_3290c9beef6a91aef28301eaa1a14f62189981e6c1fc09f50855293f(meta_buf_62);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_63);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_64);
col2im_c27ba017d8daabdc8a3c3b2e9bf5f029051ad380aed0be391c790d0e(meta_buf_65);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_66);
elu_1cb70152ce229367364539c8ddd7e909cd792fb676f59e3b872f8f31(meta_buf_67);
axiswisescale_3290c9beef6a91aef28301eaa1a14f62189981e6c1fc09f50855293f(meta_buf_68);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_69);
sgemm_49ee440e78a4467f5e364896610c9bdbdd5dbf08d70b98a210d579d8(meta_buf_70);
col2im_c27ba017d8daabdc8a3c3b2e9bf5f029051ad380aed0be391c790d0e(meta_buf_71);
axiswisebias_8707f1cef37d7ca012745f51782ab9aec3c9338a73bdf7f887146384(meta_buf_72);
tanh_e8350db56083f84548b6a0abcb9432fa6464feeff5b46abf8592ad3b(meta_buf_73);
scalaraffine_1551cfcbbf2312e6600c448733bf61e346c535051d0b4e719dccb7bc(meta_buf_74);

}

