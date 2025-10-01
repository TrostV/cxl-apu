#!/usr/bin/env bash
# To extract from the benchmarks of the original implementation do this:
# $ SUFFIX=orig ./extract_stats.sh
SEPARATOR=${SEPARATOR:-";"}
GREP=${GREP:-rg} # If you don't have ripgrep, use grep


all=("b+tree" "bfs" "dwt2d" "gaussian" "hotspot" "hotspot3D" "lavaMD" "lud" "myocyte" "nn" "nw" "particlefilter" "pathfinder")
all_lats=(120 140 160 180 200)

tcc_hitrate() {
  printf "Benchmark${SEPARATOR}Hits${SEPARATOR}Accesses\n" > TCC_hits$SUFFIX.csv

  for bench in "${all[@]}"; do
    file=${bench}_$LATENCY$SUFFIX/stats.txt

    $GREP "system.ruby.tcc_cntrl0.L2cache.m_demand_hits" $file         \
      | awk -v bench=$bench -v SEPARATOR=$SEPARATOR                    \
      '{s+=$2} END {printf "%s%s%.0f%s", bench, SEPARATOR, s, SEPARATOR}'\
      >> TCC_hits$SUFFIX.csv
      
    $GREP "system.ruby.tcc_cntrl0.L2cache.m_demand_accesses" $file \
      | awk '{s+=$2} END {print s}'                                \
      >> TCC_hits$SUFFIX.csv
    
  done
}

overall_rtime() {
  printf "Benchmark${SEPARATOR}simSeconds\n" > overall_rtime$SUFFIX.csv
  for bench in "${all[@]}"; do
    file=${bench}_$LATENCY$SUFFIX/stats.txt

    $GREP "simSeconds" $file                        \
      | awk -v bench=$bench -v SEPARATOR=$SEPARATOR \
      '{s+=$2} END {print bench SEPARATOR s}'       \
      >> overall_rtime$SUFFIX.csv
  done
}

overall_ipc() {
  printf "Benchmark${SEPARATOR}Instructions${SEPARATOR}Cycles\n" > overall_ipc$SUFFIX.csv
  for bench in "${all[@]}"; do
    file=${bench}_$LATENCY$SUFFIX/stats.txt

    $GREP "system.cpu0.commitStats0.numInsts" $file                     \
      | awk -v bench=$bench -v SEPARATOR=$SEPARATOR                     \
      '{s+=$2} END {printf "%s%s%.0f%s", bench, SEPARATOR, s, SEPARATOR}' \
      >> overall_ipc$SUFFIX.csv

    $GREP "system.cpu0.numCycles" $file \
      | awk '{s+=$2} END {print s}'     \
      >> overall_ipc$SUFFIX.csv
  done
}

latency_rtime() {
  printf "Latency${SEPARATOR}" > latency_rtime.csv
  for bench in "${all[@]}"; do
    printf "%s%s" "$bench" "$SEPARATOR" >> latency_rtime.csv
  done
  printf "\n" >> latency_rtime.csv
  for lat in "${all_lats[@]}"; do
  row="$lat"
  for bench in "${all[@]}"; do
    file=${bench}_$lat/stats.txt
    val=$($GREP "simSeconds" "$file" | awk '{s+=$2} END {print s}')
    row+="${SEPARATOR}${val}"
  done
  printf "$row\n" >> latency_rtime.csv
done
  
  # Post process 
  python3 -c """import numpy as np
from sklearn.metrics import r2_score as r2
raw = np.loadtxt('latency_rtime.csv', delimiter=';', skiprows=1)
index = raw[:,0].astype(int)
data = raw[:,1:]

speedup = data[0]/data

log = np.log(speedup)
geomeans = np.exp(np.mean(log, axis=1))
s_y = log.std(ddof=1, axis=1)

upper_err = geomeans*np.exp(s_y)  - geomeans
lower_err = geomeans*np.exp(-s_y) - geomeans

out = np.column_stack((index, geomeans, upper_err, np.abs(lower_err)))
np.savetxt('latency_rtime.csv', out, fmt='%.0f;%f;%f;%f', header='Latency;Speedup;ErrLower;ErrUpper', comments='')

# Linfit
errors = np.sqrt((upper_err**2 + lower_err**2) / 2)
errors[0] = 1e-6 # Avoid div by 0
print(f'Linear fit errors: {errors}')
weights = 1 / errors**2
weights[0] = 1

coeffs = np.polyfit(index, geomeans, 1, w=weights)
slope, intercept = coeffs

print(f'Linfit: {slope}*x + {intercept}')
print(f'R^2: {r2(geomeans, slope*index + intercept,sample_weight=weights)}')
"""
}

if [ $# -ne 1 ]; then 
  printf "Usage: $0 <tcc_hitrate|overall_rtime|overall_ipc|latency_rtime>\n"
  exit 1
fi
if [[ -z "$LATENCY" && $1 -ne "latency_rtime" ]]; then
  printf "WARNING: No LATENCY environment variable set. If not running original implementation, set it to the selected latency.\n"
fi

$1 

exit $?