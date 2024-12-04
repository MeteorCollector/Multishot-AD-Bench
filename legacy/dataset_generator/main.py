import time
from configs import load_tasks
from worlds import setup_carla_client
from task_runner import run_task

def run_all_tasks(json_path):
    tasks = load_tasks(json_path)

    for task in tasks:
        time.sleep(2) # avoid sync error
        world, town_name, task_name, waypoints = setup_carla_client(task)
        if world is not None:
            run_task(world, task, town_name, task_name, waypoints)

if __name__ == "__main__":
    json_file = 'tasks.json'
    run_all_tasks(json_file)
