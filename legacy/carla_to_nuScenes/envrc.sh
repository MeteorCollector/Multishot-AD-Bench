# export CARLA_ROOT=${1:-/home/kchitta/Documents/CARLA_0.9.10.1}
# export WORK_DIR=${2:-/home/kchitta/Documents/transfuser}
export CARLA_ROOT=${1:-/media/telkwevr/22729A30729A08A5/Project_/new_carla/carla}
export WORK_DIR=${2:-/media/telkwevr/22729A30729A08A5/Project_/Tfuse-to-nuScene/carla_to_nuScenes}

export CARLA_SERVER=${CARLA_ROOT}/CarlaUE4.sh
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg
export SCENARIO_RUNNER_ROOT=${WORK_DIR}/scenario_runner
export LEADERBOARD_ROOT=${WORK_DIR}/leaderboard
export PYTHONPATH="${CARLA_ROOT}/PythonAPI/carla/":"${SCENARIO_RUNNER_ROOT}":"${LEADERBOARD_ROOT}":${PYTHONPATH}

export CONFIG_PATH=${WORK_DIR}/configs/Town05_Scenario1_converted.yaml

python ./generate.py
