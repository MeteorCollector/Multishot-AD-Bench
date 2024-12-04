import os
import sys
import yaml
from datetime import datetime

def modify_yaml_data(data):
    # 获取当前日期和时间
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H-%M-%S')

    # 遍历字典中的所有键值对
    for key, value in data.items():

        if isinstance(value, dict):
            modify_yaml_data(value)
        
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    modify_yaml_data(item)
        
        if key == 'date':
            data[key] = current_date
            print("modified date")
        elif key == 'time':
            data[key] = current_time
            print("modified time")

def modify_yaml_file(file_path):
    # 打开 YAML 文件进行读取
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    # 修改 YAML 数据
    modify_yaml_data(data)

    # 将修改后的数据写回文件
    with open(file_path, 'w') as f:
        yaml.dump(data, f)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python modify_yaml.py <yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    print(f"========= updating {yaml_file} =========")
    modify_yaml_file(yaml_file)
