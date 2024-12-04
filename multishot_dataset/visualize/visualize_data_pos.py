import os
import json
import gzip
import matplotlib.pyplot as plt

DATA_ROOT = "path/to/multishot/v1"
OUT_ROOT = "path/to/vis"
SHOT = 3

DATA_ROOT = f"{DATA_ROOT}/{SHOT}-shot"
OUT_ROOT = f"{OUT_ROOT}/{SHOT}-shot"

os.makedirs(OUT_ROOT, exist_ok=True)

def extract_pos_global(json_gz_path):
    with gzip.open(json_gz_path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('pos_global')

def visualize_pos_global(data_root, out_root):
    for folder in os.listdir(data_root):

        town_idx = int(folder[1:])
        if town_idx == 10:
            town_name = f'Town{town_idx:02}HD'
        else:
            town_name = f'Town{town_idx:02}'
        
        folder_path = os.path.join(data_root, folder)
        if not os.path.isdir(folder_path):
            continue

        print(f"Processing folder: {folder}")

        pos_list = []

        for scenario in os.listdir(folder_path):
            scenario_path = os.path.join(folder_path, scenario)
            measurements_path = os.path.join(scenario_path, "measurements")
            
            if not os.path.isdir(measurements_path):
                continue

            for json_file in os.listdir(measurements_path):
                if json_file.endswith(".json.gz"):
                    json_path = os.path.join(measurements_path, json_file)
                    pos = extract_pos_global(json_path)
                    if pos:
                        pos_list.append(pos)

        if pos_list:
            pos_array = list(zip(*pos_list))
            plt.figure(figsize=(10, 10))
            plt.scatter(pos_array[0], pos_array[1], s=1, c='blue', alpha=0.5)
            plt.title(f"Position Distribution in {town_name}")
            plt.xlabel("X")
            plt.ylabel("Y")
            plt.grid(True)

            out_file = os.path.join(out_root, f"{town_name}_{SHOT}-shot.png")
            plt.savefig(out_file)
            plt.close()
            print(f"Saved plot to {out_file}")
        else:
            print(f"No pos_global data found in {town_name}")

if __name__ == "__main__":
    visualize_pos_global(DATA_ROOT, OUT_ROOT)
