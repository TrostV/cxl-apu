include ../../common/make.config

CC := $(ROCM_PATH)/bin/hipcc

# INCLUDE := $(CUDA_DIR)/include

SRC = hotspot.cu

EXE = hotspot

release: $(SRC)
	$(CC) $(KERNEL_DIM) $(SRC) -o $(EXE) 

enum: $(SRC)
	$(CC) $(KERNEL_DIM) -deviceemu $(SRC) -o $(EXE)

debug: $(SRC)
	$(CC) $(KERNEL_DIM) -g $(SRC) -o $(EXE) 

debugenum: $(SRC)
	$(CC) $(KERNEL_DIM) -g -deviceemu $(SRC) -o $(EXE) 

clean: $(SRC)
	rm -f $(EXE) $(EXE).linkinfo result.txt
