import carla
import time
import sys
import shutil
import os
from tqdm import tqdm
from math import floor
from worlds import set_random_weather, create_agent_vehicle, spawn_npc_vehicles, spawn_pedestrians
from configs import create_save_path
from sensors import attach_camera_to_vehicle, save_image
from data_collect import Env_Manager
from srunner.scenariomanager.scenario_manager import ScenarioManager
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from agents.navigation.global_route_planner import GlobalRoutePlanner

def clean_actor(actor_list, env_manager):
    time.sleep(2)
    for actor in actor_list:
        if actor is not None:
            try:
                actor.destroy()
            except Exception as e:
                print(f"[Warning] Failed to destroy actor")
    time.sleep(2)
    if env_manager is not None:
        env_manager.clean_up()

# 车辆随机游走
def start_vehicle_walk(vehicle, env_manager, actor_list, time_limit, frame_rate, data_rate, save_path, waypoints):
    world = vehicle.get_world()
    planner = GlobalRoutePlanner(world.get_map(), sampling_resolution=2.0)

    silent_tick_count = 10 # first few ticks, sensors don't output
    total_ticks = int(time_limit * frame_rate) + silent_tick_count + 2
    start_time = world.get_snapshot().timestamp.elapsed_seconds

    frame_id = 0
    waypoint_index = 1 # target start from second waypoint, the first one is starting point
    num_waypoints = len(waypoints)

    # main loop
    with tqdm(total=num_waypoints, desc="Vehicle Waypoint Progress") as pbar:
        pbar.update(1)
        sys.stdout.write(f"Current tick: 0")
        for tick in range(total_ticks):
            current_time = world.get_snapshot().timestamp.elapsed_seconds

            if vehicle is None:
                print(f"Agent vehicle is None, ending at {current_time - start_time}s. Please check.")
                clean_actor(actor_list, env_manager)
                return

            # 检查时间限制，是否超出time_limit
            if current_time - start_time >= time_limit:
                clean_actor(actor_list, env_manager)
                return

            # 设置车辆为自动驾驶模式
            vehicle.set_autopilot(True)

            # 获取当前车辆位置
            vehicle_location = vehicle.get_location()

            # 获取下一个路径点
            waypoint = waypoints[waypoint_index]

            # 将路径点设置为车辆的目标位置
            waypoint_location = carla.Location(
                x=waypoint['x'],
                y=waypoint['y'],
                z=waypoint['z']
            )

            # 检查车辆是否接近下一个路径点（例如距离小于 2.0 米）
            if vehicle_location.distance(waypoint_location) < 2.0:
                waypoint_index += 1  # 到达路径点后，移动到下一个路径点
                pbar.update(1)  # 更新进度条

            # 如果到达最后一个路径点，终止仿真
            if waypoint_index >= num_waypoints:
                print("Vehicle has reached the final waypoint.")
                clean_actor(actor_list, env_manager)
                return

            if tick >= silent_tick_count:
                env_manager.route_plan = planner.trace_route(vehicle_location, waypoint_location)
                tick_data = env_manager.tick()

                near_node, far_node, near_command, far_command = get_near_and_far_waypoints(env_manager.route_plan)

                env_manager.save(near_node, far_node, near_command, far_command, tick_data, floor((current_time - start_time) * data_rate))
                # save(self, near_node, far_node, tick_data, frame)

                sys.stdout.write(f"\rCurrent tick: {tick + 1 - silent_tick_count}")
                sys.stdout.flush()

                frame_id += 1  # 增加帧ID

            world.tick()
            
    # 停止并销毁相机
    clean_actor(actor_list, env_manager)
    return

# 主要任务函数
def run_task(world, task, town_name, task_name, waypoints):
    max_trial = 5
    print(f"============== {town_name} {task_name} ==============")
    time.sleep(2)

    for shot in range(task['shot_count']):
        trial_count = 0
        while trial_count < max_trial: # if error, try more times.
            env_manager = None
            # try:
            print(f"Shot {shot + 1} of {task['shot_count']}, Trial {trial_count + 1} of {max_trial}")
            weather_name = set_random_weather(world)

            actor_list = []
            try:
                vehicle = create_agent_vehicle(world, waypoints)
                actor_list.append(vehicle)
            except RuntimeError as e:
                print(f"[Error] Failed to spawn agent vehicle: {e}, task ends.")
                clean_actor(actor_list, env_manager)
                return

            try:
                NPCvehicles = spawn_npc_vehicles(world, task['vehicle_count'])
                pedestrians = spawn_pedestrians(world, task['pedestrian_count'])
                actor_list.append(NPCvehicles)
                actor_list.append(pedestrians)
            except RuntimeError as e:
                print(f"[Error] Failed to spawn NPC vehicles or pedestrians: {e}, task ends.")
                clean_actor(actor_list, env_manager)
                return

            if vehicle is not None:
                # data_manager = DataManager()
                CarlaDataProvider.set_world(world)
                save_path = create_save_path(town_name, task_name, weather_name)
                env_manager = Env_Manager(vehicle, world, town_name, weather_name, save_path)
                env_manager.setup_sensors()
                start_vehicle_walk(vehicle, env_manager, actor_list, task['time_limit'], task['frame_rate'], task['data_rate'], save_path, waypoints)

            print(f"Task {task_name} finished with weather: {weather_name}.")
            break

            # except Exception as e:
            #     print(f"[Error] An error occurred during task execution: {e}")
            #     clean_actor(actor_list, env_manager)

            #     if os.path.exists(save_path):
            #         print(f"Deleting save_path: {save_path}")
            #         shutil.rmtree(save_path)

            #     trial_count += 1
            #     if trial_count >= max_trial:
            #         print(f"Max trial limit reached. Task {task_name} failed after {max_trial} attempts.")
            #         return

def get_near_and_far_waypoints(route_plan):
    near_node = None
    near_command = None
    far_node = None
    far_command = None

    if len(route_plan) > 0:
        waypoint, command = route_plan[0]
        near_node = [waypoint.transform.location.x, waypoint.transform.location.y]
        near_command = command
        
        if len(route_plan) > 1:
            next_waypoint, next_command = route_plan[1]
            far_node = [next_waypoint.transform.location.x, next_waypoint.transform.location.y]
            far_command = next_command
        
    return near_node, far_node, near_command, far_command
