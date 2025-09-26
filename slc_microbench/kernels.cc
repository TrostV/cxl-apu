#include "kernels.hpp"
#include <hip/hip_runtime.h>

__global__ void read_bench(float4 *in) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  float4 data;
  #pragma unroll
  for (unsigned i = 0; i < 100; i++) {
    flat_load_dwordx4_slc(&in[idx + i], data);
  }
}

__global__ void write_bench(float4 *out) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  float4 data = make_float4(1.0f, 2.0f, 3.0f, 4.0f);
  #pragma unroll
  for (unsigned i = 0; i < 100; i++) {
    flat_store_dwordx4_slc(&out[idx + i], data);
  }
}

__global__ void read_write_bench(float4 *inout) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  float4 data;
  #pragma unroll
  for (unsigned i = 0; i < 100; i++) {
    flat_load_dwordx4_slc(&inout[idx + i], data);
    flat_store_dwordx4_slc(&inout[idx + i], data);
  }
}