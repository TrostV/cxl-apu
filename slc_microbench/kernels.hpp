#pragma once
#include <hip/hip_runtime.h>
#define F4_TO_INT128(f4) (*(reinterpret_cast<__int128*>(&f4)))
#define flat_load_dwordx4(addr, data) asm volatile("flat_load_dwordx4 %0, %1" : "=v"(data) : "v"(addr))
#define flat_load_dwordx4_slc(addr, data) asm volatile("flat_load_dwordx4 %0, %1 slc" : "=v"(data) : "v"(addr))
// For some reason the this doesn't work when passing float4 directly. We cast to __int128 instead.
#define flat_store_dwordx4_slc(addr, data) asm volatile("flat_store_dwordx4 %0, %1 slc" :: "v"(addr), "v"(F4_TO_INT128(data)))
#define flat_store_dwordx4(addr, data) asm volatile("flat_store_dwordx4 %0, %1" :: "v"(addr), "v"(F4_TO_INT128(data)))



extern __global__ void read_bench(float4 *in);
extern __global__ void read_bench_no_slc(float4 *in);
extern __global__ void write_bench(float4 *out);
extern __global__ void write_bench_no_slc(float4 *out);
extern __global__ void read_write_bench(float4 *inout);
extern __global__ void read_write_bench_no_slc(float4 *inout);