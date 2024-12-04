#!/bin/bash

export CARLA_ROOT=${1:-/media/telkwevr/22729A30729A08A5/Project_/new_carla/carla}
export WORK_DIR=${2:-/media/telkwevr/22729A30729A08A5/Project_/Tfuse-to-nuScene/carla_to_nuScenes}
export SAVE_PATH=${WORK_DIR}/results

export CARLA_SERVER=${CARLA_ROOT}/CarlaUE4.sh
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg
export SCENARIO_RUNNER_ROOT=${WORK_DIR}/scenario_runner
export LEADERBOARD_ROOT=${WORK_DIR}/leaderboard
export PYTHONPATH="${CARLA_ROOT}/PythonAPI/carla/":"${SCENARIO_RUNNER_ROOT}":"${LEADERBOARD_ROOT}":${PYTHONPATH}

CONFIG_PATHS=$(find ${WORK_DIR}/route_configs -name "*.yaml")

INDEX=1

while true; do
    for CONFIG_PATH in $CONFIG_PATHS; do
        export CONFIG_PATH

        python update_timestamp.py "$CONFIG_PATH"
        python ./generate.py

        RESULT_DIR="${SAVE_PATH}/$(basename ${CONFIG_PATH%.*})"
        mkdir -p "$RESULT_DIR/$INDEX"
        cp -r ./dataset/* "$RESULT_DIR/$INDEX"
        rm -rf ./dataset

        ((INDEX++))
    done
done