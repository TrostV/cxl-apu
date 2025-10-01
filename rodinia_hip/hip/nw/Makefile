include ../../common/make.config

CC := $(ROCM_PATH)/bin/hipcc

SRC = needle.cu

EXE = needle

release: $(SRC)
	$(CC) ${KERNEL_DIM} $(SRC) -o $(EXE) 

clang: $(SRC)
	clang++ $(SRC) -o $(EXE) -I../util \
		  -ldl -lrt -pthread -DTIMING

enum: $(SRC)
	$(CC) ${KERNEL_DIM} -deviceemu $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR) 

debug: $(SRC)
	$(CC) ${KERNEL_DIM} -g $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR) 

debugenum: $(SRC)
	$(CC) ${KERNEL_DIM} -g -deviceemu $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR) 

clean: $(SRC)
	rm -f $(EXE) $(EXE).linkinfo result.txt
