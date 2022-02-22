#!/bin/sh

cd /backup || exit

for f in *; do
  f_b=$(basename "$f")
  tar cf "/compressed/$f_b.tar" "${f}"
done
