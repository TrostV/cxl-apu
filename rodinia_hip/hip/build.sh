#!/bin/bash
export ROCM_PATH=/opt/rocm
for d in */ ; do
  [ -d "$d" ] || continue
  if [ -f "$d/Makefile" ] || [ -f "$d/makefile" ]; then
    printf "======================================\n%s\n======================================\n" "$d"
    ( cd "$d" && make )
    # read -p "Continue?"
  fi
done
