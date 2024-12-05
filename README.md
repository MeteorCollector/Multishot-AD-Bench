# Multishot Autonomous Driving Benchmark

我们构建了一个由1-shot, 2-shot, 3-shot数据，也就是ego vehicle在每处恰巧经过1, 2, 3次的数据集，来evaluate对历史路径数据敏感的自动驾驶模型。虽然一开始是只针对perception任务设计的，但是因为我们有足够的数据，也支持端到端的全任务evaluate，并与[Bench2Drive](https://github.com/Thinklab-SJTU/Bench2Drive)框架适配。

我们的开源代码包括：

1. 使用 sota rule-based model [pdm-lite](https://github.com/OpenDriveLab/DriveLM/tree/DriveLM-CARLA/pdm_lite) 进行采集的 Bench2Drive 格式 Carla 数据采集脚本。

2. Multishot 数据集。

3. 使用 Bench2Drive 架构的训练/测试脚本，给出了 UniAD 的 evaluate 例子。

数据集下载请移步 [huggingface](https://huggingface.co/datasets/Telkwevr/Multishot-AD-Bench/tree/main)

数据集结构细节请查阅 [anno.md](anno.md)

## 数据采集 Data Collection

Generate dataset in nuscenes ([Bench2Drive](https://github.com/Thinklab-SJTU/Bench2Drive) version) format using Carla! You can config your dataset in configs.

### 项目结构 Data Collection Project Structure

`dataset_generator` 里面放着我们改进的 Carla 的 nuScenes 格式数据集采集代码；剩下的部分是 `transfuser` 里面的一些代码。`legacy` 里面是之前开发时候遗留下来的代码，不必理会。

Real useful codes are placed under `dataset_generator` folder, rest of them are legacy codes from `transfuser` and prototype projects for development, just ignore them.

### 安装 Installation

目前我们用的是 `dataset_generator`，我们目前只配置它的环境。这个仓库使用的是最新版本的 `Carla`，因此请先配置 `Carla 0.9.15`（经过我的考察，`Carla >= 0.9.12`即可，但是我现在用的是最新版）：

We only set up environment for `dataset_generator`. Please install `Carla` beforehands, version 0.9.15 is the best choice in practice.

首先配置 `python 3.8` 版本的虚拟环境：

Firstly, create virtual environment with `python 3.8`

```bash
conda create --name kshot python=3.8 -y
conda activate kshot
```

配置包：

Install pygame and numpy

```bash
pip install --user pygame numpy
```

下载 Carla：

Download Carla, please refer to [Official Tutorial](https://carla.readthedocs.io/en/0.9.15/start_quickstart/)

请参考[官方教程](https://carla.readthedocs.io/en/0.9.15/start_quickstart/)，推荐的下载方式是github release。下载完成后，将文件转移到你想安装的目录，进行

```bash
tar -xf CARLA_0.9.15.tar.gz
tar -xf AdditionalMaps_0.9.15.tar.gz
```

(当然你的压缩包可能和我的有出入，版本对就好)

这样 Carla 就安装好了。

本项目还暂时没有弄 `requirements.txt`，报错少包就一直安装吧，以后可能更新一个。

Currently we don't have a `requirements.txt` to manage dependencies, please help yourself. We will implement it soon, hopefully.

### CARLA 特别提醒 Carla Special Reminder

 - 在无图形化界面服务器上运行新版 Carla 时，请添加参数 `-RenderOffScreen`，即

   ```bash
   ./CarlaUE4.sh -RenderOffScreen
   ```
 
 - 在使用 GNU-Screen 工具进行后台运行时，一定要先进入 screen 再进行 conda/source activate ，否则也会产生一些问题。

### 使用 pdm-lite 进行采集 Use pdm-lite to Collect Data

在 pdm-lite 脚本之前，我们还实现过几个数据采集脚本，在 `legacy/dataset_generator` 文件夹下可以找到。但是非常不建议运行。旧脚本的文档位于[这里](data_generator_legacy.md)。

我们使用 pdm-lite 这个 rule-based 的 sota agent 进行数据采集，和 DriveLM 使用同款。pdm-lite 的仓库位于 [这里](https://github.com/OpenDriveLab/DriveLM/tree/DriveLM-CARLA/pdm_lite)。

### 环境配置 Environment Setup

按照上述描述可能还需要再装几个包才能跑 pdmlite，比如 webcolor, transform3d, gym 等等，不过我具体也不记得了，一路跟着报错装下来就可以了。

### 配置采集任务 Setup Config

打开 `pdm_lite/start_expert_local.sh`，配置 `CARLA_ROOT` 为你的 `CARLA` 所在的路径，`WORK_DIR` 为你的 `pdm_lite` 文件夹所在路径。

确认 `DATAGEN` 环境变量为`1`。

`SAVE_PATH` 是采集出来的数据所在的文件夹，默认是相对路径 `./logs`。

`PTH_ROUTE` 请填入采集数据用的 `scenario` 的 `xml` 文件位置，但是不需要填入 `.xml` 后缀。你会发现每个 `xml` 文件中，有若干条 `route`。对于每条 `route`，采集脚本都会单独生成一个文件夹来存放数据。

采集脚本会自动生成一个和 `xml` 文件相同名称的 `json` 文件，用来存放数据采集进度，方便任务中断之后下次从没有采完的部分接着进行。因此，假如你要进行多次采集，忽略之前的进度，**请把json文件删除**。

可以使用 `ONLY_DAY` 和 `ONLY_NIGHT` 两个环境变量来限定只采白天或者黑夜的数据。由于 Carla 中模拟时白天黑夜的能见度差距极大，建议分类讨论。

在这个采集脚本中，相比原版 `scenario_runner`，我们采用当前的时间种子对 `ego_vehicle` 附近车辆的生成 `pattern` 进行了随机化（包括车辆型号和生成位置、数量等），避免多次运行同一条 `route` 时，车辆完全相同而产生过拟合的结果。如果你不想这样，可以 export `RANDOM_SEED` 这个环境变量来固定随机种子。

### 运行 Run

```shell
cd ./pdm_lite
./start_expert_local.sh
```

注意：**无需单独启动 Carla**，该 bash 脚本已经包含了 Carla 的启动。

## 模型测试/训练 Model Evaluation/Train

使用数据集进行模型的测试和训练的方法与 [Bench2DriveZoo](https://github.com/Thinklab-SJTU/Bench2DriveZoo/tree/uniad/vad) 类似。

以下步骤请移步

```shell
cd ./benchmark/Bench2DriveZoo
```

操作。

### 数据准备 Data Preparation

从我们的 [huggingface](https://huggingface.co/datasets/Telkwevr/Multishot-AD-Bench/tree/main) 仓库下载数据集，确保结构如此：

Download our dataset from releases and make sure the structure of data as follows:

```
    Bench2DriveZoo
    ├── ...                   
    ├── data/
    |   ├── multishot/
    |   |   ├── v1/                                          # Bench2Drive base 
    |   |   |   ├── 1-shot/
    |   |   |   ├── 2-shot/
    |   |   |   └── 3-shot/
    |   |   └── maps/                                        # maps of Towns
    |   |       ├── Town01_HD_map.npz
    |   |       ├── Town02_HD_map.npz
    |   |       └── ...
    |   ├── others
    |   |       └── b2d_motion_anchor_infos_mode6.pkl        # motion anchors for UniAD
    |   └── splits
    |           ├── multishot_1-shot_train_val_split.json    # trainval_split of multishot dataset 
    |           ├── multishot_2-shot_train_val_split.json
    |           └── multishot_3-shot_train_val_split.json

```

`multishot/v1` 文件夹下的 `1-shot` `2-shot` `3-shot` 等数据集本身文件、`maps/` 文件夹下的地图文件请从 [huggingface](https://huggingface.co/datasets/Telkwevr/Multishot-AD-Bench/tree/main) 处下载。

### 生成 Data Info Prepare Data Info

由于 nuscenes 的历史遗留问题，需要生成 data_info 文件。我们有一个脚本 [prepare_multishot.py](benchmark/Bench2DriveZoo/mmcv/datasets/prepare_multishot.py) 来做这件事。但是在运行之前，请先修改：

1. 该脚本不能同时生成所有 shot 的 info，请更改 `SHOT` 变量的值来确定。

2. 请确认 `DATAROOT` `MAP_ROOT` `OUT_DIR` 路径正确，一般不会有问题。

接着运行：

```shell
cd mmcv/datasets
python prepare_multishot.py --workers 16   # workers used to prepare data
```

The command will generate `multishot_infos_train.pkl`, `multishot_infos_val.pkl`, `multishot_map_infos.pkl` under `data/infos`.

如果不想自己运行（推荐自己运行，可以自行修改 split json 来划分训练/测试集），你也可以使用 repo 里面的使用所有数据作为验证集的[`data_info`](./multishot_dataset/dataset_info_split/)。`map_info` 可以从 release 处下载。

### 验证 UniAD Evaluate UniAD

```shell
cd ./benchmark/Bench2DriveZoo
./adzoo/uniad/uniad_dist_eval.sh ./adzoo/uniad/configs/stage2_e2e/multishot_e2e.py path/to/uniad_base_b2d.pth 1
```

使用的是哪个 dataset 取决于 infos 文件夹下使用的是多少 shot 的 `data_info`。