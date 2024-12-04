export WORK_DIR=${2:-/media/telkwevr/22729A30729A08A5/Project_/Tfuse-to-nuScene/xml_to_config}

export EMB_PATH=${WORK_DIR}/emb.yaml
export INPUT_DIR=${WORK_DIR}/input
export OUTPUT_DIR=${WORK_DIR}/output

export Z_DELTA=0.5

python ./xml_to_config.py
