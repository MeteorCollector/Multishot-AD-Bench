（实际上，怀疑简易脚本写错了。。。每个 `scenario` 其实跑了很多条不同的路线，简易脚本把它们都连一起了）

## 配置项目设置 Set up configs

要让数据采集成功跑起来，还需要修改一些地方。

You must modify some configure information to get start.

首先是 `dataset_generator/generate_datasets.sh`，请务必将 `CARLA_ROOT` 配置成你的 `carla` 所在目录，并且请确保引用的 `.egg` 文件与你下载版本的 `.egg` 文件名称相同（对这个 `python` 包文件的引用可以在 `PYTHON_PATH` 附近找到）。

Firstly, open `dataset_generator/generate_datasets.sh`, please set `CARLA_ROOT` to your CARLA directory, then check out `PYTHON_PATH`, make sure the `.egg` file bash script refers to is exactly the same file you installed.

然后是 `dataset_generator/tasks.json` 这个配置文件。这里给出一个示例：

Then set config file `dataset_generator/tasks.json`, here's an example:

```json
[
    {
        "scenario_path": "./scenarios/Scenario3/Town06_Scenario3.json",
        "time_limit": 1,
        "shot_count": 2,
        "frame_rate": 60,
        "data_rate": 10,
        "vehicle_count": 20,
        "pedestrian_count": 20
    },
    {
        "scenario_path": "./scenarios/Scenario1/Town05_Scenario1.json",
        "time_limit": 1,
        "shot_count": 2,
        "frame_rate": 60,
        "data_rate": 10,
        "vehicle_count": 20,
        "pedestrian_count": 20
    }
]
```

在这个示例里，每组大括号内代表一个 task，`senario_path` 代表路径文件所在位置，这个文件决定了 `ego_vehicle` 的行驶路线。这些路径文件可以在 `transfuser` 项目中找到。`time_limit` 是每个任务在CARLA中执行时间的上限（单位：秒），当车辆到达终点或者达到时间限制时，会终止仿真和传感器采集。`shot_count` 是这个 task 执行的次数，每一个 shot 会生成一个数据集子集。`frame_rate` 代表游戏中仿真每秒的 tick 数，建议不要太少，否则每一步模拟的时间太长会导致问题。`data_rate` 代表传感器每秒采集的数据份数，`vehicle_count` 和 `pedestrain_count` 代表场景中NPC车辆、行人的数量。

生成的数据集会存储在 `dataset_generator/data`。数据结构请看[anno.md](./anno.md)。

In this example, each set of attributes inside a `{}` represents a task. `senario_path` links to the position of route config file, which decides the running route of ego vehicle. These route files can be found inside `transfuser` project. `time_limit` is the maximum running time (in seconds) inside CARLA of this task. Either when the ego vehicle reaches the destination or the clock inside CARLA exceeds time limit, simulation of this task will end. `shot_count` is the iteration count of the task, each shot will generate a subset of dataset independently. `frame_rate` is the tick count per second inside CARLA. We recommend a higher rate to guarantee the precision of simulation. `data_rate` defines frequancies of sensors, `vehicle_count` and `pedestrain_count` defines the count of NPC vehicles and pedestrains in simulated CARLA town.

Generated datased will be stored under `dataset_generator/data`. For the structure of data, please refer to [anno.md](./anno.md)

## 运行 Run

首先到 Carla 所在路径运行 Carla:

Before running data generation, cd to Carla's directory to run Carla:

```bash
   ./CarlaUE4.sh --world-port=2000
```

然后运行 `generate_datasets.sh`：

Then run `generate_datasets.sh`:

```bash
    cd ./dataset_generator
    chmod a+x ./generate_all_datasets.sh
    ./generate_all_datasets.sh
```