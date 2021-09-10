SETTINGS_FILE="/home/max/remote/airport-harper-sumo/SASUMO/input_files/first_try.yaml"

source venv/bin/activate
export SIMULATION_ROOT=/home/max/remote/airport-harper-sumo
export SENSITIVITY_ANALYSIS_OUTPUT=/home/max/tmp/airport_harper_sumo_sasumo

# Start Ray
ray start --head --port=6379

# Run Simulation
python SASUMO/SASUMO/creator.py $SETTINGS_FILE

