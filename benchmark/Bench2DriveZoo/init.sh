export PATH=/usr/share/gcc/bin:/usr/bin/gcc/bin:/usr/lib/gcc/bin:$PATH
export CUDA_HOME=/home/telkwevr/anaconda3/envs/b2d_zoo/
export CARLA_ROOT=${1:-/media/telkwevr/22729A30729A08A5/Project_/new_carla/carla}
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg
echo "$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg" >> /home/telkwevr/anaconda3/envs/b2d_zoo/lib/python3.7/site-packages/carla.pth # python 3.8 also works well, please set YOUR_CONDA_PATH and YOUR_CONDA_ENV_NAME


