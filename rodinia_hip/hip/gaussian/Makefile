include ../../common/make.config

CC := $(ROCM_PATH)/bin/hipcc

# INCLUDE := $(CUDA_DIR)/include

SRC = gaussian.cu
EXE = gaussian

release: $(SRC)
	$(CC) $(KERNEL_DIM) $(SRC) -o $(EXE)
	
clang: $(SRC)
	clang++ $(SRC) -o $(EXE) -I../util --cuda-gpu-arch=sm_20 \
		-L/usr/local/cuda/lib64  -ldl -lrt -pthread -DTIMING

clean:
	rm gaussian
