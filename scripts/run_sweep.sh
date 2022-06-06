# BUILD SASUMO
. ./SASUMO/scripts/install.sh ./


SETTINGS_FILE="SASUMO/input_files/param_sweeps/EmissionsProbability.yaml"

CPUS="60"

# change these for your own system
export SENSITIVITY_ANALYSIS_OUTPUT=/home/max/tmp/sasumo-output
export NOHUP=$SENSITIVITY_ANALYSIS_OUTPUT/nohup.out
export NOHUP_ERROR=$SENSITIVITY_ANALYSIS_OUTPUT/nohup.err

# try to shutdown existing ray instances
ray stop

# Start Ray
ray start --head --port=6379  --num-cpus=$CPUS

# Run Simulation
# nohup python SASUMO/SASUMO/creator.py $SETTINGS_FILE  > $NOHUP 2> $NOHUP_ERROR < /dev/null &

# tail $NOHUP -f

python SASUMO/SASUMO/parameter_sweep.py $SETTINGS_FILE