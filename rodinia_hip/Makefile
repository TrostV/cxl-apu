include common/make.config


export ROCM_PATH=/opt/rocm
RODINIA_BASE_DIR := $(shell pwd)
BIN_DIR := $(RODINIA_BASE_DIR)/bin

HIP_DIRS := backprop bfs cfd gaussian heartwall hotspot kmeans lavaMD leukocyte lud nn nw srad streamcluster particlefilter pathfinder mummergpu

all: HIP

HIP: 
	cd hip/b+tree;		    make; cp b+tree.out $(BIN_DIR)
	cd hip/bfs;           make; cp bfs.out $(BIN_DIR)
	cd hip/dwt2d;         make; cp dwt2d  $(BIN_DIR)
	cd hip/gaussian;      make; cp gaussian $(BIN_DIR)
	cd hip/hotspot;       make; cp hotspot $(BIN_DIR)
	cd hip/hotspot3D;     make; cp 3D $(BIN_DIR)
	cd hip/lavaMD;        make; cp lavaMD $(BIN_DIR)
	cd hip/leukocyte;     make; cp CUDA/leukocyte $(BIN_DIR)
	cd hip/lud;           make; cp cuda/lud_cuda $(BIN_DIR)
	cd hip/nn;            make; cp nn $(BIN_DIR)
	cd hip/nw;            make; cp needle $(BIN_DIR)
	cd hip/particlefilter;make; cp particlefilter_float $(BIN_DIR)       
	cd hip/pathfinder;		make; cp pathfinder $(BIN_DIR)

	

clean:
	cd $(BIN_DIR); rm -f *
	for dir in $(HIP_DIRS) ; do cd cuda/$$dir ; make clean ; cd ../.. ; done
	