#!/bin/bash

# BUILD SASUMO
# . ./SASUMO/scripts/install.sh ./

CPUS="64"

# try to shutdown existing ray instances
# ray stop

# # Start Ray
# ray start --head --port=6379  --num-cpus=$CPUS

# Run Simulation
# nohup python SASUMO/SASUMO/creator.py $SETTINGS_FILE  > $NOHUP 2> $NOHUP_ERROR < /dev/null &

# tail $NOHUP -f
F="/home/max/Development/airport-harper-sumo/SASUMO/input_files/randomness_for_optimization/uniform_analysis.yaml"

# python SASUMO/SASUMO/parameter_sweep.py $1

NS=("2" "4" "8" "16" "32" "5" "10" "20" "40");
for n in "${NS[@]}"; 
do
    # doing this because I am bad at bash
    export N=$n
    S=$(yq '.ParameterSweep.N=strenv(N)' $F)
    python SASUMO/SASUMO/creator.py --parameter-sweep "$S"
  # take action on each file. $f store current file name
  # perform some operation with the file
done