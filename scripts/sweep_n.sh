# BUILD SASUMO
. ./SASUMO/scripts/install.sh ./

# specify the number of cpus
CPUS=$(nproc)

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

# Running the incomplete simulation
python SASUMO/SASUMO/creator.py "/home/max/tmp/sasumo-output/PaperFinalCarFollowingV0.2/08.18.2022_09.18.29/sasumo_params.yaml"

FILES="$1/*"
for f in $FILES
do
  echo "Running SA for $f file..."
  python SASUMO/SASUMO/creator.py $f
  # take action on each file. $f store current file name
  # perform some operation with the file
done