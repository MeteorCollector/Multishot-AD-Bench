import xml.etree.ElementTree as ET
import yaml
import copy
import os
from tqdm import tqdm
import re

def find_town(text):
    pattern = r'\bTown\w*(?=_)'
    matches = re.findall(pattern, text)
    return matches

def from_xml_to_config(xml_path, yaml_path):

    # print(f"Processing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    def include_constructor(loader, node):
        filename = loader.construct_scalar(node)
        with open(filename, 'r') as f:
            return yaml.safe_load(f)

    yaml.SafeLoader.add_constructor('!include', include_constructor)

    emb_Path = os.environ.get('EMB_PATH', None)

    with open(emb_Path, 'r') as file:
        data = yaml.safe_load(file)



    n = len(root.findall('route'))

    for i in range(n - 1):
        data['worlds'][0]['captures'][0]['scenes'].append(copy.deepcopy(data['worlds'][0]['captures'][0]['scenes'][0]))
    

    k = 0

    for route in root.findall('route'):
        waypoints = route.findall('waypoint')
        wpCount = 0

        len_wp = len(waypoints)
        for i in range(len_wp - 1):
            data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['path'].append(copy.deepcopy(data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['path'][0]))

        for waypoint in waypoints:
            x = float(waypoint.get('x'))
            y = float(waypoint.get('y'))
            z = float(waypoint.get('z')) + float(os.environ.get('Z_DELTA', None))
            yaw = float(waypoint.get('yaw'))
            pitch = float(waypoint.get('pitch'))
            roll = float(waypoint.get('roll'))
            if wpCount == 0:
                data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['location']['x'] = x
                data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['location']['y'] = y
                data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['location']['z'] = z
                
                data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['rotation']['yaw'] = yaw
                data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['rotation']['pitch'] = pitch
                data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['rotation']['roll'] = roll
            
            data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['path'][wpCount]['x'] = x
            data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['path'][wpCount]['y'] = y
            data['worlds'][0]['captures'][0]['scenes'][k]['ego_vehicle']['path'][wpCount]['z'] = z
            wpCount = wpCount + 1
        k = k + 1
    
    data['worlds'][0]['map_name'] = str(find_town(os.path.basename(xml_path))[0])

    assert(k == n)

    with open(yaml_path, 'w') as file:
        yaml.dump(data, file)
        # print(f"Saved into {yaml_path}.")

    

def convert_folder(in_path, out_path):
    files = []

    for root, _, filenames in os.walk(in_path):
        for filename in filenames:
            if filename.endswith('.xml'):
                files.append(os.path.join(root, filename))

    for file in tqdm(files):
        fname = os.path.basename(file).split('.')[0]
        wname = f"{fname}_converted.yaml"
        wpath = os.path.join(out_path, wname)

        from_xml_to_config(file, wpath)


if __name__ == "__main__":
    xml_path = os.environ.get('INPUT_DIR', None)
    out_path = os.environ.get('OUTPUT_DIR', None)
    convert_folder(xml_path, out_path)