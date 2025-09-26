HIPCC=/opt/rocm/bin/hipcc
CXXFLAGS=-O3 -Wall

all: slc_microbench
clean: 
        rm *.o slc_microbench
.PHONY: all clean


slc_microbench: main.o kernels.o
        $(HIPCC) $^ -o $@ $(CXXFLAGS)

%.o: %.cc
        $(HIPCC) $< -o $@ -c $(CXXFLAGS)