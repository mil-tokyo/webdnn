#include <iostream>
#include <cstdint>
#include <chrono>
#include <Eigen/Dense>

// g++ gemm.cpp -O3 --std=c++11
// em++ gemm.cpp -O3 -std=c++11 -s "EXPORTED_FUNCTIONS=['_bench']" -s "WASM=1" -s "TOTAL_MEMORY=67108864" -o gemm.js

using namespace std;

class sgemm_data
{
  public:
    float *a, *b, *c;
    int m, n, k;

    sgemm_data(int m, int n, int k)
    {
        this->m = m;
        this->n = n;
        this->k = k;

        a = new float[m * k];
        b = new float[k * n];
        c = new float[m * n]; // filled with 0

        fill_var(a, m * k);
        fill_var(b, k * n);
    }

    ~sgemm_data()
    {
        delete[] a;
        delete[] b;
        delete[] c;
    }

  private:
    void fill_var(float *data, int size)
    {
        for (int i = 0; i < size; i++)
        {
            data[i] = (float)i / size;
        }
    }
};

void sgemm_naive(sgemm_data &data)
{
    const float *a = data.a;
    const float *b = data.b;
    float *c = data.c;
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    for (int row = 0; row < m; row++)
    {
        for (int col = 0; col < n; col++)
        {
            float sum = 0.0F;
            for (int ip = 0; ip < k; ip++)
            {
                sum += a[row * k + ip] * b[n * ip + col];
            }
            c[row * n + col] = sum;
        }
    }
}


void sgemm_eigen(sgemm_data &data)
{
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(data.a, m, k);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(data.b, k, n);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(data.c, m, n);

    c_mat.noalias() = a_mat * b_mat;
}


class int8gemm_data
{
  public:
    int8_t *a, *b;
    int32_t *c;
    int m, n, k;

    int8gemm_data(int m, int n, int k)
    {
        this->m = m;
        this->n = n;
        this->k = k;

        a = new int8_t[m * k];
        b = new int8_t[k * n];
        c = new int32_t[m * n]; // filled with 0

        fill_var(a, m * k);
        fill_var(b, k * n);
    }

    ~int8gemm_data()
    {
        delete[] a;
        delete[] b;
        delete[] c;
    }

  private:
    void fill_var(int8_t *data, int size)
    {
        for (int i = 0; i < size; i++)
        {
            data[i] = (int8_t)(i % 256);
        }
    }
};

void int8gemm_naive(int8gemm_data &data)
{
    const int8_t *a = data.a;
    const int8_t *b = data.b;
    int32_t *c = data.c;
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    for (int row = 0; row < m; row++)
    {
        for (int col = 0; col < n; col++)
        {
            int32_t sum = 0;
            for (int ip = 0; ip < k; ip++)
            {
                int16_t aval = a[row * k + ip];
                int16_t bval = b[n * ip + col];
                int16_t mul = aval * bval;
                sum += mul;
            }
            c[row * n + col] = sum;
        }
    }
}

void int8gemm_eigen_cast(int8gemm_data &data)
{
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    int32_t *a_int32_data = new int32_t[m*k];
    for (int i = 0; i < m*k; i++)
    {
        a_int32_data[i] = data.a[i];
    }
    int32_t *b_int32_data = new int32_t[k*n];
    for (int i = 0; i < k*n; i++)
    {
        b_int32_data[i] = data.b[i];
    }
    Eigen::Map<Eigen::Matrix<int32_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(a_int32_data, m, k);
    Eigen::Map<Eigen::Matrix<int32_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(b_int32_data, k, n);
    Eigen::Map<Eigen::Matrix<int32_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(data.c, m, n);

    c_mat.noalias() = a_mat * b_mat;
    delete[] a_int32_data;
    delete[] b_int32_data;
}

void int8gemm_eigen_wrong(int8gemm_data &data)
{
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    int8_t* c_int8_data = new int8_t[m*n];
    Eigen::Map<Eigen::Matrix<int8_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(data.a, m, k);
    Eigen::Map<Eigen::Matrix<int8_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(data.b, k, n);
    Eigen::Map<Eigen::Matrix<int8_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(c_int8_data, m, n);

    c_mat.noalias() = a_mat * b_mat;
    data.c[0] = c_int8_data[0];
}

class int32gemm_data
{
  public:
    int32_t *a, *b;
    int32_t *c;
    int m, n, k;

    int32gemm_data(int m, int n, int k)
    {
        this->m = m;
        this->n = n;
        this->k = k;

        a = new int32_t[m * k];
        b = new int32_t[k * n];
        c = new int32_t[m * n]; // filled with 0

        fill_var(a, m * k);
        fill_var(b, k * n);
    }

    ~int32gemm_data()
    {
        delete[] a;
        delete[] b;
        delete[] c;
    }

  private:
    void fill_var(int32_t *data, int size)
    {
        for (int i = 0; i < size; i++)
        {
            data[i] = (int32_t)(i % 256);
        }
    }
};

void int32gemm_naive(int32gemm_data &data)
{
    const int32_t *a = data.a;
    const int32_t *b = data.b;
    int32_t *c = data.c;
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    for (int row = 0; row < m; row++)
    {
        for (int col = 0; col < n; col++)
        {
            int32_t sum = 0;
            for (int ip = 0; ip < k; ip++)
            {
                sum += a[row * k + ip] * b[n * ip + col];
            }
            c[row * n + col] = sum;
        }
    }
}

void int32gemm_eigen(int32gemm_data &data)
{
    const int m = data.m;
    const int n = data.n;
    const int k = data.k;

    Eigen::Map<Eigen::Matrix<int32_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(data.a, m, k);
    Eigen::Map<Eigen::Matrix<int32_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(data.b, k, n);
    Eigen::Map<Eigen::Matrix<int32_t, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(data.c, m, n);

    c_mat.noalias() = a_mat * b_mat;
}


extern "C" int run(int mode, int m, int n, int k, int times)
{
    int dummy_result = 0;
    switch (mode)
    {
    case 0:
    {
        sgemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            sgemm_naive(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    case 1:
    {
        int8gemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            int8gemm_naive(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    case 2:
    {
        sgemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            sgemm_eigen(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    case 3:
    {
        int8gemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            int8gemm_eigen_cast(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    case 4:
    {
        int32gemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            int32gemm_naive(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    case 5:
    {
        int32gemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            int32gemm_eigen(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    case 6:
    {
        int8gemm_data data(m, n, k);
        for (int t = 0; t < times; t++)
        {
            int8gemm_eigen_wrong(data);
            dummy_result += (int)data.c[0];
        }
    }
    break;
    }

    return dummy_result;
}

volatile int dummy_result = 0;
#ifdef __EMSCRIPTEN__
int main()
{
    return 0;
}

extern "C" void bench(int mode, int m, int n, int k, int times)
{
    dummy_result = run(mode, m, n, k, times);
}
#else
void bench(int m, int n, int k, int times)
{
    for (int mode = 0; mode < 7; mode++)
    {
        auto start = std::chrono::system_clock::now();

        dummy_result = run(mode, m, n, k, times);

        auto end = std::chrono::system_clock::now();
        auto dur = end - start;
        auto msec = std::chrono::duration_cast<std::chrono::milliseconds>(dur).count();
        auto single_run_msec = msec / times;
        std::cout << "mode" << mode << "," << single_run_msec << " ms" << std::endl;
    }
}

int main()
{
    bench(512, 512, 512, 10);
    return 0;
}
#endif
