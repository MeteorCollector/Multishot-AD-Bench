#!/bin/bash

# This script starts PDM-Lite and the CARLA simulator on a local machine

# Make sure any previously started Carla simulator instance is stopped
# Sometimes calling pkill Carla only once is not enough.
pkill Carla
pkill Carla
pkill Carla

term() {
  echo "Terminated Carla"
  pkill Carla
  pkill Carla
  pkill Carla
  exit 1
}
trap term SIGINT

# envs
export CARLA_ROOT=${1:-/media/telkwevr/22729A30729A08A5/Project_/new_carla/carla}
export WORK_DIR=/media/telkwevr/22729A30729A08A5/Project_/Tfuse-to-nuScene/pdm_lite
export CARLA_SERVER=${CARLA_ROOT}/CarlaUE4.sh
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg
export PYTHONPATH=$PYTHONPATH:${WORK_DIR}/scenario_runner
export PYTHONPATH=$PYTHONPATH:${WORK_DIR}/leaderboard
export SCENARIO_RUNNER_ROOT=${WORK_DIR}/scenario_runner
export LEADERBOARD_ROOT=${WORK_DIR}/leaderboard

# carla
export CARLA_SERVER=${CARLA_ROOT}/CarlaUE4.sh
export REPETITIONS=1
export DEBUG_CHALLENGE=0

# export PTH_ROUTE=${WORK_DIR}/data/routes_devtest
# export PTH_ROUTE=${WORK_DIR}/xml_routes/old_towns/s1/Town04_Scenario1
export PTH_ROUTE=${WORK_DIR}/Bench2Drive_xml/data/bench2drive220

# Function to handle errors
handle_error() {
  pkill Carla
  exit 1
}

# Set up trap to call handle_error on ERR signal
trap 'handle_error' ERR

# Start the carla server
# export PORT=$((RANDOM % (40000 - 2000 + 1) + 2000)) # use a random port
export PORT=2000
sh ${CARLA_SERVER} -RenderOffScreen -nosound -carla-streaming-port=0 -carla-rpc-port=${PORT} &
sleep 20 # on a fast computer this can be reduced to sth. like 6 seconds

echo 'Port' $PORT

export TEAM_AGENT=${WORK_DIR}/team_code/data_agent.py # use autopilot.py here to only run the expert without data generation
export CHALLENGE_TRACK_CODENAME=MAP
export ROUTES=${PTH_ROUTE}.xml
export TM_PORT=$((PORT + 3))

export CHECKPOINT_ENDPOINT=${PTH_ROUTE}.json
export TEAM_CONFIG=${PTH_ROUTE}.xml
export PTH_LOG='logs'
export RESUME=0
export DATAGEN=1
export SAVE_PATH='logs'
export TM_SEED=$(date +%s)
export NO_WET=1 # disable water on road
export ONLY_DAY=1 # if ONLY_DAY==1, only day
export ONLY_NIGHT=0 # if ONLY_NIGHT=1, only night

# Start the actual evaluation / data generation
python leaderboard/leaderboard/leaderboard_evaluator_local.py --port=${PORT} --traffic-manager-port=${TM_PORT} --routes=${ROUTES} --repetitions=${REPETITIONS} --track=${CHALLENGE_TRACK_CODENAME} --checkpoint=${CHECKPOINT_ENDPOINT} --agent=${TEAM_AGENT} --agent-config=${TEAM_CONFIG} --debug=0 --resume=${RESUME} --timeout=2000 --traffic-manager-seed=${TM_SEED}

# Kill the Carla server afterwards
pkill Carla