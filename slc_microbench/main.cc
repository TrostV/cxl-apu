#include "kernels.hpp"
#include <cstdio>
#include <cstdlib>
#include <hip/hip_runtime.h>

#define touch(addr, i) do {                           \
  asm("movss %%xmm0, %0":: "m" (addr[i].x) : "xmm0"); \
  asm("movss %%xmm0, %0":: "m" (addr[i].y) : "xmm0"); \
  asm("movss %%xmm0, %0":: "m" (addr[i].z) : "xmm0"); \
  asm("movss %%xmm0, %0":: "m" (addr[i].w) : "xmm0"); \
} while(0)

#define write(addr, i) do {       \
  asm("movss %0, %%xmm0": "=m" (addr[i].x) :: "xmm0"); \
  asm("movss %0, %%xmm0": "=m" (addr[i].y) :: "xmm0"); \
  asm("movss %0, %%xmm0": "=m" (addr[i].z) :: "xmm0"); \
  asm("movss %0, %%xmm0": "=m" (addr[i].w) :: "xmm0"); \
} while(0)

static const char usage[] = "Usage: %s <THREADS> <BLOCK> <ITERATIONS> <BENCHMARK>\n"
                          "\n  Possible BENCHMARK values:\n"
                            "    0: GPU read\n"
                            "    1: GPU read, CPU read\n"
                            "    2: GPU read, CPU write\n"


                            "    3: GPU write\n"
                            "    4: GPU write, CPU read\n"
                            "    5: GPU write, CPU write\n"


                            "    6: GPU read/write\n"
                            "    7: GPU read/write, CPU read\n"
                            "    8: GPU read/write, CPU write\n"
                            "    9: GPU read/write, CPU read/write\n";

int main(int argc, char** argv) {
  if (argc != 5) {
    fprintf(stderr, usage, argv[0]);
    return 1;
  }
  int threads = atoi(argv[1]);
  int blocks = atoi(argv[2]);
  int iterations = atoi(argv[3]);
  int benchmark = atoi(argv[4]);
  printf("%d Blocks, %d Threads, %d Iterations\n", blocks, threads, iterations);
  unsigned size = threads * blocks * iterations * 100;
  float4 *data = static_cast<float4*>(calloc(size, sizeof(float4)));
  if (!data) {
    fprintf(stderr, "Failed to allocate memory for data\n");
    return 1;
  }

  switch (benchmark) {
    case 0:
      printf("Running GPU read\n");
      for (int i = 0; i < iterations; i++) {
        read_bench<<<dim3(blocks), dim3(threads)>>>(data);
        hipDeviceSynchronize();
      }
      break;

    case 1:
      printf("Running GPU read, CPU read\n");
      for (int i = 0; i < iterations; i++) {
        read_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++)
          touch(data, j);

        hipDeviceSynchronize();
      }
      break;

    case 2:
      printf("Running GPU read, CPU write\n");
      for (int i = 0; i < iterations; i++) {
        read_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++) {
          write(data, j);
        }

        hipDeviceSynchronize();
      }
      break;

    case 3:
      printf("Running GPU write\n");
      for (int i = 0; i < iterations; i++) {
        write_bench<<<dim3(blocks), dim3(threads)>>>(data);

        hipDeviceSynchronize();
      }
      break;

    case 4:
      printf("Running GPU write, CPU read\n");
      for (int i = 0; i < iterations; i++) {
        write_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++)
          touch(data, j);

        hipDeviceSynchronize();
      }
      break;

    case 5:
      printf("Running GPU write, CPU write\n");
      for (int i = 0; i < iterations; i++) {
        write_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++) {
          write(data, j);
        }

        hipDeviceSynchronize();
      }
      break;

    case 6:
      printf("Running GPU read/write\n");
      for (int i = 0; i < iterations; i++) {
        read_write_bench<<<dim3(blocks), dim3(threads)>>>(data);

        hipDeviceSynchronize();
      }
      break;

    case 7:
      printf("Running GPU read/write, CPU read\n");
      for (int i = 0; i < iterations; i++) {
        read_write_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++)
          touch(data, j);

      }
      break;

    case 8:
      printf("Running GPU read/write, CPU write\n");
      for (int i = 0; i < iterations; i++) {
        read_write_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++) {
          write(data, j);
        }

        hipDeviceSynchronize();
      }
      break;

    case 9:
      printf("Running GPU read/write, CPU read/write\n");
      for (int i = 0; i < iterations; i++) {
        read_write_bench<<<dim3(blocks), dim3(threads)>>>(data);
        for(int j = 0; j < size; j++) {
          touch(data, j);
          write(data, j);
        }

        hipDeviceSynchronize();
      }
    default:
      fprintf(stderr, "Invalid benchmark value %d\n", benchmark);
      free(data);
      return 1;
  }

  return 0;
}