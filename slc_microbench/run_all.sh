#!/bin/bash
# To run the benchmarks with the original implementation do this:
# $ GEM5=/gem5/build/VEGA_X86/gem5.opt SUFFIX=orig ./run_all.sh


GEM5=${GEM5:-/gem5/build/cxl_apu/gem5.opt}
CONF=${CONF:-/gem5/configs/example/apu_se.py}

for bench in $(seq 0 9); do 
  printf "Starting benchmark %d\n" $bench
  $GEM5 -d slc_microbench_out_$bench$SUFFIX \
        -r -e \
        $CONF -n 4 -u 4 \
        --cmd slc_microbench --options "32 32 50 $bench" & 
done

wait
printf "All done\n"