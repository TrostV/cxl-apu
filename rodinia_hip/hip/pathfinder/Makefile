include ../../common/make.config

CC := $(ROCM_PATH)/bin/hipcc
INCLUDE := $(CUDA_DIR)/include

SRC = pathfinder.cu

EXE = pathfinder

release:
	$(CC) $(SRC) -o $(EXE) 

clang: $(SRC)
	clang++ $(SRC) -o $(EXE) -I../util  \
		 -ldl -lrt -pthread -DTIMING

enum:
	$(CC) -deviceemu $(SRC) -o $(EXE) 

debug:
	$(CC) -g $(SRC) -o $(EXE) 

debugenum:
	$(CC) -g -deviceemu $(SRC) -o $(EXE) 

clean:
	rm -f pathfinder
