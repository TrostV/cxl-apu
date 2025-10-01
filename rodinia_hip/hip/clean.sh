#!/bin/sh
for d in */ ; do
  [ -d "$d" ] || continue
  ( cd "$d" && make clean || true )
done
