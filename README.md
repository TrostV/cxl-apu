# CXL APU
This is a proof-of-concept of a APU system using the CXL memory pooling.
It is based on the gem5 simulator and the VIPER GPU model.

## Building 
Copy contents of gem5 directory to your gem5 source directory. (Tested with gem5 version `25.0`)
Use the `gcn-gpu` docker provided by gem5 as your build environment, e.g. with:
```
docker run                                     \
        --device /dev/kvm                      \
        --volume path/to/your/gem5:/gem5       \
        -u $UID:$GID                           \
        -it ghcr.io/gem5/gcn-gpu:v25-0
``` 

Then configure a build with:
```
/gem5 $ scons defconfig build/cxl_apu/ build_opts/VEGA_X86
/gem5 $ scons setconfig build/cxl_apu/ RUBY_PROTOCOL_GPU_VIPER_CXL_MESIF=y RUBY_PROTOCOL_GPU_VIPER=n PROTOCOL=GPU_VIPER_CXL_MESIF
```
Finally build with:
```
/gem5 $ scons build/cxl_apu/gem5.opt -j<number_of_cores>
```

## Running
Any HIP 4.0 Binary can be used, though for maximum compatibility it should be compiled in the `gcn-gpu` docker.
Running the simulation is done with: (this should also be run within the docker)
```
/gem5/build/cxl_apu/gem5.opt /gem5/configs/example/apu_se.py -c <BINARY-PATH> -u <NUMBER_CUS> -n <NUMBER_CORES>
```
> [!WARNING]
> Number of CPUs must be >2 else the simulation will fail.
> See [this](https://www.mail-archive.com/gem5-users@gem5.org/msg19940.html)

