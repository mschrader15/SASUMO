#! /bin/sh

DIRECTORIES="$1/*"
for f in $DIRECTORIES
do
  echo "$f"
  python SASUMO/SASUMO/utils/process_output.py $f --parameter-sweep
done