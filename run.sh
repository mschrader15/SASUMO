SETTINGS_FILE="/home/max/remote/airport-harper-sumo/SASUMO/input_files/first_try.yaml"

# Getting the CPU Cores
CPU_LINES="$(grep -oP '(?>cpu_cores:).(?:\d)+' $SETTINGS_FILE)"
CPUS="$(grep -oP '(\d)+' <<< $CPU_LINES)"

source venv/bin/activate

# change these for your own system
export SIMULATION_ROOT=/home/max/remote/airport-harper-sumo
export SENSITIVITY_ANALYSIS_OUTPUT=/home/max/tmp/airport_harper_sumo_sasumo
export NOHUP=$SENSITIVITY_ANALYSIS_OUTPUT/nohup.out
export NOHUP_ERROR=$SENSITIVITY_ANALYSIS_OUTPUT/nohup.err

# try to shutdown existing ray instances
ray stop

# Start Ray
ray start --head --port=6379  --num-cpus=$CPUS

# Run Simulation
nohup python SASUMO/SASUMO/creator.py $SETTINGS_FILE > $NOHUP 2> $NOHUP_ERROR < /dev/null &

tail $NOHUP -f