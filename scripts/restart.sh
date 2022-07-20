PID=87521

echo Waiting...; while ps -p $PID > /dev/null; do sleep 1; done; sh $AIRPORT_HARPER_SUMO/SASUMO/scripts/run.sh