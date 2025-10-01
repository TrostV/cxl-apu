#!/usr/bin/env bash
# To run the benchmarks with the original implementation do this:
# $ GEM5=/gem5/build/VEGA_X86/gem5.opt SUFFIX=orig ./run.sh all

GEM5=${GEM5:-/gem5/build/cxl_apu/gem5.opt}
CONF=${CONF:-/gem5/configs/example/apu_se.py}
RODINIA=${RODINIA:-/rodinia_hip}
RODINIA_BIN=${RODINIA_BIN:-${RODINIA}/bin}
RODINIA_DATA=${RODINIA_DATA:-${RODINIA}/data}

if [[ -v "$LATENCY" ]]; then
  lat="--to-dir-latency=$LATENCY"
fi

all=("b+tree" "bfs" "dwt2d" "gaussian" "hotspot" "hotspot3D" "lavaMD" "lud" "myocyte" "nn" "nw" "particlefilter" "pathfinder")

b+tree() {
  $GEM5 -d btree_$LATENCY$SUFFIX      \
        -r -e                         \
        $CONF -n 4 -u 4 $lat          \
        --cmd $RODINIA_BIN/b+tree.out \
        --options="file $RODINIA_DATA/b+tree/mil.txt command $RODINIA_DATA/b+tree/command.txt" 
}

bfs() {
  $GEM5 -d bfs_$LATENCY$SUFFIX     \
        -r -e                      \
        $CONF -n 4 -u 4 $lat       \
        --cmd $RODINIA_BIN/bfs.out \
        --options="file $RODINIA_DATA/bfs/graph65536.txt" 
}

dwt2d() {
  $GEM5 -d dwt2d_$LATENCY$SUFFIX    \
        -r -e                       \
        $CONF -n 4 -u 4 $lat        \
        --cmd $RODINIA_BIN/dwt2d    \
        --options="192.bmp -d 192x192 -f -5 -l 3" 
}

gaussian() {
  $GEM5 -d gaussian_$LATENCY$SUFFIX   \
        -r -e                         \
        $CONF -n 4 -u 4 $lat          \
        --cmd $RODINIA_BIN/gaussian   \
        --options="-f $RODINIA_DATA/gaussian/matrix4.txt" 
}

hotspot() {
  $GEM5 -d hotspot_$LATENCY$SUFFIX    \
        -r -e                         \
        $CONF -n 4 -u 4 $lat          \
        --cmd $RODINIA_BIN/hotspot    \
        --options="512 2 2 $RODINIA_DATA/hotspot/temp_512 $RODINIA_DATA/hotspot/power_512 output.out" 
}

hotspot3D() {
  $GEM5 -d hotspot3D_$LATENCY$SUFFIX    \
        -r -e                           \
        $CONF -n 4 -u 4 $lat            \
        --cmd $RODINIA_BIN/3D           \
        --options="512 8 100 $RODINIA_DATA/hotspot3D/power_512x8 $RODINIA_DATA/hotspot3D/temp_512x8 output.out" 
}

lavaMD() {
  $GEM5 -d lavaMD_$LATENCY$SUFFIX     \
        -r -e                         \
        $CONF -n 4 -u 4 $lat          \
        --cmd $RODINIA_BIN/lavaMD     \
        --options="-boxes1d 10"       
}

lud() {
  $GEM5 -d lud_$LATENCY$SUFFIX     \
        -r -e                      \
        $CONF -n 4 -u 4 $lat       \
        --cmd $RODINIA_BIN/lud_cuda\
        --options="-s 256 -v"      
}

myocyte() {
  $GEM5 -d myocyte_$LATENCY$SUFFIX     \
        -r -e                          \
        $CONF -n 4 -u 4 $lat           \
        --cmd $RODINIA_BIN/myocyte.out \
        --options="100 1 0"            
}

nn() {
  printf "${RODINIA_DATA}/nn/cane4_0.db\n${RODINIA_DATA}/nn/cane4_1.db\n${RODINIA_DATA}/nn/cane4_2.db\n${RODINIA_DATA}/nn/cane4_3.db" > filelist.txt
  $GEM5 -d nn_$LATENCY$SUFFIX       \
        -r -e                       \
        $CONF -n 4 -u 4 $lat        \
        --cmd $RODINIA_BIN/nn       \
        --options="filelist.txt -r 5 -lat 30 -lng 90" 

}

nw() {
  $GEM5 -d nw_$LATENCY$SUFFIX       \
        -r -e                       \
        $CONF -n 4 -u 4 $lat        \
        --cmd $RODINIA_BIN/needle   \
        --options="2048 10"         
}

particlefilter() {
  $GEM5 -d particlefilter_$LATENCY$SUFFIX       \
        -r -e                                   \
        $CONF -n 4 -u 4 $lat                    \
        --cmd $RODINIA_BIN/particlefilter_float \
        --options="-x 128 -y 128 -z 10 -np 1000" 
}

pathfinder() {
  $GEM5 -d pathfinder_$LATENCY$SUFFIX   \
        -r -e                           \
        $CONF -n 4 -u 4 $lat            \
        --cmd $RODINIA_BIN/pathfinder   \
        --options="100000 100 20"       
}


if [ "$#" -eq 1 ]; then 
  if [[ " ${all[*]} " =~ " $1 " ]]; then
    printf "Running the $1 benchmark\n" 
    $1
    exit $?
  elif [ "$1" == "all" ]; then
    printf "Running all benchmarks\n" 
    for b in "${all[@]}"; do
      $b &
    end
    wait
    printf "All benchmarks finished\n"
    exit 0
  fi
else 
  printf "Usage: $0 <benchmark>\n"
  printf "Where <benchmark> is one of:\n"
  printf "  - all (to run all benchmarks)\n"
  for b in "${all[@]}"; do
    printf "  - $b\n"
  done
  
  exit 1
fi

