include ../../common/make.config

LOCAL_CC = gcc -g -O3 -Wall
CC := $(ROCM_PATH)/bin/hipcc

all : nn hurricane_gen

clean :
	rm -rf *.o nn hurricane_gen

nn : nn_cuda.cu
	$(CC) $< -o $@
clang: $(SRC)
	clang++ nn_cuda.cu -o nn -I../util --cuda-gpu-arch=sm_20 \
		-L/usr/local/cuda/lib64 -ldl -lrt -pthread -DTIMING

hurricane_gen : hurricane_gen.c
	$(LOCAL_CC) -o $@ $< -lm

#data :
#	mkdir data
#	./gen_dataset.sh
