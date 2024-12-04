import carla
import random
from configs import load_scenario
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider

def setup_carla_client(task):
    client = carla.Client('localhost', 2000)
    client.set_timeout(30.0)
    CarlaDataProvider.set_client(client)

    town_name, task_name, waypoints = load_scenario(task['scenario_path'])
    
    try:
        world = client.load_world(town_name)
    except RuntimeError as e:
        print(f"[Error] Failed to load world: {e}")
        return None

    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 1 / (task['frame_rate'])
    world.apply_settings(settings)

    return world, town_name, task_name, waypoints

# 设置随机天气，并返回天气名称
def set_random_weather(world):
    weather_presets = {
        "ClearNoon": carla.WeatherParameters.ClearNoon,
        "ClearSunset": carla.WeatherParameters.ClearSunset,
        "CloudyNoon": carla.WeatherParameters.CloudyNoon,
        "CloudySunset": carla.WeatherParameters.CloudySunset,
        "WetNoon": carla.WeatherParameters.WetNoon,
        "WetSunset": carla.WeatherParameters.WetSunset,
        "MidRainyNoon": carla.WeatherParameters.MidRainyNoon,
        "MidRainSunset": carla.WeatherParameters.MidRainSunset,
        "WetCloudyNoon": carla.WeatherParameters.WetCloudyNoon,
        "WetCloudySunset": carla.WeatherParameters.WetCloudySunset,
        "HardRainNoon": carla.WeatherParameters.HardRainNoon,
        "HardRainSunset": carla.WeatherParameters.HardRainSunset,
        "SoftRainNoon": carla.WeatherParameters.SoftRainNoon,
        "SoftRainSunset": carla.WeatherParameters.SoftRainSunset,
        "ClearNight": carla.WeatherParameters.ClearNight,
        "CloudyNight": carla.WeatherParameters.CloudyNight,
        "WetNight": carla.WeatherParameters.WetNight,
        "WetCloudyNight": carla.WeatherParameters.WetCloudyNight,
        "SoftRainNight": carla.WeatherParameters.SoftRainNight,
        "MidRainyNight": carla.WeatherParameters.MidRainyNight,
        "HardRainNight": carla.WeatherParameters.HardRainNight,
        "DustStorm": carla.WeatherParameters.DustStorm
    }

    weather_name, random_weather = random.choice(list(weather_presets.items()))
    world.set_weather(random_weather)
    return weather_name

def create_agent_vehicle(world, waypoints, max_trial=20):
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.find('vehicle.ford.crown') # you can modify this! refer to https://carla.readthedocs.io/en/latest/catalogue_vehicles/#ford-crown-taxi

    first_waypoint = waypoints[0]
    first_waypoint = waypoints[0]
    spawn_x = first_waypoint['x']
    spawn_y = first_waypoint['y']
    spawn_z = first_waypoint['z']
    spawn_yaw = first_waypoint.get('yaw', 0)

    vehicle = None
    trial = 0
    
    while trial < max_trial and vehicle is None:
        # avoid z-axis collision
        spawn_point = carla.Transform(
            carla.Location(x=spawn_x, y=spawn_y, z=spawn_z + 0.1 * trial),
            carla.Rotation(pitch=0, yaw=spawn_yaw, roll=0)
        )
        
        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        
        if vehicle:
            print(f"Agent vehicle successfully spawned after {trial + 1} attempts (z = {spawn_z + 0.1 * trial}).")
            break
        
        trial += 1

    if vehicle is None:
        raise RuntimeError(f"Failed to spawn the agent vehicle after {max_trial} attempts.")

    return vehicle

def spawn_npc_vehicles(world, vehicle_count):
    actor_list = []
    blueprint_library = world.get_blueprint_library()
    vehicle_blueprints = blueprint_library.filter('vehicle.*')

    spawn_points = world.get_map().get_spawn_points()
    if len(spawn_points) < vehicle_count:
        vehicle_count = len(spawn_points)

    real_vehicle_count = 0
    for i in range(vehicle_count):
        vehicle_bp = random.choice(vehicle_blueprints)
        spawn_point = random.choice(spawn_points)

        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
        if vehicle:
            actor_list.append(vehicle)

            vehicle.set_autopilot(True)
            real_vehicle_count += 1
    
    print(f"Successfully spawned {real_vehicle_count} NPC vehicles (tried {vehicle_count}).")
    return actor_list

def spawn_pedestrians(world, pedestrian_count):
    actor_list = []
    blueprint_library = world.get_blueprint_library()
    pedestrian_blueprints = blueprint_library.filter('walker.pedestrian.*')  # 过滤出所有行人模型

    spawn_points = []
    for i in range(pedestrian_count):
        spawn_point = carla.Transform()
        spawn_point.location = world.get_random_location_from_navigation()  # 从导航网格中随机选一个地点
        spawn_points.append(spawn_point)

    batch = []
    for spawn_point in spawn_points:
        pedestrian_bp = random.choice(pedestrian_blueprints)
        walker = world.try_spawn_actor(pedestrian_bp, spawn_point)
        if walker:
            actor_list.append(walker)
            batch.append(walker)

    walker_controller_bp = blueprint_library.find('controller.ai.walker')
    for walker in batch:
        walker_controller = world.try_spawn_actor(walker_controller_bp, carla.Transform(), walker)
        if walker_controller:
            actor_list.append(walker_controller)
            walker_controller.start()

    print(f"Successfully spawned {len(batch)} pedestrians (tried {pedestrian_count}).")
    return actor_list