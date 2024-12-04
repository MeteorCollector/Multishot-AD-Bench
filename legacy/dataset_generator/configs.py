import json
import os
import random

# read json file
def load_tasks(json_path):
    with open(json_path, 'r') as f:
        tasks = json.load(f)
    return tasks

def load_scenario(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    town_name = list(data['available_scenarios'][0].keys())[0]
    scenario = data['available_scenarios'][0][town_name][0]
    transforms = [config['transform'] for config in scenario['available_event_configurations']]
    
    return town_name, scenario['scenario_type'], transforms

# crate folder for dataset
def create_save_path(town_name, task_name, weather_name):
    random_digits = str(random.randint(1000, 9999))
    dir_name = f"{town_name}_{task_name}_{weather_name}_{random_digits}"
    save_path = os.path.join('./data', dir_name)
    os.makedirs(save_path, exist_ok=True)
    return save_path