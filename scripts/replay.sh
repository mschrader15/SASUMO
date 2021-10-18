#!/bin/bash
# Variables required
SAMPLE_NUM="1038"
SA_ROOT="/media/HDD/max/sasumo-files/Car_Following_Params_V2_630AM/2021_10_06-10_11_53"
REPLAY_DIR_NAME="replay_gui"
export SIMULATION_ROOT="/home/max/remote/airport-harper-sumo"
export SENSITIVITY_ANALYSIS_OUTPUT="/media/HDD/max/sasumo-files/Car_Following_Params_V2_630AM"


# Try to fix the simulation params paths
LAST_ROOT="/home/max/tmp/airport_harper_sumo_sasumo/Car_Following_Params_V2_630AM/2021_10_06-10_11_53"
# replace file paths
sed -i s+$LAST_ROOT+$SA_ROOT+g "$SA_ROOT/sample_$SAMPLE_NUM/simulation_params.json"

# try to make the replay directory
mkdir -p "$SA_ROOT/sample_$SAMPLE_NUM/$REPLAY_DIR_NAME"


# run the replay
python ./SASUMO/utils/replay.py $SA_ROOT --sample_num $SAMPLE_NUM --results_dir $REPLAY_DIR_NAME