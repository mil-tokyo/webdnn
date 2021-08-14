#include <algorithm>
#include <cmath>
#include <Eigen/Dense>
#include "../../common/kernel.hpp"
#include "../../common/unary.hpp"

extern "C"
{
  static void add_bias(float *c, float *y, int m, int n) {
    for (int row = 0; row < m; row++)
    {
      for (int col = 0; col < n; col++)
      {
        y[row * n + col] += c[col];
      }
    }
  }

  static void do_gemm_transa0_transb0(float *a, float *b, float *y, int m, int n, int k)
  {
    // 'const' float *a raises compile error
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(a, m, k);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(b, k, n);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > y_mat(y, m, n);

    y_mat.noalias() = a_mat * b_mat;
  }

  void WEBDNN_KERNEL kernel_gemm_transa0_transb0(float *a, float *b, float *y, int m, int n, int k)
  {
    do_gemm_transa0_transb0(a, b, y, m, n, k);
  }

  void WEBDNN_KERNEL kernel_gemm_transa0_transb0_c(float *a, float *b, float *c, float *y, int m, int n, int k)
  {
    do_gemm_transa0_transb0(a, b, y, m, n, k);
    add_bias(c, y, m, n);
  }

  static void do_gemm_transa0_transb1(float *a, float *b, float *y, int m, int n, int k)
  {
    // 'const' float *a raises compile error
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > a_mat(a, m, k);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> > b_mat(b, k, n);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > y_mat(y, m, n);

    y_mat.noalias() = a_mat * b_mat;
  }

  void WEBDNN_KERNEL kernel_gemm_transa0_transb1(float *a, float *b, float *y, int m, int n, int k)
  {
    do_gemm_transa0_transb1(a, b, y, m, n, k);
  }

  void WEBDNN_KERNEL kernel_gemm_transa0_transb1_c(float *a, float *b, float *c, float *y, int m, int n, int k)
  {
    do_gemm_transa0_transb1(a, b, y, m, n, k);
    add_bias(c, y, m, n);
  }

  
  static void do_gemm_transa1_transb0(float *a, float *b, float *y, int m, int n, int k)
  {
    // 'const' float *a raises compile error
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> > a_mat(a, m, k);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > b_mat(b, k, n);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > y_mat(y, m, n);

    y_mat.noalias() = a_mat * b_mat;
  }

  void WEBDNN_KERNEL kernel_gemm_transa1_transb0(float *a, float *b, float *y, int m, int n, int k)
  {
    do_gemm_transa1_transb0(a, b, y, m, n, k);
  }

  void WEBDNN_KERNEL kernel_gemm_transa1_transb0_c(float *a, float *b, float *c, float *y, int m, int n, int k)
  {
    do_gemm_transa1_transb0(a, b, y, m, n, k);
    add_bias(c, y, m, n);
  }

  
  static void do_gemm_transa1_transb1(float *a, float *b, float *y, int m, int n, int k)
  {
    // 'const' float *a raises compile error
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> > a_mat(a, m, k);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> > b_mat(b, k, n);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > y_mat(y, m, n);

    y_mat.noalias() = a_mat * b_mat;
  }

  void WEBDNN_KERNEL kernel_gemm_transa1_transb1(float *a, float *b, float *y, int m, int n, int k)
  {
    do_gemm_transa1_transb1(a, b, y, m, n, k);
  }

  void WEBDNN_KERNEL kernel_gemm_transa1_transb1_c(float *a, float *b, float *c, float *y, int m, int n, int k)
  {
    do_gemm_transa1_transb1(a, b, y, m, n, k);
    add_bias(c, y, m, n);
  }
}
