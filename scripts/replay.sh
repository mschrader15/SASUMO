#!/bin/bash
export SIMULATION_ROOT="/home/max/remote/airport-harper-sumo"
export SENSITIVITY_ANALYSIS_OUTPUT="/media/HDD/max/sasumo-files/Simplified_Car_Following"

# Variables required
SAMPLE_NUM="1197"
RUN_DATETIME="2021_11_03-08_04_35"
SA_ROOT="/media/HDD/max/sasumo-files/Simplified_Car_Following"
REPLAY_DIR_NAME="replay"
DETECTOR_FILE="$SIMULATION_ROOT/sumo-xml/sasumo-xml/detectors/detectors.add.xml"


# Try to fix the simulation params paths
LAST_ROOT="/home/max/tmp/airport_harper_sumo_sasumo/Simplified_Car_Following"
# replace file paths
sed -i s+$LAST_ROOT+$SA_ROOT+g "$SA_ROOT/$RUN_DATETIME/sample_$SAMPLE_NUM/simulation_params.json"

# try to make the replay directory
mkdir -p "$SA_ROOT/$RUN_DATETIME/sample_$SAMPLE_NUM/$REPLAY_DIR_NAME"

# copy over the detector file, as it is required to by the simulation and the parameter file has the wrong path
cp $DETECTOR_FILE "$SA_ROOT/$RUN_DATETIME/sample_$SAMPLE_NUM/__temp__.detector.add.xml"

# run the replay
python ./SASUMO/utils/replay.py "$SA_ROOT/$RUN_DATETIME" --sample_num $SAMPLE_NUM --results_dir $REPLAY_DIR_NAME