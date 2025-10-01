#!/bin/bash
# To extract from the benchmarks of the original implementation do this:
# $ SUFFIX=orig ./extract_stats.sh

SEPARATOR=";"
GREP="rg" # if you don't have ripgrep, change to "grep"

# Simulated seconds
# Note SimSeconds is calculated per kernel, so we need to sum them up
## GPU only benchmarks
printf "Benchmark${SEPARATOR}SimSeconds\n" > GPUonly$SUFFIX.csv
#       0      3       6
names=("read" "write" "mixed")
n=0

for i in 0 3 6; do
   $GREP "simSeconds" slc_microbench_out_$i$SUFFIX/stats.txt \
   | awk -v bench="${names[$n]}" -v SEPARATOR="${SEPARATOR}" \
   '{s+=$2} END {print bench SEPARATOR s}' >> GPUonly$SUFFIX.csv
  n=$((n+1))
done

## GPU+CPU benchmarks
printf "Benchmark${SEPARATOR}SimSeconds\n" > GPUCPU$SUFFIX.csv
#       1           2            4             5
names=("read+read" "read+write" "write+write" "write+read")
n=0

for i in 1 2 4 5; do
  $GREP "simSeconds" slc_microbench_out_$i$SUFFIX/stats.txt \
   | awk -v bench="${names[$n]}" -v SEPARATOR="${SEPARATOR}" \
   '{s+=$2} END {print bench SEPARATOR s}' >> GPUCPU$SUFFIX.csv
  n=$((n+1))
done

# Average latency
# NOTE: Average latency is calculated per kernel, so we need to average the averages
printf "Benchmark${SEPARATOR}AvrgLatency\n" > AvrgLatency_ST$SUFFIX.csv
names=("read" "read+read" "read+write" "write" "write+write" "write+read")
for i in 0 1 2 3 4 5; do
  $GREP "system\.ruby\.RequestType\.ST\.latency_hist_seqr::mean" slc_microbench_out_$i$SUFFIX/stats.txt \
    | awk -v bench="${names[$i]}" -v SEPARATOR="${SEPARATOR}" \
    '{s+=$2; c++} END {print bench SEPARATOR s/c}' >> AvrgLatency_ST$SUFFIX.csv
done

printf "Benchmark${SEPARATOR}AvrgLatency\n" > AvrgLatency_LD$SUFFIX.csv
for i in 0 1 2 3 4 5; do
  $GREP "system\.ruby\.RequestType\.LD\.latency_hist_seqr::mean" slc_microbench_out_$i$SUFFIX/stats.txt \
    | awk -v bench="${names[$i]}" -v SEPARATOR="${SEPARATOR}" \
    '{s+=$2; c++} END {print bench SEPARATOR s/c}' >> AvrgLatency_LD$SUFFIX.csv
done
